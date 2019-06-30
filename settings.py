"""imports settings from settings.json"""
import json
class Settings(object):
    """Class container for settings dict's"""
    def __init__(self):
        self.imported_settings = {}
        with open('settings.json', 'r') as settings:
            #self.imported_settings = settings.read()
            self.imported_settings = json.load(settings)
            for key, value in self.imported_settings.items():
                setattr(self, key, value)
