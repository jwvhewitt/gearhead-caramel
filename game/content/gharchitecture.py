import pygame

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

class DungeonDecor(OmniDec):
    WALL_DECOR = (ghterrain.TorchTerrain,)
    WALL_FILL_FACTOR = 0.33

class MysteryDungeonDecor(OmniDec):
    WALL_DECOR = (ghterrain.BlueTorchTerrain,)
    WALL_FILL_FACTOR = 0.33


class RundownFactoryDecor(OmniDec):
    WALL_DECOR = (ghterrain.SteelPipe, ghterrain.TekruinsWallDecor, ghterrain.SteelPipe, ghterrain.ShippingShelvesTerrain)
    WALL_FILL_FACTOR = 0.33
    FLOOR_DECOR = (ghterrain.Tekdebris, ghterrain.NorthSouthShelvesTerrain)
    FLOOR_FILL_FACTOR = 0.03


class DefiledFactoryDecor(OmniDec):
    WALL_DECOR = (ghterrain.TekruinsWallDecor,ghterrain.Cybertendrils)
    WALL_FILL_FACTOR = 0.33
    FLOOR_DECOR = (ghterrain.Bones,ghterrain.Tekdebris)
    FLOOR_FILL_FACTOR = 0.07


class OrganicStructureDecor(OmniDec):
    WALL_DECOR = (ghterrain.Cybertendrils,)
    WALL_FILL_FACTOR = 0.20
    FLOOR_DECOR = (ghterrain.Bones,)
    FLOOR_FILL_FACTOR = 0.05


class FactoryDecor(OmniDec):
    WALL_DECOR = (ghterrain.SteelPipe, ghterrain.ShippingShelvesTerrain, ghterrain.VentFanTerrain)
    WALL_FILL_FACTOR = 0.25


class StoneUndercityDecor(OmniDec):
    WALL_DECOR = (ghterrain.WallStones,ghterrain.WallStones,ghterrain.WallStones,ghterrain.BlueTorchTerrain)
    WALL_FILL_FACTOR = 0.45
    FLOOR_DECOR = (ghterrain.FloorStones,)
    FLOOR_FILL_FACTOR = 0.10

class DesertDecor(OmniDec):
    FLOOR_DECOR = (ghterrain.Bones,)
    FLOOR_FILL_FACTOR = 0.05


class BunkerDecor(OmniDec):
    WALL_DECOR = (ghterrain.LockersTerrain,ghterrain.VentFanTerrain,ghterrain.ShippingShelvesTerrain,)
    FLOOR_DECOR = (ghterrain.UlsaniteDesk,ghterrain.NorthSouthShelvesTerrain,)
    FLOOR_FILL_FACTOR = 0.01

class StorageRoomDecor(ColumnsDecor):
    WALL_DECOR = (ghterrain.ShippingShelvesTerrain,ghterrain.ShippingShelvesTerrain,ghterrain.ShippingShelvesTerrain,ghterrain.VentFanTerrain)
    WALL_FILL_FACTOR = 0.6
    FLOOR_DECOR = (ghterrain.NorthSouthShelvesTerrain,)

class UlsaniteOfficeDecor(OfficeDecor):
    DESK_TERRAIN = (ghterrain.UlsaniteDesk,)
    CHAIR_TERRAIN = (ghterrain.UlsaniteChair,)
    WALL_DECOR = (ghterrain.UlsaniteBookshelfTerrain,ghterrain.UlsaniteFilingCabinetTerrain)
    #WALL_DECOR = (ghterrain.TekruinsWallDecor,)

class WorldScaleDeadzone(Architecture):
    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.Water,ghterrain.DeadZoneGround,ghterrain.TechnoRubble,higround=0.8,maxhiground=0.9)
    DEFAULT_FLOOR_TERRAIN = ghterrain.DeadZoneGround

class MechaScaleDeadzone(Architecture):
    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.DeadZoneGround
    DEFAULT_ROOM_CLASSES = (ghrooms.ForestRoom,ghrooms.LakeRoom,ghrooms.WreckageRoom,ghrooms.DragonToothRoom,ghrooms.MSRuinsRoom)

