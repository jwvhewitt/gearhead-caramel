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
