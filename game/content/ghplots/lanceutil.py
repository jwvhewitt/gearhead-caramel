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


#  *********************************
#  ***   LANCE_VIRTUE_REACTION   ***
#  *********************************
#
# Needed Elements: METROSCENE, METRO, UPHELD_VIRTUES, VIOLATED_VIRTUES
#      ACTING: Gerund phrase describing what is being reacted to
#      ACTED: Past tense clause describing what happened
#
# Lancemates who share the UPHELD_VIRTUES get reaction bonus, speak their mind
# Lancemates who hold the VIOLATED_VIRTUES lose reaction bonus, speak their mind
#

class BasicVirtueReaction(Plot):
    LABEL = "LANCE_VIRTUE_REACTION"
    active = True
    scope = "METRO"

    def METRO_ENTER(self, camp: gears.GearHeadCampaign):
        upheld_virtues = set(self.elements.get("UPHELD_VIRTUES", set()))
        violated_virtues = set(self.elements.get("VIOLATED_VIRTUES", set()))
        conflicted_lancemates = list()
        upset_lancemates = list()
        happy_lancemates = list()
        for npc in camp.get_lancemates():
            if npc.personality.intersection(upheld_virtues) and npc.personality.intersection(violated_virtues):
                conflicted_lancemates.append(npc)
            elif npc.personality.intersection(upheld_virtues):
                happy_lancemates.append(npc)
            elif npc.personality.intersection(violated_virtues):
                upset_lancemates.append(npc)
        pc_is_hypocrite = camp.pc.personality.intersection(violated_virtues)
        if conflicted_lancemates or upset_lancemates or happy_lancemates or pc_is_hypocrite:
            my_cutscene = pbge.cutscene.CutscenePlan(
                "city_intro", {"METROSCENE": camp.scene}, start_beats=("first_impression", "typhon_attack"),
                mid_beats=[],
                final_beats=("mission_reminder",)
            )

        self.end_plot(camp, True)

