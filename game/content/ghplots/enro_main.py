import gears
from pbge.plots import Plot
import pbge
from pbge.dialogue import Offer, ContextTag
from game import teams, ghdialogue
from game.ghdialogue import context
import random
from game.content.plotutility import AdventureModuleData
from game.content import gharchitecture, ghterrain, ghrooms, ghwaypoints, ghcutscene, plotutility



class EndlessRoadStub(Plot):
    LABEL = "SCENARIO_ENDLESSROAD"
    active = True
    scope = True

    ADVENTURE_MODULE_DATA = AdventureModuleData(
        "Endless Road",
        "During your travels, you arrive at a small town which is having trouble.",
        (158, 4, 6), "VHS_EndlessRoad.png", convoborder="sys_convoborder_bbmc.png",
        pre_release=True, multi_use=True
    )

    def custom_init(self, nart):
        """Load the features."""
        self.ADVENTURE_MODULE_DATA.apply(nart.camp)
        self.add_sub_plot(nart, "CF_STANDARD_LANCEMATE_HANDLER")

        self.add_first_locale_sub_plot(nart, "TOWNBUILDER")

        # This gets called last to prevent major NPCs who are used elsewhere in the plot from showing up here.
        self.add_sub_plot(nart, "ADD_INSTANT_EGG_LANCEMATE", necessary=False)

        return True
