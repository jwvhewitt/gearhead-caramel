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


class TimeAndChallengeExpiration(object):
    def __init__(self, camp, chal, time_limit=10):
        self.chal = chal
        self.time_limit = camp.day + time_limit

    def __call__(self, camp, plot):
        return camp.day > self.time_limit or not self.chal.active


#   *****************************
#   ***  DIPLOMACY_CHALLENGE  ***
#   *****************************

class BasicDiplomaticChallenge(Plot):
    LABEL = "CHALLENGE_PLOT"
    active = True
    scope = "METRO"

    @classmethod
    def matches(cls, pstate: PlotState):
        return "METROSCENE" in pstate.elements and "MISSION_GATE" in pstate.elements

    def custom_init(self, nart: GHNarrativeRequest):
        self.candidates = [c for c in nart.challenges if c.chaltype == ghchallenges.DIPLOMACY_CHALLENGE]
        if self.candidates:
            npc = self.seek_element(nart, "NPC", self._is_good_npc, lock=True, scope=self.elements["METROSCENE"])
            mychallenge = self.register_element("CHALLENGE", self._get_challenge_for_npc(nart, npc))
            self.register_element("NPC_SCENE", npc.scene)
            self.register_element("ENEMY_FACTION", mychallenge.key[0])
            self.expiration = TimeAndChallengeExpiration(nart.camp, mychallenge, time_limit=5)
            self.RUMOR = Rumor(
                "{} has strong opinions about {}".format(npc, mychallenge.data["challenge_subject"]),
                offer_msg="I'm sure {NPC.gender.subject_pronoun} would love to argue with you about it. You can find {NPC.gender.object_pronoun} at {NPC_SCENE}.",
                memo="{} wants to argue about {}".format(npc, mychallenge.data["challenge_subject"]),
                prohibited_npcs=("NPC",)
            )

            return True

    def _get_challenge_for_npc(self, nart, npc):
        candidates = [c for c in self.candidates if c.is_involved(nart.camp, npc)]
        if candidates:
            return random.choice(candidates)

    def _is_good_npc(self, nart: GHNarrativeRequest, candidate):
        return (
            isinstance(candidate, gears.base.Character) and candidate not in nart.camp.party and
            (not candidate.relationship or gears.relationships.RT_LANCEMATE not in candidate.relationship.tags) and
            self._get_challenge_for_npc(nart, candidate)
        )

    def _win_the_mission(self, camp):
        self.elements["CHALLENGE"].advance(camp, 2)
        self.end_plot(camp)

    def NPC_offers(self, camp):
        mylist = list()

        subject = random.choice(self.elements["CHALLENGE"].data["challenge_statements"])

        mylist.append(Offer(
            "[HELLO] [CONTROVERSIAL_OPINION]", ContextTag([context.HELLO,]),
            data={"opinion": subject}
        ))

        ghdialogue.SkillBasedPartyReply(
            Offer(
                "[MAYBE_YOU_ARE_RIGHT_ABOUT_OPINION] [I_MUST_CONSIDER_MY_NEXT_STEP]",
                ContextTag([context.CUSTOM,]), effect=self._win_the_mission,
                data={
                    "reply": "[HAVE_YOU_CONSIDERED]",
                    "consider_this": random.choice(self.elements["CHALLENGE"].data["pc_rebuttals"]),
                    "opinion": random.choice(self.elements["CHALLENGE"].data["npc_agreement"])
                }, subject=subject
            ), camp, mylist, gears.stats.Charm, gears.stats.Negotiation, self.rank, gears.stats.DIFFICULTY_AVERAGE
        )

        mylist.append(Offer(
            "{}. [GOODBYE]".format(random.choice(self.elements["CHALLENGE"].data["npc_disagreement"])),
            ContextTag([context.CUSTOM]), effect=self.end_plot,
            data={"reply": "[YOU_COULD_BE_RIGHT]"}, subject=subject
        ))

        return mylist


#   *************************
#   ***  FIGHT_CHALLENGE  ***
#   *************************

