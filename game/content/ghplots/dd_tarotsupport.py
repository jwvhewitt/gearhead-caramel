# This unit contains support plots for tarot cards.
from pbge.plots import Plot, PlotState
from game.content import ghwaypoints,ghterrain,plotutility
import gears
import pbge
from game import teams,ghdialogue
from game.ghdialogue import context
import random
from pbge.dialogue import ContextTag,Offer
from . import dd_main,dd_customobjectives
from . import dd_tarot
from .dd_tarot import ME_FACTION,ME_PERSON,ME_CRIME,ME_CRIMED,CONSEQUENCE_WIN,CONSEQUENCE_LOSE,ME_PUZZLEITEM
from game.content import mechtarot
import game.content.plotutility
import game.content.gharchitecture
from . import dd_combatmission
import collections
from . import missionbuilder

#   ****************************
#   ***  MT_REVEAL_ClueItem  ***
#   ****************************

class ClueInBunker( Plot ):
    LABEL = "MT_REVEAL_ClueItem"
    active = True
    scope = "METRO"
    ITEM_TYPES = (ghwaypoints.RetroComputer,ghwaypoints.Bookshelf,ghwaypoints.UlsaniteFilingCabinet)
    def custom_init( self, nart ):
        team1 = teams.Team(name="Player Team")
        return_to = (self.elements["METROSCENE"],self.elements["MISSION_GATE"])
        outside_scene = gears.GearHeadScene(
            35,35,plotutility.random_deadzone_spot_name(),player_team=team1,scale=gears.scale.MechaScale,
            exploration_music="Lines.ogg", combat_music="Late.ogg",exit_scene_wp=return_to
        )
        myscenegen = pbge.randmaps.SceneGenerator(outside_scene, game.content.gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, outside_scene, myscenegen, ident="LOCALE", dident="METROSCENE", temporary=True )

        mygoal = self.register_element("_goalroom",pbge.randmaps.rooms.FuzzyRoom(random.randint(8,15),random.randint(8,15),parent=outside_scene,anchor=pbge.randmaps.anchors.middle))

        self.register_element("ENTRANCE_ROOM", pbge.randmaps.rooms.OpenRoom(5, 5, anchor=random.choice(pbge.randmaps.anchors.EDGES)), dident="LOCALE")
        myent = self.register_element(
            "ENTRANCE", game.content.ghwaypoints.Exit(anchor=pbge.randmaps.anchors.middle,
             dest_scene=self.elements["METROSCENE"], dest_entrance=self.elements["MISSION_GATE"]), dident="ENTRANCE_ROOM"
        )

        team1 = teams.Team(name="Player Team")
        inside_scene = gears.GearHeadScene(
            12,12,"Bunker",player_team=team1,scale= gears.scale.HumanScale,
            exploration_music="Lines.ogg", combat_music="Late.ogg",exit_scene_wp=return_to
        )
        intscenegen = pbge.randmaps.SceneGenerator(inside_scene, game.content.gharchitecture.DefaultBuilding())
        self.register_scene( nart, inside_scene, intscenegen, ident="GOALSCENE", dident="LOCALE", temporary=True )

        introom = self.register_element('_introom', pbge.randmaps.rooms.OpenRoom(random.randint(6,10), random.randint(6,10), anchor=pbge.randmaps.anchors.middle, decorate=pbge.randmaps.decor.OmniDec(win=game.content.ghterrain.Window)), dident="GOALSCENE")

        self.register_element(ME_PUZZLEITEM, random.choice(self.ITEM_TYPES)(plot_locked=True), dident="_introom")

        int_con = game.content.plotutility.IntConcreteBuildingConnection(self, outside_scene, inside_scene, room1=mygoal, room2=introom)

        self.add_sub_plot(
            nart, "MECHA_ENCOUNTER",
            spstate=PlotState().based_on(self,{"ROOM":mygoal,"FACTION":self.elements.get(ME_FACTION)}), necessary=False
        )
        self.add_sub_plot(nart,"BASE_ROOM_LOOT",spstate=PlotState(elements={"ROOM":introom,"FACTION":self.elements.get(ME_FACTION)},).based_on(self))

        self.location_unlocked = False
        self.clue_uncovered = False
        self.add_sub_plot(nart,"REVEAL_LOCATION",spstate=PlotState(
            elements={"INTERESTING_POINT":"The place is supposed to be uninhabited, but I caught sight of a mecha base and got chased off by the defenders."},
        ).based_on(self),ident="LOCATE")
        return True

    def LOCATE_WIN(self,camp):
        self.location_unlocked = True

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.location_unlocked:
            thingmenu.add_item("Go to {}".format(self.elements["LOCALE"]), self.go_to_locale)

    def go_to_locale(self,camp):
        camp.destination, camp.entrance = self.elements["LOCALE"],self.elements["ENTRANCE"]

    def ME_PUZZLEITEM_menu(self, camp, thingmenu):
        if self.clue_uncovered:
            thingmenu.desc = '{} It appears to contain records belonging to {}.'.format(thingmenu.desc,self.elements[ME_FACTION])
        thingmenu.add_item("Search randomly.",self._win_mission)
        thingmenu.add_item("Leave it alone.",None)

    def _win_mission(self,camp):
        pbge.alert("You search for a while, but don't really know what to look for. It appears to contain records belonging to {}.".format(self.elements[ME_FACTION]))
        self.clue_uncovered = True
        camp.check_trigger("WIN",self)


