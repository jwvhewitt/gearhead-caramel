
# A Waypoint is a special effect waiting on a tile. It is normally invisible,
# but can affect the terrain of the tile it is placed in. Walking onto the tile
# or bumping it will activate its effect.

import pbge
import ghterrain
from game.content.ghterrain import DZDTownTerrain, DZDWCommTowerTerrain, DZDCommTowerTerrain
from pbge.scenes.waypoints import Waypoint


class VendingMachine( Waypoint ):
    TILE = pbge.scenes.Tile( None, None, ghterrain.VendingMachineTerrain )
    desc = "You stand before a vending machine."

class Exit( Waypoint ):
    name = "Exit"
    TILE = pbge.scenes.Tile( None, ghterrain.ExitTerrain, None )
    def __init__( self, dest_scene=None, dest_entrance=None, **kwargs ):
        self.dest_scene = dest_scene
        self.dest_entrance = dest_entrance
        super(Exit,self).__init__(**kwargs)

    def unlocked_use( self, camp ):
        # Perform this waypoint's special action.
        if self.dest_scene and self.dest_entrance:
            camp.destination = self.dest_scene
            camp.entrance = self.dest_entrance
        else:
            pbge.alert("This door doesn't seem to go anywhere.")


class DZDTown( Exit ):
    name = 'Town'
    TILE = pbge.scenes.Tile( None, DZDTownTerrain, None )
    desc = "You stand before a deadzone community."


class DZDWCommTower( Exit ):
    name = 'Comm Tower'
    TILE = pbge.scenes.Tile( None, DZDWCommTowerTerrain, None )
    desc = "You stand before a communications tower."


class DZDCommTower( Exit ):
    name = 'Comm Tower'
    TILE = pbge.scenes.Tile( None, DZDCommTowerTerrain, None )
    desc = "You stand before a communications tower."

class Victim(Waypoint):
    name = 'Victim'
    TILE = pbge.scenes.Tile(None,None,ghterrain.VictimTerrain)
    desc = "This person has seen better days."

class RetroComputer(Waypoint):
    name = 'Computer Terminal'
    ATTACH_TO_WALL = True
    TILE = pbge.scenes.Tile(None,None,ghterrain.RetroComputerTerrain)
    desc = "An obsolete but still functioning computer terminal."

class ScrapIronDoor(Exit):
    name = 'Door'
    ATTACH_TO_WALL = True
    TILE = pbge.scenes.Tile(None,None,ghterrain.ScrapIronDoorTerrain)
    desc = "A door."

class ScreenDoor(Exit):
    name = 'Door'
    ATTACH_TO_WALL = True
    TILE = pbge.scenes.Tile(None,None,ghterrain.ScreenDoorTerrain)
    desc = "A door."

class WoodenDoor(Exit):
    name = 'Door'
    ATTACH_TO_WALL = True
    TILE = pbge.scenes.Tile(None,None,ghterrain.WoodenDoorTerrain)
    desc = "A door."

class DZDWConcreteBuilding( Exit ):
    name = 'Concrete Building'
    TILE = pbge.scenes.Tile( None, ghterrain.DZDWConcreteBuilding, None )
    desc = "You stand before a concrete building."


class DZDConcreteBuilding( Exit ):
    name = 'Concrete Building'
    TILE = pbge.scenes.Tile( None, ghterrain.DZDConcreteBuilding, None )
    desc = "You stand before a concrete building."

class MetalDoor( Waypoint ):
    name = "Door"
    TILE = pbge.scenes.Tile( None, ghterrain.MetalDoorClosed, None )
    def unlocked_use( self, camp ):
        # Perform this waypoint's special action.
        if camp.scene.get_wall(*self.pos) is ghterrain.MetalDoorClosed:
            camp.scene.set_wall(self.pos[0],self.pos[1],ghterrain.MetalDoorOpen)
        elif camp.scene.get_wall(*self.pos) is ghterrain.MetalDoorOpen and not camp.scene.get_actors(self.pos):
            camp.scene.set_wall(self.pos[0],self.pos[1],ghterrain.MetalDoorClosed)

