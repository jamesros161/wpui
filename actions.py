"""When view finishes loading to the screen,
if it has an "action_on_load" attribute set,
then the cooresponding method of Actions will be called.

Any views that have to load a separate thread or process"""
import os
import shutil
import datetime
from logmod import Log
from wpcli import Installations, DatabaseInformation, WpConfig
from wpcli import Themes, Plugins
L = Log()


class Actions(object):
    """This class contains all the action methods
        that are called after a view loads"""

    def __init__(self, app):
        self.app = app
        self.revisions = RevisionActions(app)
        self.wp_config = WpConfigActions(app)
        self.plugins = PluginActions(app, self.revisions)
        self.database = DatabaseActions(app, self.revisions)
        self.themes = ThemeActions(app, self.revisions)

    def change_text_attr(self, main_loop, changes):
        """Changes the attribute of a text_object as part
        of an alarm callback"""
        L.debug('main_loop: %s, changes: %s', main_loop, changes)
        text_object = changes[0]
        new_attr = changes[1]
        text = text_object.get_text()[0]
        text_object.set_text(
            (new_attr, text)
        )


class DatabaseActions(object):
    """Actions related to Database functions"""

    def __init__(self, app, revisions):
        self.app = app
        self.revisions = revisions
        self.wpcli = DatabaseInformation(app)
        self.db_exported = False
        self.sr_search_term = None
        self.replace_term = None

    def wpcli_not_exist(self):
        """Checks if the database's wpcli instance exists"""

        if hasattr(self, 'wpcli'):
            L.debug("DatabaseActions.wpcli exists")
            return False
        else:
            return self.app.settings.messages["db_not_exist"]

    def get_database_information(self):
        """Obtains general database information and table status
        """
        db_info = self.wpcli.get_db_size()
        L.debug('db_info: %s', db_info)
        self.app.views.Database.body.after_action(
            db_info)

    def db_export(self, button_instance,
                  silent=False, file_path=None):
        """Exports Database to the file_path and displays result
        unless the silent option is set, in which case it returns
        False, and does not load the result view page."""

        L.debug("Export Database Action Started: %s",
                button_instance)

        if self.wpcli_not_exist():
            export_result = self.wpcli_not_exist()
            L.warning(export_result)
            self.db_exported = False
            if silent:
                return False
        else:
            L.debug("DatabaseActions.wpcli exists")
            self.wpcli.export(file_path=file_path)
            if silent:
                if export_result == "Database Export Failed":
                    return False
                else:
                    return True
        if not silent:
            # self.app.views.DbExport.body.after_action(export_result)
            self.app.views.Database.body.show_database_action_response()

    def get_db_imports(self):
        """Obtains list of available .sql files to import
        that match the selected installation's currently set DB_NAME"""

        L.debug("Import Database Action Started")
        if self.wpcli_not_exist():
            import_list = False
            L.warning(self.wpcli_not_exist)
        else:
            import_list = self.wpcli.get_import_list()
            L.debug('Imports:  %s', import_list)
        self.app.views.DbImport.body.after_action(import_list)

    def import_db(self, button, path):
        """Performs actual import"""

        L.debug("button: %s, path: %s", button, path)
        self.revisions.auto_bk(backup_db=True)
        if self.wpcli_not_exist():
            import_results = self.wpcli_not_exist()
            L.warning(import_results)
        else:
            L.debug("self.database_information exists")
            import_results = self.wpcli.import_db(self.app, path)
        self.app.views.DbImport.body.after_import(import_results)

    def db_optimize(self, button):
        """Optimizes Database"""
        L.debug("Start db_optimize action: %s", button)
        self.revisions.auto_bk(backup_db=True)
        if self.wpcli_not_exist():
            optimize_results = self.wpcli_not_exist()
            L.warning(optimize_results)
        else:
            L.debug("self.wpcli exists")
            optimize_results = True
            self.wpcli.optimize_db()
        self.app.views.Database.body.show_database_action_response()

    def db_repair(self, button):
        """Repairs Database"""
        L.debug("Start db_repair action: %s", button)
        self.revisions.auto_bk(backup_db=True)
        if self.wpcli_not_exist():
            repair_results = self.wpcli_not_exist()
            L.warning(repair_results)
        else:
            L.debug("self.wpcli exists")
            repair_results = True
            self.wpcli.db_repair()
        self.app.views.Database.body.show_database_action_response()

    def db_search(self, edit, query):
        """Search Database for Query"""
        L.debug('Edit Obj: %s, Query: %s', edit, query)
        if self.wpcli_not_exist():
            db_search_results = self.wpcli_not_exist()
            L.warning(db_search_results)
        else:
            L.debug("self.database_information exists")
            db_search_results = self.wpcli.db_search(
                query)
        L.debug("DB Search Results: %s", db_search_results)
        self.app.views.DbSearch.body.after_action(
            db_search_results, query)

    def sr_search(self, origin, search_term):
        """obtains search and replace search term"""

        L.debug('Origin: %s, Search Term: %s', origin, search_term)
        self.sr_search_term = search_term
        self.db_exported = self.revisions.auto_bk(backup_db=True)

    def sr_dry_run(self):
        """search and replace dry run"""
        search_term = self.app.state.sr_search_term
        replace_term = self.app.state.sr_replace_term
        L.debug('Search_term: %s, Replace_term: %s', search_term, replace_term)
        results = self.wpcli.search_replace(
            search_term,
            replace_term,
            dry_run=True)
        self.db_exported = self.revisions.auto_bk(backup_db=True)
        self.db_exported = not self.db_exported
        self.app.views.SearchReplace.body.after_dry_run(
            search_term,
            replace_term,
            results,
            self.db_exported)

    def sr_replace(self, origin, terms):
        """Replaces search_term with replace_term"""
        L.debug('Origin: %s, Search_term: %s,  Replace_term: %s',
                origin, terms[0], terms[1])
        results = self.wpcli.search_replace(
            terms[0],
            terms[1],
            dry_run=False)
        self.app.views.SearchReplace.body.after_replacement(
            results
        )


