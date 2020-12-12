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
        # First off, we're gonna need a name for the town Cetus wrecks, aka THAT_TOWN
        self.elements["THAT_TOWN_NAME"] = gears.selector.DEADZONE_TOWN_NAMES.gen_word()

        # Add the victory party subplot
        self.add_sub_plot(nart, "DZDC_VICTORY_PARTY", ident="PARTY")


        return True

    def PARTY_WIN(self, camp: gears.GearHeadCampaign):
        # We get the PARTY_WIN trigger when the PC is informed about the happenings in THAT_TOWN.
        pass

class VictoryParty(Plot):
    # Following the player's success in opening the road, there will be a victory party.
    # This party will be interrupted by the attack on DoomedTown.
    LABEL = "DZDC_VICTORY_PARTY"
    active = True
    scope = True

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
