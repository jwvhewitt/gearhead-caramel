import random
from game import content, services, teams, ghdialogue
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges, ghrooms
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor, PlotState
from pbge import stories, quests
from pbge.memos import Memo
from . import missionbuilder, rwme_objectives, campfeatures, ghquests
from pbge.challenges import Challenge, AutoOffer
from .shops_plus import get_building
import collections


WMW_CONSOLIDATION = "WMW_CONSOLIDATION"


# A consolidation plot gets the following elements:
# METROSCENE, METRO, WORLD_MAP_WAR
# FORMER_FACTION: The faction you just kicked out. May be None.

class DiplomaticConsolidation(Plot):
    # Talk to residents and try to convince them that the occupation is OK.
    LABEL = WMW_CONSOLIDATION
    scope = "METRO"
    active = True

    intro_ready = True

    DEFAULT_CHALLENGE_STEP = 1

    CHALLENGE_SUBJECTS = (
        "",
    )

    def custom_init(self, nart):
        self.elements["ALLIED_FACTION"] = self.elements["WORLD_MAP_WAR"].player_team

        self.register_element("CHALLENGE", Challenge(
            "Promote {ALLIED_FACTION} in {METROSCENE}".format(**self.elements),
            ghchallenges.PR_CHALLENGE, [self.elements["WORLD_MAP_WAR"].player_team],
            involvement=ghchallenges.InvolvedMetroResidentNPCs(self.elements["METROSCENE"]), active=False,
            data={
                "challenge_subject": None,
                "pc_promotions": (),
                "npc_opinions": (),
                "npc_agreement": (),
                "npc_disagreement": ()
            },
            oppoffers=(
                AutoOffer(
                    dict(
                        msg="[THINK_ABOUT_THIS] [IT_IS_OK_OR_BETTER]",
                        context=ContextTag([context.CUSTOM,]), effect=self._advance_challenge,
                        data={
                            "reply": "How do you feel about {ALLIED_FACTION}?".format(**self.elements),
                            "it": "{ALLIED_FACTION} being in {METROSCENE}".format(**self.elements)
                        }
                    ), active=True, uses=99,
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Charm, gears.stats.Negotiation, self.rank, untrained_ok=True,
                        difficulty=gears.stats.DIFFICULTY_HARD
                    )
                ),
            ), memo=pbge.challenges.ChallengeMemo(
                "You should ensure that the residents of {METROSCENE} are okay with the presence of {ALLIED_FACTION}.".format(**self.elements)
            ), memo_active=True, deactivate_on_win=True

        ))

        return True

    def CHALLENGE_WIN(self, camp):
        pbge.BasicNotification("Consolidation complete!", count=160)
        camp.check_trigger("WIN", self)
        self.elements["WORLD_MAP_WAR"].player_can_act = True
        self.end_plot(camp)

    def _advance_challenge(self, camp):
        self.elements["CHALLENGE"].advance(camp, self.DEFAULT_CHALLENGE_STEP)

    def METROSCENE_ENTER(self, camp):
        if self.intro_ready:
            pbge.alert("The next step is to consolidate your victory in {METROSCENE}. ".format(**self.elements))
            self.elements["CHALLENGE"].activate(camp)
            self.intro_ready = False

