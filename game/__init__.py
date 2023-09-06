from . import exploration
from . import combat
from . import teams
from . import content
from . import ghdialogue
from . import configedit
from . import invoker
from . import cosplay
from . import chargen
from . import services
from . import fieldhq
from . import mechabrowser
from . import geareditor
from . import devstuff
from . import scenariocreator
from . import traildrawer
from game.fieldhq import backpack
import pbge
import os


class AdventureMenu(object):
    LEFT_COLUMN = pbge.frects.Frect(-300, -250,280,500)
    RIGHT_COLUMN = pbge.frects.Frect(20,-100,280,350)
    TEXT_AREA = pbge.frects.Frect(20,-250,280,110)

    def __init__(self, egg, redrawer):
        self.egg = egg
        self.redrawer = redrawer
        self.posters = dict()

    def adventure_desc(self, menu_item):
        item = menu_item.value
        if item:
            myrect = self.LEFT_COLUMN.get_rect()
            pbge.default_border.render(myrect)
            if item.ADVENTURE_MODULE_DATA.title_card:
                if item not in self.posters:
                    self.posters[item] = pbge.image.Image(item.ADVENTURE_MODULE_DATA.title_card)
                self.posters[item].render((myrect.x,myrect.y))
            if menu_item.desc:
                myrect = self.TEXT_AREA.get_rect()
                pbge.default_border.render(myrect)
                pbge.draw_text(pbge.MEDIUMFONT, menu_item.desc, myrect)

    def __call__(self):
        mymenu = pbge.rpgmenu.Menu(
            self.RIGHT_COLUMN.dx,
            self.RIGHT_COLUMN.dy,
            self.RIGHT_COLUMN.w, self.RIGHT_COLUMN.h,
            font=pbge.my_state.huge_font, predraw=self.redrawer, padding=16
        )
        mymenu.descobj = self.adventure_desc

        for p in content.ghplots.UNSORTED_PLOT_LIST:
            if hasattr(p, "ADVENTURE_MODULE_DATA") and p.ADVENTURE_MODULE_DATA.can_play(self.egg):
                mymenu.add_item(
                    p.ADVENTURE_MODULE_DATA.name, p,
                    'NT{}.{:02}.{:02}: {}'.format(*p.ADVENTURE_MODULE_DATA.date, p.ADVENTURE_MODULE_DATA.desc)
                )
        mymenu.items.sort(key=lambda x: x.value.ADVENTURE_MODULE_DATA.date)

        mymenu.add_item("[Cancel]", None)
        return mymenu.query()


def start_campaign(pc_egg, redrawer, version):
    mymenu = AdventureMenu(pc_egg, redrawer)
    adv_type = mymenu()

    if adv_type:
        pbge.please_stand_by()
        camp = content.narrative_convenience_function(pc_egg,adv_type=adv_type.LABEL)
        if camp:
            camp.version = version
            camp._really_go()
            camp.save()

            if not pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                pc_egg.backup()
                os.remove(pbge.util.user_dir(pbge.util.sanitize_filename("egg_{}.sav".format(pc_egg.pc.name))))

            camp.play()


def init_game():
    content.backstory.init_backstory()
    content.ghplots.init_plots()
    scenariocreator.init_plotcreator()
    configedit.init_configedit()
