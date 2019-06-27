import os, sys, getpass, subprocess, json
from datetime import datetime
class Installations():
    def __init__(self,app):
        self.app = app
        self.app.L.debug('Installations Initialized')
        call = Call(self.app.L)
        self.username = getpass.getuser()
        self.homedir = os.path.expanduser('~%s' % self.username)
        self.installations = self.get_installation_dirs()
        for installation in self.installations:
            installation['call_process'] = call.wpcli(installation['directory'],['db','check',])
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
        for installation in self.installations:
            self.app.loop.watch_file(installation['call_process'].stdout,self.show_installation_details)
    def show_installation_details(self):
        for installation in self.installations:
            self.app.L.debug("call_process stdout: %s", installation['call_process'].communicate())
class Call():
    def __init__(self,L):
        self.L = L
    def wpcli(self, path, arguments):
        popen_args = ['wp']
        for argument in arguments:
            popen_args.append(argument)
        popen_args.append('--path='+path)

        call_process = subprocess.Popen(popen_args, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
            )
        self.L.debug("WPCLI Call Process: %s", call_process)
        return call_process

