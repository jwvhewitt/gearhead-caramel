# We have plots for every occassion- random events to spice up your metroscenes.

from pbge.plots import Plot, PlotState, Rumor, TimeExpiration
from pbge.memos import Memo
import game
import gears
import pbge
import pygame
import random
from game import teams, ghdialogue
from game.content import gharchitecture, ghterrain, ghwaypoints, plotutility, ghcutscene
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed
from . import missionbuilder, rwme_objectives, campfeatures
from .lancemates import get_hire_cost, LMSkillsSelfIntro

RANDOM_PLOT_RECHARGE = "RANDOM_PLOT_RECHARGE"


def npc_is_ready_for_plot(npc, camp: gears.GearHeadCampaign):
    if isinstance(npc, gears.base.Character) and npc not in camp.party:
        mydata = camp.get_campdata(npc)
        return mydata.get(RANDOM_PLOT_RECHARGE, 0) <= camp.day


def set_npc_recharge(npc, camp, time=10):
    mydata = camp.get_campdata(npc)
    mydata[RANDOM_PLOT_RECHARGE] = camp.day + time


class CollectMedicinalHerbs(Plot):
    LABEL = "RANDOM_PLOT"
    active = True
    scope = "METRO"
    RUMOR = Rumor(
        "{NPC} is looking for an explorer to go collect medicinal herbs",
        offer_msg="If you're interested in taking the mission, speak to {NPC} at {NPC_SCENE}.",
        memo="{NPC} is looking for an explorer to collect medicinal herbs.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(cls, pstate):
        return pstate.elements["METROSCENE"].attributes.intersection(
            [gears.personality.DeadZone, gears.personality.GreenZone])

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, lock=True, scope=self.elements["METROSCENE"])
        self.register_element("NPC_SCENE", npc.scene)

        self.expiration = TimeExpiration(nart.camp)
        self.elements["HERB"] = plotutility.random_plant_name()

        # Create the mission seed.
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            nart.camp, "Gather {HERB} for {NPC}".format(**self.elements),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            allied_faction=npc.faction, rank=self.rank,
            objectives=(missionbuilder.BAMOP_FIND_HERBS, missionbuilder.BAMOP_DUNGEONLIKE),
            one_chance=True, scale=gears.scale.HumanScale,
            architecture=gharchitecture.HumanScaleForest(), cash_reward=100,
            custom_elements={
                "SCENE_ATTRIBUTES": (gears.tags.SCENE_OUTDOORS, gears.tags.SCENE_FOREST),
                missionbuilder.BAMEP_MONSTER_TYPE: ("ANIMAL", "FOREST", "GREEN", "BRIGHT")
            },
            combat_music="Komiku_-_07_-_Run_against_the_universe.ogg", exploration_music="airtone_-_reCreation.ogg"
        )

        set_npc_recharge(npc, nart.camp, time=10)
        self.mission_active = False
        return True

    def _is_good_npc(self, nart, candidate):
        if npc_is_ready_for_plot(candidate, nart.camp) and nart.camp.is_not_lancemate(candidate):
            job_ok = candidate.job and gears.tags.Medic in candidate.job.tags
            scene_ok = gears.tags.SCENE_PUBLIC in candidate.scene.attributes
            return job_ok and scene_ok

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        if not self.mission_active:
            mylist.append(Offer(
                "[LOOKING_FOR_CAVALIER] I need to gather some {HERB} to synthesize medicine.".format(**self.elements),
                ContextTag([context.HELLO, ]),
            ))

            if self._rumor_memo_delivered:
                ghdialogue.SkillBasedPartyReply(Offer(
                    "[GOOD] The sooner you can get the herbs to me, the sooner I can start brewing the medicine.",
                    context=ContextTag([context.CUSTOM]), effect=self.activate_mission,
                    dead_end=True, data={"reply": "I know where to find {HERB}.".format(**self.elements)}
                ), camp, mylist, gears.stats.Knowledge, gears.stats.Wildcraft, self.rank)

                if camp.do_skill_test(gears.stats.Charm, gears.stats.Negotiation, self.rank,
                                      gears.stats.DIFFICULTY_HARD):
                    mylist.append(Offer(
                        "Let me give you a detailed description of the plant I need, {HERB}. You should be able to find it in a small but thriving forest near town. Unfortunately, the forest is also home to a lot of dangerous wildlife...".format(
                            **self.elements),
                        ContextTag([context.CUSTOM]), effect=self.activate_mission,
                        dead_end=True, data={"reply": "[HELLO:MISSION]"}
                    ))
                else:
                    mylist.append(Offer(
                        "Sorry, but this mission requires a specialist who knows how to harvest wild plants. [GOODBYE]",
                        ContextTag([context.CUSTOM]), effect=self.end_plot,
                        dead_end=True, data={"reply": "[HELLO:MISSION]"}
                    ))

            else:
                ghdialogue.SkillBasedPartyReply(Offer(
                    "[THATS_GOOD] We really need this medicine, and that herb is the only way to produce it.",
                    context=ContextTag([context.CUSTOM]), effect=self.activate_mission, subject=self.elements["HERB"],
                    dead_end=True, data={"reply": "I know exactly where to find some.".format(**self.elements)}
                ), camp, mylist, gears.stats.Knowledge, gears.stats.Wildcraft, self.rank)

                if camp.do_skill_test(gears.stats.Charm, gears.stats.Negotiation, self.rank,
                                      gears.stats.DIFFICULTY_HARD):
                    mylist.append(Offer(
                        "I'll send the field identification page for {HERB} to your phone. It grows in a small but thriving forest near town. Unfortunately, the forest is also home to a lot of dangerous animals...".format(
                            **self.elements),
                        ContextTag([context.CUSTOM]), effect=self.activate_mission, subject=self.elements["HERB"],
                        dead_end=True, data={"reply": "[ICANDOTHAT]"}
                    ))
                else:
                    mylist.append(Offer(
                        "No offense, but I'm not sure you're qualified for this job. What I really need is a specialist in gathering wild plants. [GOODBYE]",
                        ContextTag([context.CUSTOM]), effect=self.end_plot, subject=self.elements["HERB"],
                        dead_end=True, data={"reply": "[ICANDOTHAT]"}
                    ))

        return mylist

    def t_UPDATE(self, camp):
        if self.mission_seed.ended:
            self.end_plot(camp)

    def activate_mission(self, camp):
        self.mission_active = True
        self.expiration = None
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed and self.mission_active:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)


