import pbge
from pbge import quests, plots, challenges
from game.content import ghchallenges


VERB_EXPEL = "EXPEL"        # Like DEFEAT, but the enemy is an outside power of some type
VERB_REPRESS = "REPRESS"    # Like DEFEAT, but the enemy has to be located first

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
        self.register_element("CHALLENGE", challenges.Challenge(
            "Locate {}'s {}".format(my_outcome.target, base_name), ghchallenges.LOCATE_ENEMY_BASE_CHALLENGE,
            key=(my_outcome.target,), involvement=my_outcome.participants,
            data={"base_name": base_name}

        ))
        return True

