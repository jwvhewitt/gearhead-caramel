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
# RIVAL_FACTIONS: A list of other factions that also want this metro area. May be falsy.
# ORIGINAL_FACTION: The faction that originally controlled this area. May be "None".
# RESISTANCE_FACTION: A faction that may attempt to oust the occupier. May be the same as ORIGINAL_FACTION. Optional.
OCCUPIER = "OCCUPIER"
RIVAL_FACTIONS = "RIVAL_FACTIONS"
ORIGINAL_FACTION = "ORIGINAL_FACTION"
RESISTANCE_FACTION = "RESISTANCE_FACTION"


class OccupationPlot(Plot):
    # Subclassing an Occupation Plot. The only change from regular plots is a property confirming that this is an
    # OccupationPlot. Why? Because only one OccupationPlot can be active in a city at once; if there are any more,
    # they get deleted.
    IS_OCCUPATION_PLOT = True

# During a world map war, different factions may have different effects on the territories they conquer. This may give
# special opportunities to the player character, depending on which side of the conflict the PC is working for (if any).

TEST_WAR_PLOT = "TEST_WAR_PLOT"

WMWO_DEFENDER = "WMWO_DEFENDER"  # The faction will attempt to defend this location.
# Plots may involve shoring up defenses, evacuating civilians, and repairing damage done during the attack.
# This plot type will usually be associated with the original owner of a given territory, but not necessarily.