class PluginActions(object):
    """Set of actions performed on plugins"""

    def __init__(self, app, revisions):
        self.app = app
        self.wpcli = Plugins(app)
        self.revisions = revisions

    def activate(self, plugin):
        """activates a given plugin"""

        self.wpcli.activate(plugin['name'])
        self.app.views.Plugins.body.show_plugin_action_response()

    def deactivate(self, plugin):
        """Deactivates a given plugin"""

        self.wpcli.deactivate(plugin['name'])
        self.app.views.Plugins.body.show_plugin_action_response()

    def deactivate_all(self):
        """Deactivates all active plugins, and stores a list
        of the plugins that were active"""

        active_plugins = self.wpcli.get_active_plugins()
        L.debug('Active Plugins: %s', active_plugins)
        self.app.views.Plugins.body.deactivated_plugins = active_plugins
        self.wpcli.deactivate('--all')
        self.app.views.Plugins.body.show_plugin_action_response()

    def get_plugin_list(self):
        """Gets list of plugins"""

        plugin_list = self.wpcli.get_plugin_list()
        L.debug('Plugin_list: %s', plugin_list)
        self.app.views.Plugins.body.after_action(
            plugin_list)

    def install_plugin(self, edit_widget, edit_text):
        """Installs a plugin from wordpress.org repo"""

        L.debug("edit_widget: %s, edit_text: %s", edit_widget, edit_text)
        self.app.views.Plugins.body.show_plugin_action_response()
        self.wpcli.install(edit_text)
        L.debug('wpcli_pipe fstat: %s', os.fstat(self.app.wpcli_pipe))

    def reactivate_all(self):
        """Reactivates all plugins that were previously deactivated
        by deactivate_all"""
        result = self.wpcli.set_active_plugins(
            self.app.views.Plugins.body.deactivated_plugins
        )
        self.app.views.Plugins.body.deactivated_plugins = []
        self.app.views.Plugins.body.show_plugin_action_response(
            response_text=result)
        self.app.views.Plugins.body.after_response()

    def details(self, plugin):
        """Obtain plugin details"""

        plugin_details = self.wpcli.get_details(plugin['name'])
        L.debug('Plugin Details: %s', plugin_details)
        self.app.views.Plugins.body.show_plugin_details(
            plugin_details
        )

    def update_all(self):
        """Updates all plugins"""

        L.debug('Update All')
        plugin_dir = self.wpcli.get_plugin_path()
        L.debug('Plugin_dir: %s', plugin_dir)
        if not self.revisions.auto_bk(
                plugin_src=plugin_dir,
                plugin_dest=('plugins/' + 'all_plugins'),
                backup_plugins=True,
                backup_db=True):
            self.app.views.Plugin.backup_failed = True
        self.app.views.Plugins.body.show_plugin_action_response()
        self.wpcli.update('--all')
        L.debug('wpcli_pipe fstat: %s', os.fstat(self.app.wpcli_pipe))

    def update(self, plugin):
        """Updates specified plugin"""

        plugin_dir = self.wpcli.get_plugin_path(plugin['name'])
        L.debug('Plugin_dir: %s', plugin_dir)
        if not self.revisions.auto_bk(
                plugin_src=plugin_dir,
                plugin_dest=('plugins/' + plugin['name']),
                backup_plugins=True,
                backup_db=True):
            self.app.views.Plugin.backup_failed = True
        self.app.views.Plugins.body.show_plugin_action_response()
        self.wpcli.update(plugin['name'])
        L.debug('wpcli_pipe fstat: %s', os.fstat(self.app.wpcli_pipe))

    def uninstall(self, plugin):
        """Uninstalls specified plugin"""

        plugin_dir = self.wpcli.get_plugin_path(plugin['name'])
        L.debug('Plugin_dir: %s', plugin_dir)
        if not self.revisions.auto_bk(
                plugin_src=plugin_dir,
                plugin_dest=('plugins/' + plugin['name']),
                backup_themes=False):
            self.app.views.Plugin.backup_failed = True
        self.app.views.Plugins.body.show_plugin_action_response()
        self.wpcli.uninstall(plugin['name'])
        L.debug('wpcli_pipe fstat: %s', os.fstat(self.app.wpcli_pipe))


