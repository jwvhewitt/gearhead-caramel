# Character development plots for lancemates.
import game.content
from pbge.plots import Plot, PlotState
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
from gears import relationships
import pbge
import random
from game.content import gharchitecture, ghwaypoints, plotutility, ghterrain, backstory, ghcutscene, dungeonmaker
from . import missionbuilder, dd_customobjectives, lancedev_objectives


#  Required elements: METRO, METROSCENE, MISSION_GATE

class LMPlot(Plot):
    LANCEDEV_PLOT = True
    UNIQUE = True

    # Contains convenience methods for lancemates.
    def npc_is_ready_for_lancedev(self, camp, npc):
        return (isinstance(npc, gears.base.Character) and npc in camp.party and npc.relationship
                and npc.relationship.can_do_development())

    def t_START(self, camp):
        npc = self.elements["NPC"]
        if self.LANCEDEV_PLOT and (npc.is_destroyed() or npc not in camp.party):
            self.end_plot(camp)

    def proper_end_plot(self, camp, improve_react=True):
        self.elements["NPC"].relationship.development_plots += 1
        if improve_react:
            self.elements["NPC"].relationship.reaction_mod += random.randint(1, 10)
        self.end_plot(camp)

    def proper_non_end(self, camp, improve_react=True):
        # This plot is not ending, but it's entering a sort of torpor phase where we don't want it interfering
        # with other LANCEDEV plots. For instance: if a plot adds a permanent new location to the world, you
        # might not want to end the plot but you will want to unlock the NPC and whatever else.
        self.elements["NPC"].relationship.development_plots += 1
        self.LANCEDEV_PLOT = False
        if improve_react:
            self.elements["NPC"].relationship.reaction_mod += random.randint(1, 10)
        if "NPC" in self.locked_elements:
            self.locked_elements.remove("NPC")


class LMMissionPlot(LMPlot):
    mission_active = False
    mission_seed = None
    MISSION_OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_CAPTURE_BUILDINGS)
    MISSION_SCALE = gears.scale.MechaScale
    CASH_REWARD = 150
    EXPERIENCE_REWARD = 150
    MISSION_NAME = "{NPC}'s Mission"

    def prep_mission(self, camp: gears.GearHeadCampaign, custom_elements=None, sgen_override=None, archi_override=None):
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(camp.scene.get_metro_scene())
        if sgen_override:
            sgen = sgen_override
        if archi_override:
            archi = archi_override
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, self.MISSION_NAME.format(**self.elements),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            enemy_faction=self.elements.get("ENEMY_FACTION"),
            rank=camp.renown, objectives=self.MISSION_OBJECTIVES,
            cash_reward=self.CASH_REWARD, experience_reward=self.EXPERIENCE_REWARD,
            on_win=self.win_mission, on_loss=self.lose_mission,
            scenegen=sgen, architecture=archi,
            custom_elements=custom_elements, scale=self.MISSION_SCALE
        )

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_active and self.mission_seed:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

    def win_mission(self, camp):
        self.proper_end_plot(camp)

    def lose_mission(self, camp):
        self.proper_end_plot(camp)


# The actual plots...



class Earth_RescueAndBiotech(LMMissionPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    MISSION_OBJECTIVES = (missionbuilder.BAMOP_DUNGEONLIKE, missionbuilder.BAMOP_RESCUE_VICTIM,
                          lancedev_objectives.BAMOP_DISCOVER_BIOTECHNOLOGY)
    CASH_REWARD = 100
    EXPERIENCE_REWARD = 150
    MISSION_SCALE = gears.scale.HumanScale

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return (gears.personality.DeadZone in pstate.elements["METROSCENE"].attributes or
                gears.personality.GreenZone in pstate.elements["METROSCENE"].attributes)

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)

        self.add_sub_plot(nart, "NPC_VACATION", ident="FREEZER")
        self.prep_mission(
            nart.camp, custom_elements={lancedev_objectives.BAME_LANCEMATE: npc, missionbuilder.BAMEP_MONSTER_TYPE: ("SYNTH", "MUTANT", "ANIMAL")},
            archi_override=gharchitecture.StoneCave(decorate=gharchitecture.CaveDecor())
        )
        self.had_convo = False
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                gears.tags.Medic in candidate.get_tags() and
                gears.stats.Biotechnology not in candidate.statline and
                candidate.relationship.expectation in (None, gears.relationships.E_IMPROVER, gears.relationships.E_ADVENTURE)
            )

    def METROSCENE_ENTER(self,camp):
        if not self.had_convo:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {METROSCENE}, you notice {NPC} looking anxiously at {NPC.gender.possessive_determiner} phone.".format(**self.elements))

            mymenu = ghcutscene.SimpleMonologueMenu(
                "A hiker has gone missing in an area known to contain biomonsters... They're calling on all medics in the area to help with the search and rescue.",
                npc, camp
            )
            mymenu.no_escape = True
            mymenu.add_item("Let's go see if we can find find this hiker.", self._accept_offer)
            mymenu.add_item("We're in no shape to face biomonsters.", self._reject_offer)
            choice = mymenu.query()
            if choice:
                choice(camp)

    def _accept_offer(self,camp):
        npc: gears.base.Character = self.elements["NPC"]
        ghcutscene.SimpleMonologueDisplay(
            "One more thing about this mission... the hiker was probably drawn to these caves because of the rumors of lost biotechnology inside. At the very least, we should keep our eyes open for useful discoveries.", npc)(camp, False)
        self.elements["NPC"].relationship.expectation = relationships.E_DISCOVERY
        self.had_convo = True
        self.mission_active = True

    def _reject_offer(self,camp):
        npc: gears.base.Character = self.elements["NPC"]
        npc.relationship.history.append(gears.relationships.Memory(
            "you refused to aid the search and rescue", "I didn't help you with the search and rescue", -25,
            (gears.relationships.MEM_Ideological,)
        ))
        if npc.get_reaction_score(camp.pc, camp) < 1:
            ghcutscene.SimpleMonologueDisplay("I will go join the search party by myself, then. Don't bother waiting for me as I have no interest in rejoining your lance.", npc)(camp, False)
            plotutility.AutoLeaver(self.elements["NPC"])(camp)
            self.subplots["FREEZER"].freeze_now(camp)
            if relationships.RT_LANCEMATE in npc.relationship.tags:
                npc.relationship.tags.remove(relationships.RT_LANCEMATE)
        else:
            ghcutscene.SimpleMonologueDisplay("You're probably right about that. I just wish there were something we could do.", npc)(camp, False)
        self.proper_end_plot(camp,False)


class Earth_GetInTheMekShimli(LMMissionPlot):
    # A Shimli Test is the kind of personality quiz you might find on Buzzfeed; I think it also refers to the kind of
    # personality test a doctor might give you but such is the extent of my Korean language ability. Anyhow, this is
    # a kind of personlaity test where the test is whether or not you get in the mek.
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    MISSION_OBJECTIVES = (missionbuilder.BAMO_DEFEAT_THE_BANDITS, missionbuilder.BAMO_DEFEAT_COMMANDER)
    CASH_REWARD = 250
    EXPERIENCE_REWARD = 150

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return (gears.personality.DeadZone in pstate.elements["METROSCENE"].attributes or
                gears.personality.GreenZone in pstate.elements["METROSCENE"].attributes)

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        defender = self.seek_element(
            nart, "DEFENDER", self._is_good_defender, scope=self.elements["METROSCENE"], lock=True)

        self.elements["ENEMY_FACTION"] = plotutility.RandomBanditCircle(nart.camp)

        self.prep_mission(nart.camp, sgen_override=gharchitecture.DeadZoneHighwaySceneGen,
                          custom_elements={"ENTRANCE_ANCHOR": pbge.randmaps.anchors.east})
        self.mission_seed.make_enemies = False

        self.started_convo = False
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                candidate.relationship.expectation == gears.relationships.E_GREATERGOOD and
                not candidate.relationship.role
            )

    def _is_good_defender(self, nart, candidate):
        return (isinstance(candidate, gears.base.Character) and nart.camp.is_not_lancemate(candidate) and
                nart.camp.are_faction_allies(self.elements["METROSCENE"], candidate))

    def METROSCENE_ENTER(self,camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            defender = self.elements["DEFENDER"]
            pbge.alert("As you enter {METROSCENE}, {DEFENDER} rushes to you in a near-panic.".format(**self.elements))

            ghcutscene.SimpleMonologueDisplay("[THIS_IS_AN_EMERGENCY] There's a convoy under attack just outside of town. It includes civilian transports. You're the only lance in the area that can possibly make it there in time to defend.", defender)(camp)
            mymenu = ghcutscene.SimpleMonologueMenu("We'll do it. [LETS_START_MECHA_MISSION]", npc, camp)

            mymenu.add_item("Absolutely right. Let's get to work.", self._start_mission)
            mymenu.add_item("Wait a minute- Who do you think the boss of this lance is?", self._question_mission)

            act = mymenu.query()
            if act:
                act(camp)

    def _start_mission(self, camp):
        pbge.alert("You rush to intercept the bandits before they can reach the convoy.")
        npc = self.elements["NPC"]
        npc.relationship.role = gears.relationships.R_COLLEAGUE
        self.mission_seed(camp)

    def _question_mission(self, camp):
        npc = self.elements["NPC"]
        mymenu = ghcutscene.SimpleMonologueMenu("Alright then, \"boss\", what do you say we do?", npc, camp)

        mymenu.add_item("I guess we have no choice- we have to rescue the convoy.", self._grudgingly_start_mission)
        mymenu.add_item("We reject the mission. There are other things we need to do right now.", self._deny_mission)

        act = mymenu.query()
        if act:
            act(camp)

    def _grudgingly_start_mission(self, camp):
        pbge.alert("You go to intercept the bandits before they can reach the convoy. Hopefully you are not too late.")
        npc = self.elements["NPC"]
        npc.relationship.role = gears.relationships.R_CHAPERONE
        self.mission_seed(camp)

    def _deny_mission(self, camp: gears.GearHeadCampaign):
        npc = self.elements["NPC"]
        ghcutscene.SimpleMonologueDisplay(
            "This is no time for your petty ego. I'm going to rescue that convoy; who else is with me?",
            npc)(camp, False)
        deserters = [lm for lm in camp.get_lancemates() if (lm is npc) or (lm.get_reaction_score(camp.pc, camp) < 30) or {gears.personality.Peace, gears.personality.Fellowship}.intersection(lm.personality)]
        deserter_names = [str(d) for d in deserters]
        npc.relationship.expectation = gears.relationships.E_AVENGER
        if len(deserter_names) > 2:
            mymsg = ", ".join(deserter_names[:-1]) + ", and " + deserter_names[-1] + " leave"
        elif len(deserter_names) > 1:
            mymsg = " and ".join(deserter_names) + " leave"
        else:
            mymsg = "{} leaves".format(npc)
        pbge.alert("{} your lance to go rescue the convoy.".format(mymsg))
        for lm in deserters:
            plotutility.AutoLeaver(lm)(camp)
            lm.relationship.reaction_mod -= random.randint(1, 20)
            vplot = game.content.load_dynamic_plot(camp, "NPC_VACATION", PlotState().based_on(self, update_elements={"NPC": lm}))
            vplot.freeze_now(camp)
        self.proper_end_plot(camp, False)


class HowDoYouSeeMe(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene)
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    gears.personality.Sociable in candidate.personality and
                    gears.personality.Fellowship not in candidate.personality and
                    not candidate.relationship.role
            )

    def METROSCENE_ENTER(self, camp: gears.GearHeadCampaign):
        npc = self.elements["NPC"]
        pbge.alert("As you enter {METROSCENE}, {NPC} calls you aside for a talk.".format(**self.elements))

        mymenu = ghcutscene.SimpleMonologueMenu(
            "I just wanted to have a chat, get to know you better. They say that Fellowship is one of the primary cavalier virtues. Of course, it means different things to different people. How do you envision our relationship as part of this lance?",
            npc.get_root(), camp)

        if gears.personality.Fellowship in camp.pc.personality:
            mymenu.add_item("I would say that we are friends, adventuring companions. There's a special bond that only cavaliers know.", self.choose_friend)

        mymenu.add_item("We are colleagues, coworkers. Professionals working together in a dangerous field.", self.choose_colleague)

        if npc.relationship.attitude == gears.relationships.A_SENIOR or npc.renown > camp.renown:
            mymenu.add_item("You are a senior pilot to me. I look up to you and try to learn from you. If anything, you are my mentor.", self.choose_mentor)

        if gears.relationships.RT_FAMILY not in npc.relationship.tags:
            mymenu.add_item("Honestly speaking, ever since you joined the team I've had a bit of a crush on you...", self.choose_crush)

        mymenu.add_item("I don't know?! What is this, some kind of team building activity? We're just lancemates, alright?", self.choose_confusion)

        npc.personality.add(gears.personality.Fellowship)

        answer = mymenu.query()
        if answer:
            answer(npc, camp)

        self.proper_end_plot(camp)

    def choose_friend(self, npc, camp):
        ghcutscene.SimpleMonologueDisplay(
            "Yes, I would say that's the correct answer. Being a cavalier isn't like any other job... the bonds we form on the battlefield are special.", npc
        )(camp, False)
        npc.relationship.role = gears.relationships.R_FRIEND
        npc.relationship.reaction_mod += 10

    def choose_colleague(self, npc, camp):
        ghcutscene.SimpleMonologueDisplay(
            "That's a very professional answer. You didn't used to work for the corporations by any chance, did you?", npc
        )(camp, False)
        npc.relationship.role = gears.relationships.R_COLLEAGUE

    def choose_mentor(self, npc, camp: gears.GearHeadCampaign):
        ghcutscene.SimpleMonologueDisplay(
            "I suppose I am a mentor to you. I'll do my best to pass on whatever knowledge I have to you and the rest of the lance.", npc
        )(camp, False)
        camp.dole_xp(100)
        npc.relationship.role = gears.relationships.R_MENTOR

    def choose_crush(self, npc: gears.base.Character, camp):
        if npc.get_reaction_score(camp.pc, camp) > 20:
            ghcutscene.SimpleMonologueDisplay(
                "Well, that's a pleasant answer to hear. We'll have to talk more about this later.", npc
            )(camp, False)
            npc.relationship.reaction_mod += 10
            npc.relationship.role = gears.relationships.R_CRUSH
        else:
            ghcutscene.SimpleMonologueDisplay(
                "Slow down there, [PC]. I wasn't expecting this much information when I asked the question!", npc
            )(camp, False)
            npc.relationship.reaction_mod -= 10
            npc.relationship.role = gears.relationships.R_COLLEAGUE

    def choose_confusion(self, npc, camp):
        if npc.get_reaction_score(camp.pc, camp) > 40:
            ghcutscene.SimpleMonologueDisplay(
                "Sorry, I didn't mean to confuddle you. I can assure you that we are, in fact, friends... even if that doesn't seem obvious to you right now.", npc
            )(camp, False)
            npc.relationship.role = gears.relationships.R_FRIEND
        else:
            ghcutscene.SimpleMonologueDisplay(
                "Alright, yes, we are lancemates. That part at least everyone can agree on.", npc
            )(camp, False)
            npc.relationship.role = gears.relationships.R_COLLEAGUE


