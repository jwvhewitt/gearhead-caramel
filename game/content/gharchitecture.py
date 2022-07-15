import pygame

from . import ghterrain
from pbge.randmaps.decor import OmniDec,ColumnsDecor,OfficeDecor
import pbge
from . import ghwaypoints,ghrooms
from .ghrooms import MSWreckageDecor
import gears
from gears import GearHeadArchitecture
import random


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


class TechDungeonDecor(OmniDec):
    WALL_DECOR = (ghterrain.TekruinsWallDecor,ghterrain.SteelPipe, ghterrain.VentFanTerrain, ghterrain.TekruinsWallDecor)
    WALL_FILL_FACTOR = 0.40
    FLOOR_DECOR = (ghterrain.Bones, ghterrain.Tekdebris)
    FLOOR_FILL_FACTOR = 0.07


class RundownChemPlantDecor(OmniDec):
    WALL_DECOR = (ghterrain.TekruinsWallDecor,ghterrain.SteelPipe, ghterrain.SteelPipe, ghterrain.TekruinsWallDecor)
    WALL_FILL_FACTOR = 0.40
    FLOOR_DECOR = (ghterrain.Bones, ghterrain.Tekdebris)
    FLOOR_FILL_FACTOR = 0.05
    ALTERNATE_FLOOR = (ghterrain.ToxicSludge, )
    ALT_FLOOR_FACTOR = 0.03


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


class CaveDecor(OmniDec):
    WALL_DECOR = (ghterrain.WallStones,)
    WALL_FILL_FACTOR = 0.10
    FLOOR_DECOR = (ghterrain.FloorStones,)
    FLOOR_FILL_FACTOR = 0.02


class ToxicCaveDecor(OmniDec):
    WALL_DECOR = (ghterrain.WallStones,)
    WALL_FILL_FACTOR = 0.10
    FLOOR_DECOR = (ghterrain.FloorStones, ghterrain.Bones)
    FLOOR_FILL_FACTOR = 0.03
    ALTERNATE_FLOOR = (ghterrain.ToxicSludge, )
    ALT_FLOOR_FACTOR = 0.02


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

class WorldScaleDeadzone(GearHeadArchitecture):
    ENV = gears.tags.GroundEnv
    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.Water,ghterrain.DeadZoneGround,ghterrain.TechnoRubble,higround=0.8,maxhiground=0.9)
    DEFAULT_FLOOR_TERRAIN = ghterrain.DeadZoneGround

class MechaScaleGreenzone(GearHeadArchitecture):
    ENV = gears.tags.GroundEnv
    DEFAULT_CONVERTER = pbge.randmaps.converter.PlasmaConverter(ghterrain.DragonTeethWall,ghterrain.DragonTeethWall,ghterrain.Forest)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.GreenZoneGrass
    DEFAULT_ROOM_CLASSES = (ghrooms.ForestRoom,ghrooms.LakeRoom,ghrooms.MSRuinsRoom)

class MechaScaleDeadzone(GearHeadArchitecture):
    ENV = gears.tags.GroundEnv
    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.DeadZoneGround
    DEFAULT_ROOM_CLASSES = (ghrooms.ForestRoom,ghrooms.LakeRoom,ghrooms.WreckageRoom,ghrooms.DragonToothRoom,ghrooms.MSRuinsRoom)

class MechaScaleRuins(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.MSRuinedWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.Water,ghterrain.DeadZoneGround,ghterrain.TechnoRubble,loground=0.0,higround=0.3)
    DEFAULT_FLOOR_TERRAIN = ghterrain.TechnoRubble
    DEFAULT_DECORATE = MSWreckageDecor()

class MechaScaleSemiDeadzone(GearHeadArchitecture):
    ENV = gears.tags.GroundEnv
    DEFAULT_CONVERTER = pbge.randmaps.converter.PlasmaConverter(ghterrain.DragonTeethWall,ghterrain.DragonTeethWall,ghterrain.Forest)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.SemiDeadZoneGround
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.SemiDeadZoneGround, ghterrain.SemiDeadZoneGround, ghterrain.GreenZoneGrass, higround=0.65)
    DEFAULT_ROOM_CLASSES = (ghrooms.ForestRoom,ghrooms.LakeRoom,ghrooms.WreckageRoom,ghrooms.DragonToothRoom,ghrooms.MSRuinsRoom)

class MechaScaleSemiDeadzoneRuins(GearHeadArchitecture):
    ENV = gears.tags.GroundEnv
    DEFAULT_CONVERTER = pbge.randmaps.converter.PlasmaConverter(ghterrain.DragonTeethWall,ghterrain.DragonTeethWall,ghterrain.Forest)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.SemiDeadZoneGround
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.SemiDeadZoneGround, ghterrain.SemiDeadZoneGround, ghterrain.GreenZoneGrass, higround=0.65)
    DEFAULT_ROOM_CLASSES = (ghrooms.WreckageRoom,ghrooms.MSRuinsRoom)


class HumanScaleDeadzone(GearHeadArchitecture):
    ENV = gears.tags.GroundEnv
    #    DEFAULT_WALL_TERRAIN = ghterrain.DefaultWall
#    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.CrackedEarth