class Cookies(Plot):
    # A revival of the old "FortuneCookies" plot.
    LABEL = "RANDOM_PLOT"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, must_find=True, lock=True,
                                scope=self.elements["METROSCENE"])
        self.elements["NPC_SCENE"] = npc.scene
        self.expiration = TimeExpiration(nart.camp, time_limit=5)
        set_npc_recharge(npc, nart.camp, 5)
        return True

    def _is_good_npc(self, nart, candidate):
        if npc_is_ready_for_plot(candidate, nart.camp):
            return gears.tags.SCENE_PUBLIC in candidate.scene.attributes

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        npc = self.elements["NPC"]

        mylist.append(Offer(
            "[HELLO] [chat_lead_in] [Fortune_cookie].",
            ContextTag([context.HELLO]), effect=self.end_plot
        ))

        return mylist

    def _get_dialogue_grammar(self, npc, camp):
        # The secret private function that returns custom grammar.
        if npc is not self.elements["NPC"]:
            return {"[News]": ["{NPC} likes cookies".format(**self.elements)]}


class Entropy(Plot):
    # Nothing is happening. I am just wasting a plot slot so the player can't stay in the same place and milk plots
    # forever.
    LABEL = "RANDOM_PLOT"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        self.expiration = TimeExpiration(nart.camp, time_limit=10)
        return True

    def t_START(self, camp: gears.GearHeadCampaign):
        # Get rid of the entropy if there's an active challenge about.
        if random.randint(1,5) == 3 and camp.get_active_challenges():
            self.end_plot(camp)


