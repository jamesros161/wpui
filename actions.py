from wpcli import Installations
class Actions():
    def __init__(self,app):
        self.app = app
    def get_installations(self):
        installations = Installations(self.app.L)