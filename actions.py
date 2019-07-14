"""When view finishes loading to the screen,
if it has an "action_on_load" attribute set,
then the cooresponding method of Actions will be called.

Any views that have to load a separate thread or process"""
from logmod import Log
from wpcli import Installations, DatabaseInformation, WpConfig
L = Log()


class Actions(object):
    """This class contains all the action methods
        that are called after a view loads"""

    def __init__(self, app):
        self.app = app
        self.installations = None
        self.database_information = None
        self.wp_config = WpConfig(self.app)
        self.db_exported = False
        self.sr_search_term = ''

    def get_installations(self):
        """searches user's homedir for wp installations
        and calls wp-cli command to get general installation
        information
        """
        L.debug("get_installations Action Started")
        self.installations = Installations(self.app)
        self.app.views.Installs.body.after_action(
            self.installations.installations)

    def get_database_information(self):
        """Obtains general database information and table status
        """
        L.debug("get_database_information Action Started")
        self.database_information = DatabaseInformation(self.app)
        L.debug('db_info: %s', self.database_information.db_info)
        self.app.views.Database.body.after_action(
            self.database_information.db_info)

    def get_wp_config(self):
        """Obtains wp_config information
        """
        L.debug("get_wp_config Action Started")
        self.wp_config.get_wp_config()
        L.debug('wp_config: %s', self.wp_config)
        self.app.views.GetWpConfig.body.after_action(self.wp_config)

    def set_wp_config(self,
                      edit_map,
                      directive_name,
                      directive_value,
                      remove=False
                      ):
        """Sets a single wp_config directive.
        This is used by the wp_config display screen edit widgets"""
        if remove:
            result = self.wp_config.del_wp_config(directive_name)
        else:
            result = self.wp_config.set_wp_config(
                directive_name,
                directive_value)
        L.debug("wp-cli set config result: %s", result)
        L.debug("edit_map: %s", edit_map)
        if result:
            edit_map.set_attr_map({None: 'body'})
        else:
            edit_map.set_attr_map({None: 'alert'})

    def re_salt(self):
        """Refreshes the salts defined in the wp-config.php"""
        self.wp_config.re_salt()
        self.app.views.activate(self.app, 'GetWpConfig')

    def db_export(self, silent=False):
        """Exports Database"""
        L.debug("Export Database Action Started")
        if hasattr(self, 'database_information'):
            L.debug("self.database_information exists")
            export_result = self.database_information.export()
            self.db_exported = True
            if silent:
                if export_result == "Database Export Failed":
                    return False
                else:
                    return True
        else:
            L.debug("No  Database for this WP Install \n \
                Or no WP Installation selected")
            export_result = "No  Database for this WP Install \n \
                Or no WP Installation selected"
            self.db_exported = False
            if silent:
                return False
        if not silent:
            self.app.views.DbExport.body.after_action(export_result)

    def get_db_imports(self):
        """Imports Databases"""
        L.debug("Import Database Action Started")
        if hasattr(self, 'database_information'):
            import_list = self.database_information.get_import_list()
            L.debug('Imports:  %s', import_list)
        else:
            import_list = False
        self.app.views.DbImport.body.after_action(import_list)

    def import_db(self, button, path):
        """Performs actual import"""
        L.debug("button: %s, path: %s", button, path)
        if hasattr(self, 'database_information'):
            L.debug("self.database_information exists")
            import_results = self.database_information.import_db(path)
        else:
            L.debug("No  Database for this WP Install \n \
                Or no WP Installation selected")
            import_results = "No  Database for this WP Install \n \
                Or no WP Installation selected"
        self.app.views.DbImport.body.after_import(import_results)

    def db_optimize(self):
        """Optimizes Database"""
        L.debug("Start db_optimize action")
        path = self.app.state.active_installation['directory']
        if hasattr(self, 'database_information'):
            L.debug("self.database_information exists")
            optimize_results = self.database_information.optimize_db(path)
        else:
            L.debug("No  Database for this WP Install \n \
                Or no WP Installation selected")
            import_results = "No  Database for this WP Install \n \
                Or no WP Installation selected"
        self.app.views.DbOptimize.body.after_action(optimize_results)

    def db_repair(self):
        """Optimizes Database"""
        L.debug("Start db_repair action")
        path = self.app.state.active_installation['directory']
        if hasattr(self, 'database_information'):
            L.debug("self.database_information exists")
            db_repair_results = self.database_information.db_repair(path)
        else:
            L.debug("No  Database for this WP Install \n \
                Or no WP Installation selected")
            import_results = "No  Database for this WP Install \n \
                Or no WP Installation selected"
        self.app.views.DbRepair.body.after_action(db_repair_results)

    def db_search(self, edit, query):
        """Search Database for Query"""
        L.debug('Query: %s', query)
        path = self.app.state.active_installation['directory']
        if hasattr(self, 'database_information'):
            L.debug("self.database_information exists")
            db_search_results = self.database_information.db_search(
                path, query)
        else:
            L.debug("No  Database for this WP Install \n \
                Or no WP Installation selected")
            import_results = "No  Database for this WP Install \n \
                Or no WP Installation selected"
        L.debug("DB Search Results: %s", db_search_results)
        self.app.views.DbSearch.body.after_action(
            db_search_results, query)

    def sr_search(self, origin, search_term):
        L.debug('Origin: %s, Search Term: %s', origin, search_term)
        self.sr_search_term = search_term
        self.db_exported = self.db_export(silent=True)

    def sr_replace(self, origin, replace_term, dry_run=True):
        L.debug('Origin: %s, Replace Term: % s, db_exported: %s',
                origin, replace_term, self.db_exported)
        if isinstance(replace_term, basestring):
            L.debug('replace_term is string: %s', type(replace_term))
            self.replace_term = replace_term
        else:
            L.debug('replace_term is not string: %s', type(replace_term))
            dry_run = replace_term[0]
        path = self.app.state.active_installation['directory']
        db_export_message = ''
        results = []
        if not self.db_exported:
            db_exported = self.db_export(silent=True)
            L.debug("Second Try to Export: %s", db_exported)
            if db_exported:
                pass
            else:
                L.warning('DB Export Failed!')
                db_export_message = (
                    "WP-CLI Failed to Export this site's database.\n"
                    "Proceed with Search & Replace with caution\n")
        if dry_run:
            results, count = self.database_information.sr_search_replace(
                path,
                self.sr_search_term,
                self.replace_term,
                dry_run=True
            )
            self.app.views.SearchReplace.body.after_dry_run(
                results, count, db_export_message)
        else:
            results, count = self.database_information.sr_search_replace(
                path,
                self.sr_search_term,
                self.replace_term,
                dry_run=False
            )
            self.app.views.SearchReplace.body.after_replacement(
                results, count, db_export_message)