class LoadChallengePlot(Plot):
    LABEL = "RANDOM_PLOT"
    active = False
    scope = None
    COMMON = True

    def custom_init(self, nart):
        self.add_sub_plot(nart, "CHALLENGE_PLOT")
        return True


class MechaMissionForCity(Plot):
    LABEL = "RANDOM_PLOT"
    active = True
    scope = "METRO"
    RUMOR = Rumor(
        "{NPC} is looking for a pilot to fight {ENEMY_FACTION} for {METROSCENE}",
        offer_msg="If you're interested in taking the mission, speak to {NPC} at {NPC_SCENE}.",
        memo="{NPC} is looking for a pilot to fight {ENEMY_FACTION}.",
        prohibited_npcs=("NPC",)
    )

    OBJECTIVES = (
        missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_DEFEAT_COMMANDER,
        missionbuilder.BAMO_AID_ALLIED_FORCES, missionbuilder.BAMO_EXTRACT_ALLIED_FORCES,
        missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL, missionbuilder.BAMO_CAPTURE_BUILDINGS
    )

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, lock=True, scope=self.elements["METROSCENE"])
        self.register_element("NPC_SCENE", npc.scene)
        ef = self.register_element("ENEMY_FACTION", nart.camp.get_enemy_faction(self.elements["METROSCENE"]))
        if ef:
            self.expiration = TimeExpiration(nart.camp)

            sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])
            # Create the mission seed. Turn the defeat_trigger off because we'll be handling that manually.
            self.mission_seed = missionbuilder.BuildAMissionSeed(
                nart.camp, "{NPC}'s Mission".format(**self.elements),
                self.elements["METROSCENE"], self.elements["MISSION_GATE"],
                allied_faction=npc.faction,
                enemy_faction=self.elements["ENEMY_FACTION"], rank=self.rank,
                objectives=random.sample(self.OBJECTIVES, 2),
                one_chance=True,
                scenegen=sgen, architecture=archi,
                cash_reward=100
            )

            set_npc_recharge(npc, nart.camp, time=10)
            self.mission_active = False
            return True

    def _is_good_npc(self, nart, candidate):
        if npc_is_ready_for_plot(candidate, nart.camp) and nart.camp.is_not_lancemate(candidate):
            faction_ok = candidate.faction and nart.camp.are_faction_allies(candidate, self.elements["METROSCENE"])
            scene_ok = gears.tags.SCENE_PUBLIC in candidate.scene.attributes
            return faction_ok and scene_ok

    def NPC_offers(self, camp):
        mylist = list()

        if not self.mission_active:
            mylist.append(Offer(
                "[LOOKING_FOR_CAVALIER] [MechaMissionVsEnemyFaction].",
                ContextTag([context.HELLO, context.MISSION]), data={"enemy_faction": self.elements["ENEMY_FACTION"]}
            ))

            mylist.append(Offer(
                "Mecha from {ENEMY_FACTION} have been operating near {METROSCENE}. [DOYOUACCEPTMISSION]".format(
                    **self.elements),
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

    def t_UPDATE(self, camp):
        if self.mission_seed.ended:
            self.end_plot(camp)

    def activate_mission(self, camp):
        self.mission_active = True
        self.expiration = None
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed and self.mission_active:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)


class MercenaryPassingThrough(Plot):
    LABEL = "RANDOM_PLOT"
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        "{NPC} is a mercenary pilot just passing through {METROSCENE}",
        offer_msg="If you need a new lancemate, you can find {NPC.gender.object_pronoun} at {NPC_SCENE}.",
        memo="{NPC} is a mercenary pilot who can be found at {NPC_SCENE}.",
        prohibited_npcs=("NPC",)
    )

    def custom_init(self, nart):
        npc = gears.selector.random_character(max(self.rank + random.randint(-10,10), 10),
                                              camp=nart.camp, can_cyberize=True,
                                              job=gears.jobs.ALL_JOBS["Mercenary"])
        if random.randint(1,23) == 5:
            npc.statline[random.choice(gears.stats.NONCOMBAT_SKILLS)] += random.randint(1,5)
        self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"],
                          backup_seek_func=self._is_okay_scene)
        self.register_element("NPC", npc, dident="NPC_SCENE", lock=True)
        self.expiration = TimeExpiration(nart.camp, time_limit=5)
        self.call_on_end.append(self._delete_mercenary)
        return True

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
                and gears.tags.SCENE_MEETING in candidate.attributes)

    def _is_okay_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def _delete_mercenary(self, camp):
        npc = self.elements["NPC"]
        if not (npc.relationship and gears.relationships.RT_LANCEMATE in npc.relationship.tags):
            npc.container.remove(npc)

    def NPC_offers(self, camp):
        mylist = list()
        npc = self.elements["NPC"]
        self.hire_cost = get_hire_cost(camp, npc)
        if gears.relationships.RT_LANCEMATE not in npc.relationship.tags:
            if camp.can_add_lancemate():
                mylist.append(Offer("My signing fee is ${:,}. [DOYOUACCEPTMYOFFER]".format(self.hire_cost),
                                    context=ContextTag((context.PROPOSAL, context.JOIN)),
                                    data={"subject": "joining my lance"},
                                    subject=self, subject_start=True,
                                    ))
                mylist.append(Offer("[DENY_JOIN] [GOODBYE]",
                                    context=ContextTag((context.DENY, context.JOIN)), subject=self
                                    ))
                if camp.credits >= self.hire_cost:
                    mylist.append(Offer("[THANKS_FOR_CHOOSING_ME] [LETSGO]",
                                        context=ContextTag((context.ACCEPT, context.JOIN)), subject=self,
                                        effect=self._pay_to_join
                                        ))
                mylist.append(Offer(
                    "[HELLO] [WAITINGFORMISSION]", context=ContextTag((context.HELLO,))
                ))
            mylist.append(LMSkillsSelfIntro(npc))

        return mylist

    def _pay_to_join(self, camp):
        camp.credits -= self.hire_cost
        self._join_lance(camp)

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        effect = game.content.plotutility.AutoJoiner(npc)
        effect(camp)
        self.end_plot(camp)


