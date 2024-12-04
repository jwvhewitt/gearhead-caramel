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


# **************************
# ***   THE  DOCKYARDS   ***
# **************************

class DockyardsPlot(Plot):
    LABEL = "ROPP_DOCKYARDS_PLOT"
    scope = "METRO"
    active = True

    def custom_init(self, nart):
        self.elements["METROSCENE"] = self.elements["LOCALE"]
        self.add_sub_plot(nart, "ROPP_DOCKYARDS_HOUSEOFBLADES")
        return True

class RoppDockHouseOfBlades(Plot):
    LABEL = "ROPP_DOCKYARDS_HOUSEOFBLADES"
    scope = "METRO"
    active = True

    def custom_init(self, nart):
        locale: gears.GearHeadScene = self.register_element("LOCALE", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['000000A7'])
        room = self.register_element("_ROOM", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['000000A8'])

        shopkeeper = self.register_element("SHOPKEEPER", gears.selector.random_character(
            self.rank, local_tags=(gears.personality.L5DustyRing,), job=gears.jobs.ALL_JOBS["Smuggler"]
        ))

        mycounter = ghrooms.ShopCounterArea(random.randint(4, 6), random.randint(3, 5), anchor=pbge.randmaps.anchors.north)
        room.contents.append(mycounter)
        salesteam = self.register_element("SALES_TEAM", teams.Team(name="Sales Team", allies=[locale.civilian_team]))
        mycounter.contents.append(salesteam)

        shopkeeper.place(locale, team=salesteam)

        self.shop = services.Shop(npc=shopkeeper, ware_types=services.GENERAL_STORE_PLUS_MECHA, rank=self.rank + 25,
                                  shop_faction=gears.factions.BladesOfCrihna, buy_stolen_items=True)

        return True

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer(
            "[HELLO] Welcome to {LOCALE}, where we stock only the finest items manufactured offworld in the L5 Region.".format(**self.elements),
            context=ContextTag([context.HELLO]),
        ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": str(self.elements["LOCALE"]), "wares": "imported luxury goods"},
                            ))

        return mylist


# **********************
# ***   THE  NOGOS   ***
# **********************

class NogosPlot(Plot):
    LABEL = "ROPP_NOGOS_PLOT"
    scope = "METRO"
    active = True
    QOL = gears.QualityOfLife(prosperity=-2, stability=-3, health=-1)

    def custom_init(self, nart):
        self.elements["METROSCENE"] = self.elements["LOCALE"]
        self.add_sub_plot(nart, "LOCAL_PROBLEM", ident="LOCALPROBLEM")
        self.finished_local_problem = False
        return True

    def LOCALPROBLEM_WIN(self, camp):
        if not self.finished_local_problem:
            self.finished_local_problem = True
            camp.campdata["hero_points"] += 1

