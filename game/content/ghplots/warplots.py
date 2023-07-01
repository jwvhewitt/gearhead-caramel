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
# METRO, METROSCENE, WORLD_MAP_WAR
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

WMWO_DEFENDER = "WMWO_DEFENDER"  # The faction will attempt to defend this location.
# Plots may involve shoring up defenses, evacuating civilians, and repairing damage done during the attack.
# This plot type will usually be associated with the original owner of a given territory, but not necessarily.

class OccupationFortify(Plot):
    LABEL = WMWO_DEFENDER
    scope = "METRO"
    active = True

    def custom_init(self, nart):
        # The invading faction is going to fortify their position.
        candidates = self.elements.get(RIVAL_FACTIONS)
        if candidates:
            rival = random.choice(candidates)
        else:
            rival = None

        oc1 = quests.QuestOutcome(
            ghquests.VERB_FORTIFY, target=rival,
            involvement=ghchallenges.InvolvedMetroFactionNPCs(self.elements["METROSCENE"], self.elements["OCCUPIER"]),
            effect=self._occupier_wins, loss_effect=self._occupier_loses,
            lore=[
                quests.QuestLore(
                    ghquests.LORECAT_OUTCOME, texts={
                        quests.TEXT_LORE_HINT: "{OCCUPIER} must bring order to {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_INFO: "{RESISTANCE_FACTION} are dissidents who resist {OCCUPIER} and must be crushed".format(**self.elements),
                        quests.TEXT_LORE_TOPIC: "the state of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_SELFDISCOVERY: "You learned that {RESISTANCE_FACTION} is working against {OCCUPIER} in {METROSCENE}.".format(**self.elements),
                        quests.TEXT_LORE_TARGET_TOPIC: "{RESISTANCE_FACTION}'s rebellion".format(**self.elements),
                    }, involvement = ghchallenges.InvolvedMetroFactionNPCs(
                        self.elements["METROSCENE"], self.elements["OCCUPIER"]
                    ), priority=True
                )
            ]
        )

        oc2 = quests.QuestOutcome(
            ghquests.VERB_EXPEL, target=self.elements[OCCUPIER],
            involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"],
                                                                        self.elements["OCCUPIER"]),
            effect=self._occupier_loses, loss_effect=self._occupier_wins, lore=[
                quests.QuestLore(
                    ghquests.LORECAT_OUTCOME, texts={
                        quests.TEXT_LORE_HINT: "life under {OCCUPIER} has been unbearable".format(**self.elements),
                        quests.TEXT_LORE_INFO: "a resistance has formed to get rid of {OCCUPIER}".format(**self.elements),
                        quests.TEXT_LORE_TOPIC: "{OCCUPIER}'s occupation of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_SELFDISCOVERY: "You learned that there is a resistance dedicated to ousting {OCCUPIER} from {METROSCENE}.".format(**self.elements),
                        quests.TEXT_LORE_TARGET_TOPIC: "{OCCUPIER}'s occupation of {METROSCENE}".format(**self.elements),
                    }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(
                        self.elements["METROSCENE"], self.elements["OCCUPIER"]
                    ), priority=True
                )
            ]
        )

        myquest = self.register_element(quests.QUEST_ELEMENT_ID, quests.Quest(
            outcomes=(oc1, oc2), end_on_loss=True
        ))
        myquest.build(nart, self)

        return True

    def _occupier_wins(self, camp: gears.GearHeadCampaign):
        pbge.alert("The occupier wins!")

    def _occupier_loses(self, camp: gears.GearHeadCampaign):
        pbge.alert("The resistance wins!")


WMWO_IRON_FIST = "WMWO_IRON_FIST"  # The faction will impose totalitarian rule on this location.
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
            involvement=ghchallenges.InvolvedMetroFactionNPCs(self.elements["METROSCENE"], self.elements["OCCUPIER"]),
            effect=self._occupier_wins, loss_effect=self._resistance_wins,
            lore=[
                quests.QuestLore(
                    ghquests.LORECAT_OUTCOME, texts={
                        quests.TEXT_LORE_HINT: "{OCCUPIER} must bring order to {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_INFO: "{RESISTANCE_FACTION} are dissidents who resist {OCCUPIER} and must be crushed".format(**self.elements),
                        quests.TEXT_LORE_TOPIC: "the state of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_SELFDISCOVERY: "You learned that {RESISTANCE_FACTION} is working against {OCCUPIER} in {METROSCENE}.".format(**self.elements),
                        quests.TEXT_LORE_TARGET_TOPIC: "{RESISTANCE_FACTION}'s rebellion".format(**self.elements),
                    }, involvement = ghchallenges.InvolvedMetroFactionNPCs(
                        self.elements["METROSCENE"], self.elements["OCCUPIER"]
                    ), priority=True
                )
            ]
        )

        oc2 = quests.QuestOutcome(
            ghquests.VERB_EXPEL, target=self.elements[OCCUPIER],
            involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"],
                                                                        self.elements["OCCUPIER"]),
            effect=self._resistance_wins, loss_effect=self._occupier_wins, lore=[
                quests.QuestLore(
                    ghquests.LORECAT_OUTCOME, texts={
                        quests.TEXT_LORE_HINT: "life under {OCCUPIER} has been unbearable".format(**self.elements),
                        quests.TEXT_LORE_INFO: "a resistance has formed to get rid of {OCCUPIER}".format(**self.elements),
                        quests.TEXT_LORE_TOPIC: "{OCCUPIER}'s occupation of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_SELFDISCOVERY: "You learned that there is a resistance dedicated to ousting {OCCUPIER} from {METROSCENE}.".format(**self.elements),
                        quests.TEXT_LORE_TARGET_TOPIC: "{OCCUPIER}'s occupation of {METROSCENE}".format(**self.elements),
                    }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(
                        self.elements["METROSCENE"], self.elements["OCCUPIER"]
                    ), priority=True
                )
            ]
        )

        myquest = self.register_element(quests.QUEST_ELEMENT_ID, quests.Quest(
            outcomes=(oc1, oc2), end_on_loss=True
        ))
        myquest.build(nart, self)

        return True

    def _occupier_wins(self, camp: gears.GearHeadCampaign):
        pbge.alert("The occupier wins!")

    def _resistance_wins(self, camp: gears.GearHeadCampaign):
        pbge.alert("The resistance wins!")


WMWO_MARTIAL_LAW = "WMWO_MARTIAL_LAW"  # The faction will attempt to impose law and order on the territory.
# Plots may involve capturing fugitives, enforcing curfew, and dispersing riots. This plot will usually be associated
# with either an invading force or a totalitarian force reasserting control over areas lost to rebellion or outside
# influence.