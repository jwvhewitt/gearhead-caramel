import random
from game import content, services, teams, ghdialogue
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges, ghrooms
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor, PlotState
from pbge import stories, quests
from pbge.memos import Memo
from . import missionbuilder, rwme_objectives, campfeatures, ghquests
from pbge.challenges import Challenge, AutoOffer
from .shops_plus import get_building
import collections

#  *****************************
#  ***   OCCUPATION  PLOTS   ***
#  *****************************

# Required Elements:
# METRO, METROSCENE
# OCCUPIER: The faction that has occupied this metro area.
# RIVAL_FACTIONS: A list of other factions that also want this metro area. Optional.
# ORIGINAL_FACTION: The faction that originally controlled this area. Optional.
# RESISTANCE_FACTION: A faction that may attempt to oust the occupier. May be the same as ORIGINAL_FACTION. Optional.
OCCUPIER = "OCCUPIER"
RIVAL_FACTIONS = "RIVAL_FACTIONS"
ORIGINAL_FACTION = "ORIGINAL_FACTION"
RESISTANCE_FACTION = "RESISTANCE_FACTION"

# During a world map war, different factions may have different effects on the territories they conquer. This may give
# special opportunities to the player character, depending on which side of the conflict the PC is working for (if any).

WMWO_DEFENDER = "WMWO_DEFENDER"         # The faction will attempt to defend this location.
# Plots may involve shoring up defenses, evacuating civilians, and repairing damage done during the attack.
# This plot type will usually be associated with the original owner of a given territory, but not necessarily.

WMWO_IRON_FIST = "WMWO_IRON_FIST"       # The faction will impose totalitarian rule on this location.
# Plots may involve forced labor, rounding up dissidents, and propaganda campaigns. This plot type will usually be
# associated with an invading dictatorship, but not necessarily.


class OccupationCrushDissent(Plot):
    LABEL = WMWO_IRON_FIST
    scope = "METRO"
    active = True

    def custom_init(self, nart):
        # The invading faction is going to try and crush dissent in this region. The locals are going to try to resist
        # this as well as they can.
        self.expiration = plotutility.RulingFactionExpiration(self.elements["METROSCENE"], self.elements["OCCUPIER"])
        if RESISTANCE_FACTION not in self.elements:
            self.elements[RESISTANCE_FACTION] = gears.factions.Circle(
                nart.camp, parent_faction=self.elements.get(ORIGINAL_FACTION)
            )

        oc1 = quests.QuestOutcome(
            ghquests.VERB_REPRESS, target=self.elements[RESISTANCE_FACTION],
            participants=ghchallenges.InvolvedMetroFactionNPCs(self.elements["METROSCENE"], self.elements["OCCUPIER"]),
            effect=self._occupier_wins
        )

        oc2 = quests.QuestOutcome(
            ghquests.VERB_EXPEL, target=self.elements[OCCUPIER],
            participants=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"],
                                                                         self.elements["OCCUPIER"]),
            effect=self._resistance_wins
        )

        myquest = self.register_element(quests.DEFAULT_QUEST_ELEMENT_ID, quests.Quest(
            outcomes=(oc1, oc2)
        ))
        myquest.build(nart, self)

        return True

    def _occupier_wins(self, camp: gears.GearHeadCampaign):
        pass

    def _resistance_wins(self, camp: gears.GearHeadCampaign):
        pass


WMWO_MARTIAL_LAW = "WMWO_MARTIAL_LAW"   # The faction will attempt to impose law and order on the territory.
# Plots may involve capturing fugitives, enforcing curfew, and dispersing riots. This plot will usually be associated
# with either an invading force or a totalitarian force reasserting control over areas lost to rebellion or outside
# influence.

