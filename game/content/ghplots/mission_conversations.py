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

from .missionbuilder import MissionGrammar, BuildAMissionSeed, CONVO_CANT_WITHDRAW, CONVO_CANT_RETREAT


class NoDevBattleConversation(Plot):
    # A conversation for mook NPCs who don't need any development.
    LABEL = "MC_NDBCONVERSATION"
    active = True
    scope = "LOCALE"

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist


#  *******************************
#  ***   MC_DUEL_DEVELOPMENT   ***
#  *******************************
# NPC: The opponent who needs character development
# LOCALE: The fight scene.

class BasicDuelConversation(Plot):
    # No real character development, but record the memory of this battle.MC_GRUDGE_MATCH
    LABEL = "MC_DUEL_DEVELOPMENT"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        self.convo_happened = False
        return True

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[DUEL_GREETING]",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        return mylist

    def _start_conversation(self, camp):
        self.convo_happened = True


#  ********************************
#  ***   MC_ENEMY_DEVELOPMENT   ***
#  ********************************
# NPC: The enemy who needs character development
# LOCALE: The fight scene.
#
#   Change LABEL to "TEST_ENEMY_CONVO" to run a basic test

class BasicBattleConversation(Plot):
    # No real character development, but record the memory of this battle.
    LABEL = "MC_ENEMY_DEVELOPMENT"
    active = True
    scope = "LOCALE"
    WIN_REACTION_ADJUST = -5
    LOSE_REACTION_ADJUST = 0

    def custom_init(self, nart):
        self.convo_happened = False
        self.memory_recorded = False
        return True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        mylist.append(Offer("[BATTLE_GREETING] I will [objective_ep]!",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        if not self.elements.get(CONVO_CANT_RETREAT, False):
            game.ghdialogue.SkillBasedPartyReply(
                Offer(
                    "[CHANGE_MIND_AND_RETREAT] Until we meet again, [PC].",
                    context=ContextTag([context.RETREAT]), effect=self._enemies_retreat,
                ), camp, mylist, gears.stats.Ego, gears.stats.Negotiation, self._effective_rank(),
                difficulty=gears.stats.DIFFICULTY_LEGENDARY, no_random=False
            )
        if not self.elements.get(CONVO_CANT_WITHDRAW, False):
            if camp.renown < self._effective_rank():
                mylist.append(Offer("[WITHDRAW]", effect=self._player_retreat,
                                    context=ContextTag([context.WITHDRAW, ])))
        return mylist

    def _effective_rank(self):
        return max(self.elements["NPC"].renown, self.rank)

    def _player_retreat(self, camp: gears.GearHeadCampaign):
        if self.LABEL != "TEST_ENEMY_CONVO":
            camp.scene.player_team.retreat(camp)

    def _enemies_retreat(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        myroot = npc.get_root()
        myteam = camp.scene.local_teams.get(myroot, None)
        if myteam:
            myteam.retreat(camp)
        elif myroot in camp.scene.contents:
            camp.scene.contents.remove(myroot)

    def _start_conversation(self, camp):
        self.convo_happened = True

    def _win_adventure(self, camp):
        self.elements["NPC"].relationship.history.append(Memory(
            random.choice(self.adv.mission_grammar["[win_ep]"]),
            random.choice(self.adv.mission_grammar["[win_pp]"]),
            self.WIN_REACTION_ADJUST, memtags=(relationships.MEM_Clash, relationships.MEM_LoseToPC)
        ))

    def _lose_adventure(self, camp):
        self.elements["NPC"].relationship.history.append(Memory(
            random.choice(self.adv.mission_grammar["[lose_ep]"]),
            random.choice(self.adv.mission_grammar["[lose_pp]"]),
            self.LOSE_REACTION_ADJUST, memtags=(relationships.MEM_Clash, relationships.MEM_DefeatPC)
        ))

    def t_UPDATE(self, camp):
        if self.LABEL != "TEST_ENEMY_CONVO" and self.adv.is_completed() and self.convo_happened and not self.memory_recorded:
            self.memory_recorded = True
            if self.adv.is_won():
                self._win_adventure(camp)
            else:
                self._lose_adventure(camp)


class AegisInferiorityIntroduction(BasicBattleConversation):
    UNIQUE = True

    @classmethod
    def matches(cls, pstate):
        return (
                   pstate.elements["NPC"].faction and
                   pstate.elements["NPC"].faction.get_faction_tag() is gears.factions.AegisOverlord and
                   pstate.elements["METROSCENE"].attributes.intersection({gears.personality.DeadZone, gears.personality.GreenZone}) and
                   (not pstate.elements["NPC"].relationship or
                    pstate.elements["NPC"].relationship.attitude in (None, relationships.A_DISTANT))
               ) or cls.LABEL == "TEST_ENEMY_CONVO"

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer("I don't understand why the Terrans want to fight Aegis. Can't you see that we're only trying to help? [AEGIS_PROPAGANDA]",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))

        mylist.append(Offer(
            "I'd like to, but I heard that everyone here is a dangerous barbarian. [LETSFIGHT]",
            context=ContextTag([context.COMBAT_CUSTOM, ]),
            data={"reply": "Maybe if you tried talking to the people of Earth you'd find out."}
        ))

        if not self.elements.get(CONVO_CANT_RETREAT, False):
            game.ghdialogue.SkillBasedPartyReply(
                Offer(
                    "It seems I have no chance of winning here today... [I_MUST_CONSIDER_MY_NEXT_STEP] [GOODBYE]",
                    context=ContextTag([context.COMBAT_CUSTOM]), effect=self._enemies_retreat,
                    data={"reply": "[YOU_SEEM_NICE_BUT_ENEMY] Why don't you go back to Luna where it's safe?"}
                ), camp, mylist, gears.stats.Ego, gears.stats.Negotiation, self._effective_rank(),
                difficulty=gears.stats.DIFFICULTY_AVERAGE, no_random=False
            )

        return mylist

    def _start_conversation(self, camp: gears.GearHeadCampaign):
        super()._start_conversation(camp)
        npc: gears.base.Character = self.elements["NPC"]
        npc.relationship = camp.get_relationship(npc)
        npc.relationship.attitude = relationships.A_JUNIOR


class AegisSuperiorityIntroduction(BasicBattleConversation):
    UNIQUE = True

    @classmethod
    def matches(cls, pstate):
        return (
                   pstate.elements["NPC"].faction and
                   pstate.elements["NPC"].faction.get_faction_tag() is gears.factions.AegisOverlord and
                   (not pstate.elements["NPC"].relationship or
                    pstate.elements["NPC"].relationship.attitude in (None, relationships.A_DISTANT))
               ) or cls.LABEL == "TEST_ENEMY_CONVO"

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer("Why do you resist Aegis? [AEGIS_PROPAGANDA]",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))

        mylist.append(Offer(
            "I could tell you are a {pc.gender.noun} of great intelligence, but still we must battle, because I am here to [objective_ep]!".format(pc=camp.pc),
            context=ContextTag([context.COMBAT_CUSTOM, ]),
            data={"reply": "[AGREE]"}, effect=self._agree
        ))

        mylist.append(Offer(
            "Words are for the weak; truth is decided by those with the power to back it up! [LETSFIGHT]",
            context=ContextTag([context.COMBAT_CUSTOM, ]),
            data={"reply": "[YOU_BELIEVE_THE_HYPE]"}
        ))

        mylist.append(Offer(
            "And that is why you will lose, because you don't even have a reason to fight. [THREATEN]",
            context=ContextTag([context.COMBAT_CUSTOM, ]),
            data={"reply": "[I_DONT_CARE] I'm just here to [objective_pp]."}
        ))

        return mylist

    def _agree(self, camp: gears.GearHeadCampaign):
        npc: gears.base.Character = self.elements["NPC"]
        npc.relationship.reaction_mod += 20

    def _start_conversation(self, camp: gears.GearHeadCampaign):
        super()._start_conversation(camp)
        npc: gears.base.Character = self.elements["NPC"]
        npc.relationship = camp.get_relationship(npc)
        npc.relationship.attitude = relationships.A_SENIOR


class LoserBecomesImprover(BasicBattleConversation):
    UNIQUE = True

    @classmethod
    def matches(cls, pstate):
        return (
                       pstate.elements["NPC"].relationship and
                       pstate.elements["NPC"].relationship.get_recent_memory([relationships.MEM_LoseToPC]) and
                       pstate.elements["NPC"].relationship.expectation is None
               ) or cls.LABEL == "TEST_ENEMY_CONVO"

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer("Some time ago [MEM_LoseToPC]... I think you'll find this time I am not so easy to defeat!",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer(
            "Yes, actually. I've been training a lot since our last battle. In addition to everything else it's really building my confidence.",
            context=ContextTag([context.COMBAT_CUSTOM, ]), effect=self._compliment,
            data={"reply": "Have you been working out? It's hard to tell over the vidfeed, but you're looking good."}))
        mylist.append(Offer("We'll see about that. [LETSFIGHT]",
                            context=ContextTag([context.COMBAT_CUSTOM, ]),
                            data={"reply": "I'm just here to [objective_pp], and you're going to lose again."}))
        return mylist

    def _compliment(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        npc.relationship.reaction_mod += random.randint(10, 30)

    def _start_conversation(self, camp):
        super()._start_conversation(camp)
        npc: gears.base.Character = self.elements["NPC"]
        for skill in gears.stats.FUNDAMENTAL_COMBATANT_SKILLS:
            if npc.get_stat(skill) < camp.pc.get_stat(skill):
                npc.statline[skill] += 1
            npc.renown += 5

        npc.relationship.expectation = relationships.E_IMPROVER


class JuniorImproverToFriendlyOrRival(BasicBattleConversation):
    UNIQUE = True

    @classmethod
    def matches(cls, pstate):
        return (
                       pstate.elements["NPC"].relationship and
                       pstate.elements["NPC"].relationship.attitude == gears.relationships.A_JUNIOR and
                       pstate.elements["NPC"].relationship.expectation in (None, gears.relationships.E_IMPROVER) and
                       not pstate.elements.get(CONVO_CANT_RETREAT, False)
               ) or cls.LABEL == "TEST_ENEMY_CONVO"

    def NPC_offers(self, camp):
        mylist = list()
        myclash = self.elements["NPC"].relationship.get_recent_memory([relationships.MEM_LoseToPC])
        if myclash:
            mylist.append(Offer("[BAD_NEWS] It's [PC] again... The last time we met, {}. [WE_ARE_DOOMED]".format(
                myclash.npc_perspective),
                context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        else:
            mylist.append(Offer("[BAD_NEWS] I wasn't counting on you showing up today... [WE_ARE_DOOMED]",
                                context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))

        mylist.append(Offer("Thanks for the encouragement, [PC]... I'll do my best! [LETSFIGHT]",
                            context=ContextTag([context.COMBAT_CUSTOM, ]), effect=self._encourage_npc,
                            data={"reply": "Don't give up hope so easily. You might beat me this time!"}))

        mylist.append(
            Offer("I think my team can handle this by themselves... but the next time we meet, I'll [defeat_you]!",
                  context=ContextTag([context.COMBAT_CUSTOM, ]), effect=self._drive_away_npc,
                  data={"reply": "[ATTACK:RETREAT]"}))

        return mylist

    def _encourage_npc(self, camp):
        self.elements["NPC"].relationship.attitude = relationships.A_FRIENDLY

    def _drive_away_npc(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        npc.relationship.expectation = relationships.E_RIVAL
        for skill in gears.stats.FUNDAMENTAL_COMBATANT_SKILLS:
            if npc.get_stat(skill) < camp.pc.get_stat(skill):
                npc.statline[skill] += 2
            else:
                npc.statline[skill] += 1
            npc.renown += 10
        myroot = npc.get_root()
        if myroot in camp.scene.contents:
            camp.scene.contents.remove(myroot)


class FriendlyAdventurer(BasicBattleConversation):
    UNIQUE = True

    @classmethod
    def matches(cls, pstate):
        return (
                       pstate.elements["NPC"].relationship and
                       pstate.elements["NPC"].relationship.attitude == gears.relationships.A_FRIENDLY and
                       pstate.elements["NPC"].relationship.expectation in (None, gears.relationships.E_IMPROVER)
               ) or cls.LABEL == "TEST_ENEMY_CONVO"

    def NPC_offers(self, camp):
        mylist = list()
        myclash = self.elements["NPC"].relationship.get_recent_memory([relationships.MEM_Clash])
        if myclash:
            mylist.append(Offer(
                "[WE_MEET_AGAIN] I remember when {}. This time we'll have another awesome battle!".format(
                    myclash.npc_perspective),
                context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        else:
            mylist.append(Offer(
                "I've been dying to fight you, [PC]. I can't wait to see what kind of a challenge you put up.",
                context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))

        mylist.append(Offer("I wouldn't be doing this except for the adventure, the challenge... [LETSFIGHT]",
                            context=ContextTag([context.COMBAT_CUSTOM, ]),
                            data={"reply": "You seem pretty happy for someone who is about to lose."}))

        mylist.append(Offer("But where would the fun be in running away? I'm in this for the adventure! [LETSFIGHT]",
                            context=ContextTag([context.COMBAT_CUSTOM, ]),
                            data={"reply": "[ATTACK:RETREAT]"}))

        return mylist

    def _start_conversation(self, camp):
        super()._start_conversation(camp)
        self.elements["NPC"].relationship.expectation = relationships.E_ADVENTURE


class OpponentStansPC(BasicBattleConversation):
    UNIQUE = True

    @classmethod
    def matches(cls, pstate):
        return cls.LABEL == "TEST_ENEMY_CONVO" or \
               not (pstate.elements["NPC"].relationship and pstate.elements["NPC"].relationship.met_before)

    def custom_init(self, nart):
        if super().custom_init(nart):
            return nart.camp.pc.has_badge("Pop Star") or self.LABEL == "TEST_ENEMY_CONVO"

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "My name is {NPC}, and I am going to [objective_ep]... Hey, wait a minute. Aren't you [audience]?".format(
                **self.elements),
            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(
            Offer("Awesome! I have all of your albums! I can't wait to tell everyone that I fought against [audience]!",
                  context=ContextTag([context.COMBAT_CUSTOM, ]), effect=self._admit_pop_star,
                  data={"reply": "That's right, I'm {}, and I'm going to [objective_pp]!".format(camp.pc)}))
        mylist.append(Offer(
            "This is so cool! Before we start, I just want to say that I love your music... Now it's time for me to [defeat_you].",
            context=ContextTag([context.COMBAT_CUSTOM, ]), effect=self._deny_pop_star,
            data={"reply": "None of your business; all you need to know is that I'm here to [threat]!"}))
        return mylist

    def _admit_pop_star(self, camp):
        self.elements["NPC"].relationship.attitude = relationships.A_FRIENDLY

    def _deny_pop_star(self, camp):
        self.elements["NPC"].relationship.expectation = relationships.E_ADVENTURE

    def _win_adventure(self, camp):
        self.elements["NPC"].relationship.history.append(Memory(
            "you totally kicked my arse",
            random.choice(self.adv.mission_grammar["[win_pp]"]),
            20, memtags=(relationships.MEM_CallItADraw, relationships.MEM_Clash, relationships.MEM_LoseToPC)
        ))

    def _lose_adventure(self, camp):
        self.elements["NPC"].relationship.history.append(Memory(
            "we had an epic battle",
            random.choice(self.adv.mission_grammar["[lose_pp]"]),
            10, memtags=(relationships.MEM_CallItADraw, relationships.MEM_Clash, relationships.MEM_DefeatPC)
        ))


class IRememberYouBC(BasicBattleConversation):
    UNIQUE = True

    @classmethod
    def matches(cls, pstate):
        return (
                pstate.elements["NPC"].relationship and
                pstate.elements["NPC"].relationship.get_recent_memory([relationships.MEM_Clash]) and
                pstate.elements["NPC"].relationship.role is None
        )

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer("I remember you... [MEM_Clash]! This time I'm going to [objective_ep].",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _start_conversation(self, camp):
        super()._start_conversation(camp)
        self.elements["NPC"].relationship.role = relationships.R_OPPONENT


class RegularOpponentBC(BasicBattleConversation):
    @classmethod
    def matches(cls, pstate):
        return (
                pstate.elements["NPC"].relationship and
                pstate.elements["NPC"].relationship.get_recent_memory([relationships.MEM_Clash]) and
                pstate.elements["NPC"].relationship.role is None
        )

    def NPC_offers(self, camp):
        mylist = list()
        myclash = self.elements["NPC"].relationship.get_recent_memory([relationships.MEM_Clash])
        mylist.append(Offer("[WE_MEET_AGAIN] The last time we met in battle, {}.".format(myclash.npc_perspective),
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        if not self.elements.get(CONVO_CANT_RETREAT, False):
            game.ghdialogue.SkillBasedPartyReply(
                Offer(
                    "[CHANGE_MIND_AND_RETREAT] [GOODBYE]",
                    context=ContextTag([context.RETREAT]), effect=self._enemies_retreat
                ), camp, mylist, gears.stats.Ego, gears.stats.Negotiation, max(self.elements["NPC"].renown, self.rank),
                difficulty=gears.stats.DIFFICULTY_LEGENDARY, no_random=False
            )
        return mylist

    def _start_conversation(self, camp):
        super()._start_conversation(camp)
        self.elements["NPC"].relationship.role = relationships.R_OPPONENT


class GlorySortingBattleBC(BasicBattleConversation):
    UNIQUE = True

    @classmethod
    def matches(cls, pstate):
        return (
                gears.personality.Glory in pstate.elements["NPC"].personality and
                (not pstate.elements["NPC"].relationship or
                 not pstate.elements["NPC"].relationship.attitude)
        )

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[BATTLE_GREETING] Will this be a worthy challenge or just another boring smackdown?",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("I will [objective_ep] and dare you to stop me.",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    WIN_MEMORIES = (
        "you proved yourself the better pilot", "you showed me that I have much to learn"
    )

    def _win_adventure(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.attitude = relationships.A_JUNIOR
        npc.relationship.history.append(Memory(
            random.choice(self.WIN_MEMORIES),
            random.choice(self.adv.mission_grammar["[win_pp]"]),
            5, memtags=(relationships.MEM_Clash, relationships.MEM_LoseToPC)
        ))

    LOSE_MEMORIES = (
        "I showed you that I am the better pilot", "I demonstrated my superiority to you"
    )

    def _lose_adventure(self, camp):
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
    def matches(cls, pstate):
        # No Glory virtue because this pilot is a sore loser.
        return (
                gears.personality.Passionate in pstate.elements["NPC"].personality and
                gears.personality.Glory not in pstate.elements["NPC"].personality and
                (not pstate.elements["NPC"].relationship or
                 not pstate.elements["NPC"].relationship.attitude)
        )

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            "[BATTLE_GREETING] Obviously you don't know who you're dealing with, or you wouldn't dare to face me!",
            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("Watch me [objective_ep]!!!",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    WIN_MEMORIES = (
        "you humiliated me in battle", "you destroyed my favorite mecha"
    )

    def _win_adventure(self, camp):
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

    def _lose_adventure(self, camp):
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
    def matches(cls, pstate):
        # No Glory virtue because this pilot is a sore winner.
        return (
                gears.personality.Grim in pstate.elements["NPC"].personality and
                gears.personality.Glory not in pstate.elements["NPC"].personality and
                (not pstate.elements["NPC"].relationship or
                 not pstate.elements["NPC"].relationship.attitude)
        )

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[BATTLE_GREETING] If you think you can defeat me, I'll show you how wrong you are!",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    WIN_MEMORIES = (
        "you demolished my false pride", "you taught me a valuable lesson"
    )

    def _win_adventure(self, camp):
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

    def _lose_adventure(self, camp):
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
        "you showed me some wicked moves", "I got to take the time off early"
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
        "you didn't put up much of a fight", "you rolled over like a soup sandwich"
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
            "[BATTLE_GREETING] I've been practicing every time, and sometime I hope to be as good a pilot as you!",
            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("Time to see if my training has paid off...",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _start_conversation(self, camp):
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
            "[WE_MEET_AGAIN] Another time hard at work, eh [PC]?",
            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(
            Offer("I try to [objective_ep], you do whatever you're doing, and at the end of the time we both get paid!",
                  context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _start_conversation(self, camp):
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
            "[WE_MEET_AGAIN] Why do you always show up to ruin my time?",
            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("This time it's personal!",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _start_conversation(self, camp):
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

    def _start_conversation(self, camp):
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
        mylist.append(Offer(
            "Yes, of course. I knew I wouldn't be able to buy you off right now... any cavalier who breaks a contract mid-mission will never be hired again.",
            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _start_conversation(self, camp):
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

    def _start_conversation(self, camp):
        super()._start_conversation(camp)
        self.elements["NPC"].relationship.attitude = relationships.A_RESENT

    def _win_adventure(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.history.append(Memory(
            "you cost me a lot of money",
            random.choice(self.adv.mission_grammar["[win_pp]"]),
            -10, memtags=(relationships.MEM_Clash, relationships.MEM_LoseToPC)
        ))


#  ***************************
#  ***   MC_GRUDGE_MATCH   ***
#  ***************************
# A battle conversation in which the enemy is acting on a grudge against the PC; the regular mission grammar can
# usually be ignored, because all the NPC cares about is wrecking the PC.
# NPC: The enemy who needs character development
# LOCALE: The fight scene.

class BasicGrudgeMatchConversation(Plot):
    # No real character development, but the battle outcome will affect how angry the NPC is.
    LABEL = "MC_GRUDGE_MATCH"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        self.convo_happened = False
        self.memory_recorded = False
        return True

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[BATTLE_GREETING] [ANNOUNCE_GRUDGE]",
                            context=ContextTag([context.ATTACK, ]), effect=self._start_conversation))
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _start_conversation(self, camp):
        self.convo_happened = True

    def _win_adventure(self, camp):
        self.elements["NPC"].relationship.reaction_mod -= random.randint(1, 10)

    def _lose_adventure(self, camp):
        self.elements["NPC"].relationship.reaction_mod += random.randint(1, 6)

    def t_UPDATE(self, camp):
        if self.adv.is_completed() and self.convo_happened and not self.memory_recorded:
            self.memory_recorded = True
            if self.adv.is_won():
                self._win_adventure(camp)
            else:
                self._lose_adventure(camp)


#   ******************************
#   ***   ENEMY_CONVO_TESTER   ***
#   ******************************

class EnemyConvoTester(Plot):
    LABEL = "ENEMY_CONVO_TESTER"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        npc: gears.base.Character = self.register_element("NPC", gears.selector.random_pilot())
        npc.relationship = nart.camp.get_relationship(npc)
        self.convoplot = self.add_sub_plot(nart, "TEST_ENEMY_CONVO",
                                           spstate=PlotState(adv=BuildAMissionSeed(nart.camp, "", None, None)).based_on(
                                               self))
        return True

    def LOCALE_ENTER(self, camp):
        myoffers = self.convoplot.NPC_offers(camp)
        if not isinstance(myoffers, list):
            pbge.alert("{} returned malformed offers.".format(self.convoplot))
        for o in myoffers:
            if o.effect:
                o.effect(camp)
        self.convoplot._start_conversation(camp)
        self.convoplot._win_adventure(camp)
        self.convoplot._lose_adventure(camp)
        pbge.alert("{} doesn't crash. Good luck.".format(self.convoplot))

    def _get_dialogue_grammar(self, npc, camp):
        return MissionGrammar()
