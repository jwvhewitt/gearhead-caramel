import random
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges
from game import teams, ghdialogue
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor
from . import missionbuilder, rwme_objectives
from pbge.challenges import Challenge, AutoOffer


#  ****************************
#  ***   CHALLENGE  TOOLS   ***
#  ****************************
#
#   These constants describe various tools the challenge-offering faction might be willing to use to get the job
#   done. A challenge designer might invoke more than one challenge to allow for different ways of solving the problem.
#   When a designed challenge is won, it will emit a "WIN" trigger and also emit the tool involved in the challenge
#   as a trigger.

# We are passed a situation, some details about it, and a list of possible outcomes. These plots will then construct
# a set of challenges that fulfil the requirements.

class SuppressRebellion(Plot):
    LABEL = "CD_SUPPRESS_REBELLION"
    scope = "METRO"
    active = False

    # There's a rebellion going on, and the members of CHALLENGE_FAC wish it wasn't.
    #
    # Elements
    #   CHALLENGE_FAC       The faction doing the suppression
    #   REBEL_FAC           The faction doing the rebelling
    #   CHALLENGE_TOOLS     List of tools the CHALLENGE_FAC is willing to use against the rebellion

    def custom_init(self, nart):
        return True
