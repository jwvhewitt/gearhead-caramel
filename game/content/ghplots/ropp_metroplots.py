# City plots for Raid on Pirate's Point, since I am still working on the scenario editor.

import random
from game import content, services, teams, ghdialogue
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges, ghrooms
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor, PlotState
from pbge.memos import Memo
from . import missionbuilder, rwme_objectives, campfeatures, worldmapwar, wmw_occupation
from pbge.challenges import Challenge, AutoOffer
from .shops_plus import get_building
import collections


class DockyardsPlot(Plot):
    LABEL = "ROPP_DOCKYARDS_PLOT"
    scope = "METRO"
    active = True

    def custom_init(self, nart):
        self.add_sub_plot(nart, "ROPP_DOCKYARDS_HOUSEOFBLADES")
        return True

class RoppDockHouseOfBlades(Plot):
    LABEL = "ROPP_DOCKYARDS_HOUSEOFBLADES"
    scope = "METRO"
    active = True

    def custom_init(self, nart):
        locale = self.register_element("LOCALE", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['000000A7'])
        room = self.register_element("_ROOM", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['000000A8'])


        return True
