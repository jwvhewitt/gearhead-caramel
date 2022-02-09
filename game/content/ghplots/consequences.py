from pbge.plots import Plot, PlotState, Rumor, TimeExpiration
import game
import gears
import pbge
import pygame
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints,plotutility,ghcutscene, ghchallenges
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed, GHNarrativeRequest
from . import missionbuilder, rwme_objectives, campfeatures


class MilitaryOccupation(Plot):
    # Elements:
    #   METROSCENE, METRO
    #   OCCUPYING_FACTION = The faction that has taken over this city.
    LABEL = "CONSEQUENCE_MILOCCUPATION"
    active = True
    scope = "METRO"

    QOL = gears.QualityOfLife(
        0, -2, 0, -2, -1
    )

    def custom_init(self, nart):
        # Step One: Check to make sure the city isn't already occupied.
        mycity: gears.GearHeadScene = self.elements.get("METROSCENE")
        camp: gears.GearHeadCampaign = nart.camp
        original_faction = mycity.faction
        occupying_faction = self.elements["OCCUPYING_FACTION"]
        if mycity and mycity.faction is not occupying_faction:
            # Go through the city and place all allies of the original faction in exile, replacing them with
            # occupying forces when possible.
            num_new_npcs = 0
            for thing in camp.all_contents(mycity):
                if hasattr(thing, "faction"):
                    if isinstance(thing, gears.base.Character) and camp.are_faction_enemies(thing, occupying_faction):
                        myscene = thing.scene
                        camp.freeze(thing)
                        num_new_npcs += 1
                        self.register_element("SCENE{}".format(num_new_npcs), myscene)
                        new_npc = self.register_element(
                            "NPC{}".format(num_new_npcs),
                            gears.selector.random_character(
                                self.rank, current_year=camp.year, faction=occupying_faction,
                                combatant=thing.combatant
                            ), dident="SCENE{}".format(num_new_npcs)
                        )
                    elif isinstance(thing, gears.GearHeadScene) and thing.faction is original_faction:
                        thing.faction = occupying_faction

            return True

    def get_dialogue_grammar(self, npc: gears.base.Character, camp: gears.GearHeadCampaign):
        mygram = dict()

        if npc.faction is self.elements["OCCUPYING_FACTION"]:
            mygram["[CURRENT_EVENTS]"] = [
                "{METROSCENE} is now safely under the protection of {OCCUPYING_FACTION}.".format(**self.elements),
            ]
        else:
            mygram["[CURRENT_EVENTS]"] = [
                "{METROSCENE} has been taken over by {OCCUPYING_FACTION}.".format(**self.elements),
            ]

        return mygram

    def t_UPDATE(self, camp):
        # This plot ends if the metroscene faction changes.
        if self.elements["METROSCENE"].faction is not self.elements["OCCUPYING_FACTION"]:
            self.end_plot(camp, True)