class RetroComputerInPlainSight( Plot ):
    # Just stick the clue right there in town. Note that this clue only works if the
    # associated faction has an allied building in town.
    LABEL = "MT_REVEAL_ClueItem"
    active = True
    scope = "METRO"
    @classmethod
    def matches( cls, pstate ):
        """Returns True if this plot matches the current plot state."""
        return ME_FACTION in pstate.elements

    def custom_init( self, nart ):
        myscene = self.elements["METROSCENE"]
        myfac = self.elements[ME_FACTION]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene, must_find=True)
        destroom = self.seek_element(nart, "_ROOM", self._is_good_room, scope=destscene, must_find=True)

        myclue = self.register_element(ME_PUZZLEITEM,ghwaypoints.RetroComputer(plot_locked=True),dident="_ROOM")
        self.logged_in = False
        return True
    def _is_best_scene(self,nart,candidate):
        return (isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and
                gears.tags.SCENE_BUILDING in candidate.attributes and
                candidate.faction and nart.camp.are_ally_factions(candidate.faction,self.elements[ME_FACTION]))
    def _is_good_room(self,nart,candidate):
        return isinstance(candidate,pbge.randmaps.rooms.Room)
    def ME_PUZZLEITEM_menu(self, camp, thingmenu):
        thingmenu.desc = '{} It appears to contain records belonging to {}.'.format(thingmenu.desc,self.elements[ME_FACTION])
        if not self.logged_in:
            thingmenu.add_item("Attempt to log in.",self._win_mission)
        else:
            thingmenu.add_item("Search for interesting data.", self._search_interesting)
        thingmenu.add_item("Leave it alone.",None)

    def _win_mission(self,camp):
        pbge.alert("Amazingly enough, someone left the computer turned on! You begin snooping through files.")
        self.logged_in = True
        camp.check_trigger("WIN",self)

    def _search_interesting(self,camp):
        pbge.alert("You search for a while, but there is too much noise and not enough signal. If only you knew what you were looking for.")


#   ****************************
#   ***  MT_REVEAL_WarCrime  ***
#   ****************************

class LunarRefugeeLost( Plot ):
    LABEL = "MT_REVEAL_WarCrime"
    active = True
    scope = "METRO"

    # Meet a Lunar refugee who got separated from their group.
    def custom_init( self, nart ):
        myscene = self.elements["METROSCENE"]
        enemy_fac = self.elements.get(ME_FACTION)
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene)

        mynpc = self.register_element("NPC",gears.selector.random_character(rank=random.randint(self.rank-10,self.rank+10),local_tags=(gears.personality.Luna,)),dident="_DEST")
        destscene.local_teams[mynpc] = destscene.civilian_team

        self.register_element(dd_tarot.ME_CRIME,"the destruction of a Lunar refugee camp")
        self.register_element(dd_tarot.ME_CRIMED,"destroyed {}'s refugee camp".format(mynpc))

        self.mission_seed = missionbuilder.BuildAMissionSeed(
            nart.camp,"Investigate {}'s village".format(self.elements["NPC"]),
            (self.elements["LOCALE"], self.elements["MISSION_GATE"]),
            enemy_faction=self.elements[ME_FACTION], rank=self.rank,
            objectives=(dd_customobjectives.DDBAMO_INVESTIGATE_REFUGEE_CAMP,),
            cash_reward=500, experience_reward=250,one_chance=False,
            win_message= "You approach the campsite of the Lunar refugees, and see that it has been utterly destroyed by {}.".format(enemy_fac),
        )

        self.mission_accepted = False
        self.mission_finished = False
        self.got_rumor = False

        return True

    def t_START(self,camp):
        if self.mission_seed.is_won() and not self.mission_finished:
            camp.check_trigger("WIN", self)
            self.mission_finished = True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if camp.scene.get_root_scene() is self.elements["LOCALE"] and npc is not self.elements["NPC"] and not self.got_rumor:
            mygram["[News]"].append("some Aegis refugees have moved into the area")
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.got_rumor and camp.scene.get_root_scene() is self.elements["LOCALE"] and npc is not self.elements["NPC"]:
            mynpc = self.elements["NPC"]
            goffs.append(Offer(
                msg="You can ask {} about that; {}'s one of them. You can usually find {} at {}.".format(mynpc,mynpc.gender.subject_pronoun,mynpc.gender.object_pronoun,self.elements["_DEST"]),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject="Aegis refugees", data={"subject": "the refugees"}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self,camp):
        self.got_rumor = True
        self.memo = "{} is a refugee from Luna who can usually be found at {}.".format(self.elements["NPC"],self.elements["_DEST"])

    def NPC_offers(self,camp):
        mylist = list()

        # This plot has three phases: Before PC has accepted mission, while PC is doing mission, and
        # after PC has completed mission.
        if not self.mission_accepted:
            mylist.append(Offer(
                "[HELP_ME_BY_DOING_SOMETHING] I am a refugee from Luna, seeking asylum on Earth, but my camp was attacked by mecha in the dead zone and I became separated from the others...",
                context=(context.HELLO,)
            ))
            mylist.append(Offer(
                "If you could visit our camp site and make sure that everything is okay, I'd greatly appreciate it.",
                context=(context.PROPOSAL,),subject=self,subject_start=True,data={"subject":"your camp"}
            ))
            mylist.append(Offer(
                "Thank you so much. Here are the coordinates where they were last.",
                context=(context.ACCEPT,),subject=self,effect=self._accept_mission
            ))
        else:
            if not self.mission_seed.is_won():
                mylist.append(Offer(
                    "Come back and let me know when you've found out what's happening at the camp.",
                    context=(context.HELLO,)
                ))
            else:
                mylist.append(Offer(
                    "[HELLO] Did you find out anything about what happened to my camp?",
                    context=(context.HELLO,)
                ))
                enemy_fac = self.elements.get(dd_tarot.ME_FACTION)
                if enemy_fac:
                    mylist.append(Offer(
                        "[THANKS_FOR_BAD_NEWS] [I_MUST_CONSIDER_MY_NEXT_STEP] Above all, I know that {} must pay for what they did.".format(enemy_fac),
                        context=(context.CUSTOM,), data={"reply":"The camp was destroyed by {}.".format(enemy_fac)},
                        effect=self._deliver_the_news
                    ))
                else:
                    mylist.append(Offer(
                        "[THANKS_FOR_BAD_NEWS] [I_MUST_CONSIDER_MY_NEXT_STEP] I am now alone on this world, or nearly so... I hope that I can see you again.",
                        context=(context.CUSTOM,), data={"reply":"The camp was destroyed."},
                        effect=self._deliver_the_news
                    ))

        return mylist

    def _deliver_the_news(self,camp):
        if self.elements["NPC"].combatant:
            self.elements["NPC"].relationship.tags.add(gears.relationships.RT_LANCEMATE)
        self.elements["NPC"].relationship.role = gears.relationships.R_ACQUAINTANCE
        self.elements["NPC"].relationship.expectation = gears.relationships.E_AVENGER
        self.end_plot(camp)

    def _accept_mission(self,camp):
        self.mission_accepted = True
        self.elements["NPC"].relationship.reaction_mod += random.randint(1,50)
        self.memo = "{} at {} asked you to investigate what happened to {} refugee camp.".format(self.elements["NPC"],self.elements["_DEST"],self.elements["NPC"].gender.possessive_determiner)
        missionbuilder.NewMissionNotification("Investigate {}'s village".format(self.elements["NPC"]), self.elements["MISSION_GATE"])

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_accepted and not self.mission_finished:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)



