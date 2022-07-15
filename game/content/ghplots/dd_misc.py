from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context, OneShotInfoBlast
import gears
import pbge
from .dd_main import DZDRoadMapExit,RoadNode
import random
from game.content import gharchitecture,ghwaypoints,plotutility,ghterrain,backstory,GHNarrativeRequest,PLOT_LIST
from gears import personality



class RanMagnusMechaFactory(Plot):
    LABEL = "DZD_MAGNUSMECHA"

    active = True
    scope = "METRO"

    QOL = gears.QualityOfLife(defense=1, prosperity=1)

    def custom_init(self, nart):
        # Create a building within the town.
        garage_name = "Magnus Mecha Works"
        building = self.register_element("_EXTERIOR", ghterrain.IndustrialBuilding(
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name=garage_name)},
            door_sign=(ghterrain.FixitShopSignEast, ghterrain.FixitShopSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="METROSCENE")

        self.rank = 55
        tplot = self.add_sub_plot(nart, "MECHA_WORKSHOP", elements={"BUILDING_NAME": garage_name})
        self.elements["LOCALE"] = tplot.elements["LOCALE"]

        mycon2 = plotutility.TownBuildingConnection(nart, self, self.elements["METROSCENE"], tplot.elements["LOCALE"],
                                                    room2=tplot.elements["FOYER"],
                                                    room1=building, door1=building.waypoints["DOOR"],
                                                    move_door1=False)

        npc = self.register_element("SHOPKEEPER",
                                    gears.selector.random_character(
                                        name="Ran Magnus",
                                        rank=75, local_tags=(gears.personality.GreenZone,),
                                        job=gears.jobs.ALL_JOBS["Mecha Designer"],
                                        birth_year=106, combatant=False, faction=gears.factions.ProDuelistAssociation,
                                        personality=[personality.Passionate, personality.Sociable, personality.Fellowship],
                                        mnpcid="RAN_MAGNUS",
                                        gender=gears.genderobj.Gender.get_default_female(),
                                        portrait='card_f_ranmagnus.png',
                                        colors=(gears.color.GriffinGreen, gears.color.DarkSkin, gears.color.Fuschia,
                                                gears.color.PlasmaBlue, gears.color.CardinalRed),
                                    ))
        npc.place(tplot.elements["LOCALE"], team=tplot.elements["CIVILIAN_TEAM"])

        self.shop = services.Shop(npc=npc, shop_faction=gears.factions.ProDuelistAssociation,
                                  ware_types=services.MEXTRA_STORE, rank=55)

        self.got_reward = False

        self.magnus_info = (
            OneShotInfoBlast("Osmund",
                             "We used to be lancemates back in the old days. You couldn't ask for a better partner. Then his knees gave out and I discovered that I like building mecha better than I like blasting them."),

            OneShotInfoBlast("mecha",
                             "Kind of a lifelong obsession for me. One of several, to be honest. But, it's the one that gets me paid. I've been designing mecha for thirty years now. Around ten years back I started this company and now I build mecha, too."),

            OneShotInfoBlast("design",
                             "It's important that a mecha know what its job is. There is no such thing as a perfect mecha, just fitness for a particular role. Install that which is useful, uninstall that which is not, and create that which is essentially your own."),

            OneShotInfoBlast("factory",
                             "This is my first factory in Eurasia. We're trying to ramp up production; the possibility of a war with Luna has doubled the demand for our meks. It's way too cold in {} but the local food is delicious so that kind of evens out.".format(self.elements["METROSCENE"]),
                             subject_text="the factory"),
        )


        return True

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        if camp.campdata.get("MINE_MISSION_WON") and not self.got_reward:
            mylist.append(Offer("[HELLO] Osmund told me that you liberated my mine from those bandits; that means you get to buy the good stuff.",
                            context=ContextTag([context.HELLO]), effect=self._open_custom_shop
                            ))
        else:
            mylist.append(Offer("[HELLO] [_MAGNUS_SPIEL]",
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": str(self.elements["LOCALE"]), "wares": "mecha"}
                            ))

        for inf in self.magnus_info:
            if inf.active:
                mylist.append(inf.build_offer())

        return mylist

    def _open_custom_shop(self, camp):
        self.got_reward = True
        self.shop.sell_champion_equipment = True
        self.shop.last_updated = -1
        self.elements["SHOPKEEPER"].relationship.history.append(gears.relationships.Memory(
            "you liberated my mine from some bandits", "I recovered your mine from bandits", 10,
            (gears.relationships.MEM_AidedByPC,)
        ))
        camp.campdata["CD_SPOKE_TO_RAN"] = True

    def _get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        mygram["[_MAGNUS_SPIEL]"] = [
            "This factory is where the magic happens.",
            "Next time you're in Wujung tell Osmund to come visit {METROSCENE}.".format(**self.elements),
            "Remember when [MEM_AidedByPC]? Good times.",
            "Obviously pilots are important, but it's the right design that spells the difference between victory and defeat.",
            "This is where the mecha magic happens."
        ]

        return mygram
