from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
import pbge
from game.content import backstory, plotutility, ghterrain, ghwaypoints
import random
from gears import relationships

# The PC has invited someone on a date or someone has invited the PC on a date and this unit has plots to
# cover that. A date plot will usually involve relationship development.

class DateVenue(object):
    def __init__(self, scene, name):
        self.scene = scene
        self.name = name


#   ************************
#   ***   GO_ON_A_DATE   ***
#   ************************
#
#  NPC: The NPC to be dated. May be a lancemate.
#  METRO, METROSCENE: The city where the date will take place.
#  VENUE: The date venue; a bunch of information about where/when the date will be.


