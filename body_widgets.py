"""Collection of classes each used for a view"""
import datetime
import time
import getpass
from html.parser import HTMLParser
from collections import OrderedDict
import urwid as U
from logmod import Log
from settings import Settings
from widgets import CustomWidgets, BoxButton, WpConfigValueMap
from widgets import DbImportEditMap, DbSearchEditMap
from widgets import SRSearchEditMap
S = Settings()
L = Log()
W = CustomWidgets()


class BodyWidget(object):
    """Parent Class for body widgets

    Returns:
        obj -- Returns a widget to be used as the 'body' portion of the frame
    """

    def __init__(self, app, initial_text, progress_bar=False):
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
        L.debug(' Initial_Text : %s, Progress_bar: %s',
                initial_text, progress_bar)
        if initial_text:
            initial_text_str = str(initial_text)
        else:
            initial_text_str = str(' ')
        initial_text = W.get_text(
            'body',
            str(initial_text_str),
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
            L.debug('self.app.action_pipe: %s', self.app.action_pipe)
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
        L.debug('Progress: %s', progress)
        if progress:
            self.progress_bar.set_completion(int(float(progress)))
        else:
            self.progress_bar.set_completion(100)
            try:
                self.app.loop.remove_watch_pipe(self.app.action_pipe)
            except OSError:
                L.Warning('Error trying to remove watch_pipe')
            self.app.loop.draw_screen()

# ADD SUBCLASSES HERE for each view's body


class Home(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(Home, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)


class Invalid(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(Invalid, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)


class Installs(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(Installs, self).__init__(
            app, initial_text, progress_bar=progress_bar)
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

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(GetWpConfig, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def after_action(self, wp_config):
        """Updates the view's body in response to the
        views action_on_load function
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
                on_enter=self.app.views.actions.wp_config.set_wp_config,
                user_data={'directive_name': str(directive['name'])},
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
        add_option_name_button = WpConfigValueMap(
            self,
            'underline',
            user_data={'option_value_widget': add_option_value_button},
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
                    on_press=self.app.views.actions.wp_config.re_salt
                ),
                W.get_blank_flow()
            ])
        )
        self.pile = U.Pile(directives_list)
        filler = U.Filler(self.pile)
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()


class Database(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(Database, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)
        self.menu_items = self.app.menus.DbSubMenu.items
        self.response_pile = None

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
        options = [W.get_blank_flow()]
        for item in self.menu_items:
            if 'action' in item[1].keys():
                action_class = getattr(
                    self.app.views.actions, item[1]['action_class'])
                action = getattr(action_class, item[1]['action'])
                options.append((
                    len(item[0].lstrip().rstrip()) + 8,
                    BoxButton(
                        item[0],
                        on_press=action,
                        strip_padding=True)))
            if 'view' in item[1].keys():
                action = self.app.views.activate
                options.append((
                    len(item[0].lstrip().rstrip()) + 8,
                    BoxButton(
                        item[0],
                        on_press=action,
                        user_data=item[1],
                        strip_padding=True)))
        options.append(W.get_blank_flow())
        db_info_rows.extend([
            W.get_div(),
            W.get_div(),
            W.get_col_row(options)
        ])
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

    def show_database_action_response(self, response_text=None):
        """Displays response from plugin-actions"""
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
        if self.response_pile:
            self.response_pile.contents.append((
                W.get_col_row([
                    W.get_blank_flow(),
                    W.get_text('default', wpcli_output, 'left'),
                    W.get_blank_flow()
                ]), ('weight', 1)))

    def after_response(self):
        """Redirects to plugin_list after response"""
        time.sleep(2)
        self.app.views.actions.database.get_database_information()


class DbImport(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(DbImport, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

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
                            on_press=self.app.views.actions.database.import_db,
                            user_data=item)),
                        W.get_blank_flow()
                    ])
                )
        import_edit = DbImportEditMap(
            self.app,
            'body',
            edit_text=self.app.state.homedir,
            align='left',
            on_enter=self.app.views.actions.database.import_db,
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

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(DbOptimize, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

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

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(DbRepair, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

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

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(DbSearch, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, initial_text, progress_bar=False):
        L.debug(' initial_text : %s', initial_text)
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
                    on_enter=self.app.views.actions.database.db_search,
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

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(SearchReplace, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, initial_text, progress_bar=False):
        L.debug(' initial_text : %s', initial_text)
        self.sr_pile = SRSearchEditMap(self.app)
        return U.Filler(self.sr_pile, 'middle')

    def after_dry_run(self, search_term, replace_term, results, db_export):
        """Displays the Search-replace dry-run results"""

        L.debug('results: %s', results)
        dry_run_rows = []
        if not db_export:
            db_export_msg = self.app.settings.messages['db_export_warning']
            db_export_msg = db_export_msg + \
                self.app.settings.messages['mycophagists']
            L.debug('db_export_message: %s', db_export_msg)
            dry_run_rows.append(
                W.get_col_row([
                    W.get_blank_flow(),
                    U.AttrMap(
                        W.get_text(
                            'flashing', db_export_msg, 'center'),
                        'flashing'),
                    W.get_blank_flow()
                ])
            )
            dry_run_rows.append(W.get_div())
        header_string = 'There are ' + str(results['count']) + \
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
        if str(results['count']) == '0':
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
        if str(results['count']) != '0':
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
            for result in results['results']:
                if not isinstance(result, str):
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
            sr_replace = self.app.views.actions.database.sr_replace
            L.debug('sr_replace: %s', sr_replace)
            dry_run_rows.append(
                W.get_col_row([
                    W.get_blank_flow(),
                    BoxButton(
                        'Perform Replacement',
                        on_press=sr_replace,
                        user_data=[search_term, replace_term]),
                    BoxButton(
                        'New Search & Replace',
                        on_press=self.app.views.activate,
                        user_data='SearchReplace'),
                    W.get_blank_flow()
                ])
            )
        pile = U.Pile(dry_run_rows)
        if not db_export:
            self.app.loop.set_alarm_in(
                5, self.app.views.actions.change_text_attr,
                user_data=[
                    pile.contents[0][0].contents[1][0].original_widget,
                    'alert'
                ])
        filler = U.Filler(pile, 'middle')
        self.app.frame.contents.__setitem__('body', [filler, None])
        time.sleep(1)
        self.app.loop.draw_screen()

    def after_replacement(self, results):
        """Displays search-replace results after replacement"""

        L.debug("After Replacement: %s", results)
        replaced_rows = []
        if results:
            replaced_rows.append(
                W.get_col_row([
                    W.get_blank_flow(),
                    U.AttrMap(W.get_blank_flow(), 'header'),
                    U.AttrMap(
                        W.get_text(
                            'header',
                            'There were ' + str(results['count']) +
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
            L.debug('results["results"]: %s', results['results'])
            for result in results['results']:
                if not isinstance(result, str):
                    L.debug('result["count"]: %s', result['count'])
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
                        on_press=self.app.views.activate,
                        user_data={
                            'view': 'RevertChanges',
                            'return_view': self.app.views.Database}),
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

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(Themes, self).__init__(
            app, initial_text, progress_bar=progress_bar)
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
                    on_press=self.app.views.actions.themes.details,
                    user_data=[theme]),
                BoxButton(
                    'Uninstall',
                    on_press=self.app.views.actions.themes.uninstall,
                    user_data=[theme])
            ])
            if theme['update'] == 'available':
                theme_row.append(BoxButton(
                    'Update',
                    on_press=self.app.views.actions.themes.update,
                    user_data=[theme]))
            else:
                theme_row.append(
                    W.get_blank_flow()
                )

            if theme['status'] == 'inactive':
                theme_row.append(BoxButton(
                    'Activate',
                    on_press=self.app.views.actions.themes.activate,
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
                    on_press=self.app.views.actions.themes.update_all,
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
                    on_enter=self.app.views.actions.themes.install,
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
        self.app.views.actions.themes.get_theme_list()


class InstallThemes(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(InstallThemes, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, initial_text, progress_bar=False):
        """shows initial widget"""

        L.debug(' initial_text : %s', initial_text)
        theme_install_edit = DbSearchEditMap(
            self.app,
            self,
            'body',
            caption='Enter Theme Name to Install: ',
            on_enter=self.app.views.actions.themes.install,
            align='center')

        return U.Filler(theme_install_edit, 'middle')


class Plugins(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(Plugins, self).__init__(
            app, initial_text, progress_bar=progress_bar)
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
                    on_press=self.app.views.actions.plugins.details,
                    user_data=[plugin]),
                BoxButton(
                    'Uninstall',
                    on_press=self.app.views.actions.plugins.uninstall,
                    user_data=[plugin])
            ])
            if plugin['update'] == 'available':
                plugin_row.append(BoxButton(
                    'Update',
                    on_press=self.app.views.actions.plugins.update,
                    user_data=[plugin]))
            else:
                plugin_row.append(
                    W.get_blank_flow()
                )

            if plugin['status'] == 'inactive':
                plugin_row.append(BoxButton(
                    'Activate',
                    on_press=self.app.views.actions.plugins.activate,
                    user_data=[plugin]))
            else:
                plugin_row.append(BoxButton(
                    'Deactivate',
                    on_press=self.app.views.actions.plugins.deactivate,
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
                on_press=self.app.views.actions.plugins.reactivate,
                user_data=self.deactivated_plugins)
        else:
            act_deact_all_plugins = BoxButton(
                'Deactivate All',
                on_press=self.app.views.actions.plugins.deactivate_all,
                user_data='--all')
        plugin_rows.append(
            W.get_col_row([
                W.get_blank_flow(),
                act_deact_all_plugins,
                BoxButton(
                    'Update All',
                    on_press=self.app.views.actions.plugins.update_all,
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
                    on_enter=self.app.views.actions.plugins.install,
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
        self.app.views.actions.plugins.get_plugin_list()


class RevertChanges(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(RevertChanges, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

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

        revisions_sorted = OrderedDict(sorted(revisions.items()))
        for revision_time, revision_data in revisions_sorted.items():
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
                on_press=self.app.views.actions.revisions.restore_revision,
                user_data=[revisions_sorted, revision_time]
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
        self.after_response()

    def after_response(self):
        """After response is displayed, redirect to theme list"""

        time.sleep(2)
        self.app.views.actions.themes.get_theme_list()


class Users(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(Users, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)


class Core(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(Core, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)


class Quit(BodyWidget):
    """Creates the specific body widget for the view of the same name"""

    def __init__(self, app, initial_text, user_args=None,
                 calling_view=None, progress_bar=False):
        super(Quit, self).__init__(
            app, initial_text, progress_bar=progress_bar)
        L.debug("user_args: %s, calling_view: %s", user_args, calling_view)

    def define_widget(self, initial_text, progress_bar=False):
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
