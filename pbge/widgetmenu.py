from . import widgets
from . import image
from . import my_state, Border
from . import rpgmenu

DEFAULT_UPDOWN_IMAGE_W_H = ("sys_updownbuttons.png", 128, 16)

widget_menu_border_off = Border(border_width=8, tex_width=16, border_name="sys_widbor_edge1.png",
                           tex_name="sys_defbackground.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2, padding=16)
widget_menu_border_on = Border(border_width=8, tex_width=16, border_name="sys_widbor_edge2.png",
                          tex_name="sys_defbackground.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2, padding=16)

class MenuItemWidget(widgets.LabelWidget):
    def __init__(self, dx, dy, w, h,
                 on_color=rpgmenu.MENU_SELECT_COLOR, off_color=rpgmenu.MENU_ITEM_COLOR, **kwargs):
        super().__init__(dx, dy, w, h, **kwargs)
        self.on_color = on_color
        self.off_color = off_color

    @property
    def color(self):
        if self._should_flash():
            return self.on_color
        else:
            return self.off_color

    @color.setter
    def color(self, nuval):
        self.off_color = nuval

    def _default_flash(self):
        # The default flash for this widget is "don't".
        pass


class MenuWidget(widgets.ColumnWidget):
    def __init__(self, dx, dy, w, h, draw_border=True, border=widget_menu_border_on,
                 off_border=widget_menu_border_off, activate_child_on_enter=False,
                 on_activate_item=None, center_interior=True, padding=5,
                 font=None, item_class=MenuItemWidget, item_data=None, **kwargs):
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
            on_activate_child=on_activate_item
        )
        super().add_interior(self.up_arrow)
        super().add_interior(self.scroll_column)
        super().add_interior(self.down_arrow)
        self.item_data = dict()
        if font:
            self.item_data["font"] = font
        if item_data:
            self.item_data.update(item_data)
        self.item_class = item_class

    def _enter_column(self, wid):
        my_state.active_widget = wid

    def activate(self):
        my_state.active_widget = self.scroll_column

    def _render(self, delta):
        if self.draw_border:
            if self._should_flash():
                self.border.render(self.get_rect())
            else:
                self.off_border.render(self.get_rect())

    def _should_flash(self):
        return (
            self.scroll_column is my_state.active_widget
            or self.up_arrow is my_state.active_widget
            or self.down_arrow is my_state.active_widget
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
        return self.scroll_column.active_widget

    @active_index.setter
    def active_index(self, nuval):
        self.scroll_column.scroll_to_index(nuval)
        self.scroll_column.active_widget = nuval

    def is_in_menu(self, other_widget):
        return self.scroll_column.is_interior_widget(other_widget)

    def items(self):
        return list(self.scroll_column._interior_widgets)

    def get_active_item(self):
        return self.scroll_column.get_active_item()

    # Utility function for adding default menu items.
    def add_item(self,msg,on_click,data=None):
        item = self.item_class( 0, 0, self.scroll_column.w, 0, text=str(msg), data=data, on_click=on_click, **self.item_data)
        self.add_interior( item )
        return item

