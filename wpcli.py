import os, sys, getpass, subprocess, json
from datetime import datetime
class Installations():
    def __init__(self,app):
        self.app = app
        self.app.L.debug('Installations Initialized')
        self.call = Call(self.app.L)
        self.username = getpass.getuser()
        self.homedir = os.path.expanduser('~%s' % self.username)
        self.installations = self.get_installation_dirs()
        self.get_installation_details()
                #x['error'] = error
                #if data:
                #    data = data.splitlines()
                #    for line in data:
                #        if '_options' in line and 'OK' in line:
                #            x['valid_wp_options'] = True
                #            homedata,_ = call.wpcli(root,['option','get','home','--skip-plugins','--skip-themes'])
                #            if homedata:
                #                x['home_url'] = homedata
                #        if 'Success: Database checked' in line:
                #            x['wp_db_check_success'] = True
                #installations.append(x)
                #print(os.path.join(root, name))
        self.app.L.debug("WP Installation for user %s: %s", self.username, self.installations)
    def get_installation_dirs(self):
        installations = []
        for root,_,files in os.walk(self.homedir, topdown=True):
            if 'wp-config.php' in files:
                if not '/.' in root:
                    x = {
                        'directory' : root,
                        'home_url' : '',
                        'valid_wp_options' : False,
                        'wp_db_check_success' : False,
                        'wp_db_error' : ''
                    }
                    installations.append(x)
        return installations
    def get_installation_details(self):
        self.app.L.debug('Start get_installation_details')
        self.progress = 0
        progress_sections = 100 / len(self.installations)
        progress_increments = progress_sections / 2
        for installation in self.installations:
            self.progress = self.progress + progress_increments
            self.app.L.debug('Progress: %s', self.progress)
            os.write(self.app.action_pipe,str(self.progress))
            db_check_data,db_check_error = self.call.wpcli(installation['directory'],['db','check'])
            if db_check_data:
                data = db_check_data.splitlines()
                for line in data:
                    if '_options' in line and 'OK' in line:
                        self.app.L.debug('Line: %s', line)
                        installation['valid_wp_options'] = True
                        self.progress = self.progress + progress_increments
                        self.app.L.debug('Progress: %s', self.progress)
                        os.write(self.app.action_pipe,str(self.progress))
                        homedata,_ = self.call.wpcli(installation['directory'],['option','get','home','--skip-plugins','--skip-themes'])
                        if homedata:
                            installation['home_url'] = homedata.rstrip()
                    if 'Success: Database checked' in line:
                        installation['wp_db_check_success'] = True
            if db_check_error:
                self.app.L.debug('Line: %s', line)
                installation['wp_db_error'] = db_check_error
        os.close(self.app.action_pipe)
class Call():
    def __init__(self,L):
        self.L = L
    def wpcli(self, path, arguments):
        popen_args = ['wp']
        for argument in arguments:
            popen_args.append(argument)
        popen_args.append('--path='+path)

        data,error = subprocess.Popen(popen_args, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
            ).communicate()
        return data,error

