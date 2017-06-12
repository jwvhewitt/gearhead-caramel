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

myscene = scenes.Scene(50,50,"Testaria")
myscene.fill(Rect(0,0,49,49), floor=Floor, wall=None)
myscene.fill(Rect(5,5,24,24), wall=Wall)

myview = scenes.viewer.SceneView( myscene )

mymenu = pbge.rpgmenu.Menu(-150,-150,300,300,predraw=myview)
mymenu.add_item('One',1)
mymenu.add_item('Two',2)
mymenu.add_item('Three',3)
mymenu.query()


