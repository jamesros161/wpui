import json, importlib, BodyWidgets, threading
#BodyWidgets = importlib.import_module('BodyWidgets')
from actions import Actions
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
        #current_view = self.state.get_state('active_view')
        activating_view = getattr(self,args[0])
        if not "no_view_chain" in activating_view.view_type:
            self.state.view_chain_pos += 1
            self.state.set_view(activating_view)
        #self.state.set_view(activating_view)
        activating_view.start()
class View():
    def __init__(self,app,name,view_json_data):
        self.app = app
        self.app.L.debug("View %s Initialized", name)
        self.name = name
        self.actions = Actions(app)
        self.view_type = view_json_data['view_type']
        self.title = view_json_data['title']
        self.sub_title = view_json_data['sub_title']
        self.action_on_load = view_json_data['action_on_load']
    def start(self):
        self.header = self.app.W.get_header(self.name,self.title,self.sub_title)
        self.footer = self.app.W.get_footer(self.name,self.app)
        self.set_view_body()
        self.show_header()
        self.show_body()
        self.show_footer()
        if self.view_type == 'no_input':
            self.set_focus('footer')
        else:
            self.set_focus('body')
        if self.action_on_load:
            self.app.L.debug('This View has an action to be run on load')
            action = getattr(self.actions,self.action_on_load)
            action()
    def reload(self):
        self.show_header()
        self.show_body()
        self.show_footer()
    def show_header(self):
        self.app.frame.contents.__setitem__('header', [self.header, None])
    def show_body(self):
        self.app.frame.contents.__setitem__('body', [self.body.widget, None])
    def show_footer(self):
        self.app.frame.contents.__setitem__('footer', [self.footer, None])
    def draw_screen(self):
        self.app.loop.draw_screen()
    def set_focus(self, focus_position):
        self.app.frame.set_focus(focus_position)
    def set_view_body(self, *args):
        #debug('BodyWidgets.get_body_widget:: view_name: %s :: args: %s', view_name, args)
        BodyClass = getattr(BodyWidgets, self.name)
        self.body = BodyClass(self.app,user_args=args, calling_view=self)
        