class Earth_ProBonoMetalPanic(LMMissionPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    MISSION_OBJECTIVES = (missionbuilder.BAMO_AID_ALLIED_FORCES, missionbuilder.BAMO_DEFEAT_COMMANDER)
    CASH_REWARD = 0
    EXPERIENCE_REWARD = 250

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return (gears.personality.DeadZone in pstate.elements["METROSCENE"].attributes or
                gears.personality.GreenZone in pstate.elements["METROSCENE"].attributes)

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.elements["ENEMY_FACTION"] = plotutility.RandomBanditCircle(nart.camp)
        self.add_sub_plot(nart, "NPC_VACATION", ident="FREEZER")
        self.prep_mission(nart.camp)
        self.started_convo = False
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                candidate.relationship.attitude == gears.relationships.A_THANKFUL and
                candidate.relationship.expectation == gears.relationships.E_IMPROVER
            )

    def METROSCENE_ENTER(self,camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {METROSCENE}, {NPC} rushes over to talk.".format(**self.elements))
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.PROPOSAL)))
            self.started_convo = True

    def NPC_offers(self,camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.mission_active:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "I just saw this mission on CavNet; a cooperative close to {METROSCENE} is being attacked by bandits. They can't afford a reward, but we've got to go help them!".format(**self.elements),
                (context.HELLO,context.PROPOSAL),
                subject=self, subject_start=True, allow_generics=False
            ))
            mylist.append(Offer(
                "[THANK_YOU] [LETS_START_MECHA_MISSION]".format(**self.elements),
                (context.CUSTOM,),subject=self,data={"reply": "[MISSION:ACCEPT]"},
                effect=self._accept_offer
            ))
            mem = npc.relationship.get_positive_memory()
            if mem:
                mylist.append(Offer(
                    "Remember when {}? It's our job as cavaliers to help people... and if we can't do that, I don't even know what we're here for.".format(mem.npc_perspective),
                    (context.CUSTOM,),subject="Blah", subject_start=True, data={"reply": "We can't afford to do that."},
                ))
            else:
                mylist.append(Offer(
                    "What good are we as cavaliers if we can't protect the people who need protecting? We might be the only people in town who can respond to this emergency.",
                    (context.CUSTOM,),subject="Blah", subject_start=True, data={"reply": "We can't afford to do that."},
                ))

            mylist.append(Offer(
                "[THANK_YOU] [LETS_START_MECHA_MISSION]".format(**self.elements),
                (context.CUSTOMREPLY,), subject="Blah", data={"reply": "Alright, you've convinced me."},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "You can stay here if you want, but I'm going to respond to the call myself. [GOODBYE]",
                (context.CUSTOMREPLY,), subject="Blah", data={"reply": "[MISSION:DENY]"},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_GREATERGOOD
        self.mission_active = True

    def _reject_offer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_GREATERGOOD
        self.elements["NPC"].relationship.attitude = relationships.A_DISRESPECT
        plotutility.AutoLeaver(self.elements["NPC"])(camp)
        self.subplots["FREEZER"].freeze_now(camp)
        self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
            "you refused to help defend the cooperative farm", "I didn't go with you to defend the cooperative", -25,
            (gears.relationships.MEM_Ideological,)
        ))
        self.proper_end_plot(camp,False)

    def win_mission(self, camp: gears.GearHeadCampaign):
        npc: gears.base.Character = self.elements["NPC"]
        if npc in camp.party and not npc.is_destroyed():
            ghcutscene.SimpleMonologueDisplay(
                "We did it!",
                npc.get_root())(camp)
            npc.statline[gears.stats.MechaPiloting] += 1

        self.proper_end_plot(camp)


class FriendInTroubleRightNow(LMMissionPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    MISSION_OBJECTIVES = (missionbuilder.BAMO_CAPTURE_BUILDINGS, missionbuilder.BAMO_RESCUE_NPC)

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.elements["ENEMY_FACTION"] = plotutility.RandomBanditCircle(nart.camp)
        sp = self.add_sub_plot(nart,"ADD_COMBATANT_NPC")
        self.elements["FRIEND"] = sp.elements["NPC"]
        self.add_sub_plot(nart, "NPC_VACATION", ident="FREEZER")
        self.prep_mission(nart.camp)
        self.started_convo = False
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                candidate.relationship.attitude == gears.relationships.A_FRIENDLY and
                gears.personality.Fellowship in candidate.personality and
                candidate.relationship.role is None
            )

    def METROSCENE_ENTER(self,camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {METROSCENE}, {NPC} rushes over to tell you something.".format(**self.elements))
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.PROPOSAL)))
            self.started_convo = True

    def NPC_offers(self,camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.mission_active:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "I have to leave right now; my friend {FRIEND} is in trouble and needs help.".format(**self.elements),
                (context.HELLO,context.PROPOSAL),
                subject=self, subject_start=True, allow_generics=False
            ))
            mylist.append(Offer(
                "[THANK_YOU] We have to hurry... {FRIEND} is being attacked by {ENEMY_FACTION} as we speak!".format(**self.elements),
                (context.CUSTOM,),subject=self,data={"reply": "Let's go together. If your friend needs help, we'll all help."},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "Thanks for understanding. I'm sure I'll have no problem handling this by myself.",
                (context.CUSTOM,),subject=self,data={"reply": "Good luck with that. I'll see you later."},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self,camp):
        self.elements["NPC"].relationship.role = relationships.R_FRIEND
        self.mission_active = True
        self.mission_seed(camp)

    def _reject_offer(self,camp):
        self.elements["NPC"].relationship.role = relationships.R_COLLEAGUE
        plotutility.AutoLeaver(self.elements["NPC"])(camp)
        self.subplots["FREEZER"].freeze_now(camp)
        friend = self.elements["FRIEND"]
        friend.container.remove(friend)
        self.proper_end_plot(camp,False)

    def prep_mission(self, camp: gears.GearHeadCampaign):
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(camp.scene.get_metro_scene())
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, self.MISSION_NAME.format(**self.elements),
            self.elements["METROSCENE"],self.elements["MISSION_GATE"],
            enemy_faction=self.elements.get("ENEMY_FACTION"),
            rank=camp.renown + 5, objectives=self.MISSION_OBJECTIVES,
            cash_reward=self.CASH_REWARD, experience_reward=self.EXPERIENCE_REWARD,
            on_win=self.win_mission, on_loss=self.lose_mission,
            custom_elements={missionbuilder.BAME_RESCUENPC: self.elements["FRIEND"]},
            scenegen=sgen, architecture=archi
        )

    def win_mission(self, camp: gears.GearHeadCampaign):
        npc: gears.base.Character = self.elements["NPC"]
        if npc in camp.party and not npc.is_destroyed():
            ghcutscene.SimpleMonologueDisplay(
                "Thanks for coming along, [PC]. Seems like I did need your help after all.",
                npc.get_root())(camp)
            npc.statline[gears.stats.MechaPiloting] += 1

        friend: gears.base.Character = self.elements["FRIEND"]
        if not friend.relationship:
            friend.relationship = camp.get_relationship(friend)
        friend.relationship.tags.add(gears.relationships.RT_LANCEMATE)

        self.proper_end_plot(camp)


