import collections

import pbge
import gears
import copy
import random
from pbge import quests, plots, challenges
from pbge.plots import Rumor
from game.content import ghchallenges, plotutility, gharchitecture, ghcutscene
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from pbge.challenges import Challenge, AutoOffer, ChallengeMemo
from pbge.quests import OutcomeVerb
from . import missionbuilder, ghquest_objectives, mission_bigobs

#VERB_CONTACT = "CONTACT"  # You need to make contact with the target NPC

OE_ALLYFACTION = "OE_ALLYFACTION"
OE_ENEMYFACTION = "OE_ENEMYFACTION"
OE_OBJECT = "OE_OBJECT"
OE_QUEST_GIVER = "OE_QUEST_GIVER"   # Note: the death or disappearance of the quest giver is a valid reason to lose a quest!

OTAG_AGGRESSIVE = "OTAG_AGGRESSIVE"


class ExpelVerb(OutcomeVerb):
    name = "Expel"
    needed_elements = (OE_ENEMYFACTION,)
    tags = (OTAG_AGGRESSIVE,)


class FortifyVerb(OutcomeVerb):
    name = "Fortify"
    needed_elements = (OE_OBJECT,)


class RepressVerb(OutcomeVerb):
    name = "Repress"
    needed_elements = (OE_ALLYFACTION, OE_ENEMYFACTION,)
    tags = (OTAG_AGGRESSIVE,)


LORECAT_OUTCOME = "OUTCOME"

LORECAT_CHARACTER = "CHARACTER"
L_CHARACTER_ALIAS = "L_CHARACTER_ALIAS"
L_CHARACTER_IDENTITY = "L_CHARACTER_IDENTITY"   # Place the actual NPC here in the lore dict.

LORECAT_EMERGENCY = "EMERGENCY"

LORECAT_KNOWLEDGE = "KNOWLEDGE"

LORECAT_LOCATION = "LOCATION"
L_LOCATION_NAME = "L_LOCATION_NAME"

LORECAT_MOTIVE = "MOTIVE"                       # A motive. May belong to the enemy faction or the allied faction or
    # somone else entirely. Use the LORETAGs to indicate whose motive this is.
L_MOTIVE_CONFESSION = "[MOTIVE_CONFESSION]"     # Independent clause; a member of target faction admits their motive

LORETAG_ALLY = "LORETAG_ALLY"
LORETAG_ENEMY = "LORETAG_ENEMY"
LORETAG_HIDDEN = "LORETAG_HIDDEN"
LORETAG_PRIMARY = "LORETAG_PRIMARY"     # An important lore; usually something straight from the conclusion.
LORETAG_PROTECTED = "LORETAG_PROTECTED"


def default_player_can_do_outcome(camp, outcome: quests.QuestOutcome):
    # Generally, a PC can take part in a quest outcome if the player isn't an enemy of the allied faction and isn't
    # an ally of the enemy faction.
    if camp:
        if OE_ALLYFACTION in outcome.o_elements and camp.is_unfavorable_to_pc(outcome.o_elements[OE_ALLYFACTION]):
            return False
        elif OE_ENEMYFACTION in outcome.o_elements and camp.is_favorable_to_pc(outcome.o_elements[OE_ENEMYFACTION]):
            return False
    return True


#     **********************
#   **************************
#   ***                    ***
#   ***   IMPORTANT!!!!!   ***
#   ***                    ***
#   **************************
#     **********************
#
# When adding a Challenge to one of the quest tasks or conclusions, make sure that your Challenge is marked as private!
# You can do this by adding an underscore to the start of the Element ID, so instead of naming the Challenge "CHALLENGE"
# name it "_CHALLENGE" instead. Tasks are subplots of the QuestPlot that spawned them, so if you don't mark the
# challenge as private, it will be propagated to all the children and you might be able to finish the conclusion of
# the Quest before the Quest even starts. And that's the best case scenario. This element naming convention was added
# for a reason and you should respect that, Future Joe. Yes, I'm writing this long rambling warning specifically for
# myself. Because this is exactly the kind of dumb thing I'd do that would lead to a weird hard-to-replicate bug.
#

#  ******************************
#  ***   QUEST  CONCLUSIONS   ***
#  ******************************


class DefendNewFortification(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_CONCLUSION
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        outc = pstate.elements.get(quests.OUTCOME_ELEMENT_ID)
        if outc.verb in (FortifyVerb,):
            ob = outc.o_elements.get(OE_OBJECT)
            return isinstance(ob, gears.GearHeadScene)

    def custom_init(self, nart):
        self.elements["_BASE_NAME"] = "Fortress"
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        my_scene = my_outcome.o_elements.get(OE_OBJECT)
        self.elements["_FORT_SCENE"] = my_scene
        my_ally = my_outcome.o_elements.get(OE_ALLYFACTION)
        if not my_ally:
            my_ally = nart.camp.get_ally_faction(my_scene)
            my_outcome.o_elements[OE_ALLYFACTION] = my_ally
        self.elements["_ALLIED_FACTION"] = my_ally
        my_enemy = my_outcome.o_elements.get(OE_ENEMYFACTION)
        if not my_enemy:
            my_enemy = nart.camp.get_enemy_faction(self.elements["_ALLIED_FACTION"])
            my_outcome.o_elements[OE_ENEMYFACTION] = my_enemy
        self.elements["_ENEMY_FACTION"] = my_enemy
        self.mission_name = "Defend {_ALLIED_FACTION}'s new {_BASE_NAME} in {_FORT_SCENE}".format(**self.elements)
        self.memo = plots.Memo(
            "{_ALLIED_FACTION}'s {_BASE_NAME} has been completed, but must be protected until its defenses are in place. You can do this at {MISSION_GATE}.".format(**self.elements),
            self.elements["METROSCENE"]
        )

        base_lore = quests.QuestLore(
            LORECAT_LOCATION, texts={
                quests.TEXT_LORE_HINT: "{_ALLIED_FACTION} has been working on something to defend {_FORT_SCENE}".format(**self.elements),
                quests.TEXT_LORE_INFO: "they've built a {_BASE_NAME} to defend {_FORT_SCENE}, but its defenses are not fully operational yet".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "{_ALLIED_FACTION}'s project".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "You have learned about {_ALLIED_FACTION}'s {_BASE_NAME}.".format(**self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "{_ALLIED_FACTION}'s {_BASE_NAME}".format(**self.elements),
                L_LOCATION_NAME: "{_BASE_NAME}".format(**self.elements),
                quests.TEXT_LORE_MEMO: "{_ALLIED_FACTION} has a {_BASE_NAME} in {METROSCENE}.".format(
                    **self.elements),
            }, involvement=ghchallenges.InvolvedMetroNoEnemyToFactionNPCs(self.elements["METROSCENE"], my_ally),
            outcome=my_outcome,
            tags=(
                LORETAG_ALLY, LORETAG_PRIMARY
            ),
        )
        self.quest_record._needed_lore.add(base_lore)

        enemy_lore = quests.QuestLore(
            LORECAT_MOTIVE, texts={
                quests.TEXT_LORE_HINT: "{_ENEMY_FACTION} is planning to strike {_FORT_SCENE}".format(**self.elements),
                quests.TEXT_LORE_INFO: "I'm not sure {_FORT_SCENE}'s defenses are ready for an attack yet".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "{_ENEMY_FACTION}'s plans".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "You have learned that {_ENEMY_FACTION} plans to strike {_FORT_SCENE}.".format(**self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "{_ENEMY_FACTION}'s planned attack on {_FORT_SCENE}".format(**self.elements),
                L_MOTIVE_CONFESSION: "{_ENEMY_FACTION} will take {_FORT_SCENE}, and no-one can stop us",
                quests.TEXT_LORE_MEMO: "{_ENEMY_FACTION} plans to attack {_FORT_SCENE}.".format(
                    **self.elements),
            }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], my_enemy),
            outcome=my_outcome,
            tags=(
                LORETAG_ENEMY, LORETAG_PRIMARY
            ),
        )
        self.quest_record._needed_lore.add(enemy_lore)

        return True

    def _get_mission(self, camp):
        # Return a mission seed for the current state of this mission. The state may be altered by unfinished tasks-
        # For instance, if the fortress is defended by artillery, that gets added into the mission.
        objectives = [mission_bigobs.BAMO_DEFEND_FORTRESS,]
        rank = self.rank

        #ace_task = self.quest_record.get_task(QUEST_TASK_ACE_DEFENSE)
        #if ace_task:
        #    drank, dobjs = ace_task.get_ace_mission_mods(camp)
        #    rank += drank
        #    objectives += dobjs

        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])

        el_seed = missionbuilder.BuildAMissionSeed(
                camp, self.mission_name,
                self.elements["METROSCENE"], self.elements["MISSION_GATE"],
                enemy_faction=self.elements["_ENEMY_FACTION"], rank=rank,
                objectives=objectives,
                one_chance=True,
                scenegen=sgen, architecture=archi,
                cash_reward=100, on_win=self._win_outcome, on_loss=self._lose_outcome
            )

        return el_seed

    def _win_outcome(self, camp):
        self.quest_record.win_task(self, camp)

    def _lose_outcome(self, camp):
        self.quest_record.lose_task(self, camp)

    def MISSION_GATE_menu(self, camp, thingmenu):
        thingmenu.add_item(self.mission_name, self._get_mission(camp))