class BasicFightChallenge(Plot):
    LABEL = "CHALLENGE_PLOT"
    active = True
    scope = "METRO"
    RUMOR = Rumor(
        "{NPC} is looking for a pilot to fight {ENEMY_FACTION}",
        offer_msg="You can speak to {NPC} at {NPC_SCENE} if you want the mission.",
        memo="{NPC} is looking for a pilot to fight {ENEMY_FACTION}.",
        prohibited_npcs=("NPC",)
    )

    DEFAULT_OBJECTIVES = (
        ghchallenges.DescribedObjective(
            missionbuilder.BAMO_LOCATE_ENEMY_FORCES, "mecha from {ENEMY_FACTION} have been detected nearby"
        ),
        ghchallenges.DescribedObjective(
            missionbuilder.BAMO_DEFEAT_COMMANDER, "an agent of {ENEMY_FACTION} has been operating in this area"
        )
    )

    @classmethod
    def matches(cls, pstate: PlotState):
        return "METROSCENE" in pstate.elements and "MISSION_GATE" in pstate.elements

    def custom_init(self, nart: GHNarrativeRequest):
        self.candidates = [c for c in nart.challenges if c.chaltype == ghchallenges.FIGHT_CHALLENGE]
        if self.candidates:
            #mychallenge = self.register_element("CHALLENGE", random.choice(self.candidates))
            npc = self.seek_element(nart, "NPC", self._is_good_npc, lock=True, scope=self.elements["METROSCENE"])
            mychallenge = self.register_element("CHALLENGE", self._get_challenge_for_npc(nart, npc))
            self.register_element("NPC_SCENE", npc.scene)
            self.register_element("ENEMY_FACTION", mychallenge.key[0])
            self.expiration = TimeAndChallengeExpiration(nart.camp, mychallenge, time_limit=5)

            my_dobjectives = random.sample(list(self.DEFAULT_OBJECTIVES) + mychallenge.data.get("mission_objectives", []), 2)
            self.mission_desc = random.choice(my_dobjectives).mission_desc.format(**self.elements)

            mgram = missionbuilder.MissionGrammar(
                random.choice(mychallenge.data.get("challenge_objectives", ["[defeat_you]",]) + list(c.objective_pp for c in my_dobjectives)),
                random.choice(mychallenge.data.get("enemy_objectives", ["[defeat_you]",]) + list(c.objective_ep for c in my_dobjectives)),
                random.choice([c.win_pp for c in my_dobjectives]),
                random.choice([c.win_ep for c in my_dobjectives]),
                random.choice([c.lose_pp for c in my_dobjectives]),
                random.choice([c.lose_ep for c in my_dobjectives])
            )

            sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])
            self.mission_seed = missionbuilder.BuildAMissionSeed(
                nart.camp, "{NPC}'s Mission".format(**self.elements),
                self.elements["METROSCENE"], self.elements["MISSION_GATE"],
                allied_faction=npc.faction,
                enemy_faction=self.elements["ENEMY_FACTION"], rank=self.rank,
                objectives=[c.objective for c in my_dobjectives],
                one_chance=True,
                scenegen=sgen, architecture=archi, mission_grammar=mgram,
                cash_reward=120,
                on_win=self._win_the_mission
            )

            self.mission_active = False

            return True

    def _get_challenge_for_npc(self, nart, npc):
        candidates = [c for c in self.candidates if c.is_involved(nart.camp, npc)]
        if candidates:
            return random.choice(candidates)

    def _is_good_npc(self, nart: GHNarrativeRequest, candidate):
        return (
            isinstance(candidate, gears.base.Character) and candidate not in nart.camp.party and
            (not candidate.relationship or gears.relationships.RT_LANCEMATE not in candidate.relationship.tags) and
            self._get_challenge_for_npc(nart, candidate)
        )

    def _win_the_mission(self, camp):
        comp = self.mission_seed.get_completion(True)
        self.elements["CHALLENGE"].advance(camp, max((comp-61)//10, 1))
        self.end_plot(camp)

    def get_mission_intro(self):
        mylist = ["[MechaMissionVsEnemyFaction]."]
        mychallenge = self.elements["CHALLENGE"]
        mylist += mychallenge.data.get("mission_intros", [])

        return random.choice(mylist)

    def NPC_offers(self, camp):
        mylist = list()

        if not self.mission_active:
            mylist.append(Offer(
                "[LOOKING_FOR_CAVALIER] {}".format(self.get_mission_intro()),
                ContextTag([context.HELLO, context.MISSION]), data={"enemy_faction": self.elements["ENEMY_FACTION"]}
            ))

            mylist.append(Offer(
                "{}. [DOYOUACCEPTMISSION]".format(self.mission_desc),
                ContextTag([context.MISSION]), data={"enemy_faction": self.elements["ENEMY_FACTION"]},
                subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "[IWillSendMissionDetails]; [GOODLUCK]",
                ContextTag([context.ACCEPT]), effect=self.activate_mission,
                subject=self
            ))

            mylist.append(Offer(
                "[UNDERSTOOD] [GOODBYE]",
                ContextTag([context.DENY]), effect=self.end_plot,
                subject=self
            ))

        return mylist

    def t_START(self,camp):
        if self.LABEL == "DZRE_TEST" and not self.mission_active:
            self.mission_active = True

    def t_UPDATE(self,camp):
        if self.mission_seed.ended:
            self.end_plot(camp)

    def activate_mission(self,camp):
        self.mission_active = True
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])
        self.expiration = None

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed and self.mission_active:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

