# nuitka-project: --output-filename=ghcaramel
# nuitka-project: --mode=onefile
# nuitka-project: --follow-imports
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/data=data
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/design=design
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/image=image
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/music=music
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/soundfx=soundfx
# nuitka-project: --include-package=pygame
# nuitka-project: --include-package=numpy
# nuitka-project: --include-package=yapf
# nuitka-project: --include-package=caramel-recolor-cython
# nuitka-project: --nofollow-import-to=setuptools
# nuitka-project: --nofollow-import-to=Cython


import pbge
import sys
import os

# Step one is to find our gamedir. The process is slightly different depending on whether we are running from
# source, running from a PyInstaller build, or running from a cx_Freeze build.
if getattr(sys, "_MEIPASS", False):
    # PyInstaller build.
    gamedir = sys._MEIPASS
    neargamedir = os.path.dirname(sys.argv[0])
elif getattr(sys, "frozen", False):
    # cx_Freeze build.
    gamedir = os.path.dirname(sys.executable)
    neargamedir = gamedir
else:
    # The application is not frozen
    gamedir = os.path.dirname(__file__)
    #neargamedir = gamedir
    neargamedir = os.path.dirname(sys.argv[0])

print(gamedir)
print(neargamedir)

pbge.init('GearHead Caramel', 'ghcaramel', gamedir, poster_pattern='eyecatch_*.png')
pbge.please_stand_by()

import game
import pygame
import gears
import random
# import timeit
import glob
import pickle
import copy
import math
import logging
import traceback

VERSION = "v0.976"

