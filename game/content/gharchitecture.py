from . import ghterrain
from pbge.randmaps.architect import Architecture
from pbge.randmaps.decor import OmniDec,ColumnsDecor,OfficeDecor
import pbge
from . import ghwaypoints,ghrooms
from .ghrooms import MSWreckageDecor


class CheeseShopDecor(OmniDec):
    WALL_DECOR = (ghterrain.WoodenShelves,)

class ResidentialDecor(OmniDec):
    WALL_DECOR = (ghterrain.WoodenShelves,)
    WIN_DECOR = ghterrain.ScreenWindow


class StorageRoomDecor(ColumnsDecor):
    WALL_DECOR = (ghterrain.ShippingShelvesTerrain,ghterrain.ShippingShelvesTerrain,ghterrain.ShippingShelvesTerrain,ghterrain.VentFanTerrain)
    WALL_FILL_FACTOR = 0.6
    FLOOR_DECOR = (ghterrain.NorthSouthShelvesTerrain,)

class UlsaniteOfficeDecor(OfficeDecor):
    DESK_TERRAIN = (ghterrain.UlsaniteDesk,)
    CHAIR_TERRAIN = (ghterrain.UlsaniteChair,)
    WALL_DECOR = (ghterrain.UlsaniteBookshelfTerrain,ghterrain.UlsaniteFilingCabinetTerrain)

class WorldScaleDeadzone(Architecture):
    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.Water,ghterrain.DeadZoneGround,ghterrain.TechnoRubble,higround=0.8,maxhiground=0.9)
    DEFAULT_FLOOR_TERRAIN = ghterrain.DeadZoneGround

class MechaScaleDeadzone(Architecture):
    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.DeadZoneGround
    DEFAULT_ROOM_CLASSES = (ghrooms.ForestRoom,ghrooms.LakeRoom,ghrooms.WreckageRoom,ghrooms.DragonToothRoom)

class MechaScaleRuins(Architecture):
    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.FortressWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.Water,ghterrain.DeadZoneGround,ghterrain.TechnoRubble,loground=0.0,higround=0.3)
    DEFAULT_FLOOR_TERRAIN = ghterrain.TechnoRubble
    DEFAULT_DECORATE = MSWreckageDecor()

class MechaScaleSemiDeadzone(Architecture):
    DEFAULT_CONVERTER = pbge.randmaps.converter.PlasmaConverter(ghterrain.DragonTeethWall,ghterrain.DragonTeethWall,ghterrain.Forest)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.SemiDeadZoneGround
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.SemiDeadZoneGround, ghterrain.SemiDeadZoneGround, ghterrain.GreenZoneGrass, higround=0.65)
    DEFAULT_ROOM_CLASSES = (ghrooms.ForestRoom,ghrooms.LakeRoom,ghrooms.WreckageRoom,ghrooms.DragonToothRoom)

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

class ScrapIronWorkshop(Architecture):
    DEFAULT_WALL_TERRAIN = ghterrain.ScrapIronWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.GrateFloor
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

class FortressBuilding(Architecture):
    DEFAULT_WALL_TERRAIN = ghterrain.FortressWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.OldTilesFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor
