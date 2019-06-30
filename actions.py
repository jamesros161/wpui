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
        self.wp_config = None

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
        self.app.views.database.body.after_action(self.database_information.db_info)
        #active_view = self.app.state.active_view
    def get_wp_config(self):
        """Obtains wp_config information
        """
        L.debug("get_wp_config Action Started")
        self.wp_config = WpConfig(self.app)
        L.debug('wp_config: %s', self.wp_config)
        self.app.views.GetWpConfig.body.after_action(self.wp_config)
