# This unit contains support plots for tarot cards.
from pbge.plots import Plot, PlotState
import game.content.ghwaypoints
import game.content.ghterrain
import gears
import pbge
from game import teams,ghdialogue
from game.ghdialogue import context
import random
from pbge.dialogue import ContextTag,Offer
from . import dd_main
from . import dd_tarot
from game.content import mechtarot
import game.content.plotutility
import game.content.gharchitecture
from . import dd_combatmission
import collections



#  *******************************
#  ***   DZD_SplinterFaction   ***
#  *******************************
#  Create the splinter faction's circle, add at least one NPC belonging to the faction, and set the ability to
#  reveal the card.
#
#  Elements:
#    FACTION: A circle created by this plot.
#
#  Signals:
#    WIN: Send this trigger when it's time to reveal the tarot card.
#

class SpFa_MilitarySplinter(Plot):
    LABEL = "DZD_SplinterFaction"
    active = True
    scope = True

    @classmethod
    def matches( cls, pstate ):
        """Returns True if this plot matches the current plot state."""
        return "LOCALE" in pstate.elements and pstate.elements["LOCALE"].faction and "METRO" in pstate.elements and "MISSION_GATE" in pstate.elements

    def custom_init(self, nart):
        # Step one: Determine the military faction that will be the basis of our splinter.
        city = self.elements["LOCALE"]
        city_fac = city.faction
        if city_fac in nart.camp.faction_relations:
            candidates = [fac for fac in nart.camp.faction_relations[city_fac].allies if gears.tags.Military in fac.factags]
            if candidates:
                myfac = random.choice(candidates)
                mycircle = self.register_element("FACTION",gears.factions.Circle(myfac))
                if myfac in nart.camp.faction_relations and nart.camp.faction_relations[myfac].enemies:
                    hated_fac = random.choice(nart.camp.faction_relations[myfac].enemies)
                    hated_origin = random.choice(hated_fac.LOCATIONS)
                    if hated_origin not in myfac.LOCATIONS:
                        self.hates = hated_origin
                    else:
                        self.hates = None
                else:
                    self.hates = None
                self.add_sub_plot(nart,"PLACE_LOCAL_REPRESENTATIVES")
                # Add at least one loyalist, too.
                self.add_sub_plot(nart,"PLACE_LOCAL_REPRESENTATIVES",spstate=PlotState(elements={"FACTION":myfac}).based_on(self))

            self.adventure_seed = None
            self.mission_giver = None
            return bool(candidates)

    def register_adventure(self,camp):
        self.adventure_seed = dd_combatmission.CombatMissionSeed(camp, "Mission for {}".format(self.elements["FACTION"]),
                                                                 (self.elements["LOCALE"], self.elements["ENTRANCE"]),
                                                enemy_faction=None, allied_faction=self.elements["FACTION"], include_war_crimes=True)
        self.memo = "{} sent you to do a mysterious mecha mission for {}.".format(self.mission_giver,self.elements["FACTION"])

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

        if npc.faction is self.elements["FACTION"]:
            if not self.adventure_seed:
                if self.hates in camp.pc.personality:
                    # No mission for you, foreigner.
                    goffs.append(Offer("Not for you; {} doesn't need the help of your kind.".format(self.elements["FACTION"]),context=ContextTag([context.MISSION,]),effect=self._no_mission_for_you))
                else:
                    self.mission_giver = npc
                    goffs.append(Offer("As you know, {} is responsible for keeping {} safe. We have a mission coming up, and I could use your help.".format(self.elements["FACTION"],self.elements["LOCALE"]),context=ContextTag([context.MISSION,]),subject=self,subject_start=True))
                    goffs.append(Offer("[GOOD] Report to the combat zone as quickly as possible; we will inform you of the mission objectives as soon as you arrive.",context=ContextTag([context.ACCEPT,]),subject=self,effect=self.register_adventure))
                    goffs.append(Offer("Don't think I will forget this.",context=ContextTag([context.DENY,]),subject=self))
        elif self.hates in npc.personality:
            goffs.append(Offer("[BeCarefulOfSubject]; they say they're protecting {}, but really they've turned into a hate club. They want to get rid of all of us outsiders.".format(self.elements["LOCALE"]),
                               data={"subject":str(self.elements["FACTION"])},
                               context=ContextTag([context.INFO, ]), effect=self._no_mission_for_you, subject=str(self.elements["FACTION"])))
        return goffs

    def _no_mission_for_you(self,camp):
        """

        :type camp: gears.GearHeadCampaign
        """
        camp.check_trigger("WIN",self)
        self.end_plot(camp)


