from game.content import mechtarot
from game.content.mechtarot import TarotCard, Interaction, TagChecker, NameChecker, ME_TAROTPOSITION, \
    ME_AUTOREVEAL,CardTransformer, Consequence
import pbge
import gears
from game.ghdialogue import context
from pbge.dialogue import Offer
import random
import collections

MT_CRIME = "CRIME"
MT_FACTION = "FACTION"
MT_HEROIC = "HEROIC"
MT_INCRIMINATING = "INCRIMINATING"
MT_PERSON = "PERSON"
MT_THREAT = "THREAT"

ME_FACTION = "CARD_FACTION"
ME_PERSON = "CARD_PERSON"
ME_PUZZLEITEM = "CARD_PUZZLEITEM"
ME_CRIME = "CRIME_TEXT"
ME_CRIMED = "CRIME_VERBED_TEXT"

class TheDisbanded(TarotCard):
    TAGS = (MT_FACTION,)

class MilitantSplinter(TarotCard):
    TAGS = (MT_FACTION,MT_THREAT)
    NEGATIONS = (TheDisbanded,)
    ASCENSIONS = ()

    def get_incrimination_offers(self, beta_card, npc, camp, interaction):
        myoff = list()
        myfac = self.elements[ME_FACTION]
        if npc.faction and npc.faction.get_faction_tag() == myfac.get_faction_tag() and npc.faction != myfac:
            # This character is a member of the main faction, but not a member of the splinter faction.
            myoff.append(
                Offer("Thanks for letting me know.", context=(context.REVEAL,), subject=self, subject_start=True, data={"reveal": "{} has gone rogue".format(myfac)})
            )

        return myoff

    INTERACTIONS = (
        Interaction(
            # Revealing an atrocity committed by the splinter faction will force them to disband.
            card_checker=TagChecker(needed_tags=(MT_INCRIMINATING,),needed_elements=(ME_FACTION,)),
            action_triggers={
                mechtarot.AT_GET_DIALOGUE_OFFERS: get_incrimination_offers,
            },
            consequences = {
                "Justice": Consequence(alpha_card_tf=CardTransformer("TheDisbanded",alpha_params=(ME_FACTION,)))
            }
        ),
    )

    def custom_init( self, nart ):
        # Add the subplot which will decide the splinter faction and provide a discovery route.
        if not self.elements.get(ME_AUTOREVEAL):
            tplot = self.add_sub_plot(nart, "DZD_SplinterFaction", ident="REVEAL")
            self.elements[ME_FACTION] = tplot.elements["FACTION"]
        else:
            self.memo = "You learned that {} has been taken over by extremists.".format(self.elements[ME_FACTION])

        return True

    def REVEAL_WIN(self,camp):
        # The subplot has been won.
        self.visible = True
        self.memo = "You learned that {} has been taken over by extremists.".format(self.elements[ME_FACTION])

    def get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if camp.scene.civilian_team and camp.scene.local_teams.get(npc) is camp.scene.civilian_team:
            if not self.visible:
                mygram["[News]"].append("there has been a lot of hostility from {} lately".format(self.elements[ME_FACTION]))
        if npc.faction is self.elements[ME_FACTION]:
            mygram["[HELLO]"].append("I am proud to be a member of {}.".format(self.elements[ME_FACTION]))
        return mygram


class Atrocity(TarotCard):
    TAGS = (MT_FACTION,MT_INCRIMINATING)

    def t_START(self,camp):
        if not self.visible:
            pbge.alert("This is a test: {} did something bad.".format(self.elements[ME_FACTION]))
            self.visible = True

