from game.content import mechtarot
from game.content.mechtarot import TarotCard, Interaction, TagChecker, NameChecker, ME_TAROTPOSITION, \
    ME_AUTOREVEAL,CardTransformer, Consequence, CardCaller, CardDeactivator
import pbge
import gears
from game.ghdialogue import context
from pbge.dialogue import Offer
import random
import collections
import actionscenes
import missionbuilder

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

class Renegades(TarotCard):
    TAGS = (MT_FACTION,)
    QOL = gears.QualityOfLife(defense=-1)

class MilitantSplinter(TarotCard):
    TAGS = (MT_FACTION,MT_THREAT)
    NEGATIONS = (TheDisbanded,)
    ASCENSIONS = ()
    QOL = gears.QualityOfLife(stability=-2,community=-2,defense=2)

    def get_incrimination_offers(self, beta_card, npc, camp, interaction):
        """

        :type camp: gears.GearHeadCampaign
        """
        myoff = list()
        myfac = self.elements[ME_FACTION]
        mycity = camp.scene.get_metro_scene()
        if npc.faction and npc.faction.get_faction_tag() == myfac.get_faction_tag() and npc.faction != myfac:
            # This character is a member of the main faction, but not a member of the splinter faction.
            myoff.append(
                Offer(
                    "[THIS_IS_TERRIBLE_NEWS] [FACTION_MUST_BE_PUNISHED] You are authorized to launch a mecha strike against their command center.",
                    context=(context.REVEAL,), subject=self, subject_start=True,
                    data={"reveal": "{} has {}".format(myfac,beta_card.elements.get(ME_CRIMED,"gone rogue")),"faction":str(self.elements[ME_FACTION])},
                    effect=CardCaller(beta_card,interaction,self._start_disbanding_mission)
                )
            )
        elif npc.faction and npc.faction != myfac and gears.tags.Police in npc.faction.get_faction_tag().factags:
            # This character is a police officer; they can also authorize action against the lawbreakers.
            myoff.append(
                Offer(
                    "[THIS_IS_TERRIBLE_NEWS] [FACTION_MUST_BE_PUNISHED] You are authorized to launch a mecha strike against their command center.",
                    context=(context.REVEAL,), subject=self, subject_start=True,
                    data={"reveal": "{} has {}".format(myfac,beta_card.elements.get(ME_CRIMED,"gone rogue")),"faction":str(self.elements[ME_FACTION])},
                    effect=CardCaller(beta_card,interaction,self._start_disbanding_mission)
                )
            )
        elif mycity and mycity.faction and npc.faction and npc.faction != myfac and npc.faction.get_faction_tag() is mycity.faction.get_faction_tag():
            # This character belongs to the city's ruling faction. They too can authorize a mecha strike.
            myoff.append(
                Offer(
                    "[THIS_IS_TERRIBLE_NEWS] [FACTION_MUST_BE_PUNISHED] You are authorized to launch a mecha strike against their command center.",
                    context=(context.REVEAL,), subject=self, subject_start=True,
                    data={"reveal": "{} has {}".format(myfac,beta_card.elements.get(ME_CRIMED,"gone rogue")),"faction":str(self.elements[ME_FACTION])},
                    effect=CardCaller(beta_card,interaction,self._start_disbanding_mission)
                )
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
                "Justice": Consequence(alpha_card_tf=CardTransformer("TheDisbanded",alpha_params=(ME_FACTION,)),beta_card_tf=CardDeactivator()),
                "Lose": Consequence(alpha_card_tf=CardTransformer("Renegades", alpha_params=(ME_FACTION,)),beta_card_tf=CardDeactivator()),
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

        self.adventure_seed = None

        return True

    def REVEAL_WIN(self,camp):
        # The subplot has been won.
        self.visible = True
        self.memo = "You learned that {} has been taken over by extremists.".format(self.elements[ME_FACTION])

    def get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if npc.faction is not self.elements[ME_FACTION]:
            if not self.visible:
                mygram["[News]"].append("there has been a lot of hostility from {} lately".format(self.elements[ME_FACTION]))
        if npc.faction is self.elements[ME_FACTION]:
            mygram["[HELLO]"].append("I am proud to be a member of {}.".format(self.elements[ME_FACTION]))
        return mygram

    def _start_disbanding_mission(self,camp,beta_card,interaction):
        self.adventure_seed = missionbuilder.BuildAMissionSeed(
            camp, "Strike {}'s command center".format(self.elements[ME_FACTION]),
            (self.elements["LOCALE"], self.elements["MISSION_GATE"]),
            enemy_faction=self.elements[ME_FACTION], rank=self.rank,
            objectives=(missionbuilder.BAMO_STORM_THE_CASTLE,),
            cash_reward=500, experience_reward=250,
            data={
                "win":CardCaller(self,beta_card,interaction.consequences["Justice"]),
                "lose": CardCaller(self, beta_card, interaction.consequences["Lose"]),
                "win_message": "With their command center destroyed, the remnants of {} are quickly brought to justice.".format(self.elements[ME_FACTION]),
                "lose_message": "Following the attack on their command center, the remnants of {} scatter to the wind. They will continue to be a thorn in the side of {} for years to come.".format(self.elements[ME_FACTION],self.elements["LOCALE"]),
            }
        )
        self.memo = "You have been authorized to take action against {}'s command center.".format(self.elements[ME_FACTION])
        self.elements["METROSCENE"].purge_faction(camp,self.elements[ME_FACTION])

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.adventure_seed:
            thingmenu.add_item(self.adventure_seed.name, self.adventure_seed)

    def t_UPDATE(self, camp):
        # If the adventure has ended, get rid of it.
        if self.adventure_seed and self.adventure_seed.ended:
            if self.adventure_seed.is_won():
                pbge.alert(self.adventure_seed.data["win_message"])
                self.adventure_seed.data["win"](camp)
            else:
                pbge.alert(self.adventure_seed.data["lose_message"])
                self.adventure_seed.data["lose"](camp)
            self.adventure_seed = None


class Atrocity(TarotCard):
    # A faction has been implicated in serious wrongdoing.
    TAGS = (MT_FACTION,MT_INCRIMINATING)
    QOL = gears.QualityOfLife(stability=-2)

    def custom_init( self, nart ):
        # Add the subplot which will decide the splinter faction and provide a discovery route.
        if not self.elements.get(ME_AUTOREVEAL):
            tplot = self.add_sub_plot(nart, "DZD_WarCrimes", ident="REVEAL")
            self.elements[ME_CRIME] = tplot.elements[ME_CRIME]
            self.elements[ME_CRIMED] = tplot.elements[ME_CRIMED]
        else:
            if not self.elements.get(ME_CRIME):
                self.register_element(ME_CRIME,"an atrocity")
            if not self.elements.get(ME_CRIMED):
                self.register_element(ME_CRIMED,"committed atrocities")
            self.memo = "You know that {} {}.".format(self.elements[ME_FACTION],self.elements[ME_CRIMED])
        return True

    def REVEAL_WIN(self,camp):
        # The subplot has been won.
        self.visible = True
        self.memo = "You learned that {} has {}.".format(self.elements[ME_FACTION],self.elements[ME_CRIMED])


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