#  *************************
#  ***   DZD_WarCrimes   ***
#  *************************
#  Discover war crimes committed by someone.
#
#  Inherited Elements:
#    CARD_FACTION: The committer of the atrocities. May be None.
#
#  Elements Set:
#    ME_CRIME, ME_CRIMED: Noun and verb forms of the war crime committed
#
#  Signals:
#    WIN: Send this trigger when the crimes are revealed to the player.
#

class LunarRefugeeLost( Plot ):
    LABEL = "DZD_WarCrimes"
    active = True
    scope = True

    # Meet a Lunar refugee who got separated from their group.
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        enemy_fac = self.elements.get(dd_tarot.ME_FACTION)
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene)

        mynpc = self.register_element("NPC",gears.selector.random_character(rank=random.randint(self.rank-10,self.rank+10),local_tags=(gears.personality.Luna,)),dident="_DEST")
        destscene.local_teams[mynpc] = destscene.civilian_team

        self.register_element(dd_tarot.ME_CRIME,"the destruction of a Lunar refugee camp")
        self.register_element(dd_tarot.ME_CRIMED,"destroyed {}'s refugee camp".format(mynpc))

        sp = self.add_sub_plot(nart,"WAR_CRIME_WITNESS",spstate=PlotState(elements={"FACTION":enemy_fac,"MISSION_RETURN":(self.elements["LOCALE"],self.elements["MISSION_GATE"])}).based_on(self),ident="MISSION")
        self.mission_accepted = False
        self.mission_finished = False
        self.got_rumor = False

        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if camp.scene.get_root_scene() is self.elements["LOCALE"] and npc is not self.elements["NPC"]:
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
            if not self.mission_finished:
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
            self.elements["NPC"].relationship.expectation = gears.relationships.E_AVENGER
            self.elements["NPC"].relationship.role = gears.relationships.R_ACQUAINTANCE
        self.end_plot(camp)

    def _accept_mission(self,camp):
        self.mission_accepted = True
        self.elements["NPC"].relationship.reaction_mod += random.randint(1,50)
        self.memo = "{} at {} asked you to investigate what happened to {} refugee camp.".format(self.elements["NPC"],self.elements["_DEST"],self.elements["NPC"].gender.possessive_determiner)

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_accepted and not self.mission_finished:
            thingmenu.add_item("Investigate {}'s village".format(self.elements["NPC"]), self._go_to_mission)

    def _go_to_mission(self,camp):
        self.subplots["MISSION"].start_mission(camp)

    def MISSION_WIN(self,camp):
        if not self.mission_finished:
            enemy_fac = self.elements.get(dd_tarot.ME_FACTION)
            if enemy_fac:
                pbge.alert("You approach the campsite of the Lunar refugees, and see that it has been utterly destroyed by {}.".format(enemy_fac))
            else:
                pbge.alert("You approach the campsite of the Lunar refugees, and see that it has been utterly destroyed.")
            camp.check_trigger("WIN", self)
            self.mission_finished = True

    def MISSION_END(self,camp):
        self.MISSION_WIN(camp)


#  *** OLD PLOTS - MAYBE NOT USEFUL ANYMORE? ***

#  **************************
#  ***   DZD_LostPerson   ***
#  **************************
#
#  Elements:
#   PERSON: The NPC or prop who is lost. This element should be placed.
#   GOALSCENE: The scene where the NPC can be found.