class DDLD_ContactInTown(LMMissionPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    CASH_REWARD = 300
    EXPERIENCE_REWARD = 200
    MISSION_NAME = "{MISSIONGIVER}'s Mission"
    MISSION_OBJECTIVES = (missionbuilder.BAMO_STORM_THE_CASTLE,)

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        candidates = [fac for fac, rel in nart.camp.faction_relations.items() if
                      nart.camp.are_faction_enemies(self.elements["METROSCENE"], fac) and
                      not nart.camp.are_faction_allies(npc, fac)]
        if candidates:
            self.elements["ENEMY_FACTION"] = random.choice(candidates)
            sp = self.add_sub_plot(nart, "PLACE_LOCAL_REPRESENTATIVES", elements={"LOCALE": self.elements["METROSCENE"], "FACTION": self.elements["METROSCENE"].faction})
            self.elements["MISSIONGIVER"] = sp.elements["NPC"]
            self.prep_mission(nart.camp)
            self.started_convo = False
            return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                candidate.relationship.expectation == gears.relationships.E_MERCENARY and
                gears.personality.Fellowship in candidate.personality and
                candidate.relationship.attitude in (gears.relationships.A_JUNIOR, gears.relationships.A_SENIOR, None)
            )

    def METROSCENE_ENTER(self,camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("{NPC} approaches you, smiling broadly.".format(**self.elements))
            npc.relationship.attitude = relationships.A_FRIENDLY
            ghcutscene.SimpleMonologueDisplay(
                "I just got a message from [foaf]. {MISSIONGIVER} at {MISSIONGIVER.scene} is looking for a cavalier to run a lucrative mission.".format(**self.elements),
                npc.get_root())(camp)
            self.memo = pbge.memos.Memo( "{MISSIONGIVER} may have a lucrative mission for you.".format(**self.elements)
                            , self.elements["MISSIONGIVER"].get_scene()
                            )
            self.started_convo = True

    def MISSIONGIVER_offers(self,camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.mission_active:
            mylist.append(Offer(
                "There are troops belonging to {} setting up in the area, and nobody wants that. Your job will be to clear them out and destroy their fortifications.".format(self.elements["ENEMY_FACTION"].name),
                (context.MISSION,),
                subject=self, subject_start=True
            ))
            mylist.append(Offer(
                "[IWillSendMissionDetails]. [GOODLUCK]",
                (context.ACCEPT,),subject=self,
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "I expect that some of the local pilots will be eager to prove themselves on this mission. [GOODBYE]",
                (context.DENY,),subject=self,
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self,camp):
        self.mission_active = True
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def _reject_offer(self,camp):
        self.proper_end_plot(camp,False)


class BeFriendsRaidFactory(LMMissionPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    CASH_REWARD = 300
    ENEMY_FACTIONS = (gears.factions.KettelIndustries, gears.factions.RegExCorporation, gears.factions.BioCorp,)
    MISSION_OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_CAPTURE_THE_MINE)

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return (gears.personality.DeadZone in pstate.elements["METROSCENE"].attributes or
                gears.personality.GreenZone in pstate.elements["METROSCENE"].attributes)

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.elements["ENEMY_FACTION"] = random.choice(self.ENEMY_FACTIONS)
        self.prep_mission(nart.camp)
        self.started_convo = False
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                candidate.relationship.expectation is None and gears.tags.Criminal in candidate.get_tags()
                and candidate.relationship.role == gears.relationships.R_FRIEND
            )

    def METROSCENE_ENTER(self,camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {METROSCENE}, {NPC} pulls you aside for a private chat.".format(**self.elements))
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.PROPOSAL)))
            self.started_convo = True

    def NPC_offers(self,camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.mission_active:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "There's a processing facility belonging to {} just outside of town, and today they'll be moving some valuable cargo. If we strike fast we can rob them blind.".format(self.elements["ENEMY_FACTION"].name),
                (context.HELLO,context.PROPOSAL),
                subject=self, subject_start=True, allow_generics=False
            ))
            mylist.append(Offer(
                "[GOOD] We don't need to tell anyone else what kind of mission this is... They wouldn't understand.",
                (context.CUSTOM,),subject=self,data={"reply": "[MISSION:ACCEPT]"},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "Yeah, I know... old habits die hard, I guess. Let's just keep this conversation between you and me. I'll try to stay on the up and up from here on out.",
                (context.CUSTOM,),subject=self,data={"reply": "No; we're cavaliers, not bandits."},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_MERCENARY
        self.mission_active = True
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def _reject_offer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_IMPROVER
        self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
            "you convinced me to give up on crime", "I helped you to reform", 5,
            (gears.relationships.MEM_Ideological,)
        ))
        self.elements["NPC"].statline[gears.stats.Ego] += 2
        self.proper_end_plot(camp,False)

    def win_mission(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        if npc in camp.party and not npc.is_destroyed():
            ghcutscene.SimpleMonologueDisplay(
                "I'll keep looking out for more opportunities like this.",
                npc.get_root())(camp)
            npc.statline[gears.stats.Scouting] += 2

        self.proper_end_plot(camp)


class PureBiznessRelationship(LMMissionPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    CASH_REWARD = 200

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        candidates = [fac for fac, rel in nart.camp.faction_relations.items() if
                      rel.pc_relation == rel.ENEMY and not nart.camp.are_faction_allies(npc, fac)]
        if candidates:
            self.elements["ENEMY_FACTION"] = random.choice(candidates)
            self.prep_mission(nart.camp)
            self.started_convo = False
            return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.relationship.expectation is None
                    and candidate.relationship.role is None
            )

    def METROSCENE_ENTER(self,camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("{NPC}'s phone rings. After a short conversation, {NPC.gender.subject_pronoun} turns to you.".format(**self.elements))
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.PROPOSAL)))
            self.started_convo = True

    def NPC_offers(self,camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.mission_active:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "I just got a hot tip from [foaf]; there's a mission available right now to fight {} for double standard pay. We could really use that money.".format(self.elements["ENEMY_FACTION"].name),
                (context.HELLO,context.PROPOSAL),
                subject=self, subject_start=True, allow_generics=False
            ))
            mylist.append(Offer(
                "[GOOD] I'm receiving the data on my phone now... we can get started any time you want.",
                (context.CUSTOM,),subject=self,data={"reply":"[MISSION:ACCEPT]"},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "[YOU_ARE_THE_BOSS]",
                (context.CUSTOM,),subject=self,data={"reply":"[MISSION:DENY]"},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_MERCENARY
        self.mission_active = True
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def _reject_offer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_MERCENARY
        self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
            "you rejected the mission I suggested", "I didn't accept the mission you suggested", -10,
            (gears.relationships.MEM_Ideological,)
        ))
        self.proper_end_plot(camp,False)

    def win_mission(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        if npc in camp.party and not npc.is_destroyed():
            ghcutscene.SimpleMonologueDisplay(
                "Maybe in the future, I could arrange even more missions like this for us. I should practice that.",
                npc.get_root())(camp)
            npc.statline[gears.stats.Negotiation] += 2

        self.proper_end_plot(camp)


class PrezeroMacguffin(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return (gears.personality.DeadZone in pstate.elements["METROSCENE"].attributes or
                gears.personality.GreenZone in pstate.elements["METROSCENE"].attributes)

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.rank = npc.renown
        self.started_conversation = False
        self.got_info = False

        # Add the ruin dungeon
        self.dungeon_name = "{} Ruin".format(gears.selector.EARTH_NAMES.gen_word())
        self.dungeon = dungeonmaker.DungeonMaker(
            nart, self, self.elements["METROSCENE"], self.dungeon_name,
            gharchitecture.FortressBuilding(),
            self.rank,
            monster_tags=("ROBOT", "SYNTH", "MUTANT", "RUINS"),
            scene_tags=(gears.tags.SCENE_DUNGEON, gears.tags.SCENE_RUINS,)
        )
        d_entrance = pbge.randmaps.rooms.ClosedRoom(7, 7, anchor=pbge.randmaps.anchors.middle)
        self.dungeon.entry_level.contents.append(d_entrance)
        self.dungeon_entrance = ghwaypoints.Exit(dest_wp=self.elements["MISSION_GATE"],
                                                 anchor=pbge.randmaps.anchors.middle)
        d_entrance.contents.append(self.dungeon_entrance)

        # Add the goal room
        final_room = self.register_element(
            "FINAL_ROOM", pbge.randmaps.rooms.ClosedRoom(9, 9, ),
        )
        self.dungeon.goal_level.contents.append(final_room)
        self.add_sub_plot(
            nart, "MONSTER_ENCOUNTER", spstate=PlotState(rank=self.rank + 12).based_on(self),
            elements={
                "ROOM": final_room, "LOCALE": self.dungeon.goal_level,
                "TYPE_TAGS": ("ROBOT", "SYNTH", "MUTANT", "RUINS")
            }
        )
        mycrate = ghwaypoints.Crate(treasure_rank=self.rank + 20, treasure_amount=250)
        final_room.contents.append(mycrate)
        myitem = self.register_element(
            "MACGUFFIN", gears.base.Treasure(value=1000000, weight=45, name="Proto-Sculpture",
                                             desc="A mysterious statue crafted by the original inhabitants of {}.".format(
                                                 self.dungeon_name))
        )
        mycrate.contents.append(myitem)

        self.got_macguffin = False

        return True

    def MACGUFFIN_GET(self, camp):
        if not self.got_macguffin:
            self.got_macguffin = True
            npc: gears.base.Character = self.elements["NPC"]
            if npc in camp.party:
                ghcutscene.SimpleMonologueDisplay(
                    "Oh wow, do you realize what that is? Neither do I but I bet it's worth a fortune!", npc)(camp)
                npc.statline[gears.stats.Knowledge] += 2

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.relationship.attitude == gears.relationships.A_FRIENDLY and
                    candidate.relationship.role in (None, gears.relationships.R_COLLEAGUE)
                    and {gears.tags.Adventurer, gears.tags.Criminal}.intersection(candidate.get_tags())
            )

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.got_info:
            thingmenu.add_item("Go to {}".format(self.dungeon_name), self.go_to_dungeon)

    def go_to_dungeon(self, camp):
        camp.go(self.dungeon_entrance)

    def t_START(self, camp):
        if not self.got_info:
            super().t_START(camp)

    def METROSCENE_ENTER(self, camp):
        if not self.started_conversation:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {}, you notice {} gazing out toward the horizon.".format(camp.scene, npc))
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.PROPOSAL)))
            self.started_conversation = True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.got_info:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "There's a synth-infested ruin near {METROSCENE} that's supposed to be filled with PreZero artifacts. I've always wanted to go there and try my luck. In fact, I'd love to go there with you.".format(
                    **self.elements),
                (context.HELLO, context.PROPOSAL),
                subject=self, subject_start=True, allow_generics=False
            ))
            if self.rank > camp.renown + 5:
                mylist.append(Offer(
                    "Well, I'm not sure you're ready for that yet, [PC]. It's a dangerous place and I don't want to be the one responsible for getting you killed. But maybe later, we can come back and go treasure hunting.",
                    (context.CUSTOM,), subject=self, data={"reply": "I'd like that too, [audience]."},
                    effect=self._accept_offer
                ))
            else:
                mylist.append(Offer(
                    "[GOOD] I've always wanted a buddy to explore dungeons with. This is going to be fun!",
                    (context.CUSTOM,), subject=self, data={"reply": "I'd like that too, [audience]."},
                    effect=self._accept_offer
                ))
            if npc.get_reaction_score(camp.pc, camp) > 25:
                if self.rank > camp.renown + 5:
                    mylist.append(Offer(
                        "What?! No... Well, maybe. I mean, it's a really dangerous place, it's not a good spot for... You're going to need some training before we can go there.",
                        (context.CUSTOM,), subject=self, data={"reply": "You mean, like, on a date?"},
                        effect=self._flirty_offer
                    ))
                else:
                    mylist.append(Offer(
                        "What?! Yes... I mean no. A dungeon is no place for a first date. But I mean, if you wanted to, maybe we could go to a restaurant or something after we finish looting the place...?",
                        (context.CUSTOM,), subject=self, data={"reply": "You mean, like, on a date?"},
                        effect=self._flirty_offer
                    ))

            mylist.append(Offer(
                "That's too bad. I've always wanted to have an adventure buddy to explore dungeons with, but I guess that's not your style. I'm still glad to be your lancemate.",
                (context.CUSTOM,), subject=self, data={"reply": "No thanks, we have no time for that."},
                effect=self._reject_offer
            ))
        return mylist

    def _make_memo(self):
        self.memo = pbge.memos.Memo(
            "{NPC} told you about a ruin where you can find valuable PreZero artifacts.".format(**self.elements)
            , "{} at {}".format(self.dungeon_name, self.elements["METROSCENE"])
            )

    def _accept_offer(self, camp):
        self.got_info = True
        self.elements["NPC"].relationship.role = gears.relationships.R_FRIEND
        self._make_memo()
        self.proper_non_end(camp)

    def _flirty_offer(self, camp):
        self.got_info = True
        self.elements["NPC"].relationship.role = gears.relationships.R_CRUSH
        self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
            "you asked me out", "I kind of asked you out", 10, (gears.relationships.MEM_Romantic,)
        ))
        self._make_memo()
        self.proper_non_end(camp)

    def _reject_offer(self, camp):
        self.elements["NPC"].relationship.role = gears.relationships.R_FRIEND
        self.proper_end_plot(False)


