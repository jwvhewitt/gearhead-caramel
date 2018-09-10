import mechtarot
from mechtarot import TarotCard,Interaction,TagChecker,NameChecker
import pbge


MT_PERSON = "PERSON"
MT_THREAT = "THREAT"
MT_HEROIC = "HEROIC"

ME_PERSON = "PERSON"


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
    def custom_init( self, nart ):
        if ME_PERSON not in self.elements:
            self.register_element(ME_PERSON,"The Bad Guy")
        return True
    def t_START(self,camp):
        pbge.alert("Demagogue is here")


class Warrant(TarotCard):
    INTERACTIONS = (Interaction(TagChecker([MT_PERSON],[ME_PERSON]),action_triggers=[],effect_plot='',results=(None,"Convict",None),passparams=(None,((ME_PERSON,),None),None)),
                    )
    def t_START(self,camp):
        pbge.alert("Warrant Person: {}".format(self.elements.get(ME_PERSON)))


class TheLaw(TarotCard):
    INTERACTIONS = (Interaction(NameChecker(["Evidence"]),action_triggers=[],effect_plot='',results=(None,None,"Warrant"),passparams=(None,None,(None,(ME_PERSON,)))),
                    )
    def t_START(self,camp):
        pbge.alert("The Law Person: {}".format(self.elements.get(ME_PERSON)))


class LocalHero(TarotCard):
    TAGS = (MT_PERSON,MT_HEROIC)
    def custom_init( self, nart ):
        if ME_PERSON not in self.elements:
            self.register_element(ME_PERSON,"Deadzone Drifter")
        return True

    def t_START(self,camp):
        pbge.alert("Local Hero Person: {}".format(self.elements.get(ME_PERSON)))

class TheBadge(TarotCard):
    INTERACTIONS = (Interaction(TagChecker([MT_PERSON,MT_HEROIC]),action_triggers=[],effect_plot='',results=(None,"TheLaw",None),passparams=(None,(None,(ME_PERSON,)),None)),
                    )
    def t_START(self,camp):
        pbge.alert("The Badge Person: {}".format(self.elements.get(ME_PERSON)))


class Evidence(TarotCard):
    # If first card, place the evidence right in a crime scene that the PC can discover-
    # correspondence in a bandit base, a personal effect at a murder scene, etc.
    pass


class Clue(TarotCard):
    INTERACTIONS = (Interaction(NameChecker(["Crime"]),action_triggers=[],effect_plot='',results=("Evidence",None,None),passparams=(((ME_PERSON,),None),None,None)),
                    )
    def t_START(self,camp):
        pbge.alert("Clue Person: {}".format(self.elements.get(ME_PERSON)))


class Crime(TarotCard):
    def t_START(self,camp):
        pbge.alert("Crime Person: {}".format(self.elements.get(ME_PERSON)))

