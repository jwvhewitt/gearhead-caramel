
# A Waypoint is a special effect waiting on a tile. It is normally invisible,
# but can affect the terrain of the tile it is placed in. Walking onto the tile
# or bumping it will activate its effect.

import pbge
import ghterrain
from pbge.scenes.waypoints import Waypoint


class VendingMachine( Waypoint ):
    TILE = pbge.scenes.Tile( None, None, ghterrain.VendingMachineTerrain )
    desc = "You stand before a vending machine."

class WinterMochaBarrel( Waypoint ):
    TILE = pbge.scenes.Tile( None, None, ghterrain.WinterMochaBarrelTerrain )
    desc = "You stand before a big container of fuel."

class WinterMochaShovel( Waypoint ):
    TILE = pbge.scenes.Tile( None, None, ghterrain.WinterMochaBrokenShovel )
    desc = "You stand before a broken shovel."

class WinterMochaToolbox( Waypoint ):
    TILE = pbge.scenes.Tile( None, None, ghterrain.WinterMochaToolboxTerrain )
    desc = "You stand before an abandoned toolbox."