class DeadZoneSortingDuel(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return gears.personality.DeadZone in pstate.elements["METROSCENE"].attributes

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.started_conversation = False
        self.accepted_duel = False
        self.duel = missionbuilder.BuildAMissionSeed(
            nart.camp, "{}'s Duel".format(npc), self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            rank=npc.renown, objectives=[dd_customobjectives.DDBAMO_DUEL_LANCEMATE], solo_mission=True,
            custom_elements={"LMNPC": npc}, experience_reward=200, salvage_reward=False
        )
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return candidate.relationship.expectation == gears.relationships.E_PROFESSIONAL and not candidate.relationship.attitude

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.accepted_duel:
            thingmenu.add_item("Travel into the deadzone to have a practice match with {}".format(self.elements["NPC"]),
                               self.duel)

    def t_START(self, camp):
        npc = self.elements["NPC"]
        if not self.accepted_duel:
            super().t_START(camp)
        elif npc.is_destroyed():
            self.end_plot(camp)
        if self.duel.is_completed():
            if self.duel.is_won():
                npc.relationship.attitude = gears.relationships.A_JUNIOR
                ghcutscene.SimpleMonologueDisplay(
                    "Your skills are incredible. It seems I have a lot to learn from you.", npc)(camp)
            else:
                npc.relationship.attitude = gears.relationships.A_SENIOR
                ghcutscene.SimpleMonologueDisplay(
                    "You show great potential, but you aren't quite there yet. Maybe someday we can have a rematch.",
                    npc)(camp)
            self.proper_end_plot(camp)

    def t_UPDATE(self, camp):
        if not self.started_conversation:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {}, you notice {} giving you a quizzical look.".format(camp.scene, npc))
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.QUERY)))
            self.started_conversation = True

    def NPC_offers(self, camp):
        mylist = list()
        if not self.accepted_duel:
            mylist.append(Offer(
                "We've been traveling together for a while, but I still haven't figured out how you rank. [CAN_I_ASK_A_QUESTION]",
                (context.HELLO, context.QUERY), allow_generics=False
            ))
            mylist.append(Offer(
                "I'm curious about how your combat skills compare to mine. How would you like to go out into the dead zone, find a nice uninhabited place, and have a friendly little practice duel?",
                (context.QUERY,), subject=self, subject_start=True
            ))
            mylist.append(Offer(
                "[GOOD] Whenever you're ready, we can head out of town and find an appropriate place.",
                (context.ANSWER,), subject=self, data={"reply": "[ACCEPT_CHALLENGE]"},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "That's very disappointing. I never imagined you to be a coward, but as I said earlier I don't quite have you figured out yet...",
                (context.ANSWER,), subject=self, data={"reply": "No thanks, we have no time for that."},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self, camp):
        self.accepted_duel = True

    def _reject_offer(self, camp):
        self.elements["NPC"].relationship.attitude = gears.relationships.A_RESENT
        self.proper_end_plot(camp, False)


class ProfessionalGlory(LMMissionPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    EXPERIENCE_REWARD = 200

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        candidates = [fac for fac, rel in nart.camp.faction_relations.items() if
                      rel.pc_relation == rel.ENEMY and not nart.camp.are_faction_allies(npc, fac)]
        if candidates:
            self.elements["ENEMY_FACTION"] = random.choice(candidates)

            self.prep_mission(nart.camp)
            self.started_convo = False
            return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.relationship.expectation is None
                    and gears.personality.Glory in candidate.personality
            )

    def METROSCENE_ENTER(self, camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert(
                "{NPC}'s phone rings. After a short conversation, {NPC.gender.subject_pronoun} turns to you.".format(
                    **self.elements))
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.PROPOSAL)))
            self.started_convo = True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.mission_active:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "I just got a call from [foaf]; [subject_pronoun] needs a professional cavalier team for a high stakes mission. Are we going to accept?".format(
                    self.elements["ENEMY_FACTION"].name),
                (context.HELLO, context.PROPOSAL),
                subject=self, subject_start=True, allow_generics=False
            ))
            mylist.append(Offer(
                "[GOOD] I've forwarded the mission data to everyone.",
                (context.CUSTOM,), subject=self, data={"reply": "[MISSION:ACCEPT]"},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "[YOU_ARE_THE_BOSS]",
                (context.CUSTOM,), subject=self, data={"reply": "[MISSION:DENY]"},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self, camp):
        self.elements["NPC"].relationship.expectation = relationships.E_PROFESSIONAL
        self.mission_active = True
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def _reject_offer(self, camp):
        self.elements["NPC"].relationship.expectation = relationships.E_PROFESSIONAL
        self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
            "you rejected the mission I suggested", "I didn't accept the mission you suggested", -10,
            (gears.relationships.MEM_Ideological,)
        ))
        self.proper_end_plot(camp, False)

    def win_mission(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        if npc in camp.party and not npc.is_destroyed():
            ghcutscene.SimpleMonologueDisplay(
                "Winning missions like this will help us to build a solid reputation and become better cavaliers.",
                npc.get_root())(camp)
            npc.statline[gears.stats.MechaPiloting] += 1

        self.proper_end_plot(camp)


class LD_SurpriseMechaPresent(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene)

        # generate a new customized mecha to give to the PC.
        pc_mek = nart.camp.get_pc_mecha(nart.camp.pc)
        if pc_mek and pc_mek.get_full_name() in gears.selector.DESIGN_BY_NAME:
            self.base_mek = gears.selector.get_design_by_full_name(pc_mek.get_full_name())
        else:
            self.base_mek = gears.selector.MechaShoppingList.generate_single_mecha(self.rank + 25, npc.fac)

        if self.base_mek:
            if pc_mek:
                self.base_mek.colors = pc_mek.colors
            else:
                self.base_mek.colors = gears.color.random_mecha_colors()
            gears.champions.upgrade_to_champion(self.base_mek)
            # Make sure there's more than one lancemate so all the "we", "they" below makes sense.
            return len(nart.camp.get_lancemates()) > 1

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.relationship.role == gears.relationships.R_FRIEND and
                    candidate.relationship.attitude == gears.relationships.A_THANKFUL
            )

    def METROSCENE_ENTER(self, camp: gears.GearHeadCampaign):
        npc = self.elements["NPC"]
        pbge.alert("As you enter {METROSCENE}, your lancemates surround you. They have a cake.".format(**self.elements))

        ghcutscene.SimpleMonologueDisplay(
            "Surprise! In honor of you being such a good team leader, we've bought you a brand new {}!".format(
                self.base_mek.get_full_name()),
            npc.get_root())(camp)

        candidates = [npc2 for npc2 in camp.get_lancemates() if
                      npc2 is not npc and (gears.stats.Science in npc2.statline or gears.stats.Repair in npc2.statline)]
        if candidates:
            npc2 = random.choice(candidates)
            ghcutscene.SimpleMonologueDisplay(
                "I upgraded some of the parts on it. I think you'll find that it performs much better than the stock model.",
                npc2.get_root())(camp, False)

        npc.relationship.attitude = relationships.A_EQUAL
        npc.statline[gears.stats.Charm] += 1

        ghcutscene.SimpleMonologueDisplay(
            "Here are the keys, and now let's go enjoy this cake before the icing melts.",
            npc.get_root())(camp, False)

        camp.party.append(self.base_mek)
        # camp.assign_pilot_to_mecha(camp.pc, self.base_mek)
        self.proper_end_plot(camp)


