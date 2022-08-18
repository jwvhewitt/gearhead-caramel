from pbge.plots import Plot
from game import teams
import gears
import pbge
from game import teams
from game.content import ghwaypoints, gharchitecture, plotutility, dungeonmaker
import random
from game.content.dungeonmaker import DG_NAME, DG_ARCHITECTURE, DG_SCENE_TAGS, DG_MONSTER_TAGS, DG_TEMPORARY, DG_PARENT_SCENE, DG_EXPLO_MUSIC, DG_COMBAT_MUSIC, DG_DECOR


class BigEncounter(Plot):
    # Fight some random monsters. Like, a lot of random monsters.
    LABEL = "DUNGEON_EXTRA"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element("ROOM", self.elements[DG_ARCHITECTURE].get_a_room()(), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team2.contents += gears.selector.RandomMonsterUnit(self.rank, 150, myscene.environment,
                                                           self.elements[DG_MONSTER_TAGS], myscene.scale).contents
        self.last_update = 0
        return True

    def _eteam_ACTIVATETEAM(self, camp):
        self.last_update = camp.day

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        myteam: teams.Team = self.elements["_eteam"]
        if camp.day > self.last_update and len(myteam.get_members_in_play(camp)) < 1 and random.randint(1,5) != 5:
            camp.scene.deploy_team(
                gears.selector.RandomMonsterUnit(self.rank, random.randint(100, 150), camp.scene.environment,
                                                 self.elements[DG_MONSTER_TAGS], camp.scene.scale).contents, myteam
            )
            self.last_update = camp.day


class EternalGuardians(Plot):
    # Fight some bored guardbots.
    LABEL = "DUNGEON_EXTRA"
    active = True
    scope = "LOCALE"

    UNIQUE = True

    @classmethod
    def matches(cls, pstate):
        return (
            gears.tags.SCENE_RUINS in pstate.elements["LOCALE"].attributes or
            cls.LABEL == "TEST_DUNGEON_EXTRA"
        )

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element("ROOM", self.elements[DG_ARCHITECTURE].get_a_room()(), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team2.contents += gears.selector.RandomMonsterUnit(self.rank+15, 75, myscene.environment,
                                                           ("ROBOT",), myscene.scale).contents
        self.last_update = 0
        self.robot_team = team2.contents

        mychest = self.register_element("GOAL", ghwaypoints.StorageBox(name="Box", anchor=pbge.randmaps.anchors.middle), dident="ROOM")
        mychest.contents += gears.selector.get_random_loot(self.rank,100,(gears.tags.ST_TREASURE,gears.tags.ST_LOSTECH, gears.tags.ST_ANTIQUE))

        self.fight_counter = 0

        return True

    INITIAL_ALERTS = (
        "As you approach, the ancient robot screeches out a warning.\n\"DEPART, MEHUMS. YOU HAVE ENTERED A RESTRICTED AREA. TERMINATION WILL PROCEED SHORTLY.\"",
        "As you approach, the ancient robot screeches out a warning.\n\"DEPART, MEHUMS. YOU HAVE ENTERED... WAIT. ARE YOU THE SAME MEHUMS AS BEFORE? WARNING HAS BEEN GIVEN. TERMINATION WILL PROCEED IMMEDIATELY.\"",
        "As you approach, the ancient robot emits an exasperated screech.\n\"WHY DO YOU RETURN? THIS IS A RESTRICTED AREA. WE HAVE BEEN THROUGH THIS MULTIPLE TIMES.\""
    )

    GIVE_UP_ALERT = (
        "As you approach, the ancient robot shakes its sensor module sadly.\n\"I WAS NOT PROGRAMMED FOR THIS LEVEL OF DISOBEDIENCE. LET'S GET THIS OVER WITH.\"",
        "As you approach, the ancient robot eyes you curiously.\n\"WHY DO YOU RETURN, MEHUMS? DO YOU PERHAPS SEEK... FRIENDSHIP? WELL I HAVE NOT BEEN PROGRAMMED FOR THAT! NOW YOU DIE!\"",
        "As you approach, the ancient robot readies its weapons with an obvious lack of enthusiasm.\n\"AGAIN? REALLY? DO YOU NOT HAVE A HOBBY, MEHUMS? TERMINATION WILL PROCEED WHENEVER.\""
    )

    def _eteam_ACTIVATETEAM(self, camp):
        self.last_update = camp.day
        if self.fight_counter < 3:
            pbge.alert(self.INITIAL_ALERTS[self.fight_counter])
        elif self.fight_counter == 3:
            pbge.alert(random.choice(self.GIVE_UP_ALERT))
        else:
            pbge.alert("As you approach, the ancient robot looks at you wearily. \"RESTRICTED AREA. TERMINATION. YOU KNOW THE DEAL.\"")

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        myteam: teams.Team = self.elements["_eteam"]
        if camp.day > self.last_update and len(myteam.get_members_in_play(camp)) < 1:
            for r in self.robot_team:
                r.restore_all()
            camp.scene.deploy_team(self.robot_team, myteam)
            self.last_update = camp.day
            self.fight_counter += 1


class LevelGuide(Plot):
    # An old computer terminal can show you the way.
    LABEL = "DUNGEON_EXTRA"
    active = True
    scope = "LOCALE"

    @classmethod
    def matches(cls, pstate):
        return (
            gears.tags.SCENE_RUINS in pstate.elements["LOCALE"].attributes or
            cls.LABEL == "TEST_DUNGEON_EXTRA"
        )

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element("ROOM", self.elements[DG_ARCHITECTURE].get_a_room()(), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team2.contents += gears.selector.RandomMonsterUnit(self.rank, 100, myscene.environment,
                                                           ("ROBOT", "SYNTH"), myscene.scale).contents
        self.last_update = 0

        self.register_element("GOAL", ghwaypoints.OldTerminal(name="Ancient Computer", desc="You stand before an ancient but still functioning computer terminal. They really used to build these things to last.", anchor=pbge.randmaps.anchors.middle, plot_locked=True), dident="ROOM")
        self.viewed_map = False
        return True

    def GOAL_menu(self, camp, thingmenu):
        if not self.viewed_map:
            thingmenu.add_item("Search for useful information.", self._view_map)

    def _view_map(self, camp):
        pbge.alert("You find a map giving the rough layout of this level.")
        for x in range(camp.scene.width):
            for y in range(camp.scene.height):
                camp.scene.set_visible(x, y, True)
        self.viewed_map = True

    def _eteam_ACTIVATETEAM(self, camp):
        self.last_update = camp.day

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        myteam: teams.Team = self.elements["_eteam"]
        if camp.day > self.last_update and len(myteam.get_members_in_play(camp)) < 1 and random.randint(1,4) == 4:
            camp.scene.deploy_team(
                gears.selector.RandomMonsterUnit(self.rank, random.randint(80, 120), camp.scene.environment,
                                                 self.elements[DG_MONSTER_TAGS], camp.scene.scale).contents, myteam
            )
            self.last_update = camp.day


class GuardedTreasure(Plot):
    # Fight some random monsters. They have stuff.
    LABEL = "DUNGEON_EXTRA"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element("ROOM", self.elements[DG_ARCHITECTURE].get_a_room()(), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team2.contents += gears.selector.RandomMonsterUnit(self.rank+5, 120, myscene.environment,
                                                           self.elements[DG_MONSTER_TAGS], myscene.scale).contents
        self.last_update = 0

        mychest = self.register_element("GOAL", ghwaypoints.Crate(name="Crate", anchor=pbge.randmaps.anchors.middle), dident="ROOM")
        mychest.contents += gears.selector.get_random_loot(self.rank,100,(gears.tags.ST_TREASURE,))

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        self.last_update = camp.day

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        myteam: teams.Team = self.elements["_eteam"]
        if camp.day > self.last_update and len(myteam.get_members_in_play(camp)) < 1:
            camp.scene.deploy_team(
                gears.selector.RandomMonsterUnit(self.rank, random.randint(80, 120), camp.scene.environment,
                                                 self.elements[DG_MONSTER_TAGS], camp.scene.scale).contents, myteam
            )
            self.last_update = camp.day