class RevisionActions(object):
    """This class contains the methods for generating
    and restoring revisions"""
    def __init__(self, app):
        self.app = app
        self.themes = ThemeActions(app, self)
        self.plugins = PluginActions(app, self)
        self.temp_dir = self.app.settings.app['temp_dir'].name
        L.debug('temp_dir: %s', self.temp_dir)

    def auto_bk(self, theme_src=None, theme_dest=None,
                plugin_src=None, plugin_dest=None,
                backup_db=False, backup_themes=False, backup_plugins=False):
        """Automatically backups database, themes, and / or plugins
        to allow for reverting changes. Returns False if any of the backups
        fail."""

        L.debug('Plugin_src: %s, Plugin_dest: %s', plugin_src, plugin_dest)
        bk_result = []
        bk_options = {}
        # Generates the date-time portion of reversion names.
        bk_options['copy_time'] = (
            datetime.datetime.now().strftime(
                self.app.settings.datetime['date_string']))
        bk_options['temp_dir'] = self.temp_dir
        # install_dir is the name of the wp doc_root without
        # the full path
        bk_options['install_dir'] = os.path.split(
            self.app.state.active_installation['directory'])[1]
        # call to database backup function
        if backup_db:
            if not self.bkdb(self.app, bk_options):
                bk_result.append('Database Backup Failed')
        # call to file backup function for themes
        if backup_themes:
            if not self.copy_dir(
                    bk_options, theme_src, theme_dest):
                bk_result.append('Theme Backup Failed')
        # Call to file backup function for plugins
        if backup_plugins:
            if not self.copy_dir(
                    bk_options, plugin_src, plugin_dest):
                bk_result.append('Plugin Backup Failed')
        # if any backup fails, logs error and returns False
        if bk_result:
            error = '\n'.join(bk_result)
            L.warning('%s', error)
            return False
        return True

    @staticmethod
    def bkdb(app, bk_options):
        """exports database to temp dir
        Returns true if successful, False if it fails"""

        db_name = app.state.active_installation['db_name']
        dest = db_name + '-' + bk_options['copy_time'] + '.sql'
        # bkdb_dir is the path where the database revisions are stored
        bkdb_dir = os.path.join(
            bk_options['temp_dir'], bk_options['install_dir'], 'databases')
        # if bkdb_dir soes not exist, it will be created
        if not os.path.isdir(bkdb_dir):
            os.makedirs(bkdb_dir)
        # absolute filepath of the db to be exported by wp db export
        bkdb_path = os.path.join(bkdb_dir, dest)
        if DatabaseInformation.export_db(app, file_path=bkdb_path):
            return True
        else:
            return False

    @staticmethod
    def copy_dir(bk_options, src, dest):
        """Copies theme or plugin directory to temp_dir
        Returns true if successful, False if it fails"""

        dest = dest + '-' + bk_options['copy_time']
        install_temp_dir = os.path.join(
            bk_options['temp_dir'], bk_options['install_dir'])
        destination = os.path.join(install_temp_dir, dest)
        if not os.path.isdir(bk_options['temp_dir']):
            try:
                os.makedirs(bk_options['temp_dir'])
            except (shutil.Error, OSError, IOError) as error:
                L.warning('Error making temp_dir: %s', error)
                return False
        try:
            shutil.copytree(src, destination)
        except (shutil.Error, OSError, IOError) as error:
            L.warning('Error backing up to temp_dir: %s', error)
            return False
        L.debug("%s copied to %s", src, destination)
        return True

    def get_revisions(self, *args):
        """Obtains list of available revisions"""
        # install_dir is the document root of the WP install
        # without the full path
        L.debug('Args: %s', args)
        install_dir = os.path.split(
            self.app.state.active_installation['directory'])[1]
        # dict for the directories the revisions can be found
        revision_dirs = {
            'themes': os.path.join(
                self.temp_dir, install_dir,
                'themes'),
            'databases': os.path.join(
                self.temp_dir, install_dir,
                'databases'),
            'plugins': os.path.join(
                self.temp_dir, install_dir,
                'plugins')
        }
        revisions = {}
        for revision_type, revision_dir in revision_dirs.items():
            if os.path.isdir(revision_dir):
                available_revisions = os.listdir(revision_dir)
                for revision in available_revisions:
                    split_rev = revision.split('-')
                    L.debug('split_rev: %s', split_rev)
                    if '.sql' in split_rev[1]:
                        split_sql = split_rev[1].split('.')
                        revision_time = split_sql[0]
                    else:
                        revision_time = split_rev[1]
                    if revision_time in revisions.keys():
                        revisions[revision_time][revision_type] = split_rev[0]
                    else:
                        revisions[revision_time] = {}
                        revisions[revision_time][revision_type] = split_rev[0]
        L.debug('Available Revisions: %s', revisions)
        self.app.views.RevertChanges.body.after_action(
            revisions)

    def restore_revision(self, button, user_data):
        """Restores revisions"""

        L.debug(
            'Button: %s, Revisions: %s, Revision to Restore: %s',
            button, user_data[0], user_data[1])
        revisions = user_data[0]
        revision_time = user_data[1]
        install_dir = os.path.split(
            self.app.state.active_installation['directory'])[1]
        theme_root = self.themes.wpcli.get_theme_root()
        plugin_root = self.plugins.wpcli.get_plugin_path()
        results = {
            'revision': revision_time,
            'themes': 'N/A',
            'plugins': 'N/A',
            'databases': 'N/A',
        }
        for revision_type, revision_name in revisions[revision_time].items():
            if 'database' in revision_type:
                revision_dirname = revision_name + '-' + \
                    revision_time + '.sql'
                revision_path = os.path.join(
                    self.temp_dir, install_dir, 'databases', revision_dirname)
                result = DatabaseInformation.import_db(self.app, revision_path)
                if result:
                    results['databases'] = 'Successful'
                else:
                    results['databases'] = 'Failed'
            else:
                revision_dirname = revision_name + '-' + \
                    revision_time
                revision_path = os.path.join(
                    self.temp_dir,
                    install_dir,
                    revision_type,
                    revision_dirname)
                if 'theme' in revision_type:
                    destination_dir = os.path.join(
                        theme_root, revision_name)
                if 'plugin' in revision_type:
                    destination_dir = os.path.join(
                        plugin_root, revision_name)
                if os.path.isdir(destination_dir):
                    shutil.rmtree(destination_dir)
                try:
                    shutil.move(revision_path, destination_dir)
                except shutil.Error as error:
                    L.warning('Error restoring revision: %s', error)
                    results[revision_type] = "Failed"
                else:
                    results[revision_type] = "Successful"
            L.debug('Restore Results: %s', results)
            self.app.views.RevertChanges.body.after_revert(results)


