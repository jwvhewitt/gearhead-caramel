import pbge
import os
from pbge import scenes, KeyObject
from pygame import Rect
import pygame
import gears

gamedir = os.path.dirname(__file__)
pbge.init('GearHead Caramel','ghcaramel',gamedir)


class Floor( pbge.scenes.terrain.VariableTerrain ):
    imagename = 'terrain_floor_new.png'

class Wall( pbge.scenes.terrain.WallTerrain ):
    imagename = 'terrain_wall_fortress.png'

class Character( pbge.scenes.PlaceableThing):
    imagename = 'PD_Sean.png'
    imageheight = 64
    imagewidth = 64
    #colors=(127,255,212)

#myarmor = gears.base.Armor( size = 5, sub_com=[gears.base.Armor(size=1)], scale=gears.scale.HumanScale, foo="bar" )

mygearlist = gears.Loader(os.path.join(pbge.util.game_dir('design'),'BuruBuru.txt')).load()
myarmor = mygearlist[0]

print myarmor.mass
print myarmor.max_health
myarmor.termdump()

myscene = scenes.Scene(50,50,"Testaria")
#myscene.fill(Rect(0,0,50,50), floor=Floor, wall=None)
#myscene.fill(Rect(5,5,24,24), wall=Wall)
#myscene.fill(Rect(0,49,29,49), wall=Wall)

mychar = Character()
#mychar.place(myscene,(2,13))

myfilter = pbge.randmaps.converter.BasicConverter(Wall)
mymutate = pbge.randmaps.mutator.CellMutator()
myarchi = pbge.randmaps.architect.Architecture(Floor,myfilter,mutate=mymutate)
myscenegen = pbge.randmaps.SceneGenerator(myscene,myarchi)

myroom1 = pbge.randmaps.rooms.Room()
myroom2 = pbge.randmaps.rooms.Room()
myroom3 = pbge.randmaps.rooms.Room()
myroom1.contents.append(mychar)
myroom3.contents.append(myarmor)

myscenegen.contents.append(myroom1)
myscenegen.contents.append(myroom2)
myscenegen.contents.append(myroom3)

myscenegen.make()

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

