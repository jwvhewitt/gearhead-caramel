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

class WinterMochaDomeTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha.png'
    frame = 3
    blocks = (Walking,Skimming,Rolling)

class WinterMochaGeothermalGeneratorTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha.png'
    frame = 4
    blocks = (Walking,Skimming,Rolling)

class WinterMochaSnowdrift( pbge.scenes.terrain.HillTerrain ):
    altitude = 20
    image_middle = 'terrain_wintermocha_snowdrift.png'
    bordername = ''
    blocks = (Walking,Skimming,Rolling)


