import pbge
import gears
from pbge.scenes.movement import Walking, Flying, Vision
from gears.tags import Skimming, Rolling, Cruising, SpaceFlight
import random
from gears.geffects import TerrainBreaker
from pbge.scenes.terrain import Terrain



class Forest(pbge.scenes.terrain.VariableTerrain):
    image_top = 'terrain_trees_fg.png'
    image_middle = 'terrain_trees_bg.png'
    movement_cost = {pbge.scenes.movement.Walking: 1.5, gears.tags.Skimming: 2.0, gears.tags.Rolling: 2.0,
                     pbge.scenes.movement.Vision: 5}
    breaker = TerrainBreaker(10, None)
    tags = {gears.tags.TERRAIN_FLAMMABLE,}


class Bushes(pbge.scenes.terrain.VariableTerrain):
    image_top = 'terrain_bushes.png'
    movement_cost = {pbge.scenes.movement.Vision: 5}
    blocks = (Walking, Skimming, Rolling, Cruising)
    breaker = TerrainBreaker(10, None)
    tags = {gears.tags.TERRAIN_FLAMMABLE,}


class Water(pbge.scenes.terrain.AnimTerrain):
    image_biddle = 'terrain_water2.png'
    image_bottom = 'terrain_water1.png'
    altitude = -24
    transparent = True
    movement_cost = {pbge.scenes.movement.Walking: 3.0, gears.tags.Rolling: 3.0, Cruising: 1.0}
    border = pbge.scenes.terrain.FloorBorder('terrain_border_beach.png')
    border_priority = 1000

class DeepWater(pbge.scenes.terrain.AnimTerrain):
    image_biddle = 'terrain_water2.png'
    image_bottom = 'terrain_water1.png'
    altitude = -24
    transparent = True
    blocks = (Walking, Rolling, SpaceFlight)
    border = pbge.scenes.terrain.FloorBorder('terrain_border_beach.png')
    border_priority = 1000


class BorderMarkerSW(pbge.scenes.terrain.AnimTerrain):
    image_middle = 'terrain_decor_areaborder.png'
    frames = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    anim_delay = 1
    position_dependent = False


class BorderMarkerW(pbge.scenes.terrain.AnimTerrain):
    image_middle = 'terrain_decor_areaborder.png'
    frames = (10, 11, 12, 13, 14, 15, 16, 17, 18, 19)
    anim_delay = 1
    position_dependent = False


class BorderMarkerNW(pbge.scenes.terrain.AnimTerrain):
    image_middle = 'terrain_decor_areaborder.png'
    frames = (20, 21, 22, 23, 24, 25, 26, 27, 28, 29)
    anim_delay = 1
    position_dependent = False


class BorderMarkerN(pbge.scenes.terrain.AnimTerrain):
    image_middle = 'terrain_decor_areaborder.png'
    frames = (30, 31, 32, 33, 34, 35, 36, 37, 38, 39)
    anim_delay = 1
    position_dependent = False


class BorderMarkerNE(pbge.scenes.terrain.AnimTerrain):
    image_middle = 'terrain_decor_areaborder.png'
    frames = (40, 41, 42, 43, 44, 45, 46, 47, 48, 49)
    anim_delay = 1
    position_dependent = False


class BorderMarkerE(pbge.scenes.terrain.AnimTerrain):
    image_middle = 'terrain_decor_areaborder.png'
    frames = (50, 51, 52, 53, 54, 55, 56, 57, 58, 59)
    anim_delay = 1
    position_dependent = False


class BorderMarkerSE(pbge.scenes.terrain.AnimTerrain):
    image_middle = 'terrain_decor_areaborder.png'
    frames = (60, 61, 62, 63, 64, 65, 66, 67, 68, 69)
    anim_delay = 1
    position_dependent = False


class BorderMarkerS(pbge.scenes.terrain.AnimTerrain):
    image_middle = 'terrain_decor_areaborder.png'
    frames = (70, 71, 72, 73, 74, 75, 76, 77, 78, 79)
    anim_delay = 1
    position_dependent = False


