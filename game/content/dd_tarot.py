import mechtarot
from mechtarot import TarotCard,Interaction,TagChecker,NameChecker
import pbge


MT_PERSON = "PERSON"
MT_THREAT = "THREAT"

class Convict(TarotCard):
    # This person has been arrested.
    TAGS = (MT_PERSON,)


class Demagogue(TarotCard):
    # Threat card. -Politics.
    # Effects on Game World:
    # - Villagers who match "type" will epouse Demagogue's views, -25 reaction to PC
    # Interactions:
    #
    TAGS = (MT_PERSON,MT_THREAT)
    NEGATIONS = (Convict,)
    def t_START(self,camp):
        pbge.alert("Demagogue is here")


class Warrant(TarotCard):
    INTERACTIONS = (Interaction(TagChecker([MT_PERSON]),action_triggers=[],effect_plot='',results=(None,"Convict",None)),
                    )


class TheLaw(TarotCard):
    INTERACTIONS = (Interaction(NameChecker(["Evidence"]),action_triggers=[],effect_plot='',results=(None,None,"Warrant")),
                    )


class Evidence(TarotCard):
    pass


class Clue(TarotCard):
    INTERACTIONS = (Interaction(NameChecker(["Crime"]),action_triggers=[],effect_plot='',results=("Evidence",None,None)),
                    )


class Crime(TarotCard):
    pass

