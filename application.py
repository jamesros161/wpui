"""This module contains classes for handling
the overall flow and state of the application

Raises:
    U.ExitMainLoop: Exits the application
"""
import urwid as U
from settings import Settings
from logmod import Log
from widgets import CustomWidgets
from menus import Menus
from views import Views

S = Settings()
L = Log()
W = CustomWidgets()


class App(object):
    """App Class is a container for the state, views, menu, loop, and frame classes"""
    def __init__(self):
        L.debug("App Class Initializing")
        self.S = S
        self.frame = U.Frame(U.Filler(W.get_text('body', 'Loading...Please Wait', 'center')))
        self.loop = U.MainLoop(self.frame,
                               S.display['palette'],
                               unhandled_input=self.unhandled_input,
                               handle_mouse=False)
        self.state = State(self)
        self.views = Views(self)
        self.menus = Menus(self)
    def exit(self, *args):
        """Exits the applications

        Raises:
            U.ExitMainLoop: Exits the application
        """
        L.debug("Args: %s", args)
        raise U.ExitMainLoop()
    def unhandled_input(self, key):
        """Manages input that is not handled by a
        specific widget

        Arguments:
            key {str} -- the str/char representation of the
                         key pressed
        """
        if isinstance(key, basestring):
            #raw = loop.screen.get_input(raw_keys=True)
            #debug('raw: %s', raw)
            if key in 'ctrl e':
                self.views.activate(self, 'Quit')
            if key in 'tab':
                if self.frame.focus_position == 'footer':
                    self.frame.focus_position = 'body'
                else:
                    if S.display['menu_enabled']:
                        self.frame.focus_position = 'footer'
            if 'end' in key:
                self.state.go_back()
            if 'home' in key:
                self.state.go_back()
class State(object):
    """This is the state manager used to track movement between views,
    and allow user to go backwards and forwards
    """
    def __init__(self, app):
        self.app = app
        L.debug('App.State Initializing')
        self.active_view = None
        self.active_view_name = None
        self.previous_view = None
        self.previous_view_name = None
        self.view_count = -1
        self.view_chain = []
        self.view_chain_pos = -1
        self.active_installation = None
    def update_state(self, state_prop, value):
        """Update's a specified property of the application state

        Arguments:
            state_prop {str} -- the name of the prop to update
            value {str} -- the value you are setting the property to
        """
        try:
            getattr(self, state_prop)
        except AttributeError:
            L.warning('App.State.%s Does not Exist! Propery Not Updated', state_prop)
        else:
            setattr(self, state_prop, value)
            if hasattr(value, 'name'):
                L.debug('App.State.%s updated to %s', state_prop, value.name)
            else:
                L.debug('App.State.%s updated to %s', state_prop, value)
    def set_installation(self, obj, installation):
        """Sets the currently selected wp installation

        Arguments:
            obj {obj} -- the object / method that called this method
            installation {dict} -- dictionary of the active installation
        """
        L.debug("Obj Arg: %s", obj)
        self.active_installation = installation
        if self.active_installation['home_url']:
            sub_title = self.active_installation['directory'] + \
                ' ( ' + self.active_installation['home_url'] + ' )'
        else:
            sub_title = self.active_installation['directory']
        self.app.S.display['sub_title'] = sub_title
        L.debug('self.app.S.display["subtitle"]: %s', self.app.S.display['sub_title'])
        self.app.views.activate(self.app, 'GetWpConfig')
        _x = W.get_header('set_installation', S.display['title'], sub_title)
        self.app.frame.contents.__setitem__('header', [_x, None])

    def get_state(self, state_prop):
        """class getter for state properties

        Arguments:
            state_prop {str} -- State Property

        Returns:
            var -- returns pointer to the state property
        """
        try:
            getattr(self, state_prop)
        except AttributeError:
            L.warning('App.State.%s Does not Exist! Propery Not Retrievable', state_prop)
            return False
        else:
            _x = getattr(self, state_prop)
            if hasattr(_x, 'name'):
                L.debug('App.State.%s updated to %s', state_prop, _x.name)
            else:
                L.debug('App.State.%s value is: %s', state_prop, _x)
            return _x
    def set_view(self, view):
        """This method is called whenever user moves to a new view.
        This records the new view, and moves the old active_view to
        the previous view variable. This also tracks the user's position
        in the view_chain

        Arguments:
            view {obj} -- [the view instance]
        """
        L.debug('Current View: %s %s', view.name, view)
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
        L.debug('Preview View: %s %s', self.previous_view_name, self.previous_view)
        L.debug('View Chain Pos: %s, View Chain: %s', self.view_chain_pos, self.view_chain)
    def set_view_chain_pos(self, adjustment):
        """This set's the user's position in the view chain
        when setting a activating a new view

        Arguments:
            adjustment {int} -- Whether to adjust the view + or -

        Returns:
            boolean -- True if the position change succeeded
                        False if it did not
        """
        if adjustment > 0 and self.get_view_chain_pos() < len(self.view_chain) - 1:
            self.view_chain_pos += adjustment
            return True
        if adjustment < 0 and self.get_view_chain_pos() > 0:
            self.view_chain_pos += adjustment
            return True
        else:
            return False
    def get_view_from_chain(self, chain_pos):
        """Obtaines a view based on the provided chain_pos

        Arguments:
            chain_pos {int} -- Chain position

        Returns:
            obj -- view
        """
        return self.view_chain[chain_pos]
    def get_view_chain_pos(self):
        """Obtains the chain pos of the current view_chain_pos

        Returns:
            [type] -- [description]
        """
        return self.view_chain_pos
    def go_back(self, *args):
        """Moves user back one position in view chain
        """
        L.debug("Args: %s", args)
        L.debug('View Chain Pos: %s', self.get_view_chain_pos())
        if self.set_view_chain_pos(-1):
            _x = self.get_view_from_chain(self.get_view_chain_pos())
            L.debug('Going back to view: %s', _x.name)
            _x.reload()
    def go_forward(self):
        """Moves user forward one position in view chain
        """
        if self.set_view_chain_pos(1):
            _x = self.get_view_from_chain(self.get_view_chain_pos())
            _x.reload()
