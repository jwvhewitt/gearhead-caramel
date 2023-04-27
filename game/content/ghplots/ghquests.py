import collections

import pbge
import gears
import copy
import random
from pbge import quests, plots, challenges
from pbge.plots import Rumor
from game.content import ghchallenges, plotutility, gharchitecture
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from pbge.challenges import Challenge, AutoOffer, ChallengeMemo
from . import missionbuilder

VERB_EXPEL = "EXPEL"  # Like DEFEAT, but the enemy is an outside power of some type
VERB_REPRESS = "REPRESS"  # Like DEFEAT, but the enemy has to be located first

LORECAT_OUTCOME = "OUTCOME"

LORECAT_LOCATION = "LOCATION"


AGGRESSIVE_VERBS = (
    quests.VERB_DEFEAT, VERB_EXPEL, VERB_REPRESS
)

QE_LORE_TO_LOCK = "QE_LORE_TO_LOCK"

QUEST_TASK_FINDENEMYBASE = "QUEST_TASK_FINDENEMYBASE"
# If given a lore to lock, that lore should be the existence of the base.
# This task will lock that lore and reveal it when activated.
QE_BASE_NAME = "QE_BASE_NAME"



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

# Given a quest, construct a series of obstacles leading to the conclusion. The obstacles may be parallel or
# serial. They may be blocking, preventing the next challenge from activating until they are complete, or they
# may be optional, allowing the player to attempt the next challenge with a penalty. It is the responsibility of the
# parent plot to check penalties from incomplete/lost challenges!

#  ******************************
#  ***   QUEST  CONCLUSIONS   ***
#  ******************************


class StrikeTheLeader(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_CONCLUSION
    scope = "METRO"

    QUEST_DATA = quests.QuestData(
        (),
    )

    @classmethod
    def matches(cls, pstate):
        outc = pstate.elements.get(quests.DEFAULT_OUTCOME_ELEMENT_ID)
        return outc and outc.verb in (quests.VERB_DEFEAT, VERB_REPRESS)


class TheyHaveAFortress(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_CONCLUSION
    scope = "METRO"

    QUEST_DATA = quests.QuestData(
        (QUEST_TASK_FINDENEMYBASE,),
    )

    @classmethod
    def matches(cls, pstate):
        outc = pstate.elements.get(quests.DEFAULT_OUTCOME_ELEMENT_ID)
        return outc and outc.verb in (quests.VERB_DEFEAT, VERB_EXPEL)

    def custom_init(self, nart):
        self.elements[QE_BASE_NAME] = "Fortress"
        my_outcome: quests.QuestOutcome = self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID]
        self.elements["_ENEMY_FACTION"] = my_outcome.target
        self.mission_name = "Attack {_ENEMY_FACTION}'s {QE_BASE_NAME}".format(**self.elements)
        self.memo = plots.Memo(
            "You know the location of {_ENEMY_FACTION}'s {QE_BASE_NAME} and can attack at any time.".format(**self.elements),
            self.elements["METROSCENE"]
        )

        base_lore = quests.QuestLore(
            LORECAT_LOCATION, texts={
                quests.TEXT_LORE_HINT: "{_ENEMY_FACTION} has been working on a large project near {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_INFO: "they've built a {QE_BASE_NAME}".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "{_ENEMY_FACTION}'s project".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "You have learned about {_ENEMY_FACTION}'s {QE_BASE_NAME}.".format(**self.elements)
            }, involvement=my_outcome.involvement, outcome=my_outcome
        )
        self.quest_record.needed_lore.add(base_lore)
        self.elements[QE_LORE_TO_LOCK] = base_lore
        return True

    def _get_mission(self, camp):
        # Return a mission seed for the current state of this mission. The state may be altered by unfinished tasks-
        # For instance, if the fortress is defended by artillery, that gets added into the mission.
        objectives = [missionbuilder.BAMO_STORM_THE_CASTLE,]
        rank = self.rank
        sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])

        el_seed = missionbuilder.BuildAMissionSeed(
                camp, self.mission_name,
                self.elements["METROSCENE"], self.elements["MISSION_GATE"],
                enemy_faction=self.elements["_ENEMY_FACTION"], rank=rank,
                objectives=objectives,
                one_chance=True,
                scenegen=sgen, architecture=archi,
                cash_reward=100
            )

        return el_seed

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

