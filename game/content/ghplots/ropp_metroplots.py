# City plots for Raid on Pirate's Point, since I am still working on the scenario editor.

import random
from typing import override
from game import content, services, teams, ghdialogue
from game.content.ghplots import worldmapwar
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges, ghrooms
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor, PlotState
from pbge.memos import Memo
from pbge.scenes import waypoints
from . import missionbuilder, mission_bigobs, worldmapwar, relayplots
from pbge.challenges import Challenge, AutoOffer
from .shops_plus import get_building
import collections

ROPPCD_HERO_POINTS = "hero_points"
ROPPCD_FOUND_CARGO = "found_cargo"
ROPPCD_SPENT_CARGO = "spent_cargo"


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
        self.add_sub_plot(nart, "RANDOM_SHOP")
        self.finished_local_problem = False
        return True

    def LOCALPROBLEM_WIN(self, camp):
        if not self.finished_local_problem:
            self.finished_local_problem = True
            camp.campdata[ROPPCD_HERO_POINTS] += 1


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
            camp.campdata[ROPPCD_HERO_POINTS] += 1


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
    scope = True
    active = True

    SENTENCE_FORMS = [
        "the spy passed information about the Blades to Luna",
        "the spy made sure one of the guild pilots got killed in combat",
        "Aegis bought off one of Bogo's trusted henchmen",
        "the spy has been tracking contraband that goes through the spaceport"
    ]

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

        _ = self.seek_element(nart, "NEXT_METROSCENE", self._is_best_next, backup_seek_func=self._is_okay_next)

        # Needed elements for the Aegis Infiltrator subplot
        self.elements["INFO"] = relayplots.InfoRelayTracker("the Aegis infiltrator", random.sample(self.SENTENCE_FORMS, 1))
        self.elements["ALLIED_FACTION"] = gears.factions.BladesOfCrihna
        self.elements["ENEMY_FACTION"] = gears.factions.AegisOverlord

        self.did_crihna_talk = False
        self.gave_advice = False

        return True

    def _is_best_next(self, nart, candidate):
        return (
            isinstance(candidate, gears.GearHeadScene) and candidate is not self.elements["METROSCENE"] and 
            hasattr(candidate, "metrodat") and 
            gears.tags.SCENE_PUBLIC in candidate.attributes and gears.tags.CITY_UNINHABITED not in candidate.attributes
            )

    def _is_okay_next(self, nart, candidate):
        return (
            isinstance(candidate, gears.GearHeadScene) and candidate is not self.elements["METROSCENE"] and 
            hasattr(candidate, "metrodat") and gears.tags.SCENE_PUBLIC in candidate.attributes
            )

    def INFO_WIN(self, camp):
        print("Won the info relay")
        pass

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

        if not camp.is_favorable_to_pc(gears.factions.AegisOverlord) and not self.gave_advice:
            mylist.append(Offer(
                "There's a rumor passing among the Blades in town that the Guild's inner circle has been infiltrated by Aegis spies. You can probably learn more in {NEXT_METROSCENE}...".format(**self.elements),
                ContextTag([context.CUSTOM,]), data={"reply": "What advice do you have for fighting Aegis?"},
                effect=self._start_search
            ))

        return mylist

    def _start_search(self, camp):
        pstate = PlotState(adv=self.adv, elements={"METROSCENE": self.elements["NEXT_METROSCENE"]}, rank=self.rank+2).based_on(self)
        _ = content.load_dynamic_plot(camp, "INFO_RELAY", pstate)
        self.gave_advice = True

    def _do_crihna_talk(self, camp):
        self.did_crihna_talk = True
        camp.faction_relations[gears.factions.BladesOfCrihna].set_pc_ally()

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
        camp.campdata[ROPPCD_HERO_POINTS] -= 1

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed and self.mission_active:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

    def _win_mission(self, camp: gears.GearHeadCampaign):
        if not self.won_mission:
            self.memo = Memo("You helped {NPC} provide safe passage to refugees fleeing the war in Pirate's Point.".format(**self.elements), location=self.elements["NPC_SCENE"])
            self.won_mission = True
            camp.campdata[ROPPCD_HERO_POINTS] += 1
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
            camp.campdata[ROPPCD_HERO_POINTS] += 1


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
        self.add_sub_plot(nart, "ROPP_SCRAPYARD_POWEROUTAGE")
        return True