class DDLD_ProfessionalColleague(LMMissionPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        enemy_npc = self.seek_element(nart, "ENEMY_NPC", self._is_good_enemy, scope=nart.camp, lock=True)
        self.elements["ENEMY_FACTION"] = enemy_npc.faction
        self.prep_mission(nart.camp)
        self.started_convo = False
        return not nart.camp.are_faction_allies(enemy_npc, npc)

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.relationship.role is None
                    and candidate.relationship.expectation == gears.relationships.E_PROFESSIONAL
            )

    def _is_good_enemy(self, nart, candidate):
        return (isinstance(candidate, gears.base.Character) and nart.camp.is_not_lancemate(candidate) and
                candidate.faction and nart.camp.are_faction_enemies(candidate, self.elements["METROSCENE"]))

    def METROSCENE_ENTER(self, camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert(
                "As you enter {METROSCENE}, {NPC} walks up to show you something on {NPC.gender.possessive_determiner} phone.".format(
                    **self.elements))
            ghdialogue.start_conversation(camp, camp.pc, npc,
                                          cue=pbge.dialogue.Cue((context.HELLO, context.PROPOSAL)))
            npc.relationship.role = gears.relationships.R_COLLEAGUE
            self.started_convo = True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.mission_active:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "Look at this... {ENEMY_NPC.faction} {ENEMY_NPC} has been sighted in this area. There's a significant reward if we can capture {ENEMY_NPC.gender.object_pronoun}, plus it would be a huge boost to our reputation.".format(
                    **self.elements),
                (context.HELLO, context.PROPOSAL),
                subject=self, subject_start=True, allow_generics=False
            ))
            mylist.append(Offer(
                "[GOOD] It shouldn't be that hard to locate {ENEMY_NPC}... {ENEMY_NPC.gender.possessive_determiner} lance has been cutting a path of destruction through the area around {METROSCENE}.".format(
                    **self.elements),
                (context.CUSTOM,), subject=self, data={"reply": "[MISSION:ACCEPT]"},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "You know what? I really think that you lack ambition.",
                (context.CUSTOM,), subject=self, data={"reply": "[MISSION:DENY]"},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self, camp):
        self.mission_active = True
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def _reject_offer(self, camp):
        self.proper_end_plot(camp, False)

    def win_mission(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        if npc in camp.party and not npc.is_destroyed():
            ghcutscene.SimpleMonologueDisplay(
                "It would be useful if we could track down bounties like this more often. I'm going to start working on it.",
                npc.get_root())(camp)
            npc.statline[gears.stats.Scouting] += 2
        self.proper_end_plot(camp)

    def prep_mission(self, camp: gears.GearHeadCampaign):
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, self.MISSION_NAME.format(**self.elements),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            enemy_faction=self.elements.get("ENEMY_FACTION"),
            allied_faction=self.elements["METROSCENE"].faction,
            rank=camp.renown, objectives=(missionbuilder.BAMO_DEFEAT_NPC, missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL),
            cash_reward=self.CASH_REWARD, experience_reward=self.EXPERIENCE_REWARD,
            on_win=self.win_mission, on_loss=self.lose_mission,
            custom_elements={missionbuilder.BAME_NPC: self.elements["ENEMY_NPC"]}
        )


class DDLD_HermitMechaniac(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    @classmethod
    def matches(self, pstate):
        """Returns True if this plot matches the current plot state."""
        return gears.personality.DeadZone in pstate.elements["METROSCENE"].attributes

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)

        shopkeeper: gears.base.Character = self.register_element("SHOPKEEPER",
                                                                 gears.selector.random_character(
                                                                     self.rank,
                                                                     local_tags=self.elements["METROSCENE"].attributes,
                                                                     job=gears.jobs.ALL_JOBS["Mecha Designer"]
                                                                 ))

        mwsp = self.add_sub_plot(nart, "MECHA_WORKSHOP", ident="FACTORY", elements={"OWNER_NAME": str(shopkeeper)})
        fcsp = self.add_sub_plot(nart, "FENIX_CASTLE", ident="FENIXCASTLE",
                                 elements={"CASTLE_NAME": str(mwsp.elements["LOCALE"]), })

        self.elements["WORKSHOP"] = mwsp.elements["LOCALE"]
        shopkeeper.place(mwsp.elements["LOCALE"], team=mwsp.elements["LOCALE"].civilian_team)

        plotutility.IntConcreteBuildingConnection(
            nart, self, fcsp.elements["LOCALE"], mwsp.elements["LOCALE"], room1=fcsp.elements["CASTLE_ROOM"],
            room2=mwsp.elements["FOYER"],
        )

        self.shop = services.Shop(npc=shopkeeper, shop_faction=self.elements["METROSCENE"].faction,
                                  sell_champion_equipment=True,
                                  ware_types=services.MECHA_STORE, rank=self.rank + 5)

        self.wins = 0
        self.rewards = 0
        self.told_about_raiders = False

        self.started_convo = False
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.relationship.attitude == gears.relationships.A_FRIENDLY
                    and candidate.relationship.expectation == gears.relationships.E_MECHANIAC
            )

    def METROSCENE_ENTER(self, camp: gears.GearHeadCampaign):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {METROSCENE}, {NPC} runs up to you excitedly.".format(**self.elements))

            ghcutscene.SimpleMonologueDisplay(
                "There's a workshop just outside of town belonging to the famous mecha designer {SHOPKEEPER}. We should go and see if we can get some custom gear!".format(
                    **self.elements),
                npc.get_root())(camp)
            self.started_convo = True
            npc.relationship.attitude = gears.relationships.A_HEARTFUL
            self.subplots["FENIXCASTLE"].activate(camp)
            missionbuilder.NewLocationNotification(self.elements["WORKSHOP"], self.elements["MISSION_GATE"])
            self.proper_non_end(camp)

    def FENIXCASTLE_WIN(self, camp):
        self.wins += 1
        self.shop.rank += self.wins * 5
        self.rewards += gears.selector.calc_threat_points(self.rank + self.wins * 5, 15)
        if self.wins >= 3:
            self.subplots["FENIXCASTLE"].encounters_on = False

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        if self.rewards > 0:
            mylist.append(Offer(
                "[HELLO] Thanks for protecting my factory from those raiders; here is a reward for ${:,}.".format(
                    self.rewards),
                context=ContextTag([context.HELLO]), effect=self._give_rewards
                ))
        else:
            mylist.append(Offer("[HELLO] Can I interest you in a new [mecha] today?",
                                context=ContextTag([context.HELLO]),
                                ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": str(self.elements["LOCALE"]), "wares": "mecha"}
                            ))

        if not self.told_about_raiders:
            mylist.append(Offer(
                "They're a small time gang of highway bandits who got pissed off that I wouldn't supply them with mecha, but behaviour like this is exactly why I didn't supply them with mecha!",
                context=ContextTag([context.INFO]), effect=self._tell_about_raiders,
                data={"subject": "the raiders"}, no_repeats=True
                ))

        return mylist

    def _give_rewards(self, camp: gears.GearHeadCampaign):
        camp.credits += self.rewards
        self.rewards = 0

    def _tell_about_raiders(self, camp):
        self.told_about_raiders = True


class WangttaScent(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.started_conversation = False
        self.accepted_duel = False
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(nart.camp.scene.get_metro_scene())
        self.duel = missionbuilder.BuildAMissionSeed(
            nart.camp, "{}'s Duel".format(npc), self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            rank=npc.renown, objectives=[dd_customobjectives.DDBAMO_DUEL_LANCEMATE], solo_mission=True,
            custom_elements={"LMNPC": npc}, experience_reward=200, salvage_reward=False,
            scenegen=sgen, architecture=archi
        )
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return candidate.relationship.attitude is None and candidate.get_stat(gears.stats.MechaPiloting) < (
                        candidate.renown // 10 + 4)

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.accepted_duel:
            thingmenu.add_item("Travel outside of town to have a practice match with {}".format(self.elements["NPC"]),
                               self.duel)

    def t_START(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        if not self.accepted_duel:
            super().t_START(camp)
        elif npc.is_destroyed():
            self.end_plot(camp)
        if self.duel.is_completed():
            if self.duel.is_won():
                npc.relationship.attitude = gears.relationships.A_JUNIOR
                ghcutscene.SimpleMonologueDisplay(
                    "I think I learned a couple of things from the way you kicked my arse. I promise to keep practicing and improving!",
                    npc)(camp)
            else:
                npc.relationship.attitude = gears.relationships.A_FRIENDLY
                ghcutscene.SimpleMonologueDisplay(
                    "Wow, I guess that I learned more from you than I thought. That was awesome!", npc)(camp)
            npc.dole_experience(2000)
            self.proper_end_plot(camp)

    def t_UPDATE(self, camp):
        if not self.started_conversation:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {}, {} waves you over for a conversation.".format(camp.scene, npc))
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.QUERY)))
            self.started_conversation = True

    def NPC_offers(self, camp):
        mylist = list()
        if not self.accepted_duel:
            mylist.append(Offer(
                "I've really enjoyed traveling with you, but sometimes I get the feeling that I'm sort of holding the lance back... [CAN_I_ASK_A_QUESTION]",
                (context.HELLO, context.QUERY), allow_generics=False
            ))
            mylist.append(Offer(
                "My mecha skills aren't really as good as the rest of the team. They say the best way to learn is to practice... would you like to go have a practice match with me outside of town? I've learned a lot just from watching you, but I think a real duel could be even better.",
                (context.QUERY,), subject=self, subject_start=True
            ))
            mylist.append(Offer(
                "[GOOD] Whenever you're ready, we can head out of town and find an appropriate place.",
                (context.ANSWER,), subject=self, data={"reply": "[ACCEPT_CHALLENGE]"},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "I understand... I guess my advancement isn't your problem. I won't bother you about it again.",
                (context.ANSWER,), subject=self, data={"reply": "No thanks, we have no time for that."},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self, camp):
        self.accepted_duel = True

    def _reject_offer(self, camp):
        self.elements["NPC"].relationship.attitude = gears.relationships.A_DESPAIR
        self.elements["NPC"].statline[gears.stats.MechaPiloting] += 1
        self.proper_end_plot(camp, False)


class FinishingRegrets(LMMissionPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    CASH_REWARD = 200

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        candidates = [fac for fac, rel in nart.camp.faction_relations.items() if
                      rel.pc_relation == rel.ENEMY and not nart.camp.are_faction_allies(npc, fac)]
        if candidates:
            self.elements["ENEMY_FACTION"] = random.choice(candidates)
            self.prep_mission(nart.camp)
            self.started_convo = False
            return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.relationship.expectation == gears.relationships.E_IMPROVER
                    and candidate.relationship.attitude is None
            )

    def METROSCENE_ENTER(self, camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert(
                "{NPC}'s phone rings. After a short and tense conversation, {NPC.gender.subject_pronoun} turns to you.".format(
                    **self.elements))
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.PROPOSAL)))
            self.started_convo = True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.mission_active:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "I just heard from [foaf]; there's a strike team from {} operating nearby. The same strike team that killed all of my previous lancemates. Let's destroy them and collect the reward.".format(
                    self.elements["ENEMY_FACTION"].name),
                (context.HELLO, context.PROPOSAL),
                subject=self, subject_start=True, allow_generics=False
            ))
            mylist.append(Offer(
                "[GOOD] Sending you the data now... Let's get started as soon as possible.",
                (context.CUSTOM,), subject=self, data={"reply": "[MISSION:ACCEPT]"},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "[YOU_ARE_THE_BOSS]",
                (context.CUSTOM,), subject=self, data={"reply": "[MISSION:DENY]"},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self, camp):
        self.elements["NPC"].relationship.attitude = relationships.A_THANKFUL
        self.mission_active = True
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def _reject_offer(self, camp):
        self.elements["NPC"].relationship.attitude = relationships.A_DESPAIR
        self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
            "you held me back from avenging my lost lancemates",
            "I stopped you from getting killed looking for vengeance", -25,
            (gears.relationships.MEM_Ideological,)
        ))
        self.proper_end_plot(camp, False)

    def win_mission(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        if npc in camp.party and not npc.is_destroyed():
            ghcutscene.SimpleMonologueDisplay(
                "It is over. My dear friends can sleep peacefully now.",
                npc.get_root())(camp)
            npc.statline[gears.stats.Vitality] += 2
            npc.statline[gears.stats.Athletics] += 2
            npc.statline[gears.stats.Concentration] += 2
            if gears.personality.Fellowship in npc.personality:
                npc.statline[gears.stats.Ego] += 2
            else:
                npc.personality.add(gears.personality.Fellowship)

            self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
                "you helped me avenge my fallen lancemates",
                "I helped you avenge your fallen lancemates", 15,
                (gears.relationships.MEM_AidedByPC,)
            ))

        self.proper_end_plot(camp)


