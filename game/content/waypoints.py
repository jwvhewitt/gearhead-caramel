
# A Waypoint is a special effect waiting on a tile. It is normally invisible,
# but can affect the terrain of the tile it is placed in. Walking onto the tile
# or bumping it will activate its effect.

import pbge
import ghterrain
from pbge.scenes.waypoints import Waypoint


class VendingMachine( Waypoint ):
    TILE = pbge.scenes.Tile( None, None, ghterrain.VendingMachineTerrain )
    desc = "You stand before a vending machine."

class Exit( Waypoint ):
    TILE = pbge.scenes.Tile( None, None, ghterrain.ExitTerrain )
    def __init__( self, dest_scene=None, dest_entrance=None, **kwargs ):
        self.dest_scene = dest_scene
        self.dest_entrance = dest_entrance
        super(Exit,self).__init__(**kwargs)

    def unlocked_use( self, camp ):
        # Perform this waypoint's special action.
        camp.destination = self.dest_scene
        camp.entrance = self.dest_entrance




