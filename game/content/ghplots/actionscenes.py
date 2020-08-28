from pbge.plots import Plot
import game
import gears
import pbge
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints, plotutility, dungeonmaker



#   **********************
#   ***  FENIX_CASTLE  ***
#   **********************
#
# A recurring battle outside of a scene entrance. After however many victories, the player may get a reward.
#
#  Inherited Elements:
#    CASTLE_NAME: Give a name to the destination
#    ENEMY_FACTION: The attacker of the castle. If None, a random faction may be created.
#    MISSION_GATE:  For entering this scene after it's been activated.
#    METROSCENE: The city/town where this takes place.
#    METRO: The scope.
#
#  Signals:
#    LOSE:  Send this trigger when the party faints out of the scene.
#    WIN: Send this trigger when the fortification is destroyed.
#

class STC_FenixCastle( Plot ):
    LABEL = "FENIX_CASTLE"
    active = False
    scope = "METRO"
    def custom_init( self, nart ):
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(50,50,plotutility.random_deadzone_spot_name(),player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, game.content.gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", dident="METROSCENE")

        if not self.elements.get("ENEMY_FACTION"):
            self.register_element("ENEMY_FACTION", plotutility.RandomBanditCircle(nart.camp))

        self.register_element("_EROOM",pbge.randmaps.rooms.OpenRoom(6,6,anchor=random.choice(pbge.randmaps.anchors.EDGES)),dident="LOCALE")
        destination,entrance = self.elements["MISSION_GATE"].scene, self.elements["MISSION_GATE"]
        myent = self.register_element( "ENTRANCE", game.content.ghwaypoints.Exit(dest_scene=destination,dest_entrance=entrance,anchor=pbge.randmaps.anchors.middle), dident="_EROOM")

        castle_room = self.register_element("CASTLE_ROOM",pbge.randmaps.rooms.FuzzyRoom(10,10,anchor=pbge.randmaps.anchors.middle),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="CASTLE_ROOM")
        #myunit = gears.selector.RandomMechaUnit(level=self.rank,strength=150,fac=self.elements["ENEMY_FACTION"],env=myscene.environment)
        #team2.contents += myunit.mecha_list

        self.mission_entrance = (myscene,myent)
        self.next_update = 0
        self.encounters_on = True

        return True

    def MISSION_GATE_menu(self, camp, thingmenu):
        thingmenu.add_item("Go to {}".format(self.elements["CASTLE_NAME"]), self.go_to_castle)

    def go_to_castle(self, camp):
        camp.destination, camp.entrance = self.mission_entrance

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        myteam: game.teams.Team = self.elements["_eteam"]
        if self.encounters_on and camp.day > self.next_update and len(myteam.get_members_in_play(camp)) < 1:
            camp.scene.deploy_team(
                gears.selector.RandomMechaUnit(level=self.rank,strength=150,fac=self.elements["ENEMY_FACTION"],
                                               env=self.elements["LOCALE"].environment).mecha_list, myteam
            )
            self.next_update = camp.day + 5
            self.rank += random.randint(1,6)
        else:
            dungeonmaker.dungeon_cleaner(self.elements["LOCALE"])

    def t_ENDCOMBAT(self,camp):
        # If the player team gets wiped out, end the mission.
        myteam = self.elements["_eteam"]
        if len(myteam.get_members_in_play(camp)) < 1:
            camp.check_trigger("WIN",self)
            camp.dole_xp(100)
        elif not camp.first_active_pc():
            camp.destination, camp.entrance = self.elements["MISSION_GATE"].scene, self.elements["MISSION_GATE"]
            camp.check_trigger("LOSE",self)





