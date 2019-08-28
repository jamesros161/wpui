# -*- coding: utf-8 -*-
"""Contains wp-cli calling and parsing classes / methods"""
import os
import getpass
import subprocess
import json
from datetime import datetime
from threading import Thread
from random import randint
from logmod import Log


L = Log()


class Installations(object):
    """Class used for obtaining installation dir and details"""

    def __init__(self, app):
        self.app = app
        L.debug('Installations Initialized')
        self.username = getpass.getuser()
        self.homedir = os.path.expanduser('~%s' % self.username)
        self.app.state.homedir = self.homedir
        self.app.state.temp_dir = os.path.join(self.homedir, 'wpuitmp')
        if not os.path.isdir(self.app.state.temp_dir):
            os.mkdir(self.app.state.temp_dir)
        L.debug("Homedir: %s", self.homedir)
        self.installations = self.get_installation_dirs()
        if self.installations:
            self.get_installation_details()
            L.debug(
                "WP Installation for user %s: %s",
                self.username, self.installations)
        else:
            L.warning("No WP Installations available for this User!")

    def get_installation_dirs(self):
        """Gets installation directory list using os.walk"""
        installations = []
        L.debug("%s Homedir: %s", self.username, self.homedir)
        for root, _, files in os.walk(self.homedir, topdown=True):
            if 'wp-config.php' in files:
                if '/.' not in root:
                    _x = {
                        'directory': root,
                        'home_url': '',
                        'valid_wp_options': False,
                        'wp_db_check_success': False,
                        'wp_db_error': ''
                    }
                    installations.append(_x)
        return installations

    def get_installation_details(self):
        """Getter for installation details"""
        L.debug('Start get_installation_details')
        self.progress = 0
        if self.installations:
            progress_sections = 100 / len(self.installations)
        else:
            progress_sections = 100
        progress_increments = progress_sections / 2
        for installation in self.installations:
            L.debug('installation: %s', installation)
            self.progress = self.progress + progress_increments
            # L.debug('Progress: %s', self.progress)
            os.write(self.app.action_pipe, str.encode(str(self.progress)))
            db_check_data, db_check_error = Call.wpcli(
                self.app,
                ['db', 'check'],
                install_path=installation['directory'])
            if db_check_data:
                data = db_check_data.splitlines()
                for line in data:
                    if '_options' in line and 'OK' in line:
                        # L.debug('Line: %s', line)
                        installation['valid_wp_options'] = True
                        self.progress = self.progress + progress_increments
                        # L.debug('Progress: %s', self.progress)
                        progress = str(self.progress)
                        os.write(
                            self.app.action_pipe,
                            progress.encode(encoding='UTF-8'))
                        homedata, _ = Call.wpcli(
                            self.app,
                            [
                                'option',
                                'get',
                                'home'],
                            install_path=installation['directory'])
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
        L.debug('Installations Initialized. AppInstance: %s', self.app)
        self.installation = self.app.state.active_installation
        self.db_info = {
            'name': None,
            'size': None,
            'size_error': None,
            'check_tables': None,
            'check_error': None
        }

    def get_db_size(self):
        """Get database size and name list"""
        progress = 0
        progress_increments = 100 / 2

        # GET DATABASE NAME AND SIZE
        progress = progress + progress_increments
        L.debug('Progress: %s', progress)
        db_info = {
            'name': None,
            'size': None,
            'size_error': None,
            'check_tables': None,
            'check_error': None
        }
        try:
            os.write(self.app.action_pipe, str.encode(str(progress)))
        except OSError as error:
            L.warning('self.app.action_pipe Not Open Yet: %s', error)
        dbsize_result, dbsize_error = Call.wpcli(
            self.app, [
                'db', 'size',
                '--human-readable',
                '--format=json', '--no-color'])
        if dbsize_result:
            result_json = json.loads(dbsize_result)
            L.debug(
                'wp_db_name: %s, wp_db_size:%s',
                result_json[0]['Name'],
                result_json[0]['Size'])
            db_info['name'] = result_json[0]['Name']
            db_info['size'] = result_json[0]['Size']

            dbcheck_result, dbcheck_error = Call.wpcli(
                self.app,
                ['db', 'check'])
            dbcheck_result_list = []
            if dbcheck_result:
                for line in dbcheck_result.splitlines():
                    if db_info['name'] in line:
                        _x = line.split()
                        dbcheck_result_list.append(
                            {
                                'table_name': _x[0],
                                'check_status': _x[1]
                            }
                        )
                db_info['check_tables'] = dbcheck_result_list
            if dbcheck_error:
                db_check_decoded = dbcheck_error.decode(encoding='UTF-8')
                db_info['check_error'] = db_check_decoded
        try:
            dbsize_error.decode(encoding='UTF-8')
        except AttributeError as error:
            db_info['size_error'] = dbsize_error
        else:
            db_info['size_error'] = dbsize_error.decode(encoding='UTF-8')
        # RUN CHECK DB
        progress = progress + progress_increments
        L.debug('Progress: %s', progress)
        try:
            os.write(self.app.action_pipe, str.encode(str(progress)))
        except OSError:
            L.warning('self.app.action_pipe Not Open Yet')
        # L.debug('db_info: %s',self.db_info)
        try:
            os.close(self.app.action_pipe)
        except OSError:
            L.warning('self.app.action_pipe Not Open')
        self.db_info = db_info
        return db_info

    def export(self, file_path=None):
        """installs theme from wordpress.org repo"""

        self.app.wpcli_pipe = self.app.loop.watch_pipe(
            self.app.views.Database.body.update_view)
        L.debug("self.app.wpcli_pipe: %s", self.app.wpcli_pipe)
        if not file_path:
            export_path = self.app.state.homedir
            n_length = 6
            rand_numb = ''.join(
                [
                    "%s" % randint(0, 9) for _ in range(0, n_length)
                ])
            date = datetime.now()
            date = datetime.strftime(
                date,
                "%Y%m%d")
            file_name = self.db_info['name'] + \
                '-' + date + '-' + rand_numb + '.sql'
            file_path = os.path.join(
                export_path,
                file_name)
        else:
            file_path = file_path

        wpcli_thread = Thread(
            target=Call.wpcli_live_response,
            name='wpcli_thread',
            args=[
                self.app,
                self.app.views.Database.body.after_response,
                [
                    'db',
                    'export',
                    file_path
                ]
            ])
        wpcli_thread.start()

    @staticmethod
    def export_db(app, file_path=None):
        """Exports Database"""

        file_path = file_path
        export = Call.wpcli(
            app,
            [
                'db',
                'export',
                file_path
            ])
        if export[0]:
            return True
        else:
            return False

    @staticmethod
    def import_db(app, path):
        """Exports wp database"""
        file_path = path
        import_result = Call.wpcli(
            app,
            [
                'db',
                'import',
                file_path
            ])
        L.debug('Import_results: %s', import_result)
        if import_result[0]:
            L.debug('Import Result:  %s', import_result[0])
            return import_result[0]
        return "Database Import Failed"

    def get_import_list(self):
        """Return list of imports in user's directory"""
        imports = []
        username = getpass.getuser()
        homedir = os.path.expanduser('~%s' % username)
        L.debug("%s Homedir: %s", username, homedir)
        db_name = self.db_info['name']
        L.debug('db_name: %s', db_name)
        for root, _, files in os.walk(homedir, topdown=True):
            for file_name in files:
                if db_name in file_name and 'sql' in file_name:
                    L.debug('Import Found: %s', file_name)
                    if '/.' not in root:
                        _x = os.path.join(root, file_name)
                        imports.append(_x)
        return imports

    def optimize_db(self):
        """Optimize Database"""
        L.debug("Begin Optimize DB")
        # Export Database before optimizing
        self.app.views.actions.revisions.auto_bk(backup_db=True)

        self.app.wpcli_pipe = self.app.loop.watch_pipe(
            self.app.views.Database.body.update_view)
        L.debug("self.app.wpcli_pipe: %s", self.app.wpcli_pipe)

        wpcli_thread = Thread(
            target=Call.wpcli_live_response,
            name='wpcli_thread',
            args=[
                self.app,
                self.app.views.Database.body.after_response,
                [
                    'db',
                    'optimize',
                ]
            ])
        wpcli_thread.start()

    def db_repair(self):
        """Repairs Database"""
        L.debug("Begin Repair DB")
        # Export Database before optimizing
        self.app.views.actions.revisions.auto_bk(backup_db=True)

        self.app.wpcli_pipe = self.app.loop.watch_pipe(
            self.app.views.Database.body.update_view)
        L.debug("self.app.wpcli_pipe: %s", self.app.wpcli_pipe)

        wpcli_thread = Thread(
            target=Call.wpcli_live_response,
            name='wpcli_thread',
            args=[
                self.app,
                self.app.views.Database.body.after_response,
                [
                    'db',
                    'repair',
                ]
            ])
        wpcli_thread.start()

    def db_search(self, query):
        """Searches database"""
        L.debug("Begin DB Search WP Cli")
        result, error = Call.wpcli(
            self.app,
            [
                'db',
                'search',
                query,
            ])
        L.debug('Database Search Result: %s', result)
        if result:
            result = result.splitlines()
            result_dicts = []
            i = 0
            while i < len(result):
                # L.debug('i % 2 %s', i % 2)
                if i % 2 == 0 or i == 0:
                    split_result = result[i].split(':')
                    result_dicts.append({
                        'table': split_result[0],
                        'column': split_result[1]
                    })
                else:
                    split_result = result[i].split(':', 1)
                    L.debug('a : %s', split_result)
                    L.debug('result_dicts: %s', result_dicts)
                    # pylint: disable=invalid-sequence-index
                    result_dicts[int(i / 2)]['row'] = split_result[0]
                    result_dicts[int(i / 2)]['value'] = split_result[1]
                i += 1
            return result_dicts
        elif not error:
            L.debug("No search results")
            return "No Matching Results"
        else:
            L.warning('Database Search error: %s', error)
            return "Database Search Error"

    def search_replace(self, sr_search_term, sr_replace_term, dry_run=True):
        """Search and replace database"""
        L.debug("Begin wp search-replace")
        call_args = [
            'search-replace',
            sr_search_term,
            sr_replace_term,
            '--all-tables',
            '--precise'
        ]
        if dry_run:
            call_args.append('--dry-run')
        results, error = Call.wpcli(
            self.app,
            call_args)
        L.debug('Search & Replace Result: %s', results)
        L.debug('Search & Replace Error: %s', error)
        results_count = ''
        if results:
            results_dicts = []
            results = results.splitlines()
            for result in results:
                if result not in results[0]:
                    if result in results[-1]:
                        split_result = result.split()
                        if dry_run:
                            results_count = split_result[1]
                        else:
                            results_count = split_result[2]
                    else:
                        split_result = result.split('\t')
                        results_dicts.append({
                            "table": split_result[0],
                            "column": split_result[1],
                            "count": split_result[2]
                        })
            L.debug('Search & Replace Result: %s', results_dicts)
            L.debug('Search & Replace Count: %s', results_count)
            return {'results': results_dicts, 'count': results_count}
        else:
            return error