class LostPersonRadioTower( Plot ):
    LABEL = "DZD_LostPerson"
    def custom_init( self, nart ):
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(35,35,"Radio Tower Area",player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, game.content.gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )
        myscene.exploration_music = 'Lines.ogg'
        myscene.combat_music = 'Late.ogg'

        mygoal = self.register_element("_goalroom",pbge.randmaps.rooms.FuzzyRoom(10,10,parent=myscene,anchor=pbge.randmaps.anchors.middle))

        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(10,10,"Radio Tower Interior",player_team=team1,civilian_team=team2,scale= gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, game.content.gharchitecture.DefaultBuilding())
        self.register_scene( nart, intscene, intscenegen, ident="GOALSCENE" )

        introom = self.register_element('_introom', pbge.randmaps.rooms.OpenRoom(7, 7, anchor=pbge.randmaps.anchors.middle, decorate=pbge.randmaps.decor.OmniDec(win=game.content.ghterrain.Window)), dident="GOALSCENE")
        self.move_element(self.elements["PERSON"],introom)
        intscene.local_teams[self.elements["PERSON"]] = team2
        self.register_element('WAYPOINT', game.content.ghwaypoints.RetroComputer(), dident="_introom")

        world_scene = self.elements["WORLD"]

        wm_con = game.content.plotutility.WMCommTowerConnection(self, world_scene, myscene)
        if random.randint(1,3) != 1:
            wm_con.room1.tags = (dd_main.ON_THE_ROAD,)
        int_con = game.content.plotutility.IntCommTowerConnection(self, myscene, intscene, room1=mygoal, room2=introom)

        tplot = self.add_sub_plot(nart, "DZD_MECHA_ENCOUNTER", spstate=PlotState().based_on(self,{"ROOM":mygoal}), necessary=False)
        return True

#  *******************************
#  ***   DZD_MECHA_ENCOUNTER   ***
#  *******************************
#
#  Elements:
#   LOCALE: The scene where the encounter will take place
#   ROOM: The room where the encounter will take place
#

class RandoMechaEncounter( Plot ):
    # Fight some factionless mecha. What do they want? To pad the adventure.
    LABEL = "DZD_MECHA_ENCOUNTER"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        myroom = self.elements["ROOM"]
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        team2.contents += gears.selector.RandomMechaUnit(self.rank,100,None,myscene.environment).mecha_list
        return True

#  **********************************
#  ***   DZD_CriminalEnterprise   ***
#  **********************************
#
# Add a hive of scum and villany to the game world.
# This place should include an OFFICE, where secret stuff might be hidden.
#

