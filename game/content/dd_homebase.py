from pbge.plots import Plot, Adventure, NarrativeRequest
from pbge.dialogue import Offer,ContextTag,Cue
from .. import teams,services,ghdialogue
from ..ghdialogue import context
import gears
import gharchitecture
import pbge
import plotutility
import ghwaypoints
import ghterrain

class DZD_Wujung( Plot ):
    LABEL = "DZD_HOME_BASE"

    # noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
    def custom_init( self, nart ):
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team",allies=(team1,))
        myscene = gears.GearHeadScene(50,50,"Wujung City",player_team=team1,civilian_team=team2,
                                      scale=gears.scale.HumanScale,
                                      attributes=(gears.personality.GreenZone,gears.tags.City))
        myscene.exploration_music = 'Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg'

        npc = gears.selector.random_character(50,local_tags=myscene.attributes)
        npc.place(myscene,team=team2)

        myscenegen = pbge.randmaps.CityGridGenerator(myscene,gharchitecture.HumanScaleGreenzone(),road_terrain=ghterrain.Flagstone)

        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )

        #myscene.contents.append(ghterrain.ScrapIronBuilding(waypoints={"DOOR":ghwaypoints.ScrapIronDoor(),"OTHER":ghwaypoints.RetroComputer()}))

        myroom = self.register_element("_ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5),dident="LOCALE")
        myent = self.register_element( "ENTRANCE", ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="_ROOM")

        # Add the services.
        tplot = self.add_sub_plot( nart, "DZDHB_AlliedArmor" )

        return True

class DZD_AlliedArmor(Plot):
    LABEL = "DZDHB_AlliedArmor"

    active = True
    scope = "INTERIOR"
    def custom_init( self, nart ):
        # Create a building within the town.
        building = self.register_element("_EXTERIOR",ghterrain.BrickBuilding(waypoints={"DOOR":ghwaypoints.ScrapIronDoor(name="Allied Armor")},door_sign=(ghterrain.AlliedArmorSignEast,ghterrain.AlliedArmorSignSouth)),dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35,35,"Allied Armor",player_team=team1,civilian_team=team2,scale= gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene,gharchitecture.CommercialBuilding())
        self.register_scene( nart, intscene, intscenegen, ident="INTERIOR" )
        foyer = self.register_element('_introom',pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,decorate=gharchitecture.CheeseShopDecor()),dident="INTERIOR")
        foyer.contents.append(ghwaypoints.AlliedArmorSignWP())

        mycon2 = plotutility.TownBuildingConnection(self,self.elements["LOCALE"],intscene,room1=building,room2=foyer,door1=building.waypoints["DOOR"],move_door1=False)
        # Generate a criminal enterprise of some kind.
        #cplot = self.add_sub_plot(nart, "DZD_CriminalEnterprise")

        npc = self.register_element("SHOPKEEPER",gears.selector.random_character(50,local_tags=self.elements["LOCALE"].attributes, job=gears.jobs.ALL_JOBS["Shopkeeper"]))
        npc.place(intscene,team=team2)

        self.shop = services.Shop()

        return True

    def SHOPKEEPER_offers(self,camp):
        mylist = list()

        mylist.append(Offer("Testing the shop.",
            context=ContextTag([context.OPEN_SHOP]),effect=self.shop
            ))

        return mylist