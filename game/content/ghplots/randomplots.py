# We have plots for every occassion- random events to spice up your metroscenes.

from pbge.plots import Plot, PlotState, Rumor, TimeExpiration
import game
import gears
import pbge
import pygame
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints,plotutility,ghcutscene
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed
from . import missionbuilder, rwme_objectives, campfeatures

class LoadChallengePlot(Plot):
    LABEL = "RANDOM_PLOT"
    active = False
    scope = None
    COMMON = True

    def custom_init(self, nart):
        self.add_sub_plot(nart, "CHALLENGE_PLOT")
        return True


class DaveHasAPlot(Plot):
    LABEL = "zRANDOM_PLOT"
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        "{NPC} at {NPC_SCENE} has a plot"
    )

    def custom_init( self, nart ):
        npc = self.seek_element(nart, "NPC", self.is_good_npc, scope=self.elements["METROSCENE"])
        self.elements["NPC_SCENE"] = npc.scene
        self.expiration = TimeExpiration(nart.camp, time_limit=5)
        return True

    def is_good_npc(self, nart, candidate):
        return (
            isinstance(candidate, gears.base.Character)
        )

    def METROSCENE_ENTER(self, camp: gears.GearHeadCampaign):
        pbge.alert("Days remaining: {}".format(self.expiration.time_limit - camp.day))

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "I've got a plot!", context=ContextTag([context.HELLO,]),
        ))
        return mylist
