"""Class for importing Json config files"""
import os
import json
class Config(object):
    """Class for importing Json config files"""
    @staticmethod
    def load(filename):
        """Loads json files for app config"""
        try:
            file_dir = os.path.dirname(__file__)
            path = os.path.join(file_dir, filename)
            with open(path, 'r') as menus:
                file_object = json.load(menus)
        except IOError:
            try:
                file_dir = os.path.dirname('/etc/wpui/')
                path = os.path.join(file_dir, filename)
                with open(path, 'r') as menus:
                    file_object = json.load(menus)
            except IOError:
                print('JSON FILES MISSING. CHECK INSTALLATION PATH')
            else:
                file_dir = os.path.dirname('/etc/wpui/')
                path = os.path.join(file_dir, filename)
                with open(path, 'r') as menus:
                    file_object = json.load(menus)
                return file_object
        else:
            file_dir = os.path.dirname(__file__)
            path = os.path.join(file_dir, filename)
            with open(path, 'r') as menus:
                file_object = json.load(menus)
            return file_object
