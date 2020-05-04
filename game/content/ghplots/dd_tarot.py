from game.content import mechtarot
from game.content.mechtarot import TarotCard, Interaction, ME_TAROTPOSITION, \
    ME_AUTOREVEAL,CardTransformer, Consequence, CardCaller, CardDeactivator
import pbge
import gears
from game.ghdialogue import context
from pbge.dialogue import Offer
import random
import collections
from . import actionscenes
from . import missionbuilder

MT_CRIME = "CRIME"
MT_FACTION = "FACTION"
MT_HEROIC = "HEROIC"
MT_INCRIMINATING = "INCRIMINATING"
MT_PERSON = "PERSON"
MT_THREAT = "THREAT"
MT_HOUSE = "HOUSE"

ME_FACTION = "CARD_FACTION"
ME_PERSON = "CARD_PERSON"
ME_PUZZLEITEM = "CARD_PUZZLEITEM"
ME_CRIME = "CRIME_TEXT"
ME_CRIMED = "CRIME_VERBED_TEXT"


class HateClub(TarotCard):
    TAGS = (MT_HOUSE,MT_THREAT)
    QOL = gears.QualityOfLife(stability=-2,community=-2)

    # Init: This house requires a leader and a muscle.
    # Interactions:
    # Leader + Muscle.Incrimination ->
    # Muscle + Leader.Incrimination ->
    # Reactions:
    # Leader Destroyed -> Muscle goes renegade
    # Leader Shamed -> Muscle disbands
    # Muscle Destroyed -> Leader goes renegade

