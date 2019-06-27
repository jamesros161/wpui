import os, sys, getpass, subprocess
class Installations():
    def __init__(self,L):
        self.username = getpass.getuser()
        self.homedir = os.path.expanduser('~%s' % self.username)
        installation_dirs = []
        for root, dirs, files in os.walk(self.homedir, topdown=True):
            if 'wp-config.php' in files:
                installation_dirs.append(root)
                #print(os.path.join(root, name))
        L.debug("WP Installation Directories for user %s: %s", self.username, installation_dirs)
