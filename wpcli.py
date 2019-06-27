import os, sys, getpass, subprocess, json
class Installations():
    def __init__(self,L):
        L.debug('Installations Initialized')
        call = Call(L)
        self.username = getpass.getuser()
        self.homedir = os.path.expanduser('~%s' % self.username)
        installation_dirs = []
        for root, dirs, files in os.walk(self.homedir, topdown=True):
            if 'wp-config.php' in files:
                call.wpcli(root,['db','check'])
                installation_dirs.append(root)
                #print(os.path.join(root, name))
        L.debug("WP Installation Directories for user %s: %s", self.username, installation_dirs)
class Call():
    def __init__(self,L):
        self.L = L
    def wpcli(self, path, arguments):

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
        self.L.debug("Data: %s \nError: %s", data,error)

