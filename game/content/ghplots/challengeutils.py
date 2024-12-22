import random
import gears
import pbge
from game.content import ghchallenges
from game import teams, ghdialogue
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor
from . import missionbuilder, rwme_objectives
from pbge.challenges import Challenge, AutoOffer


#   **********************************
#   ***  MURDER_MYSTERY_CHALLENGE  ***
#   **********************************
#
#   We're being passed a mystery. Create a challenge around it.
#
# Needed Elements:
#    METROSCENE, METRO, MISSION_GATE, MYSTERY
#
# Triggers:
#   This plot will send a WIN signal if won, or a LOSE signal if it becomes unwinnable.

class MurderMysteryBountyHunter(Plot):
    LABEL = "MURDER_MYSTERY_CHALLENGE"
    scope = "METRO"
    UNIQUE = True
    active = True

    RUMOR = Rumor(
        "{NPC} has been investigating {MYSTERY}",
        offer_msg="{NPC} is a bounty hunter; I don't think {NPC.gender.subject_pronoun} is very good at investigation, though. You can talk to {NPC.gender.object_pronoun} at {NPC_SCENE}.",
        memo="{NPC} is a bounty hunter investigating {MYSTERY}",
        prohibited_npcs=("NPC",)
    )

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=max(random.randint(self.rank - 10, self.rank + 10), 25),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              job=gears.jobs.ALL_JOBS["Bounty Hunter"])
        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"],
                                  backup_seek_func=self._is_ok_scene)
        self.register_element("NPC", npc, dident="NPC_SCENE")

        mymystery: pbge.okapipuzzle.OkapiPuzzle = self.elements["MYSTERY"]
        self.elements["CULPRIT"] = mymystery.solution[0].gameob

        involved_set = set()
        for d in mymystery.decks:
            for c in d.cards:
                if c.gameob:
                    involved_set.add(c.gameob)
        excluded_set = involved_set.copy()
        excluded_set.add(npc)

        mychallenge = self.register_element("CHALLENGE", pbge.challenges.MysteryChallenge(
            str(mymystery), self.elements["MYSTERY"],
            memo=pbge.challenges.MysteryMemo("{NPC} sent you to investigate {MYSTERY.name}.".format(**self.elements)),
            active=False,
            oppoffers=[
                pbge.challenges.AutoOffer(
                    dict(
                        msg="[I_KNOW_THINGS_ABOUT_STUFF] [LISTEN_TO_MY_INFO]",
                        context=ContextTag([context.CUSTOM, ]), effect=self._get_a_clue,
                        data={
                            "reply": "Do you know anything about {MYSTERY}?".format(**self.elements),
                            "stuff": "{MYSTERY}".format(**self.elements)
                        }, dead_end=True
                    ), active=True, uses=99,
                    involvement=ghchallenges.InvolvedIfCluesRemainAnd(
                        self.elements["MYSTERY"],
                        ghchallenges.InvolvedMetroResidentNPCs(self.elements["METROSCENE"], exclude=excluded_set)),
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Perception, gears.stats.Negotiation, self.rank, untrained_ok=True
                    )
                ),

                pbge.challenges.AutoOffer(
                    dict(
                        msg="[THINK_ABOUT_THIS] [I_REMEMBER_NOW]",
                        context=ContextTag([context.CUSTOM, ]),
                        data={
                            "reply": "Do you remember anything about the {MYSTERY}?".format(**self.elements),
                            "stuff": "the {MYSTERY}".format(**self.elements)
                        }, dead_end=True
                    ), active=True, uses=99,
                    involvement=ghchallenges.InvolvedIfUnassociatedCluesRemainAnd(
                        mymystery, mymystery.decks[0], pbge.challenges.InvolvedSet(involved_set)
                    ),
                    npc_effect=self._get_unassociated_clue,
                ),
            ],
        ))

        return True

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
                and gears.tags.SCENE_GOVERNMENT in candidate.attributes)

    def _is_ok_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def _get_unassociated_clue(self, camp, npc):
        candidates = [c for c in self.elements["MYSTERY"].unknown_clues if not c.is_involved(npc)]
        if candidates:
            self.elements["CHALLENGE"].advance(camp, random.choice(candidates))
        else:
            self.elements["CHALLENGE"].advance(camp)

    def _get_a_clue(self, camp):
        self.elements["CHALLENGE"].advance(camp)

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        if not self.elements["CHALLENGE"].active:
            mylist.append(Offer(
                "[HELLO] I've been investigating {MYSTERY}, but so far I've only found a few leads.".format(
                    **self.elements),
                ContextTag([context.HELLO, ]),
            ))

            mylist.append(Offer(
                "Here, I'll share my notes with you. So far I have a list of suspects, some possible motives... not much.",
                ContextTag([context.CUSTOM, ]), subject=str(self.elements["MYSTERY"]),
                data={"reply": "Maybe I could help you with that."},
                effect=self._start_challenge, dead_end=True
            ))
        else:
            mylist.append(Offer(
                "[HELLO] Have you learned anything about {MYSTERY}?".format(**self.elements),
                ContextTag([context.HELLO, ]),
            ))

            if self.elements["CHALLENGE"].is_won():
                mylist.append(Offer(
                    "[GOOD_JOB] {CULPRIT} will be going away for a long time... Here's your share of the reward.".format(
                        **self.elements),
                    ContextTag([context.CUSTOM, ]),
                    data={"reply": "I have. {MYSTERY.solution_text}".format(**self.elements)},
                    effect=self._win_challenge
                ))

            mylist.append(Offer(
                "Great. Please let me know if you discover any leads.".format(**self.elements),
                ContextTag([context.CUSTOM, ]),
                data={"reply": "[STILL_WORKING_ON_IT]"}
            ))

        return mylist

    def _start_challenge(self, camp):
        self.elements["CHALLENGE"].activate(camp)
        self.memo = pbge.memos.Memo(
            "{NPC} asked you to help investigate {MYSTERY}.".format(**self.elements), self.elements["NPC_SCENE"]
        )

    def _win_challenge(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)
        camp.dole_xp(100)
        camp.freeze(self.elements["CULPRIT"])
        camp.credits += gears.selector.calc_mission_reward(self.rank, 150)
        self.end_plot(camp)

    def t_UPDATE(self, camp: gears.GearHeadCampaign):
        if not self.elements["NPC"].is_operational():
            camp.check_trigger("LOSE", self)
            self.end_plot(camp)


