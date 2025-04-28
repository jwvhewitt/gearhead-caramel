from typing import override
from pbge.plots import Plot
import game
import gears
import pbge
import pygame
import random
from game import teams, ghdialogue
from game.content import gharchitecture, ghwaypoints, plotutility, missiontext, ghcutscene
from pbge.dialogue import Offer, ContextTag
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed
from gears import champions
from game.content.dungeonmaker import DG_NAME, DG_ARCHITECTURE, DG_SCENE_TAGS, DG_MONSTER_TAGS, DG_TEMPORARY, \
    DG_PARENT_SCENE, DG_EXPLO_MUSIC, DG_COMBAT_MUSIC, DG_DECOR
import copy

from . import mission_bigobs
from game.content.ghplots.missionbuilder import MAIN_OBJECTIVE_VALUE

# Mystery missions are exactly what they sound like - a mystery!
# Do not call these missions lightly - save them for one-shot local events and/or lancedev!
# A mystery mission may add an ongoing side story, a permanent complication to the campaign, 
# or who knows what else!
BAMO_MYSTERYMISSION = "BAMO_MYSTERYMISSION"


class MyMi_LancemateTimedDefense(mission_bigobs.BAM_TimedDefense):
    LABEL = BAMO_MYSTERYMISSION
    active = True
    scope = "LOCALE"

    @override
    def custom_init(self, nart):
        ok = super().custom_init(nart)

        npc = nart.camp.egg.seek_dramatis_person(nart.camp, self._is_good_npc, self)
        if not npc:
            return False

        myscene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"])
        self.register_element("NPC", npc, dident="NPC_SCENE", lock=True)
        _=plotutility.CharacterMover(nart.camp, self, npc, self.elements["LOCALE"], self.elements["_bunkerteam"])

        self.npc_obj = adventureseed.MissionObjective("Defend {}".format(self.elements["NPC"]),
                                                  MAIN_OBJECTIVE_VALUE, can_reset=False)
        self.adv.objectives.append(self.npc_obj)

        self.convo_ready = True

        return ok

    def _is_good_npc(self, camp, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.relationship and gears.relationships.RT_LANCEMATE in candidate.relationship.tags and candidate.combatant

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def t_PCMOVE(self, camp: gears.GearHeadCampaign):
        super().t_PCMOVE(camp)
        if self.combat_started and self.convo_ready:
            ghcutscene.SimpleMonologueDisplay(
                "[HELP_ME_VS_MECHA_COMBAT] This [town] is under attack.",
                self.elements["NPC"].get_root()
            )(camp)

            self.convo_ready = False

    def t_COMBATROUND(self, camp):
        super().t_COMBATROUND(camp)

        if self.combat_started and self.round_counter >= self.round_target:
            ally = self.elements["NPC"].get_root()
            if ally.is_operational():
                self.npc_obj.win(camp, 100 - ally.get_percent_damage_over_health())
                ghcutscene.SimpleMonologueDisplay(
                    "[THANKS_FOR_MECHA_COMBAT_HELP] I'll be at {NPC_SCENE} later if you need me.".format(**self.elements),
                    ally
                )(camp)
            else:
                self.elements["NPC"].relationship.reaction_mod -= 20
