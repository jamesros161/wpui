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
    def exit(self,*args):
        raise U.ExitMainLoop()
    def unhandled_input(self,key):
        if type(key) == str:
            #raw = loop.screen.get_input(raw_keys=True)
            #debug('raw: %s', raw)
            if key in 'ctrl e':
                self.views.activate(self,'quit')
            if key in 'tab':
                if self.frame.focus_position == 'footer':
                    self.frame.focus_position = 'body'
                else:
                    if self.S.display['menu_enabled']:
                        self.frame.focus_position = 'footer'
            if 'end' in key:
                    self.state.go_back()
            if 'home' in key:
                    self.state.go_back()
class State():
    def __init__(self,app):
        self.app = app
        self.L = app.L #pylint: disable=no-member
        self.L.debug('App.State Initializing')
        self.active_view = None
        self.previous_view = None
        self.view_count = -1
        self.view_chain = []
        self.view_chain_pos = -1
        self.active_installation = None
    def update_state(self,state_prop,value):
        try:
            getattr(self,state_prop)
        except:
            self.L.warning('App.State.%s Does not Exist! Propery Not Updated', state_prop) #pylint: disable=no-member
        else:
            setattr(self,state_prop,value)
            if hasattr(value,'name'):
                self.L.debug('App.State.%s updated to %s', state_prop, value.name)
            else:
                self.L.debug('App.State.%s updated to %s', state_prop, value)
    def set_installation(self,obj,installation):
        self.active_installation = installation
        if self.active_installation['home_url']:
            subtitle = self.active_installation['home_url']
        else:
            subtitle = self.active_installation['directory']
        self.app.S.display['subtitle'] = subtitle
        x = self.app.W.get_header('set_installation',None,subtitle)
        self.app.frame.contents.__setitem__('header',[x,None])

    def get_state(self,state_prop):
        try:
            getattr(self,state_prop)
        except:
            self.L.warning('App.State.%s Does not Exist! Propery Not Retrievable', state_prop)
            return False
        else:
            x = getattr(self,state_prop)
            if hasattr(x,'name'):
                self.L.debug('App.State.%s updated to %s', state_prop, x.name)
            else:
                self.L.debug('App.State.%s value is: %s', state_prop, x)
            return x
    def set_view(self, view):
        self.L.debug('Current View: %s %s', view.name,view)
        if self.active_view:
            self.previous_view = self.active_view
        else:
            self.previous_view = None
        self.active_view = view
        self.active_view_name = self.active_view.name
        if self.previous_view:
            self.previous_view_name = self.previous_view.name
        else:
            self.previous_view_name = None
        if len(self.view_chain) > self.view_chain_pos:
            self.view_chain.insert(self.view_chain_pos, view)
        else:
            self.view_chain.append(view)
        self.view_chain = self.view_chain[0:self.view_chain_pos + 1]
        self.L.debug('Preview View: %s %s', self.previous_view_name, self.previous_view)
        self.L.debug('View Chain Pos: %s, View Chain: %s', self.view_chain_pos, self.view_chain)
    def set_view_chain_pos(self,adjustment):
        if adjustment > 0 and self.get_view_chain_pos() < len(self.view_chain) - 1:
            self.view_chain_pos += adjustment
            return True
        if adjustment < 0 and self.get_view_chain_pos() > 0:
            self.view_chain_pos += adjustment
            return True
        else:
            #debug('Length of view_chain (%s) does not allow adjusting chain_pos from %s by %s positions', len(state.view_chain), state.get_view_chain_pos(), adjustment)
            return False
    def get_view_from_chain(self,chain_pos):
        return self.view_chain[chain_pos]
    def get_view_chain_pos(self):
        return self.view_chain_pos
    def go_back(self, *args):
        self.L.debug('View Chain Pos: %s', self.get_view_chain_pos())
        if self.set_view_chain_pos(-1):
            x = self.get_view_from_chain(self.get_view_chain_pos())
            self.L.debug('Going back to view: %s', x.name)
            x.reload()
            #debug('Column Button Action: %s, user_data: %s', body.listDisplayCols[0].contents[0][0].on_press_action, body.listDisplayCols[0].contents[0][0].user_data)
    def go_forward(self):
        if self.set_view_chain_pos(1):
            x = self.get_view_from_chain(self.get_view_chain_pos())
            x.reload()