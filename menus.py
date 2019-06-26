import json
class Menus():
    def __init__(self,L):
        with open('menus.json','r') as menus:
           menus_json = json.load(menus)
        #L.debug('Menus_json: %s', menus_json)#pylint: disable=no-member
        for key,value in menus_json.items():
            setattr(self,key,Menu(L,key,value))
class Menu():
    def __init__(self,L,menu_name, menu_items):
        L.debug("Menu %s Initialized",menu_name)#pylint: disable=no-member
        self.name = menu_name
        self.items = menu_items
        L.debug("Menu Items: %s", self.items)