#   ****************************
#   ***  MT_REVEAL_HateClub  ***
#   ****************************

class SpFa_MilitarySplinter(Plot):
    LABEL = "MT_REVEAL_HateClub"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        # Step one: Determine the military faction that will be the basis of our splinter.
        city = self.elements["LOCALE"]
        city_fac = city.faction
        if city_fac in nart.camp.faction_relations:
            candidates = [fac for fac in nart.camp.faction_relations[city_fac].allies if gears.tags.Military in fac.factags]
            if candidates:
                myfac = random.choice(candidates)
                mycircle = self.register_element(ME_FACTION,gears.factions.Circle(nart.camp,parent_faction=myfac))
                if myfac in nart.camp.faction_relations and nart.camp.faction_relations[myfac].enemies:
                    hated_fac = random.choice(nart.camp.faction_relations[myfac].enemies)
                    hated_origin = random.choice(hated_fac.LOCATIONS)
                    if hated_origin not in myfac.LOCATIONS:
                        self.hates = hated_origin
                    else:
                        self.hates = None
                else:
                    self.hates = None
                self.add_sub_plot(nart,"PLACE_LOCAL_REPRESENTATIVES",spstate=PlotState(elements={"FACTION":mycircle}).based_on(self))
                # Add at least one loyalist, too.
                self.add_sub_plot(nart,"PLACE_LOCAL_REPRESENTATIVES",spstate=PlotState(elements={"FACTION":myfac}).based_on(self))
            self.adventure_seed = None
            self.mission_giver = None
            return bool(candidates)

    def register_adventure(self,camp):
        self.adventure_seed = dd_combatmission.CombatMissionSeed(camp, "Mission for {}".format(self.elements[ME_FACTION]),
                                                                 (self.elements["LOCALE"], self.elements["ENTRANCE"]),
                                                enemy_faction=None, allied_faction=self.elements[ME_FACTION], include_war_crimes=True)
        self.memo = "{} sent you to do a mysterious mecha mission for {}.".format(self.mission_giver,self.elements[ME_FACTION])
        missionbuilder.NewMissionNotification(self.adventure_seed.name, self.elements["MISSION_GATE"])

    def t_UPDATE(self,camp):
        # If the mission has ended, get rid of it.
        if self.adventure_seed and self.adventure_seed.ended:
            self.memo = None
            if self.adventure_seed.crimes_happened:
                camp.check_trigger("WIN", self)
                self.end_plot(camp)
            self.adventure_seed = None

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.adventure_seed:
            thingmenu.add_item(self.adventure_seed.name, self.adventure_seed)

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()

        if npc.faction is self.elements[ME_FACTION]:
            if not self.adventure_seed:
                if self.hates in camp.pc.personality:
                    # No mission for you, foreigner.
                    goffs.append(Offer("Not for you; {} doesn't need the help of your kind.".format(self.elements[ME_FACTION]),context=ContextTag([context.MISSION,]),effect=self._no_mission_for_you))
                else:
                    self.mission_giver = npc
                    goffs.append(Offer("As you know, {} is responsible for keeping {} safe. We have a mission coming up, and I could use your help.".format(self.elements[ME_FACTION],self.elements["LOCALE"]),context=ContextTag([context.MISSION,]),subject=self,subject_start=True))
                    goffs.append(Offer("[GOOD] Report to the combat zone as quickly as possible; we will inform you of the mission objectives as soon as you arrive.",context=ContextTag([context.ACCEPT,]),subject=self,effect=self.register_adventure))
                    goffs.append(Offer("Don't think I will forget this.",context=ContextTag([context.DENY,]),subject=self))
        elif camp.are_faction_allies(npc,self.elements[ME_FACTION]):
            goffs.append(Offer("[THIS_IS_A_SECRET] [chat_lead_in] {ME_FACTION} have crossed the line. They see enemies everywhere, from within and outside of {LOCALE}.".format(**self.elements),
                               data={"subject":str(self.elements[ME_FACTION])},no_repeats=True,
                               context=ContextTag([context.INFO, ]), effect=self._no_mission_for_you, subject=str(self.elements[ME_FACTION])))
        elif self.hates in npc.personality:
            goffs.append(Offer("[BeCarefulOfSubject]; they say they're protecting {}, but really they've turned into a hate club. They want to get rid of all of us outsiders.".format(self.elements["LOCALE"]),
                               data={"subject":str(self.elements[ME_FACTION])},no_repeats=True,
                               context=ContextTag([context.INFO, ]), effect=self._no_mission_for_you, subject=str(self.elements[ME_FACTION])))
        return goffs

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if npc.faction is not self.elements[dd_tarot.ME_FACTION]:
            mygram["[News]"] = ["{ME_FACTION} are fanatical in their defense of {LOCALE}".format(**self.elements), ]
        return mygram

    def _no_mission_for_you(self,camp):
        camp.check_trigger("WIN",self)
        self.end_plot(camp)


