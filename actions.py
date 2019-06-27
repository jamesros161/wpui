from wpcli import Installations
class Actions():
    def __init__(self,app):
        self.app = app
    def get_installations(self):
        self.app.L.debug("get_installations Action Started")
        installations = Installations(self.app)