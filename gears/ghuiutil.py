# I wanted to keep the gears package clean from UI messiness, but here we are. I guess I already broke that rule with
# the info unit... anyhow, here are some UI things used by GearHead things.

import pbge
import pygame
from . import info

class GearMenuDesc( pbge.widgets.Widget ):
    def __init__(self, dx, dy, w, h, menu: pbge.widgetmenu.MenuWidget, anchor=pbge.frects.ANCHOR_CENTER):
        super().__init__(dx, dy, w, h, anchor=anchor)
        self.library = dict()
        self.menu = menu

    def _render(self, _delta):
        super()._render(_delta)

        mygear = self.menu.current_data
    
        # Just print this weapon's stats in the provided area.
        if mygear not in self.library:
            self.library[mygear] = info.get_longform_display(
                mygear,width=self.w,font=pbge.MEDIUMFONT
            )
        myrect = self.get_rect()
        self.library[mygear].render(myrect.x,myrect.y)

# Data gatherers should have gather(data: dict) and confirm(data: dict) methods.

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

    def gather(self, data):
        mymenu = pbge.widgetmenu.MenuWidget(
            self.RIGHT_COLUMN_X, self.COLUMN_Y, self.COLUMN_WIDTH, self.COLUMN_HEIGHT,
            font=pbge.MEDIUM_DISPLAY_FONT, pop_when_clicked=True, auto_escape=True
        )
        mymenu.set_header(pbge.widgets.LabelWidget(
            0, 0, 200, 0, self.caption, font=pbge.BIGFONT, justify=0, draw_border=True
        ))
        mymenu.children.append(GearMenuDesc(self.LEFT_COLUMN_X, self.COLUMN_Y, self.COLUMN_WIDTH, self.COLUMN_HEIGHT, mymenu))
        mymenu.TAGS_TO_DEACTIVATE = {pbge.widgets.WTAG_WIDGET,}

        for g in self.gear_list:
            _=mymenu.add_item(g.get_full_name(), self._on_click, data=(data, g))

        mymenu.push_and_deploy()

    def confirm(self, data):
        # If the key is present in the data and the value is from the gear list, all is good.
        return self.data_key in data and data[self.data_key] in self.gear_list

    def _on_click(self, wid, _ev):
        data, mygear = wid.data
        data[self.data_key] = mygear


class TextDisplayWidget(pbge.widgetmenu.MenuWidget):
    def __init__(self, text_list):
        super().__init__(-300,-250,600,500, activate_child_on_enter=False)
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