class HateClub_GenericHaters(Plot):
    LABEL = "MT_REVEAL_HateClub"
    active = True
    scope = "METRO"
    _ADJECTIVES = (
        "Vigilant","Pure","National","Militant","Patriotic","Radical", "Armed", "Popular", "Orthodox", "Confederate",
        "First", "Loyal"
    )
    _NOUNS = (
        "Front", "Bloc", "Patriots", "Order", "Force", "Rally", "Hooligans", "Rebels", "Movement", "Army", "League"
    )
    _PURPOSE = (
        "Justice", "Purity", "Blood", "Hatred", "Freedom", "Strength", "Power","Empire","Pride","Action","Identity"
    )
    _PATTERNS = (
        'the {A1} {N} for {A2} {P}', 'the {A1} {N} of {L}', 'the {A1} {L} {N} for {P}', 'the {A1} {P} {N} of {L}',
        'the {L} {N} for {A1} {P}'
    )

    @classmethod
    def matches( cls, pstate ):
        """Returns True if this plot matches the current plot state."""
        return "LOCALE" in pstate.elements and pstate.elements["LOCALE"].faction and "METRO" in pstate.elements and "MISSION_GATE" in pstate.elements

    def custom_init(self, nart):
        # Step one: Determine the faction that will be the basis of our splinter.
        if dd_tarot.ME_FACTION not in self.elements:
            self.register_element(dd_tarot.ME_FACTION,gears.factions.Circle(nart.camp,name=self._make_faction_name()))
        self.won = False
        return True

    def _make_faction_name(self):
        mydict = dict()
        adjectives = random.sample(self._ADJECTIVES,2)
        mydict['A1'] = adjectives[0]
        mydict['A2'] = adjectives[0]
        mydict['N'] = random.choice(self._NOUNS)
        mydict['P'] = random.choice(self._PURPOSE)
        mydict['L'] = str(self.elements["LOCALE"])
        mypat = random.choice(self._PATTERNS)
        return mypat.format(**mydict)

    def LOCALE_ENTER(self, camp):
        # Make sure we always have at least one member of this faction present. I don't know if they're gonna
        # die, but we might need them around for plots.
        if not [npc for npc in camp.scene.contents if isinstance(npc,gears.base.Character) and npc.faction is self.elements[dd_tarot.ME_FACTION]]:
            npc = gears.selector.random_character(self.rank,faction=self.elements[dd_tarot.ME_FACTION])
            camp.scene.contents.append(npc)

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()

        if npc.faction is self.elements[dd_tarot.ME_FACTION]:
            goffs.append(
                Offer(
                    "[HATE_SLOGAN] [HATE_CHAT]",
                    context=ContextTag([context.HELLO,])
                )
            )
            if not self.won:
                goffs.append(
                    Offer(
                        "All of our problems started when they began appearing in {LOCALE}... You know the ones I mean. You must know. Unless you're one of them? When {ME_FACTION} are triumphant, we will burn this corrupted city to the ground in order to protect our purity of essence!".format(**self.elements),
                        context=ContextTag([context.INFO]), effect=self._tell_about_club,
                        subject="{ME_FACTION}".format(**self.elements),
                        data={"subject": "{ME_FACTION}".format(**self.elements)}, no_repeats=True,
                    )
                )
            else:
                ghdialogue.SkillBasedPartyReply(
                    Offer(
                        "Ow, my [body_part]!",
                        context=ContextTag([context.CUSTOM]),data={"reply": "<punch {}>".format(camp.pc,npc)},
                        dead_end=True, effect=self._tell_about_club,
                    ),camp,goffs,gears.stats.Body,gears.stats.CloseCombat,self.rank,message_format="<{} punches "+ str(npc) + ">"
                )
        else:
            goffs.append(
                Offer(
                    "They're anti-mutant, anti-idealist, anti-immigrant, anti-intellectual, and probably any other antis you want to add to the list. [THEYWOULDBEFUNNYBUT]".format(**self.elements),
                    context=ContextTag([context.INFO]), effect=self._tell_about_club,
                    subject="{ME_FACTION}".format(**self.elements), no_repeats=True,
                    data={"subject": "{ME_FACTION}".format(**self.elements),'they': "{ME_FACTION}".format(**self.elements)}
                )
            )

        return goffs

    def _tell_about_club(self, camp):
        if not self.won:
            self.won = True
            camp.check_trigger("WIN", self)

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if npc.faction is not self.elements[dd_tarot.ME_FACTION] and not self.won:
            mygram["[News]"] = ["{ME_FACTION} are a local hate club".format(**self.elements), ]
        if npc.faction is self.elements[dd_tarot.ME_FACTION]:
            mygram["[HATE_SLOGAN]"] = [
                "{LOCALE} for {LOCALE} people! No mutants or uglies!".format(**self.elements),
                "You don't look like you're from around these parts; piss off before I make you!",
                "There's no problem in {LOCALE} that a murderous rampage couldn't fix.".format(**self.elements),
                "What we need to keep {LOCALE} safe is to bust a few heads open!".format(**self.elements),
                "Violence is power! Power is freedom! {LOCALE} is being choked by outsiders and uglies!".format(**self.elements),
            ]
            mygram["[HATE_CHAT]"] = [
                "Only {ME_FACTION} has the guts to look out for our precious bodily fluids!".format(**self.elements),
                "Know that {ME_FACTION} doesn't fear any of the multitudinous enemies conspiring against {LOCALE}!".format(**self.elements),
                "Join {ME_FACTION} and help us immanentize the eschaton!".format(**self.elements),
                "Look at these brain dead sheep entranced by lunar mind rays; only {ME_FACTION} dares to speak the truth!".format(**self.elements),
                "They call us a hate club, but {ME_FACTION} will make them all sorry when the uglies take over!".format(**self.elements),
            ]
        return mygram

