"""Collection of classes each used for a view"""
import datetime
import time
import getpass
from HTMLParser import HTMLParser
import urwid as U
from logmod import Log
from settings import Settings
from widgets import CustomWidgets, BoxButton, WpConfigValueMap
from widgets import WpConfigNameMap, DbImportEditMap, DbSearchEditMap
from widgets import SRSearchEditMap
S = Settings()
L = Log()
W = CustomWidgets()


class BodyWidget(object):
    """Parent Class for body widgets

    Returns:
        obj -- Returns a widget to be used as the 'body' portion of the frame
    """

    def __init__(self, app, initial_text='', progress_bar=False):
        self.progress_bar = U.ProgressBar(
            'body',
            'progressbar',
            current=0,
            done=100)
        self.app = app
        self.widget = self.define_widget(
            initial_text,
            progress_bar
        )
        self.pile = None
        self.progress = 0

    def define_widget(self, initial_text, progress_bar=False):
        """Page displayed as Home Page for the application
        """
        L.debug(' Initial_Text : %s', initial_text)
        initial_text = W.get_text(
            'body',
            str(initial_text),
            'center')
        if progress_bar:
            progress_row = W.get_col_row([
                ('weight', 2, W.get_blank_flow()),
                self.progress_bar,
                ('weight', 2, W.get_blank_flow())
            ])
            main_pile = U.Pile([initial_text, progress_row])
            self.app.action_pipe = self.app.loop.watch_pipe(
                self.update_progress_bar)
        else:
            main_pile = U.Pile([initial_text])
        return U.Filler(main_pile, 'middle')

    def update_progress_bar(self, progress):
        """Updates the progress bar on body widgets that
        have a progress bar

        Arguments:
            progress {str} -- string representation of the current
                              progress
        """
        # L.debug('Progress: %s', progress)
        if progress:
            self.progress_bar.set_completion(int(progress))
        else:
            self.progress_bar.set_completion(100)
            self.app.loop.remove_watch_pipe(self.app.action_pipe)
            self.app.loop.draw_screen()

# ADD SUBCLASSES HERE for each view's body