class OddJobsBiotechnology(Plot):
    # Help someone with your biotechnological skills.
    LABEL = "RANDOM_PLOT"
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        "{NPC} has been trying to analyze a weird chemical",
        offer_msg="What {NPC} really needs is an expert in biotechnology. If you know anything about that subject, go to {NPC_SCENE} and talk to {NPC.gender.object_pronoun} about it.",
        memo="{NPC} has been trying to analyze a chemical but needs the assistance of a biotechnology expert.",
        prohibited_npcs=("NPC",)
    )

    MATERIAL_TYPES = ("fluid", "ooze", "pathogen", "solid", "toxin", "crystal")

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, must_find=True, lock=True,
                                scope=self.elements["METROSCENE"])
        self.elements["NPC_SCENE"] = npc.scene
        self.reward = self.register_element("_REWARD", gears.selector.calc_mission_reward(self.rank, 75))
        self.elements["MATERIAL"] = random.choice(self.MATERIAL_TYPES)
        self.expiration = TimeExpiration(nart.camp, time_limit=5)
        set_npc_recharge(npc, nart.camp)
        return True

    def _is_good_npc(self, nart, candidate):
        if npc_is_ready_for_plot(candidate, nart.camp):
            job_ok = candidate.job and candidate.job.tags.intersection([gears.tags.Medic, gears.tags.Academic])
            scene_ok = gears.tags.SCENE_PUBLIC in candidate.scene.attributes
            return job_ok and scene_ok

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        npc: gears.base.Character = self.elements["NPC"]

        if camp.party_has_skill(gears.stats.Biotechnology):
            if self._rumor_memo_delivered:
                mylist.append(Offer(
                    "[You_heard_right]. We've discovered samples of an unknown {MATERIAL} but have been unable to determine its structure. Would you mind providing an expert opinion about it?".format(
                        **self.elements),
                    ContextTag([context.CUSTOM]), effect=self._attempt_analysis, dead_end=True,
                    data={"reply": "I hear you need help with some biochem analysis."}
                ))
            elif npc.get_reaction_score(camp.pc, camp) > 20:
                mylist.append(Offer(
                    "[HELLO] I've been trying to analyze an unknown {MATERIAL}, but I suspect it's of biotechnological origin. Would you be willing to examine it for me?".format(
                        **self.elements),
                    ContextTag([context.HELLO]), subject=self, subject_start=True
                ))

                mylist.append(Offer(
                    "[THANK_YOU] You're free to use any of the equipment I have.".format(**self.elements),
                    ContextTag([context.CUSTOM]), subject=self, effect=self._attempt_analysis,
                    data={"reply": "[MISSION:ACCEPT]".format(**self.elements)}, dead_end=True
                ))

        return mylist

    def _attempt_analysis(self, camp: gears.GearHeadCampaign):
        npc = self.elements["NPC"]
        pbge.alert("You begin to analyze {NPC}'s {MATERIAL}.".format(**self.elements))

        truey_or_fake = random.choice([True, True, True, False])

        pbge.my_state.view.play_anims(gears.geffects.SearchAnim(pos=camp.pc.pos))

        skroll = camp.make_skill_roll(gears.stats.Knowledge, gears.stats.Biotechnology)
        if skroll > gears.stats.get_skill_target(self.rank, gears.stats.DIFFICULTY_AVERAGE):
            if truey_or_fake:
                pbge.alert(
                    "You determine that the {MATERIAL} is definitely biotechnological; it probably originates from PreZero times.".format(
                        **self.elements))
                ghcutscene.SimpleMonologueDisplay("[THATS_INTERESTING] Here is a reward for helping with my research.",
                                                  npc)(camp)
            else:
                pbge.alert(
                    "You determine that the {MATERIAL} is of natural origin. {NPC} probably just made some measurement errors.".format(
                        **self.elements))
                ghcutscene.SimpleMonologueDisplay(
                    "Well that's disappointing. Still, here's a reward for helping with my research.", npc)(camp)
            camp.credits += self.reward
            pbge.BasicNotification("You earn ${:,}.".format(self.reward))
            relationship = camp.get_relationship(npc)
            relationship.reaction_mod += random.randint(5, 10)
            camp.dole_xp(25)

        else:
            pbge.alert(
                "After much analysis, you conclude that you don't know what this {MATERIAL} is or where it came from.".format(
                    **self.elements))
            ghcutscene.SimpleMonologueDisplay(
                "Thanks for trying, at least. I guess I'm going to have to figure this out on my own.", npc)(camp)
            relationship = camp.get_relationship(npc)
            relationship.reaction_mod -= random.randint(1, 4)
            camp.renown -= random.randint(1, 6)
            camp.dole_xp(25)

        self.end_plot(camp)


