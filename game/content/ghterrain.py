import pbge
import gears
from pbge.scenes.movement import Walking, Flying, Vision
from gears.geffects import Skimming, Rolling


class Forest( pbge.scenes.terrain.VariableTerrain ):
    image_top = 'terrain_trees_fg.png'
    image_middle = 'terrain_trees_bg.png'
    movement_cost={pbge.scenes.movement.Walking:2.0,gears.geffects.Skimming:2.0,gears.geffects.Rolling:2.0,pbge.scenes.movement.Vision:5}

class Water( pbge.scenes.terrain.AnimTerrain ):
    image_biddle = 'terrain_water2.png'
    image_bottom = 'terrain_water1.png'
    altitude = -24
    transparent = True
    movement_cost={pbge.scenes.movement.Walking:3.0,gears.geffects.Rolling:3.0}

class DeadZoneGround( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_dzground.png'
    border = pbge.scenes.terrain.FloorBorder( Water, 'terrain_border_beach.png' )

class TechnoRubble( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_technorubble.png'
    border = pbge.scenes.terrain.FloorBorder( DeadZoneGround, 'terrain_border_technoedge.png' )

class CrackedEarth( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_crackedearth.png'
    border = pbge.scenes.terrain.FloorBorder( Water, 'terrain_border_beach.png' )

class WorldMapRoad(pbge.scenes.terrain.RoadTerrain):
    image_bottom = 'terrain_decor_worldroad.png'

class Snow( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_snow.png'
    border = pbge.scenes.terrain.FloorBorder( Water, 'terrain_border_beach.png' )

class SmallSnow( pbge.scenes.terrain.VariableTerrain ):
    # As above, but uses the human scale graphics.
    image_bottom = 'terrain_floor_snow_small.png'
    border = pbge.scenes.terrain.FloorBorder( Water, 'terrain_border_beach.png' )


class Mountain( pbge.scenes.terrain.HillTerrain ):
    altitude = 20
    image_middle = 'terrain_hill_1.png'
    #image_bottom = 'terrain_hill_1.png'
    bordername = ''
    blocks = ()

class VendingMachineTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_middle = 'terrain_prop_vendingmachine.png'
    blocks = (Walking,Skimming,Rolling)

class WinterMochaBarrelTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha.png'
    frame = 0
    blocks = (Walking,Skimming,Rolling)

class WinterMochaBrokenShovel(pbge.scenes.terrain.Terrain):
    image_middle = 'terrain_wintermocha.png'
    frame = 1

class WinterMochaToolboxTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha.png'
    frame = 2
    blocks = (Walking,Skimming,Rolling)


class ExitTerrain( pbge.scenes.terrain.AnimTerrain ):
    image_top = 'terrain_wp_exit.png'
    transparent = True
    blocks = (Walking,Skimming,Rolling,Flying)
    frames = (0,1,2,3,4,5,6,7,8,9)
    anim_delay = 1


class FortressWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_fortress.png'
    blocks = (Walking,Skimming,Rolling,Vision)

class DragonTeethWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_dragonteeth.png'
    bordername = None
    altitude = 20
    blocks = (Walking, Skimming, Rolling)
