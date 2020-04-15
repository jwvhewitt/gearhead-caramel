# Character development plots for lancemates.
from pbge.plots import Plot
from pbge.dialogue import Offer, ContextTag
from game import teams, services, ghdialogue
from game.ghdialogue import context
import gears
from gears import relationships
import pbge
from .dd_main import DZDRoadMapExit,RoadNode
import random
from game.content import gharchitecture,ghwaypoints,plotutility,ghterrain,backstory,ghcutscene
from . import missionbuilder,dd_customobjectives

class LMPlot(Plot):
    # Contains convenience methods for lancemates.
    def npc_is_ready_for_lancedev(self, camp, npc):
        return (isinstance(npc, gears.base.Character) and npc in camp.party and npc.relationship
                and npc.relationship.can_do_development())

    def t_START(self,camp):
        npc = self.elements["NPC"]
        if npc.is_destroyed() or npc not in camp.party:
            self.end_plot(camp)

    def proper_end_plot(self,camp,improve_react=True):
        self.elements["NPC"].relationship.development_plots += 1
        if improve_react:
            self.elements["NPC"].relationship.reaction_mod += random.randint(1,10)
        self.end_plot(camp)


#   **********************
#   ***  DZD_LANCEDEV  ***
#   **********************
#  Required elements: METRO, METROSCENE, MISSION_GATE

class DDLD_SortingDuel(LMPlot):
    LABEL = "DZD_LANCEDEV"
    active = True
    scope = True
    def custom_init( self, nart ):
        npc = self.seek_element(nart,"NPC",self._is_good_npc,scope=nart.camp.scene,lock=True)
        self.started_conversation = False
        self.accepted_duel = False
        self.duel = missionbuilder.BuildAMissionSeed(
            nart.camp, "{}'s Duel".format(npc), (self.elements["METROSCENE"],self.elements["MISSION_GATE"]),
            rank = npc.renown, objectives = [dd_customobjectives.DDBAMO_DUEL_LANCEMATE],
            custom_elements={"LMNPC":npc},experience_reward=200,salvage_reward=False
        )
        return True

    def _is_good_npc(self,nart,candidate):
        if self.npc_is_ready_for_lancedev(nart.camp,candidate):
            return candidate.relationship.expectation == gears.relationships.E_PROFESSIONAL and not candidate.relationship.attitude

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.accepted_duel:
            thingmenu.add_item("Travel into the deadzone to have a practice match with {}".format(self.elements["NPC"]), self.duel)

    def t_START(self,camp):
        if not self.accepted_duel:
            super().t_START(camp)
        elif npc.is_destroyed():
            self.end_plot(camp)
        if self.duel.is_completed():
            npc = self.elements["NPC"]
            if self.duel.is_won():
                npc.relationship.attitude = gears.relationships.A_JUNIOR
                ghcutscene.SimpleMonologueDisplay("Your skills are incredible. It seems I have a lot to learn from you.",npc)(camp)
            else:
                npc.relationship.attitude = gears.relationships.A_SENIOR
                ghcutscene.SimpleMonologueDisplay("You show great potential, but you aren't quite there yet. Maybe someday we can have a rematch.", npc)(camp)
            self.proper_end_plot(camp)

    def t_UPDATE(self,camp):
        if not self.started_conversation:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {}, you notice {} giving you a quizzical look.".format(camp.scene,npc))
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.QUERY)))
            self.started_conversation = True

    def NPC_offers(self,camp):
        mylist = list()
        if not self.accepted_duel:
            mylist.append(Offer(
                "We've been traveling together for a while, but I still haven't figured out how you rank. [CAN_I_ASK_A_QUESTION]",
                (context.HELLO,context.QUERY),
            ))
            mylist.append(Offer(
                "I'm curious about how your combat skills compare to mine. How would you like to go out into the dead zone, find a nice uninhabited place, and have a friendly little practice duel?",
                (context.QUERY,),subject=self,subject_start=True
            ))
            mylist.append(Offer(
                "[GOOD] Whenever you're ready, we can head out of town and find an appropriate place.",
                (context.ANSWER,),subject=self,data={"reply":"[ACCEPT_CHALLENGE]"},
                effect=self._accept_offer
            ))
            mylist.append(Offer(
                "That's very disappointing. I never imagined you to be a coward, but as I said earlier I don't quite have you figured out yet...",
                (context.ANSWER,),subject=self,data={"reply":"No thanks, we have no time for that."},
                effect=self._reject_offer
            ))
        return mylist

    def _accept_offer(self,camp):
        self.accepted_duel = True

    def _reject_offer(self,camp):
        self.elements["NPC"].relationship.attitude = gears.relationships.A_RESENT
        self.proper_end_plot(camp,False)