class OddJobsPerformance(Plot):
    # Use your performance skill to earn some money.
    LABEL = "RANDOM_PLOT"
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        "{NPC} is a looking for a performer to play at {NPC_SCENE}",
        offer_msg="If you know how to handle a [instrument], you can probably earn some money at {NPC_SCENE}. Go talk to {NPC} about it.",
        memo="{NPC} is a looking for a performer to play music at {NPC_SCENE}.",
        prohibited_npcs=("NPC",)
    )

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, must_find=True, lock=True,
                                scope=self.elements["METROSCENE"])
        self.elements["NPC_SCENE"] = npc.scene
        self.reward = self.register_element("_REWARD", gears.selector.calc_mission_reward(self.rank, 90))
        self.expiration = TimeExpiration(nart.camp, time_limit=5)
        set_npc_recharge(npc, nart.camp)
        return True

    def _is_good_npc(self, nart, candidate):
        if npc_is_ready_for_plot(candidate, nart.camp):
            job_ok = str(candidate.job) in ("Innkeeper", "Bartender", "Aristo", "Dancer")
            scene_ok = (gears.tags.SCENE_PUBLIC in candidate.scene.attributes and
                        candidate.scene.attributes.intersection({gears.tags.SCENE_MEETING, gears.tags.SCENE_CULTURE}))
            return job_ok and scene_ok

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        npc = self.elements["NPC"]

        if self._rumor_memo_delivered and camp.party_has_skill(gears.stats.Performance):
            mylist.append(Offer(
                "[You_heard_right]. I'm looking for someone to play music at {NPC_SCENE}; pay is ${_REWARD:,}.".format(
                    **self.elements),
                ContextTag([context.CUSTOM]), subject=npc, subject_start=True,
                data={"reply": "I hear you're looking for a musician."}
            ))

        elif camp.pc.has_badge("Pop Star"):
            mylist.append(Offer(
                "[HELLO] I'm looking for a musician to play at {NPC_SCENE}; [You_have_the_needed_skills]. Pay is ${_REWARD:,}.".format(
                    **self.elements),
                ContextTag([context.HELLO]), subject=self, subject_start=True, effect=self._get_rumor
            ))

            if camp.party_has_skill(gears.stats.Performance):
                mylist.append(Offer(
                    "[THATS_GOOD] You can get started right away.".format(**self.elements),
                    ContextTag([context.CUSTOM]), subject=self, effect=self._play_concert,
                    data={"reply": "[MISSION:ACCEPT]"}, dead_end=True
                ))

            mylist.append(Offer(
                "Too bad. I'll have to find someone else for the job.".format(**self.elements),
                ContextTag([context.CUSTOMREPLY]), subject=self, dead_end=True,
                data={"reply": "[MISSION:DENY]"}
            ))


        else:
            mylist.append(Offer(
                "[HELLO] I've been looking for a musician to play a gig here.".format(**self.elements),
                ContextTag([context.HELLO]), subject=npc, subject_start=True, effect=self._get_rumor
            ))

            if camp.party_has_skill(gears.stats.Performance):
                mylist.append(Offer(
                    "I just need someone who can carry a tune and get some attention. Pay is ${_REWARD:,}.".format(
                        **self.elements),
                    ContextTag([context.CUSTOM]), subject=npc,
                    data={"reply": "Could you tell me a bit more about this gig?"}
                ))

        if camp.party_has_skill(gears.stats.Performance):
            mylist.append(Offer(
                "[THATS_GOOD] Remember, the goal is to attract an audience, so do your best!".format(**self.elements),
                ContextTag([context.CUSTOMREPLY]), subject=npc, effect=self._play_concert, dead_end=True,
                data={"reply": "[MISSION:ACCEPT]"}
            ))

        mylist.append(Offer(
            "Too bad. I'll have to find someone else for the job.".format(**self.elements),
            ContextTag([context.CUSTOMREPLY]), subject=npc, dead_end=True,
            data={"reply": "[MISSION:DENY]"}
        ))

        return mylist

    def _get_generic_offers(self, npc: gears.base.Character, camp):
        """Get any offers that could apply to non-element NPCs."""
        mylist = list()
        if self._rumor_memo_delivered and gears.stats.Performance in npc.statline and npc is not self.elements["NPC"]:
            mylist.append(Offer(
                "Thanks for letting me know; I could really use the job.".format(**self.elements),
                ContextTag([context.CUSTOM]), effect=plotutility.EffectCallPlusNPC(self._suggest_job_to_npc, npc),
                data={"reply": "{NPC} is looking for someone to play a gig at {NPC_SCENE}.".format(**self.elements)}
            ))

        return mylist

    def _suggest_job_to_npc(self, camp: gears.GearHeadCampaign, npc: gears.base.Character):
        relationship = camp.get_relationship(npc)
        relationship.reaction_mod += random.randint(1, 10)
        self.end_plot(camp)

    def _get_rumor(self, camp):
        self._rumor_memo_delivered = True
        self.memo = Memo("{NPC} is a looking for a performer to play music at {NPC_SCENE}.".format(**self.elements),
                         self.elements["NPC_SCENE"])
        self.RUMOR = None

    EXCELLENT_CONCERT = (
        "You rock. You roll. You play the type of set that people will be talking about for years. {NPC_SCENE} quickly fills to capacity with adoring fans.",
        "As soon as you begin, you feel the spirit of music course through your veins. The performance is flawless. {NPC_SCENE} fills with patrons eager to hear your song.",
        "From the first note to the last, you play one of the greatest concerts of your life. You don't even notice the people crowding into {NPC_SCENE} because you are lost in the music."
    )

    AVERAGE_CONCERT = (
        "You play a selection of old favorites and new songs that you've been working on. Bit by bit, {NPC_SCENE} fills with patrons drawn by your music.",
        "You begin to play. At first, not many people show up. Soon though, as you find the rhythm, {NPC_SCENE} fills with fans eager to hear your song.",
        "You play music for {NPC}. Soon, people begin to arrive to hear your performance. {NPC_SCENE} fills with the sounds of joy and togetherness."
    )

    FAIL_CONCERT = (
        "You try to play for {NPC}. The inspiration never comes. Neither does the audience.",
        "You start playing your concert, but something is off. You can't find the rhythm. Nobody comes to listen.",
        "Sometimes, things just don't go right. This is one of those times. Your performance is an abject failure."
    )

    def _play_concert(self, camp: gears.GearHeadCampaign):
        npc = self.elements["NPC"]
        pbge.alert("You begin to play a concert at {NPC_SCENE}.".format(**self.elements))

        performers = [pc for pc in camp.get_active_party() if pc.get_stat(gears.stats.Performance) > 0]
        pbge.my_state.view.play_anims(*[gears.geffects.PerformanceAnim(pos=pc.pos) for pc in performers])

        skroll = camp.make_skill_roll(gears.stats.Charm, gears.stats.Performance)
        if skroll > gears.stats.get_skill_target(self.rank, gears.stats.DIFFICULTY_LEGENDARY):
            pbge.alert(random.choice(self.EXCELLENT_CONCERT).format(**self.elements))
            ghcutscene.SimpleMonologueDisplay(
                "[THAT_WAS_INCREDIBLE] Here, you attracted so many people that I can pay twice what we agreed to.",
                npc)(camp)
            camp.credits += self.reward * 2
            pbge.BasicNotification("You earn ${:,}.".format(self.reward * 2))
            relationship = camp.get_relationship(npc)
            relationship.reaction_mod += random.randint(5, 10)
            self.elements["METRO"].local_reputation += random.randint(1, 6)
            camp.dole_xp(50)

        elif skroll > gears.stats.get_skill_target(self.rank, gears.stats.DIFFICULTY_AVERAGE):
            pbge.alert(random.choice(self.AVERAGE_CONCERT).format(**self.elements))
            ghcutscene.SimpleMonologueDisplay("[GOOD_JOB] Here's the pay we agreed to.", npc)(camp)
            camp.credits += self.reward
            pbge.BasicNotification("You earn ${:,}.".format(self.reward))
            relationship = camp.get_relationship(npc)
            relationship.reaction_mod += random.randint(1, 8)
            camp.dole_xp(50)

        else:
            pbge.alert(random.choice(self.FAIL_CONCERT).format(**self.elements))
            ghcutscene.SimpleMonologueDisplay(
                "[THAT_WAS_THE_WORST] I think you actually drove away some people... You have failed at this job.",
                npc)(camp)
            relationship = camp.get_relationship(npc)
            relationship.reaction_mod -= random.randint(1, 10)
            for pc in camp.get_lancemates():
                relationship = camp.get_relationship(pc)
                relationship.reaction_mod -= random.randint(1, 6)
            camp.renown -= random.randint(1, 4)
            camp.dole_xp(50)

        self.end_plot(camp)