class WpConfig(object):
    """Obtains and modified wp_config information"""

    def __init__(self, app):
        self.app = app
        L.debug('Installations Initialized')
        self.call = Call()
        self.installation = self.app.state.active_installation
        self.wp_config_directive_list = []
        self.wp_config_error = None
        self.progress = 0

    def get_wp_config(self):
        """getter for wp_config data"""
        self.progress = 0
        progress_increments = 100
        self.progress = self.progress + progress_increments
        L.debug('Progress: %s', self.progress)
        L.debug('self.app.action_pipe: %s', self.app.action_pipe)
        os.write(self.app.action_pipe, str.encode(str(self.progress)))
        wp_config_result, wp_config_error = Call.wpcli(
            self.app, [
                'config', 'list',
                '--format=json',
                '--no-color'])
        if wp_config_result:
            # L.debug('wp_config_result: %s', wp_config_result)
            self.wp_config_directive_list = json.loads(wp_config_result)
        if wp_config_error:
            L.debug('wp_config_error: %s', wp_config_result)
            self.wp_config_error = wp_config_error
        try:
            os.close(self.app.action_pipe)
        except OSError:
            L.warning('self.app.action_pipe already closed')

    def set_wp_config(self, directive_name, directive_value):
        """Sets a single wp_config directive.
        This is used by the wp_config display screen edit widgets"""
        return_data, return_error = Call.wpcli(
            self.app, [
                'config',
                'set',
                directive_name,
                directive_value])
        L.debug(
            'Set_Wp_Config Return Data: %s, Return Error: %s',
            return_data, return_error)
        if return_data and 'Success' in return_data:
            return True
        else:
            return False

    def del_wp_config(self, directive_name):
        """Sets a single wp_config directive.
        This is used by the wp_config display screen edit widgets"""
        return_data, return_error = Call.wpcli(
            self.app, [
                'config',
                'delete',
                directive_name
            ])
        L.debug(
            'Set_Wp_Config Return Data: %s, Return Error: %s',
            return_data, return_error)
        if return_data and 'Success' in return_data:
            return True
        else:
            return False

    def re_salt(self):
        "Refreshes the stalts defined in the wp-config.php file"
        return_data, return_error = Call.wpcli(
            self.app, [
                'config',
                'shuffle-salts'
            ])
        L.debug(
            'Set_Wp_Config Return Data: %s, Return Error: %s',
            return_data, return_error)


