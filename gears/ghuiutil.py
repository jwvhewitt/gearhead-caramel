# I wanted to keep the gears package clean from UI messiness, but here we are. I guess I already broke that rule with
# the info unit... anyhow, here are some UI things used by GearHead things.

import pbge
import pygame
from . import info

class GearMenuDesc( pbge.frects.Frect ):
    def __init__(self, dx, dy, w, h, anchor=pbge.frects.ANCHOR_CENTER):
        super().__init__(dx, dy, w, h, anchor=anchor)
        self.library = dict()

    def __call__( self, menu_item ):
        # Just print this weapon's stats in the provided window.
        if menu_item.value not in self.library:
            self.library[menu_item.value] = info.get_longform_display(
                menu_item.value,width=self.w,font=pbge.MEDIUMFONT
            )
        myrect = self.get_rect()
        self.library[menu_item.value].render(myrect.x,myrect.y)


class SelectGearDataGatherer:
    COLUMN_WIDTH = 220
    PADDING = 32
    LEFT_COLUMN_X = -COLUMN_WIDTH - PADDING//2
    RIGHT_COLUMN_X = PADDING//2
    COLUMN_Y = -150
    COLUMN_HEIGHT = 300
    CAPTION_HEIGHT = 24
    CAPTION_WIDTH = COLUMN_WIDTH + PADDING * 2
    CAPTION_X = -CAPTION_WIDTH//2
    CAPTION_Y = COLUMN_Y - PADDING - CAPTION_HEIGHT

    LEFT_COLUMN = pbge.frects.Frect(LEFT_COLUMN_X, COLUMN_Y, COLUMN_WIDTH, COLUMN_HEIGHT)
    RIGHT_COLUMN = pbge.frects.Frect(RIGHT_COLUMN_X, COLUMN_Y, COLUMN_WIDTH, COLUMN_HEIGHT)
    CAPTION_AREA = pbge.frects.Frect(CAPTION_X, CAPTION_Y, CAPTION_WIDTH, CAPTION_HEIGHT)

    def __init__(self, gear_list, caption, data_key="gear"):
        self.gear_list = gear_list
        self.caption = caption
        self.data_key = data_key

    def render(self):
        pbge.my_state.view()
        myrect = self.CAPTION_AREA.get_rect()
        pbge.default_border.render(myrect)
        pbge.draw_text(
            pbge.BIGFONT, self.caption, myrect, color=pbge.WHITE, justify=0, vjustify=0
        )

    def __call__(self, data):
        mymenu = pbge.rpgmenu.Menu(
            self.RIGHT_COLUMN_X, self.COLUMN_Y, self.COLUMN_WIDTH, self.COLUMN_HEIGHT,
            border=pbge.default_border, predraw=self.render, font=pbge.MEDIUM_DISPLAY_FONT
        )
        mymenu.descobj = GearMenuDesc(self.LEFT_COLUMN_X, self.COLUMN_Y, self.COLUMN_WIDTH, self.COLUMN_HEIGHT)

        for g in self.gear_list:
            mymenu.add_item(g.get_full_name(), g)

        data_val = mymenu.query()
        data[self.data_key] = data_val
        return data_val


class TextDisplayWidget(pbge.widgetmenu.MenuWidget):
    def __init__(self, text_list):
        super().__init__(-300,-250,600,500)
        self.text_list = text_list

        for text in self.text_list:
            for line in pbge.wrap_multi_line(text, pbge.MEDIUMFONT, self.w):
                s = pbge.MEDIUMFONT.render(line, color=pbge.INFO_GREEN)
                s.set_colorkey((0,0,0), pygame.RLEACCEL)
                self.add_interior(pbge.widgets.SurfaceWidget(
                    0, 0, s
                ))
            self.add_interior(pbge.widgets.Widget(0,0,self.w,8))
        self.active_index = len(self._interior_widgets)-1

    @classmethod
    def create_and_invoke(cls, text_list=None, redraw=None):
        # Run the UI. Return a DoInvocation action if an invocation
        # was chosen, or None if the invocation was cancelled.
        if not text_list:
            text_list = pbge.my_state.message_log
        myui = cls(text_list)
        pbge.my_state.widgets.append(myui)
        keepgoing = True
        while keepgoing:
            ev = pbge.wait_event()
            if ev.type == pbge.TIMEREVENT:
                if redraw:
                    redraw()
                else:
                    pbge.my_state.view()
                pbge.my_state.do_flip()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    keepgoing = False

        pbge.my_state.widgets.remove(myui)
