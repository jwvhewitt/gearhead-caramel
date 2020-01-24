import pbge
import pygame

class MemoBrowser(object):
    def __init__(self,camp):
        self.camp = camp
        self.text_area = pbge.frects.Frect(-200,-100,400,200)
        self.memos = [p.memo for p in camp.active_plots() if p.memo]
        if not self.memos:
            self.memos = ["<<No memos.>>"]
        self.memo_n = 0
        self.keep_browsing = True
        bfbuttonsprite = pbge.image.Image('sys_bfarrows.png',80,32)
        self.prev_button = pbge.widgets.ButtonWidget(-200,116,80,32,bfbuttonsprite,0,on_click=self.prev_memo)
        self.next_button = pbge.widgets.ButtonWidget(120,116,80,32,bfbuttonsprite,1,on_click=self.next_memo)
        closebuttonsprite = pbge.image.Image('sys_closeicon.png',13,14)
        self.close_button = pbge.widgets.ButtonWidget(200,-112,13,14,closebuttonsprite,0,on_click=self.close_browser)

    def render( self ):
        pbge.my_state.view()
        myrect = self.text_area.get_rect()
        pbge.default_border.render(myrect)
        pbge.draw_text(pbge.my_state.medium_font,self.memos[self.memo_n],myrect)

    def close_browser(self,button=None,ev=None):
        self.keep_browsing = False

    def prev_memo(self,button=None,ev=None):
        self.memo_n -= 1
        if self.memo_n < 0:
            self.memo_n = len(self.memos)-1

    def next_memo(self,button=None,ev=None):
        self.memo_n += 1
        if self.memo_n >= len(self.memos):
            self.memo_n = 0

    def update(self,ev):
        # gdi is a pygame event.
        if ev.type == pbge.TIMEREVENT:
            self.render()
            pbge.my_state.do_flip()
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_LEFT:
                self.prev_memo()
            elif ev.key == pygame.K_ESCAPE:
                self.keep_browsing = False

    def activate(self):
        pbge.my_state.widgets += [self.prev_button,self.next_button,self.close_button]

    def deactivate(self):
        pbge.my_state.widgets.remove(self.prev_button)
        pbge.my_state.widgets.remove(self.next_button)
        pbge.my_state.widgets.remove(self.close_button)

    def __call__(self):
        self.activate()
        while self.keep_browsing:
            gdi = pbge.wait_event()
            self.update(gdi)
        self.deactivate()

    @classmethod
    def browse(self, camp):
        # Run the UI. Return a DoInvocation action if an invocation
        # was chosen, or None if the invocation was cancelled.
        myui = self(camp)
        myui()
