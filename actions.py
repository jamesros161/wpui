from wpcli import Installations
class Actions():
    def __init__(self,app):
        self.app = app
    def get_installations(self):
        self.app.L.debug("get_installations Action Started")
        installations = Installations(self.app)
        active_view = self.app.state.active_view
        self.app.loop.event_loop.remove_enter_idle(active_view.action_handler)
        self.app.views.installs.body.after_action(installations.installations)