class ThemeActions(object):
    """Actions related to theme functions"""
    def __init__(self, app, revisions):
        self.app = app
        self.wpcli = Themes(app)
        self.theme_list = None
        self.revisions = revisions

    def get_theme_list(self):
        """obtains list of themes"""

        self.theme_list = self.wpcli.get_list()
        self.app.views.Themes.body.after_action(
            self.theme_list)

    def theme_actions(self, *args):
        """performs option actions on themes"""
        # L.debug('Args: %s', args)
        action_type = args[0].label
        theme = args[1][0]
        L.debug('button: %s, action_type: %s, theme: %s',
                args[0], action_type, theme)

    def details(self, theme):
        """Obtain Theme Details"""

        theme_details = self.wpcli.get_details(theme['name'])
        L.debug('Theme Details: %s', theme_details)
        self.app.views.Themes.body.show_theme_details(
            theme_details
        )

    def activate(self, theme):
        """activate theme"""

        self.wpcli.activate(theme['name'])
        self.app.views.Themes.body.show_theme_action_response()

    def update(self, theme):
        """Updates theme"""

        theme_dir = self.wpcli.get_details(theme['name'])['template_dir']
        if not self.revisions.auto_bk(
                theme_src=theme_dir,
                theme_dest=('themes/' + theme['name']),
                backup_themes=True,
                backup_db=True):
            self.app.views.Themes.backup_failed = True
        self.app.views.Themes.body.show_theme_action_response()
        self.wpcli.update(theme['name'])
        L.debug('wpcli_pipe fstat: %s', os.fstat(self.app.wpcli_pipe))

    def update_all(self):
        """Updates All Themes"""
        theme_dir = self.wpcli.get_theme_root()
        if not self.revisions.auto_bk(
                theme_src=theme_dir,
                theme_dest=('themes/' + 'all_themes'),
                backup_themes=True,
                backup_db=True):
            self.app.views.Themes.backup_failed = True
        self.app.views.Themes.body.show_theme_action_response()
        self.wpcli.update('--all')
        L.debug('wpcli_pipe fstat: %s', os.fstat(self.app.wpcli_pipe))

    def uninstall(self, theme):
        """Uninstalls theme"""

        theme_dir = self.wpcli.get_details(theme['name'])['template_dir']
        if self.revisions.auto_bk(
                theme_src=theme_dir,
                theme_dest=('themes/' + theme['name']),
                backup_themes=True,
                backup_db=True):
            self.app.views.Themes.backup_failed = True
        self.app.views.Themes.body.show_theme_action_response()
        self.wpcli.uninstall(theme['name'])
        L.debug('wpcli_pipe fstat: %s', os.fstat(self.app.wpcli_pipe))

    def install_theme(self, edit_widget, edit_text):
        """Install a theme from wordpress.org repo"""

        L.debug("edit_widget: %s, edit_text: %s", edit_widget, edit_text)
        self.app.views.Themes.body.show_theme_action_response()
        self.wpcli.install(edit_text)
        L.debug('wpcli_pipe fstat: %s', os.fstat(self.app.wpcli_pipe))


