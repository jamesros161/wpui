from wpcli import Installations, DatabaseInformation
class Actions():
    def __init__(self,app):
        self.app = app
    def get_installations(self):
        self.app.L.debug("get_installations Action Started")
        if not hasattr(self,'installations'):
            self.installations = Installations(self.app)
        #active_view = self.app.state.active_view
        #self.app.loop.event_loop.remove_enter_idle(active_view.action_handler)
        self.app.views.installs.body.after_action(self.installations.installations)
    def get_database_information(self):
        self.app.L.debug("get_database_information Action Started")
        self.database_information = DatabaseInformation(self.app)
        self.app.L.debug('db_info: %s', self.database_information.db_info)
        self.app.views.database.body.after_action(self.database_information.db_info)
        #active_view = self.app.state.active_view
    def get_wp_config(self):
        self.app.L.debug("get_wp_config Action Started")
        self.wp_config = WpConfig(self.app)
        self.app.L.debug('wp_config: %s', self.wp_config)
        self.app.views.getwpconfig.body.after_action(self.wp_config)