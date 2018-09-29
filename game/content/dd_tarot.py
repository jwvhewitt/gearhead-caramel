import mechtarot
from mechtarot import TarotCard,Interaction,TagChecker,NameChecker
import pbge
import gears


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
            npc = gears.selector.random_pilot(50)
            self.register_element(ME_PERSON,npc,dident="TOWN")
        return True
    def PERSON_offers(self,camp):
        # Return list of dialogue offers.
        mylist = list()


        return mylist




class Warrant(TarotCard):
    INTERACTIONS = (Interaction(TagChecker([MT_PERSON],[ME_PERSON]),action_triggers=[],effect_plot='',results=(None,"Convict",None),passparams=(None,((ME_PERSON,),None),None)),
                    )



class TheLaw(TarotCard):
    INTERACTIONS = (Interaction(NameChecker(["Evidence"]),action_triggers=[],effect_plot='',results=(None,None,"Warrant"),passparams=(None,None,(None,(ME_PERSON,)))),
                    )



class LocalHero(TarotCard):
    TAGS = (MT_PERSON,MT_HEROIC)
    def custom_init( self, nart ):
        if ME_PERSON not in self.elements:
            self.register_element(ME_PERSON,"Deadzone Drifter")
        return True

class TheBadge(TarotCard):
    INTERACTIONS = (Interaction(TagChecker([MT_PERSON,MT_HEROIC]),action_triggers=[],effect_plot='',results=(None,"TheLaw",None),passparams=(None,(None,(ME_PERSON,)),None)),
                    )

class Evidence(TarotCard):
    # If first card, place the evidence right in a crime scene that the PC can discover-
    # correspondence in a bandit base, a personal effect at a murder scene, etc.
    pass


class Clue(TarotCard):
    INTERACTIONS = (Interaction(NameChecker(["Crime"]),action_triggers=[],effect_plot='',results=("Evidence",None,None),passparams=(((ME_PERSON,),None),None,None)),
                    )

class Crime(TarotCard):
    pass