class StrikeTheLeader(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_CONCLUSION
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        outc = pstate.elements.get(quests.OUTCOME_ELEMENT_ID)
        if outc:
            return outc.verb in (RepressVerb,) and gears.factions.is_a_faction(outc.o_elements.get(OE_ENEMYFACTION))

    def custom_init(self, nart):
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        my_enemy = my_outcome.o_elements.get(OE_ENEMYFACTION)
        self.elements["_ENEMY_FACTION"] = my_enemy
        npc = self.register_element("_ENEMY_COMMANDER", nart.camp.cast_a_combatant(self.elements["_ENEMY_FACTION"], rank=self.rank+15, myplot=self), lock=True)

        self.mission_name = "Defeat {_ENEMY_COMMANDER} of {_ENEMY_FACTION}".format(**self.elements)
        self.memo = plots.Memo(
            "You have identified {_ENEMY_COMMANDER} as the local head of {_ENEMY_FACTION} and can challenge {_ENEMY_COMMANDER.gender.object_pronoun} at any time.".format(**self.elements),
            self.elements["METROSCENE"]
        )

        task_lore = quests.QuestLore(
            LORECAT_CHARACTER, texts={
                quests.TEXT_LORE_HINT: "the leader of {_ENEMY_FACTION} in {METROSCENE} has big plans".format(**self.elements),
                quests.TEXT_LORE_INFO: "{_ENEMY_COMMANDER} is {_ENEMY_FACTION}'s local commander".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "{_ENEMY_FACTION}'s leader".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "You have learned that the leader of {_ENEMY_FACTION} in {METROSCENE} is {_ENEMY_COMMANDER}.".format(**self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "{_ENEMY_FACTION}'s leader".format(**self.elements),
                L_CHARACTER_ALIAS: "{}'s leader".format(self.elements["_ENEMY_FACTION"]),
                L_CHARACTER_IDENTITY: npc,
                quests.TEXT_LORE_MEMO: "The leader of {_ENEMY_FACTION} in {METROSCENE} is {_ENEMY_COMMANDER}.".format(**self.elements),
            }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], my_enemy),
            outcome=my_outcome,
            tags=(LORETAG_ENEMY, LORETAG_PRIMARY)
        )
        self.quest_record._needed_lore.add(task_lore)

        return True

    SECONDARY_OBJECTIVES = (
        missionbuilder.BAMO_CAPTURE_BUILDINGS, missionbuilder.BAMO_CAPTURE_THE_MINE,
        missionbuilder.BAMO_RECOVER_CARGO, missionbuilder.BAMO_DESTROY_ARTILLERY
    )

    def _get_mission(self, camp):
        # Return a mission seed for the current state of this mission. The state may be altered by unfinished tasks-
        # For instance, if the fortress is defended by artillery, that gets added into the mission.
        objectives = [missionbuilder.BAMO_DEFEAT_NPC,] + [random.choice(self.SECONDARY_OBJECTIVES)]
        rank = self.rank

        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])

        el_seed = missionbuilder.BuildAMissionSeed(
            camp, self.mission_name,
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            enemy_faction=self.elements["_ENEMY_FACTION"], rank=rank,
            custom_elements={
                missionbuilder.BAME_NPC: self.elements["_ENEMY_COMMANDER"],
                missionbuilder.CONVO_CANT_RETREAT: True,
                missionbuilder.CONVO_CANT_WITHDRAW: True,
            },
            objectives=objectives,
            one_chance=True,
            scenegen=sgen, architecture=archi,
            cash_reward=100, on_win=self._win_outcome, on_loss=self._lose_outcome
        )

        return el_seed

    def _win_outcome(self, camp):
        self.quest_record.win_task(self, camp)

    def _lose_outcome(self, camp):
        self.quest_record.lose_task(self, camp)

    def MISSION_GATE_menu(self, camp, thingmenu):
        thingmenu.add_item(self.mission_name, self._get_mission(camp))


class TheyHaveAFortress(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_CONCLUSION
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        outc = pstate.elements.get(quests.OUTCOME_ELEMENT_ID)
        return outc.verb in (ExpelVerb,) and gears.factions.is_a_faction(outc.o_elements.get(OE_ENEMYFACTION))

    def custom_init(self, nart):
        self.elements["_BASE_NAME"] = "Fortress"
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        my_enemy = my_outcome.o_elements.get(OE_ENEMYFACTION)
        self.elements["_ENEMY_FACTION"] = my_enemy
        self.mission_name = "Attack {_ENEMY_FACTION}'s {_BASE_NAME}".format(**self.elements)
        self.memo = plots.Memo(
            "You know the location of {_ENEMY_FACTION}'s {_BASE_NAME} and can attack at any time.".format(**self.elements),
            self.elements["METROSCENE"]
        )

        base_lore = quests.QuestLore(
            LORECAT_LOCATION, texts={
                quests.TEXT_LORE_HINT: "{_ENEMY_FACTION} has been working on a large project near {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_INFO: "they've built a {_BASE_NAME}".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "{_ENEMY_FACTION}'s project".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "You have learned about {_ENEMY_FACTION}'s {_BASE_NAME}.".format(**self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "{_ENEMY_FACTION}'s {_BASE_NAME}".format(**self.elements),
                L_LOCATION_NAME: "{_BASE_NAME}".format(**self.elements),
                quests.TEXT_LORE_MEMO: "{_ENEMY_FACTION} has a {_BASE_NAME} in {METROSCENE}.".format(
                    **self.elements),

            }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], my_enemy),
            outcome=my_outcome,
            tags=(
                LORETAG_ENEMY, LORETAG_PRIMARY
            ),
        )
        self.quest_record._needed_lore.add(base_lore)

        return True

    def _get_mission(self, camp):
        # Return a mission seed for the current state of this mission. The state may be altered by unfinished tasks-
        # For instance, if the fortress is defended by artillery, that gets added into the mission.
        objectives = [missionbuilder.BAMO_STORM_THE_CASTLE,]
        rank = self.rank

        #ace_task = self.quest_record.get_task(QUEST_TASK_ACE_DEFENSE)
        #if ace_task:
        #    drank, dobjs = ace_task.get_ace_mission_mods(camp)
        #    rank += drank
        #    objectives += dobjs

        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])

        el_seed = missionbuilder.BuildAMissionSeed(
                camp, self.mission_name,
                self.elements["METROSCENE"], self.elements["MISSION_GATE"],
                enemy_faction=self.elements["_ENEMY_FACTION"], rank=rank,
                objectives=objectives,
                one_chance=True,
                scenegen=sgen, architecture=archi,
                cash_reward=100, on_win=self._win_outcome, on_loss=self._lose_outcome
            )

        return el_seed

    def _win_outcome(self, camp):
        self.quest_record.win_task(self, camp)

    def _lose_outcome(self, camp):
        self.quest_record.lose_task(self, camp)

    def MISSION_GATE_menu(self, camp, thingmenu):
        thingmenu.add_item(self.mission_name, self._get_mission(camp))


#  ***********************
#  ***   QUEST  TASKS  ***
#  ***********************
#
# A Quest Task will have access to the quest itself and the quest outcome that it is leading to. It may also need some
# extra information; a conclusion or task should record elements for all the Quest Elements that might be needed by
# any of its potential_tasks.
#

class BaseKnownByCollaborator(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_TASK
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        quest = pstate.elements.get(quests.QUEST_ELEMENT_ID)
        lores = pstate.elements.get(quests.LORE_SET_ELEMENT_ID)
        conc = pstate.elements.get(quests.OUTCOME_ELEMENT_ID)
        return conc and conc.verb is ExpelVerb and cls.get_matching_lore(quest, lores) and conc.o_elements.get(OE_ENEMYFACTION)

    @staticmethod
    def get_matching_lore(quest: quests.Quest, lores):
        candidates = [l for l in lores if quest.lore_is_unlocked(
            l) and l.category == LORECAT_LOCATION and LORETAG_ENEMY in l.tags and LORETAG_HIDDEN not in l.tags]
        if candidates:
            return random.choice(candidates)

    LOCATION_CARDS = (
        {"name": "Bar", "to_verb": "to meet {} at the bar", "verbed": "met with {} at the bar",
         "did_not_verb": "didn't meet {} at the var", "data": {"image_name": "mystery_places.png", "frame": 1}},
        {"name": "Warehouse", "to_verb": "to meet {} at the warehourse", "verbed": "met with {} at the warehouse",
         "did_not_verb": "didn't meet {} at the warehouse", "data": {"image_name": "mystery_places.png", "frame": 3}},
        {"name": "Headquarters", "to_verb": "to meet {} at their headquarters", "verbed": "met {} at their headquarters",
         "did_not_verb": "didn't meet {} at their headquarters", "data": {"image_name": "mystery_places.png", "frame": 4}},
        {"name": "Disco", "to_verb": "to meet {} at the disco",
         "verbed": "met with {} at the disco",
         "did_not_verb": "didn't meet with {} at the disco", "data": {"image_name": "mystery_verbs.png", "frame": 0}},
        {"name": "Casino", "to_verb": "to meet {} at the casino",
         "verbed": "met with {} at the casino",
         "did_not_verb": "didn't go to the casino", "data": {"image_name": "mystery_verbs.png", "frame": 5}},
    )

    MOTIVE_CARDS = (
        {"name": "Secret Attack", "to_verb": "to plan a secret attack on {METROSCENE}",
         "verbed": "planned to attack {METROSCENE}",
         "did_not_verb": "didn't plan to attack {METROSCENE}",
         "data": {"image_name": "mystery_misc.png", "frame": 4}},
        {"name": "Money", "to_verb": "to get rich", "verbed": "accepted a bribe",
         "did_not_verb": "didn't get any money", "data": {"image_name": "mystery_motives.png", "frame": 8},
         "role": pbge.okapipuzzle.SUS_MOTIVE},
        {"name": "Hatred", "to_verb": "to get revenge on {METROSCENE}", "verbed": "hated {METROSCENE}",
         "did_not_verb": "didn't hate {METROSCENE}", "data": {"image_name": "mystery_motives.png", "frame": 0},
         "role": pbge.okapipuzzle.SUS_MOTIVE},
        {"name": "Secret", "to_verb": "to protect their secrets",
         "verbed": "was being blackmailed",
         "did_not_verb": "didn't have any secrets", "data": {"image_name": "mystery_motives.png", "frame": 1},
         },
        {"name": "Power", "to_verb": "to become the new ruler of {METROSCENE}",
         "verbed": "was promised rulership of {METROSCENE}",
         "did_not_verb": "didn't want to rule {METROSCENE}", "data": {"image_name": "mystery_motives.png", "frame": 7},
         },
        {"name": "Propaganda", "to_verb": "to plan a propaganda campaign",
         "verbed": "helped devise a propaganda campaign",
         "did_not_verb": "never worked in advertising", "data": {"image_name": "mystery_verbs.png", "frame": 6},
         },
        {"name": "Assassination", "to_verb": "to plan an assassination",
         "verbed": "was hired to perform an assassination",
         "did_not_verb": "never killed anybody", "data": {"image_name": "mystery_weapons.png", "frame": 0},
         }
    )

    def custom_init(self, nart):
        quest = self.elements.get(quests.QUEST_ELEMENT_ID)
        lores = self.elements.get(quests.LORE_SET_ELEMENT_ID)
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        mylore = self.get_matching_lore(quest, lores)
        quest.lock_lore(self, mylore)
        base_name = self.register_element("_BASE_NAME", mylore.texts.get(L_LOCATION_NAME, "base"))
        self.elements["_ENEMY_FACTION"] = my_outcome.o_elements.get(OE_ENEMYFACTION)

        suspect_cards = list()
        solution = list()
        self.suspects = list()
        myplot = self.add_sub_plot(nart, "ADD_BORING_NPC")
        npc = myplot.elements["NPC"]
        self.suspects.append(npc)
        suspect_cards.append(ghchallenges.NPCSusCard(npc))
        solution.append(suspect_cards[0])

        for t in range(4):
            npc = self.seek_element(nart, "_npc_{}".format(len(self.suspects)), self._is_good_npc, scope=self.elements["METROSCENE"], must_find=False)
            if not npc:
                myplot = self.add_sub_plot(nart, "ADD_BORING_NPC")
                npc = myplot.elements["NPC"]
            self.suspects.append(npc)
            suspect_cards.append(ghchallenges.NPCSusCard(npc))

        suspect_susdeck = pbge.okapipuzzle.SusDeck("Suspect", suspect_cards)

        location_cards = list()
        location_source = copy.deepcopy(random.sample(self.LOCATION_CARDS, 5))
        for wcd in location_source:
            for k, v in wcd.items():
                if isinstance(v, str):
                    wcd[k] = v.format(self.elements["_ENEMY_FACTION"])
            location_cards.append(pbge.okapipuzzle.VerbSusCard(**wcd))
        location_susdeck = pbge.okapipuzzle.SusDeck("Location", location_cards)
        solution.append(random.choice(location_cards))

        motive_cards = list()
        motive_source = copy.deepcopy(random.sample(self.MOTIVE_CARDS, 5))
        for mcd in motive_source:
            for k, v in mcd.items():
                if isinstance(v, str):
                    mcd[k] = v.format(**self.elements)
            motive_cards.append(pbge.okapipuzzle.VerbSusCard(**mcd))
        motive_susdeck = pbge.okapipuzzle.SusDeck("Motive", motive_cards)
        solution.append(random.choice(motive_cards))

        mymystery = self.register_element("MYSTERY", pbge.okapipuzzle.OkapiPuzzle(
            "{}'s Collaborator".format(self.elements["_ENEMY_FACTION"]),
            (suspect_susdeck, location_susdeck, motive_susdeck), "{a} {b.verbed} {c.to_verb}.",
            solution=solution
        ))

        # Store and lock the culprit.
        self.elements["CULPRIT"] = mymystery.solution[0].gameob
        self.elements["CULPRIT_SCENE"] = mymystery.solution[0].gameob.scene
        self.locked_elements.add(mymystery.solution[0].gameob)

        involved_set = set()
        for d in mymystery.decks:
            for c in d.cards:
                if c.gameob:
                    involved_set.add(c.gameob)
        excluded_set = involved_set.copy()

        mychallenge = self.register_element("_CHALLENGE", pbge.challenges.MysteryChallenge(
            str(mymystery), self.elements["MYSTERY"],
            memo=pbge.challenges.MysteryMemo("Someone in {} is collaborating with {}.".format(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"])),
            active=False,
            oppoffers=[
                pbge.challenges.AutoOffer(
                    dict(
                        msg="[I_KNOW_THINGS_ABOUT_STUFF] [LISTEN_TO_MY_INFO]",
                        context=ContextTag([context.CUSTOM, ]), effect=self._get_a_clue,
                        data={
                            "reply": "Do you know anything about {MYSTERY}?".format(**self.elements),
                            "stuff": "{MYSTERY}".format(**self.elements)
                        }, dead_end=True
                    ), active=True, uses=99,
                    involvement=ghchallenges.InvolvedIfCluesRemainAnd(
                        self.elements["MYSTERY"],
                        ghchallenges.InvolvedMetroResidentNPCs(self.elements["METROSCENE"], exclude=excluded_set)),
                    access_fun=ghchallenges.AccessSocialRoll(
                        gears.stats.Perception, gears.stats.Negotiation, self.rank, untrained_ok=True
                    )
                ),

                pbge.challenges.AutoOffer(
                    dict(
                        msg="[THINK_ABOUT_THIS] [I_REMEMBER_NOW]",
                        context=ContextTag([context.CUSTOM, ]),
                        data={
                            "reply": "Do you remember anything about {MYSTERY}?".format(**self.elements),
                            "stuff": "{MYSTERY}".format(**self.elements)
                        }, dead_end=True
                    ), active=True, uses=99,
                    involvement=ghchallenges.InvolvedIfUnassociatedCluesRemainAnd(
                        mymystery, mymystery.decks[0], pbge.challenges.InvolvedSet(involved_set)
                    ),
                    npc_effect=self._get_unassociated_clue,
                ),
            ],
        ))

        self.mystery_solved = False
        self.vigilante_action = False

        base_lore = quests.QuestLore(
            LORECAT_LOCATION, texts={
                quests.TEXT_LORE_HINT: "{_ENEMY_FACTION} has a collaborator in {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_INFO: "only the collaborator knows the location of {_ENEMY_FACTION}'s {_BASE_NAME}".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "the collaborator".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "{_ENEMY_FACTION} must have a collaborator in {METROSCENE}; uncovering them could lead you to their base.".format(**self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "the secret {_BASE_NAME}".format(**self.elements),
                quests.TEXT_LORE_MEMO: "{_ENEMY_FACTION} has a collaborator in {METROSCENE} who knows the location of their {_BASE_NAME}.".format(
                    **self.elements),
            }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]), 
            outcome=my_outcome
        )
        self.quest_record._needed_lore.add(base_lore)

        return True

    def _is_good_npc(self, nart, candidate):
        if isinstance(candidate, gears.base.Character) and nart.camp.is_not_lancemate(candidate):
            faction_ok = candidate.faction and not nart.camp.are_faction_allies(candidate, self.elements["_ENEMY_FACTION"])
            scene_ok = candidate.scene and gears.tags.SCENE_PUBLIC in candidate.scene.attributes
            return faction_ok and scene_ok and candidate not in self.suspects

    def start_quest_task(self, camp):
        self.elements["_CHALLENGE"].activate(camp)

    def _get_unassociated_clue(self, camp, npc):
        candidates = [c for c in self.elements["MYSTERY"].unknown_clues if not c.is_involved(npc)]
        if candidates:
            self.elements["_CHALLENGE"].advance(camp, random.choice(candidates))
        else:
            self.elements["_CHALLENGE"].advance(camp)

    def _get_a_clue(self, camp):
        self.elements["_CHALLENGE"].advance(camp)

    def MYSTERY_SOLVED(self, camp):
        self.mystery_solved = True
        my_npc = self.elements["CULPRIT"]
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        base_name = self.elements.get("_BASE_NAME", "Base")
        pbge.BasicNotification(
            "You have learned that {} knows where {}'s {} is.".format(my_npc, self.elements["_ENEMY_FACTION"], base_name),
            count=150
        )
        self.memo = plots.Memo(
            "You have learned that {} knows where {}'s {} is.".format(my_npc, self.elements["_ENEMY_FACTION"], base_name),
            location=my_npc.scene
        )

    def win_da_task(self, camp):
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        base_name = self.elements.get("_BASE_NAME", "Base")
        pbge.BasicNotification("You have discovered the location of {}'s {}.".format(self.elements["_ENEMY_FACTION"], base_name),
                               count=150)
        self.quest_record.win_task(self, camp)

    def CULPRIT_offers(self, camp):
        mylist = list()
        if self.mystery_solved:
            my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
            base_name = "{}'s {}".format(self.elements["_ENEMY_FACTION"], self.elements["_BASE_NAME"])

            mylist.append(Offer(
                "[LETS_KEEP_THIS_A_SECRET] I will tell you the location of {}!".format(base_name),
                ContextTag([context.CUSTOM,]), effect=self.win_da_task,
                data={"reply": "I know that you've been collaborating with {}.".format(self.elements["_ENEMY_FACTION"])}
            ))

        return mylist

    def CULPRIT_SCENE_ENTER(self, camp):
        if self.mystery_solved:
            my_npc: gears.base.Character = self.elements["CULPRIT"]
            my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
            base_name = "{}'s {}".format(self.elements["_ENEMY_FACTION"], self.elements["_BASE_NAME"])
            if self.vigilante_action or my_npc.is_destroyed():
                pbge.alert("As you enter {CULPRIT_SCENE}, you notice the conspicuous absense of {CULPRIT}.".format(**self.elements))
                pbge.alert("A dataslate has been left behind with a set of map coordinates. Could this be the location of {}?".format(base_name))
                self.win_da_task(camp)

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        culprit = self.elements["CULPRIT"]
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]

        if not self.vigilante_action:
            if self.mystery_solved and my_outcome.is_involved(camp, npc) and npc is not culprit:
                goffs.append(Offer(
                    "[THATS_INTERESTING] [THIS_WILL_BE_DEALT_WITH]",
                    ContextTag([context.CUSTOM,]), effect=self._do_vigilante_action,
                    data={"reply": "I have proof that {} has been collaborating with {}.".format(culprit,
                                                                                                 self.elements["_ENEMY_FACTION"])}
                ))

        return goffs

    def _do_vigilante_action(self, camp: gears.GearHeadCampaign):
        self.vigilante_action = True
        npc: gears.base.Character = self.elements["CULPRIT"]
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        camp.freeze(npc)
        myfac = camp.get_faction(self.elements["_ENEMY_FACTION"])
        if npc.combatant and myfac and myfac.get_faction_tag():
            npc.relationship = camp.get_relationship(npc)
            npc.relationship.role = gears.relationships.R_ADVERSARY
            npc.relationship.history.append(
                gears.relationships.Memory(
                    "you revealed that I was working for {}".format(self.elements["_ENEMY_FACTION"]),
                    "I discovered you were working for {}".format(self.elements["_ENEMY_FACTION"]),
                    -5, memtags=(gears.relationships.MEM_Clash, gears.relationships.MEM_Ideological)
                )
            )
            npc.faction = myfac.get_faction_tag()
            camp.egg.dramatis_personae.add(npc)


class CommanderKnowsMotive(quests.QuestPlot):
    # You know who knows the enemy faction's motive? The enemy commander.
    LABEL = quests.DEFAULT_QUEST_TASK
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        quest = pstate.elements.get(quests.QUEST_ELEMENT_ID)
        lores = pstate.elements.get(quests.LORE_SET_ELEMENT_ID)
        outc = pstate.elements.get(quests.OUTCOME_ELEMENT_ID)
        return (
            outc and gears.factions.is_a_faction(outc.o_elements.get(OE_ENEMYFACTION)) and
            cls.get_matching_lore(quest, lores) and OTAG_AGGRESSIVE in outc.verb.tags and
            "MISSION_GATE" in pstate.elements
        )

    @staticmethod
    def get_matching_lore(quest: quests.Quest, lores):
        candidates = [l for l in lores if quest.lore_is_unlocked(l) and LORETAG_ENEMY in l.tags and LORETAG_HIDDEN
                      not in l.tags and l.category == LORECAT_MOTIVE]
        if candidates:
            return random.choice(candidates)

    def get_secondary_lore(self, quest: quests.Quest, lores):
        candidates = [
            cl for cl in lores if
            quest.lore_is_unlocked(cl) and LORETAG_ENEMY in cl.tags and LORETAG_HIDDEN not in cl.tags and
            cl.category == LORECAT_CHARACTER and L_CHARACTER_IDENTITY in cl.texts and
            cl.texts[L_CHARACTER_IDENTITY].combatant and
            quest.will_not_cause_lore_blockage(quests.LoreBlockRecord(self.quest_record, new_locked_lore=cl))
        ]
        if candidates:
            return random.choice(candidates)

    def custom_init(self, nart):
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        self.elements["_ENEMY_FACTION"] = my_outcome.o_elements.get(OE_ENEMYFACTION)

        quest = self.elements.get(quests.QUEST_ELEMENT_ID)
        lores = self.elements.get(quests.LORE_SET_ELEMENT_ID)
        self.locked_lore = self.get_matching_lore(quest, lores)
        quest.lock_lore(self, self.locked_lore)

        new_lore = quests.QuestLore(
            LORECAT_MOTIVE, texts={
                quests.TEXT_LORE_HINT: "{_ENEMY_FACTION} is up to something".format(**self.elements),
                quests.TEXT_LORE_INFO: "nobody knows what {_ENEMY_FACTION} is doing in {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "{_ENEMY_FACTION}'s plans".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "{_ENEMY_FACTION} must be planning something big in {METROSCENE}, but what?".format(**self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "{_ENEMY_FACTION}'s plans for {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_MEMO: "{_ENEMY_FACTION} has secret plans for {METROSCENE}.".format(
                    **self.elements),
                L_MOTIVE_CONFESSION: "I could tell you what we're planning, but I think it'd be better if I didn't"
            }, 
            involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]),
            outcome=my_outcome,
            tags=(LORETAG_ENEMY, LORETAG_HIDDEN)
        )
        self.quest_record.add_needed_lore(quest, self, new_lore)

        exlore = self.get_secondary_lore(quest, lores)
        if exlore:
            mynpc = self.register_element("_ENEMY_COMMANDER", exlore.texts[L_CHARACTER_IDENTITY], lock=True)
            quest.lock_lore(self, exlore)
        else:
            mynpc = self.register_element("_ENEMY_COMMANDER", nart.camp.cast_a_combatant(
                self.elements["_ENEMY_FACTION"], self.rank + 20, myplot=self
            ), lock=True)

        new_lore = quests.QuestLore(
            LORECAT_CHARACTER, texts={
                quests.TEXT_LORE_HINT: "{_ENEMY_COMMANDER} is working for {_ENEMY_FACTION}".format(**self.elements),
                quests.TEXT_LORE_INFO: "whatever they have planned for {METROSCENE}, {_ENEMY_COMMANDER} must know what's up".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "{_ENEMY_COMMANDER}'s mission".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "{_ENEMY_COMMANDER} must must know what {_ENEMY_FACTION} is planning in {METROSCENE}.".format(**self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "{_ENEMY_COMMANDER}'s mission in {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_MEMO: "{_ENEMY_COMMANDER} knows {_ENEMY_FACTION}'s plans for {METROSCENE}.".format(
                    **self.elements),
                L_CHARACTER_ALIAS: "the {_ENEMY_FACTION} commander".format(**self.elements),
                L_CHARACTER_IDENTITY: mynpc,
            }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]), outcome=my_outcome,
            tags=(LORETAG_ENEMY,)
        )
        self.quest_record.add_needed_lore(quest, self, new_lore)

        mychallenge: Challenge = self.register_element(
            "_CHALLENGE", Challenge(
                "Fight {_ENEMY_COMMANDER} to learn {_ENEMY_FACTION}'s plans for {METROSCENE},".format(**self.elements),
                ghchallenges.MISSION_CHALLENGE,
                key=(self.elements["_ENEMY_FACTION"],), involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]),
                data={
                    "challenge_objectives": [
                        "prevent {_ENEMY_COMMANDER} from threatening {METROSCENE}".format(**self.elements),
                        "defeat {_ENEMY_COMMANDER} and {_ENEMY_COMMANDER.gender.possessive_determiner} troops".format(**self.elements),
                        "stop {_ENEMY_COMMANDER} from carrying out {_ENEMY_FACTION}'s objectives".format(**self.elements),
                        "intercept {_ENEMY_FACTION} before {_ENEMY_COMMANDER} can complete their mission".format(**self.elements),
                    ],
                    "challenge_summaries": [
                        "protect {METROSCENE} from {_ENEMY_COMMANDER}".format(**self.elements),
                        "prevent {_ENEMY_COMMANDER} from completing {_ENEMY_COMMANDER.gender.possessive_determiner} mission".format(**self.elements),
                    ],
                    "challenge_rumors": [
                        "{_ENEMY_FACTION} has sent {_ENEMY_COMMANDER} to {METROSCENE}".format(**self.elements),
                        "{_ENEMY_COMMANDER} is {_ENEMY_FACTION}'s chief agent in {METROSCENE}".format(**self.elements),
                    ],
                    "challenge_subject": [
                        "{_ENEMY_COMMANDER}'s mission".format(**self.elements),
                    ],
                    "mission_intros": [
                        "we are under threat by {_ENEMY_FACTION}".format(**self.elements),
                        "{_ENEMY_FACTION} is planning something in {METROSCENE} and have sent {_ENEMY_COMMANDER} to do it".format(**self.elements),
                        "{_ENEMY_FACTION} is working on a mysterious plan in {METROSCENE}".format(**self.elements),
                    ],
                    "mission_builder": self._build_mission,
                    "priority_mission": my_outcome.prioritize_lore
                },
                memo=ChallengeMemo(
                    "You are trying to stop {_ENEMY_COMMANDER} from carrying out {_ENEMY_FACTION}'s mission in {METROSCENE}.".format(**self.elements)
                ), memo_active=False, points_target=1, num_simultaneous_plots=1
            )
        )
        return True

    OBJECTIVES = (
        missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL,
        missionbuilder.BAMO_AID_ALLIED_FORCES
    )

    def _build_mission(self, camp, npc):
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])
        return missionbuilder.BuildAMissionSeed(
            camp, "Defeat and interrogate {_ENEMY_COMMANDER}".format(**self.elements),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            allied_faction=npc.faction,
            enemy_faction=self.elements["_ENEMY_FACTION"], rank=self.rank,
            objectives=[missionbuilder.BAMO_DEFEAT_NPC] + [random.choice(self.OBJECTIVES)],
            custom_elements={
                missionbuilder.BAME_NPC: self.elements["_ENEMY_COMMANDER"],
                missionbuilder.CONVO_CANT_RETREAT: True,
            },
            scenegen=sgen, architecture=archi,
            cash_reward=100, on_win=self._win_the_mission,
            mission_grammar=missionbuilder.MissionGrammar(
                "stop {_ENEMY_FACTION}".format(**self.elements),
                "serve {_ENEMY_FACTION}".format(**self.elements),
                "I defeated you and {_ENEMY_FACTION} in {METROSCENE}".format(**self.elements),
                "you ruined my mission for {_ENEMY_FACTION} in {METROSCENE}".format(**self.elements),
                "you defeated me in {METROSCENE}".format(**self.elements),
                "I defeated you in {METROSCENE}".format(**self.elements),
            )
        )

    def _win_the_mission(self, camp: gears.GearHeadCampaign):
        self.elements["_CHALLENGE"].advance(camp, 100)

    def _CHALLENGE_WIN(self, camp):
        pbge.alert("As you survey your victory, you get one final message from {}.".format(self.elements["_ENEMY_COMMANDER"]))
        ghcutscene.SimpleMonologueDisplay(
            "[YOU_WILL_NEVER_DEFEAT_US] {}!".format(self.locked_lore.texts[L_MOTIVE_CONFESSION]),
            self.elements["_ENEMY_COMMANDER"]
        )(camp)
        self.quest_record.win_task(self, camp)


