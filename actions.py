"""When a view finishes loading to the screen,
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

    def get_installations(self):
        """searches user's homedir for wp installations
        and calls wp-cli command to get general installation
        information
        """
        L.debug("get_installations Action Started")
        self.installations = Installations(self.app)
        #active_view = self.app.state.active_view
        #self.app.loop.event_loop.remove_enter_idle(active_view.action_handler)
        self.app.views.Installs.body.after_action(self.installations.installations)
    def get_database_information(self):
        """Obtains general database information and table status
        """
        L.debug("get_database_information Action Started")
        self.database_information = DatabaseInformation(self.app)
        L.debug('db_info: %s', self.database_information.db_info)
        self.app.views.Database.body.after_action(self.database_information.db_info)
        #active_view = self.app.state.active_view
    def get_wp_config(self):
        """Obtains wp_config information
        """
        L.debug("get_wp_config Action Started")
        self.wp_config.get_wp_config()
        L.debug('wp_config: %s', self.wp_config)
        self.app.views.GetWpConfig.body.after_action(self.wp_config)
    def set_wp_config(self, edit_map, directive_name, directive_value, remove=False):
        """Sets a single wp_config directive.
        This is used by the wp_config display screen edit widgets"""
        if remove:
            result = self.wp_config.del_wp_config(directive_name)
        else:
            result = self.wp_config.set_wp_config(directive_name, directive_value)
        L.debug("wp-cli set config result: %s", result)
        L.debug("edit_map: %s", edit_map)
        if result:
            edit_map.set_attr_map({None:'body'})
        else:
            edit_map.set_attr_map({None:'alert'})
    def re_salt(self):
        """Refreshes the salts defined in the wp-config.php"""
        self.wp_config.re_salt()
        self.app.views.activate(self.app, 'GetWpConfig')
    def db_export(self):
        """Exports Database"""
        L.debug("Export Database Action Started")
        if hasattr(self, 'database_information'):
            L.debug("self.database_information exists")
            export_result = self.database_information.export()
        else:
            L.debug("No  Database for this WP Install \n \
                Or no WP Installation selected")
            export_result = "No  Database for this WP Install \n \
                Or no WP Installation selected"
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
    def import_db(self,*args):
        """Performs actual import"""
        L.debug("Args: %s", args)