class WpConfigActions(object):
    """Actions related to WpConfig"""

    def __init__(self, app):
        self.app = app
        self.wpcli = WpConfig(self.app)

    def get_installations(self):
        """searches user's homedir for wp installations
        and calls wp-cli command to get general installation
        information
        """
        L.debug("get_installations Action Started")
        installations = Installations(self.app)
        self.app.views.Installs.body.after_action(
            installations.installations)

    def get_wp_config(self):
        """Obtains wp_config information
        """
        L.debug("get_wp_config Action Started")
        self.wpcli.get_wp_config()
        L.debug('wp_config: %s', self.wpcli)
        self.app.views.GetWpConfig.body.after_action(self.wpcli)

    def set_wp_config(self, options):
        """Sets a single wp_config directive.
        This is used by the wp_config display screen edit widgets"""
        directive_name = options['user_data']['directive_name']
        directive_value = options['edit_text']
        edit_map = options['attr_map']
        if options['user_data']['remove']:
            result = self.wpcli.del_wp_config(directive_name)
        else:
            result = self.wpcli.set_wp_config(
                directive_name,
                directive_value)
        L.debug("wp-cli set config result: %s", result)
        L.debug("edit_map: %s", edit_map)
        if result:
            edit_map.set_attr_map({None: 'body'})
        else:
            edit_map.set_attr_map({None: 'alert'})

    def re_salt(self, *args):
        """Refreshes the salts defined in the wp-config.php"""
        L.debug("re_salt Args: %s", args)
        self.wpcli.re_salt()
        self.app.views.activate(self.app, 'GetWpConfig')