class DefendThePowerStation(quests.QuestPlot):
    # I seem to do a lot of plots involving power stations. Probably because of The Empire Strikes Back and also because
    # my grandfather helped build the hydroelectric plant in Deer Lake. The generation of electricity occupies a lot of
    # real estate in my brain.
    # Not sure that it makes sense because GearHead mecha run on atmospheric hydrogen fusion reactors, so if the local
    # powerplant got destroyed you could just hook your power grid up to a couple of BuruBurus. Though the pilots would
    # not like that. Most boring mission ever.
    # You know what? I'm gonna leave the plot name as it is, but choose a public utility at random. That way it won't
    # always be a power station.
    LABEL = quests.DEFAULT_QUEST_TASK
    scope = "METRO"

    PUBLIC_UTILITIES = (
        "power station", "water treatment plant", "thrunet hub", "hydroponic farm", "sewage treatment facility",
        "recycling plant", "desalination plant", "fusion reactor", "geothermal reactor", "nuclear reactor",
        "computing core", "armory", "mecha hangar"
    )

    @classmethod
    def matches(cls, pstate):
        quest = pstate.elements.get(quests.QUEST_ELEMENT_ID)
        lores = pstate.elements.get(quests.LORE_SET_ELEMENT_ID)
        outc = pstate.elements.get(quests.OUTCOME_ELEMENT_ID)
        return (
            outc and outc.o_elements.get(OE_ENEMYFACTION) and
            cls.get_matching_lore(quest, lores) and OTAG_AGGRESSIVE in outc.verb.tags and
            pstate.elements["METROSCENE"].attributes.intersection({gears.personality.GreenZone,
                                                                   gears.personality.DeadZone}) and
            "MISSION_GATE" in pstate.elements
        )

    @staticmethod
    def get_matching_lore(quest: quests.Quest, lores):
        candidates = [l for l in lores if quest.lore_is_unlocked(l) and LORETAG_ENEMY in l.tags and l.category == LORECAT_MOTIVE]
        if candidates:
            return random.choice(candidates)

    def custom_init(self, nart):
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        self.elements["_ENEMY_FACTION"] = my_outcome.o_elements.get(OE_ENEMYFACTION)
        self.elements["PUBLIC_UTILITY"] = random.choice(self.PUBLIC_UTILITIES)

        if not nart.camp.are_faction_enemies(self.elements["_ENEMY_FACTION"], self.elements["METROSCENE"]):
            return False

        new_lore = quests.QuestLore(
            LORECAT_EMERGENCY, texts={
                quests.TEXT_LORE_HINT: "{_ENEMY_FACTION} forces have been spotted near {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_INFO: "{_ENEMY_FACTION} plans to attack the {PUBLIC_UTILITY}".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "{_ENEMY_FACTION} forces".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "You find evidence that {_ENEMY_FACTION} is planning an attack on {METROSCENE}'s {PUBLIC_UTILITY}.".format(**self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "{_ENEMY_FACTION}'s plans for {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_MEMO: "{_ENEMY_FACTION} is planning an attack on {METROSCENE}'s {PUBLIC_UTILITY}.".format(
                    **self.elements),
            }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]), outcome=my_outcome,
            tags=(LORETAG_ENEMY,)
        )
        self.quest_record._needed_lore.add(new_lore)

        quest = self.elements.get(quests.QUEST_ELEMENT_ID)
        lores = self.elements.get(quests.LORE_SET_ELEMENT_ID)
        self.locked_lore = self.get_matching_lore(quest, lores)
        quest.lock_lore(self, self.locked_lore)

        mychallenge: Challenge = self.register_element(
            "_CHALLENGE", Challenge(
                "Defend the {_PUBLIC_UTILITY} from {_ENEMY_FACTION}".format(**self.elements),
                ghchallenges.MISSION_CHALLENGE,
                key=(self.elements["_ENEMY_FACTION"],), involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]),
                data={
                    "challenge_objectives": [
                        "save {METROSCENE}'s {PUBLIC_UTILITY} from {_ENEMY_FACTION}".format(**self.elements),
                        "protect our {PUBLIC_UTILITY} from {_ENEMY_FACTION}".format(**self.elements),
                        "stop {_ENEMY_FACTION} from looting the {PUBLIC_UTILITY}".format(**self.elements),
                        "intercept {_ENEMY_FACTION} before they can reach the {PUBLIC_UTILITY}".format(**self.elements),
                    ],
                    "challenge_summaries": [
                        "protect {METROSCENE}'s {PUBLIC_UTILITY} from {_ENEMY_FACTION}".format(**self.elements),
                        "prevent {_ENEMY_FACTION} from destroying {METROSCENE}'s {PUBLIC_UTILITY}".format(**self.elements),
                    ],
                    "challenge_rumors": [
                        "{_ENEMY_FACTION} is attacking the {PUBLIC_UTILITY}".format(**self.elements),
                        "our {PUBLIC_UTILITY} is being raided by {_ENEMY_FACTION}".format(**self.elements),
                    ],
                    "challenge_subject": [
                        "the {PUBLIC_UTILITY}".format(**self.elements),
                    ],
                    "mission_intros": [
                        "our {PUBLIC_UTILITY} is being targeted by {_ENEMY_FACTION}".format(**self.elements),
                        "{_ENEMY_FACTION} is planning to raid {METROSCENE}'s {PUBLIC_UTILITY}".format(**self.elements),
                        "{_ENEMY_FACTION}'s looting of {METROSCENE} has to stop".format(**self.elements),
                    ],
                    "mission_builder": self._build_mission,
                    "priority_mission": my_outcome.prioritize_lore
                },
                memo=ChallengeMemo(
                    "You are trying to prevent {_ENEMY_FACTION} from destroying {METROSCENE}'s {PUBLIC_UTILITY}.".format(**self.elements)
                ), memo_active=False, points_target=1, num_simultaneous_plots=1
            )
        )

        return True

    OBJECTIVES = (
        missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_DEFEAT_COMMANDER,
        missionbuilder.BAMO_AID_ALLIED_FORCES
    )

    def _build_mission(self, camp, npc):
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])
        return missionbuilder.BuildAMissionSeed(
            camp, "Defend the {PUBLIC_UTILITY} from {_ENEMY_FACTION}".format(**self.elements),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            allied_faction=npc.faction,
            enemy_faction=self.elements["_ENEMY_FACTION"], rank=self.rank,
            objectives=[missionbuilder.BAMO_PROTECT_BUILDINGS] + [random.choice(self.OBJECTIVES)],
            custom_elements={
                missionbuilder.CONVO_CANT_WITHDRAW: True,
            },
            scenegen=sgen, architecture=archi,
            cash_reward=100, on_win=self._win_the_mission,
            mission_grammar=missionbuilder.MissionGrammar(
                "protect the {PUBLIC_UTILITY}".format(**self.elements),
                "destroy the {PUBLIC_UTILITY}".format(**self.elements),
                "I protected {METROSCENE}'s {PUBLIC_UTILITY} from you".format(**self.elements),
                "you foiled my mission in {METROSCENE}".format(**self.elements),
                "you destroyed {METROSCENE}'s {PUBLIC_UTILITY}".format(**self.elements),
                "I destroyed {METROSCENE}'s {PUBLIC_UTILITY}".format(**self.elements),
            )
        )

    def _win_the_mission(self, camp: gears.GearHeadCampaign):
        self.elements["_CHALLENGE"].advance(camp, 100)

    def _CHALLENGE_WIN(self, camp):
        pbge.alert("[DISCOVERY_AFTER_MECHA_COMBAT] {}".format(self.locked_lore.texts[quests.TEXT_LORE_SELFDISCOVERY]))
        self.quest_record.win_task(self, camp)


class FindEnemyBaseTask(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_TASK
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        quest = pstate.elements.get(quests.QUEST_ELEMENT_ID)
        lores = pstate.elements.get(quests.LORE_SET_ELEMENT_ID)
        return cls.get_matching_lore(quest, lores)

    @staticmethod
    def get_matching_lore(quest: quests.Quest, lores):
        candidates = [l for l in lores if quest.lore_is_unlocked(l) and l.category == LORECAT_LOCATION and LORETAG_ENEMY in l.tags and LORETAG_HIDDEN not in l.tags]
        if candidates:
            return random.choice(candidates)

    def custom_init(self, nart):
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        self.elements["_ENEMY_FACTION"] = my_outcome.o_elements.get(OE_ENEMYFACTION)
        quest = self.elements.get(quests.QUEST_ELEMENT_ID)
        lores = self.elements.get(quests.LORE_SET_ELEMENT_ID)
        mylore = self.get_matching_lore(quest, lores)
        quest.lock_lore(self, mylore)
        base_name = self.register_element("_BASE_NAME", mylore.texts.get(L_LOCATION_NAME, "base"))
        mychallenge: Challenge = self.register_element(
            "_CHALLENGE", Challenge(
                "Locate {}'s {}".format(self.elements["_ENEMY_FACTION"], base_name), ghchallenges.LOCATE_ENEMY_BASE_CHALLENGE,
                key=(self.elements["_ENEMY_FACTION"],), involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]),
                data={"base_name": base_name},
                oppoffers=(
                    AutoOffer(
                        dict(
                            msg="[OF_COURSE] I'll send the coordinates to your phone.".format(**self.elements),
                            context=ContextTag([context.CUSTOM, ]),
                            data={
                                "reply": "Can you tell me how to get to {}'s {}? [PRETEXT_FOR_GOING_THERE]".format(
                                    self.elements["_ENEMY_FACTION"], base_name)
                            }, dead_end=True, effect=self._advance_fully
                        ), active=True, uses=99,
                        access_fun=ghchallenges.AccessSkillRoll(
                            gears.stats.Charm, gears.stats.Stealth, self.rank, difficulty=gears.stats.DIFFICULTY_EASY
                        ),
                        involvement=ghchallenges.InvolvedMetroFactionNPCs(
                            self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]
                        )
                    ),
                    AutoOffer(
                        dict(
                            msg="[OF_COURSE] I'll send the coordinates to your phone.".format(**self.elements),
                            context=ContextTag([context.UNFAVORABLE_CUSTOM, ]),
                            data={
                                "reply": "Can you tell me how to get to {}'s {}? [PRETEXT_FOR_GOING_THERE]".format(
                                    self.elements["_ENEMY_FACTION"], base_name)
                            }, dead_end=True, effect=self._advance_fully
                        ), active=True, uses=99,
                        access_fun=ghchallenges.AccessSkillRoll(
                            gears.stats.Charm, gears.stats.Stealth, self.rank, difficulty=gears.stats.DIFFICULTY_HARD
                        ),
                        involvement=ghchallenges.InvolvedMetroFactionNPCs(
                            self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]
                        )
                    ),
                ), memo=ChallengeMemo(
                    "{} have a hidden {} near {}.".format(self.elements["_ENEMY_FACTION"], base_name, self.elements["METROSCENE"])
                ), memo_active=True
            )
        )

        base_lore = quests.QuestLore(
            LORECAT_LOCATION, texts={
                quests.TEXT_LORE_HINT: "{_ENEMY_FACTION} has been working on a large project near {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_INFO: "{_ENEMY_FACTION} has constructed a secret {_BASE_NAME} in this area".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "{_ENEMY_FACTION}'s presence here".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "{_ENEMY_FACTION} must have a {_BASE_NAME} nearby, but where?".format(**self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "the hidden {_BASE_NAME}".format(**self.elements),
                L_LOCATION_NAME: base_name,
                quests.TEXT_LORE_MEMO: "{_ENEMY_FACTION} must have a {_BASE_NAME} near {METROSCENE}.".format(
                    **self.elements),
            }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]), outcome=my_outcome
        )
        self.quest_record._needed_lore.add(base_lore)

        return True

    def start_quest_task(self, camp):
        if "_LORE" in self.elements:
            self.quest_record.quest.reveal_lore(camp, self.elements["_LORE"])

    def _advance_challenge(self, camp):
        self.elements["CHALLENGE"].advance(camp, 2)

    def _advance_fully(self, camp):
        self.elements["CHALLENGE"].advance(camp, 100)

    def _CHALLENGE_WIN(self, camp):
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        base_name = self.elements.get("_BASE_NAME", "Base")
        pbge.BasicNotification("You have discovered the location of {}'s {}.".format(self.elements["_ENEMY_FACTION"], base_name),
                               count=150)
        self.quest_record.win_task(self, camp)


