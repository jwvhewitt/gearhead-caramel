import random

import game.content
import gears
import pbge
from game.content import gharchitecture
from game.content.ghplots import missionbuilder
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot
from . import dd_customobjectives


#   ******************************
#   ***  DZRE_MECHA_GRAVEYARD  ***
#   ******************************

class MechaGraveyardAdventure(Plot):
    LABEL = "DZRE_MECHA_GRAVEYARD"
    active = True
    scope = "METRO"

    def custom_init(self, nart):


        return True

