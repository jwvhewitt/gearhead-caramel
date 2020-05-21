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

    def t_UPDATE(self,camp):
        if self.adv.is_completed() and self.convo_happened and not self.memory_recorded:
            self.memory_recorded = True
            npc = self.elements["NPC"]
            if self.adv.is_won():
                npc.relationship.history.append(Memory(
                    random.choice(self.adv.mission_grammar["[win_ep]"]),
                    random.choice(self.adv.mission_grammar["[win_pp]"]),
                    -5, memtags=(relationships.MEM_Clash,relationships.MEM_LoseToPC)
                ))
            else:
                npc.relationship.history.append(Memory(
                    random.choice(self.adv.mission_grammar["[lose_ep]"]),
                    random.choice(self.adv.mission_grammar["[lose_pp]"]),
                    0, memtags=(relationships.MEM_Clash,relationships.MEM_DefeatPC)
                ))


class IRememberYouBC(BasicBattleConversation):
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
        self.elements["NPC"].relationship.role = relationships.R_ACQUAINTANCE


class RegularOpponentBC(BasicBattleConversation):
    @classmethod
    def matches( cls, pstate ):
        return (
            pstate.elements["NPC"].relationship and
            pstate.elements["NPC"].relationship.get_recent_memory([relationships.MEM_Clash]) and
            pstate.elements["NPC"].relationship.role in (None,relationships.R_ACQUAINTANCE)
        )
    def NPC_offers(self,camp):
        mylist = list()
        myclash = pstate.elements["NPC"].relationship.get_recent_memory([relationships.MEM_Clash])
        mylist.append(Offer("[WE_MEET_AGAIN] The last time we met in battle, {}.".format(myclash.npc_perspective),
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist
    def _start_conversation(self,camp):
        super()._start_conversation(camp)
        self.elements["NPC"].relationship.role = relationships.R_OPPONENT


