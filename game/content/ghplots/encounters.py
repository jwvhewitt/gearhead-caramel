from pbge.plots import Plot
import game
import gears
import pbge
import random
from game import teams
from gears import champions
from game.content import dungeonmaker


#  ***************************
#  ***   MECHA_ENCOUNTER   ***
#  ***************************
#
#  Elements:
#   LOCALE: The scene where the encounter will take place
#   FACTION: The faction you'll be fighting; may be None
#   ROOM: The room where the encounter will take place; if None, an open room will be added.
#

class RandoMechaEncounter(Plot):
    # Fight some random mecha. What do they want? To pad the adventure.
    LABEL = "MECHA_ENCOUNTER"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        if not self.elements.get("ROOM"):
            self.register_element("ROOM", pbge.randmaps.rooms.OpenRoom(5, 5), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team2.contents += gears.selector.RandomMechaUnit(self.rank, 100, self.elements.get("FACTION", None),
                                                         myscene.environment).mecha_list
        return True

    def t_ENDCOMBAT(self, camp):
        # If the player team gets wiped out, end the mission.
        myteam = self.elements["_eteam"]
        if len(myteam.get_members_in_play(camp)) < 1:
            self.end_plot(camp)
            camp.dole_xp(100)


class SmallMechaEncounter(Plot):
    # Fight some random mecha. What do they want? To pad the adventure.
    LABEL = "MECHA_ENCOUNTER"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        if not self.elements.get("ROOM"):
            self.register_element("ROOM", pbge.randmaps.rooms.OpenRoom(5, 5), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team2.contents += gears.selector.RandomMechaUnit(self.rank, 50, self.elements.get("FACTION", None),
                                                         myscene.environment).mecha_list
        return True

    def t_ENDCOMBAT(self, camp):
        # If the player team gets wiped out, end the mission.
        myteam = self.elements["_eteam"]
        if len(myteam.get_members_in_play(camp)) < 1:
            self.end_plot(camp)
            camp.dole_xp(50)


class RandoMechaWithChampionEncounter(RandoMechaEncounter):
    # Fight some random mecha who happen to have a champion. What do they want? To pad the adventure.

    def custom_init(self, nart):
        if super().custom_init(nart):
            myteam = self.elements["_eteam"]
            if myteam.contents:
                champions.upgrade_to_champion(random.choice(myteam.contents))
            return True
        else:
            return False

    def t_ENDCOMBAT(self, camp):
        # If the player team (why _eteam tho?) gets wiped out, end the mission.
        myteam = self.elements["_eteam"]
        if len(myteam.get_members_in_play(camp)) < 1:
            self.end_plot(camp)
            camp.dole_xp(120)


#  *****************************
#  ***   MONSTER_ENCOUNTER   ***
#  *****************************
#
#  Elements:
#   LOCALE: The scene where the encounter will take place
#   ROOM: The room where the encounter will take place; if None, an open room will be added.
#   TYPE_TAGS: The type of monster to generate
#

class RandoMonsterEncounter(Plot):
    # Fight some random monsters. What do they want? To pad the adventure.
    LABEL = "MONSTER_ENCOUNTER"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        if not self.elements.get("ROOM"):
            self.register_element("ROOM", pbge.randmaps.rooms.OpenRoom(random.randint(5,10), random.randint(5,10)), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team2.contents += gears.selector.RandomMonsterUnit(self.rank, 100, myscene.environment,
                                                           self.elements["TYPE_TAGS"], myscene.scale).contents
        self.last_update = 0
        return True

    def _eteam_ACTIVATETEAM(self, camp):
        self.last_update = camp.time

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        myteam: game.teams.Team = self.elements["_eteam"]
        if camp.time > self.last_update:
            dungeonmaker.dungeon_cleaner(self.elements["LOCALE"])
            if len(myteam.get_members_in_play(camp)) < 1 and random.randint(1, 3) != 2:
                camp.scene.deploy_team(
                    gears.selector.RandomMonsterUnit(self.rank, random.randint(80, 120), camp.scene.environment,
                                                     self.elements["TYPE_TAGS"], camp.scene.scale).contents, myteam
                )
                self.last_update = camp.time


#  **************************************
#  ***   ONE_SHOT_MONSTER_ENCOUNTER   ***
#  **************************************
#
#  As above, but monsters don't regenerate.
#

class OneShotMonsterEncounter(Plot):
    # Fight some random monsters. What do they want? To pad the adventure.
    LABEL = "ONE_SHOT_MONSTER_ENCOUNTER"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        if not self.elements.get("ROOM"):
            self.register_element("ROOM", pbge.randmaps.rooms.OpenRoom(random.randint(5,10), random.randint(5,10)), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team2.contents += gears.selector.RandomMonsterUnit(self.rank, 100, myscene.environment,
                                                           self.elements["TYPE_TAGS"], myscene.scale).contents
        self.last_update = 0
        return True

    def _eteam_ACTIVATETEAM(self, camp):
        self.last_update = camp.time + 1

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        myteam: game.teams.Team = self.elements["_eteam"]
        if camp.time > self.last_update and len(myteam.get_members_in_play(camp)) < 1:
            dungeonmaker.dungeon_cleaner(self.elements["LOCALE"])
            self.end_plot(camp, True)
