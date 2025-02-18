from ast import Pass
from pbge.plots import Plot, PlotState
import game.content.ghwaypoints
import game.content.ghterrain
import gears
import pbge
from game import teams,ghdialogue
from game.content import dungeonmaker, gharchitecture,ghwaypoints
from game.ghdialogue import context
import random
from pbge.dialogue import ContextTag,Offer
from game.content.ghplots import dd_main
import game.content.plotutility
import game.content.gharchitecture
from . import missionbuilder


#   ************************
#   ***  BASE_ROOM_LOOT  ***
#   ************************
#  It's somebody's base. Loot anything that isn't nailed down.
#   ROOM: The room to decorate/place the loot in.
#   FACTION: The faction the base belongs to; may be None

class MultipurposeRoom(Plot):
    LABEL = "BASE_ROOM_LOOT"
    def custom_init( self, nart ):
        # Add the interior scene.
        room = self.elements["ROOM"]
        if random.randint(1,2) == 1:
            room.contents.append(ghwaypoints.EarthMap())
        room.DECORATE = gharchitecture.BunkerDecor()
        return True


#   ************************************************************
#   ***  Former DUNGEON_GOAL... now moved to dungeon_extras  ***
#   ************************************************************

# TypeAlias to prevent pickle errors.
StandardTreasureChest = MultipurposeRoom
