from pbge import quests, plots


VERB_EXPEL = "EXPEL"        # Like DEFEAT, but the enemy is an outside power of some type
VERB_REPRESS = "REPRESS"    # Like DEFEAT, but the enemy has to be located first


# Given a quest, construct a series of obstacles leading to the conclusion. The obstacles may be parallel or
# serial. They may be blocking, preventing the next challenge from activating until they are complete, or they
# may be optional, allowing the player to attempt the next challenge with a penalty.

#  ******************************
#  ***   QUEST  CONCLUSIONS   ***
#  ******************************


class StrikeTheLeader(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_CONCLUSION
    scope = "METRO"
    active = True

    QUEST_DATA = quests.QuestData(
        ("",)
    )

    @classmethod
    def matches(cls, pstate):
        return True


class TheHiddenFortress(quests.QuestPlot):
    LABEL = quests.DEFAULT_QUEST_CONCLUSION
    scope = "METRO"
    active = True

    QUEST_DATA = quests.QuestData(
        ("",)
    )

