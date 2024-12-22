# Utility plots for Raid on Pirate's Point, since I am still working on the scenario editor.

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


class ROPP_WarStarter(Plot):
    LABEL = "ROPP_WAR_STARTER"
    scope = True
    active = True

    def custom_init(self, nart):
        self.elements[worldmapwar.WORLD_MAP_IDENTIFIER] = "WORLDMAP_6"
        world_map = nart.camp.campdata["WORLDMAP_6"]
        for node in world_map.nodes:
            node.visible = True

        war_teams = dict()
        war_teams[gears.factions.TheSolarNavy] = worldmapwar.WarStats(
            nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000001'],
            color=1, unpopular=False, occtype=wmw_occupation.WMWO_MARTIAL_LAW
        )

        war_teams[gears.factions.TreasureHunters] = worldmapwar.WarStats(
            nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000003'],
            color=2, unpopular=False, occtype=wmw_occupation.WMWO_DEFENDER
        )

        war_teams[gears.factions.AegisOverlord] = worldmapwar.WarStats(
            nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000005'],
            color=3, unpopular=True, loyalty=50, occtype=wmw_occupation.WMWO_IRON_FIST
        )

        nart.camp.set_faction_allies(gears.factions.TreasureHunters, gears.factions.AegisOverlord)
        nart.camp.set_faction_enemies(gears.factions.TreasureHunters, gears.factions.TheSolarNavy)
        nart.camp.set_faction_enemies(gears.factions.AegisOverlord, gears.factions.TheSolarNavy)

        self.elements[worldmapwar.WORLD_MAP_TEAMS] = war_teams
        sp = self.add_sub_plot(nart, "WORLD_MAP_WAR", ident="ROPPWAR")
        self.world_map_war = self.register_element("WORLD_MAP_WAR", sp.world_map_war)
        nart.camp.campdata["WORLD_MAP_WAR"] = self.world_map_war

        if pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
            self.register_element("LOCALE", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000001'])
            self.register_element("_ROOM", pbge.randmaps.rooms.FuzzyRoom(5,5), dident="LOCALE")
            self.register_element("COMPY", ghwaypoints.OldTerminal(
                plot_locked=True, anchor=pbge.randmaps.anchors.middle, name="War Simulator",
                desc="This is a computer terminal to test the world map war system. Yay!"
            ), dident="_ROOM")

        # Locate the major NPCs.
        self.seek_element(nart, "NPC_CHARLA", self._seek_charla, lock=True)
        self.seek_element(nart, "NPC_BRITAINE", self._seek_britaine, lock=True)
        self.seek_element(nart, "NPC_PINSENT", self._seek_pinsent, lock=True)
        self.seek_element(nart, "NPC_BOGO", self._seek_bogo, lock=True)
        self.seek_element(nart, "NPC_AEGIS", self._seek_aegis, lock=True)

        self.add_sub_plot(nart, "ROPP_SOLAR_NAVY_JOINER")
        self.add_sub_plot(nart, "ROPP_TREASURE_HUNTERS_JOINER")
        self.add_sub_plot(nart, "ROPP_AEGIS_JOINER")

        return True

    def __setstate__(self, state):
        # For v0.947 and earlier: set occtype for the war teams.
        self.__dict__.update(state)
        wardict = self.elements[worldmapwar.WORLD_MAP_TEAMS]
        wardict[gears.factions.TheSolarNavy].occtype = wmw_occupation.WMWO_MARTIAL_LAW
        wardict[gears.factions.TheSolarNavy].unpopular = False
        wardict[gears.factions.AegisOverlord].occtype = wmw_occupation.WMWO_IRON_FIST

    def ROPPWAR_WIN(self, camp: gears.GearHeadCampaign):
        pbge.alert("Congratulations, you have won the war! Thank you for playing the early access version of Raid on Pirate's Point.")
        pbge.alert("Later on there will be different endings and more options, but for now I just want to get a new release out the door. Please let me know if you found any problems.")
        camp.eject()

    def ROPPWAR_LOSE(self, camp: gears.GearHeadCampaign):
        pbge.alert("Your side in the war has been defeated. Thank you for playing the early access version of Raid on Pirate's Point.")
        pbge.alert("Later on there will be different endings and more options, but for now I just want to get a new release out the door. Please let me know if you found any problems.")
        camp.eject()

    def _seek_charla(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.mnpcid == "Admiral Charla"

    def _seek_britaine(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.mnpcid == "Britaine"

    def _seek_pinsent(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.mnpcid == "General Pinsent"

    def _seek_bogo(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.mnpcid == "Jjang Bogo"

    def _seek_aegis(self, nart, candidate):
        return (isinstance(candidate, gears.base.Character) and candidate.job.name == "Diplomat" and
                candidate.faction is gears.factions.AegisOverlord)

    def COMPY_menu(self, camp, thingmenu):
        thingmenu.add_item("Start the next round", self.start_war_round)

    def start_war_round(self, camp):
        myround = worldmapwar.WorldMapWarRound(self.world_map_war, camp)
        while myround.keep_going():
            result = myround.perform_turn()


class SolarNavyJoinerPlot(Plot):
    LABEL = "ROPP_SOLAR_NAVY_JOINER"
    scope = "METRO"
    active = True

    RUMOR = Rumor(
        "Admiral Charla is recruiting cavaliers for the Pirate Point operation",
        offer_msg="The Solar Navy's goal is to remove the Aegis Consulate from Pirate's Point. Should be a lot of good missions in it for you. If you want the job, you can speak to her at the Field HQ.",
        offer_subject="Admiral Charla is recruiting cavaliers",
        offer_subject_data="the Pirate Point operation",
        memo="Admiral Charla is recruiting cavaliers for the Pirate Point operation. You should speak to her if you want to aid the Solar Navy.",
        prohibited_npcs=("NPC_CHARLA",),
    )

    def custom_init(self, nart):
        # We have inherited all the NPCs and the war from the WarStarter. Just plug in some dialogue.
        mymetroscene = self.register_element("METROSCENE", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000001'])
        self.elements["METRO"] = mymetroscene.metrodat
        self.elements["NPC_SCENE"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000018']

        self.signing_bonus = gears.selector.calc_mission_reward(self.rank+10, 500)
        self.got_starter_kit = False
        self.did_cutscene = False
        return True

    def NPC_SCENE_ENTER(self, camp):
        if not self.did_cutscene:
            charla = self.elements["NPC_CHARLA"]
            pinsent = self.elements["NPC_PINSENT"]
            britaine = self.elements["NPC_BRITAINE"]
            pbge.alert("You enter the mobile HQ as the leaders of the three divisions of Terran service- the Solar Navy, the Defense Force, and the Guardians- debate the objectives of this operation.")
            ghcutscene.SimpleMonologueDisplay("Following the Typhon incident, we cannot afford to let Aegis Overlord maintain any presence on Earth. Their consulate in Pirate's Point must be destroyed.", charla)(camp)
            ghcutscene.SimpleMonologueDisplay("As an added bonus, we can get rid of the pirates who've been infesting this area. Two birds with one stone if you ask me.", britaine)(camp, False)
            ghcutscene.SimpleMonologueDisplay("I agree with you that Aegis needs to go, but invading a soverign city-state is going to cause more problems long-term. If you strike carelessly at every percieved threat, all you end up doing is making more enemies.", pinsent)(camp, False)
            ghcutscene.SimpleMonologueDisplay("You are thinking like a turtle, Pinsent, whereas I think like a hawk. The enemy must be defeated now before they become a threat again. Your defensive strategy didn't save us from Typhon, did it?", charla)(camp, False)
            ghcutscene.SimpleMonologueDisplay("No, and I live with the consequences of that every day... You are the one in charge of this operation and I will follow your lead. But I will not be silent when I think you're making a mistake.", pinsent)(camp, False)
            ghcutscene.SimpleMonologueDisplay("Ha-haw! Personally, I can't wait to get into battle!", britaine)(camp, False)
            pbge.alert("The three leaders stop talking when they notice that you have entered the vehicle.")
            self.did_cutscene = True

    def NPC_CHARLA_offers(self, camp):
        mylist = list()

        if not self.elements["WORLD_MAP_WAR"].player_team:
            mylist.append(Offer(
                "[THATS_GOOD] Here is a signing bonus of ${:,}; you can use it to get some equipment from the supply depot. General Pinsent can fill you in on how the ground operations are proceeding.".format(self.signing_bonus),
                ContextTag([context.CUSTOM]), effect=self._join_team,
                data={"reply": "I want to help the Solar Navy."}
            ))

        return mylist

    def _join_team(self, camp):
        self.elements["WORLD_MAP_WAR"].set_player_team(camp, gears.factions.TheSolarNavy)
        self.RUMOR = None
        self.memo = None
        camp.credits += self.signing_bonus
        pbge.BasicNotification("You receive ${:,}.".format(self.signing_bonus))


class TreasureHuntersJoinerPlot(Plot):
    LABEL = "ROPP_TREASURE_HUNTERS_JOINER"
    scope = "METRO"
    active = True

    RUMOR = Rumor(
        "Jjang Bogo is offering big money for pilots to defend Pirate's Point",
        offer_msg="The Solar Navy has finally decided to get rid of our town. If we don't fight back, it'll be game over for Pirate's Point. You can talk to the grandmaster at [NPC_SCENE] to find out more.",
        offer_subject="Jjang Bogo is offering big money",
        offer_subject_data="defending Pirate's Point",
        memo="The grandmaster of the Treasure Hunter's Guild, Jjang Bogo, is offering lots of money for pilots to defend Pirate's Point from the Solar Navy.",
        prohibited_npcs=("NPC_BOGO",),
    )

    def custom_init(self, nart):
        # We have inherited all the NPCs and the war from the WarStarter. Just plug in some dialogue.
        mymetroscene = self.register_element("METROSCENE", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000003'])
        self.elements["METRO"] = mymetroscene.metrodat
        self.elements["NPC_SCENE"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000002C']
        self.elements["NPC_MAYOR"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000002E']

        self.signing_bonus = gears.selector.calc_mission_reward(self.rank+10, 500)
        self.did_cutscene = False
        return True

    def NPC_BOGO_offers(self, camp):
        mylist = list()

        if not self.elements["WORLD_MAP_WAR"].player_team:
            mylist.append(Offer(
                "[THATS_GOOD] I give you ${cash:,} to prepare for the upcoming battles. {NPC_MAYOR} can explain what you need to do.".format(cash=self.signing_bonus, **self.elements),
                ContextTag([context.CUSTOM]), effect=self._join_team,
                data={"reply": "I want to help defend Pirate's Point."}
            ))

        return mylist

    def NPC_SCENE_ENTER(self, camp):
        if not self.did_cutscene:
            bogo = self.elements["NPC_BOGO"]
            mayor = self.elements["NPC_MAYOR"]
            pbge.alert("As you enter the hall, a heated discussion is going on between the rulers of Pirate's Point.")
            ghcutscene.SimpleMonologueDisplay("On this world, the Lunars are outlaws just like the rest of us. We will defend them, and they us, in accordance with the pact.", bogo)(camp)
            ghcutscene.SimpleMonologueDisplay("The Blades of Crihna are not going to be happy about this...", mayor)(camp, False)
            ghcutscene.SimpleMonologueDisplay("I'm not happy about it either, but it is what it is. Aegis cannot be trusted; if there's a way for them to sieze control from us, they will.", bogo)(camp, False)
            ghcutscene.SimpleMonologueDisplay("For now, at least, we need each other. The Guild lacks the power to defeat the Solar Navy in a conventional battle. Aegis has pilots and mecha but they lack the support of the people.", bogo)(camp, False)
            ghcutscene.SimpleMonologueDisplay("So we fight side by side. If the situation changes, we may choose to make different alliances.", bogo)(camp, False)
            self.did_cutscene = True

    def _join_team(self, camp):
        self.elements["WORLD_MAP_WAR"].set_player_team(camp, gears.factions.TreasureHunters)
        self.RUMOR = None
        self.memo = None
        camp.credits += self.signing_bonus
        pbge.BasicNotification("You receive ${:,}.".format(self.signing_bonus))


class AegisJoinerPlot(Plot):
    LABEL = "ROPP_AEGIS_JOINER"
    scope = "METRO"
    active = True

    RUMOR = Rumor(
        "{NPC_AEGIS} is seeking a skilled pilot to defend the Lunar district from Terran invaders",
        offer_msg="The people of Terra are always fighting, but from what I hear the warlord threatening us now is more powerful than most. You should go to the Aegis Consulate and volunteer for service.",
        offer_subject="defend the Lunar district from Terran invaders",
        offer_subject_data="defending the Lunar district",
        memo="{NPC_AEGIS} is looking for a skilled pilot to defend the Lunar district of Pirate's Point from Terran invaders.",
        prohibited_npcs=("NPC_AEGIS",),
    )

    def custom_init(self, nart):
        # We have inherited all the NPCs and the war from the WarStarter. Just plug in some dialogue.
        mymetroscene = self.register_element("METROSCENE", nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['00000005'])
        self.elements["METRO"] = mymetroscene.metrodat
        self.elements["NPC_SCENE"] = nart.camp.campdata["SCENARIO_ELEMENT_UIDS"]['0000002F']

        self.did_cutscene = False
        self.can_try_to_join = True
        return True

    def NPC_AEGIS_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        if not self.elements["WORLD_MAP_WAR"].player_team and self.can_try_to_join:
            if camp.pc.has_badge(gears.oldghloader.TYPHON_SLAYER.name):
                mylist.append(Offer(
                    "[HAGOODONE] I know exactly who you are, [audience]. You have a lot of nerve showing your face here. Unless you have official diplomatic business, I suggest you leave.",
                    ContextTag([context.CUSTOM]), effect=self._reject_pc,
                    data={"reply": "I pledge my services to Aegis Overlord Luna."}
                ))
            elif camp.pc.get_tags().intersection(gears.personality.MUTATIONS):
                mylist.append(Offer(
                    "I'm afraid the Aegis Expeditionary Force only accepts human pilots. Maybe the Solar Navy is desperate enough to hire a malformed deviant like you.",
                    ContextTag([context.CUSTOM]), effect=self._reject_pc,
                    data={"reply": "I pledge my services to Aegis Overlord Luna."}
                ))
            else:
                mylist.append(Offer(
                    "[THATS_GOOD] Aegis Overlord will overcome all opposition! I will give your team a set of advanced Lunar mecha; these should be far superior to anything you can purchase on Earth.",
                    ContextTag([context.CUSTOM]), effect=self._join_team,
                    data={"reply": "I pledge my services to Aegis Overlord Luna."}
                ))

        return mylist

    def _reject_pc(self, camp):
        self.can_try_to_join = False

    def NPC_SCENE_ENTER(self, camp):
        if not self.did_cutscene:
            diplomat = self.elements["NPC_AEGIS"]
            pbge.alert("All is silent as you enter the Aegis Consulate. The staff in the front office are hard at work, completing their tasks with tireless efficiency.")
            pbge.alert("One diplomat, obviously a {NPC_AEGIS.gender.noun} of great authority, turns to face you. You feel like {NPC_AEGIS.gender.possessive_determiner} eyes are staring directly into your soul.".format(**self.elements))
            ghcutscene.SimpleMonologueDisplay(
                "Welcome to the Aegis Consulate. As you can see, we are quite busy at the moment. Please state your business here.",
                diplomat)(camp)
            self.did_cutscene = True

    def _join_team(self, camp):
        self.elements["WORLD_MAP_WAR"].set_player_team(camp, gears.factions.AegisOverlord)
        self.RUMOR = None
        self.memo = None
        camp.party.append(gears.selector.get_design_by_full_name("CHA-03 Command Chameleon"))
        camp.party.append(gears.selector.get_design_by_full_name("CHA-02b Sniper Chameleon"))
        camp.party.append(gears.selector.get_design_by_full_name("CHA-01 Chameleon"))
        camp.party.append(gears.selector.get_design_by_full_name("CHA-01 Chameleon"))

        pbge.BasicNotification("You receive four Chameleon mecha.")
