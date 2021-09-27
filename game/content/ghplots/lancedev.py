# Character development plots for lancemates.
from pbge.plots import Plot, PlotState
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
from gears import relationships
import pbge
from .dd_main import DZDRoadMapExit,RoadNode
import random
from game.content import gharchitecture,ghwaypoints,plotutility,ghterrain,backstory,ghcutscene, dungeonmaker
from . import missionbuilder,dd_customobjectives
from game.memobrowser import Memo


#  Required elements: METRO, METROSCENE, MISSION_GATE

class LMPlot(Plot):
    LANCEDEV_PLOT = True
    UNIQUE = True
    # Contains convenience methods for lancemates.
    def npc_is_ready_for_lancedev(self, camp, npc):
        return (isinstance(npc, gears.base.Character) and npc in camp.party and npc.relationship
                and npc.relationship.can_do_development())

    def t_START(self,camp):
        npc = self.elements["NPC"]
        if self.LANCEDEV_PLOT and (npc.is_destroyed() or npc not in camp.party):
            self.end_plot(camp)

    def proper_end_plot(self,camp,improve_react=True):
        self.elements["NPC"].relationship.development_plots += 1
        if improve_react:
            self.elements["NPC"].relationship.reaction_mod += random.randint(1,10)
        self.end_plot(camp)

    def proper_non_end(self,camp,improve_react=True):
        # This plot is not ending, but it's entering a sort of torpor phase where we don't want it interfering
        # with other DZD_LANCEDEV plots. For instance: if a plot adds a permanent new location to the world, you
        # might not want to end the plot but you will want to unlock the NPC and whatever else.
        self.elements["NPC"].relationship.development_plots += 1
        self.LANCEDEV_PLOT = False
        if improve_react:
            self.elements["NPC"].relationship.reaction_mod += random.randint(1,10)
        if "NPC" in self.locked_elements:
            self.locked_elements.remove("NPC")


class LMMissionPlot(LMPlot):
    mission_active = False
    mission_seed = None
    MISSION_OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_CAPTURE_BUILDINGS)
    CASH_REWARD = 150
    EXPERIENCE_REWARD = 150
    MISSION_NAME = "{NPC}'s Mission"

    def prep_mission(self, camp: gears.GearHeadCampaign):
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(camp.scene.get_metro_scene())
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, self.MISSION_NAME.format(**self.elements),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            enemy_faction=self.elements.get("ENEMY_FACTION"),
            rank=camp.renown, objectives=self.MISSION_OBJECTIVES,
            cash_reward=self.CASH_REWARD, experience_reward=self.EXPERIENCE_REWARD,
            on_win=self.win_mission, on_loss=self.lose_mission,
            scenegen=sgen, architecture=archi
        )

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_active and self.mission_seed:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

    def win_mission(self, camp):
        self.proper_end_plot(camp)

    def lose_mission(self, camp):
        self.proper_end_plot(camp)


