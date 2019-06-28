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
class BodyWidget(object):
    def __init__(self, app):
        self.progress_bar = U.ProgressBar('body','progressbar',current=0,done=100)
        self.app = app
        self.widget = self.define_widget()
    def define_widget(self, **kwargs): 
        """Page displayed as Home Page for the application
        """
        self.app.L.debug(' kwargs : %s', kwargs)
        home_text = self.app.W.get_text('body', 'Welcome to the best Exim Search Utility ever created.\nSelect an option below to begin.','center')
        return U.Filler(home_text, 'middle')
    def update_progress_bar(self,progress):
        self.app.L.debug('Progress: %s', progress)
        if progress:
            self.progress_bar.set_completion(int(progress))
        else:
            self.progress_bar.set_completion(100)
            self.app.loop.remove_watch_pipe(self.app.action_pipe)
            self.app.loop.draw_screen()
"""
ADD SUBCLASSES HERE for each view's body
"""

class home(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        super(home, self).__init__(app)

    def define_widget(self, **kwargs): 
        self.app.L.debug(' kwargs : %s', kwargs)
        home_text = self.app.W.get_text('body', 'Welcome to the best Exim Search Utility ever created.\nSelect an option below to begin.','center')
        return U.Filler(home_text, 'middle')

class installs(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        super(installs,self).__init__(app)

    def define_widget(self, **kwargs): 
        self.app.L.debug(' kwargs : %s', kwargs)
        main_text = self.app.W.get_text('body', 'Obtaining List of available WordPress Installations','center')
        progress_row = W.get_col_row([
            ('weight',2,W.get_blank_flow()),
            self.progress_bar,
            ('weight',2,W.get_blank_flow())
        ])
        main_pile = U.Pile([main_text,progress_row])
        self.app.action_pipe = self.app.loop.watch_pipe(self.update_progress_bar)
        return U.Filler(main_pile, 'middle')
    def after_action(self,installations):
        location_list = []
        for installation in installations:
            location_list.append(len(installation['directory']))
        location_list.sort(reverse=True)
        location_width = location_list[0] + 4
        installation_columns = [W.get_col_row([
            (10,U.AttrMap(W.get_div(),'header')),
            (location_width,U.AttrMap(W.get_text('header', 'Location', 'center'),'header')),
            ('weight',2,U.AttrMap(W.get_text('header','Home URL', 'center'),'header')),
            (18,U.AttrMap(W.get_text('header','Valid wp_options','center'),'header')),
            (20,U.AttrMap(W.get_text('header','wp_db_check passed','center'),'header'))
        ])]
        for installation in installations:
            installation_rows = [
                (10,BoxButton(' + ', on_press=self.app.state.set_installation, user_data=installation)),
                (location_width,W.get_text('body', installation['directory'], 'center'))
            ]
            L.debug('valid_wp_options: %s', installation['valid_wp_options'])
            if installation['valid_wp_options'] == True:
                installation_rows.extend([
                    ('weight',2,W.get_text('body', installation['home_url'], 'center')),
                    (18,W.get_text('body', str(installation['valid_wp_options']),'center')),
                    (20,W.get_text('body', str(installation['wp_db_check_success']),'center'))
                ])
            else:
                installation_rows.append(
                    ('weight',3,W.get_text('body',str(installation['wp_db_error']),'center'))
                )
            installation_columns.append(
                W.get_col_row(installation_rows)
            )
        installation_pile = U.Pile(installation_columns)
        filler = U.Filler(installation_pile, 'middle')
        self.app.frame.contents.__setitem__('body',[filler, None])
        self.app.loop.draw_screen()
class database(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        super(database,self).__init__(app)

    def define_widget(self, **kwargs): 
        self.app.L.debug(' kwargs : %s', kwargs)
        main_text = self.app.W.get_text('body', 'Polling for Database Information','center')
        progress_row = W.get_col_row([
            ('weight',2,W.get_blank_flow()),
            self.progress_bar,
            ('weight',2,W.get_blank_flow())
        ])
        main_pile = U.Pile([main_text,progress_row])
        self.app.action_pipe = self.app.loop.watch_pipe(self.update_progress_bar)
        return U.Filler(main_pile, 'middle')
class plugins(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        super(plugins,self).__init__(app)

    def define_widget(self, **kwargs): 
        self.app.L.debug(' kwargs : %s', kwargs)
        home_text = self.app.W.get_text('body', 'Installed Plugins for selected WP Installation','center')
        return U.Filler(home_text, 'middle')

class themes(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        super(themes, self).__init__(app)

    def define_widget(self, **kwargs): 
        self.app.L.debug(' kwargs : %s', kwargs)
        home_text = self.app.W.get_text('body', 'Installed Themes for selected WP Installation','center')
        return U.Filler(home_text, 'middle')

class users(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        super(users,self).__init__(app)

    def define_widget(self, **kwargs): 
        self.app.L.debug(' kwargs : %s', kwargs)
        home_text = self.app.W.get_text('body', 'Registered Users for selected WP Installation','center')
        return U.Filler(home_text, 'middle')

class core(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        super(core,self).__init__(app)

    def define_widget(self, **kwargs): 
        self.app.L.debug(' kwargs : %s', kwargs)
        home_text = self.app.W.get_text('body', 'WordPress Core Information for selected WP Installation','center')
        return U.Filler(home_text, 'middle')

class quit(BodyWidget):
    def __init__(self,app,user_args=None,calling_view=None):
        super(quit,self).__init__(app)

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