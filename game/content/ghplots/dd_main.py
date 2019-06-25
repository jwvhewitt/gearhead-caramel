import gears
from pbge.plots import Plot, Adventure, NarrativeRequest
import game.content.ghwaypoints
import game.content.ghterrain
import pbge
from pbge.dialogue import Offer,ContextTag
from game import teams,ghdialogue
from game.ghdialogue import context
import pygame
import random
import game.content.ghplots.dd_tarot
import game.content.mechtarot
import game.content.plotutility
import game.content.gharchitecture
from game.content import PLOT_LIST

# Room tags
ON_THE_ROAD = "ON_THE_ROAD" # This location is connected to the highway, if appropriate.

class DeadzoneDrifterStub( Plot ):
    LABEL = "SCENARIO_DEADZONEDRIFTER"
    active = True
    scope = True
    # Creates a DeadZone Drifter adventure.
    # - Start by creating the "home base" city that the player character will leave from.

    def custom_init( self, nart ):
        """Create Wujung."""
        wplot = self.add_first_locale_sub_plot( nart, locale_type="DZD_INTRO" )

        return True

    def _get_generic_offers( self, npc, camp ):
        """

        :type camp: gears.GearHeadCampaign
        :type npc: gears.base.Character
        """
        mylist = list()
        if npc.relationship and gears.relationships.RT_LANCEMATE in npc.relationship.tags and camp.can_add_lancemate() and npc not in camp.party:
            # If the NPC has the lancemate tag, they might join the party.
            mylist.append(Offer("[JOIN]",
                                context=ContextTag([context.JOIN]), effect=ghdialogue.AutoJoiner(npc)))

        return mylist


class AdventureTestStub( Plot ):
    # Initial: 43.1 kB
    LABEL = "SCENARIO_ADVENTURETEST"
    active = True
    scope = True

    def custom_init( self, nart ):
        """Create the world + starting scene."""
        wplot = self.add_first_locale_sub_plot( nart, locale_type="DZD_WORLD" )

        xit = wplot.elements.get("EXIT")
        self.register_element( "MACGUFFIN", xit )
        xit.plot_locked = True

        home_scene = self.register_element("HOME_SCENE",wplot.elements["LOCALE"])
        home_base = self.register_element("HOME_BASE",wplot.elements["ENTRANCE"])

        return True

    def MACGUFFIN_menu(self,camp,thingmenu):
        thingmenu.desc = "This exit leads to a world of infinite adventure. Do you want to go there?"
        thingmenu.add_item("Sure, why not.",self.start_adventure)
        thingmenu.add_item("No thanks.",None)
    def start_adventure(self,camp):
        init = pbge.plots.PlotState(rank=1,elements={"ADVENTURE_EXIT":(self.elements["HOME_SCENE"],self.elements["HOME_BASE"])})
        nart = NarrativeRequest(camp,init,adv_type="TEST_ADVENTURE",plot_list=PLOT_LIST)
        if nart.story:
            nart.build()
            #nart.story.start(camp)
            camp.check_trigger('UPDATE')
        else:
            pbge.alert("Narrative build failed. Bummer.")

