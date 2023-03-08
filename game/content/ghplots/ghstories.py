import random
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges
from game import teams, ghdialogue
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor
from pbge import stories, quests
from . import missionbuilder, rwme_objectives
from pbge.challenges import Challenge, AutoOffer


#  ***********************
#  ***   PROPP  KEYS   ***
#  ***********************

ENEMY_KEY = stories.ProppKey(
    # The player has committed to defeating a certain character or faction.
    # Params: The StoryElementID of the enemy.
    name="ENEMY",
    narratemes=(
        "None", "Mystery", "Identified", "Located"
    ),
    max_starting_state=1
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
    )
)


