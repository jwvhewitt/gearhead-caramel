from . import widgets
from . import image
from . import my_state, Border, TEXT_COLOR, default_border, draw_text, WHITE
from . import frects
import pygame
from collections.abc import Callable


widget_menu_border_off = Border(border_width=8, tex_width=16, border_name="sys_widbor_edge1.png",
                           tex_name="sys_defbackground.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2, padding=16)
widget_menu_border_on = Border(border_width=8, tex_width=16, border_name="sys_widbor_edge2.png",
                          tex_name="sys_defbackground.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2, padding=16)

MENU_ITEM_COLOR = pygame.Color(150,145,130)
MENU_SELECT_COLOR = pygame.Color(128,250,230)


class MenuStyle:
    def __init__(
        self, arrow_image_name="sys_updownbuttons.png", arrow_image_w=128, arrow_image_h=16,
        up_arrow_on_frame=0, up_arrow_off_frame=1, down_arrow_on_frame=2, down_arrow_off_frame=3,
        corner_arrows=False
    ):
        self.arrow_image_name = arrow_image_name
        self.arrow_image_w = arrow_image_w
        self.arrow_image_h = arrow_image_h
        self.up_arrow_on_frame = up_arrow_on_frame
        self.up_arrow_off_frame = up_arrow_off_frame
        self.down_arrow_on_frame = down_arrow_on_frame
        self.down_arrow_off_frame = down_arrow_off_frame
        self.corner_arrows = corner_arrows

    def get_up_down_widgets(self):
        updown = image.Image(self.arrow_image_name, self.arrow_image_w, self.arrow_image_h)
        up_arrow = widgets.ButtonWidget(
            0, 0, self.arrow_image_w, self.arrow_image_h, sprite = updown, 
            on_frame = self.up_arrow_on_frame, off_frame = self.up_arrow_off_frame
        )
        down_arrow = widgets.ButtonWidget(
            0, 0, self.arrow_image_w, self.arrow_image_h, sprite = updown, 
            on_frame = self.down_arrow_on_frame, off_frame = self.down_arrow_off_frame
        )
        return (up_arrow, down_arrow)

    def arrange_widgets(self, menu: "MenuWidget", scroll_column, up_arrow, down_arrow):
        if self.corner_arrows:
            menu.children.append(up_arrow)
            menu.super_add_interior(scroll_column)
            menu.children.append(down_arrow)
            up_arrow.parent = menu
            up_arrow.dx, up_arrow.dy = -up_arrow.w//2, -up_arrow.h//2
            up_arrow.anchor = frects.ANCHOR_UPPERRIGHT
            down_arrow.parent = menu
            down_arrow.dx, down_arrow.dy = -down_arrow.w//2, -down_arrow.h//2
            down_arrow.anchor = frects.ANCHOR_LOWERRIGHT

        else:
            menu.super_add_interior(up_arrow)
            scroll_column.h = scroll_column.h - up_arrow.h * 2
            menu.super_add_interior(scroll_column)
            menu.super_add_interior(down_arrow)


DEFAULT_STYLE = MenuStyle(
    "sys_updownboxes.png", 24, 24, 0, 1, 3, 4, True
)
WIDE_ARROW_STYLE = MenuStyle()


class MenuWidget(widgets.ColumnWidget):
    def __init__(
        self, dx, dy, w, h, draw_border=True, border=widget_menu_border_on,
        off_border=widget_menu_border_off, activate_child_on_enter=True,
        on_activate_item=None, center_interior=True, padding=5,
        item_color=MENU_ITEM_COLOR, selected_item_color=MENU_SELECT_COLOR,
        font=None, item_class: type[widgets.Widget]=widgets.LabelWidget, item_data=None, 
        on_click_child: widgets.On_Click=None, pop_when_clicked=False,
        on_escape: Callable[[widgets.Widget, pygame.event.Event], None]|None=None,
        auto_escape=False, style=DEFAULT_STYLE,
        **kwargs
    ):
        # on_activate_item is a callable with signature (column, colitem). colitem may be None.
        #  Basically this is just passed to the interior ScrollColumn as its on_activate_child parameter.
        # on_click_child: callable with signature (child_widget, event)
        # pop_when_clicked can ***ONLY BE SET FOR A TOP LEVEL WIDGET!!!***; when a menu item is clicked,
        #  if truthy, the menu will pop before calling the child effects
        # on_escape: callable with signature (widget, event) called when escape key pressed
        #   Does not actually close menu; exact workings are up to whoever created this menu.
        # auto_escape allows this menu to pop without an on_escape function; can ***ONLY BE SET FOR A TOP LEVEL WIDGET!!!***
        super().__init__(dx, dy, w, h, draw_border=draw_border, border=border, center_interior=center_interior,
                         **kwargs)
        self.off_border = off_border

        self.up_arrow, self.down_arrow = style.get_up_down_widgets()

        self.scroll_column = widgets.ScrollColumnWidget(
            0, 0, w, h, self.up_arrow, self.down_arrow, padding = padding,
            on_enter=self._enter_column, activate_child_on_enter=activate_child_on_enter,
            on_activate_child=on_activate_item, on_click_child=self._click_child_wrapper,
            immediately_on_click=self._immediately_on_click
        )

        style.arrange_widgets(self, self.scroll_column, self.up_arrow, self.down_arrow)

        self.item_data = dict()
        if font:
            self.item_data["font"] = font
        self.item_data["color"] = item_color
        self.item_data["focus_color"] = selected_item_color
        if item_data:
            self.item_data.update(item_data)
        self.item_class = item_class
        self.on_escape = on_escape
        if auto_escape and not on_escape:
            self.on_escape = self.auto_escape_fun

        self._on_click_child = on_click_child
        self.pop_when_clicked = pop_when_clicked
        self.quick_keys = dict()

    def auto_escape_fun(self, _wid, _ev):
        self.pop()

    def _immediately_on_click(self, _wid, _ev):
        if self.pop_when_clicked:
            self.pop()

    def _click_child_wrapper(self, item_wid, ev):
        if self._on_click_child:
            self._on_click_child(item_wid, ev)

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

    # Utility function to access the menu's column contents
    def super_add_interior(self, other_w):
        super().add_interior(other_w)

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

    @property
    def current_desc(self):
        return self.active_item.desc

    @active_index.setter
    def active_index(self, nuval):
        self.scroll_column.scroll_to_index(nuval)
        self.scroll_column.selected_widget_id = nuval

    def is_in_menu(self, other_widget):
        return self.scroll_column.is_interior_widget(other_widget)

    def get_items(self):
        return self.scroll_column.get_items()

    def is_empty(self):
        return not self.scroll_column.get_items()

    # Utility function for adding default menu items.
    def add_item(self,msg,on_click: widgets.On_Click=None,data=None, desc=None):
        item = self.item_class( 0, 0, self.scroll_column.w, 0, text=str(msg), data=data, on_click=on_click, desc=desc, **self.item_data)
        self.add_interior( item )
        return item

    def add_custom(self, new_item: widgets.Widget):
        if isinstance(new_item, widgets.LabelWidget):
            new_item.w = self.scroll_column.w
            new_item.h = 0
            new_item.confirm_dimensions()
        self.add_interior(new_item)
        return new_item

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

    def _builtin_responder(self, ev):
        if ((my_state.focused_widget is self.scroll_column) or self.scroll_column.focus_locked) and (ev.type == pygame.KEYDOWN):
            if my_state.is_key_for_action(ev, "exit") and self.on_escape:
                self.register_response()
                self.on_escape(self, ev)
                #print(self, ev, id(ev))
            elif ev.unicode in self.quick_keys:
                self.quick_keys[ev.unicode].manual_click(ev)

    ALPHA_KEY_SEQUENCE = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    def add_alpha_keys(self):
        # Adds a quick key for every item currently in the menu.
        key_num = 0
        for item in self.get_items():
            if hasattr(item, "text"):
                item.text = self.ALPHA_KEY_SEQUENCE[ key_num ] + ') ' + item.text
                self.quick_keys[ self.ALPHA_KEY_SEQUENCE[ key_num ] ] = item
            key_num += 1
            if key_num >= len( self.ALPHA_KEY_SEQUENCE ):
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
            on_escape=self.close_menu
        )
        self.menu.TAGS_TO_DEACTIVATE = {widgets.WTAG_WIDGET,}
        
        if add_desc:
            self.menu.children.append(
                DescBoxWidget(
                    -w-24, 8, w, self.MENU_HEIGHT, menu=self.menu,
                    anchor=frects.ANCHOR_UPPERLEFT, parent=self.menu
                )
            )

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
        return self.menu.add_item(msg, on_click, data, desc)

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

    def close_menu(self, _also_self_probably, _ev):
        if self.menu in my_state.widgets:
            self.menu.pop()

    @property
    def active_item(self):
        return self.menu.active_item

    @property
    def current_data(self):
        return self.menu.current_data

    def clear(self):
        self.menu.clear()

    def set_item_by_data( self , dat ):
        self.menu.set_item_by_data(dat)

    def has_data( self , dat ):
        return self.menu.has_data(dat)

    def sort(self, key=None):
        self.menu.sort(key)


class PopupMenuWidget(MenuWidget):
    # By default, popup menus take precedence over any other widget.
    TAGS_TO_DEACTIVATE = {widgets.WTAG_WIDGET,}
    ACTIVATE_IMMEDIATELY = True

    def __init__(
        self, w=200, h=250, pop_when_clicked=True, 
        topleft: tuple[int,int]|None=None,
        **kwargs
    ):
        if topleft:
            x,y = topleft
        else:
            x,y = my_state.mouse_pos
        x += 8
        y += 8
        sw,sh = my_state.screen.get_size()
        if x + w + 32 > sw:
            x += -w - 32
        if y + h + 32 > sh:
            y += -h - 32

        super().__init__(
            x,y,w,h, anchor=frects.ANCHOR_UPPERLEFT,
            pop_when_clicked=pop_when_clicked, **kwargs
        )


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

    @property
    def active_item(self):
        return self.menu_widget.active_item

    def add_item(self,msg,on_click: widgets.On_Click=None,data=None, desc=None):
        return self.menu_widget.add_item(msg, on_click, data, desc)

    def set_item_by_data( self , dat ):
        self.menu_widget.set_item_by_data(dat)

    def sort(self, key=None):
        self.menu_widget.sort(key)


class DescBoxWidget(widgets.LabelWidget):
    def __init__(self, dx,dy,w=300,h=100,anchor=frects.ANCHOR_CENTER, menu=None, draw_border=True, **kwargs):
        self.menu = menu
        super().__init__(dx, dy, w, h, anchor=anchor, draw_border=draw_border, text_fun=self._desc_text_fun, border=default_border, **kwargs)

    def _desc_text_fun(self, _widg):
        my_item = self.menu.active_item
        if my_item and my_item.desc:
            return str(my_item.desc)
        else:
            return ""


class AlertMenuWidget(MenuWidget):
    WIDTH = 350
    HEIGHT = 250
    MENU_HEIGHT = 75

    FULL_RECT = frects.Frect(-WIDTH//2,-HEIGHT//2,WIDTH,HEIGHT)
    TEXT_RECT = frects.Frect(-WIDTH//2,-HEIGHT//2,WIDTH,HEIGHT - MENU_HEIGHT - 10)
    MENU_RECT = frects.Frect(-WIDTH//2, HEIGHT//2-MENU_HEIGHT, WIDTH, MENU_HEIGHT)

    ACTIVATE_IMMEDIATELY = True

    def __init__(self, msg, alert_font=None, pop_when_clicked=True, **kwargs):
        if "draw_border" in kwargs:
            kwargs.pop("draw_border")
        super().__init__(
            **self.MENU_RECT.get_dict(),
            draw_border=False, pop_when_clicked=pop_when_clicked, **kwargs
        )
        self.alert_font = alert_font or my_state.medium_font
        self.msg = msg

    def _render(self, delta):
        default_border.render(self.FULL_RECT.get_rect())
        draw_text(self.alert_font, self.msg, self.TEXT_RECT.get_rect(), justify=0)
        super()._render(delta)


class TitleMenuWidget(MenuWidget):
    WIDTH = 350
    HEIGHT = 250
    TITLE_HEIGHT = 30
    PADDING = 24

    MENU_RECT = frects.Frect(-WIDTH // 2, -HEIGHT // 2 + TITLE_HEIGHT + PADDING, WIDTH, HEIGHT - TITLE_HEIGHT - PADDING)
    TITLE_RECT = frects.Frect(-WIDTH // 2, -HEIGHT // 2, WIDTH, TITLE_HEIGHT)

    def __init__(self, title, title_font=None, **kwargs):
        if "draw_border" in kwargs:
            kwargs.pop("draw_border")
        super().__init__(
            **self.MENU_RECT.get_dict(),
            draw_border=False, **kwargs
        )
        self.title = title
        self.title_font = title_font or my_state.big_font

    def _render(self, delta):
        default_border.render(self.MENU_RECT.get_rect())
        default_border.render(self.TITLE_RECT.get_rect())
        draw_text(
            self.title_font, self.title, self.TITLE_RECT.get_rect(), justify=0, vjustify=0,
            color=WHITE
        )
        super()._render(delta)


 