#   ********************************
#   ***  MT_REVEAL_Investigator  ***
#   ********************************
#
# INVESTIGATION_SUBJECT: A string that can be used for "I'm investigating _____" or "Do you know anything about _____?"

class InvestigativeReporter(Plot):
    LABEL = "MT_REVEAL_Investigator"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        # Place the reporter.
        npc = gears.selector.random_character(rank=random.randint(self.rank, self.rank+20),
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              job=gears.jobs.ALL_JOBS["Reporter"])
        scene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])
        self.register_element(ME_PERSON, npc, dident="LOCALE")
        self.got_memo = False
        self.got_rumor = False
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def ME_PERSON_offers(self,camp):
        mylist = list()
        mylist.append(
            Offer(
                "[HELLO] Do you know anything about {INVESTIGATION_SUBJECT}? I'm working on a story.".format(**self.elements),
                ContextTag([context.HELLO,]),effect=self._reveal
            )
        )
        return mylist
    def _reveal(self,camp):
        camp.check_trigger("WIN",self)
        self.end_plot(camp)

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements[ME_PERSON]:
            # This is an NPC in Wujung. Give them some news.
            mygram["[News]"] = ["{ME_PERSON} has been investigating a story about {INVESTIGATION_SUBJECT}".format(**self.elements), ]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements[ME_PERSON] and not self.got_rumor:
            mynpc = self.elements[ME_PERSON]
            goffs.append(Offer(
                msg="As far as I know {} usually hangs out at {}.".format(mynpc,mynpc.get_scene()),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self,camp):
        mynpc = self.elements[ME_PERSON]
        self.got_rumor = True
        self.memo = "{} at {} has been investigating {}.".format(mynpc,mynpc.get_scene(),self.elements["INVESTIGATION_SUBJECT"])


#   **************************
#   ***  MT_SOCKET_Accuse  ***
#   **************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_CARD
#   ME_SOCKET

class GuardianJudgment(Plot):
    # - Make sure there's a Guardian in town at all times.
    # - Speak to the Guardian, or an ally, to activate your incrimination.
    LABEL = "MT_SOCKET_Accuse"
    active = True
    scope = "METRO"

    @classmethod
    def matches( cls, pstate ):
        """Returns True if this plot matches the current plot state."""
        return (
            "METROSCENE" in pstate.elements and
            pstate.elements["METROSCENE"] and
            pstate.elements["METROSCENE"].faction.get_faction_tag() in (gears.factions.TerranFederation,gears.factions.DeadzoneFederation)
        )

    def custom_init(self, nart):
        # Ensure there will always be at least one Guardian here.
        self.add_sub_plot(nart,"ENSURE_LOCAL_REPRESENTATION",PlotState(elements={"FACTION":gears.factions.Guardians}).based_on(self))
        self.mission_seed = None
        self.card = None
        return True

    def is_appropriate_judge(self,npc,camp):
        if npc.faction is not self.elements.get(ME_FACTION):
            return camp.are_faction_allies(npc, gears.factions.Guardians) or camp.are_faction_allies(npc,self.elements["METROSCENE"])

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if self.is_appropriate_judge(npc,camp) and not self.mission_seed:
            mysig = mysocket.get_activating_signals(mycard, camp)
            if mysig:
                card = mysig[0][0]
                    # Alright, we have someone with the power to incriminate. Harvest some information.
                villain = card.elements.get(ME_FACTION) or card.elements.get(ME_PERSON) or "Somebody"
                crimed = card.elements.get(ME_CRIMED) or "did something wrong"
                goffs.append(Offer(
                    "[THIS_IS_TERRIBLE_NEWS] [FACTION_MUST_BE_PUNISHED] You are authorized to launch a mecha strike against their command center.",
                    context=ContextTag([context.REVEAL]),effect=self._start_mission,
                    data={"reveal":"{} {}".format(villain,crimed),"faction":str(villain)}
                ))
                self.card = card
            elif mycard.visible:
                villain = self._get_villain()
                goffs.append(Offer(
                    "I'd like to help you, but without incriminating proof there's nothing I can do.",
                    context=ContextTag([context.REVEAL]),
                    data={"reveal":"{} {}".format(villain,"did something wrong"),}
                ))

        return goffs

    def _get_villain(self):
        if self.card:
            return self.card.elements.get(ME_FACTION) or self.card.elements.get(ME_PERSON) or "Somebody"
        else:
            return self.elements.get(ME_FACTION) or self.elements.get(ME_PERSON) or "Somebody"

    def _start_mission(self,camp):
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, "Strike {}'s command center".format(self.elements[ME_FACTION]),
            (self.elements["LOCALE"], self.elements["MISSION_GATE"]),
            enemy_faction=self.elements[ME_FACTION], rank=self.rank,
            objectives=(missionbuilder.BAMO_STORM_THE_CASTLE,),
            cash_reward=500, experience_reward=250,
            on_win=self._win_mission,on_loss=self._lose_mission,
            win_message = "With their command center destroyed, the remnants of {} are quickly brought to justice.".format(self.elements[ME_FACTION]),
            loss_message = "Following the attack on their command center, the remnants of {} scatter to the wind. They will continue to be a thorn in the side of {} for years to come.".format(self.elements[ME_FACTION],self.elements["LOCALE"]),
        )
        self.memo = "You have been authorized to take action against {}'s command center.".format(self._get_villain())
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])
        if ME_FACTION in self.card.elements:
            self.elements["METROSCENE"].purge_faction(camp,self.card.elements[ME_FACTION])

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

    def _win_mission(self,camp):
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if CONSEQUENCE_WIN in mysocket.consequences:
            mysocket.consequences[CONSEQUENCE_WIN](camp,mycard,self.card)
        self.end_plot(camp)

    def _lose_mission(self, camp):
        self.mission_seed = None
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if CONSEQUENCE_LOSE in mysocket.consequences:
            mysocket.consequences[CONSEQUENCE_LOSE](camp,mycard,self.card)
        self.end_plot(camp)


