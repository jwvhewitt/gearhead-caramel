import pbge
import game
import pygame
import os
import gears
import random
import sys
# import timeit
import glob
import cPickle
import copy

VERSION = "v0.130"


class Snowflake(object):
    def __init__(self, dest):
        self.dest = dest
        self.x = dest.left + random.randint(1, dest.w)
        self.y = dest.top - 12
        self.dx = random.randint(1, 6) - random.randint(1, 3)
        self.dy = random.randint(2, 4)
        self.frame = random.randint(0, 24)

    def update(self):
        # Return True if this flake should be deleted.
        self.x += self.dx
        self.y += self.dy
        if self.y > self.dest.bottom:
            return True


class TitleScreenRedraw(object):
    TITLE_DEST = pbge.frects.Frect(-325, -150, 650, 100)
    MENU_DEST = pbge.frects.Frect(-150, 0, 300, 196)

    def __init__(self):
        self.title = pbge.image.Image("sys_wmtitle.png")
        self.bg = pbge.image.Image("poster_snowday.png")
        self.snow = pbge.image.Image("sys_wm_snow.png", 24, 24)
        self.flakes = list()

    def add_snow(self, dest):
        for t in range(min(random.randint(1, 3), random.randint(1, 3))):
            self.flakes.append(Snowflake(dest))

    def __call__(self):
        pbge.my_state.screen.fill((0, 0, 0))
        dest = self.bg.bitmap.get_rect(
            center=(pbge.my_state.screen.get_width() // 2, pbge.my_state.screen.get_height() // 2))
        self.bg.render(dest)

        self.title.render(self.TITLE_DEST.get_rect())

        pbge.my_state.screen.set_clip(dest)
        self.add_snow(dest)
        for sf in list(self.flakes):
            if sf.update():
                self.flakes.remove(sf)
            else:
                self.snow.render((sf.x, sf.y), sf.frame)
        pbge.my_state.screen.set_clip(None)
        versid = pbge.render_text(pbge.my_state.medium_font, VERSION, 120, justify=1)
        pbge.my_state.screen.blit(versid, versid.get_rect(
            bottomright=(pbge.my_state.screen.get_width() - 8, pbge.my_state.screen.get_height() - 8)))


TITLE_THEME = 'Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg'


def start_game(tsrd):
    myfiles = glob.glob(pbge.util.user_dir("egg_*.sav"))
    mymenu = pbge.rpgmenu.Menu(TitleScreenRedraw.MENU_DEST.dx,
                               TitleScreenRedraw.MENU_DEST.dy,
                               TitleScreenRedraw.MENU_DEST.w, TitleScreenRedraw.MENU_DEST.h,
                               predraw=tsrd, font=pbge.my_state.huge_font
                               )

    for fname in myfiles:
        with open(fname, "rb") as f:
            # Why deepcopy the freshly loaded pickle? Because that will update any gears involved
            # to the latest version, and at this point in time it'll hopefully keep save games working
            # despite rapid early-development changes.
            egg = copy.deepcopy(cPickle.load(f))
        if egg:
            mymenu.add_item(str(egg.pc), egg)

    if not mymenu.items:
        mymenu.add_item('[No characters found]', None)

    egg = mymenu.query()
    if egg:
        if not pbge.util.config.getboolean( "GENERAL", "dev_mode_on" ):
            egg.backup()
            os.remove(pbge.util.user_dir("egg_{}.sav".format(egg.pc.name)))

        game.start_campaign(egg)

def load_game(tsrd):
    myfiles = glob.glob(pbge.util.user_dir("rpg_*.sav"))
    mymenu = pbge.rpgmenu.Menu(TitleScreenRedraw.MENU_DEST.dx,
                               TitleScreenRedraw.MENU_DEST.dy,
                               TitleScreenRedraw.MENU_DEST.w, TitleScreenRedraw.MENU_DEST.h,
                               predraw=tsrd, font=pbge.BIGFONT
                               )

    for fname in myfiles:
        with open(fname, "rb") as f:
            # See note above for why the deepcopy is here. TLDR: keeping pickles fresh and delicious.
            camp = copy.deepcopy(cPickle.load(f))
        if camp:
            mymenu.add_item(str(camp.pc), camp)

    if not mymenu.items:
        mymenu.add_item('[No campaigns found]', None)

    camp = mymenu.query()
    if camp:
        camp.play()


def import_arena_character(tsrd):
    myfiles = gears.oldghloader.GH1Loader.seek_gh1_files()
    mymenu = pbge.rpgmenu.Menu(TitleScreenRedraw.MENU_DEST.dx,
                               TitleScreenRedraw.MENU_DEST.dy,
                               TitleScreenRedraw.MENU_DEST.w, TitleScreenRedraw.MENU_DEST.h,
                               predraw=tsrd, font=pbge.my_state.huge_font
                               )

    for f in myfiles:
        mygears = gears.oldghloader.GH1Loader(f)
        mygears.load()
        rpc = mygears.find_pc()
        pc = mygears.convert_character(rpc)
        egg = mygears.get_egg()
        mymenu.add_item(str(pc), egg)
    mymenu.sort()

    if not mymenu.items:
        mymenu.add_item('[No GH1 characters found]', None)

    egg = mymenu.query()
    if egg:
        # pc.imagename = 'cha_wm_parka.png'
        game.start_campaign(egg)


def open_config_menu(tsrd):
    myconfigmenu = game.configedit.ConfigEditor(tsrd, dy=0)
    myconfigmenu()


def open_cosplay_menu(tsrd):
    game.cosplay.ColorEditor.explo_invoke(tsrd)


def open_chargen_menu(tsrd):
    game.chargen.CharacterGeneratorW.create_and_invoke(tsrd)


def play_the_game():
    try:
        # running in a bundle
        gamedir = sys._MEIPASS
    except Exception:
        # running live
        gamedir = os.path.dirname(__file__)
    # print '"'+gamedir+'"'
    pbge.init('GearHead Caramel', 'ghcaramel', gamedir, poster_pattern='eyecatch_*.png')
    pbge.please_stand_by()
    gears.init_gears()
    game.content.backstory.init_backstory()

    # print timeit.timeit("""mypic = pbge.image.Image('mecha_buruburu.png',color=(gears.color.ArmyDrab,gears.color.ShiningWhite,gears.color.ElectricYellow,gears.color.GullGrey,gears.color.Terracotta),flags=pygame.RLEACCELOK)""",setup='import pygame, pbge, gears',number=10)
    # print timeit.timeit("""mypic = pbge.image.Image('mecha_buruburu.png',color=(gears.color.ArmyDrab,gears.color.ShiningWhite,gears.color.ElectricYellow,gears.color.GullGrey,gears.color.Terracotta))""",setup='import pbge, gears',number=10)

    #mypic = pbge.image.Image('SHD_22C_Dielancer.png',color=list(gears.factions.BladesOfCrihna.mecha_colors))
    #mydest = pygame.Surface((mypic.frame_width, mypic.frame_height))
    #mydest.fill((0, 0, 255))
    #mypic.render((0,0),dest_surface=mydest)
    #pygame.image.save(mydest, pbge.util.user_dir("out.png"))

    # mypor = gears.portraits.Portrait()
    # mypor.bits = ["FBA NoBody","Haywire B3 Head"]
    # mypic = mypor.build_portrait(None,False,True)
    # pygame.image.save(mypic.bitmap, pbge.util.user_dir("out.png"))

    tsrd = TitleScreenRedraw()
    mymenu = pbge.rpgmenu.Menu(TitleScreenRedraw.MENU_DEST.dx,
                               TitleScreenRedraw.MENU_DEST.dy,
                               TitleScreenRedraw.MENU_DEST.w, TitleScreenRedraw.MENU_DEST.h,
                               predraw=tsrd, font=pbge.my_state.huge_font
                               )

    mymenu.add_item("Load Campaign", load_game)
    mymenu.add_item("Start Campaign", start_game)
    mymenu.add_item("Create Character", open_chargen_menu)
    mymenu.add_item("Import GH1 Character", import_arena_character)
    mymenu.add_item("Config Options", open_config_menu)
    mymenu.add_item("Cosplay Color Menu", open_cosplay_menu)
    mymenu.add_item("Quit", None)

    action = True
    while action:
        pbge.my_state.start_music(TITLE_THEME)
        action = mymenu.query()
        if action:
            action(tsrd)


if __name__ == "__main__":
    # clay = gears.Loader.load_design_file('Trailblazer.txt')
    # for item in clay:
    #    item.termdump()
    # clay[0].statusdump()

    play_the_game()
    pygame.quit()
