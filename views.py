"""Contains methods and classes for activing and composing views"""
from threading import Thread
from logmod import Log
from config import Config
import body_widgets
from actions import Actions
L = Log()
W = body_widgets.CustomWidgets()


class Views(object):
    """Stores individual View objects, and activates them"""

    def __init__(self, app):
        self.app = app
        self.state = app.state
        self.actions = Actions(self.app)
        views_json = Config.load('views.json')
        for key, value in views_json.items():
            setattr(self, key, View(app, self, key, value))

    def activate(self, button, user_data):
        """Activates the selected view"""
        L.debug('button: %s, user_data: %s', button, user_data)

        if 'view' in user_data.keys():
            activating_view_name = user_data['view']
        else:
            activating_view_name = 'Invalid'

        try:
            getattr(self, activating_view_name)
        except AttributeError:
            L.warning('There is no View named %s', activating_view_name)
        else:
            activating_view = getattr(self, activating_view_name)

        exempt_views = ['Home', 'Installs', 'Quit']
        if any(item in activating_view.name for item in exempt_views):
            if "no_view_chain" not in activating_view.view_type:
                self.state.view_chain_pos += 1
                self.state.set_view(activating_view)
            L.debug('About to activate view: %s', activating_view.name)
            activating_view.start(user_data)
        else:
            if not self.app.state.active_installation:
                activating_view = getattr(self, 'Installs')
            else:
                activating_view.start(user_data)
            if "no_view_chain" not in activating_view.view_type:
                self.state.view_chain_pos += 1
                self.state.set_view(activating_view)
            L.debug('About to activate view: %s', activating_view.name)
            activating_view.start(user_data)


class View(object):
    """View Objects old the various parts of a given view
    such as the header, footer, body, etc"""

    def __init__(self, app, views, name, view_json_data):
        self.app = app
        # L.debug("View %s Initialized", name)
        self.name = name
        self.footer = None
        self.body = None
        self.action = None
        self.action_class = None
        self.action_thread = None
        self.actions = views.actions
        self.view_type = view_json_data['view_type']
        self.title = view_json_data['title']
        self.sub_title = view_json_data['sub_title']
        self.action_on_load = view_json_data['action_on_load']
        if 'initial_text' in view_json_data.keys():
            self.initial_text = view_json_data['initial_text']
        else:
            self.initial_text = None
        if 'progress_bar' in view_json_data.keys():
            L.debug('%s - view_json_data["progress_bar"] : %s',
                    view_json_data['progress_bar'],
                    self.name)
            self.progress_bar = True
        else:
            self.progress_bar = False
        if 'class' in view_json_data.keys():
            self.action_class_name = view_json_data['class']
        else:
            self.action_class_name = None
        self.header = None
        self.return_view = self

    def start(self, user_data):
        """Starts the loading, and showing of the activated view
        Typically called by Views.activate, but sometimes called
        through other means"""
        L.debug('User Data: %s', user_data)
        if "return_view" in user_data.keys():
            self.return_view = user_data["return_view"]
        if self.view_type == 'no_display':
            if self.action_on_load:
                L.debug('This View has an action to be run on load')
                self.action = getattr(self.actions, self.action_on_load)
                self.action()
        else:
            self.set_view_body()
            self.show_header()
            self.show_body()
            self.show_footer()
            if self.view_type == 'no_input':
                self.set_focus('footer')
            else:
                self.set_focus('body')
            if self.action_on_load:
                # self.app.loop.draw_screen()
                L.debug('This View has an action to be run on load')
                if self.action_class_name:
                    self.action_class = getattr(
                        self.actions, self.action_class_name)
                    self.action = getattr(
                        self.action_class, self.action_on_load)
                else:
                    self.action = getattr(self.actions, self.action_on_load)
                self.action_thread = Thread(
                    target=self.action,
                    name='action_thread')
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
            title = self.app.settings.display['title']
        if self.sub_title:
            sub_title = self.sub_title
        else:
            sub_title = self.app.settings.display['sub_title']
        self.header = W.get_header(self.app, self.name, title, sub_title)
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
        self.body = body_class(
            self.app,
            self.initial_text,
            user_args=args,
            calling_view=self,
            progress_bar=self.progress_bar)
