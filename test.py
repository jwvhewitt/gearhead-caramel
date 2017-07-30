import pbge
import os
from pbge import scenes, KeyObject
from pygame import Rect
import pygame
import gears

gamedir = os.path.dirname(__file__)
pbge.init('GearHead Caramel','ghcaramel',gamedir)


class Floor( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_grass.png'

#class Wall( pbge.scenes.terrain.WallTerrain ):
#    imagename = 'terrain_wall_fortress.png'

class Wall( pbge.scenes.terrain.VariableTerrain ):
    image_top = 'terrain_trees_fg.png'
    image_middle = 'terrain_trees_bg.png'

class Water( pbge.scenes.terrain.AnimTerrain ):
    image_biddle = 'terrain_water2.png'
    image_bottom = 'terrain_water1.png'
    altitude = -24
    transparent = True

class Floor( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_grass.png'
    #image_bottom = 'terrain_floor_new.png'
    border = pbge.scenes.terrain.FloorBorder( Water, 'terrain_border_beach.png' )

class Mountain( pbge.scenes.terrain.HillTerrain ):
    altitude = 20
    image_middle = 'terrain_hill_1.png'
    bordername = ''
    block_walk = False

class Character( pbge.scenes.PlaceableThing):
    imagename = 'PD_Sean.png'
    imageheight = 64
    imagewidth = 64
    #colors=(127,255,212)

#myarmor = gears.base.Armor( size = 5, sub_com=[gears.base.Armor(size=1)], scale=gears.scale.HumanScale, foo="bar" )

mygearlist = gears.Loader(os.path.join(pbge.util.game_dir('design'),'BuruBuru.txt')).load()
mychar = mygearlist[0]

#mygearlist = gears.Loader('out.txt').load()
#myout = mygearlist[0]


#mychar.colors = ((104,130,117),(152,190,181),(220,44,51),(152,190,181),(220,44,51))

#print mychar.mass
#print mychar.calc_mobility()
#mychar.termdump()
#print mychar.__class__.__mro__

#mysaver = gears.Saver('out.txt')
#mysaver.save([mychar])

myscene = scenes.Scene(50,50,"Testaria")
#myscene.fill(Rect(0,0,50,50), floor=Floor, wall=None)
#myscene.fill(Rect(5,5,24,24), wall=Wall)

#mychar = Character()
#mychar.place(myscene,(2,13))

myfilter = pbge.randmaps.converter.BasicConverter(Wall)
mymutate = pbge.randmaps.mutator.CellMutator()
myarchi = pbge.randmaps.architect.Architecture(Floor,myfilter,mutate=mymutate)
myscenegen = pbge.randmaps.SceneGenerator(myscene,myarchi)

myroom1 = pbge.randmaps.rooms.Room()
myroom2 = pbge.randmaps.rooms.Room()
myroom3 = pbge.randmaps.rooms.Room()
myroom1.contents.append(mychar)
#myroom1.contents.append(myout)

myscenegen.contents.append(myroom1)
myscenegen.contents.append(myroom2)
myscenegen.contents.append(myroom3)

myscenegen.make()

myscene.fill(Rect(20,20,5,3), floor=Water, wall=None)
myscene.fill(Rect(21,19,3,5), floor=Water, wall=None)
myscene._map[22][22].floor = Floor
myscene._map[19][21].floor = Water
myscene.fill(Rect(10,20,1,5), wall=Mountain)
myscene.fill(Rect(8,20,5,1), wall=Mountain)

myview = scenes.viewer.SceneView( myscene )

#myview.anim_list.append( pbge.scenes.animobs.MoveModel( mychar, (30,3), 0.25))
#mymove = pbge.scenes.animobs.MoveModel( mychar, dest=(2,3), speed=0.25)
#mymove.children.append(pbge.scenes.animobs.MoveModel( mychar, start=(2,3), dest=(10,3), speed=0.25))
#myview.anim_list.append(mymove)
#myview.handle_anim_sequence()

def move_pc( dx, dy ):
    x,y = mychar.pos
    x += dx
    y += dy
    if not myscene.tile_blocks_walking(x,y):
        mychar.move((x,y),myview,0.25)

def parenthetic_contents(string):
    """Generate parenthesized contents in string as pairs (level, contents)."""
    stack = []
    for i, c in enumerate(string):
        if c == '(':
            stack.append(i)
        elif c == ')' and stack:
            start = stack.pop()
            yield (len(stack), string[start + 1: i])

def process_list( string ):
    current_list = None
    stack = []
    start_token = -1
    for i, c in enumerate(string):
        print i,c, len(stack)
        if c == '(':
            # Begin a new list
            nulist = list()
            if current_list is not None:
                stack.append(current_list)
                current_list.append( nulist )
            current_list = nulist
            start_token = i + 1
        elif c == ')':
            # Pop out to previous list
            if start_token < i:
                toke = string[start_token:i]
                current_list.append(toke)
            if stack:
                current_list = stack.pop()
            start_token=i+1
        elif c == ',':
            # Store the current item in the list
            toke = string[start_token:i]
            if toke:
                current_list.append(toke)
            start_token=i+1
    return current_list


#print process_list('((104, 130, 117), (152, 190, 181), (220, 44, 51), (152, 190, 181), (220, 44, 51))')

keep_going = True
record_anim = False
while keep_going:
    # Get input and process it.
    if myview.anim_list:
        myview.handle_anim_sequence(record_anim)
        record_anim = False

    else:
        gdi = pbge.wait_event()
        if gdi.type == pbge.TIMEREVENT:
            myview()
            pygame.display.flip()

        elif gdi.type == pygame.MOUSEBUTTONUP and gdi.button == 1:
            myanim = pbge.scenes.animobs.ShotAnim('anim_s_bigbullet.png',start_pos=mychar.pos,end_pos=myview.mouse_tile,speed=0.5)
            myview.anim_list.append( myanim )

        elif gdi.type == pygame.KEYDOWN:
            if gdi.unicode == u"1":
                move_pc( 0, 1 )
            elif gdi.unicode == u"2":
                move_pc( 1, 1 )
            elif gdi.unicode == u"3":
                move_pc( 1, 0 )
            elif gdi.unicode == u"4":
                move_pc( -1, 1 )
            elif gdi.unicode == u"6":
                move_pc( 1, -1 )
            elif gdi.unicode == u"7":
                move_pc( -1, 0 )
            elif gdi.unicode == u"8":
                move_pc( -1, -1 )
            elif gdi.unicode == u"9":
                move_pc( 0, -1 )
            elif gdi.unicode == u"Q":
                keep_going = False
            elif gdi.unicode == u"r":
                record_anim = True
            elif gdi.unicode == u"c":
                myview.focus(*mychar.pos)

        elif gdi.type == pygame.QUIT:
            keep_going = False


"""
mymenu = pbge.rpgmenu.Menu(-150,-150,300,300,predraw=myview)
mymenu.add_item('One',1)
mymenu.add_item('Two',2)
mymenu.add_item('Three',3)
mymenu.query()
"""

