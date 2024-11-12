from pbge.plots import Plot
from game import teams
import gears
import pbge
from game.content import ghwaypoints, gharchitecture, plotutility, dungeonmaker
import random
from game.content.dungeonmaker import DG_NAME, DG_ARCHITECTURE, DG_SCENE_TAGS, DG_TEMPORARY, DG_PARENT_SCENE, DG_EXPLO_MUSIC, DG_COMBAT_MUSIC, DG_DECOR


MDG_DUNGEON = "MDG_DUNGEON"


class MechaDungeon:
    HOSTILE = 0
    DEFEATED = -1
    def __init__(self, name,  status=HOSTILE):
        self.name = name
        self.status = status
    

class GenericMechaDungeonLevel(Plot):
    LABEL = "MECHA_DUNGEON_GENERIC"

    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        intscene = gears.GearHeadScene(65, 65, self.elements[DG_NAME], player_team=team1,
                                       attributes=self.elements[DG_SCENE_TAGS],
                                       combat_music=self.elements[DG_COMBAT_MUSIC],
                                       exploration_music=self.elements[DG_EXPLO_MUSIC],
                                       scale=gears.scale.MechaScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, self.elements[DG_ARCHITECTURE],
                                                   decorate=self.elements.get(DG_DECOR))
        self.register_scene(nart, intscene, intscenegen, ident="LOCALE", dident=DG_PARENT_SCENE,
                            temporary=self.elements.get(DG_TEMPORARY,False))

        self.last_update = 0

        for t in range(random.randint(2,4)):
            self.add_sub_plot(nart, "MDUNGEON_ENCOUNTER",)

        #self.add_sub_plot(nart, "DUNGEON_EXTRA", necessary=False)

        return True

    def t_ENDCOMBAT(self, camp:gears.GearHeadCampaign):
        camp.bring_out_your_dead(True)
        if camp.pc not in camp.party:
            pbge.alert("Your lance retreats...")
            camp.go(camp.home_base)

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        if camp.time > self.last_update:
            dungeonmaker.dungeon_cleaner(camp.scene)
            self.last_update = camp.time



#  **************************************
#  ***   MDUNGEON_ENCOUNTER   ***
#  **************************************
#
#   Like a mecha encounter, but it respawns like a dungeon encounter.
#
#  Elements:
#   LOCALE: The scene where the encounter will take place
#   ROOM: The room where the encounter will take place; if None, an open room will be added.
#   STRENGTH: The initial strength of the mecha encounter. If undefined, will take a default value.
#   ENEMY_FACTION: The enemy you'll be fighting
#

class BasicMechaOutpost(Plot):
    # Fight some random mecha. What do they want? To pad the adventure.
    LABEL = "MDUNGEON_ENCOUNTER"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart: pbge.plots.NarrativeRequest):
        myscene = self.elements["LOCALE"]
        fac = self.elements.get("ENEMY_FACTION")
        if not self.elements.get("ROOM"):
            mapgen: pbge.randmaps.SceneGenerator = nart.get_map_generator(myscene)
            if mapgen:
                room_class = mapgen.archi.get_a_room()
            else:
                return False
            self.register_element("ROOM", room_class(random.randint(5,10), random.randint(5,10)), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,), faction=fac), dident="ROOM")
        strength = self.elements.get("STRENGTH", 50)
        team2.contents += gears.selector.RandomMechaUnit(self.rank, strength, fac, myscene.environment).mecha_list
        self.last_update = 0
        return True

    def _eteam_ACTIVATETEAM(self, camp):
        self.last_update = camp.time

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        myteam: teams.Team = self.elements["_eteam"]
        myscene = self.elements["LOCALE"]
        fac = self.elements.get("ENEMY_FACTION")
        if camp.time > self.last_update:
            dungeonmaker.dungeon_cleaner(self.elements["LOCALE"])
            MDG = self.elements.get(MDG_DUNGEON)
            if len(myteam.get_members_in_play(camp)) < 1 and random.randint(1, 3) != 2 and not (MDG and MDG.status != MDG.HOSTILE):
                camp.scene.deploy_team(gears.selector.RandomMechaUnit(
                    self.rank, random.randint(30,80), fac, myscene.environment
                ).mecha_list, myteam
                )
                self.last_update = camp.time