class Themes(object):
    """Candles 'wp theme' wp-cli calls"""

    def __init__(self, app):
        self.app = app
        self.call = Call()
        # self.installation = self.app.state.active_installation

    def get_theme_root(self):
        """Obtain the site's theme root"""

        result, error = Call.wpcli(
            self.app,
            [
                'theme',
                'path',
            ])
        if result:
            return result
        else:
            L.warning("Error obtaining theme_root: %s", error)
            return False

    def get_list(self):
        """get's theme list"""

        progress = 0
        try:
            os.write(self.app.action_pipe, str.encode(str(progress)))
        except OSError:
            L.warning('Action Pipe not opened')
        fields = ['name', 'status', 'update', 'version',
                  'update_version', 'update_package', 'title', 'description']
        args = '--fields=' + ','.join(fields)
        results, error = Call.wpcli(
            self.app,
            [
                'theme',
                'list',
                args,
                '--format=json'
            ])
        result_json = json.loads(results)
        L.debug('get_list results: %s', result_json)
        L.debug('get_list errors: %s', error)
        try:
            os.close(self.app.action_pipe)
        except OSError:
            L.warning('Action Pipe already closed')
        if result_json:
            return result_json

    def get_details(self, theme_name):
        """Gets theme details"""

        result, error = Call.wpcli(
            self.app,
            [
                'theme',
                'get',
                theme_name,
                '--format=json'
            ])
        if result:
            result_json = json.loads(result)
            L.debug('get_list results: %s', result_json)
            L.debug('get_list errors: %s', error)
            if result_json:
                return result_json
        else:
            return False

    def activate(self, theme_name):
        """Activates theme"""

        self.app.wpcli_pipe = self.app.loop.watch_pipe(
            self.app.views.Themes.body.update_view)
        L.debug("self.app.wpcli_pipe: %s", self.app.wpcli_pipe)
        wpcli_thread = Thread(
            target=Call.wpcli_live_response,
            name='wpcli_thread',
            args=[
                self.app,
                self.app.views.Themes.body.after_response,
                [
                    'theme',
                    'activate',
                    theme_name
                ]
            ])
        wpcli_thread.start()

    def update(self, theme_name):
        """Updates theme"""

        self.app.wpcli_pipe = self.app.loop.watch_pipe(
            self.app.views.Themes.body.update_view)
        L.debug("self.app.wpcli_pipe: %s", self.app.wpcli_pipe)
        wpcli_thread = Thread(
            target=Call.wpcli_live_response,
            name='wpcli_thread',
            args=[
                self.app,
                self.app.views.Themes.body.after_response,
                [
                    'theme',
                    'update',
                    theme_name
                ]
            ])
        wpcli_thread.start()

    def uninstall(self, theme_name):
        """uninstalls theme"""

        self.app.wpcli_pipe = self.app.loop.watch_pipe(
            self.app.views.Themes.body.update_view)
        L.debug("self.app.wpcli_pipe: %s", self.app.wpcli_pipe)
        wpcli_thread = Thread(
            target=Call.wpcli_live_response,
            name='wpcli_thread',
            args=[
                self.app,
                self.app.views.Themes.body.after_response,
                [
                    'theme',
                    'uninstall',
                    theme_name
                ]
            ])
        wpcli_thread.start()

    def install(self, theme_name):
        """installs theme from wordpress.org repo"""

        self.app.wpcli_pipe = self.app.loop.watch_pipe(
            self.app.views.Themes.body.update_view)
        L.debug("self.app.wpcli_pipe: %s", self.app.wpcli_pipe)
        wpcli_thread = Thread(
            target=Call.wpcli_live_response,
            name='wpcli_thread',
            args=[
                self.app,
                self.app.views.Themes.body.after_response,
                [
                    'theme',
                    'install',
                    theme_name
                ]
            ])
        wpcli_thread.start()