class LD_GladToBeHere(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.started_convo = False
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.relationship.attitude == gears.relationships.A_THANKFUL
                    and candidate.relationship.role is None
            )

    def METROSCENE_ENTER(self, camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert(
                "As you enter {METROSCENE}, {NPC} approaches you for a conversation.".format(
                    **self.elements))
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.INFO)))
            self.started_convo = True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        npc: gears.base.Character = self.elements["NPC"]
        if npc.get_reaction_score(camp.pc, camp) > 30:
            mylist.append(Offer(
                "[Hey] I wanted to let you know how much I appreciate being a part of this team.",
                (context.HELLO, context.INFO),
                subject=self, subject_start=True, allow_generics=False
            ))
        else:
            mylist.append(Offer(
                "[Hey] I thought I should thank you for letting me be a part of this team.",
                (context.HELLO, context.INFO),
                subject=self, subject_start=True, allow_generics=False
            ))
        mylist.append(Offer(
            "I will keep doing my best to be a good lancemate. [LETS_CONTINUE]",
            (context.CUSTOM,), subject=self, data={"reply": "[OK] You've been pretty useful."},
            effect=self._set_colleague
        ))
        if npc.get_reaction_score(camp.pc, camp) > 0:
            mylist.append(Offer(
                "[GOOD] You make me feel like I really belong here. [LETS_CONTINUE]",
                (context.CUSTOM,), subject=self,
                data={"reply": "I appreciate your help, but more than that I just like having you around."},
                effect=self._set_friend
            ))
        if npc.get_reaction_score(camp.pc, camp) > 60:
            mylist.append(Offer(
                "Maybe I am... but we can talk more about that later. [LETS_CONTINUE]",
                (context.CUSTOM,), subject=self, data={
                    "reply": "Are you, like, confessing your feelings to me now? Because I have some feelings to confess too..."},
                effect=self._set_crush
            ))
        return mylist

    def _set_colleague(self, camp):
        self.elements["NPC"].relationship.role = relationships.R_COLLEAGUE
        self.elements["NPC"].statline[gears.stats.Concentration] += 2
        self.proper_end_plot(camp)

    def _set_friend(self, camp):
        self.elements["NPC"].relationship.role = relationships.R_FRIEND
        self.elements["NPC"].statline[gears.stats.Athletics] += 2
        self.proper_end_plot(camp)

    def _set_crush(self, camp):
        self.elements["NPC"].relationship.role = relationships.R_CRUSH
        self.elements["NPC"].statline[gears.stats.Vitality] += 2
        self.proper_end_plot(camp)


class LD_MercenaryColleague(LMMissionPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    CASH_REWARD = 200
    ENEMY_FACTIONS = (gears.factions.AegisOverlord, gears.factions.ClanIronwind, gears.factions.KettelIndustries,
                      gears.factions.RegExCorporation, gears.factions.BioCorp, gears.factions.BoneDevils,
                      gears.factions.BladesOfCrihna, gears.factions.AegisOverlord, gears.factions.ClanIronwind)

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.elements["ENEMY_FACTION"] = random.choice(self.ENEMY_FACTIONS)
        self.prep_mission(nart.camp)
        self.started_convo = False
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.relationship.expectation == relationships.E_MERCENARY
                    and candidate.relationship.role is None
            )

    def METROSCENE_ENTER(self, camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert(
                "{NPC}'s phone rings. After a short conversation, {NPC.gender.subject_pronoun} turns to you.".format(
                    **self.elements))
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.PROPOSAL)))
            self.started_convo = True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.mission_active:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "I just got a surprise call from [foaf]. We've been offered a high priority mission to fight {}, and it comes with a 200% bonus.".format(
                    self.elements["ENEMY_FACTION"].name),
                (context.HELLO, context.PROPOSAL),
                subject=self, subject_start=True, allow_generics=False
            ))
            mylist.append(Offer(
                "[GOOD] I'll forward the details to the rest of the lance.",
                (context.CUSTOM,), subject=self, data={"reply": "[MISSION:ACCEPT]"},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "[YOU_ARE_THE_BOSS]",
                (context.CUSTOM,), subject=self, data={"reply": "[MISSION:DENY]"},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self, camp):
        self.elements["NPC"].relationship.role = relationships.R_COLLEAGUE
        self.mission_active = True
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def _reject_offer(self, camp):
        self.elements["NPC"].relationship.role = relationships.R_COLLEAGUE
        self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
            "you rejected the double pay mission", "I didn't accept the mission you found", -10,
            (gears.relationships.MEM_Ideological,)
        ))
        self.proper_end_plot(camp, False)

    def win_mission(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        if npc in camp.party and not npc.is_destroyed():
            ghcutscene.SimpleMonologueDisplay(
                "That went well. Time to get paid.",
                npc.get_root())(camp)
            npc.statline[gears.stats.Charm] += 1

        self.proper_end_plot(camp)


class LD_DutyColleagueMission(LMMissionPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True
    MISSION_OBJECTIVES = (missionbuilder.BAMO_RESCUE_NPC, missionbuilder.BAMO_DEFEAT_COMMANDER)
    CASH_REWARD = 100
    EXPERIENCE_REWARD = 200

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.register_element("MENTOR", gears.selector.random_character(npc.renown + 20, combatant=True, camp=nart.camp,
                                                                        age=random.randint(40, 65)))
        self.elements["ENEMY_FACTION"] = plotutility.RandomBanditCircle(nart.camp)
        self.add_sub_plot(nart, "NPC_VACATION", ident="FREEZER")
        self.prep_mission(nart.camp)
        self.started_convo = False
        self.training = services.SkillTrainer(
            (gears.stats.MechaPiloting, gears.stats.MechaGunnery, gears.stats.MechaFighting))
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.relationship.role == gears.relationships.R_COLLEAGUE and
                    gears.personality.Duty in candidate.personality
            )

    def METROSCENE_ENTER(self, camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {METROSCENE}, {NPC} rushes over to talk.".format(**self.elements))
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.PROPOSAL)))
            self.started_convo = True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.mission_active:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "I just got a message from my mentor, {MENTOR}; {MENTOR.gender.subject_pronoun} is in trouble and I need to go help immediately. Sorry for the short notice.".format(
                    **self.elements),
                (context.HELLO, context.PROPOSAL),
                subject=self, subject_start=True, allow_generics=False
            ))
            mylist.append(Offer(
                "[THANK_YOU] [LETS_START_MECHA_MISSION]".format(**self.elements),
                (context.CUSTOM,), subject=self, data={"reply": "If your mentor is in trouble, we'll all go to help."},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "Thanks. I'll see you later.",
                (context.CUSTOM,), subject=self, data={"reply": "Good luck on your mission."},
                effect=self._reject_offer
            ))
        return mylist

    def prep_mission(self, camp: gears.GearHeadCampaign):
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, self.MISSION_NAME.format(**self.elements),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            enemy_faction=self.elements.get("ENEMY_FACTION"),
            rank=camp.renown, objectives=self.MISSION_OBJECTIVES,
            cash_reward=self.CASH_REWARD, experience_reward=self.EXPERIENCE_REWARD,
            on_win=self.win_mission, on_loss=self.lose_mission,
            custom_elements={missionbuilder.BAME_RESCUENPC: self.elements["MENTOR"]}
        )

    def _accept_offer(self, camp):
        self.elements["NPC"].relationship.role = relationships.R_FRIEND
        self.mission_active = True

    def _reject_offer(self, camp):
        plotutility.AutoLeaver(self.elements["NPC"])(camp)
        self.subplots["FREEZER"].freeze_now(camp)
        self.proper_end_plot(camp, False)

    def win_mission(self, camp: gears.GearHeadCampaign):
        self.mission_seed = None
        npc: gears.base.Character = self.elements["MENTOR"]
        scene: gears.GearHeadScene = self.elements["METROSCENE"]
        npc.place(scene, team=scene.civilian_team)
        self.proper_non_end(camp)

    def MENTOR_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        if not self.mission_seed:
            mylist.append(Offer(
                "See if you learn anything.",
                context=ContextTag((context.OPEN_SCHOOL,)), effect=self.training,
            ))

        return mylist


class LD_JuniorQuestions(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.started_conversation = False
        return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return not candidate.relationship.expectation and candidate.renown < 20 and candidate.relationship.attitude in (
            relationships.A_JUNIOR, None)

    def t_UPDATE(self, camp):
        if not self.started_conversation:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {}, {} pulls you aside for a conversation.".format(camp.scene, npc))
            npc.relationship.attitude = relationships.A_JUNIOR
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.QUERY)))
            self.started_conversation = True

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "[CAN_I_ASK_A_QUESTION]",
            (context.HELLO, context.QUERY), allow_generics=False
        ))
        mylist.append(Offer(
            "I'm pretty new at this cavalier business, and I don't have nearly as much sense for it as you do. What do I need to do to become a real cavalier?",
            (context.QUERY,), subject=self, subject_start=True
        ))
        mylist.append(Offer(
            "[THANKS_FOR_ADVICE] Yes, I see now that the purpose of a cavalier is to earn the fanciest toys available. I won't forget your advice!",
            (context.ANSWER,), subject=self,
            data={"reply": "Just keep finding missions and keep getting paid. Then buy a bigger robot."},
            effect=self._merc_answer
        ))
        mylist.append(Offer(
            "[THANKS_FOR_ADVICE] To be a cavalier is a journey, not a destination. I promise that I will keep doing my best!",
            (context.ANSWER,), subject=self, data={
                "reply": "Keep practicing, keep striving, and each day you move closer to the best pilot you can be."},
            effect=self._pro_answer
        ))
        mylist.append(Offer(
            "[THANKS_FOR_ADVICE] With gigantic megaweapons come gigantic responsibilities... I see that now. I promise I won't let you down!",
            (context.ANSWER,), subject=self, data={
                "reply": "We do this so that we can help people. If you make life better for one person, you've succeeded."},
            effect=self._help_answer
        ))
        mylist.append(Offer(
            "[THANKS_FOR_ADVICE] In order to fight for great justice, I must first conquer my own inner demons. I promise not to forget your ephemeral wisdom!",
            (context.ANSWER,), subject=self,
            data={"reply": "There are a lot of bad things in this world; just make sure you don't become one of them."},
            effect=self._just_answer
        ))
        mylist.append(Offer(
            "Thanks, I guess? I was hoping that you'd be able to give me some great insight, but it seems we're all working this out for ourselves. At least I feel a bit more confident now.",
            (context.ANSWER,), subject=self,
            data={"reply": "[I_DONT_KNOW] And besides, you've proven yourself as a lancemate already."},
            effect=self._fel_answer
        ))
        return mylist

    def _merc_answer(self, camp):
        self.elements["NPC"].relationship.expectation = relationships.E_MERCENARY
        if gears.personality.Glory in self.elements["NPC"].personality:
            self.elements["NPC"].statline[gears.stats.Vitality] += 1
        else:
            self.elements["NPC"].personality.add(gears.personality.Glory)
        self.proper_end_plot(camp)

    def _pro_answer(self, camp):
        self.elements["NPC"].relationship.expectation = relationships.E_PROFESSIONAL
        if gears.personality.Duty in self.elements["NPC"].personality:
            self.elements["NPC"].statline[gears.stats.Concentration] += 1
        else:
            self.elements["NPC"].personality.add(gears.personality.Duty)
        self.proper_end_plot(camp)

    def _help_answer(self, camp):
        self.elements["NPC"].relationship.expectation = relationships.E_GREATERGOOD
        if gears.personality.Peace in self.elements["NPC"].personality:
            self.elements["NPC"].statline[gears.stats.Athletics] += 1
        else:
            self.elements["NPC"].personality.add(gears.personality.Peace)
        self.proper_end_plot(camp)

    def _just_answer(self, camp):
        self.elements["NPC"].relationship.expectation = relationships.E_IMPROVER
        if gears.personality.Justice in self.elements["NPC"].personality:
            self.elements["NPC"].statline[gears.stats.MechaPiloting] += 1
        else:
            self.elements["NPC"].personality.add(gears.personality.Justice)
        self.proper_end_plot(camp)

    def _fel_answer(self, camp):
        self.elements["NPC"].relationship.attitude = relationships.A_FRIENDLY
        if gears.personality.Fellowship in self.elements["NPC"].personality:
            self.elements["NPC"].dole_experience(200, camp.pc.TOTAL_XP)
            camp.pc.dole_experience(200, camp.pc.TOTAL_XP)
        else:
            self.elements["NPC"].personality.add(gears.personality.Fellowship)
        self.proper_end_plot(camp)


