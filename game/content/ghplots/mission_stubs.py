from pbge.plots import Plot, PlotState
from game.content import ghwaypoints,ghterrain,plotutility,backstory
import gears
import pbge
from game import teams,ghdialogue
from game.ghdialogue import context
import random
from pbge.dialogue import ContextTag,Offer
from . import dd_main,dd_customobjectives
from . import tarot_cards
from .tarot_cards import ME_FACTION,ME_PERSON,ME_CRIME,ME_PUZZLEITEM,ME_ACTOR,ME_LIABILITY,CrimeObject,ME_POSITION, ME_PROBLEM, ME_BOOSTSOURCE
from game.content import mechtarot
from game.content.mechtarot import CONSEQUENCE_WIN,CONSEQUENCE_LOSE
import game.content.plotutility
import game.content.gharchitecture
from . import dd_combatmission
import collections
from . import missionbuilder


#   ********************************
#   ***  MSTUB_RECOVER_BUILDING  ***
#   ********************************
#
#  METRO
#  METROSCENE
#  MISSION_GATE
#  NPC: The mission giver
#  BUILDING_NAME: The nature of the building
#  ENEMY_FACTION: The enemies who captured the building

class RecoverMyBuilding(Plot):
    LABEL = "MSTUB_RECOVER_BUILDING"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        self.mission_seed = None
        return True

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

    def t_UPDATE(self, camp):
        # If the adventure has ended, get rid of it.
        if self.mission_seed and self.mission_seed.ended:
            self.mission_seed = None

    def NPC_offers(self, camp):
        mylist = list()
        if not self.mission_seed:
            mylist.append(Offer(
                "I have a {BUILDING_NAME} that's been taken over by bandits; I could use your help to clear them out.".format(**self.elements),
                context=ContextTag([context.MISSION, ]), subject=self, subject_start=True,
            ))
            mylist.append(Offer(
                "[IWillSendMissionDetails]. [GOODLUCK]",
                context=ContextTag([context.ACCEPT, ]), effect=self.register_adventure, subject=self,
            ))
            mylist.append(Offer(
                "[GOODBYE]",
                context=ContextTag([context.DENY, ]), subject=self,
            ))
        return mylist

    def register_adventure(self, camp):
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, "{}'s Mission".format(self.elements["NPC"]),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            self.elements.get("ENEMY_FACTION"), rank=self.rank,
            objectives=(missionbuilder.BAMO_CAPTURE_BUILDINGS,missionbuilder.BAMO_LOCATE_ENEMY_FORCES),
            on_win=self._win_mission,
        )
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def _win_mission(self, camp):
        camp.check_trigger("WIN", self)
        self.end_plot(camp, True)
