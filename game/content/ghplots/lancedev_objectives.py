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


