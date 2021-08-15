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
from .dd_homebase import CD_BIOTECH_DISCOVERIES, BiotechDiscovery


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
            "ENTRANCE",
            game.content.ghwaypoints.Exit(dest_wp=self.elements["MISSION_GATE"], anchor=pbge.randmaps.anchors.middle),
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
            nart, self, outside_scene, mydungeon.entry_level,
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

        lr2 = self.register_element(
            "LORE_ROOM_2", pbge.randmaps.rooms.ClosedRoom(7, 7, ),
        )
        levels[1].contents.append(lr2)
        self.add_sub_plot(
            nart, "MONSTER_ENCOUNTER", spstate=PlotState(rank=self.rank + 6).based_on(self),
            elements={"ROOM": lr2, "LOCALE": levels[1], "TYPE_TAGS": ("CREEPY", "ZOMBOT")}
        )
        lorecompy2 = self.register_element("LORE2", ghwaypoints.RetroComputer(plot_locked=True, name="Computer",
                                          desc="You stand before the research overview terminal."),
                                        dident="LORE_ROOM_2")

        lr3 = self.register_element(
            "LORE_ROOM_3", pbge.randmaps.rooms.ClosedRoom(7, 7, ),
        )
        levels[2].contents.append(lr3)
        self.add_sub_plot(
            nart, "MONSTER_ENCOUNTER", spstate=PlotState(rank=self.rank + 6).based_on(self),
            elements={"ROOM": lr3, "LOCALE": levels[2], "TYPE_TAGS": ("ROBOT",)}
        )
        lorecompy3 = self.register_element("LORE3", ghwaypoints.RetroComputer(plot_locked=True, name="Computer",
                                          desc="You stand before the incubation chamber control terminal."),
                                        dident="LORE_ROOM_3")
        biotank_alpha = self.register_element("BIO_A", ghwaypoints.Biotank(plot_locked=True, name="Biotank",),
                                        dident="LORE_ROOM_3")
        biotank_beta = self.register_element("BIO_B", ghwaypoints.EmptyBiotank(plot_locked=True, name="Biotank",),
                                        dident="LORE_ROOM_3")

        self.alpha_full = True
        self.beta_full = False

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

        #print(self.elements["METROSCENE"])

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
            "You smash the computer until the lights stop blinking. Then you smash it a bit more just to be safe. If that doesn't take care of the zombie mecha problem, you're not sure what will.")
        self.zombots_active = False
        self.subplots["OUTENCOUNTER"].end_plot(camp)
        camp.check_trigger("WIN", self)
        BiotechDiscovery(camp, "I found an old zombot-infested biotech laboratory.",
                         "[THATS_INTERESTING] I'll get one of our hazmat recovery teams to check it out. Here is the {cash} you've earned.",
                         self.rank//2)

    def _shutdown(self, camp: gears.GearHeadCampaign):
        pbge.alert(
            "You activate the emergency shutdown. For the first time in nearly two hundred years, the computer powers off and comes to a rest.")
        self.zombots_active = False
        self.safe_shutdown = True
        if self.beta_full:
            self.set_collector = True
        self.subplots["OUTENCOUNTER"].end_plot(camp)
        camp.check_trigger("WIN", self)
        BiotechDiscovery(camp, "I found a PreZero lab where they were developing self-repair technology",
                         "[THATS_INTERESTING] This could be a very important discovery; I'd say it's easily worth {cash}.", self.rank+15)

    def LORE3_menu(self, camp, thingmenu):
        if self.alpha_full:
            thingmenu.add_item("Drain Alpha Chamber", self._toggle_alpha)
        else:
            thingmenu.add_item("Fill Alpha Chamber", self._toggle_alpha)
        if self.beta_full:
            thingmenu.add_item("Drain Beta Chamber", self._toggle_beta)
        else:
            thingmenu.add_item("Fill Beta Chamber", self._toggle_beta)

    def _toggle_alpha(self, camp):
        if self.alpha_full:
            self.alpha_full = False
            self.elements["BIO_A"].break_tank()
            mymonster: gears.base.Monster = gears.selector.get_design_by_full_name("Skeletron")
            mymonster.roll_stats(20,False)
            mymonster.colors = (gears.color.CardinalRed, gears.color.Ebony, gears.color.ElectricYellow, gears.color.Cyan, gears.color.Malachite)
            mymonster.name = "Subject Alpha"
            mymonster.statline[gears.stats.CloseCombat] += 4
            mymonster.statline[gears.stats.Vitality] += 7
            myteam = teams.Team(enemies=(camp.scene.player_team,))
            camp.scene.place_gears_near_spot(self.elements["BIO_A"].pos[0],self.elements["BIO_A"].pos[1],myteam, mymonster)
        else:
            pbge.alert("ERROR: Alpha Chamber not responding. Please consult manual.")

    def _toggle_beta(self, camp):
        if self.beta_full:
            self.elements["BIO_B"].empty_tank()
        else:
            self.elements["BIO_B"].fill_tank()
        self.beta_full = not self.beta_full

    def BIO_A_menu(self, camp, thingmenu):
        if self.alpha_full:
            thingmenu.desc = "This biotank is filled with a cloudy green liquid. There is something moving gently inside of it."
        else:
            thingmenu.desc = "This biotank has been destroyed."

    def BIO_B_menu(self, camp, thingmenu):
        if self.set_collector:
            if self.beta_full:
                thingmenu.desc = "This biotank is filled with a cloudy green liquid. There is a large, dark shape in the middle of the tank."
            else:
                thingmenu.desc = "This biotank contains a featureless black box. You are pretty sure it wasn't there earlier."
                thingmenu.add_item("Get the box", self._get_box)
        else:
            if self.beta_full:
                thingmenu.desc = "This biotank is filled with a cloudy green liquid."
            else:
                thingmenu.desc = "This biotank is empty."

    def _get_box(self, camp):
        pbge.alert("You retrieve the box from the biotank. It appears to be some kind of mecha component.")
        self.set_collector = False
        myitem = gears.selector.get_design_by_full_name("NC-1 Self Repair System")
        camp.party.append(myitem)

    def LORE2_menu(self, camp, thingmenu):
        thingmenu.add_item("Read the overview for the NC-1 Self Repair Module", self._read_overview)
        thingmenu.add_item("Search for hidden files", self._search_l2)

    def _read_overview(self, camp):
        pbge.alert(
            "The NC-1 Self Repair Module is a revolutionary new technology for conventional battlemovers. It uses bionite agents to effect instantaneous repair of mechanical systems.")
        pbge.alert(
            "Direction is provided by the gestalt intelligence of the bionite network. This allows the system to operate without a central control unit and to make efficient use of available resources.")
        pbge.alert(
            "Join the battleforce of the future, today. Support development of the NC-1 Self Repair Module now and get early backer exclusive rewards.")

    def _search_l2(self, camp: gears.GearHeadCampaign):
        pc = camp.make_skill_roll(gears.stats.Knowledge, gears.stats.Computers, self.rank, difficulty=gears.stats.DIFFICULTY_EASY, no_random=True)
        if pc:
            if pc is camp.pc:
                pbge.alert("You easily hack into the ancient computer system.")
            else:
                pbge.alert("{} hacks into the ancient computer system.".format(pc))
            pbge.alert("You discover an additional data file for a secondary project.")
            pbge.alert("Test subject HC-Alpha shows the potential for the NC-1 system to be used not just for battlemovers, but individual soldiers as well. Biotechnology allows perfect fusion of organic and inorganic components.")
            pbge.alert("If the neural degradation problem can be solved, imagine the potential: Immortal soldiers who instantly recover from any damage. The keys to their immortality safely held by illumos who control the power source.")
            pbge.alert("Even if the degradation problem is intractable, there are ways to weaponize this phenomenon. Imagine high-C munitions loaded with NC bionites. Initial casulties could be reanimated to eliminate surviving defenders.")
            pbge.alert("Anyway, it's something to think about when we submit the third round of grant applications.")
            self.got_shutdown = True
        else:
            pbge.alert("This computer uses a PreZero operating system that is far beyond your understanding.")

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
            "\"I have introduced a small amount of NC-1 into my leg prosthetic to see if they can repair my constantly slipping ankle joint.\"")

    def _read_ms(self, camp):
        pbge.alert(
            "\"Initial tests for the NC-1 bionite have revealed problems not indicated by the prototypes. Among these issues, the infectious nature of the system must be resolved before testing resumes.\"")
        pbge.alert(
            "\"The gestalt intelligence does not differentiate between its host machinery and external units. This leads to the bionites attempting to colonize any machine they are brought into contact with. A self-repair system that will also repair your enemy's machine is, to put it bluntly, less than optimal.\"")
        pbge.alert(
            "\"So far, the spread of the bionites has been limited by their fragility when moved beyond range of the broadcast power system. Testing cannot resume until it's clear we're not risking another Onyx Jelly fiasco.\"")

    def _search_l1(self, camp: gears.GearHeadCampaign):
        pc = camp.make_skill_roll(gears.stats.Knowledge, gears.stats.Computers, self.rank, no_random=True)
        if pc:
            if pc is camp.pc:
                pbge.alert("You easily hack into the ancient computer system.")
            else:
                pbge.alert("{} hacks into the ancient computer system.".format(pc))
            pbge.alert("You discover an additional log file from Dr. Millicent Savini which someone attempted to delete from the database.")
            pbge.alert("\"Attempts to restrain the NC-1 bionite seem to be interpreted by the gestalt intelligence as a form of damage. Thus far, it has outmaneuvered every security protocol we have attempted.\"")
            pbge.alert("\"Herbert's condition is deteriorating as more of his biomass is being replaced by machinery. It is not clear what effect the infection has had on his brain. In any case, I have restrained him in a specimen vat and will be conducting further tests.\"")
            pbge.alert("\"I have installed an emergency shutdown switch into the factory control mainframe. In the event that we lose control of NC-1, the command FINAL_DEATH will cut power to the system. Active bionites will be moved to the containment system.\"")
            self.got_shutdown = True
        else:
            pbge.alert("This computer uses a PreZero operating system that is far beyond your understanding.")

    def go_to_locale(self, camp):
        camp.go(self.elements["ENTRANCE"])