class FindEnemyBaseTask(quests.QuestPlot):
    # Recommended Elements:
    #    QE_BASE_NAME
    LABEL = QUEST_TASK_FINDENEMYBASE
    scope = "METRO"

    # Required/Suggested Elements:
    #   QE_BASE_NAME

    QUEST_DATA = quests.QuestData(
        (), blocks_progress=True,
    )

    def custom_init(self, nart):
        my_outcome: quests.QuestOutcome = self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID]
        self.elements["_ENEMY_FACTION"] = my_outcome.target
        base_name = self.elements.get(QE_BASE_NAME, "Base")
        mychallenge: Challenge = self.register_element(
            "_CHALLENGE", Challenge(
                "Locate {}'s {}".format(my_outcome.target, base_name), ghchallenges.LOCATE_ENEMY_BASE_CHALLENGE,
                key=(my_outcome.target,), involvement=my_outcome.involvement,
                data={"base_name": base_name},
                oppoffers=(
                    AutoOffer(
                        dict(
                            msg="[OF_COURSE] I'll send the coordinates to your phone.".format(**self.elements),
                            context=ContextTag([context.CUSTOM, ]),
                            data={
                                "reply": "Can you tell me how to get to {}'s {}? [PRETEXT_FOR_GOING_THERE]".format(
                                    my_outcome.target, base_name)
                            }, dead_end=True, effect=self._advance_fully
                        ), active=True, uses=99,
                        access_fun=ghchallenges.AccessSkillRoll(
                            gears.stats.Charm, gears.stats.Stealth, self.rank, difficulty=gears.stats.DIFFICULTY_EASY
                        ),
                        involvement=ghchallenges.InvolvedMetroFactionNPCs(
                            self.elements["METROSCENE"], my_outcome.target
                        )
                    ),
                    AutoOffer(
                        dict(
                            msg="[OF_COURSE] I'll send the coordinates to your phone.".format(**self.elements),
                            context=ContextTag([context.UNFAVORABLE_CUSTOM, ]),
                            data={
                                "reply": "Can you tell me how to get to {}'s {}? [PRETEXT_FOR_GOING_THERE]".format(
                                    my_outcome.target, base_name)
                            }, dead_end=True, effect=self._advance_fully
                        ), active=True, uses=99,
                        access_fun=ghchallenges.AccessSkillRoll(
                            gears.stats.Charm, gears.stats.Stealth, self.rank, difficulty=gears.stats.DIFFICULTY_HARD
                        ),
                        involvement=ghchallenges.InvolvedMetroFactionNPCs(
                            self.elements["METROSCENE"], my_outcome.target
                        )
                    ),
                ), memo=ChallengeMemo(
                    "{} have a hidden {} near {}.".format(my_outcome.target, base_name, self.elements["METROSCENE"])
                ), memo_active=True
            )
        )

        base_lore = quests.QuestLore(
            LORECAT_LOCATION, texts={
                quests.TEXT_LORE_HINT: "{_ENEMY_FACTION} has been working on a large project near {METROSCENE}".format(**self.elements),
                quests.TEXT_LORE_INFO: "{_ENEMY_FACTION} has constructed a secret {QE_BASE_NAME} in this area".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "{_ENEMY_FACTION}'s presence here".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "{_ENEMY_FACTION} must have a {QE_BASE_NAME} nearby, but where?".format(**self.elements)
            }, involvement=my_outcome.involvement, outcome=my_outcome
        )
        self.quest_record.needed_lore.add(base_lore)
        if QE_LORE_TO_LOCK in self.elements:
            self.quest_record.quest.lock_lore(self, self.elements[QE_LORE_TO_LOCK])

        return True

    def start_quest_task(self, camp):
        if QE_LORE_TO_LOCK in self.elements:
            self.quest_record.quest.reveal_lore(camp, self.elements[QE_LORE_TO_LOCK])

    def _advance_challenge(self, camp):
        self.elements["CHALLENGE"].advance(camp, 2)

    def _advance_fully(self, camp):
        self.elements["CHALLENGE"].advance(camp, 100)

    def _CHALLENGE_WIN(self, camp):
        my_outcome: quests.QuestOutcome = self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID]
        base_name = self.elements.get(QE_BASE_NAME, "Base")
        pbge.BasicNotification("You have discovered the location of {}'s {}.".format(my_outcome.target, base_name),
                               count=150)
        self.quest_record.win_task(self, camp)


