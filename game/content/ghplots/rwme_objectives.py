from pbge.plots import Plot
import game
import gears
import pbge
import pygame
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints,plotutility,ghcutscene
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed
from . import missionbuilder
from gears import champions

RWMO_FIGHT_RANDOS = "RWMO_FIGHT_RANDOS"
RWMO_MAYBE_AVOID_FIGHT = "RWMO_MAYBE_AVOID_FIGHT"


class FightSomeRandos(Plot):
    LABEL = RWMO_FIGHT_RANDOS
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=True)
        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Defeat hostile mecha".format(myfac), missionbuilder.MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            pbge.alert("You are attacked by a force of hostile mecha.")
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class RWMO_SkilledAvoidance( Plot ):
    LABEL = RWMO_MAYBE_AVOID_FIGHT
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        self.intro_ready = True
        return True

    def LOCALE_ENTER(self,camp: gears.GearHeadCampaign):
        if self.intro_ready:
            self.intro_ready = False
            candidates = list()
            if camp.party_has_skill(gears.stats.Scouting):
                candidates.append(self.attempt_scouting)
            if camp.party_has_skill(gears.stats.Stealth):
                candidates.append(self.attempt_stealth)
            if camp.party_has_skill(gears.stats.Wildcraft):
                candidates.append(self.attempt_wildcraft)
            if candidates:
                random.choice(candidates)(camp)

    def attempt_scouting(self,camp):
        pc = camp.make_skill_roll(gears.stats.Perception,gears.stats.Scouting,self.rank)
        if pc:
            if pc.get_pilot() is camp.pc:
                mymenu = ghcutscene.PromptMenu("You detect hostile mecha on the road ahead. They are still far enough away that you can avoid them if you want to.")
            else:
                mymenu = ghcutscene.SimpleMonologueMenu("[I_HAVE_DETECTED_ENEMIES] [WE_CAN_AVOID_COMBAT]",pc,camp)
            mymenu.add_item("Avoid them",self.cancel_the_adventure)
            mymenu.add_item("Engage them",None)
            go = mymenu.query()
            if go:
                go(camp)

    def attempt_stealth(self,camp):
        pc = camp.make_skill_roll(gears.stats.Perception,gears.stats.Stealth,self.rank)
        if pc:
            if pc.get_pilot() is camp.pc:
                mymenu = ghcutscene.PromptMenu("You encounter a group of hostile mecha, but manage to remain unseen.")
            else:
                mymenu = ghcutscene.SimpleMonologueMenu("[ENEMIES_HAVE_NOT_DETECTED_US] [WE_CAN_AVOID_COMBAT]",pc,camp)
            mymenu.add_item("Avoid them",self.cancel_the_adventure)
            mymenu.add_item("Engage them",None)
            go = mymenu.query()
            if go:
                go(camp)

    def attempt_wildcraft(self,camp):
        pc = camp.make_skill_roll(gears.stats.Perception,gears.stats.Wildcraft,self.rank)
        if pc:
            if pc.get_pilot() is camp.pc:
                mymenu = ghcutscene.PromptMenu("You find tracks belonging to enemy mecha. It would be a simple matter to find an alternate route around them.")
            else:
                mymenu = ghcutscene.SimpleMonologueMenu("[THERE_ARE_ENEMY_TRACKS] [WE_CAN_AVOID_COMBAT]",pc,camp)
            mymenu.add_item("Avoid them",self.cancel_the_adventure)
            mymenu.add_item("Engage them",None)
            go = mymenu.query()
            if go:
                go(camp)

    def cancel_the_adventure(self,camp):
        camp.go(self.elements["ADVENTURE_GOAL"])
        self.adv.cancel_adventure(camp)