class InvestigateEnemyThroughCombatTask(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_TASK
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        quest = pstate.elements.get(quests.QUEST_ELEMENT_ID)
        lores = pstate.elements.get(quests.LORE_SET_ELEMENT_ID)
        my_outcome: quests.QuestOutcome = pstate.elements.get(quests.OUTCOME_ELEMENT_ID)
        return (
                my_outcome and my_outcome.o_elements.get(OE_ENEMYFACTION) and
                "MISSION_GATE" in pstate.elements and
                cls.get_matching_lore(quest, lores)
        )

    @staticmethod
    def get_matching_lore(quest: quests.Quest, lores):
        candidates = [l for l in lores if quest.lore_is_unlocked(l) and l.category == LORECAT_MOTIVE and LORETAG_ENEMY in l.tags and LORETAG_HIDDEN not in l.tags]
        if candidates:
            return random.choice(candidates)

    def custom_init(self, nart):
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        self.elements["_ENEMY_FACTION"] = my_outcome.o_elements.get(OE_ENEMYFACTION)

        if not nart.camp.are_faction_enemies(self.elements["_ENEMY_FACTION"], self.elements["METROSCENE"]):
            return False

        quest = self.elements.get(quests.QUEST_ELEMENT_ID)

        allied_faction = my_outcome.o_elements.get(OE_ALLYFACTION)
        if not allied_faction:
            allied_faction = self.elements["METROSCENE"].faction
        self.elements["_ALLIED_FACTION"] = allied_faction

        new_lore = quests.QuestLore(
            LORECAT_EMERGENCY, texts={
                quests.TEXT_LORE_HINT: "{_ENEMY_FACTION} has been causing trouble".format(**self.elements),
                quests.TEXT_LORE_INFO: "{_ENEMY_FACTION} mecha have been spotted near {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "{_ENEMY_FACTION} forces".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "You find evidence that {_ENEMY_FACTION} has been conducting operations near {METROSCENE}.".format(**self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "{_ENEMY_FACTION}'s forces in {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_MEMO: "{_ENEMY_FACTION} has been conducting operations near {METROSCENE}.".format(
                    **self.elements),
            }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]), outcome=my_outcome,
            tags=(LORETAG_ENEMY, LORETAG_HIDDEN)
        )
        self.quest_record.add_needed_lore(quest, self, new_lore)

        lores = self.elements.get(quests.LORE_SET_ELEMENT_ID)
        self.locked_lore = self.get_matching_lore(quest, lores)
        quest.lock_lore(self, self.locked_lore)

        if allied_faction:
            my_involvement = ghchallenges.InvolvedMetroFactionNPCs(self.elements["METROSCENE"], allied_faction)
            self.add_sub_plot(nart, "ENSURE_LOCAL_OPERATIVES", elements={"FACTION": allied_faction}, ident="LOCAL_REPS")
            self.subplots["LOCAL_REPS"].active = False
        else:
            my_involvement = ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"])

        mychallenge: Challenge = self.register_element(
            "_CHALLENGE", Challenge(
                "Investigate {}".format(self.elements["_ENEMY_FACTION"]), ghchallenges.MISSION_CHALLENGE,
                key=(self.elements["_ENEMY_FACTION"],),
                involvement=my_involvement,
                data={
                    "challenge_objectives": [
                        "investigate {_ENEMY_FACTION}'s activities near {METROSCENE}".format(**self.elements),
                        "find out what {_ENEMY_FACTION} has in store for {METROSCENE}".format(**self.elements),
                        "stop {_ENEMY_FACTION} from doing whatever it is they've planned".format(**self.elements),
                        "intercept {_ENEMY_FACTION}'s forces and gather as much information as possible".format(
                            **self.elements),
                        "seek out {_ENEMY_FACTION} and put an end to their plans".format(**self.elements),
                    ],
                    "challenge_summaries": [
                        "investigate {_ENEMY_FACTION}'s plans for {METROSCENE}".format(**self.elements),
                        "gather information on {_ENEMY_FACTION}".format(**self.elements),
                    ],
                    "challenge_rumors": [
                        "nobody knows what {_ENEMY_FACTION} has in store for {METROSCENE}".format(**self.elements),
                        "someone needs to find out what {_ENEMY_FACTION} is up to".format(**self.elements),
                    ],
                    "challenge_subject": [
                        "{_ENEMY_FACTION}'s activities".format(**self.elements),
                    ],
                    "mission_intros": [
                        "track down a lance belonging to {_ENEMY_FACTION} and gauge their strength".format(**self.elements),
                        "we are gathering info on {_ENEMY_FACTION}".format(**self.elements),
                        "I need someone to find out what {_ENEMY_FACTION} is doing in {METROSCENE}".format(**self.elements),
                    ],
                    "mission_builder": self._build_mission,
                    "priority_mission": my_outcome.prioritize_lore
                },
                memo=ChallengeMemo(
                    "You are investigating {} activity near {}.".format(self.elements["_ENEMY_FACTION"], self.elements["METROSCENE"])
                ), memo_active=True, points_target=10, num_simultaneous_plots=1
            )
        )

        return True

    OBJECTIVES = (
        missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_DEFEAT_COMMANDER,
        missionbuilder.BAMO_AID_ALLIED_FORCES, missionbuilder.BAMO_EXTRACT_ALLIED_FORCES,
        missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL, missionbuilder.BAMO_CAPTURE_BUILDINGS
    )

    def _build_mission(self, camp, npc):
        # Find some text hints to build the mission grammar.
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        candidates = [str(self.elements["_ENEMY_FACTION"])]
        for known_lore in self.quest_record.quest.revealed_lore:
            if known_lore.outcome is my_outcome and quests.TEXT_LORE_TARGET_TOPIC in known_lore.texts:
                candidates.append(known_lore.texts[quests.TEXT_LORE_TARGET_TOPIC])

        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])
        return missionbuilder.BuildAMissionSeed(
            camp, "{}'s Mission".format(npc),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            allied_faction=npc.faction,
            enemy_faction=self.elements["_ENEMY_FACTION"], rank=self.rank,
            objectives=random.sample(self.OBJECTIVES, 2),
            scenegen=sgen, architecture=archi,
            cash_reward=100, on_win=self._win_the_mission,
            mission_grammar=missionbuilder.MissionGrammar(
                "learn more about {}".format(random.choice(candidates)),
                "ensure the success of {}".format(random.choice(candidates)),
                "I uncovered {}'s secrets".format(self.elements["_ENEMY_FACTION"]),
                "you learned too much about {}".format(self.elements["_ENEMY_FACTION"]),
                "I was defeated by {}".format(self.elements["_ENEMY_FACTION"]),
                "I defeated you in the name of {}".format(self.elements["_ENEMY_FACTION"]),
            )
        )

    def start_quest_task(self, camp):
        if "LOCAL_REPS" in self.subplots:
            self.subplots["LOCAL_REPS"].activate(camp)

    def end_quest_task(self, camp):
        if "LOCAL_REPS" in self.subplots:
            self.subplots["LOCAL_REPS"].deactivate(camp)

    def _win_the_mission(self, camp: gears.GearHeadCampaign):
        learning_is_half_the_battle = camp.make_skill_roll(gears.stats.Perception, gears.stats.Scouting,
                                                           untrained_ok=True)
        points = max((learning_is_half_the_battle-30)//20, 1)
        self.elements["_CHALLENGE"].advance(camp, points)

    def _CHALLENGE_WIN(self, camp):
        ghcutscene.alert_with_grammar(camp, "[DISCOVERY_AFTER_MECHA_COMBAT] {}".format(self.locked_lore.texts[quests.TEXT_LORE_SELFDISCOVERY]))
        self.quest_record.win_task(self, camp)


class SecretWarInvestigation(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_TASK
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        quest = pstate.elements.get(quests.QUEST_ELEMENT_ID)
        lores = pstate.elements.get(quests.LORE_SET_ELEMENT_ID)
        my_outcome: quests.QuestOutcome = pstate.elements.get(quests.OUTCOME_ELEMENT_ID)
        return (
                my_outcome and my_outcome.o_elements.get(OE_ENEMYFACTION) and
                "MISSION_GATE" in pstate.elements and
                cls.get_matching_lore(quest, lores)
        )

    @staticmethod
    def get_matching_lore(quest: quests.Quest, lores):
        candidates = [l for l in lores if quest.lore_is_unlocked(
            l) and l.category == LORECAT_MOTIVE and LORETAG_ENEMY in l.tags and LORETAG_HIDDEN not in l.tags]
        if candidates:
            return random.choice(candidates)

    def custom_init(self, nart):
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        self.elements["_ENEMY_FACTION"] = my_outcome.o_elements.get(OE_ENEMYFACTION)

        if nart.camp.are_faction_enemies(self.elements["_ENEMY_FACTION"], self.elements["METROSCENE"]):
            return False

        quest = self.elements.get(quests.QUEST_ELEMENT_ID)

        new_lore = quests.QuestLore(
            LORECAT_EMERGENCY, texts={
                quests.TEXT_LORE_HINT: "{_ENEMY_FACTION} is up to something".format(**self.elements),
                quests.TEXT_LORE_INFO: "people coming into {METROSCENE} have seen a lot of {_ENEMY_FACTION} mecha around".format(
                    **self.elements),
                quests.TEXT_LORE_TOPIC: "{_ENEMY_FACTION} mecha".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "You find evidence that {_ENEMY_FACTION} is performing secret operations near {METROSCENE}.".format(
                    **self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "{_ENEMY_FACTION}'s forces in {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_MEMO: "Mecha belonging to {_ENEMY_FACTION} have been spotted near {METROSCENE}.".format(
                    **self.elements),
            }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"],
                                                                           self.elements["_ENEMY_FACTION"]),
            outcome=my_outcome,
            tags=(LORETAG_ENEMY, LORETAG_HIDDEN)
        )
        self.quest_record.add_needed_lore(quest, self, new_lore)

        lores = self.elements.get(quests.LORE_SET_ELEMENT_ID)
        self.locked_lore = self.get_matching_lore(quest, lores)
        quest.lock_lore(self, self.locked_lore)

        allied_faction = my_outcome.o_elements.get(OE_ALLYFACTION)
        if allied_faction:
            self.elements["_ALLIED_FACTION"] = allied_faction
            my_involvement = ghchallenges.InvolvedMetroFactionNPCs(self.elements["METROSCENE"], allied_faction)
            self.add_sub_plot(nart, "ENSURE_LOCAL_OPERATIVES", elements={"FACTION": allied_faction}, ident="LOCAL_REPS")
            self.subplots["LOCAL_REPS"].active = False
        else:
            my_involvement = ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"])


        mychallenge: Challenge = self.register_element(
            "_CHALLENGE", Challenge(
                "Investigate {}".format(self.elements["_ENEMY_FACTION"]), ghchallenges.MISSION_CHALLENGE,
                key=(self.elements["_ENEMY_FACTION"],),
                involvement=my_involvement,
                data={
                    "challenge_objectives": [
                        "investigate {_ENEMY_FACTION}'s activities near {METROSCENE}".format(**self.elements),
                        "find out what {_ENEMY_FACTION} is doing in {METROSCENE}".format(**self.elements),
                        "see what {_ENEMY_FACTION} has been doing here".format(**self.elements),
                        "intercept {_ENEMY_FACTION}'s forces and gather as much information as possible".format(
                            **self.elements),
                        "seek out {_ENEMY_FACTION} and figure out what they're doing".format(**self.elements),
                    ],
                    "challenge_summaries": [
                        "investigate {_ENEMY_FACTION}'s operations in {METROSCENE}".format(**self.elements),
                        "gather information on {_ENEMY_FACTION}".format(**self.elements),
                    ],
                    "challenge_rumors": [
                        "nobody knows what {_ENEMY_FACTION} has been doing in {METROSCENE}".format(**self.elements),
                        "someone needs to find out why {_ENEMY_FACTION} is suddenly active".format(**self.elements),
                    ],
                    "challenge_subject": [
                        "{_ENEMY_FACTION}'s activities".format(**self.elements),
                    ],
                    "mission_intros": [
                        "track down a lance belonging to {_ENEMY_FACTION} and see what they're up to".format(
                            **self.elements),
                        "we are gathering info on {_ENEMY_FACTION}".format(**self.elements),
                        "I need someone to find out why {_ENEMY_FACTION} has come to {METROSCENE}".format(
                            **self.elements),
                    ],
                    "mission_builder": self._build_mission,
                    "priority_mission": my_outcome.prioritize_lore
                },
                memo=ChallengeMemo(
                    "You are investigating {} activity near {}.".format(self.elements["_ENEMY_FACTION"],
                                                                        self.elements["METROSCENE"])
                ), memo_active=True, points_target=10, num_simultaneous_plots=1
            )
        )

        return True

    OBJECTIVES = (
        missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_DEFEAT_COMMANDER,
        missionbuilder.BAMO_EXTRACT_ALLIED_FORCES, missionbuilder.BAMO_RECOVER_CARGO
    )

    def _build_mission(self, camp, npc):
        # Find some text hints to build the mission grammar.
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        candidates = [str(self.elements["_ENEMY_FACTION"])]
        for known_lore in self.quest_record.quest.revealed_lore:
            if known_lore.outcome is my_outcome and quests.TEXT_LORE_TARGET_TOPIC in known_lore.texts:
                candidates.append(known_lore.texts[quests.TEXT_LORE_TARGET_TOPIC])

        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])
        return missionbuilder.BuildAMissionSeed(
            camp, "{}'s Mission".format(npc),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            allied_faction=self.elements.get("_ALLIED_FACTION"),
            enemy_faction=self.elements["_ENEMY_FACTION"], rank=self.rank,
            objectives=random.sample(self.OBJECTIVES, 2),
            scenegen=sgen, architecture=archi,
            cash_reward=100, on_win=self._win_the_mission,
            mission_grammar=missionbuilder.MissionGrammar(
                "learn more about {}".format(random.choice(candidates)),
                "ensure the success of {}".format(random.choice(candidates)),
                "I uncovered {}'s secrets".format(self.elements["_ENEMY_FACTION"]),
                "you learned too much about {}".format(self.elements["_ENEMY_FACTION"]),
                "I was defeated by {}".format(self.elements["_ENEMY_FACTION"]),
                "I defeated you in the name of {}".format(self.elements["_ENEMY_FACTION"]),
            )
        )

    def _win_the_mission(self, camp: gears.GearHeadCampaign):
        learning_is_half_the_battle = camp.make_skill_roll(gears.stats.Perception, gears.stats.Scouting,
                                                           untrained_ok=True)
        points = max((learning_is_half_the_battle - 30) // 20, 1)
        self.elements["_CHALLENGE"].advance(camp, points)

    def start_quest_task(self, camp):
        if "LOCAL_REPS" in self.subplots:
            self.subplots["LOCAL_REPS"].activate(camp)

    def end_quest_task(self, camp):
        if "LOCAL_REPS" in self.subplots:
            self.subplots["LOCAL_REPS"].deactivate(camp)

    def _CHALLENGE_WIN(self, camp):
        ghcutscene.alert_with_grammar(camp, "[DISCOVERY_AFTER_MECHA_COMBAT] {}".format(
            self.locked_lore.texts[quests.TEXT_LORE_SELFDISCOVERY]))
        self.quest_record.win_task(self, camp)


class ProtectedByArtillery(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_TASK
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        quest = pstate.elements.get(quests.QUEST_ELEMENT_ID)
        lores = pstate.elements.get(quests.LORE_SET_ELEMENT_ID)
        return cls.get_matching_lore(quest, lores)

    @staticmethod
    def get_matching_lore(quest: quests.Quest, lores):
        candidates = [l for l in lores if quest.lore_is_unlocked(l) and l.category == LORECAT_LOCATION and LORETAG_ENEMY in l.tags and LORETAG_PRIMARY in l.tags and LORETAG_PROTECTED not in l.tags]
        if candidates:
            return random.choice(candidates)

    def custom_init(self, nart):
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        self.elements["_ENEMY_FACTION"] = my_outcome.o_elements.get(OE_ENEMYFACTION)

        quest = self.elements.get(quests.QUEST_ELEMENT_ID)

        lores = self.elements.get(quests.LORE_SET_ELEMENT_ID)
        self.locked_lore = self.get_matching_lore(quest, lores)
        quest.lock_lore(self, self.locked_lore)

        primary_lore = quests.QuestLore(
            LORECAT_LOCATION, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]), outcome=my_outcome,
            tags=(LORETAG_ENEMY, LORETAG_PROTECTED, LORETAG_PRIMARY)
        )
        self.elements["_PRIMARY_NAME"] = primary_lore.texts.get(L_LOCATION_NAME, "Base")
        primary_lore.texts.update(self.locked_lore.texts)
        self.quest_record.add_needed_lore(quest, self, primary_lore)
        self.elements["_BASE_NAME"] = "Artillery"

        new_lore = quests.QuestLore(
            LORECAT_EMERGENCY, texts={
                quests.TEXT_LORE_HINT: "{_ENEMY_FACTION} has a secret weapon".format(**self.elements),
                quests.TEXT_LORE_INFO: "their {_PRIMARY_NAME} is protected by {_BASE_NAME}".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "{_ENEMY_FACTION}'s secret weapon".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "You have discovered that {_ENEMY_FACTION}'s {_PRIMARY_NAME} is protected by {_BASE_NAME}.".format(
                    **self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "{_ENEMY_FACTION}'s {_BASE_NAME}".format(**self.elements),
                quests.TEXT_LORE_MEMO: "{_ENEMY_FACTION}'s {_PRIMARY_NAME} is protected by {_BASE_NAME}.".format(
                    **self.elements),
            }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]), outcome=my_outcome,
            tags=(LORETAG_ENEMY, LORETAG_PROTECTED)
        )
        self.quest_record.add_needed_lore(quest, self, new_lore)

        self.mission_name = "Destroy {_ENEMY_FACTION}'s {_BASE_NAME}".format(**self.elements)
        self.memo = plots.Memo(
            "{_ENEMY_FACTION}'s {_PRIMARY_NAME} is protected by {_BASE_NAME}.".format(**self.elements),
            self.elements["METROSCENE"]
        )

        return True

    SECONDARY_OBJECTIVES = (
        missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_DEFEAT_COMMANDER,
        missionbuilder.BAMO_CAPTURE_BUILDINGS, missionbuilder.BAMO_NEUTRALIZE_ALL_DRONES
    )

    def _get_mission(self, camp):
        # Return a mission seed for the current state of this mission. The state may be altered by unfinished tasks-
        # For instance, if the fortress is defended by artillery, that gets added into the mission.
        objectives = [missionbuilder.BAMO_DESTROY_ARTILLERY,] + [random.choice(self.SECONDARY_OBJECTIVES),]
        rank = self.rank
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])

        el_seed = missionbuilder.BuildAMissionSeed(
                camp, self.mission_name,
                self.elements["METROSCENE"], self.elements["MISSION_GATE"],
                enemy_faction=self.elements["_ENEMY_FACTION"], rank=rank,
                objectives=objectives,
                one_chance=True,
                scenegen=sgen, architecture=archi,
                cash_reward=100, on_win=self._win_task,
                mission_grammar=missionbuilder.MissionGrammar(
                    "destroy your {_BASE_NAME}".format(**self.elements),
                    "defend our secret {_BASE_NAME}".format(**self.elements),
                    "I destroyed your {_BASE_NAME}".format(**self.elements),
                    "you destroyed our {_BASE_NAME}".format(**self.elements),
                    lose_ep="I defended our {_BASE_NAME} from you".format(**self.elements),
                )
            )

        return el_seed

    def _win_task(self, camp):
        pbge.BasicNotification("{}'s artillery has been destroyed.".format(self.elements["_ENEMY_FACTION"]),
                               count=150)
        self.quest_record.win_task(self, camp)

    def MISSION_GATE_menu(self, camp, thingmenu):
        thingmenu.add_item(self.mission_name, self._get_mission(camp))