class Home(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(Home, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)


class Invalid(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(Invalid, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)


class Installs(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(Installs, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

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
                W.get_blank_flow(),
                (10, U.AttrMap(W.get_div(), 'header')),
                (
                    location_width,
                    U.AttrMap(
                        W.get_text(
                            'header',
                            'Location',
                            'center'
                        ),
                        'header')),
                ('weight', 2, U.AttrMap(
                    W.get_text(
                        'header',
                        'Home URL',
                        'center'
                    ),
                    'header')),
                (18, U.AttrMap(
                    W.get_text(
                        'header',
                        'Valid wp_options',
                        'center'
                    ),
                    'header')),
                (20, U.AttrMap(
                    W.get_text(
                        'header',
                        'wp_db_check passed',
                        'center'
                    ),
                    'header')),
                W.get_blank_flow()
            ])]
            for installation in installations:
                installation_rows = [
                    W.get_blank_flow(),
                    (10, BoxButton(
                        ' + ',
                        on_press=self.app.state.set_installation,
                        user_data=installation)),
                    (location_width, W.get_text(
                        'body',
                        installation['directory'],
                        'center'))
                ]
                # L.debug(
                #     'valid_wp_options: %s',
                #     installation['valid_wp_options'])
                if installation['valid_wp_options']:
                    installation_rows.extend([
                        ('weight', 2, W.get_text(
                            'body',
                            installation['home_url'],
                            'center')),
                        (18, W.get_text(
                            'body',
                            str(installation['valid_wp_options']),
                            'center')),
                        (20, W.get_text(
                            'body',
                            str(installation['wp_db_check_success']),
                            'center'))
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
                installation_rows.append(
                    W.get_blank_flow()
                )
                installation_columns.append(
                    W.get_col_row(installation_rows)
                )
        else:
            installation_columns = [W.get_col_row([
                W.get_blank_flow(),
                W.get_text(
                    'body',
                    'There Are No WordPress Installations found for User: ' +
                    getpass.getuser(),
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

    def after_action(self, wp_config):
        """Updates the view's body in response to
        the views action_on_load function
        """

        L.debug(' wp_config : %s', wp_config)
        directives_list = [
            W.get_col_row([
                W.get_blank_flow(),
                (10, U.AttrMap(W.get_text(
                    'header',
                    'Type',
                    'center'), 'header')),
                U.AttrMap(W.get_text('header', 'Name', 'center'), 'header'),
                ('weight', 2, U.AttrMap(W.get_text(
                    'header',
                    'Value',
                    'left'), 'header')),
                W.get_blank_flow()
                ])]
        for directive in wp_config.wp_config_directive_list:
            if 'DB_NAME' in str(directive['name']):
                self.app.state.active_installation['db_name'] = str(
                    directive['value']
                )
            button = WpConfigValueMap(
                self.app,
                'default',
                directive_name=str(directive['name']),
                edit_text=str(directive['value']),
                align='left')
            row_items = [
                W.get_blank_flow(),
                (10, W.get_text('default', str(directive['type']), 'center')),
                W.get_text('default', str(directive['name']), 'center'),
                ('weight', 2, button),
                W.get_blank_flow()
            ]
            row = W.get_col_row(row_items)
            directives_list.append(row)
        add_option_value_button = WpConfigValueMap(
            self.app,
            'underline',
            body_widget=self,
            align="left",
            on_enter=self.app.views.GetWpConfig.start)
        add_option_name_button = WpConfigNameMap(
            self,
            'underline',
            add_option_value_button,
            align='left')
        directives_list.extend([
            W.get_div(),
            W.get_div()
        ])
        directives_list.extend([
            W.get_col_row([
                W.get_blank_flow(),
                ('weight', 3, U.AttrMap(
                    W.get_text('header', 'Add Option', 'center'),
                    'header')),
                W.get_blank_flow()
            ]),
            W.get_div(),
            W.get_col_row([
                W.get_blank_flow(),
                (13, W.get_text('default', 'Option Name:', 'right')),
                add_option_name_button,
                W.get_blank_flow()
            ]),
            W.get_col_row([
                W.get_blank_flow(),
                (13, W.get_text('default', 'Option Value:', 'right')),
                add_option_value_button,
                W.get_blank_flow()
            ]),
            W.get_div(),
            W.get_div()
        ])
        directives_list.append(
            W.get_col_row([
                W.get_blank_flow(),
                BoxButton(
                    'Re-Salt Config',
                    on_press=self.app.views.actions.re_salt
                ),
                W.get_blank_flow()
            ])
        )
        self.pile = U.Pile(directives_list)
        filler = U.Filler(self.pile)
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()


class SetAddWpConfig(BodyWidget):
    """Adds a new option to the wp-config.php"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(SetAddWpConfig, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        self.directive_name = ''
        rows = []
        self.directive_value_edit = WpConfigValueMap(
            self.app,
            'default',
            directive_name=self.directive_name,
            edit_text='',
            align='left',
            on_enter=self.app.views.activate,
            user_args=[self.app, 'GetWpConfig'])
        self.directive_name_edit = WpConfigNameMap(
            self,
            'default',
            self.directive_value_edit,
            align='left')
        rows.append(
            W.get_col_row([
                W.get_text('default', 'WP-Config Directive Name: ', 'right'),
                self.directive_name_edit
            ])
        )
        rows.append(
            W.get_col_row([
                W.get_text('default', 'WP-Config Directive Value: ', 'right'),
                self.directive_value_edit
            ])
        )
        self.pile = U.Pile(rows)
        return U.Filler(self.pile, 'middle')

    def debug(self, *args):
        """Prints debug for module"""
        L.debug('Args: %s', args)


class SetDbCreds(BodyWidget):
    """Easily set DB credentials for WP-Config"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(SetDbCreds, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        db_name_edit = WpConfigValueMap(
            self.app,
            'default',
            directive_name='DB_NAME',
            edit_text='',
            body_widget=self,
            align='left',
            cursor_drop=True)
        db_user_edit = WpConfigValueMap(
            self.app,
            'default',
            body_widget=self,
            directive_name='DB_USER',
            edit_text='',
            align='left',
            cursor_drop=True)
        db_pass_edit = WpConfigValueMap(
            self.app,
            'default',
            body_widget=self,
            directive_name='DB_PASSWORD',
            edit_text='',
            align='left',
            on_enter=self.app.views.activate,
            user_args=[self.app, 'GetWpConfig'])
        rows = [
            W.get_col_row([
                W.get_text('default', 'Database Name: ', 'right'),
                db_name_edit
            ]),
            W.get_col_row([
                W.get_text('default', 'Database User: ', 'right'),
                db_user_edit
            ]),
            W.get_col_row([
                W.get_text('default', 'Database Pass: ', 'right'),
                db_pass_edit
            ])
        ]
        self.pile = U.Pile(rows)
        return U.Filler(self.pile, 'middle')

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
        action_pipe = self.app.loop.watch_pipe(self.update_progress_bar)
        self.app.action_pipe = action_pipe
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
        if db_info['size_error']:
            db_info_rows.append(
                W.get_text('default',
                           "Database Error:\n\n" +
                           db_info['size_error'] + "\n" +
                           "Troubleshoot Database Connection",
                           'center')
            )
        elif db_info['check_error']:
            db_info_rows.append(
                W.get_text('default',
                           "Database Error:\n\n" +
                           db_info['check_error'] + "\n" +
                           "Troubleshoot Database Connection",
                           'center')
            )
        else:
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
                    W.get_text('body', str(db_info['name']), 'center'),
                    W.get_text('body', str(db_info['size']), 'center')
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
                    U.AttrMap(W.get_text(
                        'header',
                        'Table Name',
                        'left'), 'header'),
                    (18, U.AttrMap(W.get_text(
                        'header',
                        'Check Status',
                        'center'), 'header')),
                    (5, U.AttrMap(W.get_blank_flow(), 'header'))
                ])
            )
            for table in db_info['check_tables']:
                db_info_rows.append(
                    W.get_col_row([
                        (5, W.get_blank_flow()),
                        W.get_text('body', table['table_name'], 'left'),
                        (16, W.get_text(
                            'body',
                            table['check_status'],
                            'center')),
                        (5, W.get_blank_flow())
                    ])
                )
        db_info_pile = U.Pile(db_info_rows)
        db_info_wrapper = W.get_col_row([
            W.get_blank_flow(),
            ('weight', 3, db_info_pile),
            W.get_blank_flow()
        ])
        outer_pile = U.Pile([
            W.get_div(),
            db_info_wrapper,
            W.get_div()
        ])
        filler = U.Filler(outer_pile, 'middle')
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(2)
        self.app.loop.draw_screen()


class DbExport(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(DbExport, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        main_text = W.get_text(
            'body',
            'Exporting Database....',
            'center')
        return U.Filler(main_text, 'middle')

    def after_action(self, result):
        """Updates the view's body in response to
        the views action_on_load function
        """
        L.debug('Result: %s', result)
        if result:
            text = result
        else:
            text = "Database export failed"
        main_text = W.get_text(
            'body',
            text,
            'center')
        pile = U.Pile([main_text])
        filler = U.Filler(pile, 'middle')
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()


class DbImport(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(DbImport, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        home_text = W.get_text(
            'body',
            'Searching for database dumps to import...',
            'center')
        return U.Filler(home_text, 'middle')

    def after_action(self, import_list):
        """Displays list of imports available"""
        import_rows = []
        if import_list:
            for item in import_list:
                import_rows.append(
                    W.get_col_row([
                        W.get_blank_flow(),
                        ('weight', 3, BoxButton(
                            item,
                            on_press=self.app.views.actions.import_db,
                            user_data=item)),
                        W.get_blank_flow()
                    ])
                )
        import_edit = DbImportEditMap(
            self.app,
            'body',
            edit_text=self.app.state.homedir,
            align='left',
            on_enter=self.app.views.actions.import_db,
            caption='Other Import Path: ')
        import_edit_linebox = W.get_line_box(import_edit, '')
        import_edit_row = W.get_col_row([
            W.get_blank_flow(),
            ('weight', 1, import_edit_linebox),
            W.get_blank_flow()
        ])
        import_rows.append(import_edit_row)
        import_list_box = W.get_list_box(import_rows)[0]
        # pile = U.Pile(import_rows)
        # filler = U.Filler(pile, 'middle')
        self.app.frame.contents.__setitem__('body', [import_list_box, None])
        time.sleep(1)
        self.app.loop.draw_screen()

    def after_import(self, result):
        """Updates the view's body in response to
        wp-cli's import function
        """
        L.debug('Result: %s', result)
        if result:
            text = result
        else:
            text = "Database import failed"
        main_text = W.get_text(
            'body',
            text,
            'center')
        pile = U.Pile([main_text])
        filler = U.Filler(pile, 'middle')
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()


class DbOptimize(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(DbOptimize, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        main_text = W.get_text(
            'body',
            'Optimizing Database....',
            'center')
        return U.Filler(main_text, 'middle')

    def after_action(self, result):
        """Updates the view's body in response to
        the views action_on_load function
        """
        L.debug('Result: %s', result)
        if result:
            text = result
        else:
            text = "Database Optimize failed"
        main_text = W.get_text(
            'body',
            text,
            'center')
        pile = U.Pile([main_text])
        filler = U.Filler(pile, 'middle')
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()


class DbRepair(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(DbRepair, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        main_text = W.get_text(
            'body',
            'Repairing Database....',
            'center')
        return U.Filler(main_text, 'middle')

    def after_action(self, result):
        """Updates the view's body in response to
        the views action_on_load function
        """
        L.debug('Result: %s', result)
        if result:
            text = result
        else:
            text = "Database Repair failed"
        main_text = W.get_text(
            'body',
            text,
            'center')
        pile = U.Pile([main_text])
        filler = U.Filler(pile, 'middle')
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()


class DbSearch(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(DbSearch, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        db_search_row = W.get_col_row([
            W.get_blank_flow(),
            (
                'weight',
                3,
                DbSearchEditMap(
                    self.app,
                    self,
                    'body',
                    caption='Database Search Query: ',
                    on_enter=self.app.views.actions.db_search,
                    align='left')),
            W.get_blank_flow()
        ])
        return U.Filler(db_search_row, 'middle')

    def after_action(self, db_search_results, query):
        """Displays after_action contents"""
        L.debug('Search Results: %s', db_search_results)
        search_result_rows = [
            W.get_col_row([
                W.get_blank_flow(),
                ('weight', 4, U.AttrMap(W.get_text(
                    'header', 'DB Search Results for: ', 'right'), 'header')),
                ('weight', 4, U.AttrMap(W.get_text(
                    'header', query, 'left'), 'header')),
                W.get_blank_flow()]),
            W.get_col_row([
                W.get_blank_flow(),
                ('weight', 4, U.AttrMap(W.get_blank_flow(), 'header')),
                ('weight', 4, U.AttrMap(W.get_blank_flow(), 'header')),
                W.get_blank_flow()]),
            W.get_col_row([
                W.get_blank_flow(),
                ('weight', 1, U.AttrMap(W.get_text(
                    'header', 'Row', 'center'), 'header')),
                ('weight', 1, U.AttrMap(W.get_text(
                    'header', 'Table', 'center'), 'header')),
                ('weight', 2, U.AttrMap(W.get_text(
                    'header', 'Column', 'center'), 'header')),
                ('weight', 4, U.AttrMap(W.get_text(
                    'header', 'Value', 'center'), 'header')),
                W.get_blank_flow()
            ]),
        ]
        for result in db_search_results:
            search_result_rows.append(
                W.get_col_row([
                    W.get_blank_flow(),
                    ('weight', 1, W.get_text(
                        'default', result['row'], 'center')),
                    ('weight', 1, W.get_text(
                        'default', result['table'], 'center')),
                    ('weight', 2, W.get_text(
                        'default', result['column'], 'center')),
                    ('weight', 4, W.get_text(
                        'default', result['value'], 'center')),
                    W.get_blank_flow()
                ])
            )
        pile = U.Pile(search_result_rows)
        filler = U.Filler(pile, 'middle')
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()


class SearchReplace(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(SearchReplace, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        sr_search_edit = SRSearchEditMap(
            self.app,
            self,
            'default',
            drop_cursor=True,
            on_enter=self.app.views.actions.sr_search,
            align='left')
        sr_replace_edit = SRSearchEditMap(
            self.app,
            self,
            'default',
            edit_text='',
            on_enter=self.app.views.actions.sr_replace,
            align='left')
        rows = [
            W.get_col_row([
                W.get_text('default', 'Search Term: ', 'right'),
                sr_search_edit
            ]),
            W.get_col_row([
                W.get_text('default', 'Replacement Term: ', 'right'),
                sr_replace_edit
            ])
        ]
        self.pile = U.Pile(rows)
        return U.Filler(self.pile, 'middle')

    def after_dry_run(self, results, results_count, db_export_message):
        """Displays the Search-replace dry-run results"""

        L.debug('results: %s', results)
        dry_run_rows = []
        if db_export_message:
            L.debug('db_export_message: %s', db_export_message)
            dry_run_rows.append(
                W.get_col_row([
                    W.get_blank_flow(),
                    U.AttrMap(
                        W.get_text(
                            'flashing', db_export_message, 'center'),
                        'flashing'),
                    W.get_blank_flow()
                ])
            )
            dry_run_rows.append(W.get_div())
            dry_run_rows.append(
                W.get_col_row([
                    W.get_blank_flow(),
                    U.AttrMap(
                        W.get_text(
                            'body', S.display['mycophagists'], 'center'),
                        'body'),
                    W.get_blank_flow()
                ])
            )
            dry_run_rows.append(W.get_div())
        if results:
            header_string = ''
            if results_count == '0':
                header_string = 'There are not any replacements to be made'
            else:
                header_string = 'There are ' + results_count + \
                    ' replacements to be made'
            dry_run_rows.append(
                W.get_col_row([
                    W.get_blank_flow(),
                    U.AttrMap(W.get_blank_flow(), 'header'),
                    U.AttrMap(
                        W.get_text(
                            'header',
                            header_string,
                            'center'),
                        'header'),
                    U.AttrMap(W.get_blank_flow(), 'header'),
                    W.get_blank_flow()
                ])
            )
            if results_count == '0':
                dry_run_rows.append(
                    W.get_col_row([
                        W.get_blank_flow(),
                        BoxButton(
                            'New Search & Replace',
                            on_press=self.app.views.activate,
                            user_data='SearchReplace'),
                        W.get_blank_flow()
                    ])
                )
            if results_count != '0':
                dry_run_rows.append(
                    W.get_col_row([
                        W.get_blank_flow(),
                        U.AttrMap(
                            W.get_text(
                                'header', 'Table', 'center'),
                            'header'),
                        U.AttrMap(
                            W.get_text(
                                'header', 'Column', 'center'),
                            'header'),
                        U.AttrMap(
                            W.get_text(
                                'header', 'Count', 'center'),
                            'header'),
                        W.get_blank_flow()
                    ])
                )
                for result in results:
                    if not isinstance(result, basestring):
                        if int(result['count']) > 0:
                            dry_run_rows.append(
                                W.get_col_row([
                                    W.get_blank_flow(),
                                    U.AttrMap(
                                        W.get_text(
                                            'default',
                                            result['table'],
                                            'center'),
                                        'default'),
                                    U.AttrMap(
                                        W.get_text(
                                            'default',
                                            result['column'],
                                            'center'),
                                        'default'),
                                    U.AttrMap(
                                        W.get_text(
                                            'default',
                                            result['count'],
                                            'center'),
                                        'default'),
                                    W.get_blank_flow()
                                ])
                            )
                dry_run_rows.append(W.get_div())
                dry_run_rows.append(
                    W.get_col_row([
                        W.get_blank_flow(),
                        BoxButton(
                            'Perform Replacement',
                            on_press=self.app.views.actions.sr_replace,
                            user_data=[False]),
                        BoxButton(
                            'New Search & Replace',
                            on_press=self.app.views.activate,
                            user_data='SearchReplace'),
                        W.get_blank_flow()
                    ])
                )
        pile = U.Pile(dry_run_rows)
        filler = U.Filler(pile, 'middle')
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()

    def after_replacement(self, results, results_count, db_export_message):
        """Displays search-replace results after replacement"""

        L.debug("After Replacement: %s", db_export_message)
        replaced_rows = []
        if results:
            replaced_rows.append(
                W.get_col_row([
                    W.get_blank_flow(),
                    U.AttrMap(W.get_blank_flow(), 'header'),
                    U.AttrMap(
                        W.get_text(
                            'header',
                            'There were ' + results_count +
                            ' Replacements made',
                            'center'),
                        'header'),
                    U.AttrMap(W.get_blank_flow(), 'header'),
                    W.get_blank_flow()
                ])
            )
            replaced_rows.append(
                W.get_col_row([
                    W.get_blank_flow(),
                    U.AttrMap(
                        W.get_text(
                            'header', 'Table', 'center'),
                        'header'),
                    U.AttrMap(
                        W.get_text(
                            'header', 'Column', 'center'),
                        'header'),
                    U.AttrMap(
                        W.get_text(
                            'header', 'Count', 'center'),
                        'header'),
                    W.get_blank_flow()
                ])
            )
            for result in results:
                if not isinstance(result, basestring):
                    if int(result['count']) > 0:
                        replaced_rows.append(
                            W.get_col_row([
                                W.get_blank_flow(),
                                U.AttrMap(
                                    W.get_text(
                                        'default', result['table'], 'center'),
                                    'default'),
                                U.AttrMap(
                                    W.get_text(
                                        'default', result['column'], 'center'),
                                    'default'),
                                U.AttrMap(
                                    W.get_text(
                                        'default', result['count'], 'center'),
                                    'default'),
                                W.get_blank_flow()
                            ])
                        )
            replaced_rows.append(W.get_div())
            replaced_rows.append(
                W.get_col_row([
                    W.get_blank_flow(),
                    BoxButton(
                        'Undo',
                        on_press=self.app.views.actions.import_db,
                        user_data=['Silent']),
                    W.get_blank_flow()
                ])
            )
        pile = U.Pile(replaced_rows)
        filler = U.Filler(pile, 'middle')
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()


class Themes(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(Themes, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
        self.parser = HTMLParser()
        self.response_pile = None

    def update_progress_bar(self, progress):
        self.progress = 0
        while self.progress < 100:
            L.debug('Progress: %s', int(self.progress))
            self.progress = self.progress + 10
            self.progress_bar.set_completion(int(self.progress))
            self.app.loop.draw_screen()
            time.sleep(.250)
        self.progress_bar.set_completion(100)
        self.app.loop.remove_watch_pipe(self.app.action_pipe)
        self.app.loop.draw_screen()

    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        main_text = W.get_text(
            'body',
            'Obtaining List of installed WordPress Themes',
            'center')
        progress_row = W.get_col_row([
            ('weight', 2, W.get_blank_flow()),
            self.progress_bar,
            ('weight', 2, W.get_blank_flow())
        ])
        main_pile = U.Pile([main_text, progress_row])
        self.app.action_pipe = self.app.loop.watch_pipe(
            self.update_progress_bar)
        return U.Filler(main_pile, 'middle')

    def after_action(self, theme_list):
        """Displays after_action contents"""
        theme_rows = [
            U.AttrMap(W.get_col_row([
                W.get_blank_flow(),
                W.get_text(
                    'header', 'Theme Name', 'center'),
                W.get_text(
                    'header', 'Theme Title', 'center'),
                W.get_text(
                    'header', 'Theme Version', 'center'),
                W.get_text(
                    'header', 'Theme Status', 'center'),
                W.get_text(
                    'header', 'Update Status', 'center'),
                W.get_text(
                    'header', 'Update Version', 'center'),
                ('weight', 4, W.get_text(
                    'header', 'Options', 'center')),
                W.get_blank_flow()
            ]), 'header')
        ]
        for theme in theme_list:
            theme_row = [
                W.get_blank_flow(),
                W.get_text(
                    'default', '\n' + theme['name'] + '\n', 'center'),
                W.get_text(
                    'default', '\n' + theme['title'] + '\n', 'center'),
                W.get_text(
                    'default', '\n' + theme['version'] + '\n', 'center'),
                W.get_text(
                    'default', '\n' + theme['status'] + '\n', 'center'),
                W.get_text(
                    'default', '\n' + theme['update'] + '\n', 'center'),
            ]
            if theme['update'] == 'available':
                theme_row.append(
                    W.get_text(
                        'default', '\n' + theme['update_version'] + '\n',
                        'center'),
                )
            else:
                theme_row.append(
                    W.get_blank_flow()
                )
            theme_row.extend([
                BoxButton(
                    'Details',
                    on_press=self.app.views.actions.theme_actions,
                    user_data=[theme]),
                BoxButton(
                    'Uninstall',
                    on_press=self.app.views.actions.theme_actions,
                    user_data=[theme])
            ])
            if theme['update'] == 'available':
                theme_row.append(BoxButton(
                    'Update',
                    on_press=self.app.views.actions.theme_actions,
                    user_data=[theme]))
            else:
                theme_row.append(
                    W.get_blank_flow()
                )

            if theme['status'] == 'inactive':
                theme_row.append(BoxButton(
                    'Activate',
                    on_press=self.app.views.actions.theme_actions,
                    user_data=[theme]))
            else:
                theme_row.append(
                    W.get_blank_flow()
                )

            theme_row.append(
                W.get_blank_flow()
            )
            theme_rows.append(
                W.get_col_row(theme_row)
            )
        theme_rows.append(
            W.get_div()
        )
        theme_rows.append(
            W.get_col_row([
                W.get_blank_flow(),
                BoxButton(
                    'Update All',
                    on_press=self.app.views.actions.theme_actions,
                    user_data='--all'),
                W.get_blank_flow()
            ])
        )
        theme_rows.append(
            W.get_col_row([
                W.get_blank_flow(),
                W.get_text(
                    'body', 'Install Theme:', 'right'
                ),
                DbSearchEditMap(
                    self.app,
                    self,
                    'underline',
                    on_enter=self.app.views.actions.install_theme,
                    align='left'),
                W.get_blank_flow()
            ]))
        theme_pile = U.Pile(theme_rows)
        filler = U.Filler(theme_pile)
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()

    def show_theme_details(self, theme_details):
        """Shows Theme Details"""
        L.debug('Theme Details: %s', theme_details)
        theme_name = ''
        theme_title = ''
        theme_version = ''
        if 'name' in theme_details.keys():
            theme_name = theme_details['name']
            del theme_details['name']
        if 'title' in theme_details.keys():
            theme_title = theme_details['title']
            del theme_details['title']
        if 'version' in theme_details.keys():
            theme_version = theme_details['version']
            del theme_details['version']
        theme_details_rows = [
            W.get_col_row([
                W.get_blank_flow(),
                U.AttrMap(
                    W.get_text('header', theme_name, 'center'), 'header'),
                U.AttrMap(
                    W.get_text('header', theme_title, 'center'), 'header'),
                U.AttrMap(
                    W.get_text(
                        'header', theme_version, 'center'), 'header'),
                W.get_blank_flow()
            ])
        ]
        theme_details_rows.append(W.get_div())
        for key, value in theme_details.items():
            if isinstance(value, list):
                value = " | ".join(value)
            if value:
                theme_details_rows.append(
                    W.get_col_row([
                        W.get_blank_flow(),
                        (15, W.get_text(
                            'default', str(key).capitalize(), 'left')),
                        (3, W.get_text('default', ' : ', 'center')),
                        W.get_text(
                            'default', self.parser.unescape(value), 'left'),
                        W.get_blank_flow()
                    ])
                )
        theme_details_pile = U.Pile(theme_details_rows)
        filler = U.Filler(theme_details_pile)
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()

    def show_theme_action_response(self):
        """Shows theme-action Response"""

        response_text = [
            W.get_col_row([
                W.get_blank_flow(),
                U.AttrMap(W.get_text('header', 'Result', 'center'), 'header'),
                W.get_blank_flow()
                ]),
            W.get_div()
        ]
        self.response_pile = U.Pile(response_text)
        filler = U.Filler(self.response_pile)
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()

    def update_view(self, wpcli_output):
        """Updates the view from pipe"""

        L.debug("Update: %s", wpcli_output)
        if not wpcli_output:
            self.app.loop.remove_watch_pipe(self.app.wpcli_pipe)
        self.response_pile.contents.append((
            W.get_col_row([
                W.get_blank_flow(),
                W.get_text('default', wpcli_output, 'left'),
                W.get_blank_flow()
            ]), ('weight', 1)))

    def after_response(self):
        """After response is displayed, redirect to theme list"""

        time.sleep(2)
        self.app.views.actions.get_theme_list()


class InstallThemes(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(InstallThemes, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, **kwargs):
        """shows initial widget"""

        L.debug(' kwargs : %s', kwargs)
        theme_install_edit = DbSearchEditMap(
            self.app,
            self,
            'body',
            caption='Enter Theme Name to Install: ',
            on_enter=self.app.views.actions.install_theme,
            align='center')

        return U.Filler(theme_install_edit, 'middle')


class Plugins(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(Plugins, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
        self.parser = HTMLParser()
        self.deactivated_plugins = ''
        self.response_pile = None

    def update_progress_bar(self, progress):
        """Updates the display of Progress Bar"""

        self.progress = 0
        while self.progress < 100:
            L.debug('Progress: %s', int(self.progress))
            self.progress = self.progress + 10
            self.progress_bar.set_completion(int(self.progress))
            self.app.loop.draw_screen()
            time.sleep(.250)
        self.progress_bar.set_completion(100)
        self.app.loop.remove_watch_pipe(self.app.action_pipe)
        self.app.loop.draw_screen()

    def define_widget(self, **kwargs):
        """shows initial widget"""
        L.debug(' kwargs : %s', kwargs)
        main_text = W.get_text(
            'body',
            'Obtaining List of Plugins',
            'center')
        progress_row = W.get_col_row([
            ('weight', 2, W.get_blank_flow()),
            self.progress_bar,
            ('weight', 2, W.get_blank_flow())
        ])
        main_pile = U.Pile([main_text, progress_row])
        self.app.action_pipe = self.app.loop.watch_pipe(
            self.update_progress_bar)
        return U.Filler(main_pile, 'middle')

    def after_action(self, plugin_list):
        """Displays after_action contents"""
        plugin_rows = [
            U.AttrMap(W.get_col_row([
                W.get_blank_flow(),
                ('weight', 2, W.get_text(
                    'header', 'Plugin Name', 'center')),
                W.get_text(
                    'header', 'Status', 'center'),
                W.get_text(
                    'header', 'Version', 'center'),
                W.get_text(
                    'header', 'Update Status', 'center'),
                W.get_text(
                    'header', 'Update Version', 'center'),
                ('weight', 4, W.get_text(
                    'header', 'Options', 'center')),
                W.get_blank_flow()
            ]), 'header')
        ]
        for plugin in plugin_list:
            plugin_row = [
                W.get_blank_flow(),
                ('weight', 2, W.get_text(
                    'default', '\n' + plugin['name'] + '\n', 'center')),
                W.get_text(
                    'default', '\n' + plugin['status'] + '\n', 'center'),
                W.get_text(
                    'default', '\n' + plugin['version'] + '\n', 'center'),
                W.get_text(
                    'default', '\n' + plugin['update'] + '\n', 'center'),
            ]
            if plugin['update'] == 'available':
                plugin_row.append(
                    W.get_text(
                        'default', '\n' + plugin['update_version'] + '\n',
                        'center'),
                )
            else:
                plugin_row.append(
                    W.get_blank_flow()
                )
            plugin_row.extend([
                BoxButton(
                    'Details',
                    on_press=self.app.views.actions.plugin_actions.details,
                    user_data=[plugin]),
                BoxButton(
                    'Uninstall',
                    on_press=self.app.views.actions.plugin_actions.uninstall,
                    user_data=[plugin])
            ])
            if plugin['update'] == 'available':
                plugin_row.append(BoxButton(
                    'Update',
                    on_press=self.app.views.actions.plugin_actions.update,
                    user_data=[plugin]))
            else:
                plugin_row.append(
                    W.get_blank_flow()
                )

            if plugin['status'] == 'inactive':
                plugin_row.append(BoxButton(
                    'Activate',
                    on_press=self.app.views.actions.plugin_actions.activate,
                    user_data=[plugin]))
            else:
                plugin_row.append(BoxButton(
                    'Deactivate',
                    on_press=self.app.views.actions.plugin_actions.deactivate,
                    user_data=[plugin]))

            plugin_row.append(
                W.get_blank_flow()
            )
            plugin_rows.append(
                W.get_col_row(plugin_row)
            )
        plugin_rows.append(
            W.get_div()
        )
        if self.deactivated_plugins:
            act_deact_all_plugins = BoxButton(
                'Re-Activate All',
                on_press=self.app.views.actions.plugin_actions.reactivate,
                user_data=self.deactivated_plugins)
        else:
            act_deact_all_plugins = BoxButton(
                'Deactivate All',
                on_press=self.app.views.actions.plugin_actions.deactivate_all,
                user_data='--all')
        plugin_rows.append(
            W.get_col_row([
                W.get_blank_flow(),
                act_deact_all_plugins,
                BoxButton(
                    'Update All',
                    on_press=self.app.views.actions.plugin_actions.update_all,
                    user_data='--all'),
                W.get_blank_flow()
            ])
        )
        plugin_rows.append(
            W.get_col_row([
                W.get_blank_flow(),
                W.get_text(
                    'body', 'Install Plugin:', 'right'
                ),
                DbSearchEditMap(
                    self.app,
                    self,
                    'underline',
                    on_enter=self.app.views.actions.install_plugin,
                    align='left'),
                W.get_blank_flow()
            ]))
        self.pile = U.Pile(plugin_rows)
        filler = U.Filler(self.pile)
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()

    def show_plugin_details(self, plugin_details):
        """Show Plugin Details"""
        L.debug('Plugin Details: %s', plugin_details)
        plugin_name = ''
        plugin_title = ''
        plugin_version = ''
        if 'name' in plugin_details.keys():
            plugin_name = plugin_details['name']
            del plugin_details['name']
        if 'title' in plugin_details.keys():
            plugin_title = plugin_details['title']
            del plugin_details['title']
        if 'version' in plugin_details.keys():
            plugin_version = plugin_details['version']
            del plugin_details['version']
        plugin_details_rows = [
            W.get_col_row([
                W.get_blank_flow(),
                U.AttrMap(
                    W.get_text('header', plugin_name, 'center'), 'header'),
                U.AttrMap(
                    W.get_text('header', plugin_title, 'center'), 'header'),
                U.AttrMap(
                    W.get_text(
                        'header', plugin_version, 'center'), 'header'),
                W.get_blank_flow()
            ])
        ]
        plugin_details_rows.append(W.get_div())
        for key, value in plugin_details.items():
            if isinstance(value, list):
                value = " | ".join(value)
            if value:
                plugin_details_rows.append(
                    W.get_col_row([
                        W.get_blank_flow(),
                        (15, W.get_text(
                            'default', str(key).capitalize(), 'left')),
                        (3, W.get_text('default', ' : ', 'center')),
                        W.get_text(
                            'default', self.parser.unescape(value), 'left'),
                        W.get_blank_flow()
                    ])
                )
        theme_details_pile = U.Pile(plugin_details_rows)
        filler = U.Filler(theme_details_pile)
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()

    def show_plugin_action_response(self, response_text=None):
        """Displays response from plugin-actions"""
        response_text = [
            W.get_col_row([
                W.get_blank_flow(),
                U.AttrMap(W.get_text('header', 'Result', 'center'), 'header'),
                W.get_blank_flow()
            ]),
            W.get_div()
        ]
        if response_text:
            result = response_text
            response_text.append(
                W.get_col_row([
                    W.get_blank_flow(),
                    W.get_text('default', result, 'left'),
                    W.get_blank_flow()
                ]))
        self.response_pile = U.Pile(response_text)
        filler = U.Filler(self.response_pile)
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()

    def update_view(self, wpcli_output):
        """Update's view from pipe"""
        L.debug("Update: %s", wpcli_output)
        if not wpcli_output:
            self.app.loop.remove_watch_pipe(self.app.wpcli_pipe)
        self.response_pile.contents.append((
            W.get_col_row([
                W.get_blank_flow(),
                W.get_text('default', wpcli_output, 'left'),
                W.get_blank_flow()
            ]), ('weight', 1)))

    def after_response(self):
        """Redirects to plugin_list after response"""
        time.sleep(2)
        self.app.views.actions.get_plugin_list()


class RevertChanges(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, user_args=None, calling_view=None):
        super(RevertChanges, self).__init__(app)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, **kwargs):
        L.debug(' kwargs : %s', kwargs)
        home_text = W.get_text(
            'body',
            'Obtaining List of Revisions...',
            'center')
        return U.Filler(home_text, 'middle')

    def after_action(self, revisions):
        """Displays after_action contents"""
        L.debug('list_of_revisions: %s', revisions)
        revisions_rows = [
            W.get_col_row([
                W.get_blank_flow(),
                U.AttrMap(W.get_text(
                    'header', 'Revision Time', 'center'), 'header'),
                U.AttrMap(W.get_text(
                    'header', 'Theme(s)', 'center'), 'header'),
                U.AttrMap(W.get_text(
                    'header', 'Plugin(s)', 'center'), 'header'),
                U.AttrMap(W.get_text(
                    'header', 'Database', 'center'), 'header'),
                U.AttrMap(W.get_blank_flow(), 'header'),
                W.get_blank_flow()
            ])
        ]
        for revision_time, revision_data in revisions.items():
            revision_datetime = datetime.datetime.strptime(
                revision_time,
                self.app.settings.datetime['date_string'])
            revision_time_str = revision_datetime.strftime(
                self.app.settings.datetime['string_date'])
            if 'themes' in revision_data.keys():
                themes = W.get_text(
                    'default',
                    '\n' + revision_data['themes'] + '\n', 'center')
            else:
                themes = W.get_blank_flow()
            if 'plugins' in revision_data.keys():
                plugins = W.get_text(
                    'default',
                    '\n' + revision_data['plugins'] + '\n', 'center')
            else:
                plugins = W.get_blank_flow()
            if 'databases' in revision_data.keys():
                databases = W.get_text(
                    'default',
                    '\n' + revision_data['databases'] + '\n', 'center')
            else:
                databases = W.get_blank_flow()
            restore_button = BoxButton(
                'Restore',
                on_press=self.app.views.actions.restore_revision,
                user_data=[revisions, revision_time]
            )
            revisions_rows.append(
                W.get_col_row([
                    W.get_blank_flow(),
                    W.get_text(
                        'default', '\n' + revision_time_str + '\n', 'center'),
                    themes, plugins, databases,
                    restore_button, W.get_blank_flow()
                ])
            )
        if not revisions:
            revisions_rows.append(
                W.get_col_row([
                    W.get_blank_flow(),
                    W.get_text(
                        'default',
                        'No Revisions available for restoration',
                        'center'),
                    W.get_blank_flow()
                ])
            )
        revisions_pile = U.Pile(revisions_rows)
        filler = U.Filler(revisions_pile)
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()

    def after_revert(self, result):
        """Displays results after reverting changes"""
        revision_time = datetime.datetime.strptime(
            result['revision'],
            self.app.settings.datetime['date_string']
        )
        revision_time_str = revision_time.strftime(
            self.app.settings.datetime['string_date']
        )
        result_rows = []
        result_rows.append(W.get_col_row([
            W.get_blank_flow(),
            U.AttrMap(
                W.get_text(
                    'header',
                    'Revision ' + revision_time_str + ' Results', 'center'),
                'header'),
            W.get_blank_flow()
        ]))
        for reversion_type, result in result.items():
            if 'revision' not in reversion_type:
                result_rows.append(
                    W.get_col_row([
                        W.get_blank_flow(),
                        W.get_text('default', reversion_type, 'center'),
                        W.get_text('default', result, 'center'),
                        W.get_blank_flow()
                    ])
                )
        self.pile = U.Pile(result_rows)
        filler = U.Filler(self.pile)
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()


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
