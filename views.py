import json
class Views():
    def __init__(self,app):
        self.app = app
        self.L = app.L
        self.W = app.W
        self.state = app.state
        with open('views.json','r') as views:
            views_json = json.load(views)
        self.L.debug('views_json: %s', views_json)
        for key,value in views_json.items():
            setattr(self,key,View(app,key,value))
    def activate(self,app,*args, **kwargs):
        self.L.debug('views.activate args: %s', args)
        current_view = self.state.get_state('active_view')
        self.state.set_state('previous_view',current_view)
        activating_view = getattr(self,args[0])
        self.state.set_state('active_view',activating_view)
        activating_view.start(app)
class View():
    def __init__(self,app,name,view_json_data):
        self.app = app
        self.app.L.debug("View %s Initialized", name)
        self.name = name
        self.view_type = view_json_data['view_type']
        self.title = view_json_data['title']
        self.sub_title = view_json_data['sub_title']
    def start(self,app):
        self.header = app.W.get_header(self.name,self.title,self.sub_title)
        self.footer = app.W.get_footer(self.name,self.app)
        self.body = app.W.get_body(self.name)
    def show_header(self):
        self.app.frame.contents.__setitem__('header', [self.header, None])
    def show_body(self):
        self.app.frame.contents.__setitem__('body', [self.body, None])
    def show_footer(self):
        self.app.frame.contents.__setitem__('footer', [self.footer, None])
    def draw_screen(self):
        self.app.loop.draw_screen()
    def set_focus(self, focus_position):
        self.app.frame.set_focus(focus_position)