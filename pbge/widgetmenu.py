from . import widgets
from . import image
from . import my_state, Border, TEXT_COLOR
from . import frects
import pygame


DEFAULT_UPDOWN_IMAGE_W_H = ("sys_updownbuttons.png", 128, 16)

widget_menu_border_off = Border(border_width=8, tex_width=16, border_name="sys_widbor_edge1.png",
                           tex_name="sys_defbackground.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2, padding=16)
widget_menu_border_on = Border(border_width=8, tex_width=16, border_name="sys_widbor_edge2.png",
                          tex_name="sys_defbackground.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2, padding=16)

MENU_ITEM_COLOR = pygame.Color(150,145,130)
MENU_SELECT_COLOR = pygame.Color(128,250,230)


class MenuWidget(widgets.ColumnWidget):
    def __init__(
        self, dx, dy, w, h, draw_border=True, border=widget_menu_border_on,
        off_border=widget_menu_border_off, activate_child_on_enter=False,
        on_activate_item=None, center_interior=True, padding=5,
        item_color=MENU_ITEM_COLOR, selected_item_color=MENU_SELECT_COLOR,
        font=None, item_class=widgets.LabelWidget, item_data=None, 
        on_click_child=None,
        **kwargs
    ):
        # on_activate_item is a callable with signature (column, colitem). colitem may be None.
        #  Basically this is just passed to the interior ScrollColumn as its on_activate_child parameter.
        super().__init__(dx, dy, w, h, draw_border=draw_border, border=border, center_interior=center_interior,
                         **kwargs)
        self.off_border = off_border

        image_name, image_w, image_h = DEFAULT_UPDOWN_IMAGE_W_H
        updown = image.Image(image_name, image_w, image_h)
        self.up_arrow = widgets.ButtonWidget(
            0, 0, image_w, image_h, sprite = updown, on_frame = 0, off_frame = 1
        )
        self.down_arrow = widgets.ButtonWidget(
            0, 0, image_w, image_h, sprite = updown, on_frame = 2, off_frame = 3
        )
        self.scroll_column = widgets.ScrollColumnWidget(
            0, 0, w, h - 32, self.up_arrow, self.down_arrow, padding = padding,
            on_enter=self._enter_column, activate_child_on_enter=activate_child_on_enter,
            on_activate_child=on_activate_item, on_click_child=on_click_child
        )
        super().add_interior(self.up_arrow)
        super().add_interior(self.scroll_column)
        super().add_interior(self.down_arrow)
        self.item_data = dict()
        if font:
            self.item_data["font"] = font
        self.item_data["color"] = item_color
        self.item_data["focus_color"] = selected_item_color
        if item_data:
            self.item_data.update(item_data)
        self.item_class = item_class

    def _enter_column(self, wid):
        my_state.focused_widget = wid

    def activate(self):
        my_state.focused_widget = self.scroll_column

    def _render(self, delta):
        if self.draw_border:
            if self._should_flash():
                self.border.render(self.get_rect())
            else:
                self.off_border.render(self.get_rect())

    def _should_flash(self):
        return (
            self.scroll_column is my_state.focused_widget
            or self.up_arrow is my_state.focused_widget
            or self.down_arrow is my_state.focused_widget
        )

    # Some utility functions to access the scroll column's contents directly.
    def add_interior(self, other_w, pos=None):
        self.scroll_column.add_interior(other_w, pos)

    def clear(self):
        self.scroll_column.clear()

    def remove(self, other_widget):
        self.scroll_column.remove(other_widget)

    def sort(self, key=None):
        self.scroll_column.sort(key)

    @property
    def active_index(self):
        return self.scroll_column.selected_widget_id

    @property
    def active_item(self):
        return self.scroll_column.get_active_item()

    @property
    def current_data(self):
        my_item = self.scroll_column.get_active_item()
        if my_item:
            return my_item.data

    @active_index.setter
    def active_index(self, nuval):
        self.scroll_column.scroll_to_index(nuval)
        self.scroll_column.selected_widget_id = nuval

    def is_in_menu(self, other_widget):
        return self.scroll_column.is_interior_widget(other_widget)

    def get_items(self):
        return self.scroll_column.get_items()

    def get_active_item(self):
        return self.scroll_column.get_active_item()

    # Utility function for adding default menu items.
    def add_item(self,msg,on_click: widgets.On_Click=None,data=None, desc=None):
        item = self.item_class( 0, 0, self.scroll_column.w, 0, text=str(msg), data=data, on_click=on_click, desc=desc, **self.item_data)
        self.add_interior( item )
        return item

    def set_item_by_position( self , n ):
        self.scroll_column.selected_widget_id = n

    def has_data( self , dat ):
        for i in self.get_items():
            if i.data == dat:
                return True

    def set_item_by_data( self , dat ):
        for n,i in enumerate( self.get_items() ):
            if i.data == dat:
                self.scroll_column.selected_widget_id = n
                break


class DropdownWidget(widgets.Widget):
    MENU_HEIGHT = 150

    def __init__(self, dx, dy, w, h, color=None, font=None, justify=-1, on_select=None, add_desc=False, can_take_focus=True, **kwargs):
        # on_select is a callable that takes the menu query item's data property as its argument
        self.font = font or my_state.small_font
        if h == 0:
            h = self.font.get_linesize() + 16
        super().__init__(dx, dy, w, h, can_take_focus=can_take_focus, **kwargs)
        self.color = color or TEXT_COLOR
        self.on_select = on_select
        self.on_click = self.open_menu
        self.menu = MenuWidget(
            dx, dy, w, self.MENU_HEIGHT, border=widgets.popup_menu_border, font=font,
            anchor=frects.ANCHOR_UPPERLEFT, on_click_child=self._click_item, activate_child_on_enter=True,
        )
        self.menu.TAGS_TO_DEACTIVATE = {widgets.WTAG_WIDGET,}
        
        if add_desc:
            pass
            #self.menu.add_descbox(dx-w-16, dy, w, self.MENU_HEIGHT)
            #self.menu.descobj.anchor = frects.ANCHOR_UPPERLEFT
            #self.menu.descobj.parent = self.menu

    def _render(self, delta):
        mydest = self.get_rect()
        if self is my_state.focused_widget:
            widgets.widget_border_on.render(mydest.inflate(-4, -4))
        else:
            widgets.widget_border_off.render(mydest.inflate(-4, -4))
        myimage = self.font.render(str(self.menu.active_item), True, self.color)
        my_state.screen.set_clip(mydest)
        textdest = myimage.get_rect(center=mydest.center)
        _=my_state.screen.blit(myimage, textdest)
        my_state.screen.set_clip(None)

    def add_item(self,msg,on_click: widgets.On_Click=None,data=None, desc=None):
        _=self.menu.add_item(msg, on_click, data, desc)

    def _click_item(self, item: widgets.Widget, _ev):
        self.menu.pop()
        if self.on_select:
            self.on_select(item.data)

    def open_menu(self, _also_self_probably, _ev):
        mydest = self.get_rect()
        mydest.h = self.menu.h
        mydest.w = self.menu.w
        my_screen_rect = my_state.screen.get_rect()
        mydest.clamp_ip(my_screen_rect)
        self.menu.dx, self.menu.dy = mydest.x, mydest.y
        self.menu.push_and_deploy()
        self.menu.activate()

    @property
    def current_data(self):
        return self.menu.current_data

    def clear(self):
        self.menu.clear()

    def set_item_by_data( self , dat ):
        self.menu.set_item_by_data(dat)


class ColDropdownWidget(widgets.RowWidget):
    def __init__(self, width, prompt="Choose Option", font=None, justify=-1, on_select=None, add_desc=False, **kwargs):
        mylabel = widgets.LabelWidget(0, 0, width * 2 // 5 - 10, 0, prompt, font=font)
        super().__init__(0, 0, width, mylabel.h + 8, **kwargs)
        self.add_left(mylabel)
        self.menu_widget = DropdownWidget(0, 0, width * 3 // 5, mylabel.h + 8, font=font, justify=justify,
                                             on_select=on_select, add_desc=add_desc)
        self.add_right(self.menu_widget)
        self.on_click = self.menu_widget.open_menu

    @property
    def current_data(self):
        return self.menu_widget.current_data

    def add_item(self,msg,on_click: widgets.On_Click=None,data=None, desc=None):
        self.menu_widget.add_item(msg, on_click, data, desc)

    def set_item_by_data( self , dat ):
        self.menu_widget.set_item_by_data(dat)
