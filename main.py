import pbge
import game
import pygame
import os
import gears
import random

class Snowflake(object):
    def __init__(self,dest):
        self.dest = dest
        self.x = dest.left + random.randint(1,dest.w)
        self.y = dest.top-12
        self.dx = random.randint(1,6) - random.randint(1,3)
        self.dy = random.randint(2,4)
        self.frame = random.randint(0,24)
    def update(self):
        # Return True if this flake should be deleted.
        self.x += self.dx
        self.y += self.dy
        if self.y > self.dest.bottom:
            return True

class TitleScreenRedraw(object):
    TITLE_DEST = pbge.frects.Frect(-325,-150,650,100)
    MENU_DEST = pbge.frects.Frect(-150,0,300,100)
    def __init__(self):
        self.title = pbge.image.Image("sys_wmtitle.png")
        self.bg = pbge.image.Image("poster_snowday.png")
        self.snow = pbge.image.Image("sys_wm_snow.png",24,24)
        self.flakes = list()

    def add_snow(self,dest):
        for t in range(min(random.randint(1,3),random.randint(1,3))):
            self.flakes.append(Snowflake(dest))

    def __call__(self):
        dest = self.bg.bitmap.get_rect( center=(pbge.my_state.screen.get_width()//2,pbge.my_state.screen.get_height()//2) )
        self.bg.render(dest)
        
        self.title.render(self.TITLE_DEST.get_rect())

        pbge.my_state.screen.set_clip(dest)
        self.add_snow(dest)
        for sf in list(self.flakes):
            if sf.update():
                self.flakes.remove(sf)
            else:
                self.snow.render((sf.x,sf.y),sf.frame)
        pbge.my_state.screen.set_clip(None)

TITLE_THEME = 'Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg'

def start_game(tsrd):
    name = pbge.input_string(prompt="By what name will you be known?",redrawer=tsrd)
    if not name:
        name = gears.EARTH_NAMES.gen_word()
    pc = gears.random_pilot(50)
    pc.name = name
    pc.imagename = 'cha_wm_parka.png'
    pc.colors = gears.random_character_colors()
    game.start_mocha(pc)

def import_arena_character(tsrd):
    myfiles = gears.oldghloader.GH1Loader.seek_gh1_files()
    mymenu = pbge.rpgmenu.Menu(TitleScreenRedraw.MENU_DEST.dx,
        TitleScreenRedraw.MENU_DEST.dy,
        TitleScreenRedraw.MENU_DEST.w,TitleScreenRedraw.MENU_DEST.h,
        predraw=tsrd,font=pbge.my_state.huge_font
        )

    for f in myfiles:
        mygears = gears.oldghloader.GH1Loader(f)
        mygears.load()
        rpc = mygears.find_pc()
        pc = mygears.convert_character(rpc)
        mymenu.add_item(str(pc),pc)

    if not mymenu.items:
        mymenu.add_item('[No GH1 characters found]',None)

    pc = mymenu.query()
    if pc:
        pc.imagename = 'cha_wm_parka.png'
        game.start_mocha(pc)



def play_the_game():
    gamedir = os.path.dirname(__file__)
    pbge.init('GearHead Caramel','ghcaramel',gamedir)

    tsrd = TitleScreenRedraw()
    mymenu = pbge.rpgmenu.Menu(TitleScreenRedraw.MENU_DEST.dx,
        TitleScreenRedraw.MENU_DEST.dy,
        TitleScreenRedraw.MENU_DEST.w,TitleScreenRedraw.MENU_DEST.h,
        predraw=tsrd,font=pbge.my_state.huge_font
        )

    mymenu.add_item("Start Game",start_game)
    mymenu.add_item("Import GH1 Character",import_arena_character)
    mymenu.add_item("Quit",None)

    action = True
    while action:
        pbge.my_state.start_music(TITLE_THEME)
        action = mymenu.query()
        if action:
            action(tsrd)


if __name__ == "__main__":

    #clay = gears.Loader.load_design_file('Claymore.txt')
    #clay[0].termdump()

    play_the_game()