# class Convict(TarotCard):
#     # This person has been arrested.
#     TAGS = (MT_PERSON,)
#     LABEL = "zTAROT"
#
#
# class Demagogue(TarotCard):
#     # Threat card. -Politics.
#     # Effects on Game World:
#     # - Villagers who match "type" will epouse Demagogue's views, -25 reaction to PC
#     # Interactions:
#     #
#     TAGS = (MT_PERSON, MT_THREAT)
#     NEGATIONS = (Convict,)
#     LABEL = "zTAROT"
#
#     def custom_init(self, nart):
#         if ME_PERSON not in self.elements:
#             npc = gears.selector.random_character(self.rank + random.randint(1, 50),
#                                                   local_tags=self.elements["TOWN"].attributes,
#                                                   needed_tags=[gears.tags.Politician, ])
#             self.register_element(ME_PERSON, npc, dident="TOWN")
#         return True
#
#     def PERSON_offers(self, camp):
#         # Return list of dialogue offers.
#         mylist = list()
#
#         return mylist
#
#
# class Warrant(TarotCard):
#     LABEL = "zTAROT"
#     INTERACTIONS = (Interaction(TagChecker([MT_PERSON], [ME_PERSON]), action_triggers=[
#         BetaCardDialogueTrigger(ME_PERSON, "You win!", [context.ARREST, ])], results=(None, "Convict", None),
#                                 passparams=(None, ((ME_PERSON,), None), None)),
#                     )
#
#
# class TheLaw(TarotCard):
#     LABEL = "zTAROT"
#     def _fun(self, alpha, beta, camp):
#         pass
#
#     INTERACTIONS = (Interaction(NameChecker(["Evidence"]),
#                                 action_triggers=[
#                                     AlphaCardDialogueTrigger(ME_PERSON, "Here have a warrant",
#                                                                                     [context.INFO, ],
#                                                                                     data={"subject": "the evidence"})],
#                                 results=(None, None, "Warrant"), passparams=(None, None, (None, (ME_PERSON,)))),
#                     )
#
#     def custom_init(self, nart):
#         if ME_PERSON not in self.elements:
#             npc = gears.selector.random_character(self.rank + random.randint(1, 50), combatant=True)
#             npc.name = "The Law"
#             self.register_element(ME_PERSON, npc, dident="TOWN")
#         return True
#
#     def PERSON_offers(self, camp):
#         # Return list of dialogue offers.
#         mylist = list()
#         mylist.append(Offer("I am the law.", context=(context.HELLO,), ))
#         return mylist
#
#
# class LocalHero(TarotCard):
#     LABEL = "zTAROT"
#     TAGS = (MT_PERSON, MT_HEROIC)
#
#     def custom_init(self, nart):
#         if ME_PERSON not in self.elements:
#             npc = gears.selector.random_character(self.rank + random.randint(1, 50),
#                                                   needed_tags=(gears.tags.Adventurer,),
#                                                   local_tags=self.elements["TOWN"].attributes, combatant=True)
#             npc.name = "Local Hero"
#             self.register_element(ME_PERSON, npc, dident="TOWN")
#         return True
#
#     def PERSON_offers(self, camp):
#         # Return list of dialogue offers.
#         mylist = list()
#         if not self.visible:
#             mylist.append(
#                 Offer("I am the local hero.", context=(context.HELLO,), effect=self.reveal, data={"subject": "crime"}))
#         return mylist
#
#
# class TheBadge(TarotCard):
#     LABEL = "zTAROT"
#     INTERACTIONS = (Interaction(TagChecker([MT_PERSON, MT_HEROIC]), action_triggers=[
#         BetaCardDialogueTrigger(ME_PERSON, "You win!", [context.INFO, ], data={"subject": "the badge"})],
#                                 results=(None, "TheLaw", None), passparams=(None, (None, (ME_PERSON,)), None)),
#                     )
#
#     @classmethod
#     def matches(cls, pstate):
#         """Requires the TOWN to exist."""
#         return pstate.elements.get("TOWN")
#
#     def custom_init(self, nart):
#         if self.elements.get(ME_AUTOREVEAL):
#             self.memo = "{} needs a sheriff.".format(self.elements["TOWN"], )
#         else:
#             tplot = self.add_sub_plot(nart, "DZD_RevealBadge", ident="_RevealBadge")
#         return True
#
#     def _RevealBadge_WIN(self, camp):
#         if not self.visible:
#             self.memo = "{} needs a guardian.".format(self.elements["TOWN"], )
#             self.reveal(camp)
#
#
# class Evidence(TarotCard):
#     # If first card, place the evidence right in a crime scene that the PC can discover-
#     # correspondence in a bandit base, a personal effect at a murder scene, etc.
#     LABEL = "zTAROT"
#     def custom_init(self, nart):
#         if ME_PERSON not in self.elements:
#             npc = gears.selector.random_character(self.rank + random.randint(1, 50),
#                                                   local_tags=self.elements["TOWN"].attributes,
#                                                   needed_tags=[gears.tags.Criminal, ])
#             self.register_element(ME_PERSON, npc)
#         if ME_CRIME not in self.elements or ME_CRIMED not in self.elements:
#             self.elements[ME_CRIME] = "criminal activity"
#             self.elements[ME_CRIMED] = "committed crimes"
#         if ME_PUZZLEITEM not in self.elements or not self.elements.get(ME_AUTOREVEAL):
#             # Add a subplot to reveal this clue.
#             tplot = self.add_sub_plot(nart, "DZD_RevealClue", ident="_RevealEvidence")
#             self.elements[ME_PUZZLEITEM] = tplot.elements.get(ME_PUZZLEITEM)
#         if self.elements.get(ME_AUTOREVEAL):
#             self.memo = "You have evidence that {} {}.".format(self.elements[ME_PERSON], self.elements[ME_CRIMED])
#         return True
#
#     def _RevealEvidence_WIN(self, camp):
#         if not self.visible:
#             pbge.alert(
#                 "You discover evidence linking {} to {}.".format(self.elements[ME_PERSON], self.elements[ME_CRIME]))
#             self.memo = "You discovered evidence that {} {}.".format(self.elements[ME_PERSON], self.elements[ME_CRIMED])
#             self.reveal(camp)
#
#
# class Clue(TarotCard):
#     LABEL = "zTAROT"
#     def custom_init(self, nart):
#         if ME_PERSON not in self.elements:
#             npc = gears.selector.random_character(self.rank + random.randint(1, 50),
#                                                   local_tags=self.elements["TOWN"].attributes,
#                                                   needed_tags=[gears.tags.Criminal, ])
#             self.register_element(ME_PERSON, npc)
#         if ME_PUZZLEITEM not in self.elements or not self.elements.get(ME_AUTOREVEAL):
#             # Add a subplot to reveal this clue.
#             tplot = self.add_sub_plot(nart, "DZD_RevealClue", ident="_RevealClue")
#             self.elements[ME_PUZZLEITEM] = tplot.elements.get(ME_PUZZLEITEM)
#         if self.elements.get(ME_AUTOREVEAL):
#             self.memo = "You discovered a clue, but don't know what it means yet."
#         return True
#
#     def _RevealClue_WIN(self, camp):
#         if not self.visible:
#             self.memo = "You discovered a clue, but don't know what it means yet."
#             self.reveal(camp)
#
#     def find_clue_from_puzzleitem(self, beta, camp):
#         pbge.alert("You discover evidence that {} {}.".format(self.elements[ME_PERSON], beta.elements[ME_CRIMED]))
#
#     INTERACTIONS = (Interaction(TagChecker([MT_CRIME]),
#                                 action_triggers=[
#                                     AlphaCardPuzzleItemTrigger(ME_PUZZLEITEM, menu_option="Search for clues.",
#                                                                                       extra_fx=find_clue_from_puzzleitem)],
#                                 results=("Evidence", None, None),
#                                 passparams=(((ME_PERSON,), (ME_CRIME, ME_CRIMED)), None, None)),
#                     )
#
#
# class Murder(TarotCard):
#     LABEL = "zTAROT"
#     TAGS = (MT_CRIME,)
#     CRIMED_PATTERNS = ('murdered {}', 'had {} killed', 'had {} murdered', 'killed {}')
#
#     def custom_init(self, nart):
#         if ME_PERSON not in self.elements:
#             npc = self.register_element(ME_PERSON, gears.selector.random_pilot(50))
#         else:
#             npc = self.elements[ME_PERSON]
#         # Record the crime text elements.
#         self.elements[ME_CRIME] = "the murder of {}".format(npc)
#         self.elements[ME_CRIMED] = random.choice(self.CRIMED_PATTERNS).format(npc)
#         if not self.elements.get(ME_AUTOREVEAL):
#             # Add a subplot to reveal this murder.
#             tplot = self.add_sub_plot(nart, "DZD_RevealMurder", ident="_RevealMurder")
#             self.offer_one_ready = True
#             self.offer_two_ready = True
#         else:
#             self.memo = "{} has been murdered.".format(self.elements[ME_PERSON].name)
#         return True
#
#     def _RevealMurder_WIN(self, camp):
#         if not self.visible:
#             self.memo = "You discovered that {} has been murdered.".format(self.elements[ME_PERSON].name)
#             self.reveal(camp)
#
#     def _get_generic_offers(self, npc, camp):
#         """Get any offers that could apply to non-element NPCs."""
#         goffs = list()
#         if camp.scene.civilian_team and camp.scene.local_teams.get(npc) is camp.scene.civilian_team:
#             npc = self.elements[ME_PERSON]
#             if self.offer_one_ready and not self.visible:
#                 # Any villager can tell you about the NPC going missing.
#                 goffs.append(Offer(
#                     "{} has been missing for some time now. I hope nothing bad has happened to {}.".format(npc,
#                                                                                                            npc.gender.object_pronoun),
#                     context=(context.INFO,), data={"subject": str(self.elements[ME_PERSON])},
#                     subject=str(self.elements[ME_PERSON]), effect=self._do_offer_one))
#         #            else:
#         # NPCs might give their opinion on the murder.
#         return goffs
#
#     def _do_offer_one(self, camp):
#         self.offer_one_ready = False
#         self.memo = "You heard that {} has gone missing.".format(self.elements[ME_PERSON])
#
#     def get_dialogue_grammar(self, npc, camp):
#         if camp.scene.civilian_team and camp.scene.local_teams.get(npc) is camp.scene.civilian_team:
#             # Return the IP_ grammar.
#             mygram = dict()
#             npc = self.elements[ME_PERSON]
#             if not self.visible:
#                 mygram["[News]"] = ["{} hasn't been around much lately".format(npc)]
#             else:
#                 mygram["[News]"] = ["it's a shame what happened to {}".format(npc)]
#             return mygram
