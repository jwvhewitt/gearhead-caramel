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

class MSWreckage(pbge.scenes.terrain.VariableTerrain):
    image_top = 'terrain_decor_mswreckage.png'
    frames = (0,1)
    blocks = (Walking,Skimming,Rolling)
    movement_cost={pbge.scenes.movement.Vision:10}

class Smoke( pbge.scenes.terrain.AnimTerrain ):
    image_top = 'terrain_decor_smoke.png'
    anim_delay = 5
    transparent = True
    movement_cost={pbge.scenes.movement.Vision:10}
    @classmethod
    def render_top( self, original_dest, view, x, y ):
        """Custom rendering, because we can do that."""
        dest = original_dest.move(0,-32)
        spr = view.get_terrain_sprite( self.image_top, (x,y), transparent=self.transparent )
        spr.render( dest, self.frames[(view.phase // self.anim_delay + ( x + y ) * 4 ) % len(self.frames)] )

class GreenZoneGrass( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_grass.png'

class Flagstone( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_flagstone.png'
    border = pbge.scenes.terrain.FloorBorder( GreenZoneGrass, 'terrain_border_grassy.png' )

class DeadZoneGround( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_dzground.png'
    border = pbge.scenes.terrain.FloorBorder( Water, 'terrain_border_beach.png' )

class SemiDeadZoneGround( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_dzground.png'
    border = pbge.scenes.terrain.FloorBorder( GreenZoneGrass, 'terrain_border_grassy.png' )

class Pavement( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_pavement.png'


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

class GrateFloor( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_floor_grate.png'

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

class Bones( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_decor_bones.png'


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

class WoodenWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_wood.png'
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

class MSRuinedWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_msruins.png'
    blocks = (Walking,Skimming,Rolling,Vision)


class StoneWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_stone.png'
    blocks = (Walking,Skimming,Rolling,Vision,Flying)


class WallStones(pbge.scenes.terrain.OnTheWallVariableTerrain):
    image_top = 'terrain_decor_wallstones.png'
    south_frames = (8,9,10,11,12,13,14,15)
    east_frames = (0,1,2,3,4,5,6,7)


class FloorStones(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_decor_floorstones.png'

class OrganicWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_organic.png'
    blocks = (Walking,Skimming,Rolling,Vision,Flying)

class OrganicFloor(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_organic.png'

class OrganicTubeTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'prop_biotech.png'
    frame = 1
    blocks = (Walking,Skimming,Rolling,Vision,Flying)


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

class OldCrateTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_default.png'
    frame = 1
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

class MechEngTerminalTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_mechengterminal.png'

class CyberdocTerminalTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    # TODO: Give the Cyberdoc Terminal its own graphic.
    image_top = 'terrain_decor_mechengterminal.png'

class MechaPosterTerrain(pbge.scenes.terrain.OnTheWallVariableTerrain):
    image_top = 'terrain_decor_posters_mecha.png'
    south_frames = (1,3,5,7)
    east_frames = (0,2,4,6)

class Cybertendrils(pbge.scenes.terrain.OnTheWallVariableTerrain):
    image_top = 'terrain_decor_cybertendrils.png'
    south_frames = (8,9,10,11,12,13,14,15)
    east_frames = (0,1,2,3,4,5,6,7)

class TekruinsWallDecor(pbge.scenes.terrain.OnTheWallVariableTerrain):
    image_top = 'terrain_decor_tekruins.png'
    south_frames = (8,9,10,11,12,13,14,15)
    east_frames = (0,1,2,3,4,5,6,7)

class Tekdebris( pbge.scenes.terrain.VariableTerrain ):
    image_bottom = 'terrain_decor_tekdebris.png'


class DZDWConcreteBuilding(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_worldprops.png'
    frame = 2
    blocks = (Walking,Skimming,Rolling,Flying)


class DZDConcreteBuilding(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_mechaprops.png'
    frame = 1
    blocks = (Walking,Skimming,Rolling,Flying)

class DZDDefiledFactoryTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_mechaprops.png'
    frame = 2
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

class GlassDoorTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_glassdoor.png'

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

class SteelPipeSouthMid(pbge.scenes.terrain.Terrain):
    frame = 3
    image_top = 'terrain_decor_pipes.png'

class SteelPipe(pbge.scenes.terrain.OnTheWallVariableTerrain):
    east_frames = (0,2,2)
    south_frames = (1,3,3)
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

class VentFanTerrain(pbge.scenes.terrain.OnTheWallAnimTerrain):
    east_frames = (0,1,2)
    south_frames = (3,4,5)
    image_top = 'terrain_decor_ventfan.png'
    anim_delay = 2

class TorchTerrain(pbge.scenes.terrain.OnTheWallAnimTerrain):
    east_frames = (0,2)
    south_frames = (1,3)
    image_top = 'terrain_decor_torch.png'
    anim_delay = 2

class BlueTorchTerrain(pbge.scenes.terrain.OnTheWallAnimTerrain):
    east_frames = (0,2)
    south_frames = (1,3)
    image_top = 'terrain_decor_torch_b.png'
    anim_delay = 2

class GreenBoardingChuteTerrain(pbge.scenes.terrain.OnTheWallAnimTerrain):
    east_frames = (0,2)
    south_frames = (1,3)
    image_top = 'terrain_decor_boardingchute_green.png'
    anim_delay = 5

class RedBoardingChuteTerrain(pbge.scenes.terrain.OnTheWallAnimTerrain):
    east_frames = (0,2)
    south_frames = (1,3)
    image_top = 'terrain_decor_boardingchute_red.png'
    anim_delay = 5

class AlliedArmorSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_alliedarmor.png'

class AlliedArmorSignSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_alliedarmor.png'

class AlliedArmorSignEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_alliedarmor.png'

class FixitShopSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_fixitsign.png'

class FixitShopSignSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_fixitsign.png'

class FixitShopSignEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_fixitsign.png'

class RustyFixitShopSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_fixitsign_rusty.png'

class RustyFixitShopSignSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_fixitsign_rusty.png'

class RustyFixitShopSignEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_fixitsign_rusty.png'


class CrossedSwordsTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_crossedswords.png'

class CrossedSwordsTerrainSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_crossedswords.png'

class CrossedSwordsTerrainEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_crossedswords.png'


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

class WhiteBrickBuildingTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_bottom = 'terrain_building_brick_b.png'
    image_top = 'terrain_building_whitebrick.png'
    blocks = (Walking,Skimming,Rolling,Flying)

class WhiteBrickBuilding(BrickBuilding):
    TERRAIN_TYPE = WhiteBrickBuildingTerrain

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


class IndustrialBuildingTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_bottom = 'terrain_building_industrial_b.png'
    image_top = 'terrain_building_industrial.png'
    blocks = (Walking,Skimming,Rolling,Flying)


class IndustrialBuilding(pbge.randmaps.terrset.BuildingSet):
    TERRAIN_TYPE = IndustrialBuildingTerrain
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


class CommercialBuildingTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_bottom = 'terrain_building_commercial_b.png'
    image_top = 'terrain_building_commercial.png'
    blocks = (Walking,Skimming,Rolling,Flying)


class CommercialBuilding(pbge.randmaps.terrset.BuildingSet):
    TERRAIN_TYPE = CommercialBuildingTerrain
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


class ConcreteBuildingTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_bottom = 'terrain_building_concrete_b.png'
    image_top = 'terrain_building_concrete.png'
    blocks = (Walking,Skimming,Rolling,Flying)


class ConcreteBuilding(pbge.randmaps.terrset.BuildingSet):
    TERRAIN_TYPE = ConcreteBuildingTerrain
    DEFAULT_DECOR_OPTIONS = (pbge.randmaps.terrset.WallDecor((WindowSouth,), (WindowEast,)),
                             pbge.randmaps.terrset.WallHanger(SteelPipeSouthTop,SteelPipeSouthMid,SteelPipeSouthMid,SteelPipeEastTop,SteelPipeEastMid,SteelPipeEastMid),
                             pbge.randmaps.terrset.RoofDecor((RoofStuff,)),
                             )


class ScreenDoorTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_screendoor.png'

class WoodenDoorTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_woodendoor.png'

class ScreenWindow(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_screenwindow.png'

class KojedoModelTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_mechamodels.png'
    frame = 0
    blocks = (Walking,Skimming,Rolling,Flying)

class BuruBuruModelTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_mechamodels.png'
    frame = 1
    blocks = (Walking,Skimming,Rolling,Flying)

class GladiusModelTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_mechamodels.png'
    frame = 2
    blocks = (Walking,Skimming,Rolling,Flying)

class VadelModelTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_mechamodels.png'
    frame = 3
    blocks = (Walking,Skimming,Rolling,Flying)

class HarpyModelTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_mechamodels.png'
    frame = 4
    blocks = (Walking,Skimming,Rolling,Flying)

class ClaymoreModelTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_mechamodels.png'
    frame = 5
    blocks = (Walking,Skimming,Rolling,Flying)

class MechaModelTerrain(pbge.scenes.terrain.VariableTerrain):
    image_top = 'terrain_decor_mechamodels.png'
    frames = (0,1,2,3,4,5)
    blocks = (Walking,Skimming,Rolling,Flying)

class MapTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_map.png'

class EarthMapTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_earthmap.png'

class LockersTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_lockers.png'

class ShippingShelvesTerrain(pbge.scenes.terrain.OnTheWallVariableTerrain):
    image_top = 'terrain_decor_shippingshelves.png'
    south_frames = (1,3,5,7)
    east_frames = (0,2,4,6)

class NorthSouthShelvesTerrain(pbge.scenes.terrain.VariableTerrain):
    image_top = 'terrain_decor_nsshelves.png'
    blocks = (Walking,Skimming,Rolling,Flying)
    movement_cost={pbge.scenes.movement.Vision:10}

class UlsaniteDesk(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_office_ulsanite.png'
    frame = 0
    blocks = (Walking,Skimming,Rolling)
    movement_cost={pbge.scenes.movement.Vision:5}

class UlsaniteChair(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_office_ulsanite.png'
    frame = 1
    blocks = (Walking,Skimming,Rolling)
    movement_cost={pbge.scenes.movement.Vision:5}

class UlsaniteFilingCabinetTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_office_ulsanite.png'
    SOUTH_FRAME = 3
    EAST_FRAME = 2

class UlsaniteBookshelfTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_office_ulsanite.png'
    SOUTH_FRAME = 5
    EAST_FRAME = 4

class RegExLogoTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_logo_regex.png'

class HamsterCageTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_hamstercage.png'

class StairsUpTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_stairs.png'
    blocks = (Walking,Skimming,Rolling,Flying)
    movement_cost={pbge.scenes.movement.Vision:5}

class StairsDownTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_stairs.png'
    blocks = (Walking,Skimming,Rolling,Flying)
    movement_cost={pbge.scenes.movement.Vision:5}
    frame = 1

class TrapdoorTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_stairs.png'
    blocks = (Walking,Skimming,Rolling,Flying)
    movement_cost={pbge.scenes.movement.Vision:5}
    frame = 2

class StoneStairsUpTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_stonestairs.png'
    blocks = (Walking,Skimming,Rolling,Flying)
    movement_cost={pbge.scenes.movement.Vision:5}

class HospitalSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_hospitalsign.png'

class HospitalSignSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_hospitalsign.png'

class HospitalSignEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_hospitalsign.png'

class BedTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_bed.png'
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}

class ParkStatueTerrain(pbge.scenes.terrain.VariableTerrain):
    image_top = 'terrain_decor_parkstatues.png'
    frames = (0,1,2,3,4)
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}

class ParkStatueManTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_parkstatues.png'
    frame = 0
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}

class ParkStatueWomanTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_parkstatues.png'
    frame = 1
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}

class ParkStatueMechaTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_parkstatues.png'
    frame = 2
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}

class ParkStatueSynthTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_parkstatues.png'
    frame = 3
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}

class ParkStatueSerpentTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_parkstatues.png'
    frame = 4
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}

class UndergroundEntranceTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_undergroundentrance.png'
    frame = 0
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}

class OldMainframeTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_oldmainframe.png'
    frame = 0
    blocks = (Walking,Skimming,Rolling,Flying)

class OldTerminalTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_default.png'
    frame = 2
    blocks = (Walking,Skimming,Rolling,Flying)

class BiotankTerrain(pbge.scenes.terrain.AnimTerrain):
    frames = (0,1,2,3,1,2,4,2,5,2,1,2,3,2,1,0,1,2,3,2,1,2,3,2,1)
    image_top = 'terrain_decor_biotank.png'
    anim_delay = 6
    blocks = (Walking,Skimming,Rolling,Flying)

class EmptyBiotankTerrain(pbge.scenes.terrain.Terrain):
    frame = 6
    image_top = 'terrain_decor_biotank.png'
    blocks = (Walking,Skimming,Rolling,Flying)

class BrokenBiotankTerrain(pbge.scenes.terrain.Terrain):
    frame = 7
    image_top = 'terrain_decor_biotank.png'
    blocks = (Walking,Skimming,Rolling,Flying)

class PZHoloTerrain(pbge.scenes.terrain.AnimTerrain):
    transparent = True
    frames = (1,2,3,4,5,6,7,6,5,4,3,2,3,4,5,6,7,6,5,4,3,2,1,2,3,4,5,6,7,6,5,4,3,2,3,5,1,4,7,2,6,7,6,5,4,3,2,
              1,2,3,4,5,6,7,6,5,4,3,2,1,2,3,4,5,6,7,6,5,4,3,2,1,2,3,4,5,4,3,4,5,6,5,4,3,2)
    image_top = "terrain_decor_pzholo.png"
    blocks = (Walking,Skimming,Rolling,Flying)
    anim_delay = 3
    @classmethod
    def render_top( self, dest, view, x, y ):
        """Draw terrain that should appear in front of a model in the same tile"""
        spr = view.get_terrain_sprite( self.image_top, (x,y), transparent=False)
        spr.render(dest, 0)
        spr = view.get_terrain_sprite( self.image_top, (x,y), transparent=True)
        spr.render( dest, self.frames[(view.phase // self.anim_delay + ( x + y ) * 4 ) % len(self.frames)] )

class BarTerrain(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_swall_bar.png'
    bordername = None
    altitude = 0
    blocks = (Walking, Skimming, Rolling)
    movement_cost={pbge.scenes.movement.Vision:5}


class AngelEggTerrain(pbge.scenes.terrain.Terrain):
    frame = 3
    image_top = 'terrain_dzd_mechaprops.png'
    blocks = (Walking,Skimming,Rolling)