class HumanScaleDeadzoneWilderness(GearHeadArchitecture):
    ENV = gears.tags.GroundEnv
    DEFAULT_WALL_TERRAIN = ghterrain.SandDuneWall
    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.SandDuneWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.CrackedEarth
    DEFAULT_ROOM_CLASSES = (ghrooms.OpenRoom,)


class HumanScaleSemiDeadzone(GearHeadArchitecture):
    ENV = gears.tags.GroundEnv
    DEFAULT_CONVERTER = pbge.randmaps.converter.PlasmaConverter(ghterrain.DragonTeethWall,ghterrain.DragonTeethWall,ghterrain.Forest)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.SemiDeadZoneGround
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.SemiDeadZoneGround, ghterrain.SemiDeadZoneGround, ghterrain.GreenZoneGrass, higround=0.65)
    DEFAULT_ROOM_CLASSES = (ghrooms.ForestRoom,ghrooms.LakeRoom,ghrooms.WreckageRoom,ghrooms.DragonToothRoom,ghrooms.MSRuinsRoom)

class HumanScaleUrbanDeadzone(GearHeadArchitecture):
    ENV = gears.tags.GroundEnv
    DEFAULT_FLOOR_TERRAIN = ghterrain.SemiDeadZoneGround
    DEFAULT_PREPARE = pbge.randmaps.prep.HeightfieldPrep(ghterrain.CrackedEarth, ghterrain.SemiDeadZoneGround, ghterrain.GreenZoneGrass)
    DEFAULT_ROOM_CLASSES = (ghrooms.BushesRoom,ghrooms.LakeRoom,ghrooms.WreckageRoom)

class HumanScaleGreenzone(GearHeadArchitecture):
    ENV = gears.tags.GroundEnv
    #    DEFAULT_WALL_TERRAIN = ghterrain.DefaultWall
#    DEFAULT_CONVERTER = pbge.randmaps.converter.BasicConverter(ghterrain.DragonTeethWall)
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_FLOOR_TERRAIN = ghterrain.GreenZoneGrass


class DefaultBuilding(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_WALL_TERRAIN = ghterrain.DefaultWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.OldTilesFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class ResidentialBuilding(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_WALL_TERRAIN = ghterrain.ResidentialWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.HardwoodFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class MakeScrapIronBuilding(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_WALL_TERRAIN = ghterrain.ScrapIronWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.OldTilesFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class ScrapIronWorkshop(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_WALL_TERRAIN = ghterrain.ScrapIronWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.GrateFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor


class CommercialBuilding(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_WALL_TERRAIN = ghterrain.CommercialWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.OldTilesFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class OrganicBuilding(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_WALL_TERRAIN = ghterrain.OrganicWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.OrganicFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor
    DEFAULT_ROOM_CLASSES = (pbge.randmaps.rooms.FuzzyRoom,)

class HospitalBuilding(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_WALL_TERRAIN = ghterrain.HospitalWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.WhiteTileFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class IndustrialBuilding(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_WALL_TERRAIN = ghterrain.IndustrialWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.OldTilesFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class FactoryBuilding(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_WALL_TERRAIN = ghterrain.IndustrialWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.GrateFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class FortressBuilding(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_WALL_TERRAIN = ghterrain.FortressWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.OldTilesFloor
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class StoneBuilding(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_WALL_TERRAIN = ghterrain.StoneWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.Flagstone
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor

class EarthCave(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_WALL_TERRAIN = ghterrain.EarthWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.SmallDeadZoneGround
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor
    DEFAULT_ROOM_CLASSES = (pbge.randmaps.rooms.FuzzyRoom,)

class StoneCave(GearHeadArchitecture):
    ENV = gears.tags.UrbanEnv
    DEFAULT_MUTATE = pbge.randmaps.mutator.CellMutator()
    DEFAULT_WALL_TERRAIN = ghterrain.StoneWall
    DEFAULT_FLOOR_TERRAIN = ghterrain.SmallDeadZoneGround
    DEFAULT_OPEN_DOOR_TERRAIN = ghterrain.MetalDoorOpen
    DEFAULT_DOOR_CLASS = ghwaypoints.MetalDoor
    DEFAULT_ROOM_CLASSES = (pbge.randmaps.rooms.FuzzyRoom,)


class DeadZoneHighwaySceneGen( pbge.randmaps.SceneGenerator ):
    ENV = gears.tags.GroundEnv
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


def get_mecha_encounter_scenegen_and_architecture(mymetro: gears.GearHeadScene):
    # Return a tuple containing an appropriate scenegen and architecture for a combat mission
    # set in this metroscene.
    scenegen = pbge.randmaps.SceneGenerator

    archi_candidates = list()
    if gears.personality.GreenZone in mymetro.attributes:
        archi_candidates.append(MechaScaleGreenzone())
    if gears.personality.DeadZone in mymetro.attributes:
        if gears.personality.GreenZone not in mymetro.attributes:
            archi_candidates.append(MechaScaleDeadzone())
        archi_candidates.append(MechaScaleSemiDeadzone())
        archi_candidates.append(MechaScaleSemiDeadzoneRuins())

    if not archi_candidates:
        archi_candidates.append(MechaScaleGreenzone())

    return scenegen, random.choice(archi_candidates)

