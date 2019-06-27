import os, sys, getpass, subprocess, json
from datetime import datetime
class Installations():
    def __init__(self,L):
        L.debug('Installations Initialized')
        call = Call(L)
        self.username = getpass.getuser()
        self.homedir = os.path.expanduser('~%s' % self.username)
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
                data,error = call.wpcli(root,['db','check','--skip-{plugin,theme}s'])
                x['error'] = error
                if data:
                    data = data.splitlines()
                    for line in data:
                        if '_options' in line and 'OK' in line:
                            x['valid_wp_options'] = True
                            homedata,_ = call.wpcli(root,['option','get','home','--skip-{plugin,theme}s'])
                            if homedata:
                                x['home_url'] = homedata
                        if 'Success: Database checked' in line:
                            x['wp_db_check_success'] = True
                installations.append(x)
                #print(os.path.join(root, name))
        L.debug("WP Installation for user %s: %s", self.username, installations)
class Call():
    def __init__(self,L):
        self.L = L
    def wpcli(self, path, arguments):
        run_starttime = datetime.now()
        self.L.debug("WPCLI Call Started: %s", run_starttime)
        popen_args = ['wp']
        for argument in arguments:
            popen_args.append(argument)
        popen_args.append('--path='+path)

        reqOutput, reqError = subprocess.Popen(popen_args, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
            ).communicate()
        data = reqOutput
        error = reqError
        #data = json.loads(reqOutput)
        #error = json.loads(reqError)
        #self.L.debug("Data: %s \nError: %s", data,error)
        command_runtime = datetime.now() - run_starttime
        self.L.debug("WPCLI Command Runtime: %s", command_runtime)
        return data,error

