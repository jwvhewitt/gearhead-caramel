import pbge
from pbge.plots import Plot, PlotState
from pbge.dialogue import Offer, ContextTag
from game.ghdialogue import context
import gears
import game.content.gharchitecture
import game.content.plotutility
import game.content.ghterrain
import random
from gears import relationships
from gears.relationships import Memory

class NoDevBattleConversation(Plot):
    # A conversation for mook NPCs who don't need any development.
    LABEL = "MC_NDBCONVERSATION"
    active = True
    scope = "LOCALE"

    def NPC_offers(self,camp):
        mylist = list()
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist


#  ********************************
#  ***   MC_ENEMY_DEVELOPMENT   ***
#  ********************************
# NPC: The enemy who needs character development
# LOCALE: The fight scene.

class BasicBattleConversation(Plot):
    # No real character development, but record the memory of this battle.
    LABEL = "MC_ENEMY_DEVELOPMENT"
    active = True
    scope = "LOCALE"

    def custom_init( self, nart ):
        self.convo_happened = False
        self.memory_recorded = False
        return True

    def NPC_offers(self,camp):
        mylist = list()
        mylist.append(Offer("[BATTLE_GREETING] I will [objective_ep]!",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _start_conversation(self,camp):
        self.convo_happened = True

    def _win_adventure(self,camp):
        self.elements["NPC"].relationship.history.append(Memory(
            random.choice(self.adv.mission_grammar["[win_ep]"]),
            random.choice(self.adv.mission_grammar["[win_pp]"]),
            -5, memtags=(relationships.MEM_Clash, relationships.MEM_LoseToPC)
        ))

    def _lose_adventure(self,camp):
        self.elements["NPC"].relationship.history.append(Memory(
            random.choice(self.adv.mission_grammar["[lose_ep]"]),
            random.choice(self.adv.mission_grammar["[lose_pp]"]),
            0, memtags=(relationships.MEM_Clash, relationships.MEM_DefeatPC)
        ))

    def t_UPDATE(self,camp):
        if self.adv.is_completed() and self.convo_happened and not self.memory_recorded:
            self.memory_recorded = True
            if self.adv.is_won():
                self._win_adventure(camp)
            else:
                self._lose_adventure(camp)


class IRememberYouBC(BasicBattleConversation):
    UNIQUE = True
    @classmethod
    def matches( cls, pstate ):
        return (
            pstate.elements["NPC"].relationship and
            pstate.elements["NPC"].relationship.get_recent_memory([relationships.MEM_Clash]) and
            pstate.elements["NPC"].relationship.role is None
        )
    def NPC_offers(self,camp):
        mylist = list()
        mylist.append(Offer("I remember you... [MEM_Clash]! This time I'm going to [objective_ep].",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist
    def _start_conversation(self,camp):
        super()._start_conversation(camp)
        self.elements["NPC"].relationship.role = relationships.R_OPPONENT


class RegularOpponentBC(BasicBattleConversation):
    @classmethod
    def matches( cls, pstate ):
        return (
            pstate.elements["NPC"].relationship and
            pstate.elements["NPC"].relationship.get_recent_memory([relationships.MEM_Clash]) and
            pstate.elements["NPC"].relationship.role is None
        )
    def NPC_offers(self,camp):
        mylist = list()
        myclash = self.elements["NPC"].relationship.get_recent_memory([relationships.MEM_Clash])
        mylist.append(Offer("[WE_MEET_AGAIN] The last time we met in battle, {}.".format(myclash.npc_perspective),
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist
    def _start_conversation(self,camp):
        super()._start_conversation(camp)
        self.elements["NPC"].relationship.role = relationships.R_OPPONENT


class GlorySortingBattleBC(BasicBattleConversation):
    UNIQUE = True
    @classmethod
    def matches( cls, pstate ):
        return (
            gears.personality.Glory in pstate.elements["NPC"].personality and
            (not pstate.elements["NPC"].relationship or
            not pstate.elements["NPC"].relationship.attitude)
        )
    def NPC_offers(self,camp):
        mylist = list()
        mylist.append(Offer("[BATTLE_GREETING] Will this be a worthy challenge or just another boring smackdown?",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("I will [objective_ep] and dare you to stop me.",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    WIN_MEMORIES = (
        "you proved yourself the better pilot", "you showed me that I have much to learn"
    )
    def _win_adventure(self,camp):
        npc = self.elements["NPC"]
        npc.relationship.attitude = relationships.A_JUNIOR
        npc.relationship.history.append(Memory(
            random.choice(self.WIN_MEMORIES),
            random.choice(self.adv.mission_grammar["[win_pp]"]),
            5, memtags=(relationships.MEM_Clash, relationships.MEM_LoseToPC)
        ))

    LOSE_MEMORIES = (
        "I showed you that I am the better pilot","I demonstrated my superiority to you"
    )

    def _lose_adventure(self,camp):
        npc = self.elements["NPC"]
        npc.relationship.attitude = relationships.A_SENIOR
        npc.relationship.history.append(Memory(
            random.choice(self.LOSE_MEMORIES),
            random.choice(self.adv.mission_grammar["[lose_pp]"]),
            -5, memtags=(relationships.MEM_Clash, relationships.MEM_DefeatPC)
        ))


class PassionateSortingBattleBC(BasicBattleConversation):
    UNIQUE = True
    @classmethod
    def matches( cls, pstate ):
        # No Glory virtue because this pilot is a sore loser.
        return (
            gears.personality.Passionate in pstate.elements["NPC"].personality and
            gears.personality.Glory not in pstate.elements["NPC"].personality and
            (not pstate.elements["NPC"].relationship or
            not pstate.elements["NPC"].relationship.attitude)
        )
    def NPC_offers(self,camp):
        mylist = list()
        mylist.append(Offer("[BATTLE_GREETING] Obviously you don't know who you're dealing with, or you wouldn't dare to face me!",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("Watch me [objective_ep]!!!",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    WIN_MEMORIES = (
        "you humiliated me in battle", "you destroyed my favorite mecha"
    )

    def _win_adventure(self,camp):
        npc = self.elements["NPC"]
        npc.relationship.attitude = relationships.A_RESENT
        npc.relationship.history.append(Memory(
            random.choice(self.WIN_MEMORIES),
            random.choice(self.adv.mission_grammar["[win_pp]"]),
            -10, memtags=(relationships.MEM_Clash, relationships.MEM_LoseToPC)
        ))

    LOSE_MEMORIES = (
        "I showed you that you have much to learn", "I demonstrated my true power to you"
    )

    def _lose_adventure(self,camp):
        npc = self.elements["NPC"]
        npc.relationship.attitude = relationships.A_SENIOR
        npc.relationship.history.append(Memory(
            random.choice(self.LOSE_MEMORIES),
            random.choice(self.adv.mission_grammar["[lose_pp]"]),
            -5, memtags=(relationships.MEM_Clash, relationships.MEM_DefeatPC)
        ))


class GrimSortingBattleBC(BasicBattleConversation):
    UNIQUE = True
    @classmethod
    def matches( cls, pstate ):
        # No Glory virtue because this pilot is a sore winner.
        return (
            gears.personality.Grim in pstate.elements["NPC"].personality and
            gears.personality.Glory not in pstate.elements["NPC"].personality and
            (not pstate.elements["NPC"].relationship or
            not pstate.elements["NPC"].relationship.attitude)
        )

    def NPC_offers(self,camp):
        mylist = list()
        mylist.append(Offer("[BATTLE_GREETING] If you think you can defeat me, I'll show you how wrong you are!",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    WIN_MEMORIES = (
        "you demolished my false pride", "you taught me a valuable lesson"
    )

    def _win_adventure(self,camp):
        npc = self.elements["NPC"]
        npc.relationship.attitude = relationships.A_JUNIOR
        npc.relationship.history.append(Memory(
            random.choice(self.WIN_MEMORIES),
            random.choice(self.adv.mission_grammar["[win_pp]"]),
            5, memtags=(relationships.MEM_Clash, relationships.MEM_LoseToPC)
        ))

    LOSE_MEMORIES = (
        "I showed you how weak you really are", "I put you in your place"
    )

    def _lose_adventure(self,camp):
        npc = self.elements["NPC"]
        npc.relationship.attitude = relationships.A_RESENT
        npc.relationship.history.append(Memory(
            random.choice(self.LOSE_MEMORIES),
            random.choice(self.adv.mission_grammar["[lose_pp]"]),
            -5, memtags=(relationships.MEM_Clash, relationships.MEM_DefeatPC)
        ))


class EasygoingSortingBattleBC(BasicBattleConversation):
    UNIQUE = True
    @classmethod
    def matches(cls, pstate):
        return (
                gears.personality.Easygoing in pstate.elements["NPC"].personality and
                (not pstate.elements["NPC"].relationship or
                 not pstate.elements["NPC"].relationship.attitude)
        )

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "[BATTLE_GREETING] I'm supposed to [objective_ep], so let's try to get this finished up as soon as possible.",
            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("Any time you're ready.",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    WIN_MEMORIES = (
        "you showed me some wicked moves", "I got to take the day off early"
    )

    def _win_adventure(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.attitude = relationships.A_FRIENDLY
        npc.relationship.history.append(Memory(
            random.choice(self.WIN_MEMORIES),
            random.choice(self.adv.mission_grammar["[win_pp]"]),
            5, memtags=(relationships.MEM_Clash, relationships.MEM_LoseToPC)
        ))

    LOSE_MEMORIES = (
        "you didn't put up much of a fight", "you rolled over like a soupy omelet"
    )

    def _lose_adventure(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.attitude = relationships.A_SENIOR
        npc.relationship.history.append(Memory(
            random.choice(self.LOSE_MEMORIES),
            random.choice(self.adv.mission_grammar["[lose_pp]"]),
            5, memtags=(relationships.MEM_Clash, relationships.MEM_DefeatPC)
        ))


class JuniorToImproverBC(BasicBattleConversation):
    UNIQUE = True
    @classmethod
    def matches(cls, pstate):
        return (
            pstate.elements["NPC"].relationship and
            pstate.elements["NPC"].relationship.attitude == gears.relationships.A_JUNIOR and
            not pstate.elements["NPC"].relationship.expectation
        )

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "[BATTLE_GREETING] I've been practicing every day, and sometime I hope to be as good a pilot as you!",
            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("Time to see if my training has paid off...",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _start_conversation(self,camp):
        super()._start_conversation(camp)
        self.elements["NPC"].relationship.expectation = relationships.E_IMPROVER


class FriendlyNothingToColleagueBattleBC(BasicBattleConversation):
    UNIQUE = True
    @classmethod
    def matches(cls, pstate):
        return (
            pstate.elements["NPC"].relationship and
            pstate.elements["NPC"].relationship.attitude == gears.relationships.A_FRIENDLY and
            not pstate.elements["NPC"].relationship.role
        )

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "[WE_MEET_AGAIN] Another day hard at work, eh [audience]?",
            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("I try to [objective_ep], you do whatever you're doing, and at the end of the day we both get paid!",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _start_conversation(self,camp):
        super()._start_conversation(camp)
        self.elements["NPC"].relationship.role = relationships.R_COLLEAGUE


class ResentNothingToOpponentBattleBC(BasicBattleConversation):
    @classmethod
    def matches(cls, pstate):
        return (
            pstate.elements["NPC"].relationship and
            pstate.elements["NPC"].relationship.attitude == gears.relationships.A_RESENT and
            not pstate.elements["NPC"].relationship.role
        )

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "[WE_MEET_AGAIN] Why do you always show up to ruin my day?",
            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("This time it's personal!",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _start_conversation(self,camp):
        super()._start_conversation(camp)
        self.elements["NPC"].relationship.role = relationships.R_OPPONENT


class MercenaryBanditBattleBC(BasicBattleConversation):
    @classmethod
    def matches(cls, pstate):
        return (
            pstate.elements["NPC"].faction and
            gears.tags.Criminal in pstate.elements["NPC"].faction.factags and
            pstate.elements["NPC"].relationship and
            not pstate.elements["NPC"].relationship.expectation
        )

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "[BATTLE_GREETING] Your presence is costing me money, but if I salvage your mek I can earn that back.",
            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _start_conversation(self,camp):
        super()._start_conversation(camp)
        self.elements["NPC"].relationship.expectation = relationships.E_MERCENARY


class FellowshipMercenaryFriendlyBC(BasicBattleConversation):
    UNIQUE = True
    @classmethod
    def matches(cls, pstate):
        return (
            gears.personality.Fellowship in pstate.elements["NPC"].personality and
            pstate.elements["NPC"].relationship and
            pstate.elements["NPC"].relationship.expectation == relationships.E_MERCENARY and
            not pstate.elements["NPC"].relationship.attitude
        )

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "[WE_MEET_AGAIN] What are your mission rates, anyway? Maybe next time I should hire you for my team.",
            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("Yes, of course. I knew I wouldn't be able to buy you off right now... any cavalier who breaks a contract mid-mission will never be hired again.",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _start_conversation(self,camp):
        super()._start_conversation(camp)
        self.elements["NPC"].relationship.attitude = relationships.A_FRIENDLY
        self.elements["NPC"].relationship.reaction_mod += 10

    def _win_adventure(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.history.append(Memory(
            "you refused my business offer",
            random.choice(self.adv.mission_grammar["[win_pp]"]),
            0, memtags=(relationships.MEM_Clash, relationships.MEM_LoseToPC)
        ))


class ResentfulMercenaryBC(BasicBattleConversation):
    UNIQUE = True
    @classmethod
    def matches(cls, pstate):
        return (
            pstate.elements["NPC"].relationship and
            pstate.elements["NPC"].relationship.expectation == relationships.E_MERCENARY and
            not pstate.elements["NPC"].relationship.attitude
        )

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "[WE_MEET_AGAIN] I don't know what your problem is, but I'm trying to earn a living here!",
            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("Fine, whatever. [LETSFIGHT]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _start_conversation(self,camp):
        super()._start_conversation(camp)
        self.elements["NPC"].relationship.attitude = relationships.A_RESENT

    def _win_adventure(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.history.append(Memory(
            "you cost me a lot of money",
            random.choice(self.adv.mission_grammar["[win_pp]"]),
            -10, memtags=(relationships.MEM_Clash, relationships.MEM_LoseToPC)
        ))
