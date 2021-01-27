# You need a player to find a thing but you'd rather subcontract out the finding bits.
from pbge.plots import Plot, PlotState
from game.content import plotutility
import gears
import pbge
from game import teams
import random
import game.content.plotutility
import game.content.gharchitecture


# GOAL_SCENE: The scene to be placed
# GOAL_ROOM: The entry room to this scene; may be None
# METROSCENE, MISSION_GATE: How we attach this to the adventure
# ENEMY_FACTION: Optional enemy faction for any combat encounters

class CombatSceneToTargetScene(Plot):
    LABEL = "PLACE_SCENE"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        return_to = (self.elements["METROSCENE"], self.elements["MISSION_GATE"])
        outside_scene = gears.GearHeadScene(
            35,35,plotutility.random_deadzone_spot_name(),player_team=team1,scale=gears.scale.MechaScale,
            exploration_music="Lines.ogg", combat_music="Late.ogg",exit_scene_wp=return_to
        )
        myscenegen = pbge.randmaps.SceneGenerator(outside_scene, game.content.gharchitecture.MechaScaleSemiDeadzone())
        self.register_scene( nart, outside_scene, myscenegen, ident="LOCALE", dident="METROSCENE", temporary=True )

        mygoal = self.register_element("_goalroom",pbge.randmaps.rooms.FuzzyRoom(random.randint(8,15),random.randint(8,15),parent=outside_scene,anchor=pbge.randmaps.anchors.middle))

        self.register_element("ENTRANCE_ROOM", pbge.randmaps.rooms.OpenRoom(5, 5, anchor=random.choice(pbge.randmaps.anchors.EDGES)), dident="LOCALE")
        myent = self.register_element(
            "ENTRANCE", game.content.ghwaypoints.Exit(anchor=pbge.randmaps.anchors.middle,
            dest_scene=self.elements["METROSCENE"], dest_entrance=self.elements["MISSION_GATE"]),
            dident="ENTRANCE_ROOM"
        )

        inside_scene = self.elements["GOAL_SCENE"]
        inside_room = self.elements.get("GOAL_ROOM")
        if not inside_room:
            introom = self.register_element('GOAL_ROOM',
                                            pbge.randmaps.rooms.ClosedRoom(random.randint(6, 10), random.randint(6, 10),
                                                                         anchor=pbge.randmaps.anchors.south,),
                                            dident="GOAL_SCENE")
        int_con = game.content.plotutility.IntConcreteBuildingConnection(nart, self, outside_scene, inside_scene, room1=mygoal, room2=inside_room)

        self.add_sub_plot(
            nart, "MECHA_ENCOUNTER",
            spstate=PlotState().based_on(self,{"ROOM":mygoal,"FACTION":self.elements.get("ENEMY_FACTION")}),
            necessary=False
        )

        self.location_unlocked = False
        self.add_sub_plot(nart,"REVEAL_LOCATION",spstate=PlotState(
            elements={"INTERESTING_POINT":"There's a mysterious bunker out there."},
        ).based_on(self),ident="LOCATE")
        return True

    def LOCATE_WIN(self,camp):
        self.location_unlocked = True

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.location_unlocked:
            thingmenu.add_item("Go to {}".format(self.elements["LOCALE"]), self.go_to_locale)

    def go_to_locale(self,camp):
        camp.destination, camp.entrance = self.elements["LOCALE"],self.elements["ENTRANCE"]




# THING: The thing to be placed
# METROSCENE, MISSION_GATE: How we attach this to the adventure
# ENEMY_FACTION: Optional enemy faction for any combat encounters


class ThingInBunker(Plot):
    LABEL = "PLACE_THING"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        return_to = (self.elements["METROSCENE"], self.elements["MISSION_GATE"])
        outside_scene = gears.GearHeadScene(
            35,35,plotutility.random_deadzone_spot_name(),player_team=team1,scale=gears.scale.MechaScale,
            exploration_music="Lines.ogg", combat_music="Late.ogg",exit_scene_wp=return_to
        )
        myscenegen = pbge.randmaps.SceneGenerator(outside_scene, game.content.gharchitecture.MechaScaleSemiDeadzone())
        self.register_scene( nart, outside_scene, myscenegen, ident="LOCALE", dident="METROSCENE", temporary=True )

        mygoal = self.register_element("_goalroom",pbge.randmaps.rooms.FuzzyRoom(random.randint(8,15),random.randint(8,15),parent=outside_scene,anchor=pbge.randmaps.anchors.middle))

        self.register_element("ENTRANCE_ROOM", pbge.randmaps.rooms.OpenRoom(5, 5, anchor=random.choice(pbge.randmaps.anchors.EDGES)), dident="LOCALE")
        myent = self.register_element(
            "ENTRANCE", game.content.ghwaypoints.Exit(anchor=pbge.randmaps.anchors.middle,
            dest_scene=self.elements["METROSCENE"], dest_entrance=self.elements["MISSION_GATE"]),
            dident="ENTRANCE_ROOM"
        )

        team1 = teams.Team(name="Player Team")
        inside_scene = gears.GearHeadScene(
            12,12,"Bunker",player_team=team1,scale= gears.scale.HumanScale,
            exploration_music="Lines.ogg", combat_music="Late.ogg",exit_scene_wp=return_to
        )
        intscenegen = pbge.randmaps.SceneGenerator(inside_scene, game.content.gharchitecture.DefaultBuilding())
        self.register_scene( nart, inside_scene, intscenegen, ident="GOALSCENE", dident="LOCALE", temporary=True )

        introom = self.register_element('_introom', pbge.randmaps.rooms.OpenRoom(random.randint(6,10), random.randint(6,10), anchor=pbge.randmaps.anchors.middle, decorate=pbge.randmaps.decor.OmniDec(win=game.content.ghterrain.Window)), dident="GOALSCENE")

        mything = self.elements["THING"]
        self.place_element(mything,introom)

        int_con = game.content.plotutility.IntConcreteBuildingConnection(nart, self, outside_scene, inside_scene, room1=mygoal, room2=introom)

        self.add_sub_plot(
            nart, "MECHA_ENCOUNTER",
            spstate=PlotState().based_on(self,{"ROOM":mygoal,"FACTION":self.elements.get("ENEMY_FACTION")}),
            necessary=False
        )
        self.add_sub_plot(nart,"BASE_ROOM_LOOT",spstate=PlotState(elements={"ROOM":introom,"FACTION":self.elements.get("ENEMY_FACTION")},).based_on(self))

        self.location_unlocked = False
        self.add_sub_plot(nart,"REVEAL_LOCATION",spstate=PlotState(
            elements={"INTERESTING_POINT":"There's a mysterious bunker out there."},
        ).based_on(self),ident="LOCATE")
        return True

    def LOCATE_WIN(self,camp):
        self.location_unlocked = True

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.location_unlocked:
            thingmenu.add_item("Go to {}".format(self.elements["LOCALE"]), self.go_to_locale)

    def go_to_locale(self,camp):
        camp.destination, camp.entrance = self.elements["LOCALE"],self.elements["ENTRANCE"]

