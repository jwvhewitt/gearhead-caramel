import pbge
import os
from pbge import scenes, KeyObject
from pygame import Rect
import pygame
import gears
import random
import copy
import cPickle

import game

gamedir = os.path.dirname(__file__)
pbge.init('GearHead Caramel','ghcaramel',gamedir)


#class Wall( pbge.scenes.terrain.WallTerrain ):
#    imagename = 'terrain_wall_fortress.png'

class Wall( pbge.scenes.terrain.VariableTerrain ):
    image_top = 'terrain_trees_fg.png'
    image_middle = 'terrain_trees_bg.png'
    movement_cost={pbge.scenes.movement.Walking:2.0,gears.geffects.Skimming:2.0,gears.geffects.Rolling:2.0}

class Water( pbge.scenes.terrain.AnimTerrain ):
    image_biddle = 'terrain_water2.png'
    image_bottom = 'terrain_water1.png'
    altitude = -24
    transparent = True
    movement_cost={pbge.scenes.movement.Walking:3.0,gears.geffects.Rolling:3.0}

class Floor( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_grass.png'
    #image_bottom = 'terrain_floor_new.png'
    border = pbge.scenes.terrain.FloorBorder( Water, 'terrain_border_beach.png' )

class Mountain( pbge.scenes.terrain.HillTerrain ):
    altitude = 20
    image_middle = 'terrain_hill_1.png'
    #image_bottom = 'terrain_hill_1.png'
    bordername = ''
    blocks = ()


mygearlist = gears.Loader(os.path.join(pbge.util.game_dir('design'),'BuruBuru.txt')).load()
mychar = mygearlist[0]
mychar.mmode = scenes.movement.Walking
#mychar.mmode = gears.geffects.Skimming

mypilot = gears.base.Character(name="Bob",statline={gears.stats.Body:15, gears.stats.Reflexes:13,gears.stats.Speed:13,gears.stats.Perception:12,gears.stats.MechaPiloting:5,gears.stats.MechaGunnery:5})
mychar.load_pilot( mypilot )

#mygearlist = gears.Loader('out.txt').load()
#myout = mygearlist[0]

myclon = copy.deepcopy(mychar)
myclon.colors = ((236,254,255),(194,16,38),(220,44,51),(152,190,181),(220,44,51))
myclon.name = "Buru2"
mypilot.name = "Argh"
#myclon.termdump()

mytarg = copy.deepcopy(mychar)
mytarg.colors = ((236,254,50),(16,194,38),(220,44,51),(152,190,181),(220,44,51))
mytarg.name = "Buru3"
mywoobie = mytarg.get_pilot()
mywoobie.statline[gears.stats.MechaPiloting] = 1

#print mychar.mass
#print mychar.calc_mobility()
#mychar.termdump()
#print mychar.__class__.__mro__

#mysaver = gears.Saver('out.txt')
#mysaver.save([mychar])

myscene = gears.GearHeadScene(50,50,"Testaria")

mycamp = gears.GearHeadCampaign(explo_class=game.exploration.Explorer)
mycamp.scene = myscene
mycamp.party = [mychar,]


myfilter = pbge.randmaps.converter.BasicConverter(Wall)
mymutate = pbge.randmaps.mutator.CellMutator()
myarchi = pbge.randmaps.architect.Architecture(Floor,myfilter,mutate=mymutate)
myscenegen = pbge.randmaps.SceneGenerator(myscene,myarchi)

myroom1 = pbge.randmaps.rooms.Room()
myroom2 = pbge.randmaps.rooms.Room()
myroom3 = pbge.randmaps.rooms.Room()
myroom1.contents.append(mychar)
myroom1.contents.append(myclon)
myroom1.contents.append(mytarg)

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



my_modules = pbge.image.Image('sys_modules.png',16,16)

BIGFONT = pygame.font.Font( pbge.util.image_dir( "Anita semi square.ttf" ) , 15 )


my_mapcursor = pbge.image.Image('sys_mapcursor.png',64,64)

mycamp.fight = game.combat.Combat(mycamp,myclon)

mycamp.play()

"""

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
            mmecha = myview.modelmap.get(myview.mouse_tile)
            if mmecha:
                x,y = pygame.mouse.get_pos()
                y -= 64
                MechaStatusDisplay((x,y),mmecha[0])
            pygame.display.flip()

            myview.overlays.clear()
            myview.overlays[ myview.mouse_tile ] = (my_mapcursor,0)


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
            elif gdi.unicode == u"a":
                my_targeter = TargetingUI(mycamp, mychar, myinvo )
                targets = my_targeter.select_area()
                if targets:
                    myinvo.invoke(mycamp, mychar, targets, myview.anim_list )

            elif gdi.unicode == u"c":
                myview.focus(*mychar.pos)
            elif gdi.unicode == u"s":
                #record_anim = True
                endpos = list(mychar.pos)
                endpos[0] += 15
                for t in range(-10,11):
                    endpos[1] = mychar.pos[1] - 10 + abs(t*2)
                    myanim = pbge.scenes.animobs.ShotAnim('anim_s_bigbullet.png',start_pos=mychar.pos,end_pos=endpos,speed=0.5,delay=t*2+20)
                    myview.anim_list.append( myanim )
            elif gdi.unicode == u"p":
                myanim = pbge.scenes.animobs.Caption('Eat a dozen burritos!',pos=mychar.pos,delay=1)
                myview.anim_list.append( myanim )
            elif gdi.unicode == u"d":
                gears.damage.Damage( mycamp, gears.scale.MechaScale.scale_health( 
                  random.randint(1,6)+random.randint(1,6)+random.randint(1,6),
                  gears.materials.Metal ), random.randint(1,100), mychar, myview.anim_list )
            elif gdi.unicode == u"D":
                gears.damage.Damage( mycamp, gears.scale.MechaScale.scale_health( 
                  11,
                  gears.materials.Metal ), random.randint(1,100), mychar, myview.anim_list )

            elif gdi.unicode == u"w":
                mychar.wipe_damage()

            elif gdi.unicode == u"x":
                mpos = pygame.mouse.get_pos()
                print myview.mouse_tile, ' -> ', myview.fmap_x(*mpos), ',', myview.fmap_y(*mpos)


        elif gdi.type == pygame.QUIT:
            keep_going = False


mymenu = pbge.rpgmenu.Menu(-150,-150,300,300,predraw=myview)
mymenu.add_item('One',1)
mymenu.add_item('Two',2)
mymenu.add_item('Three',3)
mymenu.query()
"""

