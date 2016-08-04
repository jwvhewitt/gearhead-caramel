import engine
import os
import scenes
from pygame import Rect

gamedir = os.path.dirname(__file__)
engine.init('GearHead Caramel','dmeternal',gamedir)

MTL = scenes.terrain.TerrainList()
FLOOR = MTL.append( scenes.terrain.Terrain('terrain_floor_tile.png') )
WALL = MTL.append( scenes.terrain.WallTerrain('terrain_wall_rocks.png') )

myscene = scenes.Scene(30,30,MTL,"Testaria")
myscene.fill(Rect(0,0,29,29), floor=FLOOR, wall=WALL)
myscene.fill(Rect(5,5,24,24), wall=None)

mymenu = engine.rpgmenu.Menu(-150,-150,300,300)
mymenu.add_item('One',1)
mymenu.add_item('Two',1)
mymenu.add_item('Three',1)
mymenu.query()


