import pbge
from . import WHITE, frects
from . import my_state, draw_text, TEXT_COLOR, Border, default_border, wrap_multi_line, wrapline
import pygame
from . import image
import weakref
from collections.abc import Callable


# respond_event: Receives an event.
#   If the widget has a method corresponding to the event,
#   that method will be called.

# Note that the widget needs to be added to my_state.widgets to be used!
# Or, as the child of another widget. Removing it from that list
# removes it.

ACTIVE_FLASH = [(0, 0, 0), ] * 5 + [(230, 230, 0), ] * 20

widget_border_off = Border(border_width=8, tex_width=16, border_name="sys_widbor_edge1.png",
                           tex_name="sys_widbor_back2.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2, padding=2)
widget_border_on = Border(border_width=8, tex_width=16, border_name="sys_widbor_edge2.png",
                          tex_name="sys_widbor_back.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2, padding=2)
popup_menu_border = Border(border_width=8, tex_width=16, border_name="sys_widbor_edge2.png",
                           tex_name="sys_defbackground.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2, padding=8,
                           transparent=False)


WTAG_WIDGET = "WTAG_WIDGET"


class FrozenUIState:
    # Widgets may have "on_activate" and "on_freeze" methods that get called when the widget is either popped or
    # pushed.
    def __init__(self, *widgets_to_push, tags_to_deactivate=(), tags_to_hide=()):
        self.pushed_widgets = list()
        for wtp in widgets_to_push:
            self.push_widget(wtp)

        self.deactivated_widgets = list()
        self.hidden_widgets = list()
        tags_to_deactivate = set(tags_to_deactivate)
        tags_to_hide = set(tags_to_hide)

        for widg in my_state.all_widgets():
            if widg.active and widg.tags.intersection(tags_to_deactivate):
                self.deactivated_widgets.append(widg)
                widg.active = False
            if widg.visible and widg.tags.intersection(tags_to_hide):
                self.hidden_widgets.append(widg)
                widg.visible = False

        try:
            self.focused_widget_wr = weakref.ref(my_state.focused_widget)
        except TypeError:
            self.focused_widget_wr = None

        my_state.ui_stack.append(self)

    def push_widget(self, widget_to_push):
        if widget_to_push in my_state.widgets and widget_to_push not in self.pushed_widgets:
            self.pushed_widgets.append(widget_to_push)
            my_state.widgets.remove(widget_to_push)
            if hasattr(widget_to_push, "on_freeze"):
                widget_to_push.on_freeze()

    def unfreeze(self):
        for widg in self.pushed_widgets:
            my_state.widgets.append(widg)
            if hasattr(widg, "on_activate"):
                widg.on_activate()

        for widg in self.deactivated_widgets:
            widg.active = True
            if hasattr(widg, "on_activate"):
                widg.on_activate()

        for widg in self.hidden_widgets:
            widg.visible = True
            if hasattr(widg, "on_activate"):
                widg.on_activate()

        if self.focused_widget_wr:
            reactivate_this = self.focused_widget_wr()
            if reactivate_this in list(my_state.all_widgets()):
                my_state.focused_widget = reactivate_this

type On_Click = Callable[[Widget, pygame.event.Event], None]|None


class Widget(frects.Frect):
    def __init__(self, dx, dy, w, h, data=None, on_click: On_Click=None, tooltip=None, children=(), active=True,
                 on_right_click=None, anchor=frects.ANCHOR_CENTER, parent=None, can_take_focus=False,
                 on_enter=None, on_leave=None, visible=True, tags=(), should_hilight=None, desc=None,
                 **kwargs):
        # on_click is a callable with signature (widget, event)
        # on_right_click is a callable with signature (widget, event)
        # on_enter is a callable with signature (widget)
        # on_leave is a callable with signature (widget)
        # should_hilight is a callable with signature (widget)
        #   NOTE: The highlit widget will act like it's the boss! It'll capture input and stuff!
        # desc is a test description of this widget which may be useful for debugging, but otherwise
        #   is only sometimes used by the menu widgets. Note that this comment might stop being true
        #   if/when desc gets used in more places.
        super().__init__(dx, dy, w, h, anchor, parent)
        self.data = data
        self.active = active
        self.visible = visible
        self.tooltip = tooltip
        self.on_click = on_click
        self.on_right_click = on_right_click
        self.children = list(children)
        self.on_enter = on_enter
        self.on_leave = on_leave
        self._mouse_is_over = False
        self.tags = set(tags)
        self.tags.add(WTAG_WIDGET)
        self.can_take_focus = can_take_focus
        self.should_hilight = should_hilight or self._default_should_hilight
        self.desc = desc

    @staticmethod
    def _default_should_hilight(widg):
        return widg is my_state.focused_widget

    def get_all_widgets(self):
        yield self
        for part in self.children:
            for p in part.get_all_widgets():
                yield p

    def get_all_active_widgets(self):
        if self.active and self.visible:
            yield self
            for part in self.children:
                for p in part.get_all_active_widgets():
                    yield p

    def respond_event(self, ev):
        if self.active and self.visible:
            for c in self.children:
                c.respond_event(ev)
            if self.get_rect().collidepoint(my_state.mouse_pos):
                if self.active and (ev.type == pygame.MOUSEBUTTONUP) and (
                        ev.button == 1) and not my_state.widget_responded:
                    if not my_state.widget_responded:
                        my_state.focused_widget = self
                    if self.on_click:
                        self.on_click(self, ev)
                    my_state.widget_responded = True
                elif self.active and (ev.type == pygame.MOUSEBUTTONUP) and (
                        ev.button == 3) and self.on_right_click and not my_state.widget_responded:
                    if not my_state.widget_responded:
                        my_state.focused_widget = self
                    self.on_right_click(self, ev)
                    my_state.widget_responded = True
                if not self._mouse_is_over:
                    self._mouse_is_over = True
                    if self.on_enter:
                        self.on_enter(self)
            else:
                if self._mouse_is_over:
                    self._mouse_is_over = False
                    if self.on_leave:
                        self.on_leave(self)
            if self.should_hilight(self) and not my_state.widget_responded and not my_state.widget_responded:
                if self.on_click and (ev.type == pygame.KEYDOWN) and my_state.is_key_for_action(ev, "click_widget"):
                    self.on_click(self, ev)
                    my_state.widget_responded = True
            if not my_state.widget_responded:
                self._builtin_responder(ev)
        else:
            self._mouse_is_over = False

    def register_response(self):
        # Call this method when _builtin_responder has responded to an event and you don't want other widgets to
        # respond to the same event.
        my_state.widget_responded = True

    def _builtin_responder(self, _ev):
        pass

    def update(self, delta):
        # This renders the widget and children, setting tooltip and whatnot.
        if self.visible:
            self._render(delta)
            if self.tooltip and self.get_rect().collidepoint(my_state.mouse_pos):
                my_state.widget_tooltip = self.tooltip
            for c in self.children:
                c.update(delta)

    def _should_flash(self):
        if self.parent and hasattr(self.parent, "kb_flash_override"):
            return self.parent.kb_flash_override(self)
        elif hasattr(self, "kbhandler") and self.kbhandler and hasattr(self.kbhandler, "kb_flash_override"):
            return self.kbhandler.kb_flash_override(self)
        else:
            return self is my_state.focused_widget

    def _default_flash(self):
        _=pygame.draw.rect(my_state.screen, ACTIVE_FLASH[my_state.anim_phase % len(ACTIVE_FLASH)], self.get_rect(), 1)

    def _render(self, _delta):
        pass

    def close(self):
        if self in my_state.widgets:
            my_state.widgets.remove(self)

    def pop(self):
        #print("Popping {}".format(self))
        self.close()
        if my_state.ui_stack:
            froz = my_state.ui_stack.pop(-1)
            froz.unfreeze()

    TAGS_TO_DEACTIVATE = set()
    TAGS_TO_HIDE = ()

    @classmethod
    def push_state_and_instantiate(cls, *widgets_to_push, **kwargs):
        _=FrozenUIState(*widgets_to_push, tags_to_deactivate=cls.TAGS_TO_DEACTIVATE, tags_to_hide=cls.TAGS_TO_HIDE)
        my_widget = cls(**kwargs)
        my_state.widgets.append(my_widget)

    def push_and_deploy(self, *widgets_to_push):
        _=FrozenUIState(*widgets_to_push, tags_to_deactivate=self.TAGS_TO_DEACTIVATE, tags_to_hide=self.TAGS_TO_HIDE)
        my_state.widgets.append(self)


class ButtonWidget(Widget):
    def __init__(self, dx, dy, w, h, sprite=None, frame=0, on_frame=0, off_frame=0, **kwargs):
        super(ButtonWidget, self).__init__(dx, dy, w, h, **kwargs)
        self.sprite = sprite
        self.frame = frame
        self.on_frame = on_frame
        self.off_frame = off_frame

    def _render(self, delta):
        if self.sprite:
            self.sprite.render(self.get_rect(), self.frame)
        if self._should_flash():
            self._default_flash()


class SurfaceWidget(Widget):
    # Like a button, but just contains a raw PyGame Surface instead of a pbge Image.
    def __init__(self, dx, dy, surf: pygame.Surface, **kwargs):
        super().__init__(dx, dy, surf.get_width(), surf.get_height(), **kwargs)
        self.surf = surf

    def _render(self, delta):
        if self.surf:
            _=my_state.screen.blit(self.surf, self.get_rect())
        if self._should_flash():
            self._default_flash()



class LabelWidget(Widget):
    def __init__(self, dx, dy, w=0, h=0, text='***', color=None, font=None, justify=-1, draw_border=False,
                 border=widget_border_off, text_fun=None, alt_smaller_fonts=(), focus_color=None,
                 focus_border=widget_border_on, **kwargs):
        # text_fun is a callable with signature (widget). It returns the text to display.
        super().__init__(dx, dy, w, h, **kwargs)
        self._text = text
        self.text = text
        self.color = color or TEXT_COLOR
        self.focus_color = focus_color or WHITE
        self.font = font or my_state.small_font
        self.draw_border = draw_border
        self.text_fun = text_fun
        if w == 0:
            self.w = self.font.size(self.text)[0]
            if self.draw_border:
                self.w += 16
                self.dx -= 8
        if h == 0:
            self.h = len(wrap_multi_line(text, self.font, self.w)) * self.font.get_linesize()
            # if self.draw_border:
            #    self.h += 16
            #    self.dy -= 8
        self.justify = justify
        self.border = border
        self.focus_border = focus_border
        self.alt_smaller_fonts = alt_smaller_fonts

    def _render(self, delta):
        if self.should_hilight(self):
            if self.draw_border and self.focus_border:
                self.focus_border.render(self.get_rect())
            color = self.focus_color
        else:
            if self.draw_border and self.border:
                self.border.render(self.get_rect())
            color = self.color

        if self.alt_smaller_fonts and len(wrap_multi_line(self.text, self.font, self.w)) * self.font.get_linesize() > self.h:
            myfont = self.alt_smaller_fonts[-1]
            for f in self.alt_smaller_fonts[:-1]:
                if len(wrap_multi_line(self.text, f, self.w)) * f.get_linesize() <= self.h:
                    myfont = f
                    break
        else:
            myfont = self.font
        draw_text(myfont, self.text, self.get_rect(), color, self.justify)

    @property
    def text(self):
        if self.text_fun:
            return self.text_fun(self)
        else:
            return self._text

    @text.setter
    def text(self, nutext):
        self._text = nutext

    def __str__(self):
        return self.text


class RadioButtonWidget(Widget):
    def __init__(self, dx, dy, w, h, sprite=None, buttons=(), spacing=2, **kwargs):
        # buttons is a list of dicts possibly containing: on_frame, off_frame, on_click, on_right_click, tooltip
        super().__init__(dx, dy, w, h, **kwargs)
        self.sprite = sprite
        self.buttons = list()
        self.spacing = spacing
        ddx = 0
        for b in buttons:
            self.buttons.append(ButtonWidget(
                ddx, 0, sprite.frame_width, sprite.frame_height, sprite,
                frame=b.get("off_frame", 1), on_frame=b.get("on_frame", 0),
                off_frame=b.get("off_frame", 1), tooltip=b.get("tooltip", None),
                on_click=self.click_radio, data=b.get("on_click", None),
                on_right_click=b.get("on_right_click", None),
                parent=self, anchor=frects.ANCHOR_UPPERLEFT
            ))
            ddx += sprite.frame_width + self.spacing
        self.buttons[0].frame = self.buttons[0].on_frame
        self.active_button = self.buttons[0]
        self.children += self.buttons

    def activate_button(self, button):
        self.active_button.frame = self.active_button.off_frame
        self.active_button = button
        button.frame = button.on_frame

    def get_button(self, data_sought):
        for b in self.buttons:
            if b.data == data_sought:
                return b

    def click_radio(self, button, ev):
        self.activate_button(button)
        if button.data:
            button.data(button, ev)


class TextTabsWidget(Widget):
    def __init__(self, dx, dy, w, h, buttons=(), spacing=12, font=None, **kwargs):
        # Basically radio buttons, but with text labels.
        # buttons is a list of dicts possibly containing: text, on_right_click, tooltip
        self.font = font or pbge.MEDIUMFONT
        super().__init__(dx, dy, w, max(h, self.font.get_linesize() + 8), **kwargs)
        self.buttons = list()
        self.spacing = spacing
        ddx = 0
        for b in buttons:
            mylabel = LabelWidget(
                ddx, 0, text=b.get("text", "Tab"),
                tooltip=b.get("tooltip", None),
                on_click=self.click_radio, data=b.get("on_click", None), draw_border=True,
                on_right_click=b.get("on_right_click", None), font=self.font, color=pbge.GREY,
                parent=self, anchor=frects.ANCHOR_UPPERLEFT, border=widget_border_off
            )
            self.buttons.append(mylabel)
            ddx += mylabel.w + self.spacing
        if self.buttons:
            self.active_button = self.buttons[0]
            self.activate_button(self.buttons[0])
        self.children += self.buttons

    def activate_button(self, button):
        self.active_button.border = widget_border_off
        self.active_button = button
        button.border = widget_border_on

    def get_button(self, data_sought):
        for b in self.buttons:
            if b.data == data_sought:
                return b

    def click_radio(self, button, ev):
        self.activate_button(button)
        if button.data:
            button.data(button, ev)


class ColumnWidget(Widget):
    def __init__(self, dx, dy, w, h, draw_border=False, border=default_border, padding=5, center_interior=False,
                 optimize_height=True, **kwargs):
        super().__init__(dx, dy, w, h, **kwargs)
        self.draw_border = draw_border
        self.border = border
        self._interior_widgets = list()
        self._header_widget = None
        self.padding = padding
        self.center_interior = center_interior
        self.optimize_height = optimize_height

    def add_interior(self, other_w):
        self.children.append(other_w)
        self._interior_widgets.append(other_w)
        # Set the position of other_w inside this widget.
        other_w.parent = self
        self._position_contents()

    def set_header(self, other_w):
        self.children.append(other_w)
        self._header_widget = other_w
        # Set the position of other_w inside this widget.
        other_w.parent = self
        self._position_contents()

    def clear(self):
        del self._interior_widgets[:]
        del self.children[:]
        self._header_widget = None

    def _position_contents(self):
        dy = 0
        if self._header_widget:
            self._header_widget.dx = -(self._header_widget.w // 2)
            self._header_widget.dy = -(self._header_widget.h // 2)
            self._header_widget.anchor = frects.ANCHOR_TOP
            dy += self._header_widget.h // 2 + self.padding
        for widg in self._interior_widgets:
            if self.center_interior:
                widg.dx = (self.w - widg.w) // 2
            else:
                widg.dx = 0
            widg.dy = dy
            widg.anchor = frects.ANCHOR_UPPERLEFT
            dy += widg.h + self.padding
        if self.optimize_height:
            self.h = dy

    def _render(self, delta):
        if self.draw_border:
            self.border.render(self.get_rect())
        if self._should_flash():
            self._default_flash()


class ScrollColumnWidget(Widget):
    def __init__(self, dx, dy, w, h, up_button, down_button, draw_border=False, border=default_border, padding=5,
                 autoclick=False, focus_locked=False, activate_child_on_enter=False, on_activate_child=None, 
                 can_take_focus=True, on_click_child=None, focus_border=widget_border_on, **kwargs):
        # if activate_child_on_enter is True, the contents of this widget will activate on mouseover.
        # on_activate_child is a callable with signature (column_widget, child_widget) that gets called when the
        #  active widget is changed. Note that child_widget may be "None".
        # on_click_child is a callable with signature (child_widget, event) that gets called when the
        #  child widget is clicked
        super().__init__(dx, dy, w, h, can_take_focus=can_take_focus, **kwargs)
        self.draw_border = draw_border
        self.border = border
        self._interior_widgets = list()
        self.padding = padding
        self.top_widget = 0
        self.up_button = up_button
        self.up_button.on_click = self.scroll_up
        self.up_button.kbhandler = self
        self.down_button = down_button
        self.down_button.on_click = self.scroll_down
        self.down_button.frame = self.down_button.off_frame
        self.down_button.kbhandler = self
        self.autoclick = autoclick
        self.focus_locked = focus_locked
        self.on_activate_child = on_activate_child
        self.activate_child_on_enter = activate_child_on_enter
        self._selected_widget_id = 0
        self.selected_widget_id = 0

        self.up_button.frame = self.up_button.off_frame
        self.down_button.frame = self.down_button.off_frame

        self.on_click_child = on_click_child

        self.focus_border = focus_border

    def _set_selected_widget_id(self, widindex):
        if 0 <= widindex < len(self._interior_widgets):
            wid = self._interior_widgets[widindex]
            if widindex != self._selected_widget_id:
                self._selected_widget_id = widindex
                if not wid.visible:
                    self.scroll_to_index(widindex)
                if self.autoclick and wid.on_click:
                    wid.on_click(wid, None)

            if self.on_activate_child:
                self.on_activate_child(self, wid)
        else:
            self._selected_widget_id = 0

    def _get_selected_widget_id(self):
        return self._selected_widget_id

    selected_widget_id = property(_get_selected_widget_id, _set_selected_widget_id)

    def kb_flash_override(self, child):
        return ((my_state.focused_widget is self) or self.focus_locked) and (child in self._interior_widgets) and (
                self._interior_widgets.index(child) == self.selected_widget_id
        )

    def _decorate_click(self, other_on_click):
        def nuclick(wid, ev):
            if wid.visible and wid in self._interior_widgets and self._selected_widget_id != self._interior_widgets.index(wid):
                self.selected_widget_id = self._interior_widgets.index(wid)
            if other_on_click:
                other_on_click(wid, ev)
            if self.on_click_child:
                self.on_click_child(wid, ev)

        return nuclick

    def _decorate_on_enter(self, other_on_enter):
        def nuenter(wid):
            if wid.visible:
                if wid in self._interior_widgets:
                    self.selected_widget_id = self._interior_widgets.index(wid)
                if other_on_enter:
                    other_on_enter(wid)

        return nuenter

    def add_interior(self, other_w, pos=None):
        self.children.append(other_w)
        if pos is None:
            self._interior_widgets.append(other_w)
        else:
            self._interior_widgets.insert(pos, other_w)
        # Set the position of other_w inside this widget.
        other_w.parent = self
        other_w.dx = 0
        other_w.anchor = frects.ANCHOR_UPPERLEFT
        other_w.should_hilight = self.kb_flash_override
        other_w.can_take_focus = False
        self._position_contents()
        other_w.on_click = self._decorate_click(other_w.on_click)
        if self.activate_child_on_enter:
            other_w.on_enter = self._decorate_on_enter(other_w.on_enter)

    def is_interior_widget(self, other_w):
        return other_w in self._interior_widgets

    def clear(self):
        for w in list(self._interior_widgets):
            self._interior_widgets.remove(w)
            self.children.remove(w)

    def remove(self, other_widget):
        if other_widget in self._interior_widgets:
            self._interior_widgets.remove(other_widget)
            self.children.remove(other_widget)
            self._position_contents()

    def _position_contents(self):
        # Disable all interior widgets, except those currently visible.
        for w in self._interior_widgets:
            w.visible = False
        dy = 0
        n = self.top_widget
        if n >= len(self._interior_widgets):
            n = 0
        while (dy < self.h) and (n < len(self._interior_widgets)):
            widg = self._interior_widgets[n]
            widg.dy = dy
            if (dy == 0) or (dy + widg.h + self.padding <= self.h):
                widg.visible = True
            dy += widg.h + self.padding
            n += 1
        # Activate or deactivate the up/down buttons.
        if self.top_widget > 0:
            self.up_button.frame = self.up_button.on_frame
        else:
            self.up_button.frame = self.up_button.off_frame
        if self._interior_widgets and not self._interior_widgets[-1].visible:
            self.down_button.frame = self.down_button.on_frame
        else:
            self.down_button.frame = self.down_button.off_frame

        if self.selected_widget_id < self.top_widget:
            self.selected_widget_id = self.top_widget
        elif self.selected_widget_id >= (n - 1):
            self.selected_widget_id = max(n - 2, 0)

    def scroll_up(self, *_args):
        if self.top_widget > 0:
            self.top_widget -= 1
            self._position_contents()

    def scroll_down(self, *_args):
        if self._interior_widgets and not self._interior_widgets[-1].visible:
            self.top_widget += 1
            self._position_contents()

    def scroll_to_index(self, index):
        '''Programmatic access to ensure a particular list item is shown'''
        if index < len(self._interior_widgets) and not self._interior_widgets[index].visible:
            self.top_widget = index
            self._position_contents()
            self.selected_widget_id = index

    def sort(self, key=None):
        if not key:
            key = str
        self._interior_widgets.sort(key=key)
        self._position_contents()

    def get_items(self):
        return list(self._interior_widgets)

    def get_active_item(self):
        if 0 <= self._selected_widget_id < len(self._interior_widgets):
            return self._interior_widgets[self._selected_widget_id]

    def set_item_by_position( self , n ):
        self.selected_widget_id = n

    def _builtin_responder(self, ev):
        if (ev.type == pygame.MOUSEBUTTONDOWN) and self.get_rect().collidepoint(my_state.mouse_pos):
            if (ev.button == 4):
                self.scroll_up()
            elif (ev.button == 5):
                self.scroll_down()
        elif ((my_state.focused_widget is self) or self.focus_locked) and (ev.type == pygame.KEYDOWN):
            #if my_state.is_key_for_action(ev, "click_widget"):
            #    if self.selected_widget_id < len(self._interior_widgets):
            #        mybutton = self._interior_widgets[self.selected_widget_id]
            #        if mybutton.on_click:
            #            mybutton.on_click(mybutton, ev)
            #        my_state.widget_responded = True
            if my_state.is_key_for_action(ev, "up") and self.selected_widget_id > 0:
                self.selected_widget_id -= 1
                self.register_response()
            elif my_state.is_key_for_action(ev, "down") and self.selected_widget_id < (len(self._interior_widgets) - 1):
                self.selected_widget_id += 1
                self.register_response()

    def _render(self, delta):
        if self.draw_border:
            if self.should_hilight(self):
                self.focus_border.render(self.get_rect())
            else:
                self.border.render(self.get_rect())


class RowWidget(Widget):
    def __init__(self, dx, dy, w, h, draw_border=False, border=default_border, padding=5, border_inflation=10,
                 **kwargs):
        super().__init__(dx, dy, w, h, **kwargs)
        self.draw_border = draw_border
        self.border = border
        self._left_widgets = list()
        self._center_widgets = list()
        self._right_widgets = list()
        self.padding = padding
        self.border_inflation=border_inflation

    def add_left(self, other_w):
        self.children.append(other_w)
        self._left_widgets.append(other_w)
        # Set the position of other_w inside this widget.
        other_w.parent = self
        self._position_contents()

    def add_center(self, other_w):
        self.children.append(other_w)
        self._center_widgets.append(other_w)
        # Set the position of other_w inside this widget.
        other_w.parent = self
        self._position_contents()

    def add_right(self, other_w):
        self.children.append(other_w)
        self._right_widgets.append(other_w)
        # Set the position of other_w inside this widget.
        other_w.parent = self
        self._position_contents()

    def _position_contents(self):
        dx = 0
        self.h = max(w.h for w in self._right_widgets + self._center_widgets + self._left_widgets)
        for widg in self._left_widgets:
            widg.dx = dx
            widg.dy = -widg.h // 2
            widg.anchor = frects.ANCHOR_LEFT
            dx += widg.w + self.padding

        if self._center_widgets:
            dx = -(sum(w.w for w in self._center_widgets) + (len(self._center_widgets) - 1) * self.padding) // 2
            for widg in self._center_widgets:
                widg.dx = dx
                widg.dy = -widg.h // 2
                widg.anchor = frects.ANCHOR_CENTER
                dx += widg.w + self.padding

        if self._right_widgets:
            dx = -sum(w.w for w in self._right_widgets) - (len(self._right_widgets) - 1) * self.padding
            for widg in self._right_widgets:
                widg.dx = dx
                widg.dy = -widg.h // 2
                widg.anchor = frects.ANCHOR_RIGHT
                dx += widg.w + self.padding

    def _render(self, delta):
        if self.draw_border:
            self.border.render(self.get_rect().inflate(self.border_inflation, self.border_inflation))
        if self._should_flash():
            self._default_flash()




class TextEntryWidget(Widget):
    ALLOWABLE_CHARACTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890()-=_+,.?"'

    def __init__(self, dx, dy, w, h, text='***', color=None, font=None, justify=0, on_change=None, draw_border=True,
                 on_left_at_zero=None, on_right_at_end=None, on_backspace_at_zero=None, can_take_focus=True, **kwargs):
        # on_left_at_zero, on_right_at_end, and on_backspace_at_zero are functions that get called when these events
        #   happen. Usually nothing happens, but when this text entry widget is part of a text entry panel (see below)
        #   we need some special behaviours.
        self.font = font or my_state.medium_font
        h = h or self.font.get_linesize()
        # on_change is a callable that takes (widget,ev) whenever the contents of the text changes.
        super(TextEntryWidget, self).__init__(dx, dy, w, h, can_take_focus=can_take_focus, **kwargs)
        if not text:
            text = ''
        self.char_list = list(text)
        self.color = color or TEXT_COLOR
        self.justify = justify
        self.input_cursor = image.Image("sys_textcursor.png", 8, 16)
        self.on_change = on_change
        self.draw_border = draw_border
        self.cursor_i = len(text)  # The cursor index is the character the cursor is currently sitting right on
        # top of. So at index len(text), it's sitting at the end of the text past the last character.
        self.on_left_at_zero = on_left_at_zero
        self.on_right_at_end = on_right_at_end
        self.on_backspace_at_zero = on_backspace_at_zero
        self.text_input_on = False

    def get_text_rect(self, w, h, mydest):
        myrect = pygame.Rect(0, 0, w, h)
        if self.justify == -1:
            myrect.midleft = mydest.midleft
        elif self.justify == 1:
            myrect.midright = mydest.midright
        else:
            myrect.center = mydest.center
        return myrect

    def _render(self, delta):
        mydest = self.get_rect()
        #print(self.should_hilight(self))
        if self.draw_border:
            if self.should_hilight(self):
                widget_border_on.render(mydest.inflate(-4, -4))

            else:
                widget_border_off.render(mydest.inflate(-4, -4))
        myimage = self.font.render(self.text, True, self.color)
        textdest = self.get_text_rect(myimage.get_width(), myimage.get_height(), mydest)
        my_state.screen.set_clip(mydest)
        _=my_state.screen.blit(myimage, textdest)
        my_state.screen.set_clip(None)
        if self.should_hilight(self):
            cursor_dest = self.input_cursor.bitmap.get_rect(topleft=textdest.topleft)
            if self.cursor_i > 0:
                cursor_dest.left += self.font.size(self.text[:self.cursor_i])[0]
            self.input_cursor.render(cursor_dest, (my_state.anim_phase // 3) % 4)

    def _builtin_responder(self, ev):
        if self.should_hilight(self):
            if ev.type == pygame.TEXTINPUT:
                if len(ev.text) > 0:
                    self.char_list.insert(max(self.cursor_i, 0), ev.text)
                    self.cursor_i += len(ev.text)
                    if self.on_change:
                        self.on_change(self, ev)
                    my_state.widget_responded = True
            elif ev.type == pygame.KEYDOWN:
                if my_state.is_key_for_action(ev, "backspace"):
                    if (len(self.char_list) > 0) and self.cursor_i > 0:
                        del self.char_list[self.cursor_i - 1]
                        self.cursor_i -= 1
                        if self.on_change:
                            self.on_change(self, ev)
                        my_state.widget_responded = True
                    elif self.on_backspace_at_zero:
                        self.on_backspace_at_zero()

                elif my_state.is_key_for_action(ev, "left"):
                    if self.cursor_i > 0:
                        self.cursor_i -= 1
                    elif self.on_left_at_zero:
                        self.on_left_at_zero()
                    my_state.widget_responded = True
                elif my_state.is_key_for_action(ev, "right"):
                    if self.cursor_i < len(self.char_list):
                        self.cursor_i += 1
                    elif self.on_right_at_end:
                        self.on_right_at_end()
                    my_state.widget_responded = True
        if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and self.get_rect().collidepoint(my_state.mouse_pos):
            mytext = self.text
            mydest = self.get_rect()
            w, h = self.font.size(mytext)
            textdest = self.get_text_rect(w, h, mydest)
            self.cursor_i = len(mytext)
            for c in range(1, len(mytext) + 1):
                w, h = self.font.size(mytext[:c])
                textdest.width = w
                if textdest.collidepoint(my_state.mouse_pos):
                    self.cursor_i = c - 1
                    break

    def _get_text(self):
        return "".join(self.char_list)

    def _set_text(self, text):
        self.char_list = list(text)
        if self.on_change:
            self.on_change(self, None)

    text = property(_get_text, _set_text)

    def quietly_set_text(self, text):
        # Set the text without calling on_change.
        self.char_list = list(text)


class TextEditorPanel(ScrollColumnWidget):
    def __init__(self, dx, dy, w, h, up_button, down_button, draw_border=False, border=default_border, padding=5,
                 text="***", color=None, font=None, justify=-1, on_change=None, **kwargs):
        # on_change is a callable that takes (widget,ev) whenever the contents of the text changes.
        super().__init__(dx, dy, w, h, up_button, down_button, padding=0, autoclick=True,
                         draw_border=True, **kwargs)
        if not text:
            text = ''
        self.color = color or TEXT_COLOR
        self.font = font or my_state.medium_font
        self.justify = justify

        self.update_text(text)
        # self.children.append(up_arrow)
        # self.children.append(down_arrow)

        self.on_change = on_change
        # The current index of the cursor and carat:
        self.cursor_i = 0

    def update_text(self, text=None):
        editor_i = 0
        editor_total = 0
        mylines = list()
        for line in self._interior_widgets:
            myline = line.text.lstrip().strip()
            mylines.append(myline)
            if line is my_state.focused_widget:
                editor_i = editor_total + line.cursor_i
            editor_total += len(myline)
            if line is not self._interior_widgets[-1]:
                editor_total += 1
        self.clear()
        if not text:
            text = ' '.join(mylines)
        mylines = wrapline(text, self.font, self.w)
        has_set_active = False
        for n, line in enumerate(mylines):
            textwidget = TextEntryWidget(0, 0, self.w - 8, 0, line, font=self.font, color=self.color,
                                         on_left_at_zero=self._on_left_at_zero, on_right_at_end=self._on_right_at_end,
                                         on_backspace_at_zero=self._on_backspace_at_zero, justify=self.justify,
                                         on_change=self._change_line, draw_border=False)
            self.add_interior(textwidget)
            if not has_set_active:
                if editor_i <= len(line):
                    self.selected_widget_id = n
                    textwidget.cursor_i = editor_i
                    has_set_active = True
                elif line is mylines[-1] and editor_i > len(line):
                    self.selected_widget_id = n
                    textwidget.char_list.append(" ")
                    textwidget.cursor_i = len(textwidget.char_list)
                    has_set_active = True
                editor_i -= len(line) + 1

        if not self._interior_widgets:
            textwidget = TextEntryWidget(0, 0, self.w - 8, 0, "", font=self.font,
                                         on_left_at_zero=self._on_left_at_zero, on_right_at_end=self._on_right_at_end,
                                         on_backspace_at_zero=self._on_backspace_at_zero,
                                         on_change=self._change_line, draw_border=False)
            self.add_interior(textwidget)
            self.selected_widget_id = 0

    def _on_left_at_zero(self):
        if self.selected_widget_id > 0:
            self.selected_widget_id -= 1
            self._interior_widgets[self.selected_widget_id].cursor_i = len(
                self._interior_widgets[self.selected_widget_id].char_list)

    def _on_right_at_end(self):
        if self.selected_widget_id < (len(self._interior_widgets) - 1):
            self.selected_widget_id += 1
            # I am setting the cursor_i to -1 since the new widget is also going to get this keyboard event and move
            # the cursor_i one more step to the right, because it's the widget after the widget that called this
            # function and hasn't processed events yet. It's kludgey and ugly but if it works waddaya gonna do?
            # If anyone has a more elegant solution please submit a pull request on GitHub.
            self._interior_widgets[self.selected_widget_id].cursor_i = -1

    def _on_backspace_at_zero(self):
        if self.selected_widget_id > 0:
            widj0 = self._interior_widgets[self.selected_widget_id]
            cursor_i = widj0.cursor_i
            self.selected_widget_id -= 1
            widj1 = self._interior_widgets[self.selected_widget_id]
            widj1.cursor_i = len(widj1.char_list) + cursor_i
            widj1.char_list += widj0.char_list
            widj0.char_list = list()
            self.update_text()

    def _set_active_widget(self, widindex):
        if 0 <= widindex < len(self._interior_widgets): # and widindex != self._active_widget:
            self._active_widget = widindex
            wid = self._interior_widgets[widindex]
            my_state.focused_widget = wid
            if not wid.active:
                self.scroll_to_index(widindex)
            if self.autoclick and wid.on_click:
                wid.on_click(wid, None)

    def _get_active_widget(self):
        if my_state.focused_widget in self._interior_widgets:
            return self._interior_widgets.index(my_state.focused_widget)
        else:
            return 0

    selected_widget_id = property(_get_active_widget, _set_active_widget)

    def _change_line(self, _wid, ev):
        self.update_text(self.text)
        if self.on_change:
            self.on_change(self, ev)

    def _get_text(self):
        lines = list()
        for w in self._interior_widgets:
            lines.append(w.text.lstrip().strip())
        return " ".join(lines)

    def _set_text(self, text):
        self.update_text(text)

    text = property(_get_text, _set_text)

    def _builtin_responder(self, ev):
        if (ev.type == pygame.MOUSEBUTTONDOWN) and self.get_rect().collidepoint(my_state.mouse_pos):
            if (ev.button == 4):
                self.scroll_up()
            elif (ev.button == 5):
                self.scroll_down()
            my_state.widget_responded = True

        elif ((my_state.focused_widget in self._interior_widgets) or self.focus_locked) and (ev.type == pygame.KEYDOWN):
            if my_state.is_key_for_action(ev, "up") and self.selected_widget_id > 0:
                cursor_i = self._interior_widgets[self.selected_widget_id].cursor_i
                self.selected_widget_id -= 1
                self._interior_widgets[self.selected_widget_id].cursor_i = min(cursor_i, len(
                    self._interior_widgets[self.selected_widget_id].char_list))
                my_state.widget_responded = True
            elif my_state.is_key_for_action(ev, "down") and self.selected_widget_id < (len(self._interior_widgets) - 1):
                cursor_i = self._interior_widgets[self.selected_widget_id].cursor_i
                self.selected_widget_id += 1
                self._interior_widgets[self.selected_widget_id].cursor_i = min(cursor_i, len(
                    self._interior_widgets[self.selected_widget_id].char_list))
                my_state.widget_responded = True


class TextEditorWidget(Widget):
    # This widget is going to be different from the text entry widget above in that it's meant to be a full
    # functioned text editor. What have I gotten myself into?
    def __init__(self, dx, dy, w, h, text='***', color=None, font=None, justify=-1, on_change=None, **kwargs):
        # on_change is a callable that takes (widget,ev) whenever the contents of the text changes.
        super().__init__(dx, dy, w, h, **kwargs)
        if not text:
            text = ''

        up_arrow = ButtonWidget(-32, -16, 32, 16, sprite=image.Image("sys_updownbuttons_small.png", 32, 16),
                                on_frame=0, off_frame=1, parent=self, anchor=frects.ANCHOR_UPPERRIGHT)
        down_arrow = ButtonWidget(-32, 0, 32, 16, sprite=image.Image("sys_updownbuttons_small.png", 32, 16),
                                  on_frame=2, off_frame=3, parent=self, anchor=frects.ANCHOR_LOWERRIGHT)

        self.editor_area = TextEditorPanel(8, 4, w - 16, h - 8, up_arrow, down_arrow,
                                           color=color, font=font, justify=justify, on_change=on_change, text=text,
                                           parent=self, draw_border=True, anchor=frects.ANCHOR_UPPERLEFT)

        self.children.append(self.editor_area)
        self.children.append(up_arrow)
        self.children.append(down_arrow)

        # self.children.append(up_arrow)
        # self.children.append(down_arrow)

    def _get_text(self):
        return self.editor_area.text

    def _set_text(self, text):
        self.editor_area.text = text

    text = property(_get_text, _set_text)





# Widgets for columns

class ColTextEntryWidget(RowWidget):
    def __init__(self, width, prompt="Enter Text", text='***', color=None, font=None, justify=-1, on_change=None,
                 **kwargs):
        mylabel = LabelWidget(0, 0, width * 2 // 5 - 10, 0, prompt, font=font)
        super().__init__(0, 0, width, mylabel.h + 8, **kwargs)
        self.add_left(mylabel)
        self.my_text_widget = TextEntryWidget(0, 0, width * 3 // 5, mylabel.h + 8, text, color, font, justify,
                                              on_change=on_change, data=kwargs.get("data"))
        self.add_right(self.my_text_widget)

    def _get_text(self):
        return self.my_text_widget.text

    def _set_text(self, text):
        self.my_text_widget.text = text

    text = property(_get_text, _set_text)

    def quietly_set_text(self, text):
        # Set the text without calling on_change.
        self.my_text_widget.quietly_set_text(text)


class CheckboxWidget(RowWidget):
    CHECK_FRAME = {True: 0, False: 1}
    def __init__(self, w, caption, is_checked, on_change, **kwargs):
        # on_change is a callback function that takes a bool value as its parameter.
        super().__init__(0, 0, w, 20, padding=5, **kwargs)
        self.state_indicator = ButtonWidget(0,0,20,20,image.Image("sys_checkbox.png", 20, 20),
                                                         frame=self.CHECK_FRAME[bool(is_checked)],
                                                         on_click=self._toggle_state)
        self.add_left(self.state_indicator)
        self.add_left(LabelWidget(0,0,w-25,0,caption, on_click=self._toggle_state))
        self.is_checked = is_checked
        self.on_click = self._toggle_state
        self.on_change = on_change

    def _toggle_state(self, _wid, _ev):
        self.is_checked = not self.is_checked
        self.state_indicator.frame = self.CHECK_FRAME[bool(self.is_checked)]
        if self.on_change:
            self.on_change(self.is_checked)