class DZDTitleScreenRedraw(object):

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
        self.sl = pbge.StretchyLayer()

    def __call__(self, draw_title=True):
        pbge.my_state.screen.fill((0, 0, 0))
        self.sl.clear()

        w, h = self.sl.get_size()
        bigrect = pygame.Rect(0, 0, w, h)
        rubblerect = pygame.Rect(0, h - self.rubble.frame_height, w, self.rubble.frame_height)

        self.sky.tile(bigrect, x_offset=self.sky_x, dest_surface=self.sl.surf)
        self.sky_x += 1
        if self.sky_x >= self.sky.frame_width:
            self.sky_x = 0

        self.cameo.render((w // 2 + self.cameo_pos[0], h // 2 + self.cameo_pos[1]), dest_surface=self.sl.surf)

        self.rubble.tile(rubblerect, x_offset=self.rubble_x, dest_surface=self.sl.surf)
        self.rubble_x += 2
        if self.rubble_x >= self.rubble.frame_width:
            self.rubble_x = 0

        self.mecha.render((self.mecha_x, (h - 600) // 2), dest_surface=self.sl.surf)
        self.mecha_x -= 1
        if self.mecha_x < -self.mecha.frame_width:
            self.mecha_x = w

        self.sl.render()

        if draw_title:
            self.title.render(self.TITLE_DEST.get_rect())

            versid = pbge.render_text(pbge.my_state.medium_font, VERSION, 120, justify=1)
            pbge.my_state.screen.blit(versid, versid.get_rect(
                bottomright=(pbge.my_state.screen.get_width() - 8, pbge.my_state.screen.get_height() - 8)))


TITLE_THEME = 'A wintertale.ogg'


class StartGameMenu:
    MENU_COLUMN = pbge.frects.Frect(20,-100,280,350)

    def __init__(self, tsrd):
        self.tsrd = tsrd
        self.menu = pbge.rpgmenu.Menu(self.MENU_COLUMN.dx, self.MENU_COLUMN.dy,
                                   self.MENU_COLUMN.w, self.MENU_COLUMN.h,
                                   predraw=self, font=pbge.my_state.huge_font,
                                   )
        self.myportraits = dict()

        self.sl = pbge.StretchyLayer()

        myfiles = glob.glob(pbge.util.user_dir("egg_*.sav"))

        for fname in myfiles:
            try:
                with open(fname, "rb") as f:
                    # Why deepcopy the freshly loaded pickle? Because that will update any gears involved
                    # to the latest version, and at this point in time it'll hopefully keep save games working
                    # despite rapid early-development changes.
                    egg = copy.deepcopy(pickle.load(f))
            except Exception as e:
                print("Error in {}- {}".format(fname, e))
                egg = None
            if egg:
                self.menu.add_item(str(egg.pc), egg)
                self.myportraits[egg] = egg.pc.get_portrait()

        if not self.menu.items:
            self.menu.add_item('[No characters found]', None)

        self.menu.sort()
        egg = self.menu.query()
        if egg:
            game.start_campaign(egg, tsrd, VERSION)

    def __call__(self):
        self.tsrd()
        menu_item = self.menu.get_current_item()
        if menu_item and menu_item.value:
            self.sl.clear()
            myimage = self.myportraits[menu_item.value]
            portrait_area = pygame.Rect(self.sl.get_width()//2 - 400, 0, 400, 600)
            myimage.render(portrait_area, dest_surface=self.sl.surf)
            self.sl.render()


class TestStartGame:
    PORTRAIT_AREA = pbge.frects.Frect(-400, -300, 400, 600)
    MENU_COLUMN = pbge.frects.Frect(20,-100,280,350)

    def __init__(self, tsrd):
        myfiles = glob.glob(pbge.util.user_dir("egg_*.sav"))
        mystories = list()

        for p in game.content.ghplots.UNSORTED_PLOT_LIST:
            if hasattr(p, "ADVENTURE_MODULE_DATA"):
                mystories.append(p)

        myeggs = list()
        for fname in myfiles:
            with open(fname, "rb") as f:
                # Why deepcopy the freshly loaded pickle? Because that will update any gears involved
                # to the latest version, and at this point in time it'll hopefully keep save games working
                # despite rapid early-development changes.
                myeggs.append(copy.deepcopy(pickle.load(f)))

        for egg in myeggs:
            for story in mystories:
                for t in range(100):
                    game.content.narrative_convenience_function(egg, adv_type=story.LABEL)
                    print("Success: {} in {} generated #{}".format(egg.pc, story.ADVENTURE_MODULE_DATA.name, t))


def prep_eggs_for_steam(tsrd):
    if not pickle.HIGHEST_PROTOCOL > 4:
        pbge.my_state.view = tsrd
        pbge.alert("Can't prep eggs for Steam since the version of GearHead Caramel you're running appears to be the Steam version. You need to do this from a non-Steam build.")
        return

    pbge.please_stand_by()
    myfiles = glob.glob(pbge.util.user_dir("egg_*.sav"))

    for fname in myfiles:
        try:
            with open(fname, "rb") as f:
                # Why deepcopy the freshly loaded pickle? Because that will update any gears involved
                # to the latest version, and at this point in time it'll hopefully keep save games working
                # despite rapid early-development changes.
                egg = copy.deepcopy(pickle.load(f))
            egg.save()
        except Exception as err:
            print(err)

    myfiles = glob.glob(pbge.util.user_dir("rpg_*.sav"))
    for fname in myfiles:
        try:
            args = gears.GearHeadCampaign.load(fname)
            args[-1].save()
        except Exception as err:
            print(err)


class LoadGameMenu:
    PORTRAIT_AREA = pbge.frects.Frect(-400, -300, 400, 600)
    THUMB_AREA = pbge.frects.Frect(-375, -180, 480, 360)
    MENU_COLUMN = pbge.frects.Frect(130,-100,225,350)
    WARNING_AREA = pbge.frects.Frect(-350, 0, 300, 54)

    def __init__(self, tsrd):
        check_rpg_saves()
        self.tsrd = tsrd
        self.menu = pbge.rpgmenu.Menu(self.MENU_COLUMN.dx, self.MENU_COLUMN.dy,
                                   self.MENU_COLUMN.w, self.MENU_COLUMN.h,
                                   predraw=self, font=pbge.my_state.huge_font,
                                   )
        self.myportraits = dict()
        self.current_version = self._string_to_major_version(VERSION)

        rc = pygame.image.load(pbge.util.image_dir("sys_roundedcorners.png"))
        rcdest = pygame.Rect(0,0,480,360)

        for fname, args in minimal_saves.items():
            self.menu.add_item(args[1].pc.name, fname, desc=args)
            self.myportraits[args] = args[1].pc.get_portrait()
            if args[2]:
                args[2].blit(rc, rcdest)
                args[2].convert_alpha()
                args[2].set_colorkey((0,0,255))


        if not self.menu.items:
            self.menu.add_item('[No campaigns found]', None, desc=None)

        self.sl = pbge.StretchyLayer()

        self.menu.sort()
        fname = self.menu.query()
        if fname:
            pbge.please_stand_by()
            # See note above for why the deepcopy is here. TLDR: keeping pickles fresh and delicious.
            try:
                camp = copy.deepcopy(gears.GearHeadCampaign.load(fname)[3])
            except Exception as err:
                print(err)
                self.deal_with_bad_file(fname, err)
                return
            camp.play()

    def deal_with_bad_file(self, fname, err):
        mymenu = pbge.rpgmenu.AlertMenu("File \"{}\" cannot be loaded due to exception \"{}\". Do you want to eject the character so you can start a new campaign?".format(fname, err))
        mymenu.add_item("Eject the character and delete the broken campaign file.", True)
        mymenu.add_item("Leave it alone for now.", False)
        if mymenu.query():
            minimal_saves[fname][1].save()
            if os.path.exists(fname):
                os.remove(fname)
            check_rpg_saves()

    @staticmethod
    def _string_to_major_version(version):
        # If the first decimal place of the version number changes, there may be problems with loading older save
        # files. Print a warning if this is the case.
        return math.floor(float(version[1:])*10)

    def __call__(self):
        self.tsrd()
        menu_item = self.menu.get_current_item()

        if menu_item.desc:
            self.sl.clear()
            w = self.sl.get_width()
            if menu_item.desc[2]:
                mydest = pygame.Rect(w//2-390, 100, 480, 360)
                _ = self.sl.surf.blit(menu_item.desc[2], mydest)
            myimage = self.myportraits[menu_item.desc]
            portrait_area = pygame.Rect(w//2 - 400, 0, 400, 600)
            myimage.render(portrait_area, dest_surface=self.sl.surf)
            self.sl.render()
            save_version = self._string_to_major_version(menu_item.desc[0])
            if save_version < self.current_version:
                mydest = self.WARNING_AREA.get_rect()
                pbge.default_border.render(mydest.inflate(8,8))
                pbge.draw_text(pbge.MEDIUMFONT, "Warning: Save from {}.\nThis might cause problems in the current version, or it might not. Good luck!".format(menu_item.desc[0]),mydest, justify=0)


def import_arena_character(tsrd):
    pbge.please_stand_by()
    myfiles = gears.oldghloader.GH1Loader.seek_gh1_files()
    mymenu = pbge.rpgmenu.Menu(DZDTitleScreenRedraw.MENU_DEST.dx,
                               DZDTitleScreenRedraw.MENU_DEST.dy,
                               DZDTitleScreenRedraw.MENU_DEST.w, DZDTitleScreenRedraw.MENU_DEST.h,
                               predraw=tsrd, font=pbge.my_state.huge_font
                               )

    for f in myfiles:
        try:
            mygears = gears.oldghloader.GH1Loader(f)
            mygears.load()
            egg = mygears.get_egg()
            mymenu.add_item(str(egg.pc), egg)
        except Exception as e:
            pbge.alert("Warning: File {} can't be parsed. {}".format(f,e))
    mymenu.sort()

    if not mymenu.items:
        mymenu.add_item('[No GH1 characters found]', None)

    myegg = mymenu.query()
    if myegg:
        myegg.save()
        pbge.BasicNotification("{} has been imported.".format(myegg.pc.name))


def open_config_menu(tsrd):
    myconfigmenu = game.configedit.ConfigEditor(tsrd, dy=-25)
    myconfigmenu()


def open_chargen_menu(tsrd):
    game.chargen.CharacterGeneratorW.create_and_invoke(tsrd)

def draw_border():
    pbge.my_state.screen.fill((0, 0, 255))
    myarea = pbge.frects.Frect(-250, 150, 500, 100)
    pbge.default_border.render(myarea.get_rect())

def just_show_background(tsrd):
    while True:
        ev = pbge.wait_event()
        if ev.type == pbge.TIMEREVENT:
            #tsrd(False)
            draw_border()
            pbge.my_state.do_flip()
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            break

minimal_saves = dict()
quarantined_files = list()

def check_rpg_saves():
    pbge.please_stand_by()
    quarantined_files.clear()
    minimal_saves.clear()
    myfiles = glob.glob(pbge.util.user_dir("rpg_*.sav"))
    for fname in myfiles:
        try:
            args = gears.GearHeadCampaign.load_minimal(fname)
            minimal_saves[fname] = args
        except Exception as err:
            print(err)
            quarantined_files.append(fname)


def view_quarantine(tsrd):
    mymenu = pbge.rpgmenu.AlertMenu("The following campaign files aren't loading properly, probably because they are from an out of date version or require DLC that is not installed. You should be able to restore the backup of your character from the 'ghcaramel' folder.", predraw=tsrd)

    for f in quarantined_files:
        mymenu.add_item(f, None)

    mymenu.query()

def test_map_generator(_tsrd):
    intscene = gears.GearHeadScene(30, 30, "Wujung Hospital", player_team=None, civilian_team=None,
                                   attributes=(
                                       gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING,
                                       gears.tags.SCENE_HOSPITAL),
                                   scale=gears.scale.HumanScale)
    intscenegen = pbge.randmaps.PackedBuildingGenerator(intscene, game.content.gharchitecture.HospitalBuilding())
    intscene.contents.append(pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south, ))
    intscene.contents.append(pbge.randmaps.rooms.ClosedRoom())
    pbge.randmaps.debugviewer.DebugViewer.test_map_generation(intscene, intscenegen)

def gen_names(namegen: pbge.namegen.NameGen):
    print(namegen.filename)
    start = len(namegen.forbidden.splitlines())
    with open(pbge.util.user_dir("{}.txt".format(namegen.filename)), "w") as f:
        for _ in range(1000):
            f.write("{}\n".format(namegen.gen_word()))
    print("Unique Names: {}".format(len(namegen.forbidden.splitlines()) - start))


def play_the_game():
    gears.init_gears()
    game.init_game()
    pbge.cutscene.init_cutscenes(pbge.util.data_dir("cspt_*.json"))
    pbge.cutscene.OPPOSITE_TAGS.update({
        gears.personality.Sociable: gears.personality.Shy,
        gears.personality.Shy: gears.personality.Sociable,
        gears.personality.Cheerful: gears.personality.Grim,
        gears.personality.Grim: gears.personality.Cheerful,
        gears.personality.Easygoing: gears.personality.Passionate,
        gears.personality.Passionate: gears.personality.Easygoing
    })

    check_rpg_saves()

    logging.basicConfig(level=logging.DEBUG, filename=pbge.util.user_dir("errors.log"))

    #pbge.namegen.KoreanNameGen.generate_library2(pbge.util.data_dir("KoreanNames.txt"), pbge.util.data_dir("ng_korean2.json"))
    #mynamegen = gears.selector.LUNA_NAMES
    #for t in range(200):
    #    print(mynamegen.gen_word())
    #gen_names(gears.selector.LUNA_NAMES)
    #gen_names(gears.selector.EARTH_NAMES)
    #gen_names(gears.selector.MARS_NAMES)
    #gen_names(gears.selector.ORBITAL_NAMES)
    #print(os.getenv("APPDATA"))

    # print timeit.timeit("""mypic = pbge.image.Image('mecha_buruburu.png',color=(gears.color.ArmyDrab,gears.color.ShiningWhite,gears.color.ElectricYellow,gears.color.GullGrey,gears.color.Terracotta),flags=pygame.RLEACCELOK)""",setup='import pygame, pbge, gears',number=10)
    # print timeit.timeit("""mypic = pbge.image.Image('mecha_buruburu.png',color=(gears.color.ArmyDrab,gears.color.ShiningWhite,gears.color.ElectricYellow,gears.color.GullGrey,gears.color.Terracotta))""",setup='import pbge, gears',number=10)

    #fname = "cha_m_polic.png"
    #mypic = pbge.image.Image(fname, color=(gears.color.Cyan, gears.color.SteelBlue, gears.color.BlackRose, gears.color.Aquamarine, gears.color.Leather))
    #mydest = pygame.Surface((mypic.frame_width, mypic.frame_height))
    #mydest.fill((0, 0, 255))
    #mypic.render((0,0),dest_surface=mydest)
    #pygame.image.save(mydest, pbge.util.user_dir("out_"+fname))

    #a = gears.base.Treasure(value=1000)
    #b = gears.base.Treasure(value=100000, material=gears.materials.Advanced)
    #c = gears.base.Treasure(value=10000000)
    #print(a, a.cost, a.shop_rank())
    #print(b, b.cost, b.shop_rank())
    #print(c, c.cost, c.shop_rank())

    # mypor = gears.portraits.Portrait()
    # mypor.bits = ["FBA NoBody","Haywire B3 Head"]
    # mypic = mypor.build_portrait(None,False,True)
    # pygame.image.save(mypic.bitmap, pbge.util.user_dir("out.png"))
    try:
        tsrd = DZDTitleScreenRedraw()
        pbge.my_state.view = tsrd

        action = True
        while action:
            mymenu = pbge.rpgmenu.Menu(DZDTitleScreenRedraw.MENU_DEST.dx,
                                       DZDTitleScreenRedraw.MENU_DEST.dy,
                                       DZDTitleScreenRedraw.MENU_DEST.w, DZDTitleScreenRedraw.MENU_DEST.h,
                                       predraw=tsrd, font=pbge.my_state.huge_font,
                                       no_escape=pbge.util.config.getboolean("GENERAL","no_escape_from_title_screen")
                                       )

            mymenu.add_item("Load Campaign", LoadGameMenu)
            mymenu.add_item("Start Campaign", StartGameMenu)
            mymenu.add_item("Create Character", open_chargen_menu)
            mymenu.add_item("Import GH1 Character", import_arena_character)
            mymenu.add_item("Config Options", open_config_menu)
            mymenu.add_item("Browse Mecha", game.mechabrowser.MechaBrowser())
            mymenu.add_item("Edit Mecha", game.geareditor.LetsEditSomeMeks)
            if quarantined_files:
                mymenu.add_item("Quarantined Saves", view_quarantine)
            if pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                mymenu.add_item("Edit Scenario", game.scenariocreator.start_plot_creator)
                mymenu.add_item("Compile Plot Bricks", game.scenariocreator.PlotBrickCompiler)
                mymenu.add_item("Test Map Generator", test_map_generator)
                #mymenu.add_item("Eggzamination", game.devstuff.Eggzaminer)
                #mymenu.add_item("Just Show Background", just_show_background)
                #mymenu.add_item("Test Adventure Generation", TestStartGame)
                mymenu.add_item("Steam The Eggs", prep_eggs_for_steam)
            mymenu.add_item("Quit", None)

            pbge.my_state.start_music(TITLE_THEME)
            pbge.my_state.view = tsrd
            action = mymenu.query()
            if action:
                action(tsrd)
    except Exception as e:
        print(traceback.format_exc())
        pbge.alert("Python Exception ({}) occurred- please send the error.log in your ghcaramel user folder to pyrrho12@yahoo.ca.\nK THX gonna crash now.".format(e))
        logging.exception(e)
        logging.critical("Please email this file to pyrrho12@yahoo.ca")

if __name__ == "__main__":
    play_the_game()
    pygame.quit()
    # Been getting some problems with the program continuing to run sometimes after pygame.quit().
    # StackExchange suggested the following... I figure it couldn't hurt.
    sys.exit()
