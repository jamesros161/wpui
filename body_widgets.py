"""Collection of classes each used for a view"""
import time
import getpass
import urwid as U
from logmod import Log
from settings import Settings
from widgets import CustomWidgets, BoxButton, WpConfigValueMap
import widgets as W
S = Settings()
L = Log()
W = CustomWidgets()
#PRIMARY BodyWidget
# Class#
class BodyWidget(object):
    """Parent Class for body widgets

    Returns:
        obj -- Returns a widget to be used as the 'body' portion of the frame
    """
    def __init__(self, app):
        self.progress_bar = U.ProgressBar('body', 'progressbar', current=0, done=100)
        self.app = app
        self.widget = self.define_widget()
    def define_widget(self, **kwargs):
        """Page displayed as Home Page for the application
        """
        L.debug(' kwargs : %s', kwargs)
        home_text = W.get_text(
            'body',
            'WP-CLI Like you have never WP-CLI\'d before!!!.\n \
            Select an option below to begin.',
            'center')
        return U.Filler(home_text, 'middle')
    def update_progress_bar(self, progress):
        """Updates the progress bar on body widgets that
        have a progress bar

        Arguments:
            progress {str} -- string representation of the current
                              progress
        """
        #L.debug('Progress: %s', progress)
        if progress:
            self.progress_bar.set_completion(int(progress))
        else:
            self.progress_bar.set_completion(100)
            self.app.loop.remove_watch_pipe(self.app.action_pipe)
            self.app.loop.draw_screen()

#ADD SUBCLASSES HERE for each view's body

