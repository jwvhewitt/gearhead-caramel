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
from . import missionbuilder, rwme_objectives, campfeatures
from pbge.challenges import Challenge, AutoOffer
from .shops_plus import get_building
import collections


# During a world map war, different factions may have different effects on the territories they conquer. This may give
# special opportunities to the player character, depending on which side of the conflict the PC is working for (if any).

WMWO_DEFENDER = "WMWO_DEFENDER"         # The faction will attempt to defend this location.
# Plots may involve shoring up defenses, evacuating civilians, and repairing damage done during the attack.
# This plot type will usually be associated with the original owner of a given territory, but not necessarily.

WMWO_IRON_FIST = "WMWO_IRON_FIST"       # The faction will impose totalitarian rule on this location.
# Plots may involve forced labor, rounding up dissidents, and propaganda campaigns. This plot type will usually be
# associated with an invading dictatorship, but not necessarily.

WMWO_MARTIAL_LAW = "WMWO_MARTIAL_LAW"   # The faction will attempt to impose law and order on the territory.
# Plots may involve capturing fugitives, enforcing curfew, and dispersing riots. This plot will usually be associated
# with either an invading force or a totalitarian force reasserting control over areas lost to rebellion or outside
# influence.

# If the faction that took over is