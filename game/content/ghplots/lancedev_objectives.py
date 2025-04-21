from gears import relationships
from pbge.plots import Plot
import game
import gears
import pbge
import pygame
import random
from game import teams, ghdialogue
from game.content import gharchitecture, ghterrain, ghwaypoints, plotutility
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed, ghcutscene
from gears import champions
from game.content.dungeonmaker import DG_NAME, DG_ARCHITECTURE, DG_SCENE_TAGS, DG_MONSTER_TAGS, DG_TEMPORARY, \
    DG_PARENT_SCENE, DG_EXPLO_MUSIC, DG_COMBAT_MUSIC, DG_DECOR
from . import missionbuilder

# Use this custom element to set the lancemate whose mission this is.
BAME_LANCEMATE = "BAME_LANCEMATE"

# Personal Lancedev Objectives
BAMOP_DISCOVER_BIOTECHNOLOGY = "BAMOP_DiscoverBiotechnology"
BAMO_BETRAYAL = "BAMO_BETRAYAL"
BAMO_PRACTICE_DUEL = "BAMO_PRACTICE_DUEL"


class DDBAMO_PracticeDuel(Plot):
    LABEL = BAMO_PRACTICE_DUEL
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]

        self.register_element("ROOM", pbge.randmaps.rooms.FuzzyRoom(15, 15, anchor=pbge.randmaps.anchors.middle),
                              dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc = self.elements[BAME_LANCEMATE]
        self.locked_elements.add(BAME_LANCEMATE)
        self.party_member = mynpc in nart.camp.party
        if self.party_member:
            plotutility.AutoLeaver(mynpc)(nart.camp)
        plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2, allow_death=False)

        self.obj = adventureseed.MissionObjective("Defeat {}".format(mynpc), missionbuilder.MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements[BAME_LANCEMATE]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def BAME_LANCEMATE_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[DUEL_GREETING]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)
        else:
            self.obj.failed = True
        if self.party_member:
            self.elements[BAME_LANCEMATE].restore_all()
            plotutility.AutoJoiner(self.elements[BAME_LANCEMATE])(camp)
        # for pc in camp.party:
        #    pc.restore_all()


class LMBetrayalFight(Plot):
    LABEL = BAMO_BETRAYAL
    active = True
    scope = "LOCALE"

    ready_to_record = True

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        mynpc = self.elements[BAME_LANCEMATE]

        _=self.register_element(
            "ROOM", pbge.randmaps.rooms.FuzzyRoom(15, 15, anchor=pbge.randmaps.anchors.middle),
            dident="LOCALE"
        )

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,), faction=mynpc.faction), dident="ROOM")

        self.locked_elements.add(BAME_LANCEMATE)
        if mynpc in nart.camp.party:
            plotutility.AutoLeaver(mynpc)(nart.camp)
        _=plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2, allow_death=False)

        myunit = gears.selector.RandomMechaUnit(self.rank, 100, mynpc.faction, myscene.environment, add_commander=False)
        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Fight {}".format(mynpc), missionbuilder.MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements[BAME_LANCEMATE]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def BAME_LANCEMATE_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[BETRAYAL] You see, I must [objective_ep]... [CHALLENGE]",
                            context=ContextTag([context.ATTACK, ])))
        return mylist

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)
        else:
            self.obj.failed = True

        if self.adv.is_completed() and self.ready_to_record and not self.intro_ready:
            self.ready_to_record = False
            if len(myteam.get_members_in_play(camp)) < 1:
                self.elements[BAME_LANCEMATE].relationship.history.append(relationships.Memory(
                    random.choice(self.adv.mission_grammar["[win_ep]"]),
                    random.choice(self.adv.mission_grammar["[win_pp]"]),
                    -5, 
                    memtags=(relationships.MEM_Clash, relationships.MEM_Ideological, relationships.MEM_LoseToPC)
                ))
            else:
                self.elements[BAME_LANCEMATE].relationship.history.append(relationships.Memory(
                    random.choice(self.adv.mission_grammar["[lose_ep]"]),
                    random.choice(self.adv.mission_grammar["[lose_pp]"]),
                    10, 
                    memtags=(relationships.MEM_Clash, relationships.MEM_Ideological, relationships.MEM_DefeatPC)
                ))


class LMBAM_DiscoverBiotechnology(Plot):
    LABEL = BAMOP_DISCOVER_BIOTECHNOLOGY
    active = True
    scope = "LOCALE"

    DEVICES = (ghwaypoints.Biotank, ghwaypoints.PZHolo, ghwaypoints.OldMainframe)

    def custom_init(self, nart):
        myscene: gears.GearHeadScene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(8, 8), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team2.contents.append(gears.selector.generate_boss_monster(self.rank, myscene.environment, ("SYNTH", "MUTANT"), gears.scale.HumanScale))

        biotech = self.register_element("MACHINE", random.choice(self.DEVICES)(
            name="Ancient Device", plot_locked=True, anchor=pbge.randmaps.anchors.middle,
            desc="You have found an ancient device that clearly dates from the Age of Superpowers."
        ), dident="ROOM")

        self.obj = adventureseed.MissionObjective("Search for lost technology", missionbuilder.MAIN_OBJECTIVE_VALUE//2)
        self.adv.objectives.append(self.obj)

        self.got_skill = False

        return True

    def MACHINE_menu(self, camp, thingmenu):
        npc: gears.base.Character = self.elements[BAME_LANCEMATE]
        if npc and npc.is_not_destroyed() and not self.got_skill:
            thingmenu.desc += " Who knows what secrets it might contain?"
            thingmenu.add_item("[Continue]", self._get_skill)

    WORD_A = ("medical", "fabrication", "computational", "therapeutic", "scientific")
    WORD_B = ("device", "machine", "apparatus", "engine", "unit", "mechanism", "tool", "rig")

    def _get_skill(self, camp: gears.GearHeadCampaign):
        npc: gears.base.Character = self.elements[BAME_LANCEMATE]
        ghcutscene.SimpleMonologueDisplay(
            "This is a biotechnological {} {}; give me some time to examine it.".format(random.choice(self.WORD_A),random.choice(self.WORD_B)),
            npc
        )(camp)
        pbge.BasicNotification("{} gains biotechnology skill.".format(npc))
        npc.statline[gears.stats.Biotechnology] += 1
        self.obj.win(camp, 100)
        camp.dole_xp(100, gears.stats.Biotechnology)
        self.got_skill = True


