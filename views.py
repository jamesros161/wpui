"""Contains methods and classes for activing and composing views"""
import json
from threading import Thread
from logmod import Log
import body_widgets
from actions import Actions
L = Log()
W = body_widgets.CustomWidgets()
class Views(object):
    """Stores individual View objects, and activates them"""
    def __init__(self, app):
        self.app = app
        self.state = app.state
        with open('views.json', 'r') as views:
            views_json = json.load(views)
        #L.debug('views_json: %s', views_json)
        for key, value in views_json.items():
            setattr(self, key, View(app, key, value))
    def activate(self, app, *args, **kwargs):
        """Activates the selected view"""
        L.debug('views.activate args: %s, kwargs: %s', args, kwargs)
        activating_view = getattr(self, args[0])
        if (not 'Home' in activating_view.name and
                not 'Installs' in activating_view.name and
                not 'Quit' in activating_view.name):
            if not self.app.state.active_installation:
                self.app.views.activate(app, 'Installs')
            else:
                if not "no_view_chain" in activating_view.view_type:
                    self.state.view_chain_pos += 1
                    self.state.set_view(activating_view)
                activating_view.start()
        else:
            if not "no_view_chain" in activating_view.view_type:
                self.state.view_chain_pos += 1
                self.state.set_view(activating_view)
            activating_view.start()
class View(object):
    """View Objects old the various parts of a given view
    such as the header, footer, body, etc"""
    def __init__(self, app, name, view_json_data):
        self.app = app
        #L.debug("View %s Initialized", name)
        self.name = name
        self.footer = None
        self.body = None
        self.action = None
        self.action_thread = None
        self.actions = Actions(app)
        self.view_type = view_json_data['view_type']
        self.title = view_json_data['title']
        self.sub_title = view_json_data['sub_title']
        self.action_on_load = view_json_data['action_on_load']
        self.header = None
    def start(self):
        """Starts the loading, and showing of the activated view
        Typically called by Views.activate, but sometimes called
        through other means"""
        self.set_view_body()
        self.show_header()
        self.show_body()
        self.show_footer()
        if self.view_type == 'no_input':
            self.set_focus('footer')
        else:
            self.set_focus('body')
        if self.action_on_load:
            self.app.loop.draw_screen()
            L.debug('This View has an action to be run on load')
            self.action = getattr(self.actions, self.action_on_load)
            self.action_thread = Thread(target=self.action, name='action_thread')
            self.action_thread.start()
    def reload(self):
        """Reloads a previously activated view. Used by State.go_back and
        State.go_forward"""
        self.show_header()
        self.show_body()
        self.show_footer()
    def show_header(self):
        """retrieves a header widget and sets the widget to the header section
        of App.frame"""
        if self.title:
            title = self.title
        else:
            title = self.app.S.display['title']
        if self.sub_title:
            sub_title = self.sub_title
        else:
            sub_title = self.app.S.display['sub_title']
        self.header = W.get_header(self.name, title, sub_title)
        self.app.frame.contents.__setitem__('header', [self.header, None])
    def show_body(self):
        """retrieves a body widget and sets the widget to the body section
        of App.frame"""
        self.app.frame.contents.__setitem__('body', [self.body.widget, None])
    def show_footer(self):
        """retrieves a footer widget and sets the widget to the footer section
        of App.frame"""
        self.footer = W.get_footer(self.name, self.app)
        self.app.frame.contents.__setitem__('footer', [self.footer, None])
    def draw_screen(self):
        """Re-draws the screen"""
        self.app.loop.draw_screen()
    def set_focus(self, focus_position):
        """Sets the cursor focus to the specified frame section"""
        self.app.frame.set_focus(focus_position)
    def set_view_body(self, *args):
        """sets the frame's body section to the specified body"""
        body_class = getattr(body_widgets, self.name)
        self.body = body_class(self.app, user_args=args, calling_view=self)