#   *******************************
#   ***  MT_SOCKET_Investigate  ***
#   *******************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_PERSON   The investigator
#   ME_CARD
#   ME_SOCKET

class InvestigateUsingWords(Plot):
    # - Send the player to Negotiate/Stealth their way into a faction meeting.
    LABEL = "MT_SOCKET_Investigate"
    active = True
    scope = "METRO"

    @classmethod
    def matches( cls, pstate ):
        """This plot requires a faction to investigate."""
        return ME_FACTION in pstate.elements

    def custom_init(self, nart):
        # Ensure there will always be at least one faction member here.
        self.add_sub_plot(nart, "ENSURE_LOCAL_REPRESENTATION", elements={"FACTION": self.elements[ME_FACTION]})
        self.card = None
        self.mission_given = False
        self.mission_won = False
        return True

    def ME_PERSON_offers(self, camp):
        """Get offers from the mission-giver."""
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if not self.mission_given:
            mysig = mysocket.get_activating_signals(mycard, camp)
            if mysig and not self.mission_given:
                card = mysig[0][0]
                villain = self.elements[ME_FACTION]
                crimed = card.elements.get(ME_CRIMED) or self.elements.get(ME_CRIMED) or "did crime"
                goffs.append(Offer(
                    "[MAYBE_YOU_COULD_HELP] I've been trying to infiltrate one of their meetings to find out more, but they all know me. You, on the other hand, could easily sneak in and record what they're planning.".format(villain),
                    context=ContextTag([context.REVEAL]),effect=self._start_mission,
                    data={"reveal":"{} {}".format(villain,crimed)}
                ))
                self.card = card
        else:
            goffs.append(Offer(
                "Come back after you have infiltrated the meeting.".format(**self.elements),
                context=ContextTag([context.HELLO]),
            ))
            if self.mission_won:
                goffs.append(Offer(
                    "[THANK_YOU] This is perfect; these recordings will prove exactly what's been going on. Hopefully now {} can be brought to justice.".format(self.elements[ME_FACTION]),
                    context=ContextTag([context.CUSTOM]), effect=self._win_investigation, no_repeats=True,
                    data={"reply":"I infiltrated the meeting and brought back this recording."}
                ))

        return goffs

    def _start_mission(self,camp):
        self.mission_given = True
        self.memo = "{} at {} asked you to investigate {} by sneaking into one of their meetings.".format(self.elements[ME_PERSON],self.elements[ME_PERSON].get_scene(),self.elements[ME_FACTION])

    def t_START(self,camp):
        # If the investigator dies, end this plot.
        if self.elements[ME_PERSON].is_destroyed():
            if not self.mission_given:
                if self.card:
                    mycard = self.elements[mechtarot.ME_CARD]
                    mysocket = self.elements[mechtarot.ME_SOCKET]
                    if CONSEQUENCE_LOSE in mysocket.consequences:
                        mysocket.consequences[CONSEQUENCE_LOSE](camp, mycard, self.card)
                self.end_plot(camp,True)
            elif self.mission_won:
                verb = self.card.elements.get(ME_CRIMED) or self.elements.get(ME_CRIMED) or "did terrible things"
                pbge.alert("Your recordings from the meeting prove that {} {}.".format(self.elements[ME_FACTION],verb))
                self._win_investigation(camp)

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if self.mission_given and npc.faction is self.elements[ME_FACTION] and not self.mission_won:
            villain = self.elements.get(ME_FACTION)
            goffs.append(Offer(
                "Our next meeting? Why would you be interested in that?",
                ContextTag([context.INFO,]),subject=self,subject_start=True,
                no_repeats=True,data={"subject":"your next meeting"}
            ))
            ghdialogue.SkillBasedPartyReply(
                Offer(
                    "It's always a pleasure to meet someone who sees the world in the right way. Come along, then... I'm heading to the meeting now.",
                    ContextTag([context.CUSTOM,]),subject=self,no_repeats=True,dead_end=True,
                    data={"reply":"I have read your newsletter and found the ideas genuinely stimulating."},
                    effect=self._attend_meeting
                ), camp, goffs, gears.stats.Charm, gears.stats.Negotiation, self.rank, gears.stats.DIFFICULTY_AVERAGE
            )
            ghdialogue.SkillBasedPartyReply(
                Offer(
                    "Oh, how wonderful! I've heard you've done great things over there. Well, the meeting is going to start soon, so let's get over there.",
                    ContextTag([context.CUSTOM, ]), subject=self, no_repeats=True, dead_end=True,
                    data={"reply": "Actually I'm a member of the Ipshil branch but just moved here."},
                    effect=self._attend_meeting
                ), camp, goffs, gears.stats.Charm, gears.stats.Stealth, self.rank, gears.stats.DIFFICULTY_AVERAGE
            )
            ghdialogue.SkillBasedPartyReply(
                Offer(
                    "Oh, right... Sorry, I guess I'm just bad with faces. Well, the meeting is going to start in a little while, so let's go there together.",
                    ContextTag([context.CUSTOM, ]), subject=self, no_repeats=True, dead_end=True,
                    data={"reply": "Don't you remember me? We met at the {} picnic last month.".format(self.elements[ME_FACTION])},
                    effect=self._attend_meeting
                ), camp, goffs, gears.stats.Charm, gears.stats.Performance, self.rank, gears.stats.DIFFICULTY_HARD
            )
            goffs.append(Offer(
                "[GOODBYE]",
                ContextTag([context.CUSTOM, ]), subject=self, no_repeats=True, dead_end=True,
                data={"reply": "Um, no reason..."}
            ))
        return goffs

    def _attend_meeting(self,camp):
        crime = self.card.elements.get(ME_CRIME) or self.elements.get(ME_CRIME) or "crime"
        pbge.alert("You attend the meeting of {ME_FACTION}. There is a lot of talk about reforging the world and purging the unworthy. It gets pretty repetitive after a while.".format(**self.elements))
        pbge.alert("Fortunately, there is also some talk of {}, and you get it all on tape.".format(crime))
        self.mission_won = True

    def _win_investigation(self,camp):
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if CONSEQUENCE_WIN in mysocket.consequences:
            mysocket.consequences[CONSEQUENCE_WIN](camp,mycard,self.card)
        self.end_plot(camp,total_removal=True)