class OccupationFortify(Plot):
    LABEL = WMWO_DEFENDER
    scope = "METRO"
    active = True

    IS_OCCUPATION_PLOT = True

    def custom_init(self, nart):
        # The invading faction is going to fortify their position.
        self.expiration = plotutility.RulingFactionExpiration(self.elements["METROSCENE"], self.elements[OCCUPIER])
        if RESISTANCE_FACTION not in self.elements:
            candidates = self.elements.get(RIVAL_FACTIONS)
            if candidates:
                rival = random.choice(candidates)
            else:
                rival = gears.factions.Circle(
                    nart.camp, parent_faction=self.elements.get(ORIGINAL_FACTION)
                )
            self.elements[RESISTANCE_FACTION] = rival

        oc1 = quests.QuestOutcome(
            ghquests.FortifyVerb, ghquests.default_player_can_do_outcome,
            win_effect=self._occupier_wins, loss_effect=self._occupier_loses,
            lore=[
                quests.QuestLore(
                    ghquests.LORECAT_OUTCOME, texts={
                        quests.TEXT_LORE_HINT: "{OCCUPIER} plans to hold onto {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_INFO: "{OCCUPIER} is working to improve {METROSCENE}'s defenses".format(**self.elements),
                        quests.TEXT_LORE_TOPIC: "the state of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_SELFDISCOVERY: "You learned that {OCCUPIER} is working to consolidate its position in {METROSCENE}.".format(**self.elements),
                        quests.TEXT_LORE_TARGET_TOPIC: "{OCCUPIER}'s plans".format(**self.elements),
                        quests.TEXT_LORE_MEMO: "{OCCUPIER} is fortifying their position in {METROSCENE}.".format(**self.elements),
                    }, involvement=ghchallenges.InvolvedMetroNoEnemyToFactionNPCs(
                        self.elements["METROSCENE"], self.elements["OCCUPIER"]
                    ), priority=True
                ),
            ], prioritize_lore=True,
            o_elements={
                ghquests.OE_ALLYFACTION: self.elements[OCCUPIER],
                ghquests.OE_ENEMYFACTION: self.elements[RESISTANCE_FACTION],
                ghquests.OE_OBJECT: self.elements["METROSCENE"],
            }
        )

        oc2 = quests.QuestOutcome(
            ghquests.ExpelVerb, ghquests.default_player_can_do_outcome,
            win_effect=self._occupier_loses, loss_effect=self._occupier_wins, lore=[
                quests.QuestLore(
                    ghquests.LORECAT_OUTCOME, texts={
                        quests.TEXT_LORE_HINT: "{OCCUPIER} is not entirely welcome here".format(**self.elements),
                        quests.TEXT_LORE_INFO: "{RESISTANCE_FACTION} seek to force {OCCUPIER} out of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_TOPIC: "{OCCUPIER}'s occupation of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_SELFDISCOVERY: "You learned that {RESISTANCE_FACTION} plans to drive {OCCUPIER} from {METROSCENE}.".format(**self.elements),
                        quests.TEXT_LORE_TARGET_TOPIC: "{OCCUPIER}'s occupation of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_MEMO: "{RESISTANCE_FACTION} opposes {OCCUPIER}'s occupation of {METROSCENE}.".format(**self.elements),
                    }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(
                        self.elements["METROSCENE"], self.elements["OCCUPIER"]
                    ), priority=True
                )
            ], prioritize_lore=False,
            o_elements={
                ghquests.OE_ALLYFACTION: self.elements[RESISTANCE_FACTION],
                ghquests.OE_ENEMYFACTION: self.elements[OCCUPIER]
            }
        )

        myquest = self.register_element(quests.QUEST_ELEMENT_ID, quests.Quest(
            "{OCCUPIER} is attempting to fortify its position in {METROSCENE}.".format(**self.elements),
            outcomes=(oc1, oc2), end_on_loss=True
        ))
        myquest.build(nart, self)

        self.add_sub_plot(nart, "ENSURE_LOCAL_OPERATIVES", elements={"FACTION": self.elements["OCCUPIER"]})

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

    IS_OCCUPATION_PLOT = True

    def custom_init(self, nart):
        # The invading faction is going to try and crush dissent in this region. The locals are going to try to resist
        # this as well as they can.
        self.expiration = plotutility.RulingFactionExpiration(self.elements["METROSCENE"], self.elements["OCCUPIER"])
        if RESISTANCE_FACTION not in self.elements:
            self.elements[RESISTANCE_FACTION] = gears.factions.Circle(
                nart.camp, parent_faction=self.elements.get(ORIGINAL_FACTION)
            )

        oc1 = quests.QuestOutcome(
            ghquests.RepressVerb, ghquests.default_player_can_do_outcome,
            win_effect=self._occupier_wins, loss_effect=self._resistance_wins,
            lore=[
                quests.QuestLore(
                    ghquests.LORECAT_OUTCOME, texts={
                        quests.TEXT_LORE_HINT: "{OCCUPIER} will bring {METROSCENE} under our complete control".format(**self.elements),
                        quests.TEXT_LORE_INFO: "{RESISTANCE_FACTION} are dissidents who resist {OCCUPIER} and must be crushed".format(**self.elements),
                        quests.TEXT_LORE_TOPIC: "the state of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_SELFDISCOVERY: "You learned that {RESISTANCE_FACTION} is working against {OCCUPIER} in {METROSCENE}.".format(**self.elements),
                        quests.TEXT_LORE_TARGET_TOPIC: "{RESISTANCE_FACTION}'s rebellion".format(**self.elements),
                        quests.TEXT_LORE_MEMO: "{OCCUPIER} is attempting to crush all dissent in {METROSCENE}.".format(**self.elements),
                    }, involvement = ghchallenges.InvolvedMetroFactionNPCs(
                        self.elements["METROSCENE"], self.elements["OCCUPIER"]
                    ), priority=True
                ),
                quests.QuestLore(
                    ghquests.LORECAT_MOTIVE, texts={
                        quests.TEXT_LORE_HINT: "{RESISTANCE_FACTION} is plotting a rebellion".format(
                            **self.elements),
                        quests.TEXT_LORE_INFO: "{OCCUPIER}'s control of {METROSCENE} will never be complete as long as {RESISTANCE_FACTION} exists".format(
                            **self.elements),
                        quests.TEXT_LORE_TOPIC: "the {RESISTANCE_FACTION} resistance".format(**self.elements),
                        quests.TEXT_LORE_SELFDISCOVERY: "You learned that {RESISTANCE_FACTION} has been trying to drive {OCCUPIER} from {METROSCENE}.".format(
                            **self.elements),
                        quests.TEXT_LORE_TARGET_TOPIC: "{OCCUPIER}'s control of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_MEMO: "{RESISTANCE_FACTION} is attempting to drive {OCCUPIER} out of {METROSCENE}.".format(
                            **self.elements),
                        ghquests.L_MOTIVE_CONFESSION: "{RESISTANCE_FACTION} will free {METROSCENE} from {OCCUPIER}".format(
                            **self.elements),
                    }, involvement=ghchallenges.InvolvedMetroFactionNPCs(
                        self.elements["METROSCENE"], self.elements["OCCUPIER"]
                    ),
                    tags=(ghquests.LORETAG_ENEMY, ghquests.LORETAG_PRIMARY),
                )
            ], prioritize_lore=True,
            o_elements={
                ghquests.OE_ALLYFACTION: self.elements[OCCUPIER],
                ghquests.OE_ENEMYFACTION: self.elements[RESISTANCE_FACTION]
            }
        )

        oc2 = quests.QuestOutcome(
            ghquests.ExpelVerb, ghquests.default_player_can_do_outcome,
            win_effect=self._resistance_wins, loss_effect=self._occupier_wins, lore=[
                quests.QuestLore(
                    ghquests.LORECAT_OUTCOME, texts={
                        quests.TEXT_LORE_HINT: "life under {OCCUPIER} has been unbearable".format(**self.elements),
                        quests.TEXT_LORE_INFO: "a resistance has formed to get rid of {OCCUPIER}".format(**self.elements),
                        quests.TEXT_LORE_TOPIC: "{OCCUPIER}'s occupation of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_SELFDISCOVERY: "You learned that the people of {METROSCENE} must unite to oust {OCCUPIER}.".format(**self.elements),
                        quests.TEXT_LORE_TARGET_TOPIC: "{OCCUPIER}'s occupation of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_MEMO: "There is a resistance opposing {OCCUPIER}'s occupation of {METROSCENE}.".format(**self.elements),
                    }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(
                        self.elements["METROSCENE"], self.elements["OCCUPIER"]
                    ), priority=True
                ),
                quests.QuestLore(
                    ghquests.LORECAT_MOTIVE, texts={
                        quests.TEXT_LORE_HINT: "{RESISTANCE_FACTION} is our only hope to stop {OCCUPIER}".format(**self.elements),
                        quests.TEXT_LORE_INFO: "no-one is safe as long as {OCCUPIER} occupies {METROSCENE}; {RESISTANCE_FACTION} is leading the resistance".format(
                            **self.elements),
                        quests.TEXT_LORE_TOPIC: "the {OCCUPIER} occupation".format(**self.elements),
                        quests.TEXT_LORE_SELFDISCOVERY: "You learned that {OCCUPIER} has been eliminating all resistance in {METROSCENE}.".format(
                            **self.elements),
                        quests.TEXT_LORE_TARGET_TOPIC: "{RESISTANCE_FACTION}'s rebellion".format(**self.elements),
                        quests.TEXT_LORE_MEMO: "{OCCUPIER} is attempting to crush all resistance to their occupation of {METROSCENE}.".format(
                            **self.elements),
                        ghquests.L_MOTIVE_CONFESSION: "{OCCUPIER} will destroy any who defy our rulership of {METROSCENE}".format(
                            **self.elements),
                    }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(
                        self.elements["METROSCENE"], self.elements["OCCUPIER"]
                    ),
                    tags=(ghquests.LORETAG_ENEMY, ghquests.LORETAG_PRIMARY),
                )

            ], prioritize_lore=False,
            o_elements={
                ghquests.OE_ALLYFACTION: self.elements[RESISTANCE_FACTION],
                ghquests.OE_ENEMYFACTION: self.elements[OCCUPIER]
            }
        )

        myquest = self.register_element(quests.QUEST_ELEMENT_ID, quests.Quest(
            "{OCCUPIER} is attempting to crush all dissent in {METROSCENE}.".format(**self.elements),
            outcomes=(oc1, oc2), end_on_loss=True
        ))
        myquest.build(nart, self)

        self.add_sub_plot(nart, "ENSURE_LOCAL_OPERATIVES", elements={"FACTION": self.elements["OCCUPIER"]})

        return True

    def _occupier_wins(self, camp: gears.GearHeadCampaign):
        pbge.alert("The occupier wins!")

    def _resistance_wins(self, camp: gears.GearHeadCampaign):
        pbge.alert("The resistance wins!")


