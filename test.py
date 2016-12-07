import pbge
import os
from pbge import scenes
from pygame import Rect

gamedir = os.path.dirname(__file__)
pbge.init('GearHead Caramel','dmeternal',gamedir)


class Floor( pbge.scenes.terrain.Terrain ):
    imagename = 'terrain_floor_tile.png'

class Wall( pbge.scenes.terrain.WallTerrain ):
    imagename = 'terrain_wall_rocks.png'

myscene = scenes.Scene(30,30,"Testaria")
myscene.fill(Rect(0,0,29,29), floor=Floor, wall=Wall)
myscene.fill(Rect(5,5,24,24), wall=None)

mymenu = pbge.rpgmenu.Menu(-150,-150,300,300)
mymenu.add_item('One',1)
mymenu.add_item('Two',2)
mymenu.add_item('Three',3)
mymenu.query()