class AlliedArmorSignWP(Waypoint):
    name = "Allied Armor"
    TILE = pbge.scenes.Tile(None,None,ghterrain.AlliedArmorSign)
    ATTACH_TO_WALL = True

class StatueM(Waypoint):
    name = "Statue"
    TILE = pbge.scenes.Tile(None,None,ghterrain.StatueMTerrain)
    ATTACH_TO_WALL = True

class StatueF(Waypoint):
    name = "Statue"
    TILE = pbge.scenes.Tile(None,None,ghterrain.StatueFTerrain)
    ATTACH_TO_WALL = True

class GoldPlaque(Waypoint):
    name = "Plaque"
    TILE = pbge.scenes.Tile(None,None,ghterrain.GoldPlaqueTerrain)
    ATTACH_TO_WALL = True

class MechEngTerminal(Waypoint):
    name = "Mecha Engineering Terminal"
    TILE = pbge.scenes.Tile(None,None,ghterrain.MechEngTerminalTerrain)
    ATTACH_TO_WALL = True

class MechaPoster(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.MechaPosterTerrain)
    ATTACH_TO_WALL = True

class VentFan(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.VentFanTerrain)
    ATTACH_TO_WALL = True

class BoardingChute(Waypoint):
    name = "Boarding Chute"
    TILE = pbge.scenes.Tile(None,None,ghterrain.GreenBoardingChuteTerrain)
    ATTACH_TO_WALL = True

class ClosedBoardingChute(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.RedBoardingChuteTerrain)
    ATTACH_TO_WALL = True

class SmokingWreckage(Waypoint):
    TILE = pbge.scenes.Tile(None,ghterrain.MSWreckage,ghterrain.Smoke)

class KojedoModel(Waypoint):
    name = "Kojedo Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.KojedoModelTerrain)

class BuruBuruModel(Waypoint):
    name = "Buru Buru Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.BuruBuruModelTerrain)

class GladiusModel(Waypoint):
    name = "Gladius Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.GladiusModelTerrain)

class VadelModel(Waypoint):
    name = "Vadel Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.VadelModelTerrain)

class HarpyModel(Waypoint):
    name = "Harpy Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.HarpyModelTerrain)

class ClaymoreModel(Waypoint):
    name = "Claymore Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.ClaymoreModelTerrain)

class MechaModel(Waypoint):
    name = "Mecha Statue"
    TILE = pbge.scenes.Tile(None, None, ghterrain.MechaModelTerrain)

class WallMap(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.MapTerrain)
    ATTACH_TO_WALL = True

class EarthMap(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.EarthMapTerrain)
    ATTACH_TO_WALL = True

class Lockers(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.LockersTerrain)
    ATTACH_TO_WALL = True

class ShippingShelves(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.ShippingShelvesTerrain)
    ATTACH_TO_WALL = True

class RegExLogo(Waypoint):
    name = "RegEx Corporation Logo"
    TILE = pbge.scenes.Tile(None,None,ghterrain.RegExLogoTerrain)
    ATTACH_TO_WALL = True

class HamsterCage(Waypoint):
    TILE = pbge.scenes.Tile(None,None,ghterrain.HamsterCageTerrain)
    ATTACH_TO_WALL = True

class Bookshelf(Waypoint):
    TILE = pbge.scenes.Tile(None, None, ghterrain.UlsaniteBookshelfTerrain)
    ATTACH_TO_WALL = True

class StoneStairsUp(Exit):
    TILE = pbge.scenes.Tile(None, None, ghterrain.StoneStairsUpTerrain)

class RecoveryBed(Waypoint):
    TILE = pbge.scenes.Tile(None, None, ghterrain.BedTerrain)
    recovery_entrance = True
