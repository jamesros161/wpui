# -*- coding: utf-8 -*-
import urwid as U
PYTHONIOENCODING="utf-8"
class BoxButton(U.WidgetWrap):
    _border_char = u'─'
    def __init__(self, label, on_press=None, user_data=None, enabled=True):
        padding_size = 2
        border = self._border_char * (len(label) + padding_size * 2 )
        self.cursor_position = len(border) + padding_size
        self.top = u'┌' + border + u'┐\n'
        self.middle = u'│  ' + label + u'  │\n'
        self.bottom = u'└' + border + u'┘'
        self.on_press_action = on_press
        self.on_press_user_data = user_data
        self.enabled = enabled
        # self.widget = urwid.Text([self.top, self.middle, self.bottom])
        self.widget = U.Pile([
            U.Text(self.top[:-1],align='center'),
            U.Text(self.middle[:-1],align='center'),
            U.Text(self.bottom,align='center'),
        ])

        self.widget = U.AttrMap(self.widget, '', 'highlight')

        # self.widget = urwid.Padding(self.widget, 'center')
        # self.widget = urwid.Filler(self.widget)

        # here is a lil hack: use a hidden button for evt handling
        #debug('on_press: %s, user_data: %s', )
        self._hidden_btn = U.Button('hidden %s' % label, on_press, user_data)

        super(BoxButton, self).__init__(self.widget)

    def selectable(self):
        if self.enabled:
            return True
        else:
            return False
    def disable(self):
        self.enabled = False
    def enable(self):
        self.enabled = True

    def keypress(self, *args, **kw):
        return self._hidden_btn.keypress(*args, **kw)

    def mouse_event(self, *args, **kw):
        return self._hidden_btn.mouse_event(*args, **kw)
class CustomWidgets():
    def __init__(self,S,L):
        self.S = S
        self.L = L
        L.debug("CustomWidgets Initialized")
    def get_blank_box(self):
        return U.Filler(self.get_blank_flow())
    def get_blank_flow(self):
        return self.get_text('body','','center')
    def get_text(self,format,textString, alignment,**kwargs):
        return U.Text((format, textString), align=alignment, wrap='space', **kwargs)
    def get_div(self,div_char=' '):
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
    def get_footer(self,name,app):
        menu = app.menus.get_menu(name)
        menuItems = menu.items
        menuGridList = []
        for item in menuItems:
            if len(item) == 3:
                #menuList.append(
                    #w.getButton(item[0],views,'activate',user_data=(item[1],item[2])))
                    #(len(item[0]) + 6, BoxButton(item[0], on_press=views.activate,user_data=(item[1],item[2]))))
                menuGridList.append(app.W.BoxButton(item[0], on_press=app.views.activate,user_data=(item[1],item[2])))
            else:
                #menuList.append(
                    #w.getButton(item[0],views, 'activate', user_data=item[1]))
                    #(len(item[0]) + 6, BoxButton(item[0], on_press=views.activate,user_data=[item[1]])))
                menuGridList.append(BoxButton(item[0], on_press=app.views.activate,user_data=(item[1])))
        itemWidths = []
        for item in menuGridList:
            itemWidths.append(item.cursor_position)
        itemWidths.sort()
        if itemWidths:
            menuGrid = U.GridFlow(menuGridList,itemWidths[-1],0,0,'center')
        else:
            menuGrid = app.W.get_div()
        legendItems = []
        for legend in app.S.display['legend']:
            #legendItems.append(w.getText('bold', legend[0] + '\n' + legend[1], 'center'))
            legendItems.append(app.W.get_text('bold', legend[0], 'center'))
        legendGrid = U.GridFlow(legendItems,21,0,0,'center')
        legendGridMap = U.AttrMap(legendGrid,'bold')
        legendItems = []
        for legend in app.S.display['legend']:
            legendItems.append(app.W.get_text('highlight', legend[1], 'center'))
        legendItemsGrid = U.GridFlow(legendItems,21,0,0,'center')
        legendItemsMap = U.AttrMap(legendItemsGrid,'highlight')
        #legendColumns = urwid.Columns(
        #    legendItems,
        #    dividechars=1,
        #    focus_column=None,
        #    min_width=1, 
        #    box_columns=None)
        return U.Pile([menuGrid, legendGridMap, legendItemsMap])
    def get_col_row(self,items, dividechars=None, **kwargs):
        """Creates a single row of columns
        
        Arguments:
            items {list} -- List of widgets, each item forming one column.
                             Items may be tuples containing width specs
        
        Returns:
            [urwid.Column] -- An urwid.Columns object 
            FLOW / BOX WIDGET
        """
        if dividechars:
                return U.Columns(items,
                dividechars=dividechars,
                focus_column=None,
                min_width=1,
                box_columns=None)
        else:
            return U.Columns(items,
                dividechars=self.S.display['col_div_chars'],
                focus_column=None,
                min_width=1,
                box_columns=None)
    def get_line_box(self,
        contents,title,
        tlcorner='┌',
        tline='─',
        lline='│',
        trcorner='┐',
        blcorner='└',
        rline='│',
        bline='─',
        brcorner='┘',
        **kwargs):
        """ Creates a SimpleFocusListWalker using contents as the list,
            adds a centered title, and draws a box around it. If the contents
            are not a list of widgets, then set content_list to False.
            
            The character that is used to draw the border can 
            be adjusted with the following keyword arguments:
                tlcorner,tline,trcorner,blcorner,rline,bline,brcorner
        
        Arguments:
            contents {widget} -- an original_widget, no widget lists -
            title {string} -- Title String
        
        Keyword Arguments:
            content_list -- If true, the value of contents must be a list of widgets
                            If false, the value must be a single widget to be used as
                            original_widget -- default{False}
        
        Returns:
            urwid.LineBox -- urwid.LineBox object
            FLOW / BOX WIDGET
        """
        return U.LineBox(contents, 
            title=str(title),
            title_align='center',
            tlcorner=tlcorner,
            tline=tline,
            lline=lline,
            trcorner=trcorner,
            blcorner=blcorner,
            rline=rline,
            bline=bline,
            brcorner=brcorner)
    def get_list_box(self,contents):
        """Creates a ListBox using a SimpleFocusListWalker, with the contents
           being a list of widgets
        
        Arguments:
            contents {list} -- list of widgets
        
        Returns:
            list -- [0]: urwid.ListBox
                    [1]: urwid.SimpleFocusListWalker - Access this to make changes to the list
                               which the SimpleFocusListWalker will follow.   
        BOX WIDGET 
        """
        #debug('Started getListBox: %s', contents)
        walker = U.SimpleFocusListWalker(contents)
        listBox = U.ListBox(walker)
        return [listBox, walker]
    def centered_list_box(self,contents, title, listHeight, **kwargs):
        filler = U.Filler(contents, height=listHeight)
        insideCol = self.get_col_row([self.get_blank_box(),('weight',2,filler),self.get_blank_box()])
        #debug('centeredListLineBox filler.sizing(): %s', filler.sizing())
        lineBox = self.get_line_box(insideCol,title)
        #debug('centeredListLineBox listBox: %s', contents)
        outsidefiller = U.Filler(lineBox,height=listHeight)
        outsideCol = self.get_col_row([self.get_blank_box(),('weight',2,outsidefiller),self.get_blank_box()])
        return U.Filler(outsideCol, height=listHeight)