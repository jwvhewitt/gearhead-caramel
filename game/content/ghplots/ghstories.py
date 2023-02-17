import random
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges
from game import teams, ghdialogue
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor
from pbge import stories
from . import missionbuilder, rwme_objectives
from pbge.challenges import Challenge, AutoOffer


VERB_EXPEL = "EXPEL"        # Like DEFEAT, but the enemy is an outside power of some type
VERB_REPRESS = "REPRESS"    # Like DEFEAT, but the enemy has to be located first

#  ***********************
#  ***   PROPP  KEYS   ***
#  ***********************

ENEMY_KEY = stories.ProppKey(
    # The player has committed to defeating a certain character or faction.
    # Params: The StoryElementID of the enemy.
    name="ENEMY",
    narratemes= (
        "None", "Mystery", "Identified", "Located"
    ),
    takes_params=True
)

MYSTERY_KEY = stories.ProppKey(
    # There is a mystery to be solved.
    name="MYSTERY",
    narratemes=(
        "None", "MissingSupplies"
    )
)

PROBLEM_KEY = stories.ProppKey(
    # There is a local problem.
    name="PROBLEM",
    narratemes=(
        "None", "Malaise", "MilitaryConflict"
    )
)

TROUBLEMAKER_KEY = stories.ProppKey(
    # A faction or character is interfering with the current state of things.
    # Params: The StoryElementID of the enemy.
    name="TROUBLEMAKER",
    narratemes= (
        "None", "Criminal", "Dissidents"
    ),
    takes_params=True
)


#  ****************************
#  ***   STORY_CONCLUSION   ***
#  ****************************

class JustATest(stories.StoryConclusionPlot):
    LABEL = stories.DEFAULT_STORY_CONCLUSION
    scope = "METRO"
    active = True

    @classmethod
    def get_conclusion_context(cls, nart, outcome):
        if outcome.verb in (VERB_REPRESS, stories.VERB_DEFEAT):
            my_state = stories.ProppState(
                {
                    TROUBLEMAKER_KEY: stories.ProppValue(
                        "Located", (outcome.target,)
                    ),
                    MYSTERY_KEY: stories.ProppValue(
                        "MissingSupplies"
                    )
                }
            )
            return my_state

class StrikeTheLeader(stories.StoryConclusionPlot):
    LABEL = stories.DEFAULT_STORY_CONCLUSION
    scope = "METRO"
    active = True

    @classmethod
    def get_conclusion_context(cls, nart, outcome):
        if outcome.verb in (VERB_REPRESS, stories.VERB_DEFEAT):
            my_state = stories.ProppState(
                {
                    ENEMY_KEY: stories.ProppValue(
                        "Located", (outcome.target,)
                    ),
                    TROUBLEMAKER_KEY: stories.ProppValue(
                        "Dissidents", (outcome.target,)
                    )
                }
            )
            return my_state


class TheHiddenFortress(stories.StoryConclusionPlot):
    LABEL = stories.DEFAULT_STORY_CONCLUSION
    scope = "METRO"
    active = True

    @classmethod
    def get_conclusion_context(cls, nart, outcome):
        if outcome.verb in (VERB_EXPEL, stories.VERB_DEFEAT):
            my_state = stories.ProppState(
                {
                    ENEMY_KEY: stories.ProppValue(
                        "Located", (outcome.target,)
                    ),
                    PROBLEM_KEY: stories.ProppValue(
                        "MilitaryConflict"
                    )
                }
            )
            return my_state