class LD_CareerChange(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene)
        self.new_job = self._get_new_job(npc)
        return True

    def _get_new_job(self, npc):
        candidates = list()
        if gears.personality.Peace in npc.personality:
            candidates += [job for job in list(gears.jobs.ALL_JOBS.values()) if
                           gears.tags.Medic in job.tags and job.name != npc.job.name]
        if gears.personality.Glory in npc.personality:
            candidates += [job for job in list(gears.jobs.ALL_JOBS.values()) if
                           gears.tags.Media in job.tags and job.name != npc.job.name]
        if gears.personality.Fellowship in npc.personality:
            candidates += [job for job in list(gears.jobs.ALL_JOBS.values()) if
                           gears.tags.Craftsperson in job.tags and job.name != npc.job.name]
        if gears.personality.Duty in npc.personality:
            candidates += [job for job in list(gears.jobs.ALL_JOBS.values()) if
                           gears.tags.Military in job.tags and job.name != npc.job.name]
        if gears.personality.Justice in npc.personality:
            candidates += [job for job in list(gears.jobs.ALL_JOBS.values()) if
                           gears.tags.Academic in job.tags and job.name != npc.job.name]
        if not candidates:
            candidates += [job for job in list(gears.jobs.ALL_JOBS.values()) if
                           gears.tags.Adventurer in job.tags and job.name != npc.job.name]
        return random.choice(candidates)

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.job and
                    candidate.relationship.expectation == gears.relationships.E_IMPROVER and
                    candidate.relationship.attitude == gears.relationships.A_FRIENDLY
            )

    def METROSCENE_ENTER(self, camp: gears.GearHeadCampaign):
        npc = self.elements["NPC"]
        pbge.alert(
            "As you enter {METROSCENE}, {NPC}'s phone beeps loudly; {NPC.gender.subject_pronoun} checks the screen and then gives a shout of joy.".format(
                **self.elements))

        self.started_convo = True

        npc.relationship.attitude = relationships.A_THANKFUL
        ghcutscene.SimpleMonologueDisplay(
            "I passed the test! I told you all that I was going to make a change, and now I have. From this point forward I'm an official certified {}!".format(
                self.new_job),
            npc.get_root())(camp)

        candidates = [npc2 for npc2 in camp.get_lancemates() if npc2 is not npc]
        if candidates:
            npc2 = random.choice(candidates)
            ghcutscene.SimpleMonologueDisplay(
                "Congratulations, {}!".format(npc),
                npc2.get_root())(camp, False)

        npc.job = self.new_job
        for sk in self.new_job.skills:
            npc.statline[sk] += 1

        for sk, bonus in self.new_job.skill_modifiers.items():
            if bonus > 0:
                npc.statline[sk] += bonus
            elif sk not in npc.statline:
                npc.statline[sk] += 1

        ghcutscene.SimpleMonologueDisplay(
            "Thanks! I wouldn't have been able to do this without your support.",
            npc.get_root())(camp, False)

        self.proper_end_plot(camp)


class LD_ThePurposeOfMoneyIsMecha(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.started_convo = False
        myscene = self.seek_element(nart, "GARAGE", self._is_good_scene, scope=self.elements["METROSCENE"])
        shopping_list = gears.selector.MechaShoppingList(
            max(gears.selector.calc_threat_points(npc.renown + 45), 350000), fac=npc.faction)
        self.best_list = sorted(shopping_list.best_choices + shopping_list.backup_choices, reverse=True,
                                key=lambda m: m.cost)

        return len(self.best_list) > 1

    def _is_good_scene(self, nart, candidate):
        return isinstance(candidate,
                          gears.GearHeadScene) and gears.tags.SCENE_GARAGE in candidate.attributes and gears.tags.SCENE_PUBLIC in candidate.attributes

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.relationship.role == gears.relationships.R_FRIEND and
                    candidate.relationship.expectation == gears.relationships.E_MERCENARY
            )

    def METROSCENE_ENTER(self, camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("You notice {NPC} gazing longingly at {GARAGE}.".format(**self.elements))
            ghcutscene.SimpleMonologueDisplay(
                "What good is money, if not to spend it on the best mecha available? [TIME_TO_UPGRADE_MECHA] Let's go to {GARAGE} and see what they have.".format(
                    **self.elements),
                npc)(camp)
            self.memo = pbge.memos.Memo("{NPC} wants to buy a new mecha.".format(**self.elements)
                                        , self.elements["GARAGE"]
                                        )
            self.started_convo = True

    def GARAGE_ENTER(self, camp):
        npc = self.elements["NPC"]
        ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.PROPOSAL)))

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        if camp.scene is self.elements["GARAGE"]:
            npc: gears.base.Character = self.elements["NPC"]
            mylist.append(Offer(
                "My favorite, I think, is the {}. I'm planning to buy that one.".format(
                    self.best_list[0].get_full_name()),
                (context.HELLO, context.PROPOSAL),
                subject=self, subject_start=True, allow_generics=False
            ))
            mylist.append(Offer(
                "Yes, I definitely made a good call. I'll take it!".format(**self.elements),
                (context.CUSTOM,), subject=self, data={"reply": "[AGREE]"},
                effect=self._buy_zeroth
            ))

            mylist.append(Offer(
                "You know what? You might be right. I'm going to pick that one instead.".format(**self.elements),
                (context.CUSTOM,), subject=self,
                data={"reply": "I think the {} suits you better.".format(self.best_list[1].get_full_name())},
                effect=self._buy_first
            ))

            if len(self.best_list) > 2:
                mylist.append(Offer(
                    "I never thought of that. You've changed my mind... the {} is the mecha for me.".format(
                        self.best_list[2].get_full_name()),
                    (context.CUSTOM,), subject=self,
                    data={"reply": "The {} is more [adjective].".format(self.best_list[2].get_full_name())},
                    effect=self._buy_second
                ))

            if len(self.best_list) > 3:
                mylist.append(Offer(
                    "Let me check that... best in reader satisfaction and post-sales maintenance. Neat. Looks like I'm getting a {}.".format(
                        self.best_list[3].get_full_name()),
                    (context.CUSTOM,), subject=self,
                    data={"reply": "CavNet's NT157 survey put the {} at the top.".format(
                        self.best_list[3].get_full_name())},
                    effect=self._buy_third
                ))

        return mylist

    def _buy_zeroth(self, camp):
        self._finalize_purchase(camp, self.best_list[0])

    def _buy_first(self, camp):
        self._finalize_purchase(camp, self.best_list[1])

    def _buy_second(self, camp):
        self._finalize_purchase(camp, self.best_list[2])

    def _buy_third(self, camp):
        self._finalize_purchase(camp, self.best_list[3])

    def _finalize_purchase(self, camp, mek):
        npc: gears.base.Character = self.elements["NPC"]
        npc.mecha_pref = mek.get_full_name()
        npc.relationship.data["mecha_level_bonus"] = npc.relationship.data.get("mecha_level_bonus", 0) + 25
        npc.relationship.expectation = gears.relationships.E_MECHANIAC
        # Auto leave the party, then auto join the party.
        plotutility.AutoLeaver(npc)(camp)
        plotutility.AutoJoiner(npc)(camp)
        self.proper_end_plot(camp)


class DDLD_LackingVirtue(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.started_conversation = False
        virtues = self.get_missing_virtues(nart.camp)
        if virtues:
            self.elements["VIRTUE"] = random.choice(list(virtues))
            # print(self.elements["VIRTUE"])
            return True

    def _is_good_npc(self, nart, candidate):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return not candidate.relationship.role and not candidate.relationship.attitude

    def get_missing_virtues(self, camp: gears.GearHeadCampaign):
        virtues = set(gears.personality.VIRTUES)
        for pc in camp.get_active_party():
            virtues = virtues.difference(pc.personality)
        return virtues

    def t_UPDATE(self, camp):
        if not self.started_conversation:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {}, {} pulls you aside for a conversation.".format(camp.scene, npc))
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.QUERY)))
            self.started_conversation = True

    OATH = {
        gears.personality.Peace: "to do right to all, and wrong no one",
        gears.personality.Glory: "to strive every moment of my life to make myself better and better, to the best of my ability, for the benefit of all",
        gears.personality.Justice: "to think of the right and lend all my assistance to those who need it, with no regard for anything but justice",
        gears.personality.Fellowship: "to be considerate of my fellow citizens and my associates in everything I say and do",
        gears.personality.Duty: "to face what comes with a smile, without loss of courage"
    }

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "[CAN_I_ASK_A_QUESTION]",
            (context.HELLO, context.QUERY), allow_generics=False
        ))
        mylist.append(Offer(
            "I haven't been in this lance long, so I want to understand how you run things. I've always thought that {} is the most important part of being a cavalier: {}. Do you agree?".format(
                self.elements["VIRTUE"].name, self.OATH[self.elements["VIRTUE"]]),
            (context.QUERY,), subject=self, subject_start=True
        ))
        mylist.append(Offer(
            "You seem to be an open minded leader. I look forward to working together.",
            (context.ANSWER,), subject=self, data={"reply": "[AGREE]"},
            effect=self._agree_answer
        ))
        mylist.append(Offer(
            "I see. You are not afraid to state your opinions directly, though I get the impression that we are going to butt heads in the future.",
            (context.ANSWER,), subject=self, data={"reply": "[DISAGREE]"},
            effect=self._disagree_answer
        ))
        if camp.pc.get_stat(gears.stats.Knowledge) > 12:
            mylist.append(Offer(
                "A wise answer. I look forward to working with you.",
                (context.ANSWER,), subject=self,
                data={"reply": "No virtue is most important; the five cavalier virtues must be considered together."},
                effect=self._fancy_answer
            ))
        elif camp.pc.get_stat(gears.stats.Knowledge) < 10:
            mylist.append(Offer(
                "I see. Your non-answer tells me all I need to know about your leadership style.",
                (context.ANSWER,), subject=self,
                data={"reply": "There are many questions about things that may be most important, or not."},
                effect=self._non_answer
            ))

        return mylist

    def _agree_answer(self, camp):
        self.elements["NPC"].relationship.role = relationships.R_COLLEAGUE
        self.elements["NPC"].personality.add(self.elements["VIRTUE"])
        self.proper_end_plot(camp)

    def _disagree_answer(self, camp):
        self.elements["NPC"].relationship.attitude = relationships.A_RESENT
        self.elements["NPC"].relationship.reaction_mod -= 10
        self.elements["NPC"].personality.add(self.elements["VIRTUE"])
        self.proper_end_plot(camp)

    def _fancy_answer(self, camp):
        self.elements["NPC"].relationship.attitude = relationships.A_JUNIOR
        self.elements["NPC"].relationship.role = relationships.R_COLLEAGUE
        self.elements["NPC"].personality.add(self.elements["VIRTUE"])
        self.proper_end_plot(camp)

    def _non_answer(self, camp):
        self.elements["NPC"].relationship.attitude = relationships.A_DESPAIR
        self.elements["NPC"].relationship.reaction_mod -= 10
        self.elements["NPC"].personality.add(self.elements["VIRTUE"])
        self.proper_end_plot(camp, False)


