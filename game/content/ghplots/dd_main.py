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
        """Create the intro/tutorial."""
        wplot = self.add_first_locale_sub_plot( nart, locale_type="DZD_INTRO", ident="INTRO" )

        # Copy over the sheriff and the name of the town
        self.register_element("DZ_CONTACT",wplot.elements["SHERIFF"])
        self.register_element("DZ_TOWN_NAME",wplot.elements["DZ_TOWN_NAME"])

        # Add Wujung and the rest of the world.
        self.add_sub_plot(nart,"DZD_HOME_BASE",ident="HOMEBASE")

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

    def INTRO_END(self, camp):
        # Wujung should be registered as the home base, so send the player there.
        camp.destination,camp.entrance = camp.home_base
        del self.subplots["INTRO"]


# Stuff from older versions of the DZD setup... keeping them here because I might use them later.

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
