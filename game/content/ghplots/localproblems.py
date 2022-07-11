#
# Some plots involving problems that affect the local metro scene. These problems generally decrease the Quality of
# Life indicators from the Metrodata object.
#

import random

import game.content
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges
from game import teams, ghdialogue
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor
from pbge.memos import Memo
from . import dd_customobjectives
from .dd_homebase import CD_BIOTECH_DISCOVERIES, BiotechDiscovery
from . import missionbuilder, rwme_objectives
from pbge.challenges import Challenge, AutoOffer


#   ***********************
#   ***  LOCAL_PROBLEM  ***
#   ***********************
#
# Needed Elements:
#    METROSCENE, METRO, MISSION_GATE
#


class RabbleRouser(Plot):
    LABEL = "LOCAL_PROBLEM"
    scope = "METRO"
    UNIQUE = True
    QOL = gears.QualityOfLife(community=-3)
    active = True

    RUMOR = Rumor(
        "{NPC} has been spreading a baseless conspiracy theory",
        offer_msg="You can speak to {NPC} at {NPC_SCENE} if you want to find out for yourself.",
        memo="{NPC} has been expounding a conspiracy theory and stirring up local resentment against {METROSCENE} leader {LEADER}.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(self, pstate):
        return "METRO" in pstate.elements and isinstance(pstate.elements["METRO"].city_leader, gears.base.Character)

    def custom_init(self, nart):
        # Start by creating and placing the rabble-rouser.
        scene = self.seek_element(
            nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"], backup_seek_func=self._is_ok_scene
        )

        metroscene = self.elements["METROSCENE"]

        npc = self.register_element(
            "NPC",
            gears.selector.random_character(
                rank=random.randint(10, 50), job=gears.jobs.ALL_JOBS["Pundit"],
                mecha_colors=gears.color.random_mecha_colors(),
                local_tags=tuple(self.elements["METROSCENE"].attributes),
            ), dident="NPC_SCENE")

        # Also save the leader in this plot.
        leader = self.elements["LEADER"] = self.elements["METRO"].city_leader

        # Find a military/police person in this city.
        guard = self.seek_element(
            nart, "GUARD", self._is_best_guard, scope=self.elements["METROSCENE"], must_find=False
        )
        if not guard:
            myplot = self.add_sub_plot(nart, "PLACE_LOCAL_REPRESENTATIVES",
                                       elements={"LOCALE": self.elements["METROSCENE"],
                                                 "FACTION": self.elements["METROSCENE"].faction})
            guard = myplot.elements["NPC"]
            self.elements["GUARD"] = guard

        # Why not add a tycoon and a rival politician as well?
        self.seek_element(
            nart, "_TYCOON_SCENE", self._is_ok_scene, scope=self.elements["METROSCENE"]
        )
        tycoon = self.register_element(
            "TYCOON",
            gears.selector.random_character(
                rank=random.randint(10, 50), job=gears.jobs.ALL_JOBS["Corporate Executive"],
                mecha_colors=gears.color.random_mecha_colors(),
                local_tags=tuple(self.elements["METROSCENE"].attributes),
            ), dident="_TYCOON_SCENE")

        self.seek_element(
            nart, "_RIVAL_SCENE", self._is_ok_scene, scope=self.elements["METROSCENE"]
        )
        rival = self.register_element(
            "RIVAL",
            gears.selector.random_character(
                rank=random.randint(10, 50), job=gears.jobs.ALL_JOBS["Bureaucrat"],
                mecha_colors=gears.color.random_mecha_colors(),
                local_tags=tuple(self.elements["METROSCENE"].attributes),
            ), dident="_RIVAL_SCENE")

        # Now, we don't know yet whether the rabble-rouser is in the right to be raising rabble, so we're going to
        # add a mystery to find out.
        suspect_cards = [ghchallenges.NPCSusCard(c) for c in (npc, leader, guard, tycoon, rival)]
        suspect_susdeck = pbge.okapipuzzle.SusDeck("Suspect", suspect_cards)

        action_cards = [
            ghchallenges.VerbSusCardFeaturingNPC("Hire {}".format(npc), "to hire {}".format(npc),
                                                 "hired {}".format(npc), "did not hire {}".format(npc), npc),
            ghchallenges.VerbSusCardFeaturingNPC("Bribery", "to bribe {}".format(guard), "bribed {}".format(guard),
                                                 "did not bribe {}".format(guard), guard),
            pbge.okapipuzzle.VerbSusCard("Spread Lies", "to spread lies", "spread lies", "didn't spread lies",
                                         data={"image_name": "mystery_verbs.png", "frame": 2}),
            pbge.okapipuzzle.VerbSusCard("Embezzled", "to embezzle", "embezzled government funds",
                                         "didn't embezzle anything",
                                         data={"image_name": "mystery_verbs.png", "frame": 2}, gameob=npc),
            pbge.okapipuzzle.VerbSusCard("Sow Chaos", "to sow chaos in {}".format(self.elements["METROSCENE"]),
                                                 "sowed chaos in {}".format(self.elements["METROSCENE"]),
                                                 "did not cause chaos in {}".format(self.elements["METROSCENE"]),
                                                 data={"image_name": "mystery_verbs.png", "frame": 2})
        ]
        action_susdeck = pbge.okapipuzzle.SusDeck("Action", action_cards)

        motive_cards = [
            pbge.okapipuzzle.VerbSusCard(
                "Keep Power", "to maintain power", "maintained control", "didn't try to maintain power",
                data={"image_name": "mystery_motives.png", "frame": 2}, role=pbge.okapipuzzle.SUS_MOTIVE
            ),
            pbge.okapipuzzle.VerbSusCard(
                "Take Over", "to usurp control of {}".format(self.elements["METROSCENE"]), "usurped control",
                "didn't try to usurp power",
                data={"image_name": "mystery_motives.png", "frame": 2}, role=pbge.okapipuzzle.SUS_MOTIVE
            ),
            pbge.okapipuzzle.VerbSusCard(
                "Pay Debts", "to pay off gambling debts", "paid off gambling debts", "didn't have gambling debts",
                data={"image_name": "mystery_verbs.png", "frame": 5}, role=pbge.okapipuzzle.SUS_MOTIVE
            ),
            ghchallenges.VerbSusCardFeaturingNPC(
                "Get Revenge", "to get revenge on {}".format(leader),
                "got revenge", "didn't try to get revenge on {}".format(leader), leader,
                role=pbge.okapipuzzle.SUS_MOTIVE
            ),
            pbge.okapipuzzle.VerbSusCard(
                "Become Rich", "to enrich themself", "enriched themself", "didn't get rich",
                data={"image_name": "mystery_motives.png", "frame": 5}, role=pbge.okapipuzzle.SUS_MOTIVE
            )
        ]
        motive_susdeck = pbge.okapipuzzle.SusDeck("Motive", motive_cards)

        # We are going to create the solution here because we need to error-check unreasonable cases.
        solution = [random.choice(suspect_cards), random.choice(action_cards), random.choice(motive_cards)]
        if random.randint(1,2) == 1:
            # The guilty party is most likely going to be the leader or the rabblerouser.
            solution[0] = random.choice(suspect_cards[:2])

        while solution[1].gameob is solution[0].gameob:
            solution[1] = random.choice(action_cards)

        if solution[0].gameob is leader:
            if solution[2] is motive_cards[1]:
                solution[2] = motive_cards[0]
            elif solution[2] is motive_cards[3]:
                solution[2] = motive_cards[4]
        elif solution[0].gameob is npc:
            if solution[2] is motive_cards[0]:
                solution[2] = motive_cards[1]

        mymystery = self.register_element("MYSTERY", pbge.okapipuzzle.OkapiPuzzle(
            "Trouble in {}".format(self.elements["METROSCENE"]),
            (suspect_susdeck, action_susdeck, motive_susdeck), "{a} {b.verbed} {c.to_verb}.",
            solution=solution
        ))

        # Now, we subcontract the actual mystery challenge out to a utility plot.
        self.add_sub_plot(nart, "POLITICAL_MYSTERY_CHALLENGE", ident="MCHALLENGE",
                          elements={"VIOLATED_VIRTUES": (gears.personality.Fellowship, gears.personality.Justice)})

        # We're also going to subcontract out NPC's attempt to dethrone LEADER and LEADER's attempt to discredit NPC.
        sp = self.add_sub_plot(
            nart, "DETHRONE_BY_POPULAR_UPRISING", ident="DETHRONE_CHALLENGE",
            elements={"NPC": leader, "VIOLATED_VIRTUES": (gears.personality.Fellowship, gears.personality.Justice),
                      "UPHELD_VIRTUE": random.choice([gears.personality.Peace, gears.personality.Glory,
                                                      gears.personality.Duty])}
        )
        sp.elements["CHALLENGE"].involvement.exclude.add(npc)

        sp = self.add_sub_plot(
            nart, "DIPLOMACY_TO_DISCREDIT", ident="DISCREDIT_CHALLENGE",
            elements={"NPC": npc, "VIOLATED_VIRTUE": gears.personality.Fellowship,
                      "UPHELD_VIRTUE": random.choice([None, gears.personality.Peace, gears.personality.Glory,
                                                      gears.personality.Justice, gears.personality.Duty]),

                      }
        )
        sp.elements["CHALLENGE"].involvement.exclude.add(leader)

        # Store the villain of the story as another element. This way, we only need to deal with the stuff once.
        self.elements["CULPRIT"] = solution[0].gameob

        self.mystery_solved = False
        self.solution_public = False

        return True

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
                and gears.tags.SCENE_CULTURE in candidate.attributes)

    def _is_ok_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def _is_best_guard(self, nart, candidate):
        return (isinstance(candidate, gears.base.Character) and candidate.combatant and
                nart.camp.is_not_lancemate(candidate) and candidate is not self.elements["LEADER"] and
                nart.camp.are_faction_allies(candidate, self.elements["METROSCENE"]) and not candidate.mnpcid)

    def MYSTERY_SOLVED(self, camp):
        self.mystery_solved = True
        self.memo = Memo(
            "You learned that {MYSTERY.solution_text}".format(**self.elements), location=self.elements["CULPRIT"].scene
        )

    def MCHALLENGE_WIN(self, camp):
        self.solution_public = True
        self.memo = Memo(
            "You learned that {MYSTERY.solution_text} This information is no longer a secret.".format(**self.elements),
            location=self.elements["CULPRIT"].scene
        )

    def DETHRONE_CHALLENGE_WIN(self, camp):
        pass

    def DISCREDIT_CHALLENGE_WIN(self, camp):
        pass

