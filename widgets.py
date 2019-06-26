import urwid as U
class CustomWidgets():
    def __init__(self,S,L):
        self.S = S
        self.L = L
        L.debug("CustomWidgets Initialized")
    def get_text(self,format,textString, alignment,**kwargs):
        return U.Text((format, textString), align=alignment, wrap='space', **kwargs)
    def get_div(self,div_char=''):
        return U.Divider(div_char=div_char,top=0,bottom=0)
    def get_header(self,name,title,subtitle):
        if title:
            self.title = self.get_text('bold',title,'center')
        else:
            self.title = self.get_text('bold',self.S.display['title'],'center')
        if subtitle:
            self.subtitle = self.get_text('bold',subtitle,'center')
        else:
            self.subtitle = self.get_text('bold',self.S.display['subtitle'],'center')
        titleMap = U.AttrMap(self.title, 'bold')
        divMap = U.AttrMap(self.get_div(), 'body')
        if subtitle:
            subtitleMap = U.AttrMap(self.subtitle, 'bold')
            return U.Pile((titleMap, subtitleMap, divMap), focus_item=None)
        else:
            return U.Pile((titleMap, divMap), focus_item=None)
    def get_footer(self,name)

