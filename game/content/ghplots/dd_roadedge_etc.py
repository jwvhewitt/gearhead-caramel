import random

import game.content
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints
from game import teams
from game.content.ghplots import missionbuilder
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, PlotState
from . import dd_customobjectives


#   ******************************
#   ***  DZRE_MECHA_GRAVEYARD  ***
#   ******************************

class MechaGraveyardAdventure(Plot):
    LABEL = "DZRE_MECHA_GRAVEYARD"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        self.zombots_active = True
        self.got_shutdown = False
        self.safe_shutdown = False
        self.set_collector = False

        # Create the entry mission: PC must defeat the zombots guarding the defiled factory
        team1 = teams.Team(name="Player Team")
        return_to = (self.elements["METROSCENE"], self.elements["MISSION_GATE"])
        outside_scene = gears.GearHeadScene(
            35, 35, plotutility.random_deadzone_spot_name(), player_team=team1, scale=gears.scale.MechaScale,
            exploration_music="Komiku_-_01_-_Ancient_Heavy_Tech_Donjon.ogg",
            combat_music="Komiku_-_03_-_Battle_Theme.ogg", exit_scene_wp=return_to
        )
        myscenegen = pbge.randmaps.SceneGenerator(outside_scene, game.content.gharchitecture.MechaScaleDeadzone())
        self.register_scene(nart, outside_scene, myscenegen, ident="LOCALE", dident="METROSCENE")

        mygoal = self.register_element(
            "_goalroom",
            pbge.randmaps.rooms.FuzzyRoom(random.randint(8, 15), random.randint(8, 15),
                                          parent=outside_scene,
                                          anchor=pbge.randmaps.anchors.middle)
        )
        self.add_sub_plot(nart, "MONSTER_ENCOUNTER", elements={"ROOM": mygoal, "TYPE_TAGS": ("ROBOT", "ZOMBOT")},
                          ident="OUTENCOUNTER")

        room1 = self.register_element(
            "ENTRANCE_ROOM",
            pbge.randmaps.rooms.FuzzyRoom(
                5, 5, anchor=random.choice(pbge.randmaps.anchors.EDGES)), dident="LOCALE"
        )
        myent = self.register_element(
            "ENTRANCE", game.content.ghwaypoints.Exit(anchor=pbge.randmaps.anchors.middle,
                                                      dest_scene=self.elements["METROSCENE"],
                                                      dest_entrance=self.elements["MISSION_GATE"]),
            dident="ENTRANCE_ROOM"
        )

        # Local NPC can tell about the entry mission.
        self.add_sub_plot(nart, "REVEAL_LOCATION", ident="LOCATE", elements={
            "INTERESTING_POINT": "The zombie mecha seem to be attracted to the ancient ruined tower there."})
        self.location_unlocked = False

        # Add the defiled factory dungeon
        mydungeon = dungeonmaker.DungeonMaker(
            nart, self, self.elements["METROSCENE"], "Defiled Factory", gharchitecture.ScrapIronWorkshop(),
            self.rank,
            monster_tags=("ROBOT", "ZOMBOT", "FACTORY"),
            explo_music="Komiku_-_01_-_Ancient_Heavy_Tech_Donjon.ogg",
            combat_music="Komiku_-_03_-_Battle_Theme.ogg",
            connector=plotutility.StairsUpToStairsDownConnector,
            scene_tags=(gears.tags.SCENE_DUNGEON, gears.tags.SCENE_RUINS, gears.tags.SCENE_FACTORY),
            decor=gharchitecture.DefiledFactoryDecor()
        )
        d_entrance = pbge.randmaps.rooms.ClosedRoom(7, 7, anchor=pbge.randmaps.anchors.south)
        mydungeon.entry_level.contents.append(d_entrance)
        mycon2 = plotutility.TownBuildingConnection(
            self, outside_scene, mydungeon.entry_level,
            room1=mygoal,
            room2=d_entrance,
            door1=ghwaypoints.DZDDefiledFactory(name="Defiled Factory", anchor=pbge.randmaps.anchors.middle),
            door2=ghwaypoints.Exit(anchor=pbge.randmaps.anchors.south)
        )

        # Add the lore rooms
        levels = random.sample(mydungeon.levels, 3)
        while len(levels) < 3:
            levels.append(random.choice(mydungeon.levels))

        lr1 = self.register_element(
            "LORE_ROOM_1", pbge.randmaps.rooms.ClosedRoom(7, 7, ),
        )
        levels[0].contents.append(lr1)
        self.add_sub_plot(
            nart, "MONSTER_ENCOUNTER", spstate=PlotState(rank=self.rank + 6).based_on(self),
            elements={"ROOM": lr1, "LOCALE": levels[0], "TYPE_TAGS": ("CREEPY", "ZOMBOT")}
        )
        lorecompy1 = self.register_element("LORE1", ghwaypoints.RetroComputer(plot_locked=True, name="Computer",
                                          desc="You stand before the primary research terminal."),
                                        dident="LORE_ROOM_1")

        # Add the goal room
        final_room = self.register_element(
            "FINAL_ROOM", pbge.randmaps.rooms.ClosedRoom(9, 9, ),
        )
        mydungeon.goal_level.contents.append(final_room)
        self.add_sub_plot(
            nart, "MONSTER_ENCOUNTER", spstate=PlotState(rank=self.rank + 12).based_on(self),
            elements={"ROOM": final_room, "LOCALE": mydungeon.goal_level, "TYPE_TAGS": ("CREEPY", "ZOMBOT")}
        )
        mycompy = self.register_element("COMPY", ghwaypoints.OldMainframe(plot_locked=True, name="Factory Control",
                                                                          anchor=pbge.randmaps.anchors.middle,
                                                                          desc="You stand before the factory control mainframe."),
                                        dident="FINAL_ROOM")
        return True

    def LOCATE_WIN(self, camp):
        self.location_unlocked = True

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.location_unlocked:
            thingmenu.add_item("Go to {}".format(self.elements["LOCALE"]), self.go_to_locale)

    def COMPY_menu(self, camp: gears.GearHeadCampaign, thingmenu):
        if self.zombots_active:
            thingmenu.desc = "{} The lights are blinking wildly.".format(thingmenu.desc)
            thingmenu.add_item("Smash the system", self._smash)
            if self.got_shutdown:
                thingmenu.add_item("Activate the FINAL_DEATH command", self._shutdown)

    def _smash(self, camp: gears.GearHeadCampaign):
        pbge.alert(
            "You smash the computer until the lights stop blinking. If that doesn't take care of the zombie mecha problem, you're not sure what will.")
        self.zombots_active = False
        self.subplots["OUTENCOUNTER"].end_plot(camp)
        camp.check_trigger("WIN", self)

    def _shutdown(self, camp: gears.GearHeadCampaign):
        pbge.alert(
            "You activate the emergency shutdown. For the first time in nearly two hundred years, the computer powers off and comes to a rest.")
        self.zombots_active = False
        self.safe_shutdown = True
        self.subplots["OUTENCOUNTER"].end_plot(camp)
        camp.check_trigger("WIN", self)

    def LORE1_menu(self, camp, thingmenu):
        thingmenu.add_item("Read the notes of Dr. Herbert Coombs", self._read_hc)
        thingmenu.add_item("Read the notes of Dr. Millicent Savini", self._read_ms)
        thingmenu.add_item("Search for hidden files", self._search_l1)

    def _read_hc(self, camp):
        pbge.alert(
            "\"Initial tests of the NC-1 bionite have shown promising results. The program is able to repair damage to mechanical systems, including systems it has never before encountered, thanks to the coordination of the cells' gestalt intelligence.\"")
        pbge.alert(
            "\"There are still limitations. The bionite mass has no internal power source, and so depends upon an external broadcast engine. Individual bionites which move beyond control range perish quickly.\"")
        pbge.alert(
            "\"I have introduced a small amount of NC-1 into my leg prosthetic to see if they can repair the constantly breaking ankle joint.\"")

    def _read_ms(self, camp):
        pass

    def _search_l1(self, camp: gears.GearHeadCampaign):
        pc = camp.make_skill_roll(gears.stats.Knowledge, gears.stats.Computers, self.rank, no_random=True)
        if pc:
            if pc is camp.pc:
                pbge.alert("You easily hack into the ancient computer system.")
            else:
                pbge.alert("{} hacks into the ancient computer system.".format(pc))
            pbge.alert("You discover an additional log file from Dr. Millicent Savini which someone attempted to delete from the database.")
            pbge.alert("\"Attempts to restrain the NC-1 bionite seem to be interpreted by the gestalt intelligence as a form of damage. Thus far, it has outmaneuvered every security protocol we have attempted.\"")
            pbge.alert("\"Herbert's condition is deteriorating as more of his biomass is being replaced by machinery. It is not clear what effect the infection has had on his brain. In any case, I do not believe that his objectivity can be trusted.\"")
            pbge.alert("\"I have installed an emergency shutdown switch into the factory control mainframe. In the event that we lose control of NC-1, the command FINAL_DEATH will cut power to the system.\"")
            self.got_shutdown = True
        else:
            pbge.alert("This computer uses a PreZero operating system that is far beyond your understanding.")

    def go_to_locale(self, camp):
        camp.destination, camp.entrance = self.elements["LOCALE"], self.elements["ENTRANCE"]
