import mechtarot
from mechtarot import TarotCard,Interaction,TagChecker,NameChecker
import pbge
import gears
from ..ghdialogue import context
from pbge.dialogue import Offer

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
    INTERACTIONS = (Interaction(TagChecker([MT_PERSON],[ME_PERSON]),action_triggers=[mechtarot.BetaCardDialogueTrigger(ME_PERSON,"You win!",[context.ARREST,])],results=(None,"Convict",None),passparams=(None,((ME_PERSON,),None),None)),
                    )



class TheLaw(TarotCard):
    def _fun(self,alpha,beta,camp):
        pass
    INTERACTIONS = (Interaction(NameChecker(["Evidence"]),action_triggers=[],effect_fun=_fun,results=(None,None,"Warrant"),passparams=(None,None,(None,(ME_PERSON,)))),
                    )
    def custom_init( self, nart ):
        if ME_PERSON not in self.elements:
            npc = gears.selector.random_pilot(50)
            npc.name = "The Law"
            self.register_element(ME_PERSON,npc,dident="TOWN")
        return True
    def PERSON_offers(self,camp):
        # Return list of dialogue offers.
        mylist = list()
        if not self.visible:
            mylist.append(Offer("I am the law.",context=(context.HELLO,),))
        return mylist



class LocalHero(TarotCard):
    TAGS = (MT_PERSON,MT_HEROIC)
    def custom_init( self, nart ):
        if ME_PERSON not in self.elements:
            npc = gears.selector.random_pilot(50)
            npc.name = "Local Hero"
            self.register_element(ME_PERSON,npc,dident="TOWN")
        return True
    def PERSON_offers(self,camp):
        # Return list of dialogue offers.
        mylist = list()
        if not self.visible:
            mylist.append(Offer("I am the local hero.",context=(context.HELLO,),effect=self._reveal,data={"subject":"crime"}))
        return mylist
    def _reveal(self,camp):
        self.visible = True

class TheBadge(TarotCard):
    INTERACTIONS = (Interaction(TagChecker([MT_PERSON,MT_HEROIC]),action_triggers=[mechtarot.BetaCardDialogueTrigger(ME_PERSON,"You win!",[context.INFO,],data={"subject":"the badge"})],results=(None,"TheLaw",None),passparams=(None,(None,(ME_PERSON,)),None)),
                    )
    def _get_generic_offers( self, npc, camp ):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if camp.scene.civilian_team and camp.scene.local_teams.get(npc) is camp.scene.civilian_team and not self.visible:
            # Any villager can tell you about the need for a lawkeeper.
            goffs.append(Offer("We need a new sheriff in this town.",context=(context.INFO,),effect=self._reveal,data={"subject":"crime"}))
        return goffs
    def _reveal(self,camp):
        self.visible = True

class Evidence(TarotCard):
    # If first card, place the evidence right in a crime scene that the PC can discover-
    # correspondence in a bandit base, a personal effect at a murder scene, etc.
    pass


class Clue(TarotCard):
    INTERACTIONS = (Interaction(NameChecker(["Crime"]),action_triggers=[],results=("Evidence",None,None),passparams=(((ME_PERSON,),None),None,None)),
                    )

class Crime(TarotCard):
    pass

