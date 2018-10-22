
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
        elif camp.scene.get_wall(*self.pos) is ghterrain.MetalDoorOpen:
            camp.scene.set_wall(self.pos[0],self.pos[1],ghterrain.MetalDoorClosed)