class DDLD_JuniorQuestions(LMPlot):
    LABEL = "DZD_LANCEDEV"
    active = True
    scope = True
    def custom_init( self, nart ):
        npc = self.seek_element(nart,"NPC",self._is_good_npc,scope=nart.camp.scene,lock=True)
        self.started_conversation = False
        return True

    def _is_good_npc(self,nart,candidate):
        if self.npc_is_ready_for_lancedev(nart.camp,candidate):
            return not candidate.relationship.expectation and candidate.renown < 20 and candidate.relationship.attitude in (relationships.A_JUNIOR,None)

    def t_UPDATE(self,camp):
        if not self.started_conversation:
            npc = self.elements["NPC"]
            pbge.alert("As you enter {}, {} pulls you aside for a conversation.".format(camp.scene,npc))
            npc.relationship.attitude = relationships.A_JUNIOR
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=pbge.dialogue.Cue((context.HELLO,context.QUERY)))
            self.started_conversation = True

    def NPC_offers(self,camp):
        mylist = list()
        mylist.append(Offer(
            "[CAN_I_ASK_A_QUESTION]",
            (context.HELLO,context.QUERY),
        ))
        mylist.append(Offer(
            "I'm pretty new at this cavalier business, and I don't have nearly as much sense for it as you do. What do I need to do to become a real cavalier?",
            (context.QUERY,),subject=self,subject_start=True
        ))
        mylist.append(Offer(
            "[THANKS_FOR_ADVICE] Yes, I see now that the purpose of a cavalier is to earn the fanciest toys available. I won't forget your advice!",
            (context.ANSWER,),subject=self,data={"reply":"Just keep finding missions and keep getting paid. Then buy a bigger robot."},
            effect=self._merc_answer
        ))
        mylist.append(Offer(
            "[THANKS_FOR_ADVICE] To be a cavalier is a journey, not a destination. I promise that I will keep doing my best!",
            (context.ANSWER,),subject=self,data={"reply":"Keep practicing, keep striving, and each day you move closer to the best pilot you can be."},
            effect=self._pro_answer
        ))
        mylist.append(Offer(
            "[THANKS_FOR_ADVICE] With gigantic megaweapons come gigantic responsibilities... I see that now. I promise I won't let you down!",
            (context.ANSWER,),subject=self,data={"reply":"We do this so that we can help people. If you make life better for one person, you've succeeded."},
            effect=self._help_answer
        ))
        mylist.append(Offer(
            "[THANKS_FOR_ADVICE] In order to fight for great justice, I must first conquer my own inner demons. I promise not to forget your ephemeral wisdom!",
            (context.ANSWER,),subject=self,data={"reply":"There are a lot of bad things in this world; just make sure you don't become one of them."},
            effect=self._just_answer
        ))
        mylist.append(Offer(
            "Thanks, I guess? I was hoping that you'd be able to give me some great insight, but it seems we're all working this out for ourselves. At least I feel a bit more confident now.",
            (context.ANSWER,),subject=self,data={"reply":"[I_DONT_KNOW] And besides, you've proven yourself as a lancemate already."},
            effect=self._fel_answer
        ))
        return mylist

    def _merc_answer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_MERCENARY
        if gears.personality.Glory in self.elements["NPC"].personality:
            self.elements["NPC"].statline[gears.stats.Vitality] += 1
        else:
            self.elements["NPC"].personality.add(gears.personality.Glory)
        self.proper_end_plot(camp)

    def _pro_answer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_PROFESSIONAL
        if gears.personality.Duty in self.elements["NPC"].personality:
            self.elements["NPC"].statline[gears.stats.Concentration] += 1
        else:
            self.elements["NPC"].personality.add(gears.personality.Duty)
        self.proper_end_plot(camp)

    def _help_answer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_GREATERGOOD
        if gears.personality.Peace in self.elements["NPC"].personality:
            self.elements["NPC"].statline[gears.stats.Athletics] += 1
        else:
            self.elements["NPC"].personality.add(gears.personality.Peace)
        self.proper_end_plot(camp)

    def _just_answer(self,camp):
        self.elements["NPC"].relationship.expectation = relationships.E_IMPROVER
        if gears.personality.Justice in self.elements["NPC"].personality:
            self.elements["NPC"].statline[gears.stats.MechaPiloting] += 1
        else:
            self.elements["NPC"].personality.add(gears.personality.Justice)
        self.proper_end_plot(camp)

    def _fel_answer(self,camp):
        self.elements["NPC"].relationship.attitude = relationships.A_FRIENDLY
        if gears.personality.Fellowship in self.elements["NPC"].personality:
            self.elements["NPC"].dole_experience(200,camp.pc.TOTAL_XP)
            camp.pc.dole_experience(200,camp.pc.TOTAL_XP)
        else:
            self.elements["NPC"].personality.add(gears.personality.Fellowship)
        self.proper_end_plot(camp)

