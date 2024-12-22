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
from . import missionbuilder, mission_bigobs
from pbge.challenges import Challenge, AutoOffer
from .shops_plus import get_building
import collections


# ***************************
# ***   LUNAR  DISTRICT   ***
# ***************************

class LunarDistrictPlot(Plot):
    LABEL = "ROPP_LUNARDISTRICT_PLOT"
    scope = "METRO"
    active = True
    QOL = gears.QualityOfLife(prosperity=1, community=1)

    def custom_init(self, nart):
        self.elements["METROSCENE"] = self.elements["LOCALE"]
        return True


# ********************************* 
# ***   RESIDENTIAL  DISTRICT   ***
# *********************************

class ResidentialPlot(Plot):
    LABEL = "ROPP_RESIDENTIAL_PLOT"
    scope = "METRO"
    active = True
    QOL = gears.QualityOfLife(stability=1, community=2)

    def custom_init(self, nart):
        self.elements["METROSCENE"] = self.elements["LOCALE"]
        self.add_sub_plot(nart, "LOCAL_PROBLEM", ident="LOCALPROBLEM")
        self.finished_local_problem = False
        return True

    def LOCALPROBLEM_WIN(self, camp):
        if not self.finished_local_problem:
            self.finished_local_problem = True
            camp.campdata["hero_points"] += 1


# ******************************
# ***   SHOPPING  DISTRICT   ***
# ******************************

class ShoppingDistrictPlot(Plot):
    LABEL = "ROPP_SHOPPINGDISTRICT_PLOT"
    scope = "METRO"
    active = True
    QOL = gears.QualityOfLife(prosperity=2)

    def custom_init(self, nart):
        self.elements["METROSCENE"] = self.elements["LOCALE"]
        self.add_sub_plot(nart, "LOCAL_PROBLEM", ident="LOCALPROBLEM")
        self.add_sub_plot(nart, "RANDOM_SHOP")
        self.add_sub_plot(nart, "SHOP_SPECIALIST")
        self.finished_local_problem = False
        return True

    def LOCALPROBLEM_WIN(self, camp):
        if not self.finished_local_problem:
            self.finished_local_problem = True
            camp.campdata["hero_points"] += 1


# *****************************
# ***   SOLAR  NAVY  BASE   ***
# *****************************

class SolarNavyBasePlot(Plot):
    LABEL = "ROPP_SOLARNAVY_PLOT"
    scope = "METRO"
    active = True

    def custom_init(self, nart):
        self.elements["METROSCENE"] = self.elements["LOCALE"]
        return True


# **************************
# ***   THE  DOCKYARDS   ***
# **************************

class DockyardsPlot(Plot):
    LABEL = "ROPP_DOCKYARDS_PLOT"
    scope = "METRO"
    active = True

    QOL = gears.QualityOfLife(prosperity=1, community=-1)

    def custom_init(self, nart):
        self.elements["METROSCENE"] = self.elements["LOCALE"]
        self.add_sub_plot(nart, "ROPP_DOCKYARDS_HOUSEOFBLADES")
        self.add_sub_plot(nart, "RANDOM_SHOP")
        self.add_sub_plot(nart, "ROPP_REFUGEE_SHIP")
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

        npc = self.register_element("NPC", nart.camp.get_major_npc("CaptainSegard"), dident="_ROOM")

        self.did_crihna_talk = False

        return True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        if camp.is_favorable_to_pc(gears.factions.AegisOverlord):
            mylist.append(Offer(
                "[HELLO_UNFAV] I have nothing to say to Aegis sympathizers.",
                context=ContextTag([context.HELLO]), dead_end=True
            ))
            mylist.append(Offer(
                "[HELLO_UNFAV] I have nothing to say to Aegis collaborators.",
                context=ContextTag([context.UNFAVORABLE_HELLO]), dead_end=True
            ))
        elif camp.is_favorable_to_pc(gears.factions.TreasureHunters) and not self.did_crihna_talk:
            if camp.are_faction_allies(gears.factions.TreasureHunters, gears.factions.AegisOverlord):
                mylist.append(Offer(
                    "The Guild thinks Aegis is in Pirate Point under their protection; Bogo doesn't realize that he's only ruling the city because Aegis allows it.",
                    context=ContextTag([context.HELLO,])
                ))
            else:
                mylist.append(Offer(
                    "Bogo was an idiot for trusting Aegis. Now he's gifted Earth to the Lunars.",
                    context=ContextTag([context.HELLO,])
                ))

        elif camp.is_favorable_to_pc(gears.factions.TheSolarNavy) and not self.did_crihna_talk:
            mylist.append(Offer(
                "The Guild thinks Aegis is in Pirate Point under their protection; Bogo doesn't realize that he's only ruling the city because Aegis allows it.",
                context=ContextTag([context.HELLO,])
            ))

        if not self.did_crihna_talk:
            mylist.append(Offer(
                "Back in '33, before Aegis even started war on their own planet, they convinced some of the L5 states that the dusty ring asteroid stations needed to be brought under control. Along with Rishiri Spinner they blew up Crihna Rock to scare the rest of us into submission. You might say it had the opposite effect.",
                context=ContextTag([context.CUSTOM,]), data={"reply": "Why do you hate Aegis so much?"},
                subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "The spinners moved in with \"peacekeepers\" and \"humanitarian aid\". In practice this meant they were free to loot our mineral resources and exploit our people for cheap labor. Who could fight back? There were pirates back then, of course, but just individual bands. The assault on Crihna galvanized us into a unified force. The Blades.",
                context=ContextTag([context.CUSTOMREPLY,]), data={"reply": "So what happened next?"},
                effect=self._do_crihna_talk, subject=self
            ))

        return mylist

    def _do_crihna_talk(self, camp):
        self.did_crihna_talk = True

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


