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

class GreenZoneGrass( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_grass.png'

class Flagstone( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_flagstone.png'
    border = pbge.scenes.terrain.FloorBorder( GreenZoneGrass, 'terrain_border_grassy.png' )

class DeadZoneGround( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_dzground.png'
    border = pbge.scenes.terrain.FloorBorder( Water, 'terrain_border_beach.png' )

class SmallDeadZoneGround( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_dzground2.png'
    border = pbge.scenes.terrain.FloorBorder( Water, 'terrain_border_beach.png' )

class TechnoRubble( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_technorubble.png'
    border = pbge.scenes.terrain.FloorBorder( DeadZoneGround, 'terrain_border_technoedge.png' )

class OldTilesFloor( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_oldtiles.png'

class WhiteTileFloor( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_whitetile.png'

class HardwoodFloor( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_hardwood.png'

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
    image_top = 'terrain_decor_vendingmachine.png'
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

class ScrapIronWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_rusty.png'
    blocks = (Walking,Skimming,Rolling,Vision)

class DefaultWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_default.png'
    blocks = (Walking,Skimming,Rolling,Vision,Flying)

class CommercialWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_commercial.png'
    blocks = (Walking,Skimming,Rolling,Vision,Flying)

class ResidentialWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_residential.png'
    blocks = (Walking,Skimming,Rolling,Vision,Flying)

class HospitalWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_hospital.png'
    blocks = (Walking,Skimming,Rolling,Vision,Flying)

class IndustrialWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_industrial.png'
    blocks = (Walking,Skimming,Rolling,Vision,Flying)

class DragonTeethWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_dragonteeth.png'
    bordername = None
    altitude = 20
    blocks = (Walking, Skimming, Rolling)
    movement_cost={pbge.scenes.movement.Vision:5}


class DZDTownTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_worldprops.png'
    frame = 0
    blocks = (Walking,Skimming,Rolling,Flying)


class DZDWCommTowerTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_worldprops.png'
    frame = 1
    blocks = (Walking,Skimming,Rolling,Flying)


class DZDCommTowerTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_mechaprops.png'
    frame = 0
    blocks = (Walking,Skimming,Rolling,Flying)


class VictimTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_default.png'
    frame = 0
    blocks = (Walking,Skimming,Rolling,Flying)

class Window(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_window.png'

class WindowSouth(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_window.png'
    frame = 1

class WindowEast(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_window.png'
    frame = 0


class RetroComputerTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_computer.png'

class WoodenShelves(pbge.scenes.terrain.OnTheWallVariableTerrain):
    image_top = 'terrain_decor_woodenshelves.png'
    south_frames = (1,3,5,7,9)
    east_frames = (0,2,4,6,8)

class StatueMTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_statue_m.png'

class StatueFTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_statue_f.png'

class GoldPlaqueTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_plaque.png'


class DZDWConcreteBuilding(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_worldprops.png'
    frame = 2
    blocks = (Walking,Skimming,Rolling,Flying)


class DZDConcreteBuilding(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_mechaprops.png'
    frame = 1
    blocks = (Walking,Skimming,Rolling,Flying)

class MetalDoorClosed(pbge.scenes.terrain.DoorTerrain):
    image_top = 'terrain_door_metal.png'
    frame = 0
    blocks = (Walking, Skimming, Rolling, Flying, Vision)

class MetalDoorOpen(pbge.scenes.terrain.DoorTerrain):
    image_middle = 'terrain_door_metal.png'
    frame = 2
    blocks = ()

class ScrapIronBuildingTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_bottom = 'terrain_building_scrapiron_b.png'
    image_top = 'terrain_building_scrapiron.png'
    blocks = (Walking,Skimming,Rolling,Flying)

class ScrapIronDoorTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_scrapirondoor.png'

class JunkWindowSouth(pbge.scenes.terrain.VariableTerrain):
    frames = (5,6,7)
    image_top = 'terrain_decor_junkwindows.png'

class JunkWindowEast(pbge.scenes.terrain.VariableTerrain):
    frames = (0,1,2)
    image_top = 'terrain_decor_junkwindows.png'

class SteelPipeEastTop(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_pipes.png'

class SteelPipeEastMid(pbge.scenes.terrain.Terrain):
    frame = 2
    image_top = 'terrain_decor_pipes.png'

class SteelPipeSouthTop(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_pipes.png'

class SteelPipeSouthMid(pbge.scenes.terrain.Terrain):
    frame = 3
    image_top = 'terrain_decor_pipes.png'

class RoofStuff(pbge.scenes.terrain.VariableTerrain):
    frames = (0,1,2,3,4,5,6,7)
    image_top = 'terrain_decor_roofstuff.png'

class VentFanEast(pbge.scenes.terrain.AnimTerrain):
    frames = (0,1,2)
    image_top = 'terrain_decor_ventfan.png'
    anim_delay = 2

class VentFanSouth(pbge.scenes.terrain.AnimTerrain):
    frames = (3,4,5)
    image_top = 'terrain_decor_ventfan.png'
    anim_delay = 2

class AlliedArmorSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_alliedarmor.png'

class AlliedArmorSignSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_alliedarmor.png'

class AlliedArmorSignEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_alliedarmor.png'

class ScrapIronBuilding(pbge.randmaps.terrset.BuildingSet):
    TERRAIN_TYPE = ScrapIronBuildingTerrain
    DEFAULT_DECOR_OPTIONS = (pbge.randmaps.terrset.WallDecor((JunkWindowSouth,), (JunkWindowEast,)),
                             pbge.randmaps.terrset.WallHanger(SteelPipeSouthTop,SteelPipeSouthMid,SteelPipeSouthMid,SteelPipeEastTop,SteelPipeEastMid,SteelPipeEastMid),
                             pbge.randmaps.terrset.RoofDecor((RoofStuff,)),
                             pbge.randmaps.terrset.WallDecor((VentFanSouth,), (VentFanEast,)),
                             )

class BrickBuildingTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_bottom = 'terrain_building_brick_b.png'
    image_top = 'terrain_building_brick.png'
    blocks = (Walking,Skimming,Rolling,Flying)

class BrickBuilding(pbge.randmaps.terrset.BuildingSet):
    TERRAIN_TYPE = BrickBuildingTerrain
    DEFAULT_DECOR_OPTIONS = (pbge.randmaps.terrset.WallDecor((WindowSouth,), (WindowEast,)),
                             pbge.randmaps.terrset.WallHanger(SteelPipeSouthTop,SteelPipeSouthMid,SteelPipeSouthMid,SteelPipeEastTop,SteelPipeEastMid,SteelPipeEastMid),
                             pbge.randmaps.terrset.RoofDecor((RoofStuff,)),
                             )

class ResidentialBuildingTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_bottom = 'terrain_building_residential_b.png'
    image_top = 'terrain_building_residential.png'
    blocks = (Walking,Skimming,Rolling,Flying)

class ResidentialBuilding(pbge.randmaps.terrset.BuildingSet):
    TERRAIN_TYPE = ResidentialBuildingTerrain
    DEFAULT_DECOR_OPTIONS = (pbge.randmaps.terrset.RoofDecor((RoofStuff,)),

                             )
    UF1_TILE = (15,)
    UF2_TILE = (16,)
    UF3_TILE = (17,)
    UF4_TILE = (18,)
    UF5_TILE = (19,)
    GF1_TILE = (20,)
    GF2_TILE = (21,)
    GF3_TILE = (22,)
    GF4_TILE = (23,)
    GF5_TILE = (24,)

class ScreenDoorTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_screendoor.png'

class WoodenDoorTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_woodendoor.png'

class ScreenWindow(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_screenwindow.png'
