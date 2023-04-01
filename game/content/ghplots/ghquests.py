import pbge
import gears
from pbge import quests, plots, challenges
from pbge.plots import Rumor
from game.content import ghchallenges, plotutility
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from pbge.challenges import Challenge, AutoOffer, ChallengeMemo

VERB_EXPEL = "EXPEL"  # Like DEFEAT, but the enemy is an outside power of some type
VERB_REPRESS = "REPRESS"  # Like DEFEAT, but the enemy has to be located first

AGGRESSIVE_VERBS = (
    quests.VERB_DEFEAT, VERB_EXPEL, VERB_REPRESS
)

QE_BASE_NAME = "QE_BASE_NAME"


# Given a quest, construct a series of obstacles leading to the conclusion. The obstacles may be parallel or
# serial. They may be blocking, preventing the next challenge from activating until they are complete, or they
# may be optional, allowing the player to attempt the next challenge with a penalty.

#  ******************************
#  ***   QUEST  CONCLUSIONS   ***
#  ******************************


class StrikeTheLeader(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_CONCLUSION
    scope = "METRO"

    QUEST_DATA = quests.QuestData(
        ()
    )

    @classmethod
    def matches(cls, pstate):
        outc = pstate.elements.get(quests.DEFAULT_OUTCOME_ELEMENT_ID)
        return outc and outc.verb in (quests.VERB_DEFEAT, VERB_REPRESS)


class TheyHaveAFortress(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_CONCLUSION
    scope = "METRO"

    QUEST_DATA = quests.QuestData(
        ("QUEST_TASK_FINDENEMYBASE",)
    )

    @classmethod
    def matches(cls, pstate):
        outc = pstate.elements.get(quests.DEFAULT_OUTCOME_ELEMENT_ID)
        return outc and outc.verb in (quests.VERB_DEFEAT, VERB_EXPEL)

    def custom_init(self, nart):
        self.elements[QE_BASE_NAME] = "Fortress"
        return True


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
    LABEL = "QUEST_TASK_FINDENEMYBASE"
    scope = "METRO"

    # Required/Suggested Elements:
    #   QE_BASE_NAME

    QUEST_DATA = quests.QuestData(
        (), blocks_progress=True
    )

    def custom_init(self, nart):
        my_outcome: quests.QuestOutcome = self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID]
        base_name = self.elements.get(QE_BASE_NAME, "Base")
        mychallenge: Challenge = self.register_element(
            "CHALLENGE", Challenge(
                "Locate {}'s {}".format(my_outcome.target, base_name), ghchallenges.LOCATE_ENEMY_BASE_CHALLENGE,
                key=(my_outcome.target,), involvement=my_outcome.participants,
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
                            gears.stats.Charm, gears.stats.Stealth, self.rank, difficulty=gears.stats.DIFFICULTY_HARD
                        ),
                        involvement=ghchallenges.InvolvedMetroFactionNPCs(
                            self.elements["METROSCENE"], my_outcome.target
                        )
                    )
                ), memo_active=True
            )
        )
        mychallenge.memo = ChallengeMemo(
            "{} have a hidden {} near {}.".format(my_outcome.target, base_name, self.elements["METROSCENE"]),
            mychallenge)

        return True

    def _advance_challenge(self, camp):
        self.elements["CHALLENGE"].advance(camp, 2)

    def _advance_fully(self, camp):
        self.elements["CHALLENGE"].advance(camp, 100)

    def CHALLENGE_WIN(self, camp):
        my_outcome: quests.QuestOutcome = self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID]
        base_name = self.elements.get(QE_BASE_NAME, "Base")
        pbge.BasicNotification("You have discovered the location of {}'s {}.".format(my_outcome.target, base_name),
                               count=150)
        self.quest_record.win_task(self, camp)


#  *************************
#  ***   QUEST  INTROS   ***
#  *************************
#
# A Quest Intro introduces a quest task. Typically only the first task in line needs an intro; subsequent tasks will
# be introduced by the task progression itself.
#

class IntroDaWar(quests.QuestIntroPlot):
    scope = "METRO"

    @classmethod
    def matches(cls, pstate):
        outc = pstate.elements.get(quests.DEFAULT_OUTCOME_ELEMENT_ID)
        return outc and outc.verb in AGGRESSIVE_VERBS

    def custom_init(self, nart):
        my_outcome: quests.QuestOutcome = self.elements[quests.DEFAULT_OUTCOME_ELEMENT_ID]
        self.elements["ENEMY_FACTION"] = my_outcome.target
        self.RUMOR = Rumor(
            "",
            offer_msg="",
            offer_subject="", offer_subject_data="",
            memo="", offer_effect_name="rumor_offer_effect",
            npc_is_prohibited_fun=plotutility.ProhibitFactionAndPCIfAllied("ENEMY_FACTION")
        )
        return True

    def rumor_offer_effect(self, camp):
        self.quest_record.win_task(self, camp)
