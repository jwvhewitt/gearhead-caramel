from . import widgets
from . import image
from . import my_state, INFO_HILIGHT, INFO_GREEN
from . import rpgmenu

DEFAULT_UPDOWN_IMAGE_W_H = ("sys_updownbuttons.png", 128, 16)


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


class MenuWidget(widgets.ColumnWidget):
    def __init__(self, dx, dy, w, h, draw_border=True, border=widgets.widget_border_on,
                 off_border=widgets.widget_border_off, activate_child_on_enter=False, **kwargs):
        super().__init__(dx, dy, w, h, draw_border=draw_border, border=border, **kwargs)
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
            0, 0, w, h - 32, self.up_arrow, self.down_arrow, padding = 0,
            on_enter=self._enter_column, activate_child_on_enter=activate_child_on_enter,
        )
        self.add_interior(self.up_arrow)
        self.add_interior(self.scroll_column)
        self.add_interior(self.down_arrow)

    def _enter_column(self, wid):
        my_state.active_widget = wid

    def render(self, flash=False):
        if self.draw_border:
            if flash:
                self.border.render(self.get_rect())
            else:
                self.off_border.render(self.get_rect())

    def _should_flash(self):
        return (
            (self.scroll_column is my_state.active_widget
             or self.up_arrow is my_state.active_widget
             or self.down_arrow is my_state.active_widget)
            and my_state.active_widget_hilight
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

