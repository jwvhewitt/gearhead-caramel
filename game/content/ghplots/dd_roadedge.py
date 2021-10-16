from pbge.plots import Plot,PlotState
import gears
import pbge
import random
from game.content import gharchitecture, plotutility
from . import missionbuilder, dd_customobjectives, campfeatures
#from missionbuilder import RoadMissionPlot

#   ***************************************************
#   ***   SUPPORT  CLASSES  FOR  BAM_ROAD_MISSION   ***
#   ***************************************************
from ..gharchitecture import DeadZoneHighwaySceneGen



class DZDREBasicPlotWithEncounterStuff(Plot):
    LABEL = "UTILITY_PARENT"

    active = True
    scope = True
    BASE_RANK = 15
    RATCHET_SETUP = "DZRE_BanditProblem"
    ENCOUNTER_CHANCE = BASE_RANK + 30
    RANDOM_ENCOUNTER_CHANCE = 20
    ENCOUNTER_NAME = "Bandit Ambush!"
    ENCOUNTER_OBJECTIVES = (missionbuilder.BAMO_DEFEAT_THE_BANDITS,)
    ENCOUNTER_ARCHITECTURE = gharchitecture.MechaScaleSemiDeadzone

    def custom_init(self, nart):
        myedge = self.elements["DZ_EDGE"]
        self.rank = self.BASE_RANK + random.randint(1,6) - random.randint(1,6)
        self.register_element("DZ_EDGE_STYLE",myedge.style)
        self.road_cleared = False
        return True

    def get_enemy_encounter(self, camp, dest_node):
        start_node = self.elements["DZ_EDGE"].get_link(dest_node)
        if start_node.pos[0] < dest_node.pos[0]:
            myanchor = pbge.randmaps.anchors.west
        else:
            myanchor = pbge.randmaps.anchors.east
        myadv = missionbuilder.BuildAMissionSeed(
            camp, self.ENCOUNTER_NAME, start_node.destination, start_node.entrance,
            enemy_faction = self.elements.get("FACTION"), rank=self.rank,
            objectives = self.ENCOUNTER_OBJECTIVES + (dd_customobjectives.DDBAMO_MAYBE_AVOID_FIGHT,),
            adv_type = "BAM_ROAD_MISSION",
            custom_elements={"ADVENTURE_GOAL": dest_node.entrance,"ENTRANCE_ANCHOR": myanchor},
            scenegen=DeadZoneHighwaySceneGen,
            architecture=self.ENCOUNTER_ARCHITECTURE(room_classes=(pbge.randmaps.rooms.FuzzyRoom,)),
            cash_reward=0,
        )
        return myadv

    def get_random_encounter(self, camp, dest_node):
        start_node = self.elements["DZ_EDGE"].get_link(dest_node)
        if start_node.pos[0] < dest_node.pos[0]:
            myanchor = pbge.randmaps.anchors.west
        else:
            myanchor = pbge.randmaps.anchors.east

        myadv = camp.campdata[campfeatures.WORLD_MAP_ENCOUNTERS](
            camp, start_node.destination, start_node.entrance,
            dest_scene=dest_node.destination, dest_wp=dest_node.entrance,
            rank=self.rank, encounter_chance=self.RANDOM_ENCOUNTER_CHANCE,
            scenegen=DeadZoneHighwaySceneGen,
            architecture=self.ENCOUNTER_ARCHITECTURE,
            environment=gears.tags.GroundEnv,
            entrance_anchor=myanchor
        )
        return myadv

    def get_road_adventure(self, camp, dest_node):
        # Return an adventure if there's going to be an adventure. Otherwise return nothing.
        if self.active and camp.has_mecha_party():
            if random.randint(1,100) <= self.ENCOUNTER_CHANCE and not self.road_cleared:
                return self.get_enemy_encounter(camp, dest_node)
            else:
                return self.get_random_encounter(camp, dest_node)

    def MISSION_WIN(self,camp):
        self.elements["DZ_EDGE"].style = self.elements["DZ_EDGE"].STYLE_SAFE
        self.road_cleared = True


class DZDREProppStarterPlot(DZDREBasicPlotWithEncounterStuff):
    LABEL = "UTILITY_PARENT"

    active = True
    scope = True
    BASE_RANK = 15
    RATCHET_SETUP = "DZRE_BanditProblem"
    ENCOUNTER_CHANCE = BASE_RANK + 30
    ENCOUNTER_NAME = "Bandit Ambush!"
    ENCOUNTER_OBJECTIVES = (missionbuilder.BAMO_DEFEAT_THE_BANDITS,)
    ENCOUNTER_ARCHITECTURE = gharchitecture.MechaScaleSemiDeadzone

    def custom_init(self, nart):
        super().custom_init(nart)
        myedge = self.elements["DZ_EDGE"]
        self.register_element("FACTION",self.get_enemy_faction(nart))
        self.add_sub_plot(nart,"ADD_REMOTE_OFFICE",ident="ENEMYRO",spstate=PlotState(rank=self.rank+5,elements={"METRO":myedge.start_node.destination.metrodat,"METROSCENE":myedge.start_node.destination,"LOCALE":myedge.start_node.destination,"MISSION_GATE":myedge.start_node.entrance}).based_on(self))
        self.add_sub_plot(nart,self.RATCHET_SETUP,ident="MISSION",spstate=PlotState(elements={"METRO":myedge.start_node.destination.metrodat,"METROSCENE":myedge.start_node.destination,"MISSION_GATE":myedge.start_node.entrance}).based_on(self))

        return True

    def get_enemy_faction(self,nart):
        myedge = self.elements["DZ_EDGE"]
        return plotutility.RandomBanditCircle(nart.camp, enemies=(myedge.start_node.destination.faction,))


#   *******************************
#   ***   DZD_ROADEDGE_YELLOW   ***
#   *******************************
#
# Yellow road edges have a difficulty rank of around 15.

class BanditsPalooza(DZDREProppStarterPlot):
    LABEL = "DZD_ROADEDGE_YELLOW"

    def _get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        myscene = camp.scene.get_root_scene()
        if self.elements["DZ_EDGE"].connects_to_city(myscene) and not self.road_cleared:
            # This city is on this road.
            mygram["[News]"] = ["you should beware {} when traveling to {}".format(str(self.elements["FACTION"]),self.elements["DZ_EDGE"].get_city_link(myscene)), ]
        return mygram


class BlackMarketBluesStarter(DZDREBasicPlotWithEncounterStuff):
    LABEL = "DZD_ROADEDGE_YELLOW"
    UNIQUE = True

    GOOD_ENEMIES = (
        gears.factions.ClanIronwind, gears.factions.BoneDevils, gears.factions.ClanIronwind,
        gears.factions.BoneDevils, gears.factions.BladesOfCrihna,
    )

    def custom_init(self, nart):
        super().custom_init(nart)
        myedge = self.elements["DZ_EDGE"]
        self.register_element("FACTION", self.get_enemy_faction(nart))
        self.add_sub_plot(nart, "DZRE_BLACKMARKETBLUES", ident="MISSION", spstate=PlotState(elements={"METRO":myedge.start_node.destination.metrodat,"METROSCENE":myedge.start_node.destination,"MISSION_GATE":myedge.start_node.entrance}).based_on(self))
        return True

    def get_enemy_faction(self,nart):
        myedge = self.elements["DZ_EDGE"]
        base_faction = random.choice(self.GOOD_ENEMIES)
        return gears.factions.Circle(nart.camp,base_faction,enemies=(myedge.start_node.destination.faction,))

    def _get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        myscene = camp.scene.get_root_scene()
        if self.elements["DZ_EDGE"].connects_to_city(myscene) and not self.road_cleared:
            # This city is on this road.
            mygram["[News]"] = ["{} have been robbing travelers going to {}".format(str(self.elements["FACTION"]),self.elements["DZ_EDGE"].get_city_link(myscene)), ]
        return mygram


#   *******************************
#   ***   DZD_ROADEDGE_ORANGE   ***
#   *******************************
#
# Orange road edges have a difficulty rank of around 25.

class TheMechaGraveyard(DZDREBasicPlotWithEncounterStuff):
    LABEL = "DZD_ROADEDGE_ORANGE"

    active = True
    scope = True
    UNIQUE = True
    BASE_RANK = 25
    ENCOUNTER_CHANCE = BASE_RANK + 30
    ENCOUNTER_ARCHITECTURE = gharchitecture.MechaScaleDeadzone

    def custom_init(self, nart):
        super().custom_init(nart)
        myedge = self.elements["DZ_EDGE"]
        self.add_sub_plot(nart, "DZRE_MECHA_GRAVEYARD", ident="MISSION", spstate=PlotState(elements={"METRO":myedge.start_node.destination.metrodat,"METROSCENE":myedge.start_node.destination,"MISSION_GATE":myedge.start_node.entrance}).based_on(self))
        return True

    def get_enemy_encounter(self, camp, dest_node):
        start_node = self.elements["DZ_EDGE"].get_link(dest_node)
        if start_node.pos[0] < dest_node.pos[0]:
            myanchor = pbge.randmaps.anchors.west
        else:
            myanchor = pbge.randmaps.anchors.east
        myadv = missionbuilder.BuildAMissionSeed(
            camp, "Zombot Attack", start_node.destination, start_node.entrance,
            enemy_faction = None, rank=self.rank,
            objectives = (missionbuilder.BAMO_FIGHT_MONSTERS, dd_customobjectives.DDBAMO_ENCOUNTER_ZOMBOTS,),
            adv_type = "BAM_ROAD_MISSION",
            custom_elements={"ADVENTURE_GOAL": dest_node.entrance,"ENTRANCE_ANCHOR": myanchor,
                             missionbuilder.BAME_MONSTER_TAGS: ("ZOMBOT",)},
            scenegen=DeadZoneHighwaySceneGen,
            architecture=self.ENCOUNTER_ARCHITECTURE(room_classes=(pbge.randmaps.rooms.FuzzyRoom,)),
            cash_reward=0,
            combat_music="Komiku_-_03_-_Battle_Theme.ogg", exploration_music="Komiku_-_01_-_Ancient_Heavy_Tech_Donjon.ogg"
        )
        return myadv

    def get_road_adventure(self, camp, dest_node):
        # Return an adventure if there's going to be an adventure. Otherwise return nothing.
        if self.active and camp.has_mecha_party():
            if random.randint(1,100) <= self.ENCOUNTER_CHANCE and not self.road_cleared:
                return self.get_enemy_encounter(camp, dest_node)
            elif random.randint(1,100) <= 15 or self.road_cleared:
                return self.get_random_encounter(camp, dest_node)

    def MISSION_WIN(self,camp):
        self.elements["DZ_EDGE"].style = self.elements["DZ_EDGE"].STYLE_SAFE
        self.road_cleared = True

    def _get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        myscene = camp.scene.get_root_scene()
        if self.elements["DZ_EDGE"].connects_to_city(myscene) and not self.road_cleared:
            # This city is on this road.
            mygram["[News]"] = ["the road to {} is known as the mecha graveyard".format(self.elements["DZ_EDGE"].get_city_link(myscene)), ]
        return mygram



class InvadersPalooza(DZDREProppStarterPlot):
    LABEL = "DZD_ROADEDGE_ORANGE"
    BASE_RANK = 25
    RATCHET_SETUP = "DZRE_InvaderProblem"
    ENCOUNTER_CHANCE = BASE_RANK + 30
    ENCOUNTER_NAME = "Invader Ambush!"
    ENCOUNTER_OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER,)
    ENCOUNTER_ARCHITECTURE = gharchitecture.MechaScaleDeadzone

    GOOD_INVADERS = (
        gears.factions.AegisOverlord, gears.factions.ClanIronwind, gears.factions.AegisOverlord,
        gears.factions.ClanIronwind, gears.factions.AegisOverlord, gears.factions.ClanIronwind,
        gears.factions.AegisOverlord, gears.factions.ClanIronwind, gears.factions.AegisOverlord,
        gears.factions.ClanIronwind, gears.factions.AegisOverlord, gears.factions.ClanIronwind,
        gears.factions.BoneDevils, gears.factions.BladesOfCrihna
    )

    def get_enemy_faction(self,nart):
        myedge = self.elements["DZ_EDGE"]
        base_faction = random.choice(self.GOOD_INVADERS)
        return gears.factions.Circle(nart.camp,base_faction,enemies=(myedge.start_node.destination.faction,))

    def _get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        myscene = camp.scene.get_root_scene()
        if self.elements["DZ_EDGE"].connects_to_city(myscene) and not self.road_cleared:
            # This city is on this road.
            mygram["[News]"] = ["the road to {1} is frequented by {0}".format(str(self.elements["FACTION"]),self.elements["DZ_EDGE"].get_city_link(myscene)), ]
        return mygram


#   ****************************
#   ***   DZD_ROADEDGE_RED   ***
#   ****************************
#
# Red road edges have a difficulty rank of around 35.

class UpgradedInvadersPalooza(DZDREProppStarterPlot):
    LABEL = "DZD_ROADEDGE_RED"
    BASE_RANK = 35
    RATCHET_SETUP = "DZRE_InvaderProblem"
    ENCOUNTER_CHANCE = BASE_RANK + 30
    ENCOUNTER_NAME = "Invader Ambush!"
    ENCOUNTER_OBJECTIVES = (missionbuilder.BAMO_DEFEAT_ARMY,)
    ENCOUNTER_ARCHITECTURE = gharchitecture.MechaScaleDeadzone

    GOOD_INVADERS = (
        gears.factions.AegisOverlord, gears.factions.ClanIronwind,
        gears.factions.BoneDevils, gears.factions.BladesOfCrihna
    )

    def get_enemy_faction(self,nart):
        myedge = self.elements["DZ_EDGE"]
        base_faction = random.choice(self.GOOD_INVADERS)
        return gears.factions.Circle(nart.camp,base_faction,enemies=(myedge.start_node.destination.faction,))

    def _get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        myscene = camp.scene.get_root_scene()
        if self.elements["DZ_EDGE"].connects_to_city(myscene) and not self.road_cleared:
            # This city is on this road.
            mygram["[News]"] = ["the road to {1} is controlled by {0}".format(str(self.elements["FACTION"]),self.elements["DZ_EDGE"].get_city_link(myscene)), ]
        return mygram

