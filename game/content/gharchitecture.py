import ghterrain
from pbge.randmaps.architect import Architecture
from pbge.randmaps.decor import OmniDec
import pbge
import ghwaypoints

class CheeseShopDecor(OmniDec):
    WALL_DECOR = (ghterrain.WoodenShelves,)

class ResidentialDecor(OmniDec):
    WALL_DECOR = (ghterrain.WoodenShelves,)
    WIN_DECOR = ghterrain.ScreenWindow

class WorldScaleDeadzone(Architecture):
    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.Water,ghterrain.DeadZoneGround,ghterrain.TechnoRubble,higround=0.8,maxhiground=0.9)
    DEFAULT_FLOOR_TERRAIN = ghterrain.DeadZoneGround

class MechaScaleDeadzone(Architecture):
    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.SmallDeadZoneGround

class HumanScaleDeadzone(Architecture):
#    DEFAULT_WALL_TERRAIN = ghterrain.DefaultWall
#    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.CrackedEarth

class HumanScaleGreenzone(Architecture):
#    DEFAULT_WALL_TERRAIN = ghterrain.DefaultWall
#    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.GreenZoneGrass

class DefaultBuilding(Architecture):
    DEFAULT_WALL_TERRAIN = ghterrain.DefaultWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.OldTilesFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class ResidentialBuilding(Architecture):
    DEFAULT_WALL_TERRAIN = ghterrain.ResidentialWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.HardwoodFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class MakeScrapIronBuilding(Architecture):
    DEFAULT_WALL_TERRAIN = ghterrain.ScrapIronWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.OldTilesFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class CommercialBuilding(Architecture):
    DEFAULT_WALL_TERRAIN = ghterrain.CommercialWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.OldTilesFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class HospitalBuilding(Architecture):
    DEFAULT_WALL_TERRAIN = ghterrain.HospitalWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.WhiteTileFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class IndustrialBuilding(Architecture):
    DEFAULT_WALL_TERRAIN = ghterrain.IndustrialWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.OldTilesFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor
