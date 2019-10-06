from pbge.plots import Plot
import game
import gears
import pbge
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed



#   **************************
#   ***  STORM_THE_CASTLE  ***
#   **************************
#
# Fairly simple combat scene against a bunch of mecha and a fortification.
#
#  Methods:
#   start_mission(camp):    Starts the mission. Pretty self-explanatory.
#
#  Inherited Elements:
#    FACTION: The committer of the atrocities. If None, a random faction may be created.
#    MISSION_RETURN:  A tuple containing the Destination, Entrance for returning the player character
#    METROSCENE: The city/town where this takes place. May be None.
#
#  Signals:
#    LOSE:  Send this trigger when the party faints out of the scene. Ignore if you want to allow multiple attempts.
#    WIN: Send this trigger when the fortification is destroyed.
#

class STC_DeadZoneFortress( Plot ):
    LABEL = "STORM_THE_CASTLE"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(50,50,"Combat Zone",player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, game.content.gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True, dident=self.elements["MISSION_RETURN"][0])

        player_a,enemy_a = random.choice(pbge.randmaps.anchors.OPPOSING_PAIRS)

        if not self.elements.get("FACTION"):
            self.register_element("FACTION",gears.factions.Circle())

        self.register_element("_EROOM",pbge.randmaps.rooms.OpenRoom(5,5,anchor=player_a),dident="LOCALE")
        destination,entrance = self.elements["MISSION_RETURN"]
        myent = self.register_element( "ENTRANCE", game.content.ghwaypoints.Exit(dest_scene=destination,dest_entrance=entrance,anchor=pbge.randmaps.anchors.middle), dident="_EROOM")

        enemy_room = self.register_element("ENEMY_ROOM",pbge.randmaps.rooms.FuzzyRoom(10,10,anchor=enemy_a),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ENEMY_ROOM")
        myunit = gears.selector.RandomMechaUnit(level=self.rank,strength=150,fac=self.elements["FACTION"],env=myscene.environment)
        team2.contents += myunit.mecha_list
        enemy_room.contents.append(ghwaypoints.SmokingWreckage())
        enemy_room.contents.append(ghwaypoints.SmokingWreckage())

        for t in range(random.randint(1,3)):
            self.add_sub_plot(nart,"MECHA_ENCOUNTER",necessary=False)

        self.mission_entrance = (myscene,myent)
        self.witness_ready = True

        return True

    def start_mission(self,camp):
        camp.destination,camp.entrance=self.elements["LOCALE"],self.elements["ENTRANCE"]

    def _eteam_ACTIVATETEAM(self,camp):
        # Activating the end fight scene will activate the win condition.
        if self.witness_ready:
            camp.check_trigger("WIN",self)
            self.witness_ready = False

    def t_ENDCOMBAT(self,camp):
        # If the player team gets wiped out, end the mission.
        myteam = self.elements["_eteam"]
        if len(myteam.get_active_members(camp)) < 1:
            camp.check_trigger("WIN",self)
            self.witness_ready = False
            self.end_the_mission(camp)
            camp.dole_xp(200)
        elif not camp.first_active_pc():
            camp.destination, camp.entrance = self.elements["MISSION_RETURN"]
            camp.check_trigger("LOSE",self)


    def end_the_mission(self,camp):
        # Restore the party at the end of the mission, then send them back to the hangar.
        camp.totally_restore_party()
        camp.destination, camp.entrance = self.elements["MISSION_RETURN"]
        camp.check_trigger("END", self)




#   ***************************
#   ***  WAR_CRIME_WITNESS  ***
#   ***************************
#
# The player will go somewhere and witness war crimes in progress. This scene may be used when the player character
# is going to discover a tragedy has unfolded, or for a defense mission where the player character will be too late
# to save the day.
#
#  Methods:
#   start_mission(camp):    Starts the mission. Pretty self-explanatory.
#
#  Inherited Elements:
#    FACTION: The committer of the atrocities. If None, a random faction may be created.
#    MISSION_RETURN:  A tuple containing the Destination, Entrance for returning the player character
#    METROSCENE: The city or location where this action scene takes place
#
#  Signals:
#    END:   The action scene has been cleared out; there's nothing left to do there.
#    LOSE:  Send this trigger when the party faints out of the scene. Probably safe to ignore most of the time.
#    WIN: Send this trigger when the crimes are revealed to the player.
#         Note: the parent plot should react in some way to let the player know what's going on,
#         since this plot just sends the trigger silently.
#


class DeadZoneRazedVillage( Plot ):
    LABEL = "WAR_CRIME_WITNESS"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(50,50,"Combat Zone",player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = pbge.randmaps.SceneGenerator(myscene, game.content.gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True, dident="METROSCENE")

        player_a,enemy_a = random.choice(pbge.randmaps.anchors.OPPOSING_PAIRS)

        if not self.elements.get("FACTION"):
            self.register_element("FACTION",gears.factions.Circle())

        self.register_element("_EROOM",pbge.randmaps.rooms.OpenRoom(5,5,anchor=player_a),dident="LOCALE")
        destination,entrance = self.elements["MISSION_RETURN"]
        myent = self.register_element( "ENTRANCE", game.content.ghwaypoints.Exit(dest_scene=destination,dest_entrance=entrance,anchor=pbge.randmaps.anchors.middle), dident="_EROOM")

        enemy_room = self.register_element("ENEMY_ROOM",pbge.randmaps.rooms.FuzzyRoom(10,10,anchor=enemy_a),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ENEMY_ROOM")
        myunit = gears.selector.RandomMechaUnit(level=self.rank,strength=150,fac=self.elements["FACTION"],env=myscene.environment)
        team2.contents += myunit.mecha_list
        enemy_room.contents.append(ghwaypoints.SmokingWreckage())
        enemy_room.contents.append(ghwaypoints.SmokingWreckage())

        for t in range(random.randint(1,3)):
            self.add_sub_plot(nart,"MECHA_ENCOUNTER",necessary=False)

        self.mission_entrance = (myscene,myent)
        self.witness_ready = True

        return True

    def start_mission(self,camp):
        camp.destination,camp.entrance=self.elements["LOCALE"],self.elements["ENTRANCE"]

    def _eteam_ACTIVATETEAM(self,camp):
        # Activating the end fight scene will activate the win condition.
        if self.witness_ready:
            camp.check_trigger("WIN",self)
            self.witness_ready = False

    def t_ENDCOMBAT(self,camp):
        # If the player team gets wiped out, end the mission.
        myteam = self.elements["_eteam"]
        if len(myteam.get_active_members(camp)) < 1:
            camp.check_trigger("WIN",self)
            self.witness_ready = False
            self.end_the_mission(camp)
            camp.dole_xp(200)
        elif not camp.first_active_pc():
            camp.destination, camp.entrance = self.elements["MISSION_RETURN"]
            camp.check_trigger("LOSE",self)


    def end_the_mission(self,camp):
        # Restore the party at the end of the mission, then send them back to the hangar.
        camp.totally_restore_party()
        camp.destination, camp.entrance = self.elements["MISSION_RETURN"]
        camp.check_trigger("END", self)

