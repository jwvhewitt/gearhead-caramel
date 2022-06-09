from pbge import widgets, image, my_state, default_border, TIMEREVENT, wait_event
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
    def __init__(self, camp):
        super().__init__(-200, -200, 400, 200)
        self.camp = camp
        self.memos = camp.get_memos()
        if not self.memos:
            self.memos = ["<<No memos.>>"]
        self._memo_n = 0
        self.memo_widget = None
        self.memo_n = 0
        self.keep_browsing = True
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
                                                   justify=0)
        self.children.append(self.memo_widget)

    def _get_memo_n(self):
        return self._memo_n

    memo_n = property(_get_memo_n, _set_memo_n)

    def render(self, flash=False):
        myrect = self.get_rect()
        default_border.render(myrect)

    def close_browser(self, button=None, ev=None):
        self.keep_browsing = False
        my_state.widgets.remove(self)

    def prev_memo(self, button=None, ev=None):
        self.memo_n -= 1

    def next_memo(self, button=None, ev=None):
        self.memo_n += 1

    def _builtin_responder(self, ev):
        # gdi is a pygame event.
        if ev.type == pygame.KEYDOWN:
            if ev.key in my_state.get_keys_for("left"):
                self.prev_memo()
            elif ev.key in my_state.get_keys_for("right"):
                self.next_memo()
            elif ev.key == pygame.K_ESCAPE:
                self.keep_browsing = False

    def activate(self):
        my_state.widgets.append(self)

    def __call__(self):
        # Run the UI. Clean up after you leave.
        self.activate()
        while self.keep_browsing and not my_state.got_quit:
            ev = wait_event()
            if ev.type == TIMEREVENT:
                my_state.render_and_flip()

        if self in my_state.widgets:
            my_state.widgets.remove(self)
