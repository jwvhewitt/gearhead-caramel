from pbge.plots import Plot
import game
import gears
import pbge
import random
from game import teams
from gears import champions


#  ***************************
#  ***   MECHA_ENCOUNTER   ***
#  ***************************
#
#  Elements:
#   LOCALE: The scene where the encounter will take place
#   FACTION: The faction you'll be fighting; may be None
#   ROOM: The room where the encounter will take place; if None, an open room will be added.
#

class RandoMechaEncounter( Plot ):
    # Fight some random mecha. What do they want? To pad the adventure.
    LABEL = "MECHA_ENCOUNTER"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        if not self.elements.get("ROOM"):
            self.register_element("ROOM",pbge.randmaps.rooms.OpenRoom(5,5),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        team2.contents += gears.selector.RandomMechaUnit(self.rank,100,self.elements.get("FACTION",None),myscene.environment).mecha_list
        return True
    def t_ENDCOMBAT(self,camp):
        # If the player team gets wiped out, end the mission.
        myteam = self.elements["_eteam"]
        if len(myteam.get_active_members(camp)) < 1:
            self.end_plot(camp)
            camp.dole_xp(100)

class SmallMechaEncounter( Plot ):
    # Fight some random mecha. What do they want? To pad the adventure.
    LABEL = "MECHA_ENCOUNTER"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        if not self.elements.get("ROOM"):
            self.register_element("ROOM",pbge.randmaps.rooms.OpenRoom(5,5),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        team2.contents += gears.selector.RandomMechaUnit(self.rank,50,self.elements.get("FACTION",None),myscene.environment).mecha_list
        return True
    def t_ENDCOMBAT(self,camp):
        # If the player team gets wiped out, end the mission.
        myteam = self.elements["_eteam"]
        if len(myteam.get_active_members(camp)) < 1:
            self.end_plot(camp)
            camp.dole_xp(50)

class RandoMechaWithChampionEncounter( RandoMechaEncounter ):
    # Fight some random mecha who happen to have a champion. What do they want? To pad the adventure.

    def custom_init( self, nart ):
        if super().custom_init(nart):
            myteam = self.elements["_eteam"]
            if myteam.contents:
                champions.upgrade_to_champion(random.choice(myteam.contents))
            return True
        else:
            return False
    def t_ENDCOMBAT(self,camp):
        # If the player team (why _eteam tho?) gets wiped out, end the mission.
        myteam = self.elements["_eteam"]
        if len(myteam.get_active_members(camp)) < 1:
            self.end_plot(camp)
            camp.dole_xp(120)


class RandoThemedChampionsEncounter( SmallMechaEncounter ):
    # Fight some random champions. What do they want? To pad the adventure.
    def custom_init( self, nart ):
        theme = random.choice(champions.THEMES)
        if super().custom_init(nart):
            myteam = self.elements["_eteam"]
            for mek in myteam.contents:
                champions.upgrade_to_champion(mek, theme)
            return True
        else:
            return False
    def t_ENDCOMBAT(self,camp):
        # If the player team (why _eteam tho?) gets wiped out, end the mission.
        myteam = self.elements["_eteam"]
        if len(myteam.get_active_members(camp)) < 1:
            self.end_plot(camp)
            camp.dole_xp(75)