class MechaScaleRuins(Architecture):
    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.MSRuinedWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.Water,ghterrain.DeadZoneGround,ghterrain.TechnoRubble,loground=0.0,higround=0.3)
    DEFAULT_FLOOR_TERRAIN = ghterrain.TechnoRubble
    DEFAULT_DECORATE = MSWreckageDecor()

class MechaScaleSemiDeadzone(Architecture):
    DEFAULT_CONVERTER = pbge.randmaps.converter.PlasmaConverter(ghterrain.DragonTeethWall,ghterrain.DragonTeethWall,ghterrain.Forest)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.SemiDeadZoneGround
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.SemiDeadZoneGround, ghterrain.SemiDeadZoneGround, ghterrain.GreenZoneGrass, higround=0.65)
    DEFAULT_ROOM_CLASSES = (ghrooms.ForestRoom,ghrooms.LakeRoom,ghrooms.WreckageRoom,ghrooms.DragonToothRoom,ghrooms.MSRuinsRoom)

class MechaScaleSemiDeadzoneRuins(Architecture):
    DEFAULT_CONVERTER = pbge.randmaps.converter.PlasmaConverter(ghterrain.DragonTeethWall,ghterrain.DragonTeethWall,ghterrain.Forest)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.SemiDeadZoneGround
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.SemiDeadZoneGround, ghterrain.SemiDeadZoneGround, ghterrain.GreenZoneGrass, higround=0.65)
    DEFAULT_ROOM_CLASSES = (ghrooms.WreckageRoom,ghrooms.MSRuinsRoom)


class HumanScaleDeadzone(Architecture):
#    DEFAULT_WALL_TERRAIN = ghterrain.DefaultWall
#    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.CrackedEarth


class HumanScaleDeadzoneWilderness(Architecture):
    DEFAULT_WALL_TERRAIN = ghterrain.SandDuneWall
    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.SandDuneWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.CrackedEarth
    DEFAULT_ROOM_CLASSES = (ghrooms.OpenRoom,)


class HumanScaleSemiDeadzone(Architecture):
    DEFAULT_CONVERTER = pbge.randmaps.converter.PlasmaConverter(ghterrain.DragonTeethWall,ghterrain.DragonTeethWall,ghterrain.Forest)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.SemiDeadZoneGround
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.SemiDeadZoneGround, ghterrain.SemiDeadZoneGround, ghterrain.GreenZoneGrass, higround=0.65)
    DEFAULT_ROOM_CLASSES = (ghrooms.ForestRoom,ghrooms.LakeRoom,ghrooms.WreckageRoom,ghrooms.DragonToothRoom,ghrooms.MSRuinsRoom)


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

class OrganicBuilding(Architecture):
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_WALL_TERRAIN = ghterrain.OrganicWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.OrganicFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor
    DEFAULT_ROOM_CLASSES = (pbge.randmaps.rooms.FuzzyRoom,)

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

class FactoryBuilding(Architecture):
    DEFAULT_WALL_TERRAIN = ghterrain.IndustrialWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.GrateFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class FortressBuilding(Architecture):
    DEFAULT_WALL_TERRAIN = ghterrain.FortressWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.OldTilesFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class StoneBuilding(Architecture):
    DEFAULT_WALL_TERRAIN = ghterrain.StoneWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.Flagstone
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor


class DeadZoneHighwaySceneGen( pbge.randmaps.SceneGenerator ):
    DO_DIRECT_CONNECTIONS = True
    def build( self, gb, archi ):
        self.fill(gb,pygame.Rect(0,gb.height//2-2,gb.width,5),wall=None)

    def DECORATE( self, gb, scenegen ):
        """
        :type gb: gears.GearHeadScene
        """
        # Draw a gret big highway going from west to east.
        self.fill(gb,pygame.Rect(0,gb.height//2-2,gb.width,5),floor=self.archi.DEFAULT_FLOOR_TERRAIN)
        self.fill(gb,pygame.Rect(0,gb.height//2-1,gb.width,3),floor=ghterrain.Pavement)