class PowerOutage(Plot):
    LABEL = "ROPP_SCRAPYARD_POWEROUTAGE"
    scope = "METRO"
    active = True

    RUMOR = Rumor(
        "the powerplant in the scrapyard has been cutting out recently",
        offer_msg="It used to be a spaceship engine... until the spaceship crashed. Amazingly, the engine didn't go boom. It's the only part of the ship still in one piece. A while back someone rigged it up to power the city; {NPC} at {NPC_SCENE} should go down there and figure out what's going wrong.",
        offer_subject="the powerplant in the scrapyard",
        offer_subject_data="the powerplant in the scrapyard",
        memo="The spaceship engine that provides electricity to Pirate's Point has been malfunctioning. {NPC} might be able to get it working again.",
        prohibited_npcs=("NPC",)
    )

    MECHA_FACTIONS = (
        gears.factions.TheSolarNavy, gears.factions.AegisOverlord, gears.factions.TreasureHunters
    )

    MACGUFFIN_ADJ = ("Fuel", "Power", "Containment", "Activation", "Ignition", "Radiation", "Energy")
    MACGUFFIN_NOUN = ("Rod", "Cell", "Regulator", "Moderator", "Sphere", "Capsule", "Filter")

    @override
    def custom_init(self, nart):
        self.elements["ROOM"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['000000A2']
        mydungeon = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000071']

        macguffin = self.elements["MACGUFFIN"] = gears.base.Treasure(
            name="Fusion {} {}".format(random.choice(self.MACGUFFIN_ADJ), random.choice(self.MACGUFFIN_NOUN)), 
            value=gears.selector.calc_mission_reward(self.rank, 200, True), weight=random.randint(20,50) * 5,
            desc="A replacement part for a spaceship engine."
        )

        self.elements["TREASURE_LEVEL"] = random.choice(mydungeon.levels)

        troom = self.register_element("TROOM", pbge.randmaps.rooms.ClosedRoom(8,8, decorate=gharchitecture.DefiledFactoryDecor()), dident="TREASURE_LEVEL")
        mychest = ghwaypoints.SteelBox(self.rank, 100, treasure_type=(gears.tags.ST_MINERAL, gears.tags.ST_TOOL, gears.tags.ST_ESSENTIAL))
        troom.contents.append(mychest)
        mychest.contents.append(macguffin)
        self.add_sub_plot(nart, "MONSTER_ENCOUNTER", elements={"LOCALE": self.elements["TREASURE_LEVEL"], "ROOM": troom, "TYPE_TAGS": {"ROBOT", "GUARD"}}, rank=self.rank+10)

        proom = self.register_element("PROOM", pbge.randmaps.rooms.OpenRoom(10,6, decorate=gharchitecture.DefiledFactoryDecor()), dident="TREASURE_LEVEL")
        self.add_sub_plot(nart, "MONSTER_ENCOUNTER", elements={"LOCALE": self.elements["TREASURE_LEVEL"], "ROOM": proom, "TYPE_TAGS": {"VERMIN", "CITY", "MUTANT"}}, rank=self.rank)
        proom.contents.append(ghwaypoints.GoldPlaque(name="Dedication", desc="The C.S.S. Gordon Lightfoot\n\nBuilt at Cesena Shipyard\n\nN.T.129"))

        self.elements["NPC"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000004D']
        self.elements["NPC_SCENE"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000004B']

        mek = gears.selector.MechaShoppingList.generate_single_mecha(self.rank+20, random.choice(self.MECHA_FACTIONS), gears.tags.GroundEnv)
        gears.champions.upgrade_to_champion(mek)
        self.elements["MECHA"] = mek

        _ = self.register_element("POWERPLANT", ghwaypoints.DeactivatedFusionCore(
            name="Fusion Core", desc="The fusion power plant of the derelict spaceship.",
            plot_locked=True
        ), dident="ROOM")

        self.accepted_mission = False
        self.repaired_generator = False

        return True

    def POWERPLANT_menu(self, camp: gears.GearHeadCampaign, thingmenu):
        if not self.repaired_generator:
            thingmenu.desc += " It is still working, but just barely."
            thingmenu.add_item("Leave it alone.", None)
            if camp.party_has_item(self.elements["MACGUFFIN"]):
                thingmenu.add_item("Replace {}.".format(self.elements["MACGUFFIN"]), self._use_macguffin)
            if camp.party_has_skill(gears.stats.Repair):
                thingmenu.add_item("Attempt to repair fusion core.", self._use_repair)
            if camp.party_has_skill(gears.stats.Science):
                thingmenu.add_item("Attempt to stabilize plasma field.", self._use_science)

    def _use_repair(self, camp: gears.GearHeadCampaign):
        if camp.do_skill_test(gears.stats.Knowledge, gears.stats.Repair, self.rank+10, difficulty=gears.stats.DIFFICULTY_HARD):
            self._activate_power_plant(camp)
        else:
            pbge.alert("You can't even figure out what's wrong with the power plant. This device is beyond your current ability to repair.")

    def _use_science(self, camp: gears.GearHeadCampaign):
        if camp.do_skill_test(gears.stats.Knowledge, gears.stats.Science, self.rank+10, difficulty=gears.stats.DIFFICULTY_AVERAGE):
            self._activate_power_plant(camp)
        else:
            pbge.alert("As near as you can tell, there is a mechanical issue with the power plant. Stabilizing the plasma field would require more scientific knowledge than you currently possess.")

    def _use_macguffin(self, camp):
        camp.take_item(self.elements["MACGUFFIN"])
        self._activate_power_plant(camp)

    def _activate_power_plant(self, camp):
        pbge.alert("You succeed. The power plant hums back into normal operation.")
        self.elements["POWERPLANT"].activate_core()
        self.repaired_generator = True
        camp.dole_xp(200)
        camp.campdata[ROPPCD_HERO_POINTS] += 1
        if not self.accepted_mission:
            self.end_plot(camp)

    def NPC_offers(self, camp):
        mylist = list()

        if not self.accepted_mission:
            mylist.append(Offer(
                "[HELLO] The power's gone bonky wook today; I won't be able to use the autofab until it's back up.",
                context=ContextTag([context.HELLO,]), subject=self, subject_start=True
            ))

            if self.memo:
                mylist.append(Offer(
                    "Who told you that? Let me know so I can kick them next time I see them. I could fix the generator if it was out in the open, but it's inside the spaceship wreckage in the debris field. You don't even want to know what kind of stuff lives in there.",
                    context=ContextTag([context.CUSTOM]),
                    data={"reply": "I was told you could go fix the powerplant."}, subject=self, subject_start=True,
                ))
            else:
                mylist.append(Offer(
                    "Hold up there. The generator is buried under tons of scrap; the scrap is infested by rats, mutants, and worse. Used to be a spaceship, now it's more like a deathtrap. I'd need a security team to get down there. There's no way I'm going to get a security team with this war going on.",
                    context=ContextTag([context.CUSTOM]),
                    data={"reply": "You're a mechanic; why don't you go fix it?"}, subject=self
                ))

            mylist.append(Offer(
                "[GOOD_IDEA] For a cavalier like yourself it shouldn't be any problem to get to the bottom of things. Literally. Come back and see me if you survive.",
                context=ContextTag([context.CUSTOMREPLY,]), subject=self,
                data={"reply": "Maybe I could fix it for you?"},
                effect=self._accept_mission
            ))
        elif self.accepted_mission and self.repaired_generator:
            mylist.append(Offer(
                "[GOOD_JOB] Here is a {} that I was planning to strip for parts. Hopefully you can put it to good use.".format(self.elements["MECHA"].get_full_name()),
                context=ContextTag([context.CUSTOM]),
                data={"reply": "I have repaired the powerplant."},
                effect=self._get_reward
            ))

        return mylist

    def _accept_mission(self, camp):
        self.accepted_mission = True
        self.RUMOR = None
        self.memo = Memo("{NPC} asked you to repair the generator in the derelict spaceship in the scrapyard.".format(**self.elements), self.elements["NPC_SCENE"])

    def _get_reward(self, camp):
        camp.party.append(self.elements["MECHA"])
        self.end_plot(camp, True)


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
        self.add_sub_plot(nart, "ROPP_SPACEPORT_SCRAMBLE")
        return True


class SpaceportScramble(Plot):
    LABEL = "ROPP_SPACEPORT_SCRAMBLE"
    scope = "METRO"
    active = True

    RUMOR = Rumor(
        "the spaceport has been placed on lockdown, meaning we're all locked down too",
        offer_msg="Surely you noticed the guardbots outside? When the fighting started they set the security system to red alert. Those of us who couldn't get out in time are hunkering down here until it's safe.",
        offer_subject="the spaceport has been placed on lockdown",
        offer_subject_data="the spaceport",
        memo="The spaceport has been placed on lockdown. Until the system is deactivated, it won't be safe to travel in this district.",
        memo_location="LOCALE",
    )

    def custom_init(self, nart):
        self.elements["DUNGEON"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['000000B7']
        self.elements["GOAL_LEVEL"] = self.elements["DUNGEON"].goal_level

        _ = self.register_element("_room", pbge.randmaps.rooms.OpenRoom(9,9), dident="GOAL_LEVEL")
        _ = self.register_element("COMPY", ghwaypoints.OldTerminal(
            name="Security Computer", 
            desc="This computer handles the automated security system for the spaceport.", 
            plot_locked=True
        ), dident="_room")

        self.elements["SHOPKEEPER"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000005E']
        self.elements["BLACKMARKET"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000005C']

        self.hid_the_shopkeeper = False

        return True

    def t_UPDATE(self, camp: gears.GearHeadCampaign):
        if not self.hid_the_shopkeeper:
            camp.freeze(self.elements["SHOPKEEPER"])
            self.hid_the_shopkeeper = True

    def BLACKMARKET_ENTER(self, camp):
        _ = pbge.alert("This shop appears to be deserted.")

    def COMPY_menu(self, camp, thingmenu):
        thingmenu.desc += " Currently the entire spaceport and its surrounding district are highlighted in red."
        thingmenu.add_item("Deactivate the security system.", self._deactivate_security)
        thingmenu.add_item("Leave it alone.", None)

    def _deactivate_security(self, camp):
        _ = pbge.alert("You shut down the security alert for the spaceport district. The spaceport buildings themselves remain highlighted in red.")
        self.elements["SHOPKEEPER"].place(self.elements["BLACKMARKET"])
        camp.campdata[ROPPCD_HERO_POINTS] += 1
        self.end_plot(camp, True)


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
        self.add_sub_plot(nart, "RANDOM_SHOP")
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
        self.add_sub_plot(nart, "ROPP_CARGO_PLOT")
        self.add_sub_plot(nart, "ROPP_WAREHOUSE_HOTEL")
        return True

class WarehouseHotelPlot(Plot):
    # Folks are trying to keep the district running out of the hotel.
    LABEL = "ROPP_WAREHOUSE_HOTEL"
    scope = "METRO"
    active = True

    def custom_init(self, nart):
        self.elements["BUSINESS_CENTER"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['000000B3']
        self.elements["MAKESHIFT_CLINIC"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['000000B4']

        npc1 = self.register_element("ARMSDEALER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS["Smuggler"]
            ), dident="BUSINESS_CENTER")

        self.arms_shop = services.Shop(
            npc=npc1, ware_types=services.ARMS_DEALER, rank=self.rank + 10,
            shop_faction=gears.factions.BoneDevils, buy_stolen_items=True
        )

        npc2 = self.register_element("CURIODEALER", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS["Tekno"]
            ), dident="BUSINESS_CENTER")

        self.curio_shop = services.Shop(
            npc=npc2, ware_types=services.CURIO_SHOP, rank=self.rank + 5,
            shop_faction=gears.factions.DeadzoneFederation, buy_stolen_items=True
        )

        return True

    def ARMSDEALER_offers(self, camp):
        mylist = list()

        mylist.append(Offer(
            "[HELLO] There may be a war going on outside, but these weapons aren't going to sell themselves.",
            context=ContextTag([context.HELLO]),
        ))

        mylist.append(Offer("Maybe next time we make a deal I won't be working out of a hotel lobby.",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.arms_shop,
                            data={"wares": "arms"},
                            ))

        return mylist

    def CURIODEALER_offers(self, camp):
        mylist = list()

        mylist.append(Offer(
            "[CRYPTIC_GREETING] I have a wide selection of strange goods looking for a new owner.",
            context=ContextTag([context.HELLO]),
        ))

        mylist.append(Offer(
            "I cannot guarantee the safety, efficacy, or authenticity of any of these goods, but at the very least you shall be entertained.",
            context=ContextTag([context.OPEN_SHOP]), effect=self.curio_shop,
            data={"wares": "curios"},
        ))

        return mylist


class WarehouseCargoPlot(Plot):
    # Once the cargo has been discovered, the PC can hand it over to their side in the world map war or to one
    # of the needy communities in Pirate's Point. Doing the former helps your side; doing the latter provides
    # a hero point.
    LABEL = "ROPP_CARGO_PLOT"
    scope = True
    active = True

    def custom_init(self, nart):
        self.elements['MAYOR'] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['000000AF']
        self.gave_cargo_to_citizens = False
        return True

    def t_UPDATE(self, camp):
        if not self.memo:
            if camp.campdata.get(ROPPCD_FOUND_CARGO, False):
                self.memo = "You discovered a shipment of food and medicine in the warehouse district. This would be useful to someone for the war."

    def MAYOR_offers(self, camp):
        mylist = list()

        if not self.gave_cargo_to_citizens:
            mylist.append(Offer(
                "[HELLO] Welcome to Pirate's Point; if you're hoping to speak to the person in charge you'll need to go to the uptown district.",
                context=ContextTag([context.HELLO])
            ))

            if not camp.campdata.get(ROPPCD_SPENT_CARGO, False):
                mywar: worldmapwar.WorldMapWar = camp.campdata["WORLD_MAP_WAR"]
                mylist.append(Offer(
                    "I advocate for the welfare of Pirate Point's residents. Bogo prefers not to concern himself with such practical matters... not even now, when the war has made food and safety more precarious than ever. Supplies are short and tempers are even shorter.",
                    context=ContextTag([context.CUSTOM]), data={"reply": "So what's your job as mayor, then?"},
                    subject=self, subject_start=True
                ))

                if mywar.player_team and mywar.player_team is camp.scene.get_metro_scene().faction:
                    mylist.append(Offer(
                        "[OK] From now on, I will forward all of the citizens' complaints to you. There's also some paperwork I'm going to need you to sign.",
                        context=ContextTag([context.CUSTOM]), data={"reply": "I have conquered this district and you answer to me now."},
                        subject=self, subject_start=True
                    ))

                if camp.campdata.get(ROPPCD_FOUND_CARGO, False):
                    mylist.append(Offer(
                        "[THATS_GREAT] This will be a big help for us. I'm afraid I can't offer you a reward, since everything we had has already been spent, but you will have our eternal gratitude.",
                        context=ContextTag([context.CUSTOM]), effect=self._donate_to_citizens,
                        data={"reply": "I've found a shipment of food and medicine that could help the people who live here."}
                    ))

                    mylist.append(Offer(
                        "[THATS_GREAT] This will be a big help for everyone in Pirate's Point. I'm afraid I can't offer you a reward, since everything we had has already been spent, but you will have our eternal gratitude.",
                        context=ContextTag([context.CUSTOMREPLY]), effect=self._donate_to_citizens,
                        data={"reply": "I've found a shipment of food and medicine that could help the people who live here."},
                        subject=self
                    ))
        return mylist

    def _donate_to_citizens(self, camp):
        camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000000F'].metrodat.local_reputation += 30  # Residential District
        camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000007'].metrodat.local_reputation += 20  # The Nogos
        camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000000B'].metrodat.local_reputation += 20  # Shopping District
        camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000009'].metrodat.local_reputation += 10  # The Scrapyard
        camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000014'].metrodat.local_reputation += 10  # The Spaceport
        camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000011'].metrodat.local_reputation += 10  # The Dockyards
        camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000003'].metrodat.local_reputation += 10  # Uptown District
        camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000000D'].metrodat.local_reputation += 10  # Warehouse District
        
        camp.campdata[ROPPCD_HERO_POINTS] += 1
        camp.campdata[ROPPCD_SPENT_CARGO] = True
        self.end_plot(camp, True)

    @override
    def _get_generic_offers(self, npc, camp: gears.GearHeadCampaign):
        mylist = list()
        mywar: worldmapwar.WorldMapWar = camp.campdata["WORLD_MAP_WAR"]

        if camp.is_not_lancemate(npc) and mywar.player_team and mywar.player_team is npc.faction:
            if camp.campdata.get(ROPPCD_FOUND_CARGO, False) and not camp.campdata.get(ROPPCD_SPENT_CARGO, False):
                mylist.append(Offer(
                    "[THATS_GREAT] I'll pass this information along to the quartermaster. Here's a bonus for your service to the cause.",
                    context=ContextTag([context.CUSTOM]), effect=self._donate_to_army,
                    data={"reply": "I've found a container of supplies that could help our team."}
                ))

        return mylist

    def _donate_to_army(self, camp: gears.GearHeadCampaign):
        for sk in gears.stats.COMBATANT_SKILLS:
            camp.dole_xp(50, sk)
        reward = gears.selector.calc_mission_reward(self.rank, 75, round_it_off=True)
        plotutility.CashRewardWithNotification(camp, reward)
        camp.campdata[ROPPCD_SPENT_CARGO] = True
        camp.campdata["WORLD_MAP_WAR"].war_teams[camp.campdata["WORLD_MAP_WAR"].player_team].boosted = True
        self.memo = None


class WarehousePasswordsPlot(Plot):
    LABEL = "ROPP_PASSWORDS_PLOT"
    scope = True
    active = True

    def custom_init(self, nart):
        self.door_codes = ["".join([str(random.randint(0,9)) for _ in range(6)]) for _ in range(5)]
        self.known_warehouse_codes = list()
        self.elements["WH13"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000009B']
        myroom = self.register_element(
            "_room13", self._get_warehouse_room(), dident="WH13"
        )
        self.register_element("FIRST_NOTE", ghwaypoints.KnifeNote(
            desc="Dagmar-\n\nYou've been assigned to warehouse 45 tonight. Don't forget that the door code is {}. Please try to remember it this time.".format(self.door_codes[0])
        ), dident="_room13")

        self.elements["WH45"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['000000A9']
        mydoor = self.seek_element(nart, "WH45_DOOR", lambda n,c: self._seek_door(n,c,"Warehouse 45"), scope=nart.camp)
        mydoor.plot_locked = True
        self.wh45_locked = True

        self.register_element("_room45", self._get_warehouse_room(), dident="WH45")
        self.register_element("SECOND_NOTE", ghwaypoints.KnifeNote(
            desc="Dagmar-\n\nI agree with you that writing down the door code is bad OpSec, but forgetting it entirely and leaving a shipment in front of the door overnight is *much worse*. The code for #9 is {}.".format(self.door_codes[1])
        ), dident="_room45")

        self.elements["WH9"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['000000AA']

        mydoor = self.seek_element(nart, "WH9_DOOR", lambda n,c: self._seek_door(n,c,"Warehouse 9"), scope=nart.camp)
        mydoor.plot_locked = True
        self.wh9_locked = True

        self.register_element("_room9", self._get_warehouse_room(), dident="WH9")
        self.register_element("THIRD_NOTE", ghwaypoints.KnifeNote(
            desc="Dagmar-\n \n Situation has changed. The big cheese from down south is moving a high security package into warehouse 24.\n \n It's very very important that no unauthorized people learn about this package; we've got to be on our \"Super S\" game for this one. That's why it's very very very important that you remember the door code is {}. Make sure you don't forget. Tattoo it on your arm if you have to. I'm counting on you, Dag; I know you can do it.".format(self.door_codes[2])
        ), dident="_room9")

        mydoor = self.seek_element(nart, "WH24_DOOR", lambda n,c: self._seek_door(n,c,"Warehouse 24"), scope=nart.camp)
        mydoor.plot_locked = True
        self.wh24_locked = True

        self.elements["WH24"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['000000AB']
        self.register_element("_room24", self._get_warehouse_room(), dident="WH24")
        self.register_element("FOURTH_NOTE", ghwaypoints.KnifeNote(
            desc="Dagmar-\n \n Sorry about last night. Your team was the decoy so we could move the ruby in safety. I honestly didn't expect anyone to attack. If you need a good deal on a new eyeball, tell Kira I sent you.\n \n Anyhow, you've got overtime at warehouse 2 tonight. The passcode is {}.".format(self.door_codes[3])
        ), dident="_room24")

        mydoor = self.seek_element(nart, "WH2_DOOR", lambda n,c: self._seek_door(n,c,"Warehouse 2"), scope=nart.camp)
        mydoor.plot_locked = True
        self.wh2_locked = True

        self.elements["WH2"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['000000AC']
        self.register_element("_room2", self._get_warehouse_room(), dident="WH2")
        self.register_element("FIFTH_NOTE", ghwaypoints.KnifeNote(
            desc="Nancy-\n \n Thank you for being my manager at Bowser Security, but I'm afraid it's time for me to pursue new challenges elsewhere. I got a generous offer for that ruby everyone was so enamoured with. The cash will more than cover my medical bills and relocation to someplace decent.\n\n *Love, Dagmar*".format(self.door_codes[3])
        ), dident="_room2")
        self.register_element("RUBY_CHEST", ghwaypoints.SteelBox(
            desc="This steel case contains a foam insert for a large hexagonal prism. The prism itself is long gone.", plot_locked=True
        ), dident="_room2")

        cargo_room = self.register_element("_room2b", pbge.randmaps.rooms.ClosedRoom(8,12, decorate=gharchitecture.WarehouseDecor()), dident="WH2")
        mydoor = self.register_element("CARGO", ghwaypoints.Waypoint(
            name="Cargo Container", plot_locked=True,
            desc="This cargo container is loaded with packaged food, medicine, and consumer goods."
            ))
        my_cargo = ghterrain.PersonalCargoContainerTerrset(waypoints={"DOOR": mydoor})
        cargo_room.contents.append(my_cargo)

        return True

    def _get_warehouse_room(self):
        myroom = pbge.randmaps.rooms.ClosedRoom(10,8, decorate=gharchitecture.StorageRoomDecor())
        for t in range(random.randint(3,6)):
            myroom.contents.append(ghwaypoints.Lockers())
        return myroom

    def _seek_door(self, nart, candidate, door_name):
        return isinstance(candidate, ghwaypoints.ReinforcedDoor) and candidate.name == door_name

    def CARGO_menu(self, camp, thingmenu):
        if camp.campdata.get(ROPPCD_SPENT_CARGO, False):
            self.elements["CARGO"].desc = "This cargo container is now empty."
            thingmenu.desc = self.elements["CARGO"].desc
        
        elif not camp.campdata.get(ROPPCD_FOUND_CARGO, False):
            thingmenu.desc += " These items could be a great boon to the war effort."
            thingmenu.add_item("[Continue]", self._get_cargo)

    def _get_cargo(self, camp: gears.GearHeadCampaign):
        camp.campdata[ROPPCD_FOUND_CARGO] = True
        pbge.alert("You gain 100XP.")
        camp.dole_xp(100)
        self.memo = "You have discovered a shipment of food and medicine that might be useful to somebody in Pirate's Point."
        camp.check_trigger("UPDATE")

    def update_memo(self, camp):
        if self.known_warehouse_codes and not camp.campdata.get(ROPPCD_FOUND_CARGO, False):
            self.memo = "You have learned the keycode for {}.".format(pbge.util.and_join_string(self.known_warehouse_codes))

    def FIRST_NOTE_BUMP(self, camp):
        if self.wh45_locked:
            self.wh45_locked = False
            pbge.BasicNotification("You have discovered the keycode for Warehouse 45.", count=150)
            self.known_warehouse_codes.append("Warehouse 45")
            self.update_memo(camp)

    def SECOND_NOTE_BUMP(self, camp):
        if self.wh9_locked:
            self.wh9_locked = False
            pbge.BasicNotification("You have discovered the keycode for Warehouse 9.", count=150)
            self.known_warehouse_codes.append("Warehouse 9")
            self.update_memo(camp)

    def THIRD_NOTE_BUMP(self, camp):
        if self.wh24_locked:
            self.wh24_locked = False
            pbge.BasicNotification("You have discovered the keycode for Warehouse 24.", count=150)
            self.known_warehouse_codes.append("Warehouse 24")
            self.update_memo(camp)

    def FOURTH_NOTE_BUMP(self, camp):
        if self.wh2_locked:
            self.wh2_locked = False
            pbge.BasicNotification("You have discovered the keycode for Warehouse 2.", count=150)
            self.known_warehouse_codes.append("Warehouse 2")
            self.update_memo(camp)

    def WH45_DOOR_menu(self, camp, thingmenu):
        thingmenu.desc = "This door is locked, and it is too strong to break down. What do you want to do?"
        thingmenu.add_item("Attempt to hack the lock. [Computers + Craft]", lambda c: self._attempt_hack_door(c, "WH45_DOOR"))
        if not self.wh45_locked:
            thingmenu.add_item("Enter keycode {}.".format(self.door_codes[0]), lambda c: self._unlock_door(c, "WH45_DOOR"))

        thingmenu.add_item("Leave it alone.", None)

    def WH9_DOOR_menu(self, camp, thingmenu):
        thingmenu.desc = "This door is locked, and it is too strong to break down. What do you want to do?"
        thingmenu.add_item("Attempt to hack the lock. [Computers + Craft]", lambda c: self._attempt_hack_door(c, "WH9_DOOR"))
        if not self.wh9_locked:
            thingmenu.add_item("Enter keycode {}.".format(self.door_codes[1]), lambda c: self._unlock_door(c, "WH9_DOOR"))

        thingmenu.add_item("Leave it alone.", None)

    def WH24_DOOR_menu(self, camp, thingmenu):
        thingmenu.desc = "This door is locked, and it is too strong to break down. There are signs that someone tried to break it down before you arrived. What do you want to do?"
        thingmenu.add_item("Attempt to hack the lock. [Computers + Craft]", lambda c: self._attempt_hack_door(c, "WH24_DOOR"))
        if not self.wh24_locked:
            thingmenu.add_item("Enter keycode {}.".format(self.door_codes[2]), lambda c: self._unlock_door(c, "WH24_DOOR"))

        thingmenu.add_item("Leave it alone.", None)

    def WH2_DOOR_menu(self, camp, thingmenu):
        thingmenu.desc = "This door is locked, and it is too strong to break down. What do you want to do?"
        thingmenu.add_item("Attempt to hack the lock. [Computers + Craft]", lambda c: self._attempt_hack_door(c, "WH2_DOOR"))
        if not self.wh2_locked:
            thingmenu.add_item("Enter keycode {}.".format(self.door_codes[3]), lambda c: self._unlock_door(c, "WH2_DOOR"))

        thingmenu.add_item("Leave it alone.", None)

    def _attempt_hack_door(self, camp: gears.GearHeadCampaign, door_ident):
        # Lambda this method for all the different doors.
        pc = camp.do_skill_test(
            gears.stats.Craft, gears.stats.Knowledge, gears.stats.get_skill_target(self.rank, difficulty=gears.stats.DIFFICULTY_LEGENDARY),
            no_random=True
        )
        if pc:
            if pc is camp.pc:
                pbge.alert("You hack the lock. The door can now be opened.")
            else:
                pbge.alert("{} hacks the lock. The door can now be opened.".format(pc))
            self.elements[door_ident].plot_locked = False
        else:
            pbge.alert("You are not skilled enough to hack this lock.")

    def _unlock_door(self, camp: gears.GearHeadCampaign, door_ident):
        # Lambda this method for all the different doors too.
        pbge.alert("The code unlocks the door.")
        self.elements[door_ident].plot_locked = False

