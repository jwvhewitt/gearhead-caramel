from pbge.plots import Plot
import gears
import pbge
from game import teams, ghdialogue
from game.content import ghwaypoints, gharchitecture, plotutility, dungeonmaker, ghrooms, ghterrain, ghcutscene
import random
from game.content.dungeonmaker import DG_NAME, DG_ARCHITECTURE, DG_SCENE_TAGS, DG_MONSTER_TAGS, DG_TEMPORARY, \
    DG_PARENT_SCENE, DG_EXPLO_MUSIC, DG_COMBAT_MUSIC, DG_DECOR
from pbge.dialogue import Offer, ContextTag
from game.ghdialogue import context


#   ***********************
#   ***  DUNGEON_EXTRA  ***
#   ***********************
#
# Elements:
#    LOCALE + all the dungeon elements imported above.
#

class DeadAdventurer(Plot):
    # Find a dead adventurer.
    LABEL = "DUNGEON_EXTRA"
    active = True
    scope = "LOCALE"

    UNIQUE = True

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.register_element("ROOM", self.elements[DG_ARCHITECTURE].get_a_room()(), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team2.contents += gears.selector.RandomMonsterUnit(self.rank, 150, myscene.environment,
                                                           ("ANIMAL", "VERMIN"), myscene.scale).contents
        self.last_update = 0

        mychest = self.register_element("GOAL", ghwaypoints.Skeleton(
            anchor=pbge.randmaps.anchors.middle, treasure_rank=self.rank + 5, plot_locked=True
        ), dident="ROOM")
        self.paid_respects = False
        return True

    def _eteam_ACTIVATETEAM(self, camp):
        self.last_update = camp.day

    def GOAL_menu(self, camp, thingmenu):
        if self.elements["GOAL"].plot_locked and not self.paid_respects:
            thingmenu.add_item("Pay your respects.", self._pay_respects)
            thingmenu.add_item("See if they were carrying anything useful.", self._loot_corpse)

    def _pay_respects(self, camp: gears.GearHeadCampaign):
        self.paid_respects = True
        candidates = list()
        for pc in camp.get_active_party():
            if pc is not camp.pc and isinstance(pc, gears.base.Character) and pc.get_tags().intersection(
                    {gears.tags.Faithworker, gears.personality.Fellowship}):
                candidates.append(pc)
                pc.relationship.reaction_mod += random.randint(3, 8)
        if candidates:
            speaker = random.choice(candidates)
        else:
            speaker = camp.pc
        ghcutscene.SimpleMonologueDisplay("[EULOGY]", speaker)(camp)
        camp.dole_xp(100)

    def _loot_corpse(self, camp):
        self.elements["GOAL"].plot_locked = False
        self.elements["GOAL"].unlocked_use(camp)

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        myteam: teams.Team = self.elements["_eteam"]
        if camp.day > self.last_update and len(myteam.get_members_in_play(camp)) < 1 and random.randint(1, 2) == 2:
            camp.scene.deploy_team(
                gears.selector.RandomMonsterUnit(self.rank, random.randint(80, 120), camp.scene.environment,
                                                 self.elements[DG_MONSTER_TAGS], camp.scene.scale).contents, myteam
            )
            self.last_update = camp.day


class WildernessCoffeeShop(Plot):
    LABEL = "DUNGEON_EXTRA"
    active = True
    scope = "INTERIOR"

    UNIQUE = True

    @classmethod
    def matches(cls, pstate):
        return (
                gears.tags.SCENE_OUTDOORS in pstate.elements["LOCALE"].attributes or
                cls.LABEL == "TEST_DUNGEON_EXTRA"
        )

    def custom_init(self, nart):
        # Create the shopkeeper
        npc1 = self.register_element("SHOPKEEPER", gears.selector.random_character(
            self.rank, job=gears.jobs.ALL_JOBS["Bartender"]))

        self.shopname = self._generate_shop_name()

        # Create a building within the dungeon.
        building = self.register_element(
            "_EXTERIOR", ghterrain.BrickBuilding(
                waypoints={"DOOR": ghwaypoints.WoodenDoor(name=self.shopname)},
                door_sign=(ghterrain.CafeSign1East, ghterrain.CafeSign1South)
            ),
            dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2,
            attributes=(gears.tags.SCENE_SEMIPUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_CULTURE),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.PackedBuildingGenerator(
            intscene, gharchitecture.DefaultBuilding(floor_terrain=ghterrain.HardwoodFloor)
        )
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(width=random.randint(20, 25),
                                                                              height=random.randint(11, 15),
                                                                              anchor=pbge.randmaps.anchors.south),
                                      dident="INTERIOR")

        mybar = ghrooms.BarArea(random.randint(5, 10), random.randint(2, 3), anchor=pbge.randmaps.anchors.north)
        foyer.contents.append(mybar)

        barteam = self.register_element("BAR_TEAM", teams.Team(name="Bar Team", allies=[team2]))
        mybar.contents.append(barteam)
        npc1.place(intscene, team=barteam)

        myfloor = pbge.randmaps.rooms.Room(foyer.width - 2, foyer.height - mybar.height - 2,
                                           anchor=pbge.randmaps.anchors.south,
                                           decorate=gharchitecture.RestaurantDecor())
        foyer.contents.append(myfloor)

        mycon2 = plotutility.TownBuildingConnection(
            nart, self, self.elements["LOCALE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        self.got_explanation = False
        self.coffee_price = self.rank * 10

        return True

    TITLE_PATTERNS = (
        "{SHOPKEEPER}'s Coffee", "The {DG_NAME} Rest Stop", "{SHOPKEEPER}'s Cafe", "{adjective} Beans",
        "{adjective} Coffee", "{SHOPKEEPER}'s {adjective} Cafe"
    )

    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(
            adjective=random.choice(ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]), **self.elements)

    EXPLANATIONS = (
        "Actually, I don't like working too hard, so I figured the easiest way to have an easy life would be to put my coffee shop in the middle of nowhere. It's worked well so far but the commute is a bit dangerous.",
        "You would not believe how many cavaliers we have trekking through this wilderness. I don't know what they're looking for, but they can always afford top dollar for premium coffee. Whatever you're looking for out here, I hope you find it.",
        "This coffee shop has been passed down in my family since PreZero times. I've always hoped that a village would spring up nearby, but until that day, I must continue my family tradition.",
        "Have you checked out real estate prices lately? It was either put the coffee shop here or sublet a disused sewer tunnel. The monsters outside are a bit of a bother but at least we have fresh air."
    )

    def SHOPKEEPER_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        mylist.append(Offer("[HELLO] Welcome to {}.".format(self.shopname),
                            context=ContextTag([context.HELLO]),
                            ))

        mylist.append(Offer("[OF_COURSE] That'll be ${:,}, please.".format(self.coffee_price),
                            context=ContextTag([context.CUSTOM]), subject=self, subject_start=True,
                            data={"reply": "Could we get some coffee, please?"}
                            ))

        if camp.credits >= self.coffee_price:
            mylist.append(Offer("[HERE_YOU_GO] Please enjoy your drinks.".format(self.coffee_price),
                                context=ContextTag([context.CUSTOMREPLY]), subject=self,
                                data={"reply": "Alright."}, effect=self._heal_party
                                ))

        mylist.append(Offer("Remember, our door is always open to you. [GOODBYE]".format(self.coffee_price),
                            context=ContextTag([context.CUSTOMREPLY]), subject=self,
                            data={"reply": "Maybe some other time."}
                            ))

        if not self.got_explanation:
            mylist.append(Offer(random.choice(self.EXPLANATIONS),
                                context=ContextTag([context.INFO]), effect=self._get_explanation, no_repeats=True,
                                data={"subject": "setting up a coffee shop all the way out here"}
                                ))

        return mylist

    def _heal_party(self, camp: gears.GearHeadCampaign):
        camp.credits -= self.coffee_price
        for pc in camp.get_active_party():
            pc.restore_all()
        pbge.alert("After drinking the coffee, you feel ready to get back to the adventure!")

    def _get_explanation(self, camp):
        self.got_explanation = True


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
        if camp.day > self.last_update and len(myteam.get_members_in_play(camp)) < 1 and random.randint(1, 5) != 5:
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
        team2.contents += gears.selector.RandomMonsterUnit(self.rank + 15, 75, myscene.environment,
                                                           ("ROBOT",), myscene.scale).contents
        self.last_update = 0
        self.robot_team = team2.contents

        mychest = self.register_element("GOAL", ghwaypoints.StorageBox(name="Box", anchor=pbge.randmaps.anchors.middle),
                                        dident="ROOM")
        mychest.contents += gears.selector.get_random_loot(self.rank, 100, (
        gears.tags.ST_TREASURE, gears.tags.ST_LOSTECH, gears.tags.ST_ANTIQUE))

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
            pbge.alert(
                "As you approach, the ancient robot looks at you wearily. \"RESTRICTED AREA. TERMINATION. YOU KNOW THE DEAL.\"")

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

        self.register_element("GOAL", ghwaypoints.OldTerminal(name="Ancient Computer",
                                                              desc="You stand before an ancient but still functioning computer terminal. They really used to build these things to last.",
                                                              anchor=pbge.randmaps.anchors.middle, plot_locked=True),
                              dident="ROOM")
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
        if camp.day > self.last_update and len(myteam.get_members_in_play(camp)) < 1 and random.randint(1, 4) == 4:
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
        team2.contents += gears.selector.RandomMonsterUnit(self.rank + 5, 120, myscene.environment,
                                                           self.elements[DG_MONSTER_TAGS], myscene.scale).contents
        self.last_update = 0

        mychest = self.register_element("GOAL", ghwaypoints.Crate(name="Crate", anchor=pbge.randmaps.anchors.middle),
                                        dident="ROOM")
        mychest.contents += gears.selector.get_random_loot(self.rank, 50, (gears.tags.ST_TREASURE,))

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
