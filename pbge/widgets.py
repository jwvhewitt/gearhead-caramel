from . import frects
from . import my_state,render_text,draw_text,TEXT_COLOR,Border,default_border,wait_event, wrap_with_records, wrap_multi_line
import pygame
from . import image
from . import rpgmenu

# respond_event: Receives an event.
#   If the widget has a method corresponding to the event,
#   that method will be called.

# Note that the widget needs to be added to my_state.widgets to be used!
# Or, as the child of another widget. Removing it from that list
# removes it.

ACTIVE_FLASH = [(0,0,0),] * 5 + [(230,230,0),] * 20

widget_border_off = Border( border_width=8, tex_width=16, border_name="sys_widbor_edge1.png", tex_name="sys_widbor_back.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2, padding=2 )
widget_border_on = Border( border_width=8, tex_width=16, border_name="sys_widbor_edge2.png", tex_name="sys_widbor_back.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2, padding=2 )
popup_menu_border = Border( border_width=8, tex_width=16, border_name="sys_widbor_edge2.png", tex_name="sys_defbackground.png", tl=0, tr=3, bl=4, br=5, t=1, b=1, l=2, r=2, padding=8, transparent=False )



class Widget( frects.Frect ):
    def __init__( self, dx, dy, w, h, data=None, on_click=None, tooltip=None, children=(), active=True, show_when_inactive=False, on_right_click=None, **kwargs ):
        # on_click takes widget, event as parameters.
        # on_right_click takes widget, event as parameters.
        super().__init__(dx,dy,w,h,**kwargs)
        self.data = data
        self.active = active
        self.tooltip = tooltip
        self.on_click = on_click
        self.on_right_click = on_right_click
        self.children = list(children)
        self.show_when_inactive = show_when_inactive

    def respond_event( self, ev ):
        if self.active:
            for c in self.children:
                c.respond_event(ev)
            if self.get_rect().collidepoint(my_state.mouse_pos):
                if self.active and (ev.type == pygame.MOUSEBUTTONUP) and (ev.button == 1) and not my_state.widget_clicked:
                    if not my_state.widget_clicked:
                        my_state.active_widget = self
                    if self.on_click:
                        self.on_click(self,ev)
                    my_state.widget_clicked = True
                elif self.active and (ev.type == pygame.MOUSEBUTTONUP) and (ev.button == 3) and self.on_right_click and not my_state.widget_clicked:
                    if not my_state.widget_clicked:
                        my_state.active_widget = self
                    self.on_right_click(self, ev)
                    my_state.widget_clicked = True
            elif my_state.active_widget is self:
                if self.on_click and (ev.type == pygame.KEYDOWN) and (ev.key in my_state.get_keys_for("click_widget")):
                    self.on_click(self,ev)
                    my_state.widget_clicked = True
            self._builtin_responder(ev)

    def _builtin_responder(self,ev):
        pass

    def super_render( self ):
        # This renders the widget and children, setting tooltip and whatnot.
        if self.active or self.show_when_inactive:
            self.render(self._should_flash())
            if self.tooltip and self.get_rect().collidepoint(my_state.mouse_pos):
                my_state.widget_tooltip = self.tooltip
            for c in self.children:
                c.super_render()

    def _should_flash(self):
        if self.parent and hasattr(self.parent, "kb_flash_override"):
            return self.parent.kb_flash_override(self)
        elif hasattr(self, "kbhandler") and self.kbhandler and hasattr(self.kbhandler, "kb_flash_override"):
            return self.kbhandler.kb_flash_override(self)
        else:
            return (self is my_state.active_widget) and my_state.active_widget_hilight

    def _default_flash(self):
        pygame.draw.rect(my_state.screen, ACTIVE_FLASH[my_state.anim_phase % len(ACTIVE_FLASH)], self.get_rect(), 1)

    def render(self, flash=False):
        if flash:
            self._default_flash()

    def is_kb_selectable(self):
        if self.parent and hasattr(self.parent, "kb_select_override"):
            return self.parent.kb_select_override(self)
        elif hasattr(self, "kbhandler") and self.kbhandler and hasattr(self.kbhandler, "kb_select_override"):
            return self.kbhandler.kb_select_override(self)
        else:
            return self.on_click


class ButtonWidget( Widget ):
    def __init__( self, dx, dy, w, h, sprite=None, frame=0, on_frame=0, off_frame=0, **kwargs ):
        super(ButtonWidget, self).__init__(dx,dy,w,h,**kwargs)
        self.sprite = sprite
        self.frame = frame
        self.on_frame = on_frame
        self.off_frame = off_frame

    def render(self, flash=False):
        if self.sprite:
            self.sprite.render(self.get_rect(),self.frame)
        if flash:
            self._default_flash()

class LabelWidget( Widget ):
    def __init__( self, dx, dy, w, h, text='***', color=None, font=None, justify=-1, draw_border=False, border=widget_border_off, text_fun = None, **kwargs ):
        # text_fun is a function that takes this widget as a parameter. It returns the text to display.
        super(LabelWidget, self).__init__(dx,dy,w,h,**kwargs)
        self.text = text
        self.color = color or TEXT_COLOR
        self.font = font or my_state.small_font
        if h == 0:
            self.h = len(wrap_multi_line(text, self.font, self.w)) * self.font.get_linesize()
        self.justify = justify
        self.draw_border = draw_border
        self.border = border
        self.text_fun = text_fun
    def render(self, flash=False):
        if self.draw_border:
            self.border.render(self.get_rect())
        if self.text_fun:
            self.text = self.text_fun(self)
        draw_text(self.font,self.text,self.get_rect(),self.color,self.justify)
        if flash:
            self._default_flash()

class TextEntryWidget( Widget ):
    ALLOWABLE_CHARACTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890()-=_+,.?"'
    def __init__( self, dx, dy, w, h, text='***', color=None, font=None, justify=-1, on_change=None, **kwargs ):
        # on_change is a callable that takes (widget,ev) whenever the contents of the text changes.
        super(TextEntryWidget, self).__init__(dx,dy,w,h,**kwargs)
        if not text:
            text = ''
        self.char_list = list(text)
        self.color = color or TEXT_COLOR
        self.font = font or my_state.big_font
        self.justify = justify
        self.input_cursor = image.Image( "sys_textcursor.png" , 8 , 16 )
        self.on_change = on_change

    def render(self, flash=False):
        mydest = self.get_rect()
        if self is my_state.active_widget:
            widget_border_on.render(mydest.inflate(-4,-4))
        else:
            widget_border_off.render(mydest.inflate(-4,-4))
        myimage = self.font.render( self.text, True, self.color )
        my_state.screen.set_clip( mydest )
        textdest = myimage.get_rect(center=mydest.center)
        my_state.screen.blit( myimage , textdest )
        my_state.screen.set_clip( None )
        if flash or (my_state.active_widget is self):
            self.input_cursor.render( textdest.topright , ( my_state.anim_phase // 3 ) % 4 )


    def _builtin_responder(self,ev):
        if my_state.active_widget is self:
            if ev.type == pygame.KEYDOWN:
                if (ev.key == pygame.K_BACKSPACE) and (len(self.char_list) > 0):
                    del self.char_list[-1]
                    if self.on_change:
                        self.on_change(self,ev)
                elif (ev.unicode in self.ALLOWABLE_CHARACTERS) and (len(ev.unicode) > 0):
                    self.char_list.append(ev.unicode)
                    if self.on_change:
                        self.on_change(self,ev)

    def is_kb_selectable(self):
        return True

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


class RadioButtonWidget( Widget ):
    def __init__( self, dx, dy, w, h, sprite=None, buttons=(), spacing=2, **kwargs ):
        # buttons is a list of dicts possibly containing: on_frame, off_frame, on_click, on_right_click, tooltip
        super().__init__(dx,dy,w,h,**kwargs)
        self.sprite = sprite
        self.buttons = list()
        self.spacing = spacing
        ddx = 0
        for b in buttons:
            self.buttons.append(ButtonWidget(
                ddx,0,sprite.frame_width,sprite.frame_height,sprite,
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

    def activate_button( self, button ):
        self.active_button.frame = self.active_button.off_frame
        self.active_button = button
        button.frame = button.on_frame

    def get_button(self, data_sought):
        for b in self.buttons:
            if b.data == data_sought:
                return b

    def click_radio( self, button, ev ):
        self.activate_button( button )
        if button.data:
            button.data(button,ev)


class ColumnWidget(Widget):
    def __init__( self, dx, dy, w, h, draw_border=False, border=default_border, padding=5, center_interior=False, **kwargs ):
        super(ColumnWidget, self).__init__(dx,dy,w,h,**kwargs)
        self.draw_border = draw_border
        self.border = border
        self._interior_widgets = list()
        self._header_widget = None
        self.padding = padding
        self.center_interior = center_interior

    def add_interior(self,other_w):
        self.children.append(other_w)
        self._interior_widgets.append(other_w)
        # Set the position of other_w inside this widget.
        other_w.parent = self
        self._position_contents()

    def set_header(self,other_w):
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
                widg.dx = ( self.w - widg.w ) // 2
            else:
                widg.dx = 0
            widg.dy = dy
            widg.anchor = frects.ANCHOR_UPPERLEFT
            dy += widg.h + self.padding
        self.h = dy

    def render(self, flash=False):
        if self.draw_border:
            self.border.render(self.get_rect())
        if flash:
            self._default_flash()


class ScrollColumnWidget(Widget):
    def __init__(self, dx, dy, w, h, up_button, down_button, draw_border=False, border=default_border, padding=5,
                 autoclick=False, focus_locked=False, **kwargs):
        super(ScrollColumnWidget, self).__init__(dx,dy,w,h,**kwargs)
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
        self._active_widget = -1
        self.active_widget = 0

    def _set_active_widget(self, widindex):
        if widindex >= 0 and widindex < len(self._interior_widgets) and widindex != self._active_widget:
            self._active_widget = widindex
            wid = self._interior_widgets[widindex]
            if not wid.active:
                self.scroll_to_index(widindex)
            if self.autoclick and wid.on_click:
                wid.on_click(wid, None)

    def _get_active_widget(self):
        return self._active_widget

    active_widget = property(_get_active_widget, _set_active_widget)

    def kb_select_override(self, child):
        return not (child in self._interior_widgets or child is self.up_button or child is self.down_button)

    def kb_flash_override(self, child):
        return ((my_state.active_widget is self) or self.focus_locked) and (child in self._interior_widgets) and (
            self._interior_widgets.index(child) == self.active_widget
        )

    def is_kb_selectable(self):
        return True

    def decorate_click(self, other_on_click):
        def nuclick(wid, ev):
            if wid in self._interior_widgets and self.active_widget != self._interior_widgets.index(wid):
                self.active_widget = self._interior_widgets.index(wid)
            other_on_click(wid, ev)
        return nuclick

    def add_interior(self,other_w):
        self.children.append(other_w)
        self._interior_widgets.append(other_w)
        # Set the position of other_w inside this widget.
        other_w.parent = self
        other_w.dx = 0
        other_w.anchor = frects.ANCHOR_UPPERLEFT
        self._position_contents()
        if other_w.on_click:
            other_w.on_click = self.decorate_click(other_w.on_click)

    def clear(self):
        for w in list(self._interior_widgets):
            self._interior_widgets.remove(w)
            self.children.remove(w)

    def _position_contents(self):
        # Disable all interior widgets, except those currently visible.
        for w in self._interior_widgets:
            w.active = False
        dy = 0
        n = self.top_widget
        if n >= len(self._interior_widgets):
            n = 0
        while (dy < self.h) and (n < len(self._interior_widgets)):
            widg = self._interior_widgets[n]
            widg.dy = dy
            if (dy==0) or (dy + widg.h + self.padding <= self.h):
                widg.active = True
            dy += widg.h + self.padding
            n += 1
        # Activate or deactivate the up/down buttons.
        if self.top_widget > 0:
            self.up_button.frame = self.up_button.on_frame
        else:
            self.up_button.frame = self.up_button.off_frame
        if self._interior_widgets and not self._interior_widgets[-1].active:
            self.down_button.frame = self.down_button.on_frame
        else:
            self.down_button.frame = self.down_button.off_frame

        if self.active_widget < self.top_widget:
            self.active_widget = self.top_widget
        elif self.active_widget >= (n-1):
            self.active_widget = max(n - 2,0)

    def scroll_up(self,*args):
        if self.top_widget > 0:
            self.top_widget -= 1
            self._position_contents()

    def scroll_down(self,*args):
        if self._interior_widgets and not self._interior_widgets[-1].active:
            self.top_widget += 1
            self._position_contents()

    def scroll_to_index(self, index):
        '''Programmatic access to ensure a particular list item is shown'''
        if index < len(self._interior_widgets) and not self._interior_widgets[index].active:
            self.top_widget = index
            self._position_contents()
            self.active_widget = index

    def sort(self,key=None):
        self._interior_widgets.sort(key=key)
        self._position_contents()

    def _builtin_responder(self,ev):
        if (ev.type == pygame.MOUSEBUTTONDOWN) and self.get_rect().collidepoint(my_state.mouse_pos):
            if (ev.button == 4):
                self.scroll_up()
            elif (ev.button == 5):
                self.scroll_down()
        elif ((my_state.active_widget is self) or self.focus_locked) and (ev.type == pygame.KEYDOWN):
            if ev.key in my_state.get_keys_for("click_widget"):
                if self.active_widget < len(self._interior_widgets):
                    mybutton = self._interior_widgets[self.active_widget]
                    mybutton.on_click(mybutton, ev)
                    my_state.widget_clicked = True
            elif ev.key in my_state.get_keys_for("up") and self.active_widget > 0:
                self.active_widget -= 1
            elif ev.key in my_state.get_keys_for("down") and self.active_widget < (len(self._interior_widgets)-1):
                self.active_widget += 1

    def render(self, flash=False):
        if self.draw_border:
            self.border.render(self.get_rect())
        if flash:
            self._default_flash()


class RowWidget(Widget):
    def __init__( self, dx, dy, w, h, draw_border=False, border=default_border, padding=5, **kwargs ):
        super().__init__(dx,dy,w,h,**kwargs)
        self.draw_border = draw_border
        self.border = border
        self._left_widgets = list()
        self._center_widgets = list()
        self._right_widgets = list()
        self.padding = padding

    def add_left(self,other_w):
        self.children.append(other_w)
        self._left_widgets.append(other_w)
        # Set the position of other_w inside this widget.
        other_w.parent = self
        self._position_contents()

    def add_center(self,other_w):
        self.children.append(other_w)
        self._center_widgets.append(other_w)
        # Set the position of other_w inside this widget.
        other_w.parent = self
        self._position_contents()

    def add_right(self,other_w):
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
            widg.dy = -widg.h//2
            widg.anchor = frects.ANCHOR_LEFT
            dx += widg.w + self.padding

        if self._center_widgets:
            dx = -(sum(w.w for w in self._center_widgets) + (len(self._center_widgets) - 1) * self.padding)//2
            for widg in self._center_widgets:
                widg.dx = dx
                widg.dy = -widg.h//2
                widg.anchor = frects.ANCHOR_CENTER
                dx += widg.w + self.padding

        if self._right_widgets:
            dx = -sum(w.w for w in self._right_widgets) - (len(self._right_widgets) - 1) * self.padding
            for widg in self._right_widgets:
                widg.dx = dx
                widg.dy = -widg.h//2
                widg.anchor = frects.ANCHOR_RIGHT
                dx += widg.w + self.padding

    def render(self, flash=False):
        if self.draw_border:
            self.border.render(self.get_rect())
        if flash:
            self._default_flash()


class DropdownWidget( Widget ):
    MENU_HEIGHT = 150
    def __init__( self, dx, dy, w, h, color=None, font=None, justify=-1, on_select=None, **kwargs ):
        # on_select is a callable that takes the menu query result as its argument
        super(DropdownWidget, self).__init__(dx,dy,w,h,**kwargs)
        self.color = color or TEXT_COLOR
        self.font = font or my_state.small_font
        self.on_select = on_select
        self.on_click = self.open_menu
        self.menu = rpgmenu.Menu(dx,dy,w,self.MENU_HEIGHT,border=popup_menu_border,font=font,anchor=frects.ANCHOR_UPPERLEFT)
    def render(self, flash=False):
        mydest = self.get_rect()
        if self is my_state.active_widget:
            widget_border_on.render(mydest.inflate(-4,-4))
        else:
            widget_border_off.render(mydest.inflate(-4,-4))
        myimage = self.font.render( str(self.menu.get_current_item()), True, self.color )
        my_state.screen.set_clip( mydest )
        textdest = myimage.get_rect(center=mydest.center)
        my_state.screen.blit( myimage , textdest )
        my_state.screen.set_clip( None )
        if flash:
            self._default_flash()

    def add_item(self,msg,value,desc=None):
        self.menu.add_item(msg,value,desc)
    def open_menu(self,also_self_probably,ev):
        mydest = self.get_rect()
        mydest.h = self.menu.h
        mydest.w = self.menu.w
        mydest.clamp_ip(my_state.screen.get_rect())
        self.menu.dx,self.menu.dy = mydest.x,mydest.y
        result = self.menu.query()
        if self.on_select:
            self.on_select(result)
    @property
    def value(self):
        return self.menu.get_current_value()

class TextEditorWidget( Widget ):
    # This widget is going to be different from the text entry widget above in that it's meant to be a full
    # functioned text editor. What have I gotten myself into?
    ALLOWABLE_CHARACTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890()-=_+,.?"\''
    def __init__( self, dx, dy, w, h, text='***', color=None, font=None, justify=-1, on_change=None, **kwargs ):
        # on_change is a callable that takes (widget,ev) whenever the contents of the text changes.
        super().__init__(dx,dy,w,h,**kwargs)
        if not text:
            text = ''
        self.char_list = list(text)
        self.color = color or TEXT_COLOR
        self.font = font or my_state.big_font
        self.justify = justify
        self.cursor_image = image.Image("sys_editcursor.png", 8, 16)

        up_arrow = ButtonWidget(w-32,-8,32,16,sprite=image.Image("sys_updownbuttons_small.png",32,16),on_frame=0,off_frame=1, parent=self)
        down_arrow = ButtonWidget(w-32,h+8,32,16,sprite=image.Image("sys_updownbuttons_small.png",32,16),on_frame=2,off_frame=3, parent=self)

        self.children.append(up_arrow)
        self.children.append(down_arrow)

        self.on_change = on_change
        # The current index of the cursor and carat:
        self.cursor_i = 0
        self.carat_i = None
        self.top_line = 0
        self.num_lines = (self.h - 12) // self.font.get_linesize()

    def get_line_pos(self, index, lengths):
        # Given the buffer index and lengths of each screen line (in characters), return the screen line
        # and the screen index of this position.
        line = 0
        for l in lengths:
            if index < l:
                break
            else:
                index -= l
                line += 1
        return line, index

    def get_buffer_index(self, dx, dy, lines):
        pass

    def render(self, flash=False):
        mydest = self.get_rect()
        if flash or (self is my_state.active_widget):
            widget_border_on.render(mydest.inflate(-4,-4))
        else:
            widget_border_off.render(mydest.inflate(-4,-4))

        lines, lengths = wrap_with_records(self.text, self.font, self.w - 12)

        cursor_line, cursor_pos = self.get_line_pos(self.cursor_i, lengths)

        if self.top_line + self.num_lines - 1 > len(lines):
            self.top_line = max(0, len(lines) - self.num_lines)

        textdest = mydest.inflate(-12,-12)
        my_state.screen.set_clip( textdest )

        current_line = self.top_line
        #print(cursor_countdown, cursor_line, cursor_pos)
        for l in lines[self.top_line:self.top_line + self.num_lines]:
            img = self.font.render(l, True, self.color )
            my_state.screen.blit(img, textdest)
            if self is my_state.active_widget and current_line == cursor_line:
                cdest = textdest.copy()
                cdest.x += self.font.size(l[:cursor_pos])[0] - 4
                self.cursor_image.render(cdest.topleft, (my_state.anim_phase // 5) % 4)
            current_line += 1
            textdest.y += self.font.get_linesize()

        my_state.screen.set_clip( None )

    def _insert(self, new_text):
        for c in list(new_text):
            self.char_list.insert(self.cursor_i, new_text)
            self.cursor_i += 1

    def _builtin_responder(self,ev):
        if my_state.active_widget is self:
            if ev.type == pygame.KEYDOWN:
                if (ev.key == pygame.K_BACKSPACE) and (len(self.char_list) > 0):
                    if self.cursor_i > 0:
                        del self.char_list[self.cursor_i - 1]
                        self.cursor_i -= 1
                        if self.on_change:
                            self.on_change(self,ev)
                elif (ev.key == pygame.K_DELETE) and (len(self.char_list) > 0):
                    if self.cursor_i < len(self.char_list):
                        del self.char_list[self.cursor_i]
                        if self.on_change:
                            self.on_change(self, ev)
                elif ev.key == pygame.K_LEFT:
                    if self.cursor_i > 0:
                        self.cursor_i -= 1
                elif ev.key == pygame.K_RIGHT:
                    if self.cursor_i < len(self.char_list):
                        self.cursor_i += 1
                elif (ev.unicode in self.ALLOWABLE_CHARACTERS) and (len(ev.unicode) > 0):
                    self._insert(ev.unicode)
                    if self.on_change:
                        self.on_change(self,ev)

    def is_kb_selectable(self):
        return True

    def _get_text(self):
        return "".join(self.char_list)

    def _set_text(self, text):
        self.char_list = list(text)
        if self.on_change:
            self.on_change(self, None)

    text = property(_get_text, _set_text)


# Widgets for columns

class ColTextEntryWidget(RowWidget):
    def __init__(self, width, prompt="Enter Text", text='***', color=None, font=None, justify=-1, on_change=None, **kwargs):
        mylabel = LabelWidget(0,0,width*2//5-10,0,prompt,font=font)
        super().__init__(0,0,width,mylabel.h+8,**kwargs)
        self.add_left(mylabel)
        self.my_text_widget = TextEntryWidget(0,0,width*3//5,mylabel.h+8,text,color,font,justify,on_change=on_change,)
        self.add_right(self.my_text_widget)

    def _get_text(self):
        return self.my_text_widget.text

    def _set_text(self, text):
        self.my_text_widget.text = text

    text = property(_get_text, _set_text)

    def quietly_set_text(self, text):
        # Set the text without calling on_change.
        self.my_text_widget.quietly_set_text(text)


class ColDropdownWidget(RowWidget):
    def __init__(self, width, prompt="Choose Option", font=None, justify=-1, on_select=None, **kwargs):
        mylabel = LabelWidget(0,0,width*2//5-10,0,prompt,font=font)
        super().__init__(0,0,width,mylabel.h+8,**kwargs)
        self.add_left(mylabel)
        self.my_menu_widget = DropdownWidget(0,0,width*3//5,mylabel.h+8, font=font, justify=justify, on_select=on_select)
        self.add_right(self.my_menu_widget)

    def add_item(self,msg,value,desc=None):
        self.my_menu_widget.add_item(msg,value,desc)

    @property
    def value(self):
        return self.my_menu_widget.value
