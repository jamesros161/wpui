import urwid as U
import widgets as W
from settings import Settings
S = Settings()
from logmod import Log
L = Log(S)
from widgets import CustomWidgets, BoxButton
W = CustomWidgets(S,L)
import wpcli
#PRIMARY BodyWidget Class#
class BodyWidget():
    def __init__(self, app):
        self.app = app
        self.widget = self.define_widget()
    def define_widget(self, **kwargs): 
        """Page displayed as Home Page for the application
        """
        self.app.L.debug(' kwargs : %s', kwargs)
        home_text = self.app.W.get_text('body', 'Welcome to the best Exim Search Utility ever created.\nSelect an option below to begin.','center')
        return U.Filler(home_text, 'middle')

"""
ADD SUBCLASSES HERE for each view's body
"""


class home(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        BodyWidget.__init__(self,app)

    def define_widget(self, **kwargs): 
        self.app.L.debug(' kwargs : %s', kwargs)
        home_text = self.app.W.get_text('body', 'Welcome to the best Exim Search Utility ever created.\nSelect an option below to begin.','center')
        return U.Filler(home_text, 'middle')

class installs(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        BodyWidget.__init__(self,app)

    def define_widget(self, **kwargs): 
        self.app.L.debug(' kwargs : %s', kwargs)
        home_text = self.app.W.get_text('body', 'Obtaining List of available WordPress Installations','center')
        return U.Filler(home_text, 'middle')

class plugins(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        BodyWidget.__init__(self,app)

    def define_widget(self, **kwargs): 
        self.app.L.debug(' kwargs : %s', kwargs)
        home_text = self.app.W.get_text('body', 'Installed Plugins for selected WP Installation','center')
        return U.Filler(home_text, 'middle')

class themes(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        BodyWidget.__init__(self,app)

    def define_widget(self, **kwargs): 
        self.app.L.debug(' kwargs : %s', kwargs)
        home_text = self.app.W.get_text('body', 'Installed Themes for selected WP Installation','center')
        return U.Filler(home_text, 'middle')

class users(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        BodyWidget.__init__(self,app)

    def define_widget(self, **kwargs): 
        self.app.L.debug(' kwargs : %s', kwargs)
        home_text = self.app.W.get_text('body', 'Registered Users for selected WP Installation','center')
        return U.Filler(home_text, 'middle')

class core(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        BodyWidget.__init__(self,app)

    def define_widget(self, **kwargs): 
        self.app.L.debug(' kwargs : %s', kwargs)
        home_text = self.app.W.get_text('body', 'WordPress Core Information for selected WP Installation','center')
        return U.Filler(home_text, 'middle')

class quit(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        BodyWidget.__init__(self,app)

    def define_widget(self): 
        self.app.L.debug(' Body Widget View Name: %s', self.app.state.active_view.name)
        self.app.L.debug(' Previous View Name: %s', self.app.state.previous_view.name)
        self.app.S.display['menu_enabled'] = True
        quitList = [
            W.get_div(),
            W.get_col_row([
                BoxButton('Yes',on_press=self.app.exit),
                BoxButton('No', on_press=self.app.state.go_back)
                ]),
            W.get_div()]
        quit_box = W.get_list_box(quitList)[0]
        return W.centered_list_box(
            quit_box, 
            'Are You Sure You Want to Quit?',
            len(quitList) + 4)