class TheBigTest(Plot):
    LABEL = "TEST_ADVENTURE"
    active = True
    scope = True

    def custom_init( self, nart ):
        """Create the world + starting scene."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(35,35,"Starting Area",player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, game.content.gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True )
        self.adv = Adventure(world=myscene)

        myroom = self.register_element("_ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5),dident="LOCALE")
        mydest = self.register_element("_ROOM2",pbge.randmaps.rooms.FuzzyRoom(3,3),dident="LOCALE")
        myent = self.register_element( "ENTRANCE", game.content.ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="_ROOM")
        myexit = self.register_element( "EXIT", game.content.ghwaypoints.Exit(name="Exit Scenario", anchor=pbge.randmaps.anchors.middle, plot_locked=True), dident="_ROOM2")
        self.entered_adventure = False

        return True

    def t_UPDATE(self,camp):
        if not self.entered_adventure:
            camp.destination = self.elements["LOCALE"]
            camp.entrance = self.elements["ENTRANCE"]
            self.entered_adventure = True

    def EXIT_menu(self,camp,thingmenu):
        thingmenu.desc = "This is the end of the adventure. Are you ready to go?"
        thingmenu.add_item("Sure, why not.",self.end_adventure)
        thingmenu.add_item("No thanks.",None)

    def end_adventure(self, camp):
        self.adv.end_adventure(camp)
        camp.destination,camp.entrance = self.elements["ADVENTURE_EXIT"]

class OldDeadzoneDrifterStub( Plot ):
    LABEL = "zzzSCENARIO_DEADZONEDRIFTER"
    # Creates a DeadZone Drifter adventure.
    # - Create a patch of DeadZone to act as the "world"
    # - Add a village, including random cards for village resources
    # - Add a Threat card
    # - Add the defenses and weakness to the Threat
    # -

    def custom_init( self, nart ):
        """Create the world + starting scene."""
        self.adv = Adventure(world=nart.camp)
        wplot = self.add_first_locale_sub_plot( nart, locale_type="DZD_WORLD" )
        w = wplot.elements.get("LOCALE")
        self.adv.world = w
        self.register_element( "WORLD", w )

        # Add the village in trouble.
        tplot = self.add_sub_plot( nart, "DZD_VILLAGE" )
        town = tplot.elements.get("LOCALE")
        self.register_element( "TOWN", town )

        threat_card = nart.add_tarot_card(self, (game.content.ghplots.dd_tarot.MT_THREAT,), )
        game.content.mechtarot.Constellation(nart, self, threat_card, threat_card.get_negations()[0], steps=3)

        return True


class DeadzoneHighwaySceneGen( pbge.randmaps.SceneGenerator ):
    DO_DIRECT_CONNECTIONS = False
    def connect_contents( self, gb, archi ):
        # Generate list of rooms.
        all_rooms = [r for r in self.contents if hasattr(r,"area")]
        road_rooms = list()
        side_rooms = list()
        for r in all_rooms:
            if ON_THE_ROAD in r.tags:
                road_rooms.append(r)
            else:
                side_rooms.append(r)

        random.shuffle(road_rooms)
        connected = list()
        connected.append( road_rooms.pop() )
        road_rooms.sort(key=lambda r: gb.distance(r.area.center,connected[0].area.center))

        room = connected[0]
        if room.anchor:
            mydest = room.anchor(room.area,None)
            self.draw_L_connection( gb, room.area.centerx, room.area.centery, mydest[0], mydest[1], archi )

        # Process them
        for room in list(road_rooms):
            road_rooms.remove(room)
            dest = min(connected, key=lambda r: gb.distance(r.area.center,room.area.center))
            self.draw_L_connection( gb, room.area.centerx, room.area.centery, dest.area.centerx, dest.area.centery, archi )
            connected.append(room)
            if room.anchor:
                mydest = room.anchor(room.area, None)
                self.draw_L_connection(gb, room.area.centerx, room.area.centery, mydest[0], mydest[1], archi)

        for room in side_rooms:
            dest = random.choice(connected)
            self.draw_direct_connection(gb,room.area.centerx, room.area.centery, dest.area.centerx, dest.area.centery, archi )
            connected.append(room)

    def draw_L_connection( self, gb, x1,y1,x2,y2, archi ):
        if random.randint(1,2) == 1:
            cx,cy = x1,y2
        else:
            cx,cy = x2,y1
        self.draw_road_connection( gb, x1, y1, cx, cy, archi )
        self.draw_road_connection( gb, x2, y2, cx, cy, archi )

    def draw_road_connection( self, gb, x1,y1,x2,y2, archi ):
        path = pbge.scenes.animobs.get_line( x1,y1,x2,y2 )
        for p in path:
            gb.fill(pygame.Rect(p[0]-1,p[1]-1,3,3), floor=game.content.ghterrain.DeadZoneGround, wall=None)
            gb.set_decor(p[0], p[1], game.content.ghterrain.WorldMapRoad)


class SomewhereOnTheHighway( Plot ):
    LABEL = "DZD_WORLD"
    def custom_init( self, nart ):
        """Create map, fill with city + services."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(30,30,"Deadzone Highway",player_team=team1,scale=gears.scale.WorldScale)
        myscene.exploration_music = 'Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg'

        anc_a,anc_b = random.choice(pbge.randmaps.anchors.OPPOSING_CARDINALS)

        myscenegen = DeadzoneHighwaySceneGen(myscene, game.content.gharchitecture.WorldScaleDeadzone())

        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )

        myroom = self.register_element("_ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5,tags=(ON_THE_ROAD),anchor=anc_a),dident="LOCALE")
        mydest = self.register_element("_ROOM2",pbge.randmaps.rooms.FuzzyRoom(3,3,tags=(ON_THE_ROAD,),anchor=anc_b),dident="LOCALE")
        myent = self.register_element( "ENTRANCE", game.content.ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="_ROOM")
        myexit = self.register_element( "EXIT", game.content.ghwaypoints.Exit(name="Exit Scenario", anchor=pbge.randmaps.anchors.middle), dident="_ROOM2")
        return True


class BasicDeadZoneHighwayTown( Plot ):
    LABEL = "DZD_VILLAGE"

    # noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
    def custom_init( self, nart ):
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team",allies=(team1,))
        myscene = gears.GearHeadScene(50,50,"DZ Village",player_team=team1,civilian_team=team2,
                                      scale=gears.scale.HumanScale,
                                      attributes=(gears.personality.DeadZone,gears.tags.Village))
        myscene.exploration_music = 'Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg'

        npc = gears.selector.random_character(50,local_tags=myscene.attributes)
        npc.place(myscene,team=team2)

        myscenegen = pbge.randmaps.SceneGenerator(myscene, game.content.gharchitecture.HumanScaleDeadzone())

        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )

        #myscene.contents.append(ghterrain.ScrapIronBuilding(waypoints={"DOOR":ghwaypoints.ScrapIronDoor(),"OTHER":ghwaypoints.RetroComputer()}))

        wm_con = game.content.plotutility.WMDZTownConnection(self, self.elements["WORLD"], myscene)
        wm_con.room1.tags = (ON_THE_ROAD,)

        return True
