import pbge
import gears
import pygame
import copy
import random

class MSRPBlock(object):
    def __init__(self, model, width=360, **kwargs):
        self.model = model
        self.width = width
        self.image = pbge.render_text(pbge.BIGFONT, "${:,}".format(model.cost), width,
                                      justify=0, color=pbge.TEXT_COLOR)
        self.height = self.image.get_height()

    def render(self, x, y):
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class MechaBrowseIP(gears.info.InfoPanel):
    # A floating status display, drawn wherever the mouse is pointing.
    DEFAULT_BLOCKS = (gears.info.FullNameBlock, MSRPBlock, gears.info.MechaFeaturesAndSpriteBlock, gears.info.DescBlock)


class BrowserDesc(object):
    # This is a DescObj for the browser menu.
    ITEM_INFO_AREA = pbge.frects.Frect(-350, -150, 325, 300)

    def __init__(self):
        self.info_cache = dict()

    def get_browse_info(self, item):
        if item in self.info_cache:
            return self.info_cache[item]
        else:
            it = MechaBrowseIP(model=item, width=self.ITEM_INFO_AREA.w)
        self.info_cache[item] = it
        return it

    def __call__(self, menuitem):
        mydest = self.ITEM_INFO_AREA.get_rect()
        item = menuitem.value
        if item:
            myinfo = self.get_browse_info(item)
            if myinfo:
                myinfo.render(mydest.x, mydest.y)


class MechaBrowser(object):
    MENU_AREA = pbge.frects.Frect(0, -200, 350, 400)

    def __init__(self):
        self.mek_list = list()
        for mek in gears.selector.DESIGN_LIST:
            if isinstance(mek,gears.base.Mecha):
                numek = copy.deepcopy(mek)
                if not numek.colors:
                    possible_colors = [f.mecha_colors for f in numek.faction_list if f and hasattr(f,"mecha_colors") and f.mecha_colors]
                    if possible_colors:
                        numek.colors = random.choice(possible_colors)
                    else:
                        numek.colors = gears.color.random_mecha_colors()
                self.mek_list.append(numek)

    def __call__(self, predraw):
        mymenu = pbge.rpgmenu.Menu(self.MENU_AREA.dx, self.MENU_AREA.dy, self.MENU_AREA.w, self.MENU_AREA.h,
                                   font=pbge.BIGFONT, predraw=predraw)
        mymenu.descobj = BrowserDesc()

        for mek in self.mek_list:
            mymenu.add_item(mek.get_full_name(),mek)
        mymenu.sort()
        mymenu.add_item("[exit]", None)

        while mymenu.query():
            pass

