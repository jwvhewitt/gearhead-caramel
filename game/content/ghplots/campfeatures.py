from pbge.plots import Plot, PlotState
import game.content.ghwaypoints
import game.content.ghterrain
import gears
import pbge
from game import teams,ghdialogue
from game.content import gharchitecture
from game.ghdialogue import context
import random
from pbge.dialogue import ContextTag,Offer
from game.content import plotutility, GHNarrativeRequest, PLOT_LIST
import game.content.gharchitecture
from . import missionbuilder
import collections
from game.content.plotutility import LMSkillsSelfIntro

from game import memobrowser
Memo = memobrowser.Memo

# This unit contains plots that handle standard features you may want to add to a campaign or a scene in that campaign.

class StandardLancemateHandler(Plot):
    LABEL = "CF_STANDARD_LANCEMATE_HANDLER"
    active = True
    scope = True

    def _get_generic_offers( self, npc, camp ):
        """

        :type camp: gears.GearHeadCampaign
        :type npc: gears.base.Character
        """
        mylist = list()
        if npc.relationship and gears.relationships.RT_LANCEMATE in npc.relationship.tags:
            if camp.can_add_lancemate() and npc not in camp.party:
                # If the NPC has the lancemate tag, they might join the party.
                if npc.relationship.data.get("DZD_LANCEMATE_TIME_OFF",0) <= camp.day:
                    mylist.append(Offer("[JOIN]", is_generic=True,
                                        context=ContextTag([context.JOIN]), effect=game.content.plotutility.AutoJoiner(npc)))
                else:
                    # This NPC is taking some time off. Come back tomorrow.
                    mylist.append(Offer("[COMEBACKTOMORROW_JOIN]", is_generic=True,
                                        context=ContextTag([context.JOIN])))
            elif npc in camp.party and gears.tags.SCENE_PUBLIC in camp.scene.attributes:
                mylist.append(Offer("[LEAVEPARTY]", is_generic=True,
                                    context=ContextTag([context.LEAVEPARTY]), effect=game.content.plotutility.AutoLeaver(npc)))
            mylist.append(LMSkillsSelfIntro(npc))
        return mylist

class MetrosceneRecoveryHandler(Plot):
    LABEL = "CF_METROSCENE_RECOVERY_HANDLER"
    active = True
    scope = "METROSCENE"
    def METROSCENE_ENTER(self, camp):
        # Upon entering this scene, deal with any dead or incapacitated party members.
        # Also, deal with party members who have lost their mecha. This may include the PC.
        camp.home_base = self.elements["MISSION_GATE"]
        etlr = plotutility.EnterTownLanceRecovery(camp, self.elements["METROSCENE"], self.elements["METRO"])
        if not etlr.did_recovery:
            # We can maybe load a lancemate scene here. Yay!
            if not any(p for p in camp.all_plots() if hasattr(p, "LANCEDEV_PLOT") and p.LANCEDEV_PLOT):
                nart = GHNarrativeRequest(camp, pbge.plots.PlotState().based_on(self), adv_type="DZD_LANCEDEV", plot_list=PLOT_LIST)
                if nart.story:
                    nart.build()