class InvestigateUsingGiantRobots(Plot):
    # - Send the player to capture a building so it can be investigated.
    LABEL = "MT_SOCKET_Investigate"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        self.mission_seed = None
        self.card = None
        return True

    def ME_PERSON_offers(self, camp):
        """Get offers from the mission-giver."""
        goffs = list()
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if not self.mission_seed:
            mysig = mysocket.get_activating_signals(mycard, camp)
            if mysig and not self.mission_seed:
                card = mysig[0][0]
                    # Alright, we have someone with the power to incriminate. Harvest some information.
                villain = card.elements.get(ME_FACTION) or self.elements.get(ME_FACTION) or card.elements.get(ME_PERSON) or "Somebody"
                crimed = card.elements.get(ME_CRIMED) or self.elements.get(ME_CRIMED) or "did crime"
                goffs.append(Offer(
                    "[MAYBE_YOU_COULD_HELP] I've been trying to get info about {}, but their facility is heavily guarded. If you could get me in, I could find all the information we need.".format(villain),
                    context=ContextTag([context.REVEAL]),effect=self._start_mission,
                    data={"reveal":"{} {}".format(villain,crimed)}
                ))
                self.card = card
        else:
            villain = self.card.elements.get(ME_FACTION) or self.elements.get(ME_FACTION) or self.card.elements.get(
               ME_PERSON) or "Somebody"
            if self.mission_seed.is_won():
                verb = self.card.elements.get(ME_CRIMED) or self.elements.get(ME_CRIMED) or "did terrible things"
                goffs.append(Offer(
                    "We did it! I've found the proof that {} {}! Now we just need to alert someone with the power to do something about it...".format(villain,verb),
                    context=ContextTag([context.HELLO]), effect=self._win_investigation
                ))
            else:
                goffs.append(Offer(
                    "[HELLO] Get back to me after you've secured the base belonging to {}.".format(villain),
                    context=ContextTag([context.HELLO]), effect=self._win_investigation
                ))

        return goffs

    def _start_mission(self,camp):
        villain = self.card.elements.get(ME_FACTION) or self.elements.get(ME_FACTION)
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, "Infiltrate {}'s base".format(self.elements[ME_FACTION]),
            (self.elements["LOCALE"], self.elements["MISSION_GATE"]),
            enemy_faction=villain, rank=self.rank,
            objectives=(missionbuilder.BAMO_CAPTURE_BUILDINGS,missionbuilder.BAMO_LOCATE_ENEMY_FORCES),
            cash_reward=500, experience_reward=250, one_chance=False,
            win_message = "Having captured their base, you can begin searching for information.".format(self.elements[ME_FACTION]),
        )
        missionbuilder.NewMissionNotification(self.mission_seed.name, self.elements["MISSION_GATE"])

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

    def t_START(self,camp):
        if self.elements[ME_PERSON].is_destroyed():
            if not self.mission_seed:
                if self.card:
                    mycard = self.elements[mechtarot.ME_CARD]
                    mysocket = self.elements[mechtarot.ME_SOCKET]
                    if CONSEQUENCE_LOSE in mysocket.consequences:
                        mysocket.consequences[CONSEQUENCE_LOSE](camp, mycard, self.card)
                self.end_plot(camp)
            elif self.mission_seed.is_won():
                villain = self.card.elements.get(ME_FACTION) or self.elements.get(ME_FACTION) or "Someone"
                verb = self.card.elements.get(ME_CRIMED) or self.elements.get(ME_CRIMED) or "did terrible things"
                pbge.alert("While searching the base, you discover proof that {} {}.".format(villain,verb))
                self._win_investigation(camp)

    def _win_investigation(self,camp):
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        if CONSEQUENCE_WIN in mysocket.consequences:
            mysocket.consequences[CONSEQUENCE_WIN](camp,mycard,self.card)
        self.end_plot(camp)



