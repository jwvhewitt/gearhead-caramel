import game.content
import pbge
from pbge.plots import Plot, PlotState
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
import gears
import random
from gears import relationships
from gears.relationships import Memory
from game.content import ghcutscene


class NoDevTeamUpConversation(Plot):
    # A conversation for mook NPCs who don't need any development.
    # NPC: The ally who needs character development
    # LOCALE: The fight scene.
    LABEL = "MT_NDDEV"
    active = True
    scope = "LOCALE"

    START_COMBAT_MESSAGE = "[HELP_ME_VS_MECHA_COMBAT]"

    def NPC_START(self,camp):
        # Check this trigger when combat is started.
        ghcutscene.SimpleMonologueDisplay(self.START_COMBAT_MESSAGE, self.elements["NPC"])(camp)

    def NPC_WIN(self,camp):
        # Check this trigger if PC wins combat.
        ghcutscene.SimpleMonologueDisplay("[THANKS_FOR_MECHA_COMBAT_HELP] I better get back to base.", self.elements["NPC"])(camp)

    def NPC_LOSE(self,camp):
        # Check this trigger if PC loses combat.
        pass


#  *********************************
#  ***   MT_TEAMUP_DEVELOPMENT   ***
#  *********************************
# NPC: The ally who needs character development
# LOCALE: The fight scene.

class BasicTeamupConversation(Plot):
    # No real character development, but record the memory of this battle.
    LABEL = "MT_TEAMUP_DEVELOPMENT"
    active = True
    scope = "LOCALE"

    START_COMBAT_MESSAGE = "[HELP_ME_VS_MECHA_COMBAT]"

    def custom_init( self, nart ):
        npc = self.elements["NPC"]
        if not npc.relationship:
            npc.relationship = nart.camp.get_relationship(npc)
        return True

    def NPC_START(self,camp):
        # Check this trigger when combat is started.
        ghcutscene.SimpleMonologueDisplay(self.START_COMBAT_MESSAGE, self.elements["NPC"])(camp)

    def NPC_WIN(self,camp):
        # Check this trigger if PC wins combat.
        ghcutscene.SimpleMonologueDisplay("[THANKS_FOR_MECHA_COMBAT_HELP] I better get back to base.", self.elements["NPC"])(camp)
        self.elements["NPC"].relationship.history.append(Memory(
            "you fought at my side",
            "I helped you in battle",
            5, memtags=(relationships.MEM_AidedByPC,)
        ))

    def NPC_LOSE(self,camp):
        # Check this trigger if PC loses combat.
        pass


class AngryLancemateForgiveness(BasicTeamupConversation):
    # An angry lancemate will forgive the PC.
    START_COMBAT_MESSAGE = "I took a mission that's beyond my skill level... [HELP_ME]"
    @classmethod
    def matches( cls, pstate: PlotState ):
        """Returns True if this plot matches the current plot state."""
        npc: gears.base.Character = pstate.elements["NPC"]
        return npc.relationship and gears.relationships.RT_LANCEMATE in npc.relationship.tags

    def custom_init( self, nart ):
        npc: gears.base.Character = self.elements["NPC"]
        return npc.get_reaction_score(nart.camp.pc, nart.camp) < 0

    def NPC_WIN(self,camp):
        # Check this trigger if PC wins combat.
        ghcutscene.SimpleMonologueDisplay("[THANKS_FOR_MECHA_COMBAT_HELP] I'll see you around, [audience].", self.elements["NPC"])(camp)
        npc: gears.base.Character = self.elements["NPC"]
        while npc.get_reaction_score(camp.pc, camp) < 1:
            npc.relationship.reaction_mod += random.randint(1, 20)


class PossiblyBecomeLancemateConvo(BasicTeamupConversation):
    # A person the PC helped will possibly become a lancemate.
    @classmethod
    def matches( cls, pstate: PlotState ):
        """Returns True if this plot matches the current plot state."""
        npc: gears.base.Character = pstate.elements["NPC"]
        return npc.relationship and gears.relationships.RT_LANCEMATE not in npc.relationship.tags and npc.relationship.get_positive_memory()

    def NPC_WIN(self,camp: gears.GearHeadCampaign):
        # Check this trigger if PC wins combat.
        npc: gears.base.Character = self.elements["NPC"]

        if npc.get_reaction_score(camp.pc, camp) > random.randint(40,80) - camp.get_party_skill(gears.stats.Charm, gears.stats.Negotiation):
            ghcutscene.SimpleMonologueDisplay("[THANKS_FOR_MECHA_COMBAT_HELP] Let me know if you ever need me to return the favor.",
                                              self.elements["NPC"])(camp)
            npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
            npc.relationship.history.append(Memory(
                "I promised to help you if you ever needed help",
                "you promised to help me when I needed you",
                15, memtags=(relationships.MEM_AidedByPC,)
            ))
        else:
            ghcutscene.SimpleMonologueDisplay("[THANKS_FOR_MECHA_COMBAT_HELP]", self.elements["NPC"])(camp)
            npc.relationship.reaction_mod += random.randint(1, 10)


