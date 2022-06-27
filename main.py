import pbge
import game
import pygame
import os
import gears
import random
import sys
# import timeit
import glob
import pickle
import copy

VERSION = "v0.830"


class TitleScreenRedraw(object):
    TITLE_DEST = pbge.frects.Frect(-325, -175, 650, 100)
    MENU_DEST = pbge.frects.Frect(-150, 0, 300, 254)

    def __init__(self):
        self.title = pbge.image.Image("sys_maintitle.png")
        self.sky = pbge.image.Image("sys_dzd_ts_skyburn.png")
        self.rubble = pbge.image.Image("sys_dzd_ts_rubble.png")
        self.mecha = pbge.image.Image("sys_dzd_ts_dielancer.png")
        self.cameo = pbge.image.Image("sys_silhouette.png")
        self.cameo_pos = (random.randint(-400, 400), random.randint(-300, 50))
        self.mecha_x = 600
        self.sky_x = 0
        self.rubble_x = 0

    def __call__(self, draw_title=True):
        pbge.my_state.screen.fill((0, 0, 0))

        w, h = pbge.my_state.screen.get_size()
        bigrect = pygame.Rect(0, (h - 600) // 2, w, 600)
        rubblerect = pygame.Rect(0, (h - 600) // 2 + 600 - self.rubble.frame_height, w, self.rubble.frame_height)

        self.sky.tile(bigrect, x_offset=self.sky_x)
        self.sky_x += 1
        if self.sky_x >= self.sky.frame_width:
            self.sky_x = 0

        self.cameo.render((w // 2 + self.cameo_pos[0], h // 2 + self.cameo_pos[1]))

        self.rubble.tile(rubblerect, x_offset=self.rubble_x)
        self.rubble_x += 2
        if self.rubble_x >= self.rubble.frame_width:
            self.rubble_x = 0

        self.mecha.render((self.mecha_x, (h - 600) // 2))
        self.mecha_x -= 1
        if self.mecha_x < -self.mecha.frame_width:
            self.mecha_x = w

        if draw_title:
            self.title.render(self.TITLE_DEST.get_rect())

            versid = pbge.render_text(pbge.my_state.medium_font, VERSION, 120, justify=1)
            pbge.my_state.screen.blit(versid, versid.get_rect(
                bottomright=(pbge.my_state.screen.get_width() - 8, pbge.my_state.screen.get_height() - 8)))


TITLE_THEME = 'A wintertale.ogg'


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
            egg = copy.deepcopy(pickle.load(f))
        if egg:
            mymenu.add_item(str(egg.pc), egg)

    if not mymenu.items:
        mymenu.add_item('[No characters found]', None)

    mymenu.sort()
    egg = mymenu.query()
    if egg:
        if not pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
            egg.backup()
            os.remove(pbge.util.user_dir("egg_{}.sav".format(egg.pc.name)))

        game.start_campaign(egg, tsrd)


def load_game(tsrd):
    myfiles = glob.glob(pbge.util.user_dir("rpg_*.sav"))
    mymenu = pbge.rpgmenu.Menu(TitleScreenRedraw.MENU_DEST.dx,
                               TitleScreenRedraw.MENU_DEST.dy,
                               TitleScreenRedraw.MENU_DEST.w, TitleScreenRedraw.MENU_DEST.h,
                               predraw=tsrd, font=pbge.my_state.huge_font
                               )

    for fname in myfiles:
        # with open(fname, "rb") as f:
        #    # See note above for why the deepcopy is here. TLDR: keeping pickles fresh and delicious.
        #    camp = copy.deepcopy(cPickle.load(f))
        start_index = fname.find("rpg_")
        mymenu.add_item(fname[start_index + 4:-4], fname)

    if not mymenu.items:
        mymenu.add_item('[No campaigns found]', None)

    mymenu.sort()
    fname = mymenu.query()
    if fname:
        pbge.please_stand_by()
        with open(fname, "rb") as f:
            # See note above for why the deepcopy is here. TLDR: keeping pickles fresh and delicious.
            camp = copy.deepcopy(pickle.load(f))
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
        egg = mygears.get_egg()
        mymenu.add_item(str(egg.pc), egg)
    mymenu.sort()

    if not mymenu.items:
        mymenu.add_item('[No GH1 characters found]', None)

    myegg = mymenu.query()
    if myegg:
        myegg.save()
        pbge.BasicNotification("{} has been imported.".format(myegg.pc.name))


def open_config_menu(tsrd):
    myconfigmenu = game.configedit.ConfigEditor(tsrd, dy=0)
    myconfigmenu()


def open_cosplay_menu(tsrd):
    game.cosplay.ColorEditor.explo_invoke(tsrd)


def open_chargen_menu(tsrd):
    game.chargen.CharacterGeneratorW.create_and_invoke(tsrd)


def just_show_background(tsrd):
    while True:
        ev = pbge.wait_event()
        if ev.type == pbge.TIMEREVENT:
            tsrd(False)
            pbge.my_state.do_flip()
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            break


def play_the_game():
    # Step one is to find our gamedir. The process is slightly different depending on whether we are running from
    # source, running from a PyInstaller build, or running from a cx_Freeze build.
    if getattr(sys, "_MEIPASS", False):
        # PyInstaller build.
        gamedir = sys._MEIPASS
    elif getattr(sys, "frozen", False):
        # cx_Freeze build.
        gamedir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        gamedir = os.path.dirname(__file__)

    pbge.init('GearHead Caramel', 'ghcaramel', gamedir, poster_pattern='eyecatch_*.png')
    pbge.please_stand_by()
    gears.init_gears()
    game.init_game()

    # myfoo = game.content.ghplots.test.Foo()
    # with open(pbge.util.user_dir('bar.p'), "wb") as f:
    #    pickle.dump(myfoo, f, -1)
    # with open(pbge.util.user_dir('bar.p'), "rb") as f:
    #    foo2 = pickle.load(f)

    # print timeit.timeit("""mypic = pbge.image.Image('mecha_buruburu.png',color=(gears.color.ArmyDrab,gears.color.ShiningWhite,gears.color.ElectricYellow,gears.color.GullGrey,gears.color.Terracotta),flags=pygame.RLEACCELOK)""",setup='import pygame, pbge, gears',number=10)
    # print timeit.timeit("""mypic = pbge.image.Image('mecha_buruburu.png',color=(gears.color.ArmyDrab,gears.color.ShiningWhite,gears.color.ElectricYellow,gears.color.GullGrey,gears.color.Terracotta))""",setup='import pbge, gears',number=10)

    # fname = "mecha_vadel.png"
    # mypic = pbge.image.Image(fname, color=(gears.color.GunRed, gears.color.Gold, gears.color.Aquamarine, gears.color.Cobalt, gears.color.Turquoise))
    # mydest = pygame.Surface((mypic.frame_width, mypic.frame_height))
    # mydest.fill((0, 0, 25))
    # mypic.render((0,0),dest_surface=mydest)
    # pygame.image.save(mydest, pbge.util.user_dir("out_"+fname))

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
    mymenu.add_item("Browse Mecha", game.mechabrowser.MechaBrowser())
    mymenu.add_item("Edit Mecha", game.geareditor.LetsEditSomeMeks)
    mymenu.add_item("Edit Scenario", game.scenariocreator.start_plot_creator)
    if pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
        mymenu.add_item("Compile Plot Bricks", game.scenariocreator.PlotBrickCompiler)
        mymenu.add_item("Eggzamination", game.devstuff.Eggzaminer)
        mymenu.add_item("Just Show Background", just_show_background)
    mymenu.add_item("Quit", None)

    action = True
    while action:
        pbge.my_state.start_music(TITLE_THEME)
        action = mymenu.query()
        if action:
            action(tsrd)


if __name__ == "__main__":
    play_the_game()
    pygame.quit()
    # Been getting some problems with the program continuing to run sometimes after pygame.quit().
    # StackExchange suggested the following... I figure it couldn't hurt.
    sys.exit()