#   *************************************
#   ***  POLITICAL_MYSTERY_CHALLENGE  ***
#   *************************************
#
#   We're being passed a mystery. Create a challenge around it.
#
# Needed Elements:
#    METROSCENE, METRO, MISSION_GATE, MYSTERY
#
# Optional Elements:
#   VIOLATED_VIRTUES = A list of virtues that this mystery violates.
#
# Triggers:
#   This plot will send a WIN signal if won, or a LOSE signal if it becomes unwinnable.

class InvestigativeReporter(Plot):
    LABEL = "POLITICAL_MYSTERY_CHALLENGE"
    scope = "METRO"
    UNIQUE = True
    active = True

    RUMOR = Rumor(
        "{NPC} has been looking for {NPC.gender.possessive_determiner} next big story",
        offer_msg="{NPC} is a reporter; {NPC.gender.subject_pronoun} thinks there's some kind of scandal happening in {METROSCENE}. You can talk to {NPC.gender.object_pronoun} at {NPC_SCENE}.",
        memo="{NPC} is a reporter looking for {NPC.gender.possessive_determiner} next big story.",
        prohibited_npcs=("NPC",)
    )

    VV_DETAILS = {
        gears.personality.Justice: [
            "Corruption has been rampant; our leaders act with impunity."
        ],
        gears.personality.Peace: [
            "People don't feel safe here. Statistically, they're right to feel that way."
        ],
        gears.personality.Fellowship: [
            "Trust and cooperation are at all-time lows. People are suspicious of their neighbors."
        ],
        gears.personality.Duty: [
            "There's plenty of military spending, but nothing to show for it. I suspect kickbacks."
        ],
        gears.personality.Glory: [
            "We've seen the standard of living fall year after year, but no explanation for why."
        ],
    }

    def custom_init(self, nart):
        npc = gears.selector.random_character(rank=max(random.randint(self.rank - 10, self.rank + 10), 25),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              job=gears.jobs.ALL_JOBS["Reporter"])
        scene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"],
                                  backup_seek_func=self._is_ok_scene)
        self.register_element("NPC", npc, dident="NPC_SCENE")

        mymystery: pbge.okapipuzzle.OkapiPuzzle = self.elements["MYSTERY"]
        involved_set = set()
        for d in mymystery.decks:
            for c in d.cards:
                if c.gameob:
                    involved_set.add(c.gameob)
        excluded_set = involved_set.copy()
        excluded_set.add(npc)

        mychallenge = self.register_element("CHALLENGE", pbge.challenges.MysteryChallenge(
            "{} Mystery".format(self.elements["METROSCENE"]), self.elements["MYSTERY"],
            memo=pbge.challenges.MysteryMemo("{NPC} sent you to investigate {MYSTERY.name}.".format(**self.elements)),
            active=False,
            oppoffers=[
                pbge.challenges.AutoOffer(
                    dict(
                        msg="[I_KNOW_THINGS_ABOUT_STUFF] [LISTEN_TO_MY_INFO]",
                        context=ContextTag([context.CUSTOM, ]), effect=self._get_a_clue,
                        data={
                            "reply": "Do you know anything about the {MYSTERY}?".format(**self.elements),
                            "stuff": "the {MYSTERY}".format(**self.elements)
                        }, dead_end=True
                    ), active=True, uses=99,
                    involvement=ghchallenges.InvolvedIfCluesRemainAnd(
                        self.elements["MYSTERY"],
                        ghchallenges.InvolvedMetroResidentNPCs(self.elements["METROSCENE"], exclude=excluded_set)),
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Perception, gears.stats.Negotiation, self.rank, untrained_ok=True
                    )
                ),

                pbge.challenges.AutoOffer(
                    dict(
                        msg="[THINK_ABOUT_THIS] [I_REMEMBER_NOW]",
                        context=ContextTag([context.CUSTOM, ]),
                        data={
                            "reply": "Do you remember anything about the {MYSTERY}?".format(**self.elements),
                            "stuff": "the {MYSTERY}".format(**self.elements)
                        }, dead_end=True
                    ), active=True, uses=99,
                    involvement=ghchallenges.InvolvedIfUnassociatedCluesRemainAnd(
                        mymystery, mymystery.decks[0], pbge.challenges.InvolvedSet(involved_set)
                    ),
                    npc_effect=self._get_unassociated_clue,
                ),
            ],
        ))

        return True

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
                and gears.tags.SCENE_MEETING in candidate.attributes)

    def _is_ok_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def _get_unassociated_clue(self, camp, npc):
        candidates = [c for c in self.elements["MYSTERY"].unknown_clues if not c.is_involved(npc)]
        if candidates:
            self.elements["CHALLENGE"].advance(camp, random.choice(candidates))
        else:
            self.elements["CHALLENGE"].advance(camp)

    def _get_a_clue(self, camp):
        self.elements["CHALLENGE"].advance(camp)

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        if not self.elements["CHALLENGE"].active:
            mylist.append(Offer(
                "[HELLO] Do you know anything about the {MYSTERY}?".format(**self.elements),
                ContextTag([context.HELLO, ]),
            ))

            vv = self.elements.get("VIOLATED_VIRTUES")
            details = ["This could extend to the highest levels of government.",
                       "The leadership is almost certainly compromised."]
            for virt in vv:
                details += self.VV_DETAILS.get(virt, [])

            mylist.append(Offer(
                "There's something going wrong in {}. {} [LET_ME_KNOW_IF_YOU_HEAR_ANYTHING]".format(
                    self.elements["METROSCENE"], random.choice(details)),
                ContextTag([context.CUSTOM, ]), subject=str(self.elements["MYSTERY"]),
                data={"reply": "Not really; why don't you tell me about it?"},
                effect=self._start_challenge
            ))
        else:
            mylist.append(Offer(
                "[HELLO] Have you learned anything about the {MYSTERY}?".format(**self.elements),
                ContextTag([context.HELLO, ]),
            ))

            if self.elements["CHALLENGE"].is_won():
                mylist.append(Offer(
                    "[GOOD_JOB] This information will be a big help to everyone in {METROSCENE}... I'll make sure it's on the landing page of every newsnet!".format(
                        **self.elements),
                    ContextTag([context.CUSTOM, ]),
                    data={"reply": "I have. {MYSTERY.solution_text}".format(**self.elements)},
                    effect=self._win_challenge
                ))

            mylist.append(Offer(
                "Great. Please let me know if you discover any leads.".format(**self.elements),
                ContextTag([context.CUSTOM, ]),
                data={"reply": "[STILL_WORKING_ON_IT]"}
            ))

        return mylist

    def _start_challenge(self, camp):
        self.elements["CHALLENGE"].activate(camp)
        self.memo = None

    def _win_challenge(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)
        camp.dole_xp(200)
        self.end_plot(camp)

    def t_UPDATE(self, camp: gears.GearHeadCampaign):
        if not self.elements["NPC"].is_not_destroyed():
            camp.check_trigger("LOSE", self)
            self.end_plot(camp)
