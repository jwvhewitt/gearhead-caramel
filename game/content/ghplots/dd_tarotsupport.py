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
from game.content.ghplots import dd_main
import game.content.plotutility
import game.content.gharchitecture
import dd_combatmission


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

            self.adventure_seed = None
            self.mission_giver = None
            return bool(candidates)

    def register_adventure(self,camp):
        self.adventure_seed = dd_combatmission.CombatMissionSeed(camp, "Mission for {}".format(self.elements["FACTION"]),
                                                                 (self.elements["LOCALE"], self.elements["ENTRANCE"]),
                                                enemy_faction=None, allied_faction=self.elements["FACTION"], include_war_crimes=True)
        self.memo = "{} sent you to do a mysterious mecha mission for {}.".format(self.mission_giver,self.elements["FACTION"])

    def t_UPDATE(self,camp):
        # If the adventure has ended, get rid of it.
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

        return goffs

    def _no_mission_for_you(self,camp):
        """

        :type camp: gears.GearHeadCampaign
        """
        camp.check_trigger("WIN",self)
        self.end_plot(camp)


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