class Plugins(object):
    """ Handles 'wp plugin' wpcli functions"""

    def __init__(self, app):
        self.app = app

    def get_plugin_list(self):
        """Obtain list of plugins"""

        fields = ['name', 'status', 'update', 'version',
                  'update_version']
        args = '--fields=' + ','.join(fields)
        progress = 0
        try:
            os.write(self.app.action_pipe, str.encode(str(progress)))
        except OSError:
            L.warning('Action Pipe not opened')
        result, error = Call.wpcli(
            self.app,
            [
                'plugin',
                'list',
                args,
                '--format=json'
            ]
        )
        try:
            os.close(self.app.action_pipe)
        except OSError:
            L.warning('Action Pipe already closed')
        if result:
            result_json = json.loads(result)
            if result_json:
                L.debug('Result_json: %s', result_json)
                return result_json
            else:
                return False
        else:
            L.warning('Error: %s', error)
            return False

    def get_details(self, plugin_name):
        """Get plugin details"""

        result, error = Call.wpcli(
            self.app,
            [
                'plugin',
                'get',
                plugin_name,
                '--format=json'
            ])
        if result:
            result_json = json.loads(result)
            L.debug('get_list results: %s', result_json)
            L.debug('get_list errors: %s', error)
            if result_json:
                return result_json
        else:
            return False

    def get_plugin_path(self, plugin_name=None):
        """Get path to plugin dir, or path to plugin_root """

        if not plugin_name:
            args = [
                'plugin',
                'path',
                '--dir'
            ]
        else:
            args = [
                'plugin',
                'path',
                plugin_name,
                '--dir'
            ]
        result, error = Call.wpcli(
            self.app,
            args)
        if result:
            return result.rstrip()
        else:
            L.warning('Error obtaining plugin_path: %s', error)
            return False

    def install(self, plugin_name):
        """Installs plugin from wordpress repo"""

        self.app.wpcli_pipe = self.app.loop.watch_pipe(
            self.app.views.Plugins.body.update_view)
        L.debug("self.app.wpcli_pipe: %s", self.app.wpcli_pipe)
        wpcli_thread = Thread(
            target=Call.wpcli_live_response,
            name='wpcli_thread',
            args=[
                self.app,
                self.app.views.Plugins.body.after_response,
                [
                    'plugin',
                    'install',
                    plugin_name
                ]
            ])
        wpcli_thread.start()

    def update(self, plugin_name,):
        """Updates a plugin """

        L.debug('plugin_name: %s', plugin_name)
        self.app.wpcli_pipe = self.app.loop.watch_pipe(
            self.app.views.Plugins.body.update_view)
        L.debug("self.app.wpcli_pipe: %s", self.app.wpcli_pipe)
        wpcli_thread = Thread(
            target=Call.wpcli_live_response,
            name='wpcli_thread',
            args=[
                self.app,
                self.app.views.Plugins.body.after_response,
                [
                    'plugin',
                    'update',
                    plugin_name
                ]
            ])
        wpcli_thread.start()

    def activate(self, plugin_name):
        """Activates a plugin"""

        self.app.wpcli_pipe = self.app.loop.watch_pipe(
            self.app.views.Plugins.body.update_view)
        L.debug("self.app.wpcli_pipe: %s", self.app.wpcli_pipe)
        wpcli_thread = Thread(
            target=Call.wpcli_live_response,
            name='wpcli_thread',
            args=[
                self.app,
                self.app.views.Plugins.body.after_response,
                [
                    'plugin',
                    'activate',
                    plugin_name
                ]
            ])
        wpcli_thread.start()

    def deactivate(self, plugin_name):
        """Deactivates a plugin"""

        self.app.wpcli_pipe = self.app.loop.watch_pipe(
            self.app.views.Plugins.body.update_view)
        L.debug("self.app.wpcli_pipe: %s", self.app.wpcli_pipe)
        wpcli_thread = Thread(
            target=Call.wpcli_live_response,
            name='wpcli_thread',
            args=[
                self.app,
                self.app.views.Plugins.body.after_response,
                [
                    'plugin',
                    'deactivate',
                    plugin_name
                ]
            ])
        wpcli_thread.start()

    def uninstall(self, plugin_name):
        """Uninstalls a plugin"""

        self.app.wpcli_pipe = self.app.loop.watch_pipe(
            self.app.views.Plugins.body.update_view)
        L.debug("self.app.wpcli_pipe: %s", self.app.wpcli_pipe)
        wpcli_thread = Thread(
            target=Call.wpcli_live_response,
            name='wpcli_thread',
            args=[
                self.app,
                self.app.views.Plugins.body.after_response,
                [
                    'plugin',
                    'uninstall',
                    plugin_name
                ]
            ])
        wpcli_thread.start()

    def get_active_plugins(self):
        """Gets list of all active plugins"""

        result, error = Call.wpcli(
            self.app,
            [
                'option',
                'get',
                'active_plugins',
                '--format=json'
            ])
        if result:
            return result
        else:
            return error

    def set_active_plugins(self, plugins):
        """Sets active plugins to match exported list"""

        L.debug('Re-Activating Plugins: %s', plugins)
        result, error = Call.wpcli(
            self.app,
            [
                'option',
                'update',
                'active_plugins',
                plugins,
                '--format=json'
            ])
        if result:
            return result
        else:
            return error