class UnknownMechaNearTown(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_TASK
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        outc = pstate.elements.get(quests.OUTCOME_ELEMENT_ID)
        target = outc.o_elements.get(OE_ENEMYFACTION)
        quest = pstate.elements.get(quests.QUEST_ELEMENT_ID)
        lores = pstate.elements.get(quests.LORE_SET_ELEMENT_ID)
        return (
            OTAG_AGGRESSIVE in outc.verb.tags
            and gears.factions.is_a_faction(target) and cls.get_matching_lore(quest, lores) and
            "MISSION_GATE" in pstate.elements
        )

    @staticmethod
    def get_matching_lore(quest: quests.Quest, lores):
        candidates = [l for l in lores if quest.lore_is_unlocked(l) and l.category == LORECAT_MOTIVE and LORETAG_ENEMY in l.tags and LORETAG_HIDDEN in l.tags]
        if candidates:
            return random.choice(candidates)

    MISSION_NAMES = (
        "Locate Unknown Invaders", "Intercept Mystery Mecha", "Confront Hostile Mecha"
    )

    def custom_init(self, nart):
        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        self.elements["_ENEMY_FACTION"] = my_outcome.o_elements.get(OE_ENEMYFACTION)
        if nart.camp.are_faction_allies(self.elements["_ENEMY_FACTION"], self.elements["METROSCENE"]):
            return False

        quest = self.elements.get(quests.QUEST_ELEMENT_ID)

        lores = self.elements.get(quests.LORE_SET_ELEMENT_ID)
        self.locked_lore = self.get_matching_lore(quest, lores)
        quest.lock_lore(self, self.locked_lore)

        self.memo = plots.Memo(
            "Hostile mecha have been spotted near {METROSCENE}; you can attempt to intercept these unknown invaders.".format(**self.elements),
            self.elements["METROSCENE"]
        )

        base_lore = quests.QuestLore(
            LORECAT_EMERGENCY, texts={
                quests.TEXT_LORE_HINT: "hostile mecha have been sighted near {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_INFO: "someone needs to intercept these intruders and find out who they are".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "the hostile mecha".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "You have learned that hostile mecha have been sighted near {METROSCENE}.".format(**self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "the unknown hostile mecha".format(**self.elements),
                quests.TEXT_LORE_MEMO: "Unknown hostile mecha have been sighted near {METROSCENE}.".format(
                    **self.elements),
            }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]), outcome=my_outcome,
            tags=(
                LORETAG_ENEMY, LORETAG_HIDDEN
            ),
        )
        self.quest_record.add_needed_lore(quest, self, base_lore)
        self.mission_name = random.choice(self.MISSION_NAMES)
        self.mission_announcement_ready = True

        return True

    MISSION_CANDIDATES = (
        missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL,
        missionbuilder.BAMO_DEFEAT_COMMANDER, missionbuilder.BAMO_EXTRACT_ALLIED_FORCES,
        missionbuilder.BAMO_RECOVER_CARGO, missionbuilder.BAMO_SURVIVE_THE_AMBUSH
    )

    def _get_mission(self, camp):
        # Return a mission seed for the current state of this mission. The state may be altered by unfinished tasks-
        # For instance, if the fortress is defended by artillery, that gets added into the mission.
        objectives = random.sample(self.MISSION_CANDIDATES, 2)
        rank = self.rank

        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])

        el_seed = missionbuilder.BuildAMissionSeed(
                camp, self.mission_name,
                self.elements["METROSCENE"], self.elements["MISSION_GATE"],
                enemy_faction=self.elements["_ENEMY_FACTION"], rank=rank,
                objectives=objectives,
                one_chance=True,
                scenegen=sgen, architecture=archi, make_enemies=False,
                cash_reward=100, on_win=self._win_outcome, on_loss=self._lose_outcome
            )

        return el_seed

    def t_UPDATE(self, camp):
        super().t_UPDATE(camp)
        if self.mission_announcement_ready:
            missionbuilder.NewMissionNotification(self.mission_name, self.elements["MISSION_GATE"])
            self.mission_announcement_ready = False

    MISSION_END_TEXTS = (
        "It's clear that {_ENEMY_FACTION} are the hostile mecha you've been tracking.",
        "The identity of the unknown mecha is now obvious: {_ENEMY_FACTION}."
    )

    def _win_outcome(self, camp):
        ghcutscene.alert_with_grammar(camp, "[DISCOVERY_AFTER_MECHA_COMBAT] {}.".format(random.choice(self.MISSION_END_TEXTS).format(**self.elements)))
        self.quest_record.win_task(self, camp)

    def _lose_outcome(self, camp):
        self.quest_record.lose_task(self, camp)

    def MISSION_GATE_menu(self, camp, thingmenu):
        thingmenu.add_item(self.mission_name, self._get_mission(camp))