class LMD_PassingJudgment(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.started_convo = False
        return True

    def _is_good_npc(self, nart, candidate: gears.base.Character):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    candidate.relationship.role == relationships.R_CHAPERONE and
                    candidate.relationship.missions_together > 10 and
                    candidate.relationship.attitude in (
                    relationships.A_JUNIOR, relationships.A_DISTANT, relationships.A_RESENT)
            )

    def METROSCENE_ENTER(self, camp: gears.GearHeadCampaign):
        if not self.started_convo:
            npc: gears.base.Character = self.elements["NPC"]
            pbge.alert("As you enter {METROSCENE}, {NPC} pulls you aside for a private talk.".format(**self.elements))
            if npc.get_reaction_score(camp.pc, camp) > 20:
                ghcutscene.SimpleMonologueDisplay(
                    "When we started, I was suspicious of you. I didn't know what kind of person you were. But now, after all we've been through, I do know. I want you to know that I believe in you and I'm glad to be your lancemate.",
                    npc
                )(camp)
                npc.relationship.role = relationships.R_COLLEAGUE
                npc.relationship.attitude = relationships.A_FRIENDLY
                camp.dole_xp(200)
                self.proper_end_plot(camp)
            else:
                ghcutscene.SimpleMonologueDisplay(
                    "When we started, I was suspicious of you. I didn't know what kind of person you were. But now, I do know, and I no longer want anything to do with you. If we ever meet again, it will be on opposite sides of the battlefield.",
                    npc
                )(camp)
                npc.relationship.role = relationships.R_ADVERSARY
                npc.relationship.attitude = relationships.A_RESENT
                if relationships.RT_LANCEMATE in npc.relationship.tags:
                    npc.relationship.tags.remove(relationships.RT_LANCEMATE)
                plotutility.AutoLeaver(npc)(camp)
                camp.freeze(npc)
                npc.relationship.history.append(gears.relationships.Memory(
                    "I quit your lance", "you quit my lance", -10,
                    (gears.relationships.MEM_Ideological,)
                ))
                self.proper_end_plot(camp)

            self.started_convo = True


class LMD_GotMyEyeOnYou(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.started_convo = False
        return True

    def _is_good_npc(self, nart, candidate: gears.base.Character):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    nart.camp.pc.has_badge("Criminal") and
                    gears.tags.Police in candidate.get_tags() and
                    candidate.relationship.role in (None, gears.relationships.R_OPPONENT)
            )

    def METROSCENE_ENTER(self, camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {METROSCENE}, {NPC} pulls you aside for a private talk.".format(**self.elements))
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.PERSONAL)))
            self.started_convo = True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        mylist.append(Offer(
            "I've been checking your history. I found out all about your criminal activities.".format(**self.elements),
            (context.HELLO, context.PERSONAL),
            subject=self, subject_start=True, allow_generics=False
        ))

        mylist.append(Offer(
            "Regardless, I'm going to be keeping my eye on you.".format(**self.elements),
            (context.CUSTOM,), subject=self, data={"reply": "That was in the past. I'm not doing that anymore."},
            effect=self._keep_eye_on
        ))

        mylist.append(Offer(
            "Not yet; I'm going to stay around for a while so I can keep an eye on you.".format(**self.elements),
            (context.CUSTOM,), subject=self, data={"reply": "Well, you can quit the lance if you want to."}
        ))

        mylist.append(Offer(
            "Oh I plan to. I'm going to be so happy that it'll scare you.",
            (context.CUSTOMREPLY,), subject="for a while so I can keep an eye on you",
            data={"reply": "Do whatever makes you happy."},
            effect=self._keep_eye_on
        ))

        mylist.append(Offer(
            "Fine. I'll see you around, [PC].",
            (context.CUSTOMREPLY,), subject="for a while so I can keep an eye on you",
            data={"reply": "No, seriously, you should quit the lance."},
            effect=self._quit_lance
        ))

        return mylist

    def _keep_eye_on(self, camp):
        self.elements["NPC"].relationship.role = gears.relationships.R_CHAPERONE
        self.elements["NPC"].dole_experience(200)
        self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
            "I found out about your criminal past", "You went snooping around in my business", -10,
            (gears.relationships.MEM_Ideological,)
        ))

        self.proper_end_plot(camp, False)

    def _quit_lance(self, camp):
        self.elements["NPC"].relationship.role = gears.relationships.R_ADVERSARY
        self.elements["NPC"].dole_experience(200)
        self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
            "I found out about your criminal past", "You went snooping around in my business", -25,
            (gears.relationships.MEM_Ideological,)
        ))
        plotutility.AutoLeaver(self.elements["NPC"])(camp)
        self.proper_end_plot(camp, False)


class LMD_SociableSorting(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.started_convo = False
        return True

    def _is_good_npc(self, nart, candidate: gears.base.Character):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    gears.personality.Sociable in candidate.personality and
                    not candidate.relationship.attitude
            )

    def METROSCENE_ENTER(self, camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {METROSCENE}, {NPC} strikes up a conversation.".format(**self.elements))
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.PERSONAL)))
            self.started_convo = True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        mylist.append(Offer(
            "[CAN_I_ASK_A_QUESTION]".format(**self.elements),
            (context.HELLO, context.PERSONAL),
            subject=self, subject_start=True, allow_generics=False
        ))

        if self.elements["NPC"].renown > camp.pc.renown:
            mylist.append(Offer(
                "I can't help but notice that you're not quite as experienced a pilot as I am. Would it be alright if I offered you a bit of constructive advice from time to time?".format(
                    **self.elements),
                (context.CUSTOM,), subject=self, data={"reply": "[HELLOQUERY:QUERY]"}
            ))
        else:
            mylist.append(Offer(
                "You have way more experience than I do. Do you think that maybe I could ask you for advice every once in a while?".format(
                    **self.elements),
                (context.CUSTOM,), subject=self, data={"reply": "[HELLOQUERY:QUERY]"}
            ))

        mylist.append(Offer(
            "[GOOD] I don't actually have anything else to say right now, but I'll let you know if I think of something.",
            (context.CUSTOMREPLY,), subject=self, data={"reply": "[YES_YOU_CAN]"},
            effect=self._accept
        ))

        mylist.append(Offer(
            "I see. Well, I know that it's one of my bad habits to talk too much, so I can promise you that I will try to keep it under control while I'm a part of this lance.",
            (context.CUSTOMREPLY,), subject=self, data={"reply": "I'd rather you didn't..."},
            effect=self._deny
        ))

        return mylist

    def _accept(self, camp):
        if self.elements["NPC"].renown > camp.pc.renown:
            self.elements["NPC"].relationship.attitude = gears.relationships.A_SENIOR
        else:
            self.elements["NPC"].relationship.attitude = gears.relationships.A_JUNIOR
        self.elements["NPC"].dole_experience(200, gears.stats.MechaPiloting)
        camp.pc.dole_experience(200, gears.stats.MechaPiloting)
        self.proper_end_plot(camp, True)

    def _deny(self, camp):
        self.elements["NPC"].relationship.attitude = gears.relationships.A_DISTANT
        self.elements["NPC"].dole_experience(200, gears.stats.Concentration)
        camp.pc.dole_experience(200, gears.stats.Vitality)
        self.proper_end_plot(camp, False)


class LMD_ShyFolk(LMPlot):
    LABEL = "LANCEDEV"
    active = True
    scope = True

    def custom_init(self, nart):
        npc = self.seek_element(nart, "NPC", self._is_good_npc, scope=nart.camp.scene, lock=True)
        self.started_convo = False
        return True

    def _is_good_npc(self, nart, candidate: gears.base.Character):
        if self.npc_is_ready_for_lancedev(nart.camp, candidate):
            return (
                    gears.personality.Shy in candidate.personality and
                    not candidate.relationship.attitude
            )

    def METROSCENE_ENTER(self, camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert(
                "As you enter {METROSCENE}, you notice {NPC} staring into the distance as though lost in thought.".format(
                    **self.elements))
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=pbge.dialogue.Cue((context.HELLO, context.PERSONAL)))
            self.started_convo = True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        mylist.append(Offer(
            "...".format(**self.elements),
            (context.HELLO, context.PERSONAL),
            subject=self, subject_start=True, allow_generics=False
        ))

        mylist.append(Offer(
            "Not right now, no. If I have anything to say I'll say it.".format(**self.elements),
            (context.CUSTOM,), subject=self, data={"reply": "Is there anything you want to talk about?"}
        ))

        mylist.append(Offer(
            "That's right, I can. And if I choose to do so you'll be the first to know.",
            (context.CUSTOMREPLY,), subject=self, data={"reply": "Come on, you can tell me what's on your mind."},
            effect=self._asky_reply
        ))

        mylist.append(Offer(
            "No bother. Thanks for understanding.",
            (context.CUSTOMREPLY,), subject=self, data={"reply": "No worries. Sorry to bother you."},
            effect=self._easy_reply
        ))

        return mylist

    def _asky_reply(self, camp):
        self.elements["NPC"].relationship.attitude = gears.relationships.A_DISTANT
        self.elements["NPC"].dole_experience(200, gears.stats.Vitality)
        self.proper_end_plot(camp, False)

    def _easy_reply(self, camp):
        self.elements["NPC"].relationship.attitude = gears.relationships.A_DISTANT
        self.elements["NPC"].dole_experience(500, gears.stats.Concentration)
        self.proper_end_plot(camp, True)