class OddJobsRepair(Plot):
    # Use your repair skill to earn some money.
    LABEL = "RANDOM_PLOT"
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        "{NPC} has broken {NPC.gender.possessive_determiner} {DEVICE} again",
        offer_msg="If you know anything about repair, maybe you can help. Talk to {NPC} at {NPC_SCENE} about it.",
        memo="{NPC} has broken {NPC.gender.possessive_determiner} {DEVICE}. This is apparently a common occurrence.",
        prohibited_npcs=("NPC",)
    )

    DEVICES = ("mobile phone", "dataslate", "watch", "headset", "fitness tracker", "comset", "telray", "laserpants",
               "thruport", "phone", "netphone")

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, must_find=True, lock=True,
                                scope=self.elements["METROSCENE"])
        self.elements["DEVICE"] = random.choice(self.DEVICES)
        self.elements["NPC_SCENE"] = npc.scene
        self.reward = self.register_element("_REWARD", gears.selector.calc_mission_reward(self.rank, 25))
        self.expiration = TimeExpiration(nart.camp, time_limit=5)
        set_npc_recharge(npc, nart.camp)
        return True

    def _is_good_npc(self, nart, candidate):
        if npc_is_ready_for_plot(candidate, nart.camp):
            skills_ok = candidate.get_stat(gears.stats.Craft) < 10 and gears.stats.Repair not in candidate.statline
            scene_ok = gears.tags.SCENE_PUBLIC in candidate.scene.attributes
            return skills_ok and scene_ok

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        npc = self.elements["NPC"]

        if self._rumor_memo_delivered and camp.party_has_skill(gears.stats.Repair):
            mylist.append(Offer(
                "[You_heard_right]. Would you mind looking at it for me? I can pay ${_REWARD:,} if you fix it.".format(
                    **self.elements),
                ContextTag([context.CUSTOM]), subject=npc, subject_start=True, effect=self._attempt_repair,
                data={"reply": "I hear you broke your {DEVICE}.".format(**self.elements)}
            ))

        return mylist

    def _attempt_repair(self, camp: gears.GearHeadCampaign):
        npc = self.elements["NPC"]
        pbge.alert("You attempt to repair {NPC}'s {DEVICE}.".format(**self.elements))

        pbge.my_state.view.play_anims(gears.geffects.RepairAnim(pos=npc.pos))

        skroll = camp.make_skill_roll(gears.stats.Craft, gears.stats.Repair)
        if skroll > gears.stats.get_skill_target(self.rank, gears.stats.DIFFICULTY_AVERAGE):
            pbge.alert("You fix it!")
            ghcutscene.SimpleMonologueDisplay("[THANKS_FOR_HELP] Here's a reward for you.", npc)(camp)
            camp.credits += self.reward
            pbge.BasicNotification("You earn ${:,}.".format(self.reward))
            relationship = camp.get_relationship(npc)
            relationship.reaction_mod += random.randint(1, 4)
            camp.dole_xp(25)

        else:
            pbge.my_state.view.play_anims(gears.geffects.BigBoom(pos=npc.pos))
            pbge.alert("Your attempts at repair destroy the {DEVICE} completely.".format(**self.elements))
            ghcutscene.SimpleMonologueDisplay("[THATSUCKS] I guess I'm going to have to buy a new one...", npc)(camp)
            relationship = camp.get_relationship(npc)
            relationship.reaction_mod -= random.randint(1, 4)
            self.elements["METRO"].local_reputation -= random.randint(1, 4)
            camp.renown -= 1
            camp.dole_xp(50)

        self.end_plot(camp)