class BanditBase( Plot ):
    LABEL = "DZD_CriminalEnterprise"
    active = True
    scope = True

    def custom_init(self, nart):
        # Create the outer grounds with the bandits and their leader.
        mybandits = game.content.plotutility.RandomBanditCircle()
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(35,35,"Bandit Base Area",player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, game.content.gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )

        # Add the connection to the world map.
        mycon = game.content.plotutility.WMConcreteBuildingConnection(self, self.elements["WORLD"], myscene, door2_id="_exit")
        if random.randint(1,10) == 1:
            mycon.room1.tags = (dd_main.ON_THE_ROAD,)

        # Add the goal room and the bandits guarding it.
        mygoal = self.register_element("_goalroom",pbge.randmaps.rooms.FuzzyRoom(10,10,parent=myscene))
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,),faction=mybandits),dident="_goalroom")
        my_unit = gears.selector.RandomMechaUnit(self.rank,100,mybandits,myscene.environment,add_commander=True)
        team2.contents += my_unit.mecha_list
        self.register_element("_commander",my_unit.commander)
        self.intro_ready = True

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        dimdiff = max(random.randint(0,4),random.randint(0,4))
        if random.randint(1,2) == 1:
            dimdiff = -dimdiff
        intscene = gears.GearHeadScene(35,35,"Bandit Base",player_team=team1,civilian_team=team2,scale= gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, game.content.gharchitecture.DefaultBuilding())
        self.register_scene( nart, intscene, intscenegen, ident="_interior" )
        introom = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(10 + dimdiff, 10 - dimdiff, anchor=pbge.randmaps.anchors.south, decorate=pbge.randmaps.decor.OmniDec(win=game.content.ghterrain.Window)), dident="_interior")

        mycon2 = game.content.plotutility.IntConcreteBuildingConnection(self, myscene, intscene, room1=mygoal, room2=introom)

        introom2 = self.register_element('OFFICE', pbge.randmaps.rooms.ClosedRoom(random.randint(7,10), random.randint(7,10), decorate=pbge.randmaps.decor.OmniDec(win=game.content.ghterrain.Window)), dident="_interior")

        return True
    def _eteam_ACTIVATETEAM(self,camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False
    def _commander_offers(self,camp):
        mylist = list()
        mylist.append(Offer("This area is under the control of {}. Leave now or we'll [threat].".format(str(self.elements["_eteam"].faction)),
            context=ContextTag([context.ATTACK,])))
        mylist.append(Offer("[CHALLENGE]",
            context=ContextTag([context.CHALLENGE,]),  ))
        mylist.append(Offer("[WITHDRAW]",
            context=ContextTag([context.WITHDRAW,]), effect=self._withdraw ))
        return mylist
    def _withdraw(self,camp):
        myexit = self.elements["_exit"]
        myexit.unlocked_use(camp)

#  *****************************
#  ***   DZD_LocalBusiness   ***
#  *****************************
#
# A local business venture that has limited relevance for the player character.
# LOCALE = The location of the business.

class LB_Cheesery(Plot):
    LABEL = "DZD_LocalBusiness"
    active = True
    scope = True
    def custom_init( self, nart ):
        # Create a building within the town.
        building = self.register_element("_EXTERIOR", game.content.ghterrain.ScrapIronBuilding(waypoints={"DOOR": game.content.ghwaypoints.ScrapIronDoor()}), dident="TOWN")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35,35,"Cheesery",player_team=team1,civilian_team=team2,scale= gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, game.content.gharchitecture.MakeScrapIronBuilding())
        self.register_scene( nart, intscene, intscenegen, ident="LOCALE" )
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south, decorate=game.content.gharchitecture.CheeseShopDecor()), dident="LOCALE")

        mycon2 = game.content.plotutility.TownBuildingConnection(self, self.elements["TOWN"], intscene, room1=building, room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        # Generate a criminal enterprise of some kind.
        #cplot = self.add_sub_plot(nart, "DZD_CriminalEnterprise")

        return True



#  ***************************
#  ***   DZD_RevealBadge   ***
#  ***************************

class RB_CatchTheRaiders( Plot ):
    LABEL = "DZD_RevealBadge"
    active = True
    scope = True
    def custom_init( self, nart ):
        # Add an NPC to the town that needs a sheriff. This NPC will offer the mission.
        npcplot = self.add_sub_plot(nart, "DZD_LocalBusiness")

        # Generate a criminal enterprise of some kind.
        #cplot = self.add_sub_plot(nart, "DZD_CriminalEnterprise")

        return True


#  **************************
#  ***   DZD_RevealClue   ***
#  **************************

class SubcontractedCrime( Plot ):
    LABEL = "DZD_RevealClue"
    active = True
    scope = True
    def custom_init( self, nart ):
        # Create a filing cabinet or records computer for the PUZZLEITEM
        my_item = self.register_element("PUZZLEITEM", game.content.ghwaypoints.RetroComputer(plot_locked=True))

        # Generate a criminal enterprise of some kind.
        cplot = self.add_sub_plot(nart, "DZD_CriminalEnterprise")

        # Seek the OFFICE, and stick the filing thing in there.
        self.elements["_room"] = cplot.elements["OFFICE"]
        self.move_element(my_item,self.elements["_room"])

        return True
    def PUZZLEITEM_BUMP(self,camp):
        # Encountering the corpse will reveal the murder.
        camp.check_trigger("WIN",self)
    def PUZZLEITEM_menu(self,camp,thingmenu):
        thingmenu.desc = "{} It seems to contain records belonging to {}.".format(thingmenu.desc,self.elements.get("PERSON"))


#  ****************************
#  ***   DZD_RevealMurder   ***
#  ****************************
#
#  Elements:
#   PERSON: The NPC being done away with.
#

class HideAndSeekWithACorpse( Plot ):
    LABEL = "DZD_RevealMurder"
    active = True
    scope = True
    def custom_init( self, nart ):
        mynpc = self.elements["PERSON"]
        mycorpse = self.register_element('PERSON', game.content.ghwaypoints.Victim(plot_locked=True, name=mynpc.name))
        self.register_element('_the_deceased',mynpc)
        tplot = self.add_sub_plot(nart, "DZD_LostPerson")
        self.elements["GOALSCENE"] = tplot.elements.get("GOALSCENE")
        self.intro_ready = True
        return True
    def PERSON_BUMP(self,camp):
        # Encountering the corpse will reveal the murder.
        camp.check_trigger("WIN",self)
        self.elements["PERSON"].remove(self.elements["GOALSCENE"])
    def PERSON_menu(self,camp,thingmenu):
        thingmenu.desc = "You find the body of {}, obviously murdered.".format(self.elements["_the_deceased"])
    def GOALSCENE_ENTER(self,camp):
        if self.intro_ready:
            #pbge.alert("You found the goalscene.")
            self.intro_ready = False