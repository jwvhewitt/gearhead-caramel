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
        self.time_limit = camp.time + time_limit

    def __call__(self, camp, plot):
        return camp.time > self.time_limit or not self.chal.active


# All CHALLENGE_PLOTs should store their Challenge as element "CHALLENGE"!!! At least, they should if they want to use
# the no_plots_for_this_challenge function above.

#   ****************************
#   ***  DETHRONE_CHALLENGE  ***
#   ****************************

class DethroneByDuelingSupporter(Plot):
    LABEL = "CHALLENGE_PLOT"
    active = True
    scope = "METRO"
    RUMOR = Rumor(
        "{NPC} is a loyal supporter of {LEADER}",
        offer_msg="You can talk to {NPC} at {NPC_SCENE} if you want to change {NPC.gender.possessive_determiner} mind.",
        memo="{NPC} is a loyal supporter of {LEADER}.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(cls, pstate: PlotState):
        return "METROSCENE" in pstate.elements and "MISSION_GATE" in pstate.elements

    def custom_init(self, nart: GHNarrativeRequest):
        self.candidates = [c for c in nart.challenges if c.chaltype == ghchallenges.DETHRONE_CHALLENGE]
        if self.candidates:
            npc = self.seek_element(nart, "NPC", self._is_good_npc, lock=True, scope=self.elements["METROSCENE"])
            mychallenge = self.register_element("CHALLENGE", self._get_challenge_for_npc(nart, npc))
            self.register_element("NPC_SCENE", npc.scene)

            self.expiration = TimeAndChallengeExpiration(nart.camp, mychallenge, time_limit=5)

            sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])
            # Create the mission seed. Turn the defeat_trigger off because we'll be handling that manually.
            self.mission_seed = missionbuilder.BuildAMissionSeed(
                nart.camp, "Duel {NPC}".format(**self.elements),
                self.elements["METROSCENE"], self.elements["MISSION_GATE"],
                enemy_faction=npc.faction, rank=self.rank,
                objectives=[missionbuilder.BAMO_DUEL_NPC],
                one_chance=True,
                scenegen=sgen, architecture=archi,
                cash_reward=120, solo_mission=True,
                on_win=self._win_the_mission, custom_elements={missionbuilder.BAME_NPC: npc},
                make_enemies=False
            )

            self.elements["LEADER"] = mychallenge.key[0]

            self.mission_active = False
            del self.candidates
            return True

    def _get_challenge_for_npc(self, nart, npc):
        candidates = [c for c in self.candidates if c.is_involved(nart.camp, npc)]
        if candidates:
            return random.choice(candidates)

    def _is_good_npc(self, nart: GHNarrativeRequest, candidate):
        return (
            isinstance(candidate, gears.base.Character) and nart.camp.is_not_lancemate(candidate) and
            candidate.combatant and self._get_challenge_for_npc(nart, candidate)
        )

    def _win_the_mission(self, camp):
        comp = self.mission_seed.get_completion(True)
        self.elements["CHALLENGE"].advance(camp, max((comp-51)//10, 3))
        self.end_plot(camp)

    def _conversation_win(self, camp: gears.GearHeadCampaign):
        if camp.party_has_personality(self.elements["CHALLENGE"].data["violated_virtue"]):
            npc: gears.base.Character = self.elements["NPC"]
            npc.relationship.reaction_mod += 10
        self.elements["CHALLENGE"].advance(camp, 4)
        self.end_plot(camp)

    def NPC_offers(self, camp):
        mylist = list()

        if not self.mission_active:
            mychallenge: pbge.challenges.Challenge = self.elements["CHALLENGE"]

            mylist.append(Offer(
                "[HELLO] {LEADER} is a great {LEADER.gender.noun} and deserves our support.".format(**self.elements),
                ContextTag([context.HELLO,])
            ))

            mylist.append(Offer(
                "[YOU_DONT_UNDERSTAND] The truth is that {}.".format(random.choice(mychallenge.data["reasons_to_support"])),
                ContextTag([context.CUSTOM]), data={"reply": "But {}!".format(random.choice(mychallenge.data["reasons_to_dethrone"]))},
                subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "[YOU_DONT_UNDERSTAND] In reality {}.".format(random.choice(mychallenge.data["reasons_to_support"])),
                ContextTag([context.UNFAVORABLE_CUSTOM]),
                data={"reply": "You know that {}!".format(random.choice(mychallenge.data["reasons_to_dethrone"]))},
                subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "[ACCEPT_CHALLENGE] I will meet you outside of town, to defend the honor of {LEADER}!".format(**self.elements),
                ContextTag([context.CUSTOMREPLY]), effect=self.activate_mission,
                subject=self, data={"reply": "[ARE_YOU_WILLING_TO_BET_YOUR_LIFE_ON_THAT]"}
            ))

            vv = mychallenge.data.get("violated_virtue")
            if vv and vv in self.elements["NPC"].personality:
                ghdialogue.SkillBasedPartyReply(
                    Offer(
                        "[MAYBE_YOU_ARE_RIGHT_ABOUT_OPINION] [I_MUST_CONSIDER_MY_NEXT_STEP]",
                        ContextTag([context.CUSTOMREPLY, ]), effect=self._conversation_win,
                        data={
                            "reply": "[HAVE_YOU_CONSIDERED]",
                            "consider_this": "{} is working against {}".format(self.elements["LEADER"], vv),
                            "opinion": "{LEADER} may not be as great as I thought".format(**self.elements)
                        }, subject=self
                    ), camp, mylist, gears.stats.Perception, gears.stats.Negotiation, self.rank,
                    gears.stats.DIFFICULTY_AVERAGE
                )

        return mylist

    def t_START(self, camp):
        if self.LABEL == "DZRE_TEST" and not self.mission_active:
            self.mission_active = True

    def t_UPDATE(self,camp):
        if self.mission_seed.ended:
            self.end_plot(camp)

    def activate_mission(self,camp):
        self.mission_active = True
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed and self.mission_active:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)



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
            del self.candidates
            return True

    def _get_challenge_for_npc(self, nart, npc):
        candidates = [c for c in self.candidates if c.is_involved(nart.camp, npc)]
        if candidates:
            return random.choice(candidates)

    def _is_good_npc(self, nart: GHNarrativeRequest, candidate):
        return (
            isinstance(candidate, gears.base.Character) and nart.camp.is_not_lancemate(candidate) and
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

        if self._rumor_memo_delivered:
            mylist.append(Offer(
                "Yes, it's true! [CONTROVERSIAL_OPINION]",
                ContextTag([context.CUSTOM, ]),
                data={"opinion": subject, "reply": "I hear that you have some controversial opinions."}
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

        ghdialogue.SkillBasedPartyReply(
            Offer(
                "[MAYBE_YOU_ARE_RIGHT_ABOUT_OPINION] [I_MUST_CONSIDER_MY_NEXT_STEP]",
                ContextTag([context.CUSTOMREPLY,]), effect=self._win_the_mission,
                data={
                    "reply": "[HAVE_YOU_CONSIDERED]",
                    "consider_this": random.choice(self.elements["CHALLENGE"].data["pc_rebuttals"]),
                    "opinion": random.choice(self.elements["CHALLENGE"].data["npc_agreement"])
                }, subject=subject
            ), camp, mylist, gears.stats.Charm, gears.stats.Negotiation, self.rank, gears.stats.DIFFICULTY_AVERAGE
        )

        mylist.append(Offer(
            "{}. [GOODBYE]".format(random.choice(self.elements["CHALLENGE"].data["npc_disagreement"])),
            ContextTag([context.CUSTOMREPLY]), effect=self.end_plot,
            data={"reply": "[YOU_COULD_BE_RIGHT]"}, subject=subject
        ))

        return mylist

#   ****************************
#   ***  EPIDEMIC_CHALLENGE  ***
#   ****************************

class ObviouslyIllPerson(Plot):
    LABEL = "CHALLENGE_PLOT"
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        "{NPC} has been looking sick",
        offer_msg="I don't know if it's {DISEASE} or something else, but {NPC} at {NPC_SCENE} has definitely been looking unwell.",
        memo="{NPC} looks sick and may have {DISEASE}.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(cls, pstate: PlotState):
        return "METROSCENE" in pstate.elements

    def custom_init(self, nart: GHNarrativeRequest):
        self.candidates = [c for c in nart.challenges if c.chaltype == ghchallenges.EPIDEMIC_CHALLENGE]
        if self.candidates:
            npc = self.seek_element(nart, "NPC", self._is_good_npc, lock=True, scope=self.elements["METROSCENE"])
            mychallenge = self.register_element("CHALLENGE", self._get_challenge_for_npc(nart, npc))
            self.elements["DISEASE"] = mychallenge.key[0]
            self.register_element("NPC_SCENE", npc.scene)
            self.expiration = TimeAndChallengeExpiration(nart.camp, mychallenge, time_limit=25)
            del self.candidates
            self.add_sub_plot(nart, "NPC_VACATION", ident="VACATION")
            return True

    def _get_challenge_for_npc(self, nart, npc):
        candidates = [c for c in self.candidates if c.is_involved(nart.camp, npc)]
        if candidates:
            return random.choice(candidates)

    def _is_good_npc(self, nart: GHNarrativeRequest, candidate):
        return (
            isinstance(candidate, gears.base.Character) and nart.camp.is_not_lancemate(candidate) and
            self._get_challenge_for_npc(nart, candidate)
        )

    def _win_the_mission(self, camp):
        self.elements["CHALLENGE"].advance(camp, 3)
        self.end_plot(camp)

    def _semi_win(self, camp):
        self.subplots["VACATION"].freeze_now(camp)
        self.elements["CHALLENGE"].advance(camp, 1)
        self.end_plot(camp)

    def NPC_offers(self, camp):
        mylist = list()

        mylist.append(Offer(
            "No, but I can't have {DISEASE}... [I_AM_STILL_STANDING]".format(**self.elements),
            ContextTag([context.CUSTOM]), subject=self, subject_start=True,
            data={"reply": "You don't look well. Have you been tested for {DISEASE}?".format(**self.elements)}
        ))

        ghdialogue.SkillBasedPartyReply(
            Offer(
                "[I_FEEL_BETTER_NOW] [THANKS_FOR_HELP]",
                ContextTag([context.CUSTOMREPLY,]), effect=self._win_the_mission,
                data={"reply": "I'm a medic; let me treat you."}, subject=self
            ), camp, mylist, gears.stats.Knowledge, gears.stats.Medicine, self.rank, gears.stats.DIFFICULTY_AVERAGE
        )

        mylist.append(Offer(
            "[MAYBE_YOU_ARE_RIGHT] I better not take any chances.".format(**self.elements),
            ContextTag([context.CUSTOMREPLY]), subject=self, effect=self._semi_win,
            data={"reply": "At least you should go home and have a rest."}
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
            # Create the mission seed. Turn the defeat_trigger off because we'll be handling that manually.
            self.mission_seed = missionbuilder.BuildAMissionSeed(
                nart.camp, "{NPC}'s Mission".format(**self.elements),
                self.elements["METROSCENE"], self.elements["MISSION_GATE"],
                allied_faction=npc.faction,
                enemy_faction=self.elements["ENEMY_FACTION"], rank=self.rank,
                objectives=[c.objective for c in my_dobjectives],
                one_chance=True,
                scenegen=sgen, architecture=archi, mission_grammar=mgram,
                cash_reward=120,
                on_win=self._win_the_mission, defeat_trigger_on=False
            )

            self.mission_active = False
            del self.candidates
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

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed and self.mission_active:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)


#   *************************************
#   ***  LOCATE_ENEMY_BASE_CHALLENGE  ***
#   *************************************

class ReconMissionToFindBase(Plot):
    LABEL = "CHALLENGE_PLOT"
    active = True
    scope = "METRO"
    RUMOR = Rumor(
        "{NPC} is looking for a pilot to fight {ENEMY_FACTION}",
        offer_msg="You can find {NPC} at {NPC_SCENE} if you want the mission.",
        offer_subject="{NPC} is looking for a pilot to fight {ENEMY_FACTION}", offer_subject_data="{NPC}'s mission",
        memo="{NPC} is looking for a pilot to fight {ENEMY_FACTION}.",
        prohibited_npcs=("NPC",), npc_is_prohibited_fun=plotutility.ProhibitFactionMembers("ENEMY_FACTION")
    )

    EXTRA_OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL)

    @classmethod
    def matches(cls, pstate: PlotState):
        return "METROSCENE" in pstate.elements and "MISSION_GATE" in pstate.elements

    def custom_init(self, nart: GHNarrativeRequest):
        self.candidates = [c for c in nart.challenges if c.chaltype == ghchallenges.LOCATE_ENEMY_BASE_CHALLENGE]
        if self.candidates:
            npc = self.seek_element(nart, "NPC", self._is_good_npc, lock=True, scope=self.elements["METROSCENE"])
            mychallenge = self.register_element("CHALLENGE", self._get_challenge_for_npc(nart, npc))
            self.register_element("NPC_SCENE", npc.scene)
            self.register_element("ENEMY_FACTION", mychallenge.key[0])
            self.register_element("BASE_NAME", mychallenge.data["base_name"])
            self.expiration = TimeAndChallengeExpiration(nart.camp, mychallenge, time_limit=5)

            sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])
            self.mission_seed = missionbuilder.BuildAMissionSeed(
                nart.camp, "{NPC}'s Mission".format(**self.elements),
                self.elements["METROSCENE"], self.elements["MISSION_GATE"],
                allied_faction=npc.faction,
                enemy_faction=self.elements["ENEMY_FACTION"], rank=self.rank,
                objectives=[missionbuilder.BAMO_LOCATE_ENEMY_FORCES,] + [random.choice(self.EXTRA_OBJECTIVES)],
                one_chance=True,
                scenegen=sgen, architecture=archi,
                cash_reward=120,
                on_win=self._win_the_mission
            )

            self.mission_active = False
            del self.candidates
            return True

    def _get_challenge_for_npc(self, nart, npc):
        candidates = [c for c in self.candidates if c.is_involved(nart.camp, npc)]
        if candidates:
            return random.choice(candidates)

    def _is_good_npc(self, nart: GHNarrativeRequest, candidate):
        return (
            isinstance(candidate, gears.base.Character) and nart.camp.is_not_lancemate(candidate) and
            self._get_challenge_for_npc(nart, candidate)
        )

    def _win_the_mission(self, camp: gears.GearHeadCampaign):
        comp = self.mission_seed.get_completion(True)
        pc = camp.do_skill_test(gears.stats.Perception, gears.stats.Scouting, self.rank)
        if pc:
            if pc.get_pilot() is camp.pc:
                pbge.alert("You trace the path taken by the enemy mecha, and find their base.")
            else:
                ghcutscene.SimpleMonologueDisplay("[I_HAVE_TRACKED_ENEMY_MECHA] We know where their {BASE_NAME} is.".format(**self.elements), pc)(camp)
            self.elements["CHALLENGE"].advance(camp, self.elements["CHALLENGE"].points_target)
        else:
            self.elements["CHALLENGE"].advance(camp, 1)
        self.end_plot(camp)

    def NPC_offers(self, camp):
        mylist = list()

        if not self.mission_active:
            mylist.append(Offer(
                "[LOOKING_FOR_CAVALIER] {ENEMY_FACTION} has been operating near {METROSCENE}, and this has to stop.".format(**self.elements),
                ContextTag([context.HELLO, context.MISSION])
            ))

            mylist.append(Offer(
                "Your job will be to find the {ENEMY_FACTION} forces and eliminate them. [DOYOUACCEPTMISSION]".format(**self.elements),
                ContextTag([context.MISSION]),
                subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "[IWillSendMissionDetails]; [GOODLUCK]",
                ContextTag([context.ACCEPT]), effect=self.activate_mission,
                subject=self
            ))

            ghdialogue.SkillBasedPartyReply(
                Offer(
                    "If you can do that, you could end their threat for good; [GOODLUCK]",
                    ContextTag([context.CUSTOMREPLY]), effect=self.activate_mission, subject=self,
                    data={"reply": "This could help us to locate {ENEMY_FACTION}'s {BASE_NAME}.".format(**self.elements)}
                ),
                camp, mylist, gears.stats.Knowledge, gears.stats.Scouting, self.rank, gears.stats.DIFFICULTY_AVERAGE,
                no_random=False
            )

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

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed and self.mission_active:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)


#   ************************
#   ***  MAKE_CHALLENGE  ***
#   ************************

class RecoverTheSupplies(Plot):
    LABEL = "CHALLENGE_PLOT"
    active = True
    scope = "METRO"
    RUMOR = Rumor(
        "{NPC} is looking for a pilot to recover stolen materials",
        offer_msg="The materials are needed to make {THING}. You can speak to {NPC} at {NPC_SCENE} if you want the mission.",
        memo="{NPC} is looking for a pilot to recover the materials needed for {THING}.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(cls, pstate: PlotState):
        return "METROSCENE" in pstate.elements and "MISSION_GATE" in pstate.elements

    def custom_init(self, nart: GHNarrativeRequest):
        self.candidates = [c for c in nart.challenges if c.chaltype == ghchallenges.MAKE_CHALLENGE]
        if self.candidates:
            npc = self.seek_element(nart, "NPC", self._is_good_npc, lock=True, scope=self.elements["METROSCENE"])
            mychallenge = self.register_element("CHALLENGE", self._get_challenge_for_npc(nart, npc))
            self.register_element("NPC_SCENE", npc.scene)
            self.register_element("THING", mychallenge.key[0])
            self.expiration = TimeAndChallengeExpiration(nart.camp, mychallenge, time_limit=5)

            mgram = missionbuilder.MissionGrammar(
                "recover the supplies needed for {THING}".format(**self.elements),
                "keep my rightfully looted cargo",
                "I recovered the supplies needed in {METROSCENE}".format(**self.elements),
                "you stole the cargo that I had just stolen",
                "you stole supplies that {METROSCENE} needed to make {THING}".format(**self.elements),
                "I ransomed the cargo that {METROSCENE} needed to make {THING} back to them for a nice profit".format(**self.elements)
            )

            sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])
            # Create the mission seed. Turn the defeat_trigger off because we'll be handling that manually.
            self.mission_seed = missionbuilder.BuildAMissionSeed(
                nart.camp, "{NPC}'s Mission".format(**self.elements),
                self.elements["METROSCENE"], self.elements["MISSION_GATE"],
                allied_faction=npc.faction,
                enemy_faction=plotutility.RandomBanditCircle(nart.camp), rank=self.rank,
                objectives=[missionbuilder.BAMO_DEFEAT_THE_BANDITS, missionbuilder.BAMO_RECOVER_CARGO],
                one_chance=True,
                scenegen=sgen, architecture=archi, mission_grammar=mgram,
                cash_reward=120,
                on_win=self._win_the_mission, defeat_trigger_on=False
            )

            self.mission_active = False
            del self.candidates
            return True

    def _get_challenge_for_npc(self, nart, npc):
        candidates = [c for c in self.candidates if c.is_involved(nart.camp, npc)]
        if candidates:
            return random.choice(candidates)

    def _is_good_npc(self, nart: GHNarrativeRequest, candidate):
        return (
            isinstance(candidate, gears.base.Character) and nart.camp.is_not_lancemate(candidate) and
            self._get_challenge_for_npc(nart, candidate)
        )

    def _win_the_mission(self, camp):
        comp = self.mission_seed.get_completion(True)
        self.elements["CHALLENGE"].advance(camp, max((comp-61)//15, 1))
        self.end_plot(camp)

    def NPC_offers(self, camp):
        mylist = list()

        if not self.mission_active:
            mylist.append(Offer(
                "[LOOKING_FOR_CAVALIER] Some bandits have captured the materials we need for {THING}.".format(**self.elements),
                ContextTag([context.HELLO, context.MISSION])
            ))

            mylist.append(Offer(
                "Your job will be to eliminate the bandits and recover the needed supplies. [DOYOUACCEPTMISSION]",
                ContextTag([context.MISSION]),
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

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed and self.mission_active:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)


#   ***************************
#   ***  MISSION_CHALLENGE  ***
#   ***************************

class BasicMissionChallenge(Plot):
    LABEL = "CHALLENGE_PLOT"
    active = True
    scope = "METRO"

    @classmethod
    def matches(cls, pstate: PlotState):
        return "METROSCENE" in pstate.elements and "MISSION_GATE" in pstate.elements

    def custom_init(self, nart: GHNarrativeRequest):
        self.candidates = [c for c in nart.challenges if c.chaltype == ghchallenges.MISSION_CHALLENGE]
        if self.candidates:
            #mychallenge = self.register_element("CHALLENGE", random.choice(self.candidates))
            npc = self.seek_element(nart, "NPC", self._is_good_npc, lock=True, scope=self.elements["METROSCENE"])
            self.elements["NPC_SCENE"] = npc.scene
            mychallenge = self.register_element("CHALLENGE", self._get_challenge_for_npc(nart, npc))
            self.register_element("NPC_SCENE", npc.scene)
            self.register_element("ENEMY_FACTION", mychallenge.key[0])
            self.expiration = TimeAndChallengeExpiration(nart.camp, mychallenge, time_limit=5)

            rumor_text = random.choice(mychallenge.data["challenge_rumors"])
            self.RUMOR = Rumor(
                rumor_text,
                offer_msg="{NPC} at {NPC_SCENE} is looking for someone to " + random.choice(mychallenge.data["challenge_summaries"])+". [IF_YOU_WANT_MISSION_GO_ASK_ABOUT_IT]",
                offer_subject=rumor_text,
                offer_subject_data=random.choice(mychallenge.data["challenge_subject"]),
                memo="{NPC} at {NPC_SCENE} is looking for someone to " + random.choice(mychallenge.data["challenge_summaries"])+".",
                prohibited_npcs=("NPC",),
                npc_is_prohibited_fun=plotutility.ProhibitFactionAndPCIfAllied("ENEMY_FACTION")
            )

            # Create the mission seed.
            self.mission_seed = mychallenge.data["mission_builder"](nart.camp, npc)

            self.mission_active = False
            del self.candidates
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

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        if not self.mission_active:
            mychallenge = self.elements["CHALLENGE"]
            mylist.append(Offer(
                "[LOOKING_FOR_CAVALIER] {}".format(random.choice(mychallenge.data["mission_intros"])),
                ContextTag([context.HELLO, context.MISSION])
            ))

            mylist.append(Offer(
                "[i_want_you_to] {}. [DOYOUACCEPTMISSION]".format(random.choice(mychallenge.data["challenge_objectives"])),
                ContextTag([context.MISSION]),
                subject=self, subject_start=True
            ))

            if not (mychallenge.key[0] and camp.is_favorable_to_pc(mychallenge.key[0])):
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

    def t_UPDATE(self,camp):
        if self.mission_seed.ended:
            self.end_plot(camp)

    def activate_mission(self,camp):
        self.mission_active = True
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])
        self.elements["CHALLENGE"].memo_active = True

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed and self.mission_active:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)


