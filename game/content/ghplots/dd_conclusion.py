from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
import pbge
from game.content import backstory, plotutility, ghterrain, ghwaypoints
import random
from gears import relationships
from game import content


class DZD_Conclusion(Plot):
    # This plot is the conclusion controller; it loads and activates the individual bits of the conclusion
    # as necessary.
    LABEL = "DZD_CONCLUSION"
    active = True
    scope = True

    def custom_init( self, nart ):
        return True


class VictoryParty(Plot):
    # Following the player's success in opening the road, there will be a victory party.
    # This party will be interrupted by the attack on DoomedTown.
    def custom_init( self, nart ):
        return True

    def start_mission(self, camp):
        pass


class DoomedTown(Plot):
    # Visit the town that has been destroyed by Cetus. Maybe fight some scavengers.
    # Learn about what happened. Find the angel egg. Fight Cetus when you return to Distant Town.
    pass


class CetusFight(Plot):
    # Each time Cetus moves to a new village, you have one chance to fight it.
    # In order to win the fight you must have at least one "advantage". Otherwise,
    # once it has taken enough damage, Cetus will simply release a death wave and fly away.
    # Also, if you lose the third fight, the TDF has had enough and will use their nukes.
    pass
