from pbge import widgets, image, my_state, default_border
import pygame


class Memo(object):
    def __init__(self, text, location=None):
        self._text = text
        self._location = location

    def __str__(self):
        if not self._location:
            return self._text
        if hasattr(self._location, 'get_root_scene'):
            root = self._location.get_root_scene()
            if root is not self._location:
                loc = "{} at {}".format(self._location, root)
            else:
                loc = str(self._location)
        else:
            loc = str(self._location)
        return "{}\n\nLocation: {}".format(self._text, loc)


class MemoBrowser(widgets.Widget):
    # Memos are held as the memo property of active Plots.
    # A memo can be any of the following:
    # - A string of text
    # - An object that has a defined str() value
    # - An object that has a get_widget(MemoBrowser, campaign) method which returns a widget
    DEFAULT_WIDTH = 400
    TAGS_TO_DEACTIVATE = {widgets.WTAG_WIDGET,}
    def __init__(self, camp):
        super().__init__(-200, -200, self.DEFAULT_WIDTH, 200)
        self.camp = camp
        self.memos = camp.get_memos()
        if not self.memos:
            self.memos = ["<<No memos.>>"]
        self._memo_n = 0
        self.memo_widget = None
        self.memo_n = 0
        bfbuttonsprite = image.Image('sys_bfarrows.png', 80, 32)
        self.prev_button = widgets.ButtonWidget(-200, 116, 80, 32, bfbuttonsprite, 0, on_click=self.prev_memo, parent=self)
        self.next_button = widgets.ButtonWidget(120, 116, 80, 32, bfbuttonsprite, 1, on_click=self.next_memo, parent=self)
        closebuttonsprite = image.Image('sys_closeicon.png', 13, 14)
        self.close_button = widgets.ButtonWidget(200, -112, 13, 14, closebuttonsprite, 0, on_click=self.close_browser, parent=self)
        self.children.append(self.prev_button)
        self.children.append(self.next_button)
        self.children.append(self.close_button)

    def _set_memo_n(self, new_value):
        if new_value < 0:
            new_value = len(self.memos) - 1
        elif new_value >= len(self.memos):
            new_value = 0
        self._memo_n = new_value
        if self.memo_widget:
            self.children.remove(self.memo_widget)
        if hasattr(self.memos[self._memo_n], "get_widget"):
            self.memo_widget = self.memos[self._memo_n].get_widget(self, self.camp)
        else:
            self.memo_widget = widgets.LabelWidget(self.dx, self.dy, self.w, self.h, text=str(self.memos[self._memo_n]),
                                                   justify=0, font=my_state.medium_font)
        self.children.append(self.memo_widget)

    def regen_memo(self):
        self.memo_n = self.memo_n

    def on_activate(self):
        self.regen_memo()

    def _get_memo_n(self):
        return self._memo_n

    memo_n = property(_get_memo_n, _set_memo_n)

    def _render(self, delta):
        myrect = self.get_rect()
        default_border.render(myrect)

    def close_browser(self, _wid, _ev):
        self.pop()

    def prev_memo(self,  _wid=None, _ev=None):
        self.memo_n -= 1

    def next_memo(self,  _wid=None, _ev=None):
        self.memo_n += 1

    def _builtin_responder(self, ev):
        # gdi is a pygame event.
        if ev.type == pygame.KEYDOWN:
            if my_state.is_key_for_action(ev, "left"):
                self.register_response()
                self.prev_memo()
            elif my_state.is_key_for_action(ev, "right"):
                self.register_response()
                self.next_memo()
            elif my_state.is_key_for_action(ev, "exit"):
                self.register_response()
                self.pop()
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 3:
            self.register_response()
            self.pop()

