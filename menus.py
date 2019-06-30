"""Imports Menus from associated menus.json file"""

import json
class Menus(object):
    """Imports Menus from associated menus.json file"""
    def __init__(self, app):
        self.app = app
        with open('menus.json', 'r') as menus:
            menus_json = json.load(menus)
        for key, value in menus_json.items():
            setattr(self, key, Menu(app, key, value))
    def get_menu(self, menu_name):
        """getter for view's menu

        Returns:
            boolean, attr
        """
        try:
            getattr(self, menu_name)
        except AttributeError:
            self.app.L.warning("No Menu Exists by the name %s!!! Menu Retrieval Failed!", menu_name)
            return False
        else:
            return getattr(self, menu_name)
class Menu(object):
    """Individual menu object for each view"""
    def __init__(self, app, menu_name, menu_items):
        #app.L.debug("Menu %s Initialized",menu_name)#pylint: disable=no-member
        self.name = menu_name
        self.items = menu_items
        app.L.debug("Menu Items: %s", self.items)
