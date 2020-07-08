# This unit contains support plots for tarot cards.
from pbge.plots import Plot, PlotState
from game.content import ghwaypoints,ghterrain,plotutility,backstory
import gears
import pbge
from game import teams,ghdialogue
from game.ghdialogue import context
import random
from pbge.dialogue import ContextTag,Offer
from . import dd_customobjectives
from . import tarot_cards
from .tarot_cards import ME_FACTION,ME_PERSON,ME_CRIME,ME_PUZZLEITEM,ME_ACTOR,ME_LIABILITY,CrimeObject
import game.content.plotutility
import game.content.gharchitecture
from . import dd_combatmission
import collections
from . import missionbuilder


#   ****************************
#   ***  MT_REVEAL_BadPress  ***
#   ****************************
#
# ME_PERSON: The NPC about whom the bad press will be revealed
# ME_LIABILITY: A string containing bad info about INVESTIGATION_SUBJECT or a Liability object

class BasicBigScoop(Plot):
    LABEL = "MT_REVEAL_BadPress"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        # Place the reporter.
        if ME_ACTOR not in self.elements:
            npc = gears.selector.random_character(rank=random.randint(self.rank, self.rank+20),
                                                  local_tags=tuple(self.elements["METROSCENE"].attributes),
                                                  job=gears.jobs.ALL_JOBS["Reporter"])
            scene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])
            self.register_element(ME_ACTOR, npc, dident="LOCALE")
        if ME_PERSON not in self.elements:
            npc = gears.selector.random_character(rank=random.randint(self.rank, self.rank+20),
                                                  local_tags=tuple(self.elements["METROSCENE"].attributes),)
            scene = self.seek_element(nart, "LOCALE2", self._is_best_scene, scope=self.elements["METROSCENE"])
            self.register_element(ME_PERSON, npc, dident="LOCALE2")

        if ME_LIABILITY not in self.elements:
            self.register_element(ME_LIABILITY, "{ME_PERSON} is guilty of tax evasion".format(**self.elements))

        self.got_memo = False
        self.got_rumor = False
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def ME_ACTOR_offers(self,camp):
        mylist = list()
        mylist.append(
            Offer(
                "[HELLO] I am working on a story about about {ME_PERSON}; {ME_LIABILITY}.".format(**self.elements),
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
            mygram["[News]"] = ["{ME_ACTOR} has been investigating a story about {ME_PERSON}".format(**self.elements), ]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if npc is not self.elements[ME_PERSON] and npc is not self.elements[ME_ACTOR] and not self.got_rumor:
            mynpc = self.elements[ME_ACTOR]
            goffs.append(Offer(
                msg="As far as I know {} usually hangs out at {}.".format(mynpc,mynpc.get_scene()),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self,camp):
        mynpc = self.elements[ME_ACTOR]
        self.got_rumor = True
        self.memo = "{} at {} has been investigating {}.".format(mynpc,mynpc.get_scene(),self.elements[ME_PERSON])


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
        return (isinstance(candidate,gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes and
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


#   *****************************
#   ***  MT_REVEAL_Demagogue  ***
#   *****************************

class MediaDemagogue(Plot):
    LABEL = "MT_REVEAL_Demagogue"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        if ME_PERSON in self.elements:
            self.register_element("LOCALE",self.elements[ME_PERSON].get_scene())
        else:
            scene = self.seek_element(
                nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"],must_find=False
            )
            if not scene:
                scene = self.seek_element(nart, "LOCALE", self._is_good_scene, scope=self.elements["METROSCENE"])

            npc = self.register_element(
                ME_PERSON,
                gears.selector.random_character(
                    rank=random.randint(10, 50),job=gears.jobs.ALL_JOBS["Pundit"],
                    mecha_colors=gears.color.random_mecha_colors(),
                    local_tags=tuple(self.elements["METROSCENE"].attributes),
                ), dident="LOCALE"
            )

        metroscene = self.elements["METROSCENE"]
        self.conspiracy = backstory.Backstory(
            commands=("CONSPIRACY",), elements={"LOCALE":metroscene}, keywords=metroscene.get_keywords()
        )
        self.got_rumor = False

        return True

    def _is_best_scene(self,nart,candidate):
        return (isinstance(candidate,gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
                and gears.tags.SCENE_CULTURE in candidate.attributes)

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        mynpc = self.elements[ME_PERSON]

        if npc is not self.elements[ME_PERSON] and npc not in camp.party and not self.got_rumor:
            goffs.append(Offer(
                msg="You can speak to {ME_PERSON} at {LOCALE} if you want to find out for yourself.".format(**self.elements),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))

        return goffs

    def _get_rumor(self,camp):
        self.got_rumor = True
        self.memo = "{ME_PERSON} at {LOCALE} has been expounding a conspiracy theory.".format(**self.elements)

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if npc is not self.elements[ME_PERSON] and npc not in camp.party:
            if gears.personality.Fellowship in npc.personality:
                if not self.got_rumor:
                    mygram["[News]"] = [
                        "{ME_PERSON} has been spreading a baseless conspiracy theory".format(**self.elements), ]
            else:
                mygram["[News]"] = ["{} claims that {}".format(self.elements[ME_PERSON],self.conspiracy.get_one("rumor")), ]
        return mygram

    def ME_PERSON_offers(self,camp):
        mylist = list()
        mylist.append(Offer(
            "[HELLO] [CRYPTIC_GREETING]",
            ContextTag([context.HELLO,]),
        ))
        mylist.append(Offer(
            self.conspiracy.get("text"),
            ContextTag([context.CUSTOM,]),data={"reply":"I heard that you have some thoughts on current events?"},
            effect=self.reveal_card
        ))
        return mylist

    def reveal_card(self,camp):
        camp.check_trigger("WIN",self)
        self.end_plot(camp)

#   ***********************************
#   ***  MT_REVEAL_FactionComputer  ***
#   ***********************************

class OutsourcedComputerPlacement( Plot ):
    LABEL = "MT_REVEAL_FactionComputer"
    active = True
    scope = "METRO"

    def custom_init( self, nart ):
        mything = self.register_element(
            ME_PUZZLEITEM, ghwaypoints.RetroComputer(plot_locked=True,
            desc="You find a computer belonging to {ME_FACTION}.".format(**self.elements))
        )
        self.add_sub_plot(nart, "PLACE_THING", indie=True, elements={"THING":mything, "ENEMY_FACTION":self.elements[ME_FACTION]})
        return True

    def THING_BUMP(self, camp):
        self._win_mission(camp)

    def _win_mission(self,camp):
        self.clue_uncovered = True
        camp.check_trigger("WIN",self)
        self.end_plot(camp,True)


#   ******************************
#   ***  MT_REVEAL_FeetOfClay  ***
#   ******************************

class WidespreadDisapproval(Plot):
    LABEL = "MT_REVEAL_FeetOfClay"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        mynpc = self.elements[ME_PERSON]
        if ME_LIABILITY not in self.elements:
            # If we don't have a secret yet, figure out the effect this NPC is having on the world.
            self.elements[ME_LIABILITY] = tarot_cards.PersonalLiability(mynpc, nart.camp)

        return True

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        mynpc = self.elements[ME_PERSON]

        if npc is not self.elements[ME_PERSON] and npc not in camp.party:
            goffs.append(Offer(
                msg="[chat_lead_in] {ME_LIABILITY}. If more people knew about this, maybe something could be done.".format(**self.elements),
                context=ContextTag((context.INFO,)), effect=self.reveal_card,
                subject=str(mynpc), data={"subject": "the things {} did".format(str(mynpc))}, no_repeats=True
            ))

        return goffs

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if npc is not self.elements[ME_PERSON] and npc not in camp.party:
            mygram["[CURRENT_EVENTS]"] = ["{ME_PERSON} needs to be stopped.".format(**self.elements),]
            mygram["[News]"] = ["{ME_PERSON} has been doing horrible things.".format(**self.elements), ]
        return mygram

    def reveal_card(self,camp):
        camp.check_trigger("WIN",self)
        self.end_plot(camp, True)


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
        if npc.faction is not self.elements[tarot_cards.ME_FACTION]:
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
        if tarot_cards.ME_FACTION not in self.elements:
            self.register_element(tarot_cards.ME_FACTION, gears.factions.Circle(nart.camp, name=self._make_faction_name()))
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
        if not [npc for npc in camp.scene.contents if isinstance(npc,gears.base.Character) and npc.faction is self.elements[tarot_cards.ME_FACTION]]:
            npc = gears.selector.random_character(self.rank, faction=self.elements[tarot_cards.ME_FACTION])
            camp.scene.contents.append(npc)

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()

        if npc.faction is self.elements[tarot_cards.ME_FACTION]:
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
        if npc.faction is not self.elements[tarot_cards.ME_FACTION] and not self.won:
            mygram["[News]"] = ["{ME_FACTION} are a local hate club".format(**self.elements), ]
        if npc.faction is self.elements[tarot_cards.ME_FACTION]:
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
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

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


class PrivateInvestigator(Plot):
    LABEL = "MT_REVEAL_Investigator"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        # Place the detective.
        npc = gears.selector.random_character(rank=random.randint(self.rank, self.rank+20),
                                              mecha_colors=gears.color.random_mecha_colors(),
                                              local_tags=tuple(self.elements["METROSCENE"].attributes),
                                              job=gears.jobs.ALL_JOBS["Detective"])
        scene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])
        self.register_element(ME_PERSON, npc, dident="LOCALE")
        self.got_memo = False
        self.got_rumor = False
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def ME_PERSON_offers(self,camp):
        mylist = list()
        mylist.append(
            Offer(
                "[HELLO] [WOULD_YOU_MIND_ANSWERING_QUESTION]".format(**self.elements),
                ContextTag([context.HELLO,context.QUERY]),
            )
        )
        mylist.append(Offer(
            "I've been hired to investigate {INVESTIGATION_SUBJECT}. [YOU_SEEM_CONNECTED] Do you know anything about this?".format(**self.elements),
            ContextTag([context.QUERY,]),effect=self._reveal
        ))
        mylist.append(Offer(
            "Thanks. Any information you find could be a big help.".format(**self.elements),
            ContextTag([context.ANSWER,]),data={"reply":"I'll let you know if I hear anything."}
        ))
        mylist.append(Offer(
            "I'll be around here if you happen to change your mind.".format(**self.elements),
            ContextTag([context.ANSWER,]),data={"reply":"[NO_TO_COP]"}
        ))
        return mylist

    def _reveal(self,camp):
        camp.check_trigger("WIN",self)
        self.end_plot(camp)

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements[ME_PERSON]:
            # This is an NPC in Wujung. Give them some news.
            mygram["[News]"] = ["{ME_PERSON} has been hired to investigate {INVESTIGATION_SUBJECT}.".format(**self.elements), ]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if npc is not self.elements[ME_PERSON] and not self.got_rumor:
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
#   ***  MT_REVEAL_Murder  ***
#   **************************

class FindABody( Plot ):
    LABEL = "MT_REVEAL_Murder"
    active = True
    scope = "METRO"

    def custom_init( self, nart ):
        mything = self.register_element(
            "THING", ghwaypoints.Victim(plot_locked=True,name=gears.selector.GENERIC_NAMES.gen_word(),
                                        desc="You find a dead body. This appears to be a murder scene.")
        )
        self.add_sub_plot(nart, "PLACE_THING", indie=True)
        self.register_element(ME_CRIME,CrimeObject("the murder of {}".format(mything),"murdered {}".format(mything)))
        return True

    def THING_BUMP(self, camp):
        self._win_mission(camp)

    def _win_mission(self,camp):
        self.clue_uncovered = True
        camp.check_trigger("WIN",self)
        self.end_plot(camp,True)


#   ****************************
#   ***  MT_REVEAL_Password  ***
#   ****************************

# noinspection PyAttributeOutsideInit
class PasswordThroughCombat( Plot ):
    LABEL = "MT_REVEAL_Password"
    active = True
    scope = "METRO"

    def custom_init( self, nart ):
        # Generate a mission-giver.
        scene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])
        npc = self.register_element(
            "NPC", gears.selector.random_character(
                job=gears.jobs.ALL_JOBS["Bounty Hunter"],
                rank=random.randint(self.rank, self.rank+20),
                local_tags=tuple(self.elements["METROSCENE"].attributes)
            ), dident="LOCALE"
        )
        self.mission_seed = None
        self.got_rumor = False
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

    def t_UPDATE(self, camp):
        # If the adventure has ended, get rid of it.
        if self.mission_seed and self.mission_seed.ended:
            self.mission_seed = None

    def NPC_offers(self, camp):
        mylist = list()
        if not self.mission_seed:
            mylist.append(
                Offer(
                    "Recently there have been some unregistered mecha causing problems outside of town, and they're more than I can handle. [IWillSendMissionDetails].",
                    context=ContextTag([context.MISSION, ]), effect=self.register_adventure,
                )
            )
        return mylist

    MOBJs = (
        missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL, missionbuilder.BAMO_DEFEAT_COMMANDER,
        missionbuilder.BAMO_EXTRACT_ALLIED_FORCES, missionbuilder.BAMO_LOCATE_ENEMY_FORCES,
        missionbuilder.BAMO_RECOVER_CARGO
    )

    def register_adventure(self, camp):
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, "{}'s Mission".format(self.elements["NPC"]),
            (self.elements["METROSCENE"], self.elements["MISSION_GATE"]),
            self.elements["ME_FACTION"], rank=self.rank, objectives=random.sample(self.MOBJs, 2),
            on_win=self._win_mission,
        )
        missionbuilder.NewMissionNotification(self.mission_seed.name,self.elements["MISSION_GATE"])

    def _win_mission(self, camp):
        pbge.alert("Following the battle, you examine the enemy mecha for salvage. In the cockpit of one abandoned mek there's a paper note bearing the phrase \"{}\". You have no idea what that means.".format(self.elements["PASSWORD"]))
        self.clue_uncovered = True
        camp.check_trigger("WIN",self)
        self.end_plot(camp,True)

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if npc is not self.elements["NPC"] and not self.got_rumor:
            mygram["[News]"] = ["{NPC} is a bounty hunter who often has missions for cavaliers".format(**self.elements), ]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if npc is not self.elements["NPC"] and not self.got_rumor:
            mynpc = self.elements["NPC"]
            goffs.append(Offer(
                msg="If you want to try your luck, go to {LOCALE}. That's where {NPC} can usually be found.".format(**self.elements),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self, camp):
        self.got_rumor = True
        self.memo = "{NPC} at {LOCALE} may have a mission for you.".format(**self.elements)


#   ***************************
#   ***  MT_REVEAL_Quitter  ***
#   ***************************
#
# ME_PERSON: The NPC who quit...
# ME_FACTION: The faction that was quit.

class UnemployedQuitter(Plot):
    LABEL = "MT_REVEAL_Quitter"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        # Place the character.
        if ME_PERSON not in self.elements:
            npc = gears.selector.random_character(rank=random.randint(self.rank, self.rank+20),
                                                  local_tags=tuple(self.elements["METROSCENE"].attributes))
            self.register_element(ME_PERSON, npc)
        scene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])
        self.place_element(self.elements[ME_PERSON],scene)

        self.got_rumor = False
        self.asked_question = False
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def ME_PERSON_offers(self,camp):
        mylist = list()
        if not self.asked_question:
            mylist.append(Offer(
                "That's a difficult subject... I don't work for {ME_FACTION} anymore. I don't even want to think about them.".format(**self.elements),
                ContextTag([context.INFO,]),effect=self._ask,data={"subject":str(self.elements[ME_FACTION])},
                no_repeats=True,
            ))
        return mylist

    def _ask(self, camp):
        self.asked_question = True
        self._reveal(camp)

    def _reveal(self,camp):
        camp.check_trigger("WIN",self)
        self.got_rumor = True

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if npc is not self.elements[ME_PERSON] and not self.got_rumor:
            # This is an NPC in Wujung. Give them some news.
            mygram["[News]"] = ["{ME_PERSON} quit working for {ME_FACTION}".format(**self.elements), ]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if npc is not self.elements[ME_PERSON] and not self.got_rumor:
            mynpc = self.elements[ME_PERSON]
            goffs.append(Offer(
                msg="If you want to ask {} about {}, {} usually hangs out at {}.".format(mynpc,self.elements[ME_FACTION],mynpc.gender.subject_pronoun,mynpc.get_scene()),
                context=ContextTag((context.INFO,)), effect=self._reveal,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))
        return goffs