# The actual plots...

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
                candidate.relationship.attitude in (relationships.A_JUNIOR,relationships.A_DISTANT,relationships.A_RESENT)
            )

    def METROSCENE_ENTER(self,camp: gears.GearHeadCampaign):
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
                candidate.relationship.role in (None,gears.relationships.R_OPPONENT)
            )

    def METROSCENE_ENTER(self,camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {METROSCENE}, {NPC} pulls you aside for a private talk.".format(**self.elements))
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.PERSONAL)))
            self.started_convo = True

    def NPC_offers(self,camp: gears.GearHeadCampaign):
        mylist = list()
        mylist.append(Offer(
            "I've been checking your history. I found out all about your criminal activities.".format(**self.elements),
            (context.HELLO,context.PERSONAL),
            subject=self, subject_start=True, allow_generics=False
        ))

        mylist.append(Offer(
            "Regardless, I'm going to be keeping my eye on you.".format(**self.elements),
            (context.CUSTOM,),subject=self,data={"reply": "That was in the past. I'm not doing that anymore."},
            effect=self._keep_eye_on
        ))

        mylist.append(Offer(
            "Not yet; I'm going to stay around for a while so I can keep an eye on you.".format(**self.elements),
            (context.CUSTOM,),subject=self,data={"reply": "Well, you can quit the lance if you want to."}
        ))

        mylist.append(Offer(
            "Oh I plan to. I'm going to be so happy that it'll scare you.",
            (context.CUSTOMREPLY,),subject="for a while so I can keep an eye on you",data={"reply": "Do whatever makes you happy."},
            effect=self._keep_eye_on
        ))

        mylist.append(Offer(
            "Fine. I'll see you around, [audience].",
            (context.CUSTOMREPLY,),subject="for a while so I can keep an eye on you",data={"reply": "No, seriously, you should quit the lance."},
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

        self.proper_end_plot(camp,False)

    def _quit_lance(self, camp):
        self.elements["NPC"].relationship.role = gears.relationships.R_ADVERSARY
        self.elements["NPC"].dole_experience(200)
        self.elements["NPC"].relationship.history.append(gears.relationships.Memory(
            "I found out about your criminal past", "You went snooping around in my business", -25,
            (gears.relationships.MEM_Ideological,)
        ))
        plotutility.AutoLeaver(self.elements["NPC"])(camp)
        self.proper_end_plot(camp,False)


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

    def METROSCENE_ENTER(self,camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {METROSCENE}, {NPC} strikes up a conversation.".format(**self.elements))
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.PERSONAL)))
            self.started_convo = True

    def NPC_offers(self,camp: gears.GearHeadCampaign):
        mylist = list()
        mylist.append(Offer(
            "[CAN_I_ASK_A_QUESTION]".format(**self.elements),
            (context.HELLO,context.PERSONAL),
            subject=self, subject_start=True, allow_generics=False
        ))

        if self.elements["NPC"].renown > camp.pc.renown:
            mylist.append(Offer(
                "I can't help but notice that you're not quite as experienced a pilot as I am. Would it be alright if I offered you a bit of constructive advice from time to time?".format(**self.elements),
                (context.CUSTOM,),subject=self,data={"reply": "[HELLOQUERY:QUERY]"}
            ))
        else:
            mylist.append(Offer(
                "You have way more experience than I do. Do you think that maybe I could ask you for advice every once in a while?".format(**self.elements),
                (context.CUSTOM,),subject=self,data={"reply": "[HELLOQUERY:QUERY]"}
            ))

        mylist.append(Offer(
            "[GOOD] I don't actually have anything else to say right now, but I'll let you know if I think of something.",
            (context.CUSTOMREPLY,),subject=self,data={"reply": "[YES_YOU_CAN]"},
            effect=self._accept
        ))

        mylist.append(Offer(
            "I see. Well, I know that it's one of my bad habits to talk too much, so I can promise you that I will try to keep it under control while I'm a part of this lance.",
            (context.CUSTOMREPLY,),subject=self,data={"reply": "I'd rather you didn't..."},
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
        self.proper_end_plot(camp,True)

    def _deny(self, camp):
        self.elements["NPC"].relationship.attitude = gears.relationships.A_DISTANT
        self.elements["NPC"].dole_experience(200, gears.stats.Concentration)
        camp.pc.dole_experience(200, gears.stats.Vitality)
        self.proper_end_plot(camp,False)



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

    def METROSCENE_ENTER(self,camp):
        if not self.started_convo:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {METROSCENE}, you notice {NPC} staring into the distance as though lost in thought.".format(**self.elements))
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.PERSONAL)))
            self.started_convo = True

    def NPC_offers(self,camp: gears.GearHeadCampaign):
        mylist = list()
        mylist.append(Offer(
            "...".format(**self.elements),
            (context.HELLO,context.PERSONAL),
            subject=self, subject_start=True, allow_generics=False
        ))

        mylist.append(Offer(
            "Not right now, no. If I have anything to say I'll say it.".format(**self.elements),
            (context.CUSTOM,),subject=self,data={"reply": "Is there anything you want to talk about?"}
        ))

        mylist.append(Offer(
            "That's right, I can. And if I choose to do so you'll be the first to know.",
            (context.CUSTOMREPLY,),subject=self,data={"reply": "Come on, you can tell me what's on your mind."},
            effect=self._asky_reply
        ))

        mylist.append(Offer(
            "No bother. Thanks for understanding.",
            (context.CUSTOMREPLY,),subject=self,data={"reply": "No worries. Sorry to bother you."},
            effect=self._easy_reply
        ))

        return mylist

    def _asky_reply(self, camp):
        self.elements["NPC"].relationship.attitude = gears.relationships.A_DISTANT
        self.elements["NPC"].dole_experience(200, gears.stats.Vitality)
        self.proper_end_plot(camp,False)

    def _easy_reply(self, camp):
        self.elements["NPC"].relationship.attitude = gears.relationships.A_DISTANT
        self.elements["NPC"].dole_experience(500, gears.stats.Concentration)
        self.proper_end_plot(camp,True)
