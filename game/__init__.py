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
from . import scenariocreator
from . import traildrawer
from game.fieldhq import backpack
import pbge
import os


class StartCampaignWidget(pbge.widgetmenu.MenuWidget):
    LEFT_COLUMN = pbge.frects.Frect(-300, -250,280,500)
    RIGHT_COLUMN = pbge.frects.Frect(20,-100,280,350)
    TEXT_AREA = pbge.frects.Frect(20,-250,280,110)

    TAGS_TO_HIDE = {pbge.widgets.WTAG_TITLEMENU,}
    ACTIVATE_IMMEDIATELY = True

    def __init__(self, egg, version):
        super().__init__(
            self.RIGHT_COLUMN.dx, self.RIGHT_COLUMN.dy, self.RIGHT_COLUMN.w, self.RIGHT_COLUMN.h,
            font=pbge.my_state.huge_font,
            on_escape=self._cancel
        )
        self.egg = egg
        self.version = version
        self.posters = dict()
        self.build_menu()

    def _render(self, delta):
        item = self.current_data
        desc = self.current_desc
        if item:
            myrect = self.LEFT_COLUMN.get_rect()
            pbge.default_border.render(myrect)
            if item.ADVENTURE_MODULE_DATA.title_card:
                if item not in self.posters:
                    self.posters[item] = pbge.image.Image(item.ADVENTURE_MODULE_DATA.title_card)
                self.posters[item].render((myrect.x,myrect.y))
            if desc:
                myrect = self.TEXT_AREA.get_rect()
                pbge.default_border.render(myrect)
                pbge.draw_text(pbge.MEDIUMFONT, desc, myrect)
        super()._render(delta)

    def build_menu(self):
        print(self.egg.past_adventures)
        for p in content.UNSORTED_PLOT_LIST:
            if hasattr(p, "ADVENTURE_MODULE_DATA") and p.ADVENTURE_MODULE_DATA.can_play(self.egg):
                _=self.add_item(
                    p.ADVENTURE_MODULE_DATA.name, on_click=self.click_your_own_adventure, data=p,
                    desc='NT{}.{:02}.{:02}: {}'.format(*p.ADVENTURE_MODULE_DATA.date, p.ADVENTURE_MODULE_DATA.desc)
                )
        self.sort(key=lambda x: x.data.ADVENTURE_MODULE_DATA.date)

        _=self.add_item("[Cancel]", on_click=self._cancel, data=None)

    def _cancel(self, _wid, _ev):
        self.pop()

    def click_your_own_adventure(self, wid, _ev):
        adv_type = wid.data
        if adv_type:
            self.pop()
            pbge.please_stand_by()
            cd = content.narrative_convenience_function(self.egg,adv_type=adv_type.LABEL)
            if cd:
                camp, dest = cd
                camp.version = self.version
                #camp._really_go()
                camp.save()

                if not pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                    self.egg.backup()
                    os.remove(pbge.util.user_dir(pbge.util.sanitize_filename("egg_{}.sav".format(self.egg.pc.name))))

                camp.play(dest_wp=dest)


PRELOAD_IMAGES = list()

def init_game():
    content.backstory.init_backstory()
    content.ghplots.init_plots()
    scenariocreator.init_plotcreator()
    configedit.init_configedit()
    chargen.lifepath.init_lifepath()
    PRELOAD_IMAGES.append(pbge.image.Image("sys_powerindicator.png"))
    PRELOAD_IMAGES.append(pbge.image.Image("sys_armormobility.png"))
    PRELOAD_IMAGES.append(pbge.image.Image("sys_modules.png"))

