"""Contains wp-cli calling and parsing classes / methods"""
import os
import getpass
import subprocess
import json
from logmod import Log
L = Log()
class Installations(object):
    """Class used for obtaining installation dir and details"""
    def __init__(self, app):
        self.app = app
        L.debug('Installations Initialized')
        self.call = Call(self.app.L)
        self.username = getpass.getuser()
        self.homedir = os.path.expanduser('~%s' % self.username)
        self.installations = self.get_installation_dirs()
        self.get_installation_details()
        L.debug("WP Installation for user %s: %s", self.username, self.installations)
    def get_installation_dirs(self):
        """Gets installation directory list using os.walk"""
        installations = []
        L.debug("%s Homedir: %s", self.username, self.homedir)
        for root, _, files in os.walk(self.homedir, topdown=True):
            if 'wp-config.php' in files:
                if not '/.' in root:
                    _x = {
                        'directory' : root,
                        'home_url' : '',
                        'valid_wp_options' : False,
                        'wp_db_check_success' : False,
                        'wp_db_error' : ''
                    }
                    installations.append(_x)
        return installations
    def get_installation_details(self):
        """Getter for installation details"""
        L.debug('Start get_installation_details')
        self.progress = 0
        progress_sections = 100 / len(self.installations)
        progress_increments = progress_sections / 2
        for installation in self.installations:
            self.progress = self.progress + progress_increments
            L.debug('Progress: %s', self.progress)
            os.write(self.app.action_pipe, str(self.progress))
            db_check_data, db_check_error = self.call.wpcli(
                installation['directory'],
                ['db', 'check'])
            if db_check_data:
                data = db_check_data.splitlines()
                for line in data:
                    if '_options' in line and 'OK' in line:
                        L.debug('Line: %s', line)
                        installation['valid_wp_options'] = True
                        self.progress = self.progress + progress_increments
                        L.debug('Progress: %s', self.progress)
                        os.write(self.app.action_pipe, str(self.progress))
                        homedata, _ = self.call.wpcli(
                            installation['directory'],
                            ['option', 'get', 'home', '--skip-plugins', '--skip-themes'])
                        if homedata:
                            installation['home_url'] = homedata.rstrip()
                    if 'Success: Database checked' in line:
                        installation['wp_db_check_success'] = True
            if db_check_error:
                installation['wp_db_error'] = db_check_error
        os.close(self.app.action_pipe)
class DatabaseInformation(object):
    """Obtains database information"""
    def __init__(self, app):
        self.app = app
        L.debug('Installations Initialized')
        self.call = Call(self.app.L)
        self.installation = self.app.state.active_installation
        self.db_info = {
            'name': None,
            'size': None,
            'size_error': None,
            'check_tables': None,
            'check_error': None
        }
        self.get_db_size()
    def get_db_size(self):
        """Get database size and name list"""
        path = self.installation['directory']
        self.progress = 0
        progress_increments = 100 / 2

        #GET DATABASE NAME AND SIZE
        self.progress = self.progress + progress_increments
        L.debug('Progress: %s', self.progress)
        os.write(self.app.action_pipe, str(self.progress))
        dbsize_result, dbsize_error = self.call.wpcli(
            path, [
                'db', 'size',
                '--human-readable',
                '--format=json', '--no-color'])
        if dbsize_result:
            result_json = json.loads(dbsize_result)
            L.debug(
                'wp_db_name: %s, wp_db_size:%s',
                result_json[0]['Name'],
                result_json[0]['Size'])
            self.db_info['name'] = result_json[0]['Name']
            self.db_info['size'] = result_json[0]['Size']
        if dbsize_error:
            L.debug('wp_db_size error:%s', dbsize_error.decode(encoding='UTF-8'))
            self.db_info['size_error'] = dbsize_error.decode(encoding='UTF-8')
        #RUN CHECK DB
        self.progress = self.progress + progress_increments
        L.debug('Progress: %s', self.progress)
        os.write(self.app.action_pipe, str(self.progress))
        if dbsize_result:
            dbcheck_result, dbcheck_error = self.call.wpcli(path, ['db', 'check'])
            dbcheck_result_list = []
            if dbcheck_result:
                for line in dbcheck_result.splitlines():
                    if self.db_info['name'] in line:
                        _x = line.split()
                        dbcheck_result_list.append(
                            {
                                'table_name': _x[0],
                                'check_status': _x[1]
                            }
                        )
                self.db_info['check_tables'] = dbcheck_result_list
            if  dbcheck_error:
                self.db_info['check_error'] = dbcheck_error.decode(encoding='UTF-8')
        #L.debug('db_info: %s',self.db_info)
        os.close(self.app.action_pipe)
class WpConfig(object):
    """Obtains and modified wp_config information"""
    def __init__(self, app):
        self.app = app
        L.debug('Installations Initialized')
        self.call = Call(self.app.L)
        self.installation = self.app.state.active_installation
        self.wp_config_directive_list = []
        self.wp_config_error = None
        self.get_wp_config()
    def get_wp_config(self):
        """getter for wp_config data"""
        path = self.installation['directory']
        self.progress = 0
        progress_increments = 100
        self.progress = self.progress + progress_increments
        L.debug('Progress: %s', self.progress)
        os.write(self.app.action_pipe, str(self.progress))
        wp_config_result, wp_config_error = self.call.wpcli(
            path, [
                'config', 'list',
                '--format=json',
                '--no-color'])
        if wp_config_result:
            L.debug('wp_config_result: %s', wp_config_result)
            self.wp_config_directive_list = json.loads(wp_config_result)
        if  wp_config_error:
            L.debug('wp_config_error: %s', wp_config_result)
            self.wp_config_error = wp_config_error
        os.close(self.app.action_pipe)
class Call(object):
    """opens a subprocess to run wp-cli command"""
    def wpcli(self, path, arguments):
        """runs_wp-cli command"""
        popen_args = ['wp']
        for argument in arguments:
            popen_args.append(argument)
        popen_args.append('--path='+path)

        data, error = subprocess.Popen(
            popen_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
            ).communicate()
        return data, error