class RefugeeShip(Plot):
    LABEL = "ROPP_REFUGEE_SHIP"
    scope = "METRO"
    active = True

    RUMOR = Rumor(
        "{NPC} has been trying to help refugees escape the war zone by ship",
        offer_msg="Trouble is, all the fighting has stirred up the sea-kaiju that live in the bay. Getting a boat through them isn't going to be easy. You can ask {NPC} at {NPC_SCENE} about it.",
        offer_subject="{NPC} has been trying to help refugees escape",
        offer_subject_data="the refugee ship",
        memo="{NPC} is trying to help civilians escape the Pirate Point war zone by ship, but the sea monsters in the bay have made this highly dangerous.",
        prohibited_npcs=("NPC",)
    )

    JOBS = ("Doctor", "Nurse", "Firefighter", "Field Medic", "Priest", "Monk", "Trader")

    def custom_init(self, nart):
        npc = gears.selector.random_character(
            rank=self.rank, local_tags=tuple(self.elements["METROSCENE"].attributes),
            combatant=True, job=gears.jobs.ALL_JOBS[random.choice(self.JOBS)],
        )
        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"])

        specialties = [sk for sk in gears.stats.NONCOMBAT_SKILLS if sk in npc.statline]
        if random.randint(-5, 5) > len(specialties):
            npc.statline[random.choice(gears.stats.NONCOMBAT_SKILLS)] += random.randint(1, 4)

        self.register_element("NPC", npc, dident="NPC_SCENE")

        self.mission_seed = missionbuilder.BuildAMissionSeed(
            nart.camp, "Escort the Refugee Ship",
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            allied_faction=gears.factions.DeadzoneFederation,
            enemy_faction=None, rank=self.rank,
            objectives=(mission_bigobs.BAMO_ESCORT_SHIP,),
            one_chance=True,
            scenegen=pbge.randmaps.SceneGenerator, architecture=gharchitecture.MechaScaleOcean(),
            adv_type="BAM_ESCORT_MISSION", custom_elements={
                "ENTRANCE_ANCHOR": pbge.randmaps.anchors.west, 
                mission_bigobs.BAME_THREAT_TYPE: mission_bigobs.CTHREAT_MONSTERS,
                mission_bigobs.CTE_MONSTER_TAGS: ("FISH", "ANIMAL", "MUTANT", "REPTILE")
            }, cash_reward=100, on_win=self._win_mission, on_loss=self._lose_mission
        )
        self.mission_active = False
        self.won_mission = False

        return True

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def activate_mission(self, camp):
        self.mission_active = True
        self.memo = Memo("{NPC} has asked you to escort the refugee ship trying to escape Pirate Point's harbor.".format(**self.elements), self.elements["NPC_SCENE"])
        self.RUMOR = None
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def deny_mission(self, camp):
        self.end_plot(camp, True)
        camp.campdata["hero_points"] -= 1

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed and self.mission_active:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

    def _win_mission(self, camp: gears.GearHeadCampaign):
        if not self.won_mission:
            self.memo = Memo("You helped {NPC} provide safe passage to refugees fleeing the war in Pirate's Point.".format(**self.elements), location=self.elements["NPC_SCENE"])
            self.won_mission = True
            camp.campdata["hero_points"] += 1
            relation = camp.get_relationship(self.elements["NPC"])
            relation.tags.add(gears.relationships.RT_LANCEMATE)
            relation.history.append(gears.relationships.Memory(
                "you helped me to evacuate refugees from Pirate's Point",
                "we helped people escape from the Pirate's Point war",
                10, memtags=(gears.relationships.MEM_AidedByPC,)
            ))
            self.elements["METRO"].local_reputation += 10

    def _lose_mission(self, camp: gears.GearHeadCampaign):
        # On losing the mission, let's never talk about this again.
        camp.freeze(self.elements["NPC"])
        self.elements["METRO"].local_reputation -= 10
        self.end_plot(camp,True)

    def _end_mission(self, camp):
        self.end_plot(camp,True)

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        if self.won_mission:
            mylist.append(Offer(
                "Thanks for helping all those people to escape the war zone. If you ever need my help with anything, feel free to ask.",
                ContextTag([context.HELLO]), effect=self._end_mission
            ))

        elif not self.mission_active:
            mylist.append(Offer(
                "[LOOKING_FOR_CAVALIER] People fleeing the war have been gathering here, at the dockyard, hoping for a ship to bring them to freedom. I have obtained a ship and crew but the harbour has been blocked by monsters drawn to the conflict.",
                ContextTag([context.HELLO, context.MISSION]),
            ))

            mission_off = Offer(
                "I need your lance to escort the ship and protect it from the creatures. Once you leave Pirate Point Bay, the ship should be able to reach Ipshil safely. [DOYOUACCEPTMISSION]".format(**self.elements),
                ContextTag([context.CUSTOM]), data={"reply": "Tell me how I can help the refugees."},
                subject = "People fleeing the war have been gathering here, at the dockyard"
            )
            if self.memo:
                mission_off.subject_start = True
            mylist.append(mission_off)

            mylist.append(Offer(
                "[IWillSendMissionDetails]; [GOODLUCK]",
                ContextTag([context.CUSTOMREPLY]), effect=self.activate_mission,
                data={"reply": "[MISSION:ACCEPT]"},
                subject="People fleeing the war have been gathering here, at the dockyard"
            ))

            mylist.append(Offer(
                "[UNDERSTOOD] [GOODBYE]",
                ContextTag([context.CUSTOMREPLY]), effect=self.deny_mission,
                data={"reply": "[MISSION:DENY]"},
                subject="People fleeing the war have been gathering here, at the dockyard"
            ))

        else:
            mylist.append(Offer(
                "The people who have lost their homes during the fighting are waiting for a way to escape Pirate's Point.",
                ContextTag([context.HELLO]),
            ))

            mylist.append(Offer(
                msg="I don't want to pressure you, but please remember that there's a war going on. The sooner the ship leaves the better.",
                context=ContextTag([context.CUSTOM]), data={"reply": "[STILL_WORKING_ON_IT]"},
                subject=""
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


# **************************
# ***   THE  SCRAPYARD   ***
# **************************

class ScrapyardPlot(Plot):
    LABEL = "ROPP_SCRAPYARD_PLOT"
    scope = "METRO"
    active = True
    QOL = gears.QualityOfLife(health=-1)

    def custom_init(self, nart):
        self.elements["METROSCENE"] = self.elements["LOCALE"]
        return True


# **************************
# ***   THE  SPACEPORT   ***
# **************************

class SpaceportPlot(Plot):
    LABEL = "ROPP_SPACEPORT_PLOT"
    scope = "METRO"
    active = True
    QOL = gears.QualityOfLife(health=-1)

    def custom_init(self, nart):
        self.elements["METROSCENE"] = self.elements["LOCALE"]
        return True


# ****************************
# ***   UPTOWN  DISTRICT   ***
# ****************************

class UptownPlot(Plot):
    LABEL = "ROPP_UPTOWN_PLOT"
    scope = "METRO"
    active = True
    QOL = gears.QualityOfLife(prosperity=1, defense=1, stability=-1)

    def custom_init(self, nart):
        self.elements["METROSCENE"] = self.elements["LOCALE"]
        return True


# *******************************
# ***   WAREHOUSE  DISTRICT   ***
# *******************************

class WarehouseDistrictPlot(Plot):
    LABEL = "ROPP_WAREHOUSEDISTRICT_PLOT"
    scope = "METRO"
    active = True
    QOL = gears.QualityOfLife(community=-1, health=-1)

    def custom_init(self, nart):
        self.elements["METROSCENE"] = self.elements["LOCALE"]
        self.add_sub_plot(nart, "ROPP_PASSWORDS_PLOT")
        return True


class WarehousePasswordsPlot(Plot):
    LABEL = "ROPP_PASSWORDS_PLOT"
    scope = True
    active = True

    def custom_init(self, nart):
        self.door_codes = [".".join([str(random.randint(0,9)) for t in range(6)]) for t in range(5)]
        print(self.door_codes)
        self.elements["WH13"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000009B']
        myroom = self.register_element(
            "_room13", pbge.randmaps.rooms.ClosedRoom(10,8, decorate=gharchitecture.StorageRoomDecor()), 
            dident="WH13"
        )
        for t in range(random.randint(3,6)):
            myroom.contents.append(ghwaypoints.Lockers())
        self.register_element("FIRST_NOTE", ghwaypoints.KnifeNote(
            desc="Dagmar-\nYou've been assigned to warehouse 49 tonight. Don't forget that the door code is {}. The big cheese is expecting an important package from down south; if security blows this, we'll be looking for new jobs on Titan.".format(self.door_codes[0])
        ), dident="_room13")

        return True

    def FIRST_NOTE_BUMP(self, camp):
        print("Bump recieved.")
