import pbge
import sys
import os

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

VERSION = "v0.946"


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

class StartGameMenu:
    PORTRAIT_AREA = pbge.frects.Frect(-400, -300, 400, 600)
    MENU_COLUMN = pbge.frects.Frect(20,-100,280,350)

    def __init__(self, tsrd):
        mymenu = pbge.rpgmenu.Menu(self.MENU_COLUMN.dx, self.MENU_COLUMN.dy,
                                   self.MENU_COLUMN.w, self.MENU_COLUMN.h,
                                   predraw=tsrd, font=pbge.my_state.huge_font,
                                   )
        mymenu.descobj = self
        self.myportraits = dict()

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
                mymenu.add_item(str(egg.pc), egg)
                self.myportraits[egg] = egg.pc.get_portrait()

        if not mymenu.items:
            mymenu.add_item('[No characters found]', None)

        mymenu.sort()
        egg = mymenu.query()
        if egg:
            game.start_campaign(egg, tsrd, VERSION)

    def __call__(self, menu_item):
        if menu_item and menu_item.value:
            myimage = self.myportraits[menu_item.value]
            myimage.render(self.PORTRAIT_AREA.get_rect())

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
        mymenu = pbge.rpgmenu.Menu(self.MENU_COLUMN.dx, self.MENU_COLUMN.dy,
                                   self.MENU_COLUMN.w, self.MENU_COLUMN.h,
                                   predraw=tsrd, font=pbge.my_state.huge_font,
                                   )
        mymenu.descobj = self
        self.myportraits = dict()
        self.current_version = self._string_to_major_version(VERSION)

        rc = pygame.image.load(pbge.util.image_dir("sys_roundedcorners.png"))
        rcdest = pygame.Rect(0,0,480,360)

        for fname, args in minimal_saves.items():
            mymenu.add_item(args[1].pc.name, fname, desc=args)
            self.myportraits[args] = args[1].pc.get_portrait()
            if args[2]:
                args[2].blit(rc, rcdest)
                args[2].convert_alpha()
                args[2].set_colorkey((0,0,255))


        if not mymenu.items:
            mymenu.add_item('[No campaigns found]', None, desc=None)

        mymenu.sort()
        fname = mymenu.query()
        if fname:
            pbge.please_stand_by()
            # See note above for why the deepcopy is here. TLDR: keeping pickles fresh and delicious.
            try:
                camp = copy.deepcopy(gears.GearHeadCampaign.load(fname)[3])
                camp.play()
            except Exception as err:
                print(err)
                self.deal_with_bad_file(fname, err)

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

    def __call__(self, menu_item):
        if menu_item.desc:
            if menu_item.desc[2]:
                mydest = self.THUMB_AREA.get_rect()
                pbge.my_state.screen.blit(menu_item.desc[2], mydest)
            myimage = self.myportraits[menu_item.desc]
            myimage.render(self.PORTRAIT_AREA.get_rect())
            save_version = self._string_to_major_version(menu_item.desc[0])
            if save_version < self.current_version:
                mydest = self.WARNING_AREA.get_rect()
                pbge.default_border.render(mydest.inflate(8,8))
                pbge.draw_text(pbge.MEDIUMFONT, "Warning: Save from {}.\nThis might cause problems in the current version, or it might not. Good luck!".format(menu_item.desc[0]),mydest, justify=0)


def import_arena_character(tsrd):
    pbge.please_stand_by()
    myfiles = gears.oldghloader.GH1Loader.seek_gh1_files()
    mymenu = pbge.rpgmenu.Menu(TitleScreenRedraw.MENU_DEST.dx,
                               TitleScreenRedraw.MENU_DEST.dy,
                               TitleScreenRedraw.MENU_DEST.w, TitleScreenRedraw.MENU_DEST.h,
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


def open_cosplay_menu(tsrd):
    game.cosplay.ColorEditor.explo_invoke(tsrd)


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
    #mynamegen = pbge.namegen.KoreanNameGen(pbge.util.data_dir("ng_korean2.json"))
    #for t in range(200):
    #    print(mynamegen.gen_word2())

    #print(os.getenv("APPDATA"))

    # print timeit.timeit("""mypic = pbge.image.Image('mecha_buruburu.png',color=(gears.color.ArmyDrab,gears.color.ShiningWhite,gears.color.ElectricYellow,gears.color.GullGrey,gears.color.Terracotta),flags=pygame.RLEACCELOK)""",setup='import pygame, pbge, gears',number=10)
    # print timeit.timeit("""mypic = pbge.image.Image('mecha_buruburu.png',color=(gears.color.ArmyDrab,gears.color.ShiningWhite,gears.color.ElectricYellow,gears.color.GullGrey,gears.color.Terracotta))""",setup='import pbge, gears',number=10)

    #fname = "WIP_JjangBogo.png"
    #mypic = pbge.image.Image(fname, color=(gears.color.HeavyPurple, gears.color.MediumSkin, gears.color.Beige, gears.color.Saffron, gears.color.PirateSunrise))
    #mydest = pygame.Surface((mypic.frame_width, mypic.frame_height))
    #mydest.fill((0, 0, 255))
    #mypic.render((0,0),dest_surface=mydest)
    #pygame.image.save(mydest, pbge.util.user_dir("out_"+fname))

    #a = gears.selector.get_design_by_full_name("Heavy Duty Duct Tape")
    #b = gears.selector.get_design_by_full_name("10 Pack Antidote")
    #c = gears.selector.get_design_by_full_name("5 Pack Quick Fix Pill")
    #print(a, a.cost, a.shop_rank())
    #print(b, b.cost, b.shop_rank())
    #print(c, c.cost, c.shop_rank())

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
        tsrd = TitleScreenRedraw()
        pbge.my_state.view = tsrd

        action = True
        while action:
            mymenu = pbge.rpgmenu.Menu(TitleScreenRedraw.MENU_DEST.dx,
                                       TitleScreenRedraw.MENU_DEST.dy,
                                       TitleScreenRedraw.MENU_DEST.w, TitleScreenRedraw.MENU_DEST.h,
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
                mymenu.add_item("Eggzamination", game.devstuff.Eggzaminer)
                mymenu.add_item("Just Show Background", just_show_background)
                mymenu.add_item("Steam The Eggs", prep_eggs_for_steam)
            mymenu.add_item("Quit", None)

            pbge.my_state.start_music(TITLE_THEME)
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
