import urwid as U
import json
from menus import Menus
from views import Views
class App():
    def __init__(self,S,L,W):
        L.debug("App Class Initializing")
        self.S = S
        self.L = L
        self.W = W
        self.frame = U.Frame(U.Filler(self.W.get_text('body','Loading...Please Wait', 'center')))
        self.loop = U.MainLoop(self.frame, self.S.display['palette'], unhandled_input=self.unhandled_input,handle_mouse=False)
        self.state = State(self)
        self.views = Views(self)
        self.menus = Menus(self)
     
    def unhandled_input(self,key):
        if type(key) == str:
            #raw = loop.screen.get_input(raw_keys=True)
            #debug('raw: %s', raw)
            if key in 'ctrl e':
                self.L.debug("ExitMainLoop")
                raise U.ExitMainLoop()
class State():
    def __init__(self,app):
        self.L = app.L #pylint: disable=no-member
        self.L.debug('App.State Initializing')
        self.active_view = None
        self.previous_view = None
        self.view_count = -1
        self.view_chain = []
        self.view_chain_pos = -1
    def update_state(self,state_prop,value):
        try:
            getattr(self,state_prop)
        except:
            self.L.warning('App.State.%s Does not Exist! Propery Not Updated', state_prop) #pylint: disable=no-member
        else:
            setattr(self,state_prop,value)
            self.L.debug('App.State.%s updated to %s', state_prop, value)
    def get_state(self,state_prop):
        try:
            getattr(self,state_prop)
        except:
            self.L.warning('App.State.%s Does not Exist! Propery Not Retrievable', state_prop)
            return False
        else:
            x = getattr(self,state_prop)
            self.L.debug('App.State.%s value is: %s', state_prop, x)
            return x