class BaseKnownByCollaborator(quests.QuestPlot):
    # Recommended Elements:
    #    QE_BASE_NAME
    LABEL = QUEST_TASK_FINDENEMYBASE
    scope = "METRO"

    QUEST_DATA = quests.QuestData(
        (), blocks_progress=True,
    )

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
        my_outcome: quests.QuestOutcome = self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID]
        base_name = self.elements.get(QE_BASE_NAME, "Base")
        self.elements["_ENEMY_FACTION"] = my_outcome.target

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
                    wcd[k] = v.format(my_outcome.target)
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
            "{}'s Collaborator".format(my_outcome.target),
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
            memo=pbge.challenges.MysteryMemo("Someone in {} is collaborating with {}.".format(self.elements["METROSCENE"], my_outcome.target)),
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
                quests.TEXT_LORE_INFO: "only the collaborator knows the location of {_ENEMY_FACTION}'s {QE_BASE_NAME}".format(**self.elements),
                quests.TEXT_LORE_TOPIC: "the collaborator".format(**self.elements),
                quests.TEXT_LORE_SELFDISCOVERY: "{_ENEMY_FACTION} must have a {QE_BASE_NAME} nearby, but where?".format(**self.elements)
            }, involvement=my_outcome.involvement, outcome=my_outcome
        )
        self.quest_record.needed_lore.add(base_lore)
        if QE_LORE_TO_LOCK in self.elements:
            self.quest_record.quest.lock_lore(self, self.elements[QE_LORE_TO_LOCK])

        return True

    def _is_good_npc(self, nart, candidate):
        if isinstance(candidate, gears.base.Character) and nart.camp.is_not_lancemate(candidate):
            faction_ok = candidate.faction and not nart.camp.are_faction_allies(candidate, self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID].target)
            scene_ok = candidate.scene and gears.tags.SCENE_PUBLIC in candidate.scene.attributes
            return faction_ok and scene_ok and candidate not in self.suspects

    def start_quest_task(self, camp):
        self.elements["_CHALLENGE"].activate(camp)
        if QE_LORE_TO_LOCK in self.elements:
            self.quest_record.quest.reveal_lore(camp, self.elements[QE_LORE_TO_LOCK])

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
        my_outcome: quests.QuestOutcome = self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID]
        base_name = self.elements.get(QE_BASE_NAME, "Base")
        pbge.BasicNotification(
            "You have learned that {} knows where {}'s {} is.".format(my_npc, my_outcome.target, base_name),
            count=150
        )
        self.memo = plots.Memo(
            "You have learned that {} knows where {}'s {} is.".format(my_npc, my_outcome.target, base_name),
            location=my_npc.scene
        )

    def win_da_task(self, camp):
        my_outcome: quests.QuestOutcome = self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID]
        base_name = self.elements.get(QE_BASE_NAME, "Base")
        pbge.BasicNotification("You have discovered the location of {}'s {}.".format(my_outcome.target, base_name),
                               count=150)
        self.quest_record.win_task(self, camp)

    def CULPRIT_offers(self, camp):
        mylist = list()
        if self.mystery_solved:
            my_outcome: quests.QuestOutcome = self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID]
            base_name = "{}'s {}".format(my_outcome.target, self.elements[QE_BASE_NAME])

            mylist.append(Offer(
                "[LETS_KEEP_THIS_A_SECRET] I will tell you the location of {}!".format(base_name),
                ContextTag([context.CUSTOM,]), effect=self.win_da_task,
                data={"reply": "I know that you've been collaborating with {}.".format(my_outcome.target)}
            ))

        return mylist

    def CULPRIT_SCENE_ENTER(self, camp):
        if self.mystery_solved:
            my_npc: gears.base.Character = self.elements["CULPRIT"]
            my_outcome: quests.QuestOutcome = self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID]
            base_name = "{}'s {}".format(my_outcome.target, self.elements[QE_BASE_NAME])
            if self.vigilante_action or my_npc.is_destroyed():
                pbge.alert("As you enter {CULPRIT_SCENE}, you notice the conspicuous absense of {CULPRIT}.".format(**self.elements))
                pbge.alert("A dataslate has been left behind with a set of map coordinates. Could this be the location of {}?".format(base_name))
                self.win_da_task(camp)

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        culprit = self.elements["CULPRIT"]
        my_outcome: quests.QuestOutcome = self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID]

        if not self.vigilante_action:
            if self.mystery_solved and my_outcome.is_involved(camp, npc) and npc is not culprit:
                goffs.append(Offer(
                    "[THATS_INTERESTING] [THIS_WILL_BE_DEALT_WITH]",
                    ContextTag([context.CUSTOM,]), effect=self._do_vigilante_action,
                    data={"reply": "I have proof that {} has been collaborating with {}.".format(culprit,
                                                                                                 my_outcome.target)}
                ))

        return goffs

    def _do_vigilante_action(self, camp: gears.GearHeadCampaign):
        self.vigilante_action = True
        npc: gears.base.Character = self.elements["CULPRIT"]
        my_outcome: quests.QuestOutcome = self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID]
        camp.freeze(npc)
        myfac = camp.get_faction(my_outcome.target)
        if npc.combatant and myfac and myfac.get_faction_tag():
            npc.relationship = camp.get_relationship(npc)
            npc.relationship.role = gears.relationships.R_ADVERSARY
            npc.relationship.history.append(
                gears.relationships.Memory(
                    "you revealed that I was working for {}".format(my_outcome.target),
                    "I discovered you were working for {}".format(my_outcome.target),
                    -5, memtags=(gears.relationships.MEM_Clash, gears.relationships.MEM_Ideological)
                )
            )
            npc.faction = myfac.get_faction_tag()
            camp.egg.dramatis_personae.add(npc)


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
        # The Outcome lore for a quest line won't be revealed to the PC if it's an aggressive verb and the PC is allied
        # with the target. But what if you want to offer the PC the choice to betray their current faction? Then don't
        # give this lore the LORECAT_OUTCOME category, and all will be well.
        if lore.category == LORECAT_OUTCOME and lore.outcome and lore.outcome.target and lore.outcome.verb in AGGRESSIVE_VERBS and camp.is_favorable_to_pc(lore.outcome.target):
            return False
        return lore.is_involved(camp, npc)

    def _get_dialogue_grammar(self, npc, camp):
        # The secret private function that returns custom grammar.
        mygram = collections.defaultdict(list)
        for lore in self.elements[quests.LORE_SET_ELEMENT_ID]:
            if lore.is_involved(camp, npc):
                mygram["[News]"].append(lore.texts[quests.TEXT_LORE_HINT])
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

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        myoffs = list()
        for lore in self.elements[quests.LORE_SET_ELEMENT_ID]:
            if self._can_reveal_lore(camp, lore, npc):
                myoffs.append(self._create_lore_revealer(npc, camp, lore))
        return myoffs