WMWO_MARTIAL_LAW = "WMWO_MARTIAL_LAW"  # The faction will attempt to impose law and order on the territory.
# Plots may involve capturing fugitives, enforcing curfew, and dispersing riots. This plot will usually be associated
# with either an invading force or a totalitarian force reasserting control over areas lost to rebellion or outside
# influence.


class OccupationRestoreOrder(Plot):
    LABEL = WMWO_MARTIAL_LAW
    scope = "METRO"
    active = True

    IS_OCCUPATION_PLOT = True

    def custom_init(self, nart):
        # The invading faction is going to fortify their position.
        self.expiration = plotutility.RulingFactionExpiration(self.elements["METROSCENE"], self.elements["OCCUPIER"])
        if RESISTANCE_FACTION not in self.elements:
            candidates = self.elements.get(RIVAL_FACTIONS)
            if candidates:
                rival = random.choice(candidates)
            else:
                rival = gears.factions.Circle(
                    nart.camp, parent_faction=self.elements.get(ORIGINAL_FACTION)
                )
            self.elements[RESISTANCE_FACTION] = rival

        oc1 = quests.QuestOutcome(
            ghquests.FortifyVerb, ghquests.default_player_can_do_outcome,
            win_effect=self._occupier_wins, loss_effect=self._occupier_loses,
            lore=[
                quests.QuestLore(
                    ghquests.LORECAT_OUTCOME, texts={
                        quests.TEXT_LORE_HINT: "{OCCUPIER} must bring order to {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_INFO: "{RESISTANCE_FACTION} are dissidents who resist {OCCUPIER} and must be crushed".format(**self.elements),
                        quests.TEXT_LORE_TOPIC: "the state of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_SELFDISCOVERY: "You learned that {RESISTANCE_FACTION} is working against {OCCUPIER} in {METROSCENE}.".format(**self.elements),
                        quests.TEXT_LORE_TARGET_TOPIC: "{RESISTANCE_FACTION}'s rebellion".format(**self.elements),
                        quests.TEXT_LORE_MEMO: "{OCCUPIER} has placed {METROSCENE} under martial law.".format(**self.elements),
                    }, involvement = ghchallenges.InvolvedMetroFactionNPCs(
                        self.elements["METROSCENE"], self.elements["OCCUPIER"]
                    ), priority=True
                )
            ], prioritize_lore=True,
            o_elements={
                ghquests.OE_ALLYFACTION: self.elements[OCCUPIER],
                ghquests.OE_ENEMYFACTION: self.elements[RESISTANCE_FACTION],
            }
        )

        oc2 = quests.QuestOutcome(
            ghquests.ExpelVerb, ghquests.default_player_can_do_outcome,
            win_effect=self._occupier_loses, loss_effect=self._occupier_wins, lore=[
                quests.QuestLore(
                    ghquests.LORECAT_OUTCOME, texts={
                        quests.TEXT_LORE_HINT: "life under {OCCUPIER} has been unbearable".format(**self.elements),
                        quests.TEXT_LORE_INFO: "a resistance has formed to get rid of {OCCUPIER}".format(**self.elements),
                        quests.TEXT_LORE_TOPIC: "{OCCUPIER}'s occupation of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_SELFDISCOVERY: "You learned that there is a resistance dedicated to ousting {OCCUPIER} from {METROSCENE}.".format(**self.elements),
                        quests.TEXT_LORE_TARGET_TOPIC: "{OCCUPIER}'s occupation of {METROSCENE}".format(**self.elements),
                        quests.TEXT_LORE_MEMO: "There is a resistance opposing {OCCUPIER}'s occupation of {METROSCENE}.".format(**self.elements),
                    }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(
                        self.elements["METROSCENE"], self.elements["OCCUPIER"]
                    ), priority=True
                )
            ], prioritize_lore=False,
            o_elements={
                ghquests.OE_ALLYFACTION: self.elements[RESISTANCE_FACTION],
                ghquests.OE_ENEMYFACTION: self.elements[OCCUPIER],
            }
        )

        myquest = self.register_element(quests.QUEST_ELEMENT_ID, quests.Quest(
            "{OCCUPIER} has imposed martial law in {METROSCENE}.".format(**self.elements),
            outcomes=(oc1, oc2), end_on_loss=True
        ))
        myquest.build(nart, self)

        self.add_sub_plot(nart, "ENSURE_LOCAL_OPERATIVES", elements={"FACTION": self.elements["OCCUPIER"]})

        return True

    def _occupier_wins(self, camp: gears.GearHeadCampaign):
        pbge.alert("The occupier wins!")

    def _occupier_loses(self, camp: gears.GearHeadCampaign):
        pbge.alert("The resistance wins!")