#   ****************************
#   ***  MT_REVEAL_TheMedia  ***
#   ****************************
#
# ME_PERSON: The media NPC
# ME_LIABILITY: A string containing bad info about INVESTIGATION_SUBJECT

class ReporterLookingForStory(Plot):
    LABEL = "MT_REVEAL_TheMedia"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        # Place the reporter.
        if ME_PERSON not in self.elements:
            npc = gears.selector.random_character(rank=random.randint(self.rank, self.rank+20),
                                                  local_tags=tuple(self.elements["METROSCENE"].attributes),
                                                  job=gears.jobs.ALL_JOBS["Reporter"])
            scene = self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])
            self.register_element(ME_PERSON, npc, dident="LOCALE")

        self.got_memo = False
        self.got_rumor = False
        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def ME_PERSON_offers(self,camp):
        mylist = list()
        mylist.append(
            Offer(
                "[HELLO] I am still looking for my next big story.",
                ContextTag([context.HELLO,]),effect=self._reveal
            )
        )
        return mylist

    def _reveal(self,camp):
        camp.check_trigger("WIN",self)

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if npc is not self.elements[ME_PERSON] and not self.got_rumor:
            # This is an NPC in Wujung. Give them some news.
            mygram["[News]"] = ["{ME_PERSON} is a reporter trying to find {ME_PERSON.gender.possessive_determiner} next big story".format(**self.elements), ]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if npc is not self.elements[ME_PERSON] and not self.got_rumor:
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
        self.memo = "{} at {} has been looking for a big story.".format(mynpc,mynpc.get_scene())


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

        self.register_element(tarot_cards.ME_CRIME, CrimeObject("the destruction of a Lunar refugee camp",
                                                                "destroyed {}'s refugee camp".format(mynpc)))

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
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

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
                enemy_fac = self.elements.get(tarot_cards.ME_FACTION)
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