class WhoIsHiddenIdentity(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_TASK
    scope = "METRO"

    CLUES = (
        "{_ALIAS} is known to be [adjective]",
        "{_ALIAS} has a [noun]",
        "{_ALIAS} is a {_NPC.gender.noun}",
        "{_ALIAS} is a {_NPC.job}",
    )

    @classmethod
    def matches(cls, pstate):
        quest = pstate.elements.get(quests.QUEST_ELEMENT_ID)
        lores = pstate.elements.get(quests.LORE_SET_ELEMENT_ID)
        return cls.get_matching_lore(quest, lores)

    @staticmethod
    def get_matching_lore(quest: quests.Quest, lores):
        candidates = [l for l in lores if quest.lore_is_unlocked(l) and l.category == LORECAT_CHARACTER and LORETAG_HIDDEN not in l.tags]
        if candidates:
            return random.choice(candidates)

    def custom_init(self, nart):
        quest = self.elements.get(quests.QUEST_ELEMENT_ID)
        lores = self.elements.get(quests.LORE_SET_ELEMENT_ID)
        self.locked_lore = self.get_matching_lore(quest, lores)
        quest.lock_lore(self, self.locked_lore)

        my_outcome: quests.QuestOutcome = self.elements[quests.OUTCOME_ELEMENT_ID]
        if OTAG_AGGRESSIVE in my_outcome.verb.tags and gears.factions.is_a_faction(my_outcome.o_elements.get(OE_ENEMYFACTION)):
            enemy_faction = my_outcome.o_elements.get(OE_ENEMYFACTION)
        else:
            enemy_faction = None

        npc = self.register_element("_NPC", self.locked_lore.texts[L_CHARACTER_IDENTITY])
        alias = self.register_element("_ALIAS", self.locked_lore.texts[L_CHARACTER_ALIAS])

        if my_outcome.prioritize_lore:
            involvement = ghchallenges.InvolvedMetroResidentNPCs(self.elements["METROSCENE"], (npc,))
        else:
            involvement = self.locked_lore.is_involved

        clues = [a.format(**self.elements) for a in self.CLUES]
        for s in gears.stats.PRIMARY_STATS:
            if npc.get_stat(s) > 12:
                clues.append("{} has exceptional {}".format(alias, s))
            else:
                clues.append("{} has average {}".format(alias, s))
        for v in gears.personality.VIRTUES:
            if v in npc.personality:
                clues.append("{} values {}".format(alias, v))
        random.shuffle(clues)

        mychallenge: Challenge = self.register_element(
            "_CHALLENGE", Challenge(
                "Investigate {}".format(npc),
                ghchallenges.GATHER_INTEL_CHALLENGE,
                key=(self.elements["_ALIAS"],), involvement=involvement,
                data={
                    "clues": clues,
                    "conclusion_told": self.locked_lore.texts[quests.TEXT_LORE_INFO],
                    "conclusion_discovered": self.locked_lore.texts[quests.TEXT_LORE_SELFDISCOVERY],
                    "enemy_faction": enemy_faction
                },
                memo=ChallengeMemo(
                    "You are trying to discover the identity of {_ALIAS}.".format(**self.elements)
                ), memo_active=True, points_target=min(3 + self.rank//25, 7), num_simultaneous_plots=1
            )
        )

        task_lore = quests.QuestLore(
            LORECAT_KNOWLEDGE, texts={
                quests.TEXT_LORE_HINT: "{_ALIAS} is very mysterious".format(**self.elements),
                quests.TEXT_LORE_INFO: "nobody knows who {_ALIAS} is".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "{_ALIAS}".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "You realize that you have have no idea who {_ALIAS} is.".format(**self.elements),
                quests.TEXT_LORE_TARGET_TOPIC: "{_ALIAS}".format(**self.elements),
            }, involvement=ghchallenges.InvolvedMetroNoFriendToFactionNPCs(self.elements["METROSCENE"], self.elements["_ENEMY_FACTION"]), outcome=my_outcome
        )
        self.quest_record.add_needed_lore(quest, self, task_lore)
        print("Plot loaded")

        return True

    def _CHALLENGE_WIN(self, camp):
        self.quest_record.win_task(self, camp)




#  ********************************
#  ***   QUEST  LORE  HANDLER   ***
#  ********************************
#
# A Quest Intro introduces a quest task. Typically only the first task in line needs an intro; subsequent tasks will
# be introduced by the task progression itself.
#

class GearHeadLoreHandler(plots.Plot):
    # Simple for now, expand later.
    LABEL = quests.DEFAULT_QUEST_LORE_HANDLER
    scope = "METRO"
    active = True

    def custom_init(self, nart):
        return True

    def t_UPDATE(self, camp):
        if not self.elements[quests.LORE_SET_ELEMENT_ID]:
            self.end_plot(camp)

    def _can_reveal_lore(self, camp: gears.GearHeadCampaign, lore: quests.QuestLore, npc: gears.base.Character):
        # The Outcome lore for a quest line won't be revealed to the PC if the Outcome itself can't be pursued by the
        # PC, as disctated by the player_can_fun function in the outcome.
        if lore.outcome and lore.outcome.player_can_fun:
            if not lore.outcome.player_can_fun(camp, lore.outcome):
                return False
        return lore.is_involved(camp, npc)

    def _get_dialogue_grammar(self, npc, camp):
        # The secret private function that returns custom grammar.
        mygram = collections.defaultdict(list)
        for lore in self.elements[quests.LORE_SET_ELEMENT_ID]:
            if lore.is_involved(camp, npc):
                mygram["[News]"].append(lore.texts[quests.TEXT_LORE_HINT])
                if lore.priority:
                    mygram["[CURRENT_EVENTS]"].append("[chat_lead_in] {}!".format(lore.texts[quests.TEXT_LORE_HINT]))
        return mygram

    DOUBLE_LORE_PATTERNS = (
        "[LISTEN_TO_MY_INFO] {}; {}.",
        "{}... {}.", "[LISTEN_UP] {}. {}.",
        "{}; [as_far_as_I_know] {}."
    )

    SINGLE_LORE_PATTERNS = (
        "[LISTEN_TO_MY_INFO] {}.",
        "{}.", "[THIS_IS_A_SECRET] {}.",
        "[as_far_as_I_know] {}."
    )

    def _create_lore_revealer(self, npc, camp, lore):
        extra_lore_candidates = [l2 for l2 in self.elements[quests.LORE_SET_ELEMENT_ID] if l2 is not lore and l2.outcome
                                 and l2.outcome is lore.outcome]
        if extra_lore_candidates:
            lore2 = random.choice(extra_lore_candidates)
            msg = random.choice(self.DOUBLE_LORE_PATTERNS).format(lore.texts[quests.TEXT_LORE_INFO],
                                                                  lore2.texts[quests.TEXT_LORE_INFO])
            lorelist = (lore, lore2)
        else:
            msg = random.choice(self.SINGLE_LORE_PATTERNS).format(lore.texts[quests.TEXT_LORE_INFO])
            lorelist = (lore,)

        return Offer(
            msg, context=ContextTag([context.INFO,]),
            effect=quests.LoreRevealer(
                lorelist, self.elements[quests.QUEST_ELEMENT_ID], self.elements[quests.LORE_SET_ELEMENT_ID]
            ), subject=lore.texts[quests.TEXT_LORE_HINT], no_repeats=True,
            data={"subject": lore.texts[quests.TEXT_LORE_TOPIC]}
        )

    def _get_generic_offers(self, npc, camp: gears.GearHeadCampaign):
        """Get any offers that could apply to non-element NPCs."""
        myoffs = list()
        if camp.is_not_lancemate(npc):
            for lore in self.elements[quests.LORE_SET_ELEMENT_ID]:
                if self._can_reveal_lore(camp, lore, npc):
                    myoffs.append(self._create_lore_revealer(npc, camp, lore))
                    if lore.is_involved(camp, npc) and (lore.priority or (lore.outcome and lore.outcome.prioritize_lore)):
                        myoffs.append(Offer(
                            "[HELLO] [chat_lead_in] {}.".format(lore.texts[quests.TEXT_LORE_HINT]),
                            ContextTag([context.HELLO,]),
                        ))

        return myoffs