#   ******************************
#   ***  MT_SOCKET_SearchClue  ***
#   ******************************
#
#   METROSCENE
#   METRO
#   MISSION_GATE
#   ME_CARD
#   ME_SOCKET

class LibraryScience2099(Plot):
    # - We have a puzzle item? Just search it.
    LABEL = "MT_SOCKET_SearchClue"
    active = True
    scope = "METRO"

    @classmethod
    def matches( cls, pstate ):
        """Returns True if this plot matches the current plot state."""
        return ME_PUZZLEITEM in pstate.elements

    def ME_PUZZLEITEM_menu(self, camp, thingmenu):
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysig = mysocket.get_activating_signals(mycard, camp)

        if mysig:
            self.card = mysig[0][0]
            subject = self.card.elements.get(ME_CRIME) or self.elements.get(ME_CRIME) or "illegal activities"
            thingmenu.add_item("Search for {}".format(subject),self._win_mission)

    def _win_mission(self,camp):
        verb = self.card.elements.get(ME_CRIMED) or self.elements.get(ME_CRIMED) or "did terrible things"
        pbge.alert("You discover evidence that {} {}.".format(self.elements[ME_FACTION],verb))
        mycard = self.elements[mechtarot.ME_CARD]
        mysocket = self.elements[mechtarot.ME_SOCKET]
        mysocket.consequences[CONSEQUENCE_WIN](camp,mycard,self.card)
        self.end_plot(camp)


