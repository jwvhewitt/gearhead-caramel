from pbge.plots import Plot
import game
import gears
import pbge
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints

class DZDIntro_GetInTheMekShimli(Plot):
    # Start of the DZD Intro. Meet the sheriff of the dead zone town you're protecting. Go into battle.
    LABEL = "DZD_INTRO"
    active = True
    scope = True
    def custom_init( self, nart ):
        """An empty map that will add subplots for the mission's objectives."""
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")

        myscene = gears.GearHeadScene(15,15,"Mecha Hangar",player_team=team1,scale=gears.scale.HumanScale,civilian_team=team2)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, gharchitecture.IndustrialBuilding(floor_terrain=ghterrain.GrateFloor))
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True)

        # Start a new adventure for this plot and its children- the intro will be disposed of when it's finished.
        self.adv = pbge.plots.Adventure(world=myscene)

        myroom = self.register_element("_EROOM",pbge.randmaps.rooms.ClosedRoom(10,7),dident="LOCALE")
        myent = self.register_element( "ENTRANCE", game.content.ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="_EROOM")
        myroom.contents.append(ghwaypoints.BoardingChute())
        myroom.contents.append(ghwaypoints.ClosedBoardingChute())
        myroom.contents.append(ghwaypoints.VentFan())


        npc = self.register_element("SHERIFF",
                            gears.selector.random_character(55, local_tags=self.elements["LOCALE"].attributes,
                                                            job=gears.jobs.ALL_JOBS["Sheriff"]))
        npc.place(myscene, team=team2)

        self.elements["DZ_TOWN_NAME"] = self.generate_town_name()

        self.mission_entrance = (myscene,myent)
        self.started_the_intro = False

        return True

    TOWN_NAME_PATTERNS = ("Fort {}","{} Fortress","{} Oasis","{} Village","New {}", "{}'s End", "{}", "Mount {}",
                          "{} Hamlet", "Castle {}", "Nova {}", "{} Ruins", "Old {}", "{} Haven", "{} Spire")
    def generate_town_name(self):
        return random.choice(self.TOWN_NAME_PATTERNS).format(gears.selector.DEADZONE_TOWN_NAMES.gen_word())

    def t_START(self,camp):
        if camp.scene is self.elements["LOCALE"] and not self.started_the_intro:
            # Make sure the PC has a mecha.
            mek = camp.get_pc_mecha(camp.pc)
            if not mek:
                mek = gears.selector.MechaShoppingList.generate_single_mecha(camp.pc.renown)
                camp.assign_pilot_to_mecha(camp.pc,mek)
                camp.party.append(mek)

            pbge.alert("You have spent the past few weeks in the deadzone community {}, helping the sheriff {} defend the town against raiders. Things have not been going well.".format(self.elements["DZ_TOWN_NAME"], self.elements["SHERIFF"]))

            npc = self.elements["SHERIFF"]
            ghdialogue.start_conversation(camp,camp.pc,npc)

            #self.started_the_intro = True

    def SHERIFF_offers(self,camp):
        mylist = list()
        if camp.scene is self.elements["LOCALE"]:
            pass


        return mylist

    def t_ENDCOMBAT(self,camp):
        # If the player team gets wiped out, end the mission.
        if not camp.first_active_pc():
            self.end_the_mission(camp)

    def end_the_mission(self,camp):
        camp.destination, camp.entrance = self.elements["ADVENTURE_RETURN"]
        self.adv.end_adventure(camp)

class DZDIntroMission( Plot ):
    # Set up the decoy story for Dead Zone Drifter.
    LABEL = "DZD_INTRO_MISSION"
    active = True
    scope = True
    def custom_init( self, nart ):
        """An empty map that will add subplots for the mission's objectives."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(50,50,"Combat Zone",player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, game.content.gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True)

        self.register_element("_EROOM",pbge.randmaps.rooms.OpenRoom(5,5,anchor=random.choice(pbge.randmaps.anchors.EDGES)),dident="LOCALE")
        myent = self.register_element( "ENTRANCE", game.content.ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="_EROOM")



        self.mission_entrance = (myscene,myent)
        self.started_the_intro = False

        return True

    def t_START(self,camp):
        if camp.scene is self.elements["LOCALE"] and not self.started_the_intro:
            pass
            self.started_the_intro = True

    def t_ENDCOMBAT(self,camp):
        # If the player team gets wiped out, end the mission.
        if not camp.first_active_pc():
            self.end_the_mission(camp)

    def end_the_mission(self,camp):
        camp.destination, camp.entrance = self.elements["ADVENTURE_RETURN"]
        self.adv.end_adventure(camp)