class Home(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(Home, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        home_text = W.get_text(
            'body',
            'WP-CLI Like you have never WP-CLI\'d before!!!.\
            \nSelect an option below to begin.', 'center')
        return U.Filler(home_text, 'middle')

class Installs(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(Installs, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        main_text = W.get_text(
            'body',
            'Obtaining List of available WordPress Installations',
            'center')
        progress_row = W.get_col_row([
            ('weight', 2, W.get_blank_flow()),
            self.progress_bar,
            ('weight', 2, W.get_blank_flow())
        ])
        main_pile = U.Pile([main_text, progress_row])
        self.app.action_pipe = self.app.loop.watch_pipe(self.update_progress_bar)
        return U.Filler(main_pile, 'middle')
    def after_action(self, installations):
        """Updates the view's body in response to
        the views action_on_load function

        Arguments:
            installations {list} -- [list of installations]
        """
        location_list = []
        if installations:
            for installation in installations:
                location_list.append(len(installation['directory']))
            location_list.sort(reverse=True)
            location_width = location_list[0] + 4
            installation_columns = [W.get_col_row([
                (10, U.AttrMap(W.get_div(), 'header')),
                (location_width, U.AttrMap(W.get_text('header', 'Location', 'center'), 'header')),
                ('weight', 2, U.AttrMap(W.get_text('header', 'Home URL', 'center'), 'header')),
                (18, U.AttrMap(W.get_text('header', 'Valid wp_options', 'center'), 'header')),
                (20, U.AttrMap(W.get_text('header', 'wp_db_check passed', 'center'), 'header'))
            ])]
            for installation in installations:
                installation_rows = [
                    (10, BoxButton(
                        ' + ',
                        on_press=self.app.state.set_installation,
                        user_data=installation)),
                    (location_width, W.get_text('body', installation['directory'], 'center'))
                ]
                #L.debug('valid_wp_options: %s', installation['valid_wp_options'])
                if installation['valid_wp_options']:
                    installation_rows.extend([
                        ('weight', 2, W.get_text('body', installation['home_url'], 'center')),
                        (18, W.get_text('body', str(installation['valid_wp_options']), 'center')),
                        (20, W.get_text('body', str(installation['wp_db_check_success']), 'center'))
                    ])
                else:
                    installation_rows.append(
                        (
                            'weight',
                            3,
                            W.get_text(
                                'body',
                                str(installation['wp_db_error']),
                                'center'))
                    )
                installation_columns.append(
                    W.get_col_row(installation_rows)
                )
        else:
            installation_columns = [W.get_col_row([
                W.get_blank_flow(),
                W.get_text(
                    'body',
                    'There Are No WordPress Installations found for User: ' + getpass.getuser(),
                    'center'),
                W.get_blank_flow()
            ])]
        installation_pile = U.Pile(installation_columns)
        filler = U.Filler(installation_pile, 'middle')
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        if installations:
            self.app.frame.set_focus('body')
        else:
            self.app.frame.set_focus('footer')
        self.app.loop.draw_screen()
class GetWpConfig(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(GetWpConfig, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        main_text = W.get_text('body', 'Obtaining WP-Config  directives', 'center')
        progress_row = W.get_col_row([
            ('weight', 2, W.get_blank_flow()),
            self.progress_bar,
            ('weight', 2, W.get_blank_flow())
        ])
        main_pile = U.Pile([main_text, progress_row])
        self.app.action_pipe = self.app.loop.watch_pipe(self.update_progress_bar)
        return U.Filler(main_pile, 'middle')
    def after_action(self, wp_config):
        """Updates the view's body in response to
        the views action_on_load function
        """

        L.debug(' wp_config : %s', wp_config)
        directives_list = [
            W.get_col_row([
                (10, U.AttrMap(W.get_text('header', 'Type', 'center'), 'header')),
                U.AttrMap(W.get_text('header', 'Name', 'center'), 'header'),
                ('weight', 2, U.AttrMap(W.get_text('header', 'Value', 'center'), 'header'))])]
        for directive in wp_config.wp_config_directive_list:
            button = WpConfigValueMap(
                self.app,
                'default',
                directive_name=str(directive['name']),
                edit_text=str(directive['value']),
                align='center')
            row_items = [
                (10, W.get_text('default', str(directive['type']), 'center')),
                W.get_text('default', str(directive['name']), 'center'),
                ('weight', 2, button)
                ]
            row = W.get_col_row(row_items)
            directives_list.append(row)
        wp_config_pile = U.Pile(directives_list)
        filler = U.Filler(wp_config_pile)
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()
class SetAddWpConfig(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(SetAddWpConfig, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        rows = []
        directive_name_edit = W.get_edit(
            '',
            align='center')
        rows.append(
            W.get_col_row([
                W.get_text('default', 'WP-Config Directive Name: ', 'right'),
                directive_name_edit
            ])
        )
        directive_value_edit = WpConfigValueMap(
            self.app,
            'default',
            directive_name=directive_name_edit.get_edit_text(),
            edit_text='',
            align='center')
        rows.append(
            W.get_col_row([
                W.get_text('default', 'WP-Config Directive Value: ', 'right'),
                directive_value_edit
            ])
        )
        U.connect_signal(
            directive_name_edit,
            'postchange',
            self.debug,
            user_arg=directive_name_edit.get_edit_text())
        pile = U.Pile([
            directive_name_edit,
            directive_value_edit])
        return U.Filler(pile, 'middle')
    def debug(self, *args):
        """Prints debug for module"""
        L.debug('Args: %s', args)
class Database(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(Database, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        main_text = W.get_text(
            'body',
            'Polling for Database Information',
            'center')
        progress_row = W.get_col_row([
            ('weight', 2, W.get_blank_flow()),
            self.progress_bar,
            ('weight', 2, W.get_blank_flow())
        ])
        main_pile = U.Pile([main_text, progress_row])
        self.app.action_pipe = self.app.loop.watch_pipe(self.update_progress_bar)
        return U.Filler(main_pile, 'middle')
    def after_action(self, db_info):
        """Updates the view's body in response to
        the views action_on_load function
        """
        db_info_rows = [
            W.get_col_row([
                U.AttrMap(W.get_text(
                    'header',
                    'Database Information',
                    'center'
                    ), 'header')
            ])
        ]
        db_info_rows.append(
            W.get_col_row([
                U.AttrMap(W.get_text(
                    'header', 'Database Name',
                    'center'
                    ), 'header'),
                U.AttrMap(W.get_text(
                    'header', 'Database Size',
                    'center'
                    ), 'header')
            ])
        )
        db_info_rows.append(W.get_div())
        db_info_rows.append(
            W.get_col_row([
                W.get_text('body', db_info['name'], 'center'),
                W.get_text('body', db_info['size'], 'center')
            ])
        )
        db_info_rows.append(W.get_div())
        db_info_rows.append(
            W.get_col_row([
                U.AttrMap(W.get_text(
                    'header',
                    'Database Table Check Results',
                    'center'
                    ), 'header')
            ])
        )
        db_info_rows.append(
            W.get_col_row([
                (5, U.AttrMap(W.get_blank_flow(), 'header')),
                U.AttrMap(W.get_text('header', 'Table Name', 'left'), 'header'),
                (18, U.AttrMap(W.get_text('header', 'Check Status', 'center'), 'header')),
                (5, U.AttrMap(W.get_blank_flow(), 'header'))
            ])
        )
        for table in db_info['check_tables']:
            db_info_rows.append(
                W.get_col_row([
                    (5, W.get_blank_flow()),
                    W.get_text('body', table['table_name'], 'left'),
                    (16, W.get_text('body', table['check_status'], 'center')),
                    (5, W.get_blank_flow())
                ])
            )
        db_info_pile = U.Pile(db_info_rows)
        db_info_wrapper = W.get_col_row([
            W.get_blank_flow(),
            db_info_pile,
            W.get_blank_flow()
        ])
        outer_pile = U.Pile([
            W.get_div(),
            db_info_wrapper,
            W.get_div()
        ])
        filler = U.Filler(outer_pile, 'middle')
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()
class DbExport(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(DbExport, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        home_text = W.get_text(
            'body',
            'Welcome to the best Exim Search Utility ever created.\
            \nSelect an option below to begin.',
            'center')
        return U.Filler(home_text, 'middle')
class DbImport(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(DbImport, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        home_text = W.get_text(
            'body',
            'Welcome to the best Exim Search Utility ever created.\
            \nSelect an option below to begin.',
            'center')
        return U.Filler(home_text, 'middle')
class DbOptimize(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(DbOptimize, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        home_text = W.get_text(
            'body',
            'Welcome to the best Exim Search Utility ever created.\
            \nSelect an option below to begin.',
            'center')
        return U.Filler(home_text, 'middle')
class DbRepair(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(DbRepair, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        home_text = W.get_text(
            'body',
            'Welcome to the best Exim Search Utility ever created.\
            \nSelect an option below to begin.',
            'center')
        return U.Filler(home_text, 'middle')
class DbSearch(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(DbSearch, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        home_text = W.get_text(
            'body',
            'Welcome to the best Exim Search Utility ever created.\
            \nSelect an option below to begin.',
            'center')
        return U.Filler(home_text, 'middle')
class Plugins(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(Plugins, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        home_text = W.get_text(
            'body',
            'Installed Plugins for selected WP Installation',
            'center')
        return U.Filler(home_text, 'middle')
class Themes(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(Themes, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        home_text = W.get_text(
            'body',
            'Installed Themes for selected WP Installation',
            'center')
        return U.Filler(home_text, 'middle')

class Users(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(Users, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        home_text = W.get_text(
            'body',
            'Registered Users for selected WP Installation',
            'center')
        return U.Filler(home_text, 'middle')

class Core(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(Core, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        home_text = W.get_text(
            'body',
            'WordPress Core Information for selected WP Installation',
            'center')
        return U.Filler(home_text, 'middle')

class Quit(BodyWidget):
    """Creates the specific body widget for the view of the same name"""
    def __init__(self, app, user_args=None, calling_view=None):
        super(Quit, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
    def define_widget(self, **kwargs):
        L.debug(' Body Widget View Name: %s', self.app.state.active_view.name)
        L.debug(' Previous View Name: %s', self.app.state.previous_view.name)
        S.display['menu_enabled'] = True
        quit_list = [
            W.get_div(),
            W.get_col_row([
                BoxButton('Yes', on_press=self.app.exit),
                BoxButton('No', on_press=self.app.state.go_back)
                ]),
            W.get_div()]
        quit_box = W.get_list_box(quit_list)[0]
        return W.centered_list_box(
            quit_box,
            'Are You Sure You Want to Quit?',
            len(quit_list) + 4)