class ToxicSludge(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_sludge.png'
    blocks = (Walking, Rolling, Cruising)
    border = pbge.scenes.terrain.FloorBorder('terrain_border_sludge.png')
    border_priority = 1200


class MSWreckage(pbge.scenes.terrain.VariableTerrain):
    image_top = 'terrain_decor_mswreckage.png'
    frames = (0, 1)
    blocks = (Walking, Skimming, Rolling, Cruising)
    movement_cost = {pbge.scenes.movement.Vision: 10}


class MSResidentialBuildings(pbge.scenes.terrain.VariableTerrain):
    image_top = 'terrain_buildings_residential.png'
    frames = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    blocks = (Walking, Skimming, Rolling, Cruising)
    movement_cost = {pbge.scenes.movement.Vision: 5}


class Smoke(pbge.scenes.terrain.AnimTerrain):
    image_top = 'terrain_decor_smoke.png'
    anim_delay = 5
    transparent = True
    movement_cost = {pbge.scenes.movement.Vision: 10}

    @classmethod
    def render_top(cls, dest, view, x, y):
        """Custom rendering, because we can do that."""
        new_dest = dest.move(0, -32)
        spr = view.get_terrain_sprite(cls.image_top, (x, y), transparent=cls.transparent)
        spr.render(new_dest, cls.frames[(view.phase // cls.anim_delay + (x + y) * 4) % len(cls.frames)])


class BrokenGround(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_rubble.png'
    border = pbge.scenes.terrain.FloorBorder('terrain_border_rubble.png')
    border_priority = 999
    blocks = (Cruising, SpaceFlight)
    movement_cost = {pbge.scenes.movement.Walking: 1.5, gears.tags.Rolling: 1.5,}


class GreenZoneGrass(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_grass.png'
    border = pbge.scenes.terrain.FloorBorder('terrain_border_grassy.png')
    border_priority = 200
    blocks = (Cruising, SpaceFlight)
    breaker = TerrainBreaker(20, BrokenGround, terrain_value=2)
    tags = {gears.tags.TERRAIN_FLAMMABLE,}


class Sand(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_sand.png'
    border = pbge.scenes.terrain.FloorBorder('terrain_border_sand.png')
    border_priority = 100
    blocks = (Cruising, SpaceFlight)


class Flagstone(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_flagstone.png'
    blocks = (Cruising, SpaceFlight)
    breaker = TerrainBreaker(15, BrokenGround, terrain_value=3)


class DeadZoneGround(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_dzground.png'
    border = pbge.scenes.terrain.FloorBorder('terrain_border_dzground.png')
    border_priority = 80
    blocks = (Cruising, SpaceFlight)
    breaker = TerrainBreaker(20, BrokenGround, terrain_value=0)


class SemiDeadZoneGround(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_dzground.png'
    border = pbge.scenes.terrain.FloorBorder('terrain_border_dzground.png')
    border_priority = 75
    blocks = (Cruising, SpaceFlight)
    breaker = TerrainBreaker(20, BrokenGround, terrain_value=0)


class Pavement(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_pavement.png'
    blocks = (Cruising, SpaceFlight)
    breaks_into=BrokenGround
    breaker = TerrainBreaker(15, DeadZoneGround, terrain_value=2)


class SmallDeadZoneGround(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_dzground2.png'
    border = pbge.scenes.terrain.FloorBorder('terrain_border_dzground2.png')
    border_priority = 45
    blocks = (Cruising, SpaceFlight)
    breaks_into=BrokenGround


class TechnoRubble(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_technorubble.png'
    border = pbge.scenes.terrain.FloorBorder('terrain_border_technoedge.png')
    border_priority = 55
    blocks = (Cruising, SpaceFlight)
    breaker = TerrainBreaker(10, DeadZoneGround)
    tags = {gears.tags.TERRAIN_FLAMMABLE,}


class OldTilesFloor(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_oldtiles.png'
    blocks = (Cruising, SpaceFlight)


class MSConcreteSlabFloor(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_ground_msconcreteslab.png'
    blocks = (Cruising, SpaceFlight)


class WhiteTileFloor(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_whitetile.png'
    blocks = (Cruising, SpaceFlight)


class HardwoodFloor(pbge.scenes.terrain.VariableTerrain):
    blocks = (Cruising, SpaceFlight)
    image_bottom = 'terrain_floor_hardwood.png'


class GrateFloor(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_grate.png'
    blocks = (Cruising, SpaceFlight)


class BlueSlabFloor(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_blueslab.png'
    blocks = (Cruising, SpaceFlight)


class GreenSlabFloor(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_greenslab.png'
    blocks = (Cruising, SpaceFlight)


class CrackedEarth(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_crackedearth.png'
    border = pbge.scenes.terrain.FloorBorder('terrain_border_crackedearth.png')
    border_priority = 50
    blocks = (Cruising, SpaceFlight)
    breaker = TerrainBreaker(20, BrokenGround, terrain_value=0)


class WorldMapRoad(pbge.scenes.terrain.RoadTerrain):
    image_bottom = 'terrain_decor_worldroad.png'
    blocks = (Cruising, SpaceFlight)


class Snow(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_snow.png'
    border = pbge.scenes.terrain.FloorBorder('terrain_border_snowline.png')
    border_priority = 300
    blocks = (Cruising, SpaceFlight)


class SmallSnow(pbge.scenes.terrain.VariableTerrain):
    # As above, but uses the human scale graphics.
    image_bottom = 'terrain_floor_snow_small.png'
    border = pbge.scenes.terrain.FloorBorder('terrain_border_snowline.png')
    border_priority = 300
    blocks = (Cruising, SpaceFlight)


class Bones(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_decor_bones.png'


class Mountain(pbge.scenes.terrain.HillTerrain):
    altitude = 20
    image_middle = 'terrain_hill_1.png'
    # image_bottom = 'terrain_hill_1.png'
    bordername = ''
    blocks = (Cruising, SpaceFlight)


class VendingMachineTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_vendingmachine.png'
    blocks = (Walking, Skimming, Rolling)


class WinterMochaBarrelTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha.png'
    frame = 0
    blocks = (Walking, Skimming, Rolling)


class WinterMochaBrokenShovel(pbge.scenes.terrain.Terrain):
    image_middle = 'terrain_wintermocha.png'
    frame = 1


class WinterMochaToolboxTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha.png'
    frame = 2
    blocks = (Walking, Skimming, Rolling)


class ExitTerrain(pbge.scenes.terrain.AnimTerrain):
    image_top = 'terrain_wp_exit.png'
    transparent = True
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)
    frames = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    anim_delay = 1


class AegisWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_aegis.png'
    blocks = (Walking, Skimming, Rolling, Vision, Cruising, SpaceFlight)


class AegisFloor(pbge.scenes.terrain.Terrain):
    image_bottom = 'terrain_floor_aegis.png'
    blocks = (Cruising, SpaceFlight)



class FortressWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_fortress.png'
    blocks = (Walking, Skimming, Rolling, Vision, Cruising, SpaceFlight)


class ScrapIronWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_rusty.png'
    blocks = (Walking, Skimming, Rolling, Vision, Cruising, SpaceFlight)


class DefaultWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_default.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class CommercialWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_commercial.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class ResidentialWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_residential.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class DingyResidentialWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_residential_dingy.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class WoodenWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_wood.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class HospitalWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_hospital.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class IndustrialWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_industrial.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class DragonTeethWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_dragonteeth.png'
    bordername = None
    altitude = 20
    blocks = (Walking, Skimming, Rolling, Cruising, SpaceFlight)
    movement_cost = {pbge.scenes.movement.Vision: 5}


class MechaFortressWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_mechfort.png'
    bordername = None
    #altitude = 20
    blocks = (Walking, Skimming, Rolling, Cruising, SpaceFlight)
    movement_cost = {pbge.scenes.movement.Vision: 50}
    

class JunkyardWall(pbge.scenes.terrain.VariableTerrain):
    image_top = 'terrain_wall_junkyard.png'
    bordername = None
    altitude = 20
    frames = tuple(range(16))
    blocks = (Walking, Skimming, Rolling, Cruising, SpaceFlight)
    movement_cost = {pbge.scenes.movement.Vision: 5}
    breaker = TerrainBreaker(30, None)
    tags = {gears.tags.TERRAIN_FLAMMABLE,}


class SandDuneWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_dune.png'
    bordername = None
    altitude = 20
    blocks = (Walking, Skimming, Rolling, Cruising, SpaceFlight)
    movement_cost = {pbge.scenes.movement.Vision: 5}


class MSRuinedWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_msruins.png'
    blocks = (Walking, Skimming, Rolling, Vision, Cruising, SpaceFlight)


class StoneWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_stone.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class EarthWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_redearth.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class VehicleWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_vehicle.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class TentWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_tent.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class WarmColorsWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_warmcolors.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class CoolColorsWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_coolcolors.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class WallStones(pbge.scenes.terrain.OnTheWallVariableTerrain):
    image_top = 'terrain_decor_wallstones.png'
    south_frames = (8, 9, 10, 11, 12, 13, 14, 15)
    east_frames = (0, 1, 2, 3, 4, 5, 6, 7)
    blocks = (Cruising, SpaceFlight)


class FloorStones(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_decor_floorstones.png'
    blocks = (Cruising, SpaceFlight)


class OrganicWall(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_wall_organic.png'
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class OrganicFloor(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_organic.png'
    blocks = (Cruising, SpaceFlight)


class GreenTileFloor(pbge.scenes.terrain.Terrain):
    image_bottom = 'terrain_floor_greentile.png'
    blocks = (Cruising, SpaceFlight)


class GravelFloor(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_floor_gravel.png'
    blocks = (Cruising, SpaceFlight)


class OrganicTubeTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'prop_biotech.png'
    frame = 1
    blocks = (Walking, Skimming, Rolling, Vision, Flying, Cruising, SpaceFlight)


class DZDTownTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_worldprops.png'
    frame = 0
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class DZDWCommTowerTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_worldprops.png'
    frame = 1
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class DZDCommTowerTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_mechaprops.png'
    frame = 0
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class VictimTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_default.png'
    frame = 0
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class OldCrateTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_containers.png'
    frame = 0
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class OpenOldCrateTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_containers.png'
    frame = 1
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class AmmoBoxTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_containers.png'
    frame = 2
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class OpenAmmoBoxTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_containers.png'
    frame = 3
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class StorageBoxTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_containers.png'
    frame = 4
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class OpenStorageBoxTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_containers.png'
    frame = 5
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class SteelBoxTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_gervais_decor.png'
    frame = 4
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class OpenSteelBoxTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_gervais_decor.png'
    frame = 5
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


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
    south_frames = (1, 3, 5, 7, 9)
    east_frames = (0, 2, 4, 6, 8)


class GervaisWeaponRacks(pbge.scenes.terrain.OnTheWallVariableTerrain):
    image_top = 'terrain_gervais_decor_weaponracks.png'
    south_frames = (1, 3, 5, 7, 9)
    east_frames = (0, 2, 4, 6, 8)


class ArmorCabinetTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_armorcabinet.png'


class ArmorMannequinTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_armormannequin.png'


class ProvisionsTerrain(pbge.scenes.terrain.OnTheWallVariableTerrain):
    image_top = 'terrain_gervais_decor_provisions.png'
    south_frames = (1, 3)
    east_frames = (0, 2)


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
    south_frames = (1, 3, 5, 7)
    east_frames = (0, 2, 4, 6)


class Cybertendrils(pbge.scenes.terrain.OnTheWallVariableTerrain):
    image_top = 'terrain_decor_cybertendrils.png'
    south_frames = (8, 9, 10, 11, 12, 13, 14, 15)
    east_frames = (0, 1, 2, 3, 4, 5, 6, 7)


class TekruinsWallDecor(pbge.scenes.terrain.OnTheWallVariableTerrain):
    image_top = 'terrain_decor_tekruins.png'
    south_frames = (8, 9, 10, 11, 12, 13, 14, 15)
    east_frames = (0, 1, 2, 3, 4, 5, 6, 7)


class Tekdebris(pbge.scenes.terrain.VariableTerrain):
    image_bottom = 'terrain_decor_tekdebris.png'


class DZDWConcreteBuilding(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_worldprops.png'
    frame = 2
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class DZDConcreteBuilding(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_mechaprops.png'
    frame = 1
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class MechaScaleMineBuildingTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'prop_dzd_buildings.png'
    frame = 0
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class DZDDefiledFactoryTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_dzd_mechaprops.png'
    frame = 2
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class MetalDoorClosed(pbge.scenes.terrain.DoorTerrain):
    image_top = 'terrain_door_metal.png'
    frame = 0
    blocks = (Walking, Skimming, Rolling, Flying, Vision, Cruising, SpaceFlight)


class MetalDoorOpen(pbge.scenes.terrain.DoorTerrain):
    image_middle = 'terrain_door_metal.png'
    frame = 2
    blocks = ()


class ScrapIronBuildingTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_bottom = 'terrain_building_scrapiron_b.png'
    image_top = 'terrain_building_scrapiron.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class ScrapIronDoorTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_scrapirondoor.png'


class GlassDoorTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_glassdoor.png'


class ReinforcedDoorTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_door_reinforced.png'


class JunkWindowSouth(pbge.scenes.terrain.VariableTerrain):
    frames = (5, 6, 7)
    image_top = 'terrain_decor_junkwindows.png'


class JunkWindowEast(pbge.scenes.terrain.VariableTerrain):
    frames = (0, 1, 2)
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


class SteelPipe(pbge.scenes.terrain.OnTheWallVariableTerrain):
    east_frames = (0, 2, 2)
    south_frames = (1, 3, 3)
    image_top = 'terrain_decor_pipes.png'


class RoofStuff(pbge.scenes.terrain.VariableTerrain):
    frames = (0, 1, 2, 3, 4, 5, 6, 7)
    image_top = 'terrain_decor_roofstuff.png'


class VentFanEast(pbge.scenes.terrain.AnimTerrain):
    frames = (0, 1, 2)
    image_top = 'terrain_decor_ventfan.png'
    anim_delay = 2


class VentFanSouth(pbge.scenes.terrain.AnimTerrain):
    frames = (3, 4, 5)
    image_top = 'terrain_decor_ventfan.png'
    anim_delay = 2


class VentFanTerrain(pbge.scenes.terrain.OnTheWallAnimTerrain):
    east_frames = (0, 1, 2)
    south_frames = (3, 4, 5)
    image_top = 'terrain_decor_ventfan.png'
    anim_delay = 2


class TorchTerrain(pbge.scenes.terrain.OnTheWallAnimTerrain):
    east_frames = (0, 2)
    south_frames = (1, 3)
    image_top = 'terrain_decor_torch.png'
    anim_delay = 2


class BlueTorchTerrain(pbge.scenes.terrain.OnTheWallAnimTerrain):
    east_frames = (0, 2)
    south_frames = (1, 3)
    image_top = 'terrain_decor_torch_b.png'
    anim_delay = 2


class GreenBoardingChuteTerrain(pbge.scenes.terrain.OnTheWallAnimTerrain):
    east_frames = (0, 2)
    south_frames = (1, 3)
    image_top = 'terrain_decor_boardingchute_green.png'
    anim_delay = 5


class RedBoardingChuteTerrain(pbge.scenes.terrain.OnTheWallAnimTerrain):
    east_frames = (0, 2)
    south_frames = (1, 3)
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


class BladesOfCrihnaSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_bladesofcrihna.png'


class BladesOfCrihnaSignSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_bladesofcrihna.png'


class BladesOfCrihnaSignEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_bladesofcrihna.png'


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


class KettelLogoTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_kettellogo.png'


class KettelLogoTerrainSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_kettellogo.png'


class KettelLogoTerrainEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_kettellogo.png'


class RegExLogoTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_logo_regex.png'


class RegExLogoTerrainSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_logo_regex.png'


class RegExLogoTerrainEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_logo_regex.png'


class BioCorpLogoTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_biocorplogo.png'


class BioCorpLogoTerrainSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_biocorplogo.png'


class BioCorpLogoTerrainEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_biocorplogo.png'


class AegisLogoSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_aegislogo.png'


class AegisLogoSignSouth(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_aegislogo.png'
    frame = 0


class AegisLogoSignEast(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_aegislogo.png'
    frame = 1


class SolarNavyLogoSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_solarnavylogo.png'


class SolarNavyLogoSignSouth(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_solarnavylogo.png'
    frame = 0


class SolarNavyLogoSignEast(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_solarnavylogo.png'
    frame = 1


class TownBanner(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_townbanner.png'


class TownBannerSouth(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_townbanner.png'
    frame = 0


class TownBannerEast(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_townbanner.png'
    frame = 1


class GoldTownHallSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_goldtownhallsign.png'


class GoldTownHallSignSouth(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_goldtownhallsign.png'
    frame = 0


class GoldTownHallSignEast(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_goldtownhallsign.png'
    frame = 1


class MilitarySign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_militarysign.png'


class MilitarySignSouth(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_militarysign.png'
    frame = 0


class MilitarySignEast(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_militarysign.png'
    frame = 1


class GeneralStoreSign1(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_generalstoresign1.png'


class GeneralStoreSign1South(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_generalstoresign1.png'
    frame = 0


class GeneralStoreSign1East(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_generalstoresign1.png'
    frame = 1


class TavernSign1(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_tavernsign.png'


class TavernSign1South(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_tavernsign.png'
    frame = 0


class TavernSign1East(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_tavernsign.png'
    frame = 1


class CafeSign1(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_cafesign.png'


class CafeSign1South(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_cafesign.png'
    frame = 0


class CafeSign1East(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_cafesign.png'
    frame = 1


class MechaModelSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_kenney_mechasign.png'


class MechaModelSignSouth(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_kenney_mechasign.png'
    frame = 0


class MechaModelSignEast(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_kenney_mechasign.png'
    frame = 1


class SkullWallSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_skulltown.png'
    SOUTH_FRAME = 2
    EAST_FRAME = 1


class SkullWallSignSouth(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_skulltown.png'
    frame = 1


class SkullWallSignEast(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_skulltown.png'
    frame = 2


class JollyRogerSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_pirateflag.png'


class JollyRogerSignSouth(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_pirateflag.png'
    frame = 0


class JollyRogerSignEast(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_pirateflag.png'
    frame = 1


class HospitalSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_hospitalsign.png'


class HospitalSignSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_hospitalsign.png'


class HospitalSignEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_hospitalsign.png'


class DragonSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_gervais_decor_dragonsign.png'


class DragonSignSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_gervais_decor_dragonsign.png'


class DragonSignEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_gervais_decor_dragonsign.png'


class KirasTattoosSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_kirasign.png'


class KirasTattoosSignSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_kirasign.png'


class KirasTattoosSignEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_kirasign.png'


class GunShopSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_gervais_decor_gunsign.png'


class GunShopSignSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_gervais_decor_gunsign.png'


class GunShopSignEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_gervais_decor_gunsign.png'


class YeOldeShopSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_gervais_decor_yeoldesign.png'


class YeOldeShopSignSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_gervais_decor_yeoldesign.png'


class YeOldeShopSignEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_gervais_decor_yeoldesign.png'


class ShieldSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_gervais_decor_shieldsign.png'


class ShieldSignSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_gervais_decor_shieldsign.png'


class ShieldSignEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_gervais_decor_shieldsign.png'


class CyberSign(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_gervais_decor_cybersign.png'


class CyberSignSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_gervais_decor_cybersign.png'


class CyberSignEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_gervais_decor_cybersign.png'


class BronzeHorseSignTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_bronzehorse.png'


class BronzeHorseTerrainSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_bronzehorse.png'


class BronzeHorseTerrainEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_bronzehorse.png'


class KnifeNoteTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_knifenote.png'


class HotelSignTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_hotelsign.png'


class HotelSignTerrainSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_hotelsign.png'


class HotelSignTerrainEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_hotelsign.png'


class UnionSignTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    # A tricolor grid representing solidarity and the power of the people. Each row and
    # column contains one red, one blue, and one white tile.
    image_top = 'terrain_decor_unionsign.png'


class UnionSignTerrainSouth(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_unionsign.png'


class UnionSignTerrainEast(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_decor_unionsign.png'



class ScrapIronBuilding(pbge.randmaps.terrset.BuildingSet):
    TERRAIN_TYPE = ScrapIronBuildingTerrain
    DEFAULT_DECOR_OPTIONS = (pbge.randmaps.terrset.WallDecor((JunkWindowSouth,), (JunkWindowEast,)),
                             pbge.randmaps.terrset.WallHanger(SteelPipeSouthTop, SteelPipeSouthMid, SteelPipeSouthMid,
                                                              SteelPipeEastTop, SteelPipeEastMid, SteelPipeEastMid),
                             pbge.randmaps.terrset.RoofDecor((RoofStuff,)),
                             pbge.randmaps.terrset.WallDecor((VentFanSouth,), (VentFanEast,)),
                             )


class BrickBuildingTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_middle = 'terrain_building_brick_b.png'
    image_top = 'terrain_building_brick.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class BrickBuilding(pbge.randmaps.terrset.BuildingSet):
    TERRAIN_TYPE = BrickBuildingTerrain
    DEFAULT_DECOR_OPTIONS = (pbge.randmaps.terrset.WallDecor((WindowSouth,), (WindowEast,)),
                             pbge.randmaps.terrset.WallHanger(SteelPipeSouthTop, SteelPipeSouthMid, SteelPipeSouthMid,
                                                              SteelPipeEastTop, SteelPipeEastMid, SteelPipeEastMid),
                             pbge.randmaps.terrset.RoofDecor((RoofStuff,)),
                             )


class WhiteBrickBuildingTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_bottom = 'terrain_building_brick_b.png'
    image_top = 'terrain_building_whitebrick.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class WhiteBrickBuilding(BrickBuilding):
    TERRAIN_TYPE = WhiteBrickBuildingTerrain


class ResidentialBuildingTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_bottom = 'terrain_building_residential_b.png'
    image_top = 'terrain_building_residential.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


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
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


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
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


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
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class ConcreteBuilding(pbge.randmaps.terrset.BuildingSet):
    TERRAIN_TYPE = ConcreteBuildingTerrain
    DEFAULT_DECOR_OPTIONS = (pbge.randmaps.terrset.WallDecor((WindowSouth,), (WindowEast,)),
                             pbge.randmaps.terrset.WallHanger(SteelPipeSouthTop, SteelPipeSouthMid, SteelPipeSouthMid,
                                                              SteelPipeEastTop, SteelPipeEastMid, SteelPipeEastMid),
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
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class BuruBuruModelTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_mechamodels.png'
    frame = 1
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class GladiusModelTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_mechamodels.png'
    frame = 2
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class VadelModelTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_mechamodels.png'
    frame = 3
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class HarpyModelTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_mechamodels.png'
    frame = 4
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class ClaymoreModelTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_mechamodels.png'
    frame = 5
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class MechaModelTerrain(pbge.scenes.terrain.VariableTerrain):
    image_top = 'terrain_decor_mechamodels.png'
    frames = (0, 1, 2, 3, 4, 5)
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class MapTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_map.png'


class EarthMapTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_earthmap.png'


class LockersTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_lockers.png'


class ShippingShelvesTerrain(pbge.scenes.terrain.OnTheWallVariableTerrain):
    image_top = 'terrain_decor_shippingshelves.png'
    south_frames = (1, 3, 5, 7)
    east_frames = (0, 2, 4, 6)


class LoungeTableTerrain(pbge.scenes.terrain.OnTheWallVariableTerrain):
    image_top = 'terrain_decor_loungetable.png'
    south_frames = (1, 3, 5, 7)
    east_frames = (0, 2, 4, 6)


class NorthSouthShelvesTerrain(pbge.scenes.terrain.VariableTerrain):
    image_top = 'terrain_decor_nsshelves.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)
    movement_cost = {pbge.scenes.movement.Vision: 10}


class UlsaniteDesk(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_office_ulsanite.png'
    frame = 0
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}


class UlsaniteChair(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_office_ulsanite.png'
    frame = 1
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}


class UlsaniteFilingCabinetTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_office_ulsanite.png'
    SOUTH_FRAME = 3
    EAST_FRAME = 2


class UlsaniteBookshelfTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_office_ulsanite.png'
    SOUTH_FRAME = 5
    EAST_FRAME = 4


class KenneyBunk(pbge.scenes.terrain.Terrain):
    image_top = "terrain_decor_kenney_milcamp.png"
    frame = 0
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}


class KenneyChairWest(pbge.scenes.terrain.Terrain):
    image_top = "terrain_decor_kenney_milcamp.png"
    frame = 1
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}

class KenneyChairSouth(pbge.scenes.terrain.Terrain):
    image_top = "terrain_decor_kenney_milcamp.png"
    frame = 2
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}

class KenneyChairEast(pbge.scenes.terrain.Terrain):
    image_top = "terrain_decor_kenney_milcamp.png"
    frame = 3
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}

class KenneyChairNorth(pbge.scenes.terrain.Terrain):
    image_top = "terrain_decor_kenney_milcamp.png"
    frame = 4
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}


class KenneyCrates(pbge.scenes.terrain.Terrain):
    image_top = "terrain_decor_kenney_milcamp.png"
    frame = 5
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 10}


class KenneyWoodenTable(pbge.scenes.terrain.Terrain):
    image_top = "terrain_decor_kenney_milcamp.png"
    frame = 6
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}


class KenneyCommandTable(pbge.scenes.terrain.Terrain):
    image_top = "terrain_decor_kenney_milcamp.png"
    frame = 7
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 10}


class TattooChairTerrain(pbge.scenes.terrain.Terrain):
    image_top = "terrain_decor_tattoochair.png"
    frame = 0
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 15}


class Dashboard1(pbge.scenes.terrain.Terrain):
    image_top = "terrain_decor_dashboard.png"
    frame = 0


class Dashboard2(pbge.scenes.terrain.Terrain):
    image_top = "terrain_decor_dashboard.png"
    frame = 1


class Dashboard3(pbge.scenes.terrain.Terrain):
    image_top = "terrain_decor_dashboard.png"
    frame = 2


class VehicleControlPanel(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = "terrain_decor_vehiclecontrolpanel.png"


class HamsterCageTerrain(pbge.scenes.terrain.OnTheWallTerrain):
    image_top = 'terrain_decor_hamstercage.png'


class StairsUpTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_stairs.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)
    movement_cost = {pbge.scenes.movement.Vision: 5}


class StairsDownTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_stairs.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)
    movement_cost = {pbge.scenes.movement.Vision: 5}
    frame = 1


class TrapdoorTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_stairs.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)
    movement_cost = {pbge.scenes.movement.Vision: 5}
    frame = 2


class TrailSignTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_stairs.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)
    movement_cost = {pbge.scenes.movement.Vision: 5}
    frame = 3


class StoneStairsUpTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_stonestairs.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)
    movement_cost = {pbge.scenes.movement.Vision: 5}


class BedTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_bed.png'
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}


class OccupiedBedTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_occupiedbed.png'
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}


class ParkStatueTerrain(pbge.scenes.terrain.VariableTerrain):
    image_top = 'terrain_decor_parkstatues.png'
    frames = (0, 1, 2, 3, 4)
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
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class OldTerminalTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_decor_default.png'
    frame = 2
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class BiotankTerrain(pbge.scenes.terrain.AnimTerrain):
    frames = (0, 1, 2, 3, 1, 2, 4, 2, 5, 2, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 2, 3, 2, 1)
    image_top = 'terrain_decor_biotank.png'
    anim_delay = 6
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class EmptyBiotankTerrain(pbge.scenes.terrain.Terrain):
    frame = 6
    image_top = 'terrain_decor_biotank.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class BrokenBiotankTerrain(pbge.scenes.terrain.Terrain):
    frame = 7
    image_top = 'terrain_decor_biotank.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class FusionCoreOnTerrain(pbge.scenes.terrain.AnimTerrain):
    frames = (0, 1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1)
    image_top = 'terrain_decor_fusioncore.png'
    anim_delay = 3
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class FusionCoreOffTerrain(pbge.scenes.terrain.Terrain):
    frame = 7
    image_top = 'terrain_decor_fusioncore.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class PZHoloTerrain(pbge.scenes.terrain.AnimTerrain):
    transparent = True
    frames = (
        1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 3, 5, 1,
        4, 7,
        2, 6, 7, 6, 5, 4, 3, 2,
        1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 4, 3, 4, 5, 6, 5, 4, 3,
        2)
    image_top = "terrain_decor_pzholo.png"
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)
    anim_delay = 3

    @classmethod
    def render_top(cls, dest, view, x, y):
        """Draw terrain that should appear in front of a model in the same tile"""
        spr = view.get_terrain_sprite(cls.image_top, (x, y), transparent=False)
        spr.render(dest, 0)
        spr = view.get_terrain_sprite(cls.image_top, (x, y), transparent=True)
        spr.render(dest, cls.frames[(view.phase // cls.anim_delay + (x + y) * 4) % len(cls.frames)])


class BarTerrain(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_swall_bar.png'
    bordername = None
    altitude = 0
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}
    TAKES_WALL_DECOR = False


class ShopCounterTerrain(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_swall_shopcounter.png'
    bordername = None
    altitude = 0
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}
    TAKES_WALL_DECOR = False


class WorkbenchTerrain(pbge.scenes.terrain.WallTerrain):
    image_top = 'terrain_swall_workbench.png'
    bordername = None
    altitude = 0
    blocks = (Walking, Skimming, Rolling)
    movement_cost = {pbge.scenes.movement.Vision: 5}
    TAKES_WALL_DECOR = False


class AngelEggTerrain(pbge.scenes.terrain.Terrain):
    frame = 3
    image_top = 'terrain_dzd_mechaprops.png'
    blocks = (Walking, Skimming, Rolling)


class SkullTownSignTerrain(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_decor_skulltown.png'
    blocks = (Walking, Skimming, Rolling)


class ShrineTerrain(pbge.scenes.terrain.Terrain):
    frame = 3
    image_top = 'terrain_decor_default.png'
    blocks = (Walking, Skimming, Rolling)


class SkeletonTerrain(pbge.scenes.terrain.Terrain):
    frame = 1
    image_top = 'terrain_gervais_decor.png'
    blocks = (Walking, Skimming, Rolling)


class PitTerrain(pbge.scenes.terrain.Terrain):
    frame = 0
    image_top = 'terrain_gervais_decor.png'
    blocks = (Walking, Skimming, Rolling)


class TableAndChairsTerrain(pbge.scenes.terrain.Terrain):
    frame = 2
    image_top = 'terrain_gervais_decor.png'
    blocks = (Walking, Skimming, Rolling)


class Wrecks(pbge.scenes.terrain.VariableTerrain):
    frames = (0, 1, 2, 3)
    image_top = 'terrain_decor_wrecks.png'
    blocks = (Walking, Skimming, Rolling)


class HerbsTerrain(pbge.scenes.terrain.Terrain):
    frame = 3
    image_top = 'terrain_gervais_decor.png'
    blocks = (Walking, Skimming, Rolling)


class CorsairTDFTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_top = 'terrain_terrset_corsair_tdf.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class CorsairDuckDict(dict):
    # Pass this to the Terrset if you want a Corsair in anything other than the Terran Defense Force colors.
    def __init__(self, colors):
        super().__init__(blocks=CorsairTDFTerrain.blocks, colors=colors, image_top='terrain_terrset_corsair.png')


class CorsairTerrset(pbge.randmaps.terrset.TerrSet):
    TERRAIN_TYPE = CorsairTDFTerrain
    TERRAIN_MAP = (
        (0, 1, 2, 3, 4),
        (5, 6, 7, 8, 9, 10),
        (None, 11, 12, 13, 14, 15, 16),
        (None, None, 18, 19, 20, 21, 22, 23),
        (None, None, 24, 25, 26, 27, 28, 29, 30),
        (None, None, None, 31, 32, 33, 34, 35, 36),
        (None, None, None, 37, 38, 39, 40, 41, 42, 43),
        (None, None, None, None, 44, 45, 46, 47, 48, 49, 50),
        (None, None, None, None, None, 51, 52, 53, 54, 55, 56),
        # (None,None,None,None, 57,58,59)
    )

class TentTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_top = 'terrain_terrset_tent.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class TentTerrset(pbge.randmaps.terrset.TerrSet):
    TERRAIN_TYPE = TentTerrain
    TERRAIN_MAP = (
        (0,1,2),
        (3,4,5),
        (6,7,8,9),
        (10,11,12,13)
    )
    WAYPOINT_POS = {
        "DOOR": (1, 3)
    }


class MobileHQTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_top = 'terrain_terrset_mobilehq.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class MobileHQTerrset(pbge.randmaps.terrset.TerrSet):
    TERRAIN_TYPE = MobileHQTerrain
    TERRAIN_MAP = (
        (1,2),
        (4,5,6),
        (8,9,10,11),
        (13,14,15,16),
        (17,18,19,20),
        (None,22,23,24),
        (None,25,26,27)
    )
    WAYPOINT_POS = {
        "DOOR": (3, 5)
    }


class FieldHospitalTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_top = 'terrain_terrset_fieldhospital.png'
    blocks = (Walking, Skimming, Rolling, Flying, Cruising, SpaceFlight)


class FieldHospitalTerrset(pbge.randmaps.terrset.TerrSet):
    TERRAIN_TYPE = FieldHospitalTerrain
    TERRAIN_MAP = (
        (0,1),
        (2,3,4),
        (5,6,7,8),
        (9,10,11,12),
        (13,14,15,16),
        (17,18,19,20),
        (21,22,23,24),
        (None,25,26,27)
    )
    WAYPOINT_POS = {
        "DOOR": (3, 5)
    }


class PersonalCargoContainerTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_top = 'terrain_terrset_pscargo.png'
    blocks = (Walking, Skimming, Rolling, Cruising, SpaceFlight)
    movement_cost = {pbge.scenes.movement.Vision: 5}


class PersonalCargoContainerTerrset(pbge.randmaps.terrset.TerrSet):
    TERRAIN_TYPE = PersonalCargoContainerTerrain
    TERRAIN_MAP = (
        (3,),
        (2,),
        (1,),
        (0,),
    )
    WAYPOINT_POS = {
        "DOOR": (0, 3)
    }
    def __init__(self, colors=None, **kwargs):
        if not colors:
            colors = gears.color.random_mecha_colors()
        my_duck_dict = dict(
            blocks=PersonalCargoContainerTerrain.blocks, colors=colors, image_top=PersonalCargoContainerTerrain.image_top,
            movement_cost=PersonalCargoContainerTerrain.movement_cost
            )
        self.TERRAIN_MAP = list()
        self.TERRAIN_MAP.append([3,])
        for t in range(min(random.randint(1,3), random.randint(1,3))):
            self.TERRAIN_MAP.append([random.randint(1,2)])
        self.TERRAIN_MAP.append([0,])
        self.WAYPOINT_POS["DOOR"] = (0, len(self.TERRAIN_MAP)-1)
        super().__init__(duck_dict=my_duck_dict, **kwargs)