class Call(object):
    """opens a subprocess to run wp-cli command"""
    @staticmethod
    def wpcli(app, arguments, skip_themes=True, skip_plugins=True,
              install_path=None):
        """runs_wp-cli command"""
        if install_path:
            path = install_path
        else:
            path = app.state.active_installation['directory']
        L.debug('Begin wp-cli command: %s', arguments)
        popen_args = ['wp']
        for argument in arguments:
            popen_args.append(argument)
        popen_args.append('--path='+path)
        if skip_themes:
            popen_args.append('--skip-themes')
        if skip_plugins:
            popen_args.append('--skip-plugins')
        data, error = subprocess.Popen(
            popen_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()
        return data.decode('UTF-8'), error.decode('UTF-8')

    @staticmethod
    def wpcli_live_response(app, callback,
                            arguments, skip_themes=True, skip_plugins=True):
        # L.debug('pipe: %s, path: %s, arguments: %s', pipe, path, arguments)
        """runs_wp-cli command"""
        L.debug('Begin wp-cli command: %s', arguments)
        path = app.state.active_installation['directory']
        popen_args = ['wp']
        for argument in arguments:
            popen_args.append(argument)
        popen_args.append('--path='+path)
        if skip_themes:
            popen_args.append('--skip-themes')
        if skip_plugins:
            popen_args.append('--skip-plugins')
        proc = subprocess.Popen(
            popen_args,
            stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline()
            if proc.poll() or line == b'':
                os.close(app.wpcli_pipe)
                break
            else:
                L.debug('proc line: %s', line)
                os.write(app.wpcli_pipe, line)
        callback()