#   ******************************
#   ***  RAISE_ARMY_CHALLENGE  ***
#   ******************************

class RaiseArmyChallenge(Plot):
    LABEL = "CHALLENGE_PLOT"
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        "{NPC} has been trying to acquire some mecha for the war effort",
        offer_msg="In addition to soldiers and pilots, we're also going to need machines. {NPC} is working hard at {NPC_SCENE} to get as many mecha in battle condition as we can get.",
        memo="{NPC} needs help obtaining mecha for the war effort.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(cls, pstate: PlotState):
        return "METROSCENE" in pstate.elements

    def custom_init(self, nart: GHNarrativeRequest):
        self.candidates = [c for c in nart.challenges if c.chaltype == ghchallenges.RAISE_ARMY_CHALLENGE]
        if self.candidates:
            npc = self.seek_element(nart, "NPC", self._is_good_npc, lock=True, scope=self.elements["METROSCENE"])
            mychallenge = self.register_element("CHALLENGE", self._get_challenge_for_npc(nart, npc))
            self.register_element("NPC_SCENE", npc.scene)

            self.expiration = TimeAndChallengeExpiration(nart.camp, mychallenge, time_limit=5)
            del self.candidates

            return True

    def _get_challenge_for_npc(self, nart, npc):
        candidates = [c for c in self.candidates if c.is_involved(nart.camp, npc)]
        if candidates:
            return random.choice(candidates)

    def _is_good_npc(self, nart: GHNarrativeRequest, candidate):
        return (
            isinstance(candidate, gears.base.Character) and nart.camp.is_not_lancemate(candidate) and
            candidate.job and
            {gears.tags.Craftsperson, gears.tags.Merchant, gears.tags.CorporateWorker}.intersection(candidate.job.tags)
            and self._get_challenge_for_npc(nart, candidate)
        )

    def _win_the_mission(self, camp):
        self.elements["CHALLENGE"].advance(camp, 3)
        self.end_plot(camp)

    def NPC_offers(self, camp):
        mylist = list()
        mychallenge: pbge.challenges.Challenge = self.elements["CHALLENGE"]

        if "threat" in mychallenge.data:
            mylist.append(Offer(
                "[HELLO] I need to obtain more mecha for the battle against {}.".format(mychallenge.data["threat"]),
                ContextTag([context.HELLO,])
            ))
        else:
            mylist.append(Offer(
                "[HELLO] I need to obtain more mecha for the war effort.",
                ContextTag([context.HELLO,])
            ))

        ghdialogue.SkillBasedPartyReply(
            Offer(
                "[THANKS_FOR_HELP] With your guidance we've been able to strip one wreck for the parts to get two more running again.",
                ContextTag([context.CUSTOM,]), effect=self._win_the_mission, subject="obtain more mecha",
                data={"reply": "I can use my repair knowledge to help you get some of these wrecks back into working order."}
            ), camp, mylist, gears.stats.Knowledge, gears.stats.Repair, self.rank, gears.stats.DIFFICULTY_HARD
        )

        ghdialogue.SkillBasedPartyReply(
            Offer(
                "[THANKS_FOR_HELP] The improvements you've suggested should produce immediate savings in both time and resources.",
                ContextTag([context.CUSTOM,]), effect=self._win_the_mission, subject="obtain more mecha",
                data={"reply": "My scientific knowledge might be able to increase your mecha production capacity."}
            ), camp, mylist, gears.stats.Knowledge, gears.stats.Science, self.rank, gears.stats.DIFFICULTY_AVERAGE
        )

        if self._rumor_memo_delivered:
            mylist.append(Offer(
                "Yes, I've been hard at work to obtain more mecha for {}. We have a ton of salvage, but nothing that will put up a fight.".format(mychallenge.key[0]),
                ContextTag([context.INFO,]), data={"subject": "the war effort"}
            ))


        return mylist
