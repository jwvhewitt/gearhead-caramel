#
# Some plots involving problems that affect the local metro scene. These problems generally decrease the Quality of
# Life indicators from the Metrodata object.
#

import random

import game.content.ghwaypoints
from game import content, services, teams, ghdialogue
import gears
import pbge
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain, \
    ghchallenges, ghrooms
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot, Rumor, PlotState
from pbge.memos import Memo
from . import missionbuilder, rwme_objectives
from pbge.challenges import Challenge, AutoOffer
from .shops_plus import get_building


#   ***********************
#   ***  LOCAL_PROBLEM  ***
#   ***********************
#
# Needed Elements:
#    METROSCENE, METRO, MISSION_GATE
#

class TheCursedSoil(Plot):
    LABEL = "TEST_LOCAL_PROBLEM"
    scope = "METRO"
    UNIQUE = True
    QOL = gears.QualityOfLife(health=-2, prosperity=-2)
    active = True

    RUMOR = Rumor(
        "{METROSCENE} is built on cursed land",
        offer_msg="It's obvious, isn't it? Our crops wither and die. Strange diseases afflict our people. And unlike other deadzone towns, the problems have only been getting worse instead of better.",
        memo="The residents of {METROSCENE} believe their land is cursed; crops won't grow, and inexplicable diseases affect the populace.",
        offer_subject_data="this curse", offer_subject="{METROSCENE} is built on cursed land"
    )

    @classmethod
    def matches(cls, pstate):
        return gears.personality.DeadZone in pstate.elements["METROSCENE"].attributes or \
               cls.LABEL == "TEST_LOCAL_PROBLEM"

    def custom_init(self, nart):
        # Create the mine exterior.
        outside_scene = gears.GearHeadScene(
            35, 35, plotutility.random_deadzone_spot_name(), player_team=teams.Team(name="Player Team"),
            scale=gears.scale.MechaScale, exploration_music="Lines.ogg", combat_music="Late.ogg"
        )
        myscenegen = pbge.randmaps.SceneGenerator(outside_scene, gharchitecture.MechaScaleDeadzone())
        self.register_scene(nart, outside_scene, myscenegen, ident="OUTSIDE", dident="METROSCENE")

        mygoal = self.register_element("_mine_entrance_room", pbge.randmaps.rooms.FuzzyRoom(parent=outside_scene,
                                                                                            anchor=pbge.randmaps.anchors.middle))
        mineent = self.register_element(
            "MINE_ENTRANCE",
            game.content.ghwaypoints.MechaScaleSmokingMineBuilding(anchor=pbge.randmaps.anchors.middle),
            dident="_mine_entrance_room"
        )

        self.register_element("ENTRANCE_ROOM",
                              pbge.randmaps.rooms.OpenRoom(5, 5, anchor=random.choice(pbge.randmaps.anchors.EDGES)),
                              dident="OUTSIDE")
        myent = self.register_element(
            "ENTRANCE",
            game.content.ghwaypoints.Exit(dest_wp=self.elements["MISSION_GATE"], anchor=pbge.randmaps.anchors.middle),
            dident="ENTRANCE_ROOM"
        )

        # Generate the in-between first level of the mine.
        inside_scene = gears.GearHeadScene(
            50, 50, "{OUTSIDE} Mine".format(**self.elements), player_team=teams.Team(name="Player Team"),
            scale=gears.scale.HumanScale, exploration_music="Lines.ogg", combat_music="Late.ogg",
            attributes=(gears.tags.SCENE_BUILDING, gears.tags.SCENE_MINE, gears.tags.SCENE_SEMIPUBLIC)
        )
        myscenegen2 = pbge.randmaps.SceneGenerator(inside_scene, gharchitecture.IndustrialBuilding(
            decorate=gharchitecture.FactoryDecor()))
        self.register_scene(nart, inside_scene, myscenegen2, ident="INSIDE", dident="OUTSIDE")

        foyer = pbge.randmaps.rooms.ClosedRoom(parent=inside_scene, anchor=pbge.randmaps.anchors.south)
        way_down = pbge.randmaps.rooms.ClosedRoom(parent=inside_scene)
        surprise = pbge.randmaps.rooms.ClosedRoom(parent=inside_scene)
        monteam = teams.Team(enemies=[inside_scene.player_team, ])
        monteam.contents += gears.selector.RandomMonsterUnit(
            self.rank, 100, gears.tags.GroundEnv, ("RUINS", "CAVE", "TOXIC", "MUTANT"), gears.scale.HumanScale
        ).contents
        surprise.contents.append(monteam)
        equipment_room = pbge.randmaps.rooms.ClosedRoom(parent=inside_scene,
                                                        decorate=gharchitecture.UlsaniteOfficeDecor())

        # Generate the dungeon.
        my_dungeon = dungeonmaker.DungeonMaker(
            nart, self, self.elements["INSIDE"], "Toxic Caves".format(**self.elements),
            gharchitecture.EarthCave(decorate=gharchitecture.ToxicCaveDecor(), gapfill=pbge.randmaps.gapfiller.RoomFiller(ghrooms.ToxicSludgeRoom, spacing=2)),
            self.rank, monster_tags=("ANIMAL", "CAVE", "TOXIC", "MUTANT", "EARTH"),
            decor=None, scene_tags=(gears.tags.SCENE_DUNGEON, gears.tags.SCENE_MINE)
        )
        goal_level = self.register_element("_fake_goal_level", my_dungeon.goal_level)
        p_goal_room = self.register_element(
            "_pentultimate_goal_room", pbge.randmaps.rooms.OpenRoom(decorate=gharchitecture.FactoryDecor()),
            dident="_fake_goal_level"
        )
        hatch = ghwaypoints.Trapdoor(name="The Hatch", anchor=pbge.randmaps.anchors.middle)
        p_goal_room.contents.append(hatch)

        final_level = gears.GearHeadScene(
            50, 50, "PreZero Factory", player_team=teams.Team(name="Player Team"),
            scale=gears.scale.HumanScale, exploration_music="Lines.ogg", combat_music="Late.ogg",
            attributes=(gears.tags.SCENE_DUNGEON, gears.tags.SCENE_RUINS)
        )
        myscenegen3 = pbge.randmaps.SceneGenerator(
            final_level, gharchitecture.ScrapIronWorkshop(decorate=gharchitecture.RundownChemPlantDecor())
        )
        self.register_scene(nart, final_level, myscenegen3, ident="FINAL_LEVEL", dident="_fake_goal_level")

        bossroom = pbge.randmaps.rooms.ClosedRoom(16, 16, parent=final_level)
        monteam2 = self.register_element("BOSSTEAM", teams.Team(enemies=[final_level.player_team, ]))
        monteam2.contents += gears.selector.RandomMonsterUnit(
            self.rank + 15, 100, gears.tags.GroundEnv, ("RUINS", "ROBOT", "SYNTH", "TOXIC", "MUTANT"),
            gears.scale.HumanScale
        ).contents
        bossroom.contents.append(monteam2)
        myboss = self.register_element("SMOGSPEWER", gears.selector.get_design_by_full_name("SMG-01 SmogSpewer"))
        monteam2.contents.append(myboss)

        # Connect everything.
        mycon = plotutility.TownBuildingConnection(
            nart, self, outside_scene, inside_scene, room1=mygoal, room2=foyer,
            door1=mineent, move_door1=False)

        mycon2 = plotutility.StairsDownToStairsUpConnector(
            nart, self, inside_scene, my_dungeon.entry_level, room1=way_down
        )

        mycon3 = plotutility.StairsDownToStairsUpConnector(
            nart, self, goal_level, final_level, room1=p_goal_room, door1=hatch, move_door1=False
        )

        self.add_sub_plot(nart, "REVEAL_LOCATION", ident="FINDMINE", elements={
            "LOCALE": outside_scene,
            "INTERESTING_POINT": "The old abandoned mine there was spewing toxic smoke. It didn't look safe."
        })

        self.found_mine = False
        self.got_final_level_message = False
        self.defeated_smogspewer = False

        return True

    def FINDMINE_WIN(self, camp):
        self.RUMOR = None
        self.memo = Memo("Toxic smoke is pouring out of an abandoned mine at {OUTSIDE}.".format(**self.elements),
                         self.elements["OUTSIDE"])
        self.found_mine = True

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.found_mine:
            thingmenu.add_item("Go to {OUTSIDE}.".format(**self.elements), self._go_to_mine)

    def FINAL_LEVEL_ENTER(self, camp):
        if not self.got_final_level_message:
            pbge.alert(
                "You have discovered a PreZero ruin. The miners must have tunneled into here before the mine shut down.")
            self.got_final_level_message = True

    def _go_to_mine(self, camp):
        camp.go(self.elements["ENTRANCE"])

    def SMOGSPEWER_FAINT(self, camp):
        pbge.alert("That should do it...")
        self.elements["MINE_ENTRANCE"].turn_off_smoke()
        self.QOL = gears.QualityOfLife(prosperity=1)


class DeadzoneDefenseSpending(Plot):
    LABEL = "LOCAL_PROBLEM"
    scope = "METRO"
    UNIQUE = True
    QOL = gears.QualityOfLife(defense=-2)
    active = True

    RUMOR = Rumor(
        "{NPC} has been designing {BUILDING_NAME}",
        offer_msg="As you know, {METROSCENE}'s defenses aren't great. So {NPC} had the brilliant idea to build {BUILDING_NAME}. But work has been going slow so far; maybe you can talk to {NPC.gender.object_pronoun} about it at {NPC_SCENE}.",
        memo="{NPC} is designing {BUILDING_NAME} for {METROSCENE}, but progress is slow.",
        prohibited_npcs=("NPC",)
    )

    PROJECTS = (
        {"BUILDING_NAME": "a new hangar", "BUILDING_NEED": "the town needs to expand its mecha force"},
        {"BUILDING_NAME": "anti-mek artillery", "BUILDING_NEED": "this will help protect the town center"},
        {"BUILDING_NAME": "long range sensors", "BUILDING_NEED": "right now the town can't detect incoming raiders"},
        {"BUILDING_NAME": "a mecha workshop", "BUILDING_NEED": "this will keep the town militia well equipped"},
        {"BUILDING_NAME": "a ginormous laser cannon", "BUILDING_NEED": "the town can use it to zap invaders"}
    )

    @classmethod
    def matches(cls, pstate):
        return gears.personality.DeadZone in pstate.elements["METROSCENE"].attributes or \
               cls.LABEL == "TEST_LOCAL_PROBLEM"

    def custom_init(self, nart):
        # Step one: Create the architect.
        scene = self.seek_element(
            nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"],
            backup_seek_func=self._is_ok_scene
        )

        npc = self.register_element(
            "NPC",
            gears.selector.random_character(
                rank=random.randint(self.rank, self.rank + 10), job=gears.jobs.ALL_JOBS["Architect"],
                mecha_colors=gears.color.random_mecha_colors(),
                local_tags=tuple(self.elements["METROSCENE"].attributes),
            ), dident="NPC_SCENE")

        # Step two: Decide on a project.
        project = random.choice(self.PROJECTS)
        self.elements.update(project)

        # Step three: Prepare the challenge starter.
        self.add_sub_plot(nart, "MAKE_BUILDING_STARTER", ident="MAKE_BUILDING")

        self.original_faction = self.elements["METROSCENE"].faction
        self.started_building = False

        return True

    def t_UPDATE(self, camp):
        # If this city gets taken over by some other faction, this building project gets cancelled. :(
        if self.elements["METROSCENE"].faction is not self.original_faction:
            self.end_plot(camp, True)

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
                and gears.tags.SCENE_GOVERNMENT in candidate.attributes)

    def _is_ok_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def NPC_offers(self, camp):
        mylist = list()

        if not self.started_building:
            mylist.append(Offer(
                "[HELLO] I tell you, it's impossible to get people to cooperate in {METROSCENE}, no matter how important the project is.".format(
                    **self.elements),
                ContextTag([context.HELLO])
            ))

            mylist.append(Offer(
                "I've been designing {BUILDING_NAME} to defend {METROSCENE}. Obviously, {BUILDING_NEED}. The plans are ready but work has barely begun.".format(
                    **self.elements),
                ContextTag([context.CUSTOM]), subject_start=True, subject=self,
                data={"reply": "What are you working on?"}
            ))

            mylist.append(Offer(
                "Please do so. I know we have enough laborers and craftspeople in {METROSCENE}; I'm just not sure we have all the required materials.".format(
                    **self.elements),
                ContextTag([context.CUSTOMREPLY]), subject=self, effect=self._start_mission,
                data={"reply": "Maybe I could try to convince some people to hurry up."}
            ))

            mylist.append(Offer(
                "[GOODBYE] Hopefully the job will get finished before the next time {METROSCENE} is invaded.".format(
                    **self.elements),
                ContextTag([context.CUSTOMREPLY]), subject=self, dead_end=True,
                data={"reply": "Well, good luck on that."}
            ))

        return mylist

    def _start_mission(self, camp):
        self.subplots["MAKE_BUILDING"].activate(camp)
        self.started_building = True
        self.RUMOR = None
        self.memo = None

    def MAKE_BUILDING_WIN(self, camp):
        pbge.alert("{METROSCENE} has finally completed work on {BUILDING_NAME}.".format(**self.elements))
        self.end_plot(camp, True)
        if self.elements["NPC"].is_operational():
            content.load_dynamic_plot(camp, "POST_PLOT_REWARD", PlotState().based_on(
                self,
                update_elements={"PC_REPLY": "{METROSCENE} has constructed {BUILDING_NAME}.".format(**self.elements)}
            ))


class SregorThrunet(Plot):
    LABEL = "LOCAL_PROBLEM"
    scope = "METRO"
    UNIQUE = True
    QOL = gears.QualityOfLife(prosperity=-3)
    active = True

    RUMOR = Rumor(
        "thanks to {NPC}, the Thrunet has been really unstable lately",
        offer_msg="{NPC} is the {NPC.job} responsible for keeping our local data node running. But these days I can't even get the latest matches from Warhammer Arena. Could you go have a talk with {NPC.gender.object_pronoun} at {NPC_SCENE}?",
        memo="The Thrunet service in {METROSCENE} is unreliable; people blame {NPC}.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(cls, pstate):
        return gears.personality.DeadZone in pstate.elements["METROSCENE"].attributes or \
               cls.LABEL == "TEST_LOCAL_PROBLEM"

    JOBS = ("Mechanic", "Buttonpusher", "Tekno", "Hacker", "Buttonpusher", "Tekno")

    def custom_init(self, nart):
        # Create the shopkeeper
        npc1 = self.register_element("NPC", gears.selector.random_character(
            self.rank, local_tags=self.elements["LOCALE"].attributes,
            job=gears.jobs.ALL_JOBS[random.choice(self.JOBS)]))

        self.shopname = self._generate_shop_name()

        # Create a building within the town.
        building = self.register_element("_EXTERIOR", get_building(
            self, ghterrain.ScrapIronBuilding,
            waypoints={"DOOR": ghwaypoints.WoodenDoor(name=self.shopname)},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP, pbge.randmaps.IS_CITY_ROOM,
                  pbge.randmaps.IS_CONNECTED_ROOM]),
                                         dident="METROSCENE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, self.shopname, player_team=team1, civilian_team=team2,
            attributes=(gears.tags.SCENE_PUBLIC, gears.tags.SCENE_BUILDING, gears.tags.SCENE_RUINS),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(
            intscene, gharchitecture.ScrapIronWorkshop(floor_terrain=ghterrain.GrateFloor,
                                                       decorate=gharchitecture.FactoryDecor())
        )
        self.register_scene(nart, intscene, intscenegen, ident="NPC_SCENE", dident="METROSCENE")
        foyer = self.register_element('FOYER', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,
                                                                              decorate=gharchitecture.FactoryDecor()),
                                      dident="NPC_SCENE")
        foyer.contents.append(team2)

        mycon = plotutility.TownBuildingConnection(
            nart, self, self.elements["METROSCENE"], intscene, room1=building,
            room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc1.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc1, ware_types=services.MECHA_PARTS_STORE,
                                  rank=self.rank + random.randint(0, 15))

        foyer.contents.append(ghwaypoints.MechEngTerminal())

        self.thrunet_broken = True
        self.npc_impressed = False
        self.deserve_reward = True

        # Generate the dungeon.
        my_dungeon = dungeonmaker.DungeonMaker(
            nart, self, intscene, "{METROSCENE} Undercity".format(**self.elements),
            gharchitecture.DefaultBuilding(floor_terrain=ghterrain.GrateFloor,
                                           decorate=gharchitecture.TechDungeonDecor()),
            self.rank, monster_tags=("ROBOT", "FACTORY", "RUINS", "MUTANT", "EARTH"),
            decor=None
        )
        goal_level = self.register_element("_goal_level", my_dungeon.goal_level)
        goal_room = self.register_element(
            "_goal_room", pbge.randmaps.rooms.ClosedRoom(decorate=gharchitecture.FactoryDecor()), dident="_goal_level"
        )
        bossteam = self.register_element("_eteam", teams.Team(enemies=(goal_level.player_team,)), dident="_goal_room")
        bossteam.contents += gears.selector.RandomMonsterUnit(self.rank + 20, 200, gears.tags.GroundEnv,
                                                              ("ROBOT", "ZOMBOT"), gears.scale.HumanScale).contents
        self.started_combat = False

        main_server = self.register_element(
            "SERVER",
            ghwaypoints.OldMainframe(
                plot_locked=True, anchor=pbge.randmaps.anchors.middle, name="Thrunet Server",
                desc="You stand before an ancient ThruNet server, part of the shadow net that dates back to the Age of Superpowers."
            ),
            dident="_goal_room"
        )

        droom = self.register_element('DUNGEON_ROOM',
                                      pbge.randmaps.rooms.ClosedRoom(decorate=gharchitecture.DefiledFactoryDecor()),
                                      dident="NPC_SCENE")

        mycon2 = plotutility.StairsDownToStairsUpConnector(
            nart, self, intscene, my_dungeon.entry_level, room1=droom
        )

        roboroom = self.register_element('ROBOT_ROOM',
                                         pbge.randmaps.rooms.ClosedRoom(decorate=gharchitecture.UlsaniteOfficeDecor()),
                                         dident="NPC_SCENE")
        roboteam = self.register_element("ROBOTEAM", teams.Team("RobotTeam"), dident="ROBOT_ROOM")
        roboforce = gears.selector.RandomMonsterUnit(self.rank + 30, 50, gears.tags.GroundEnv, ("ROBOT",),
                                                     gears.scale.HumanScale)
        roboteam.contents += roboforce.contents

        return True

    TITLE_PATTERNS = (
        "{METROSCENE} Computing", "{METROSCENE} Electronics", "{NPC}'s Telecom", "{NPC}'s Lostech",
        "{adjective} Thrunet", "{METROSCENE} Data Center", "{adjective} Salvage",
        "{NPC}'s Data Mine", "{adjective} Bits", "Comm Center {METROSCENE}", "{adjective} Data Mine",
        "{NPC}'s {adjective} Computers", "{adjective} Recycling", "{NPC}'s Upcycling"
    )

    def _generate_shop_name(self):
        return random.choice(self.TITLE_PATTERNS).format(
            adjective=random.choice(ghdialogue.ghgrammar.DEFAULT_GRAMMAR["[Adjective]"][None]),
            **self.elements)

    def NPC_offers(self, camp):
        mylist = list()

        if self.thrunet_broken:
            mylist.append(Offer(
                "[HELLO] What do you want?! The Thrunet node for {METROSCENE} is down and everyone thinks I know how to fix it.".format(
                    **self.elements),
                context=ContextTag([context.HELLO]),
                ))

            if not self.npc_impressed:
                mylist.append(Offer(
                    "[LISTEN_UP] I work with broken machines every day, I can strip every piece of usable gear out of a salvaged wreck. Everyone comes to the dead zone hoping to find lostech and strike it rich, but do you know what the biggest and most important piece of lostech is?",
                    context=ContextTag([context.CUSTOM]), subject=self, subject_start=True,
                    data={"reply": "I would like to talk about the Thrunet, actually."}
                ))

                mylist.append(Offer(
                    "It's the Thrunet. Sure, we still know how computers work, but about half the data traffic on Earth goes through PreZero nodes that we don't even know where they are. Or what they're doing, for that matter. And the data node deep under this building has decided to go bonky-wook.",
                    context=ContextTag([context.CUSTOMREPLY]), subject=self,
                    data={"reply": "[I_DONT_KNOW]"}
                ))

                ghdialogue.SkillBasedPartyReply(Offer(
                    "You know your stuff. Yeah, we don't even know where half the Thrunet nodes on Earth are- they date to PreZero times, and we lose more every year. We're building new ones but not fast enough. The node deep under this building has conked out, and I was hoping I could fix it from up here, but that doesn't seem likely.",
                    context=ContextTag([context.CUSTOMREPLY]), subject=self, effect=self._impress_npc,
                    data={"reply": "It's the Thrunet. Or the shadow Thrunet, at least."}
                ), camp, mylist, gears.stats.Knowledge, gears.stats.Computers, self.rank, gears.stats.DIFFICULTY_HARD)

            mylist.append(Offer(
                "This place is the top floor of what I guess was a PreZero office tower. The main server is right at the bottom. Unfortunately, the further down you go, the more dangerous it gets. You're a cavalier- why don't you go down and see if you can fix things?",
                context=ContextTag([context.INFO]), subject="deep under this building",
                data={"subject": "the place under this building"}, no_repeats=True, dead_end=True
            ))

        mylist.append(Offer("[OPENSHOP]",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop,
                            data={"shop_name": self.shopname, "wares": "salvage"},
                            ))

        if self.deserve_reward and not self.thrunet_broken:
            mylist.append(Offer(
                "[THANKS_FOR_HELP] And I wouldn't call it a dungeon; it's more of a basement I can't enter because it might kill me. Here's a reward for your service.",
                context=ContextTag([context.CUSTOM]), effect=self._get_reward,
                data={"reply": "We've fixed the server at the bottom of your dungeon."}
            ))

        return mylist

    def _get_reward(self, camp: gears.GearHeadCampaign):
        self.memo = None
        self.deserve_reward = False
        camp.credits += gears.selector.calc_mission_reward(self.rank, 250)
        npc: gears.base.Character = self.elements["NPC"]
        npc.relationship.history.append(gears.relationships.Memory(
            "you fixed the PreZero server in my basement",
            "I fixed the ancient computer in your dungeon",
            20, (gears.relationships.MEM_AidedByPC,)
        ))

    def _impress_npc(self, camp):
        if not self.npc_impressed:
            npc: gears.base.Character = self.elements["NPC"]
            npc.relationship.reaction_mod += 20
            self.npc_impressed = True

    def _eteam_ACTIVATETEAM(self, camp):
        if not self.started_combat:
            self.started_combat = True
            pbge.alert(
                "As you approach the control room, you see a procession of robots circling the main server, emitting bleeps in binaric code... almost as if they were worshipping it.")

    def SERVER_menu(self, camp: gears.GearHeadCampaign, thingmenu):
        if self.thrunet_broken:
            thingmenu.desc += " From the blinking lights on the panel, you can tell that it is not working properly."

            if camp.make_skill_roll(gears.stats.Craft, gears.stats.Computers, self.rank, no_random=True):
                thingmenu.add_item("Reboot the server.", self._repair_server)

            if camp.make_skill_roll(gears.stats.Craft, gears.stats.Science, self.rank, no_random=True,
                                    difficulty=gears.stats.DIFFICULTY_HARD):
                thingmenu.add_item("Attempt to update the code.", self._repair_server)

            if camp.make_skill_roll(gears.stats.Knowledge, gears.stats.Repair, self.rank, no_random=True,
                                    difficulty=gears.stats.DIFFICULTY_HARD):
                thingmenu.add_item("Try unplugging it and plugging it back in again.", self._repair_server)

        thingmenu.add_item("Leave it alone.", None)

    def _repair_server(self, camp: gears.GearHeadCampaign):
        pbge.my_state.view.play_anims(gears.geffects.OverloadAnim(pos=self.elements["SERVER"].pos))
        self.thrunet_broken = False
        self.QOL = gears.QualityOfLife(prosperity=3)
        self.RUMOR = None
        self.memo = Memo("You fixed {NPC}'s Thrunet server.".format(**self.elements), self.elements["NPC_SCENE"])
        pbge.alert(
            "With a loud beep and a few more sparks than you're comfortable with, the Thrunet server roars back into action. It seems you have successfully repaired it.")
        camp.dole_xp(100)


class ClassicMurderMystery(Plot):
    LABEL = "LOCAL_PROBLEM"
    scope = "METRO"
    UNIQUE = True
    QOL = gears.QualityOfLife(stability=-3)
    active = True

    WEAPON_CARDS = (
        {"name": "Pistol", "to_verb": "to shoot {}", "verbed": "shot {}",
         "did_not_verb": "didn't shoot {}", "data": {"image_name": "mystery_weapons.png", "frame": 0}},
        {"name": "Axe", "to_verb": "to axe {}", "verbed": "hit {} with an axe",
         "did_not_verb": "didn't have an axe", "data": {"image_name": "mystery_weapons.png", "frame": 1}},
        {"name": "Poison", "to_verb": "to poison {}", "verbed": "poisoned {}",
         "did_not_verb": "didn't poison {}", "data": {"image_name": "mystery_weapons.png", "frame": 2}},
        {"name": "Hydrospanner", "to_verb": "to bludgeon {}",
         "verbed": "bludgeoned {} with a hydrospanner",
         "did_not_verb": "didn't own a hydrospanner", "data": {"image_name": "mystery_weapons.png", "frame": 3}},
        {"name": "Workbot", "to_verb": "to send a workbot to kill {}",
         "verbed": "sent a workbot to kill {}",
         "did_not_verb": "didn't use a workbot", "data": {"image_name": "mystery_misc.png", "frame": 6}},
    )

    MOTIVE_CARDS = (
        {"name": "Revenge", "to_verb": "to get revenge on {}", "verbed": "got revenge on {}",
         "did_not_verb": "didn't get revenge on {}", "data": {"image_name": "mystery_motives.png", "frame": 9,
                                                              "excuse": "{VICTIM} was rude to me in middle school..."},
         "role": pbge.okapipuzzle.SUS_MOTIVE},
        {"name": "Money", "to_verb": "to get {}'s money", "verbed": "took {}'s money'",
         "did_not_verb": "didn't take {}'s money", "data": {"image_name": "mystery_motives.png", "frame": 8,
                                                            "excuse": "{VICTIM} had tons of money, and I can share it..."},
         "role": pbge.okapipuzzle.SUS_MOTIVE},
        {"name": "Hatred", "to_verb": "to be rid of {}", "verbed": "hated {}",
         "did_not_verb": "didn't hate {}", "data": {"image_name": "mystery_motives.png", "frame": 0,
                                                    "excuse": "All I'll say is that {VICTIM} deserved it..."},
         "role": pbge.okapipuzzle.SUS_MOTIVE},
        {"name": "Secret", "to_verb": "to protect their secrets",
         "verbed": "was being blackmailed by {}",
         "did_not_verb": "didn't have any secrets", "data": {"image_name": "mystery_motives.png", "frame": 1,
                                                             "excuse": "{VICTIM} had some dirty info on me..."}},
        {"name": "Jealousy", "to_verb": "to protect their status",
         "verbed": "was jealous of {}",
         "did_not_verb": "wasn't jealous of {}", "data": {"image_name": "mystery_motives.png", "frame": 2,
                                                          "excuse": "Why should {VICTIM} be more successful than me?!"}},
    )

    def custom_init(self, nart):
        # Start by creating the mystery!
        metroscene = self.elements["METROSCENE"]

        victim_name = self.register_element("VICTIM", gears.selector.GENERIC_NAMES.gen_word())

        suspect_cards = list()
        for t in range(5):
            myplot = self.add_sub_plot(nart, "ADD_BORING_NPC")
            npc = myplot.elements["NPC"]
            suspect_cards.append(ghchallenges.NPCSusCard(npc))

        suspect_susdeck = pbge.okapipuzzle.SusDeck("Suspect", suspect_cards)

        weapon_cards = list()
        weapon_source = random.sample(self.WEAPON_CARDS, 5)
        for wcd in weapon_source:
            for k, v in wcd.items():
                if isinstance(v, str):
                    wcd[k] = v.format(victim_name)
            weapon_cards.append(pbge.okapipuzzle.VerbSusCard(**wcd))
        weapon_susdeck = pbge.okapipuzzle.SusDeck("Weapon", weapon_cards)

        motive_cards = list()
        motive_source = random.sample(self.MOTIVE_CARDS, 5)
        for mcd in motive_source:
            for k, v in mcd.items():
                if isinstance(v, str):
                    mcd[k] = v.format(victim_name)
            motive_cards.append(pbge.okapipuzzle.VerbSusCard(**mcd))
        motive_susdeck = pbge.okapipuzzle.SusDeck("Motive", motive_cards)

        mymystery = self.register_element("MYSTERY", pbge.okapipuzzle.OkapiPuzzle(
            "{}'s Murder".format(victim_name),
            (suspect_susdeck, weapon_susdeck, motive_susdeck), "{a} {b.verbed} {c.to_verb}."
        ))

        # Store the culprit.
        self.elements["CULPRIT"] = mymystery.solution[0].gameob

        # Now, we subcontract the actual mystery challenge out to a utility plot.
        self.add_sub_plot(nart, "MURDER_MYSTERY_CHALLENGE", ident="MCHALLENGE")

        self.mystery_solved = False
        self.mchallenge_won = False
        return True

    def MYSTERY_SOLVED(self, camp):
        self.mystery_solved = True
        self.memo = Memo(
            "You learned that {MYSTERY.solution_text}".format(**self.elements), location=self.elements["CULPRIT"].scene
        )

    def MCHALLENGE_WIN(self, camp: gears.GearHeadCampaign):
        camp.freeze(self.elements["CULPRIT"])
        self.end_plot(camp, True)

    def CULPRIT_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        mystery: pbge.okapipuzzle.OkapiPuzzle = self.elements["MYSTERY"]
        bribe = gears.selector.calc_mission_reward(self.rank, 500)
        if self.mystery_solved:
            mylist.append(Offer(
                "Don't go to the authorities yet. {} I'll offer ${:,} for you to let me go.".format(
                    mystery.solution[2].data["excuse"].format(**self.elements), bribe),
                ContextTag([context.CUSTOM]), data={"reply": "I know you {}.".format(mystery.solution[1].verbed)},
                subject=self, subject_start=True
            ))

            mylist.append(Offer(
                "[I_WOULD_HAVE_GOTTEN_AWAY]",
                ContextTag([context.CUSTOMREPLY]), data={"reply": "No deal. You will pay for your crime."},
                subject=self, effect=self._catch_culprit, dead_end=True
            ))

            mylist.append(Offer(
                "[PLEASURE_DOING_BUSINESS]",
                ContextTag([context.CUSTOMREPLY]), data={"reply": "That sounds like a good deal."},
                subject=self, effect=self._release_culprit, dead_end=True
            ))

            mylist.append(Offer(
                "Let me know when you've come to a decision.",
                ContextTag([context.CUSTOMREPLY]), data={"reply": "I'll think about it."},
                subject=self, dead_end=True
            ))

        return mylist

    def _catch_culprit(self, camp):
        camp.dole_xp(100)
        reward = gears.selector.calc_mission_reward(self.rank, 150)
        camp.credits += reward
        camp.freeze(self.elements["CULPRIT"])
        pbge.alert(
            "For catching {}, you earn ${:,}.".format(self.elements["CULPRIT"], reward))
        self.end_plot(camp, True)

    def _release_culprit(self, camp: gears.GearHeadCampaign):
        camp.credits += gears.selector.calc_mission_reward(self.rank, 500)
        content.load_dynamic_plot(camp, "CONSEQUENCE_INJUSTICE", PlotState().based_on(self))
        self.end_plot(camp, True)


class ThePlague(Plot):
    LABEL = "LOCAL_PROBLEM"
    scope = "METRO"
    UNIQUE = True
    QOL = gears.QualityOfLife(health=-3)
    active = True

    RUMOR = Rumor(
        "{METROSCENE} is going through an epidemic of {DISEASE}",
        offer_msg="It's terrible; and to make matters worse, the only reliable cure for {DISEASE} is {THECURE}. {METROSCENE} has just about run out.",
        memo="{METROSCENE} is going through an epidemic of {DISEASE}, and the only cure is {THECURE}.",
        memo_location="METROSCENE",
        offer_subject="{DISEASE}", offer_subject_data="{DISEASE}", offer_effect_name="rumor_fun"
    )

    def custom_init(self, nart):
        self.elements["DISEASE"] = plotutility.random_disease_name()
        self.elements["THECURE"] = plotutility.random_medicine_name()

        self.add_sub_plot(nart, "EPIDEMIC_STARTER", ident="EPIDEMIC")
        self.add_sub_plot(nart, "MAKE_DRUGS_STARTER", ident="MAKE_DRUGS")

        return True

    def rumor_fun(self, camp):
        self.subplots["EPIDEMIC"].activate(camp)
        self.subplots["MAKE_DRUGS"].activate(camp)

    def EPIDEMIC_WIN(self, camp):
        pbge.alert("The epidemic appears to be under control now.")
        self.end_plot(camp, True)

    def MAKE_DRUGS_WIN(self, camp):
        pbge.alert("{METROSCENE} now has enough {THECURE} to bring {DISEASE} under control.".format(**self.elements))
        self.end_plot(camp, True)

    def _get_dialogue_grammar(self, npc: gears.base.Character, camp: gears.GearHeadCampaign):
        mygram = dict()

        mygram["[CURRENT_EVENTS]"] = [
            "Stand back... I don't want to catch {DISEASE}.".format(**self.elements),
            "There's been an outbreak of {DISEASE} in {METROSCENE}... If a cure isn't found, then we are doomed.".format(
                **self.elements),
        ]

        return mygram


class RabbleRouser(Plot):
    LABEL = "LOCAL_PROBLEM"
    scope = "METRO"
    UNIQUE = True
    QOL = gears.QualityOfLife(community=-3)
    active = True

    RUMOR = Rumor(
        "{NPC} has been spreading a baseless conspiracy theory",
        offer_msg="You can speak to {NPC} at {NPC_SCENE} if you want to find out for yourself.",
        memo="{NPC} has been expounding a conspiracy theory and stirring up local resentment against {METROSCENE} leader {LEADER}.",
        prohibited_npcs=("NPC",)
    )

    @classmethod
    def matches(self, pstate):
        return "METRO" in pstate.elements and isinstance(pstate.elements["METRO"].city_leader, gears.base.Character)

    def custom_init(self, nart):
        # Start by creating and placing the rabble-rouser.
        scene = self.seek_element(
            nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"],
            backup_seek_func=self._is_ok_scene
        )

        metroscene = self.elements["METROSCENE"]
        self.conspiracy = content.backstory.Backstory(
            commands=("CONSPIRACY",), elements={"LOCALE": metroscene}, keywords=metroscene.get_keywords()
        )

        npc = self.register_element(
            "NPC",
            gears.selector.random_character(
                rank=random.randint(10, 50), job=gears.jobs.ALL_JOBS["Pundit"],
                mecha_colors=gears.color.random_mecha_colors(),
                local_tags=tuple(self.elements["METROSCENE"].attributes),
            ), dident="NPC_SCENE")

        # Also save the leader in this plot.
        leader = self.elements["LEADER"] = self.elements["METRO"].city_leader

        # Find a military/police person in this city.
        guard = self.seek_element(
            nart, "GUARD", self._is_best_guard, scope=self.elements["METROSCENE"], must_find=False
        )
        if not guard:
            myplot = self.add_sub_plot(nart, "PLACE_LOCAL_REPRESENTATIVES",
                                       elements={"LOCALE": self.elements["METROSCENE"],
                                                 "FACTION": self.elements["METROSCENE"].faction})
            guard = myplot.elements["NPC"]
            self.elements["GUARD"] = guard

        # Why not add a tycoon and a rival politician as well?
        self.seek_element(
            nart, "_TYCOON_SCENE", self._is_ok_scene, scope=self.elements["METROSCENE"]
        )
        tycoon = self.register_element(
            "TYCOON",
            gears.selector.random_character(
                rank=random.randint(10, 50), job=gears.jobs.ALL_JOBS["Corporate Executive"],
                mecha_colors=gears.color.random_mecha_colors(),
                local_tags=tuple(self.elements["METROSCENE"].attributes),
            ), dident="_TYCOON_SCENE")

        self.seek_element(
            nart, "_RIVAL_SCENE", self._is_ok_scene, scope=self.elements["METROSCENE"]
        )
        rival = self.register_element(
            "RIVAL",
            gears.selector.random_character(
                rank=random.randint(10, 50), job=gears.jobs.ALL_JOBS["Bureaucrat"],
                mecha_colors=gears.color.random_mecha_colors(),
                local_tags=tuple(self.elements["METROSCENE"].attributes),
            ), dident="_RIVAL_SCENE")

        # Now, we don't know yet whether the rabble-rouser is in the right to be raising rabble, so we're going to
        # add a mystery to find out.
        suspect_cards = [ghchallenges.NPCSusCard(c) for c in (npc, leader, guard, tycoon, rival)]
        suspect_susdeck = pbge.okapipuzzle.SusDeck("Suspect", suspect_cards)

        action_cards = [
            ghchallenges.VerbSusCardFeaturingNPC("Hire {}".format(npc), "to hire {}".format(npc),
                                                 "hired {}".format(npc), "did not hire {}".format(npc), npc),
            ghchallenges.VerbSusCardFeaturingNPC("Bribery", "to bribe {}".format(guard), "bribed {}".format(guard),
                                                 "did not bribe {}".format(guard), guard),
            pbge.okapipuzzle.VerbSusCard("Spread Lies", "to spread lies", "spread lies", "didn't spread lies",
                                         data={"image_name": "mystery_verbs.png", "frame": 6}),
            pbge.okapipuzzle.VerbSusCard("Embezzled", "to embezzle", "embezzled government funds",
                                         "didn't embezzle anything",
                                         data={"image_name": "mystery_verbs.png", "frame": 7}, gameob=npc),
            pbge.okapipuzzle.VerbSusCard("Sow Chaos", "to sow chaos in {}".format(self.elements["METROSCENE"]),
                                         "sowed chaos in {}".format(self.elements["METROSCENE"]),
                                         "did not cause chaos in {}".format(self.elements["METROSCENE"]),
                                         data={"image_name": "mystery_verbs.png", "frame": 8})
        ]
        action_susdeck = pbge.okapipuzzle.SusDeck("Action", action_cards)

        motive_cards = [
            pbge.okapipuzzle.VerbSusCard(
                "Keep Power", "to maintain power", "maintained control", "didn't try to maintain power",
                data={"image_name": "mystery_motives.png", "frame": 6}, role=pbge.okapipuzzle.SUS_MOTIVE
            ),
            pbge.okapipuzzle.VerbSusCard(
                "Take Over", "to usurp control of {}".format(self.elements["METROSCENE"]), "usurped control",
                "didn't try to usurp power",
                data={"image_name": "mystery_motives.png", "frame": 7}, role=pbge.okapipuzzle.SUS_MOTIVE
            ),
            pbge.okapipuzzle.VerbSusCard(
                "Pay Debts", "to pay off gambling debts", "paid off gambling debts", "didn't have gambling debts",
                data={"image_name": "mystery_verbs.png", "frame": 5}, role=pbge.okapipuzzle.SUS_MOTIVE
            ),
            ghchallenges.VerbSusCardFeaturingNPC(
                "Get Revenge", "to get revenge on {}".format(leader),
                "got revenge", "didn't try to get revenge on {}".format(leader), leader,
                role=pbge.okapipuzzle.SUS_MOTIVE
            ),
            pbge.okapipuzzle.VerbSusCard(
                "Become Rich", "to enrich themself", "enriched themself", "didn't get rich",
                data={"image_name": "mystery_motives.png", "frame": 8}, role=pbge.okapipuzzle.SUS_MOTIVE
            )
        ]
        motive_susdeck = pbge.okapipuzzle.SusDeck("Motive", motive_cards)

        # We are going to create the solution here because we need to error-check unreasonable cases.
        solution = [random.choice(suspect_cards), random.choice(action_cards), random.choice(motive_cards)]
        if random.randint(1, 2) == 1:
            # The guilty party is most likely going to be the leader or the rabblerouser.
            solution[0] = random.choice(suspect_cards[:2])

        while solution[1].gameob is solution[0].gameob:
            solution[1] = random.choice(action_cards)

        if solution[0].gameob is leader:
            if solution[2] is motive_cards[1]:
                solution[2] = motive_cards[0]
            elif solution[2] is motive_cards[3]:
                solution[2] = motive_cards[4]
        elif solution[0].gameob is npc:
            if solution[2] is motive_cards[0]:
                solution[2] = motive_cards[1]

        mymystery = self.register_element("MYSTERY", pbge.okapipuzzle.OkapiPuzzle(
            "Trouble in {}".format(self.elements["METROSCENE"]),
            (suspect_susdeck, action_susdeck, motive_susdeck), "{a} {b.verbed} {c.to_verb}.",
            solution=solution
        ))

        # Now, we subcontract the actual mystery challenge out to a utility plot.
        self.add_sub_plot(nart, "POLITICAL_MYSTERY_CHALLENGE", ident="MCHALLENGE",
                          elements={"VIOLATED_VIRTUES": (gears.personality.Fellowship, gears.personality.Justice)})

        # We're also going to subcontract out NPC's attempt to dethrone LEADER and LEADER's attempt to discredit NPC.
        sp = self.add_sub_plot(
            nart, "DETHRONE_BY_POPULAR_UPRISING", ident="DETHRONE_CHALLENGE",
            elements={"NPC": leader, "VIOLATED_VIRTUES": (gears.personality.Fellowship, gears.personality.Justice),
                      "UPHELD_VIRTUE": random.choice([gears.personality.Peace, gears.personality.Glory,
                                                      gears.personality.Duty])}
        )
        sp.elements["CHALLENGE"].involvement.exclude.add(npc)

        sp = self.add_sub_plot(
            nart, "DIPLOMACY_TO_DISCREDIT", ident="DISCREDIT_CHALLENGE",
            elements={"NPC": npc, "VIOLATED_VIRTUE": gears.personality.Fellowship,
                      "UPHELD_VIRTUE": random.choice([None, gears.personality.Peace, gears.personality.Glory,
                                                      gears.personality.Justice, gears.personality.Duty]),

                      }
        )
        sp.elements["CHALLENGE"].involvement.exclude.add(leader)

        # Store the villain of the story as another element. This way, we only need to deal with the stuff once.
        self.elements["CULPRIT"] = solution[0].gameob

        self.mystery_solved = False
        self.solution_public = False

        self.started_dethrone = False
        self.won_dethrone = False

        self.started_discredit = False
        self.won_discredit = False

        return True

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes
                and gears.tags.SCENE_CULTURE in candidate.attributes)

    def _is_ok_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def _is_best_guard(self, nart, candidate):
        return (isinstance(candidate, gears.base.Character) and candidate.combatant and
                nart.camp.is_not_lancemate(candidate) and candidate is not self.elements["LEADER"] and
                nart.camp.are_faction_allies(candidate, self.elements["METROSCENE"]) and not candidate.mnpcid)

    def MYSTERY_SOLVED(self, camp):
        self.mystery_solved = True
        self.memo = Memo(
            "You learned that {MYSTERY.solution_text}".format(**self.elements), location=self.elements["CULPRIT"].scene
        )

    def t_UPDATE(self, camp):
        # If the city leader changes or dies, just end this plot. Things have changed sufficiently that whatever
        # schemes were going on before are no longer relevant.
        if self.elements["METRO"].city_leader is not self.elements["LEADER"]:
            self.end_plot(camp, True)
        elif not self.elements["LEADER"].is_operational():
            self.end_plot(camp, True)

    def MCHALLENGE_WIN(self, camp):
        self.solution_public = True
        self.memo = Memo(
            "You learned that {MYSTERY.solution_text} This information is no longer a secret.".format(**self.elements),
            location=self.elements["CULPRIT"].scene
        )

    def DETHRONE_CHALLENGE_WIN(self, camp):
        self.won_dethrone = True

    def DISCREDIT_CHALLENGE_WIN(self, camp):
        self.won_discredit = True

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        mylist.append(Offer(
            "[HELLO] [CRYPTIC_GREETING]",
            ContextTag([context.HELLO, ]),
        ))

        if not self.started_dethrone:
            mylist.append(Offer(
                self.conspiracy.get("text"),
                ContextTag([context.CUSTOM, ]),
                data={"reply": "I heard that you have some thoughts on current events?"},
                subject=self.conspiracy, subject_start=True
            ))

            mylist.append(Offer(
                "It is clearly {LEADER.job} {LEADER}, the leader of {METROSCENE}. Will you help me convince the populace to remove {NPC.gender.object_pronoun} from power?".format(
                    **self.elements),
                ContextTag([context.CUSTOMREPLY, ]),
                data={"reply": "And who do you think is responsible for all of that?"},
                subject=self.conspiracy
            ))

            if not self.started_discredit:
                mylist.append(Offer(
                    "[THATS_GOOD] Speak to the people of {METROSCENE}... Make them see the truth!".format(
                        **self.elements),
                    ContextTag([context.CUSTOMGOODBYE, ]),
                    data={"reply": "[IWILLDOMISSION]", "mission": "help spread your message"},
                    subject=self.conspiracy, dead_end=True, effect=self._start_dethrone
                ))

            mylist.append(Offer(
                "In time, even your eyes will be opened to the truth. [GOODBYE]".format(**self.elements),
                ContextTag([context.CUSTOMGOODBYE, ]), data={"reply": "[MISSION:DENY]"},
                subject=self.conspiracy, dead_end=True
            ))

            mylist.append(Offer(
                "[GOODBYE] Be careful out there... {LEADER} is [adjective].".format(**self.elements),
                ContextTag([context.CUSTOMREPLY, ]), data={"reply": "[I_HAVE_HEARD_ENOUGH]"},
                subject=self.conspiracy, dead_end=True
            ))
        elif self.won_dethrone:
            if self.elements["NPC"] is self.elements["CULPRIT"]:
                mylist.append(Offer(
                    "[THANKS_FOR_HELP] Now I can assume my rightful position as leader of {METROSCENE}!".format(
                        **self.elements),
                    ContextTag([context.CUSTOM, ]), data={
                        "reply": "I have turned the people of {METROSCENE} against {LEADER}.".format(**self.elements)},
                    effect=self._win_dethrone, dead_end=True
                ))
            else:
                mylist.append(Offer(
                    "[THANKS_FOR_HELP] Now {METROSCENE} is free of {LEADER.gender.possessive_determiner} tyranny!".format(
                        **self.elements),
                    ContextTag([context.CUSTOM, ]), data={
                        "reply": "I have turned the people of {METROSCENE} against {LEADER}.".format(**self.elements)},
                    effect=self._win_dethrone, dead_end=True
                ))

        return mylist

    def _start_dethrone(self, camp):
        self.subplots["DETHRONE_CHALLENGE"].activate(camp)
        self.started_dethrone = True

    def _win_dethrone(self, camp: gears.GearHeadCampaign):
        self.elements["METRO"].city_leader = None
        if self.elements["LEADER"] is not self.elements["CULPRIT"]:
            # Oops. Someone else was behind this all along.
            self.culprit_succeeded(camp)
        camp.freeze(self.elements["LEADER"])
        self.end_plot(camp, True)

    def culprit_succeeded(self, camp):
        culprit = self.elements["CULPRIT"]
        if self.elements["NPC"] is culprit:
            self.elements["METRO"].city_leader = self.elements["NPC"]
            cityhall = self.elements["LEADER"].scene
            self.elements["NPC"].place(cityhall)
            content.load_dynamic_plot(camp, "CONSEQUENCE_CULTOFPERSONALITY", PlotState().based_on(self))
            pbge.alert("With {LEADER} out of the picture, {NPC} becomes the new leader of {METROSCENE}.".format(
                **self.elements))
        elif self.elements["LEADER"] is culprit:
            camp.freeze(self.elements["NPC"])
            content.load_dynamic_plot(camp, "CONSEQUENCE_TOTALCRACKDOWN", PlotState().based_on(self, update_elements={
                "CRACKDOWN_REASON": "{LEADER} has eliminated all resistance to {LEADER.gender.possessive_determiner} absolute rule".format(
                    **self.elements)}))
            pbge.alert("With all resistance eliminated, {LEADER} becomes the absolute dictator of {METROSCENE}.".format(
                **self.elements))
        else:
            self.elements["METRO"].city_leader = culprit
            cityhall = self.elements["LEADER"].scene
            camp.freeze(self.elements["LEADER"])
            culprit.place(cityhall)
            content.load_dynamic_plot(camp, "CONSEQUENCE_KLEPTOCRACY", PlotState().based_on(self))
            pbge.alert("While {LEADER} was busy worrying about {NPC}, {CULPRIT} seized control of {METROSCENE}.".format(
                **self.elements))

    def LEADER_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        leader = self.elements["LEADER"]
        if self._rumor_memo_delivered and not self.started_discredit:
            mylist.append(Offer(
                "It's true. {NPC} is a rabble-rouser who has been trying to set the people of {METROSCENE} against me. If you could help me deliver a more positive message, that would be greatly appreciated.".format(
                    **self.elements),
                ContextTag([context.CUSTOM, ]),
                data={"reply": "I heard that {NPC} is causing problems for you.".format(**self.elements)},
                subject=leader, subject_start=True
            ))

            mylist.append(Offer(
                "That's too bad. Politics isn't for everyone.".format(**self.elements),
                ContextTag([context.CUSTOMREPLY, ]), data={"reply": "[MISSION:DENY]"},
                subject=leader
            ))

            if not self.started_dethrone:
                mylist.append(Offer(
                    "[THANK_YOU] Just talk with some of the citizens and I'm sure you'll find them receptive to my message.".format(
                        **self.elements),
                    ContextTag([context.CUSTOMREPLY, ]),
                    data={"reply": "[IWILLDOMISSION]", "mission": "help improve your image"},
                    subject=leader, effect=self._start_discredit, dead_end=True
                ))

        if self.won_discredit:
            if leader is self.elements["CULPRIT"]:
                mylist.append(Offer(
                    "[THANKS_FOR_HELP] With all opposition extinguished, I can now rule {METROSCENE} as I please!".format(
                        **self.elements),
                    ContextTag([context.CUSTOM, ]),
                    data={"reply": "I have turned the people of {METROSCENE} against {NPC}.".format(**self.elements)},
                    effect=self._win_discredit, dead_end=True
                ))
            elif self.elements["CULPRIT"] is not self.elements["NPC"]:
                mylist.append(Offer(
                    "[THANKS_FOR_HELP] But I've learned too late that {NPC} wasn't the real threat to {METROSCENE}...".format(
                        **self.elements),
                    ContextTag([context.CUSTOM, ]),
                    data={"reply": "I have turned the people of {METROSCENE} against {NPC}.".format(**self.elements)},
                    effect=self._win_discredit, dead_end=True
                ))
            else:
                mylist.append(Offer(
                    "[THANKS_FOR_HELP] Now {METROSCENE} can once more be united as a true community!".format(
                        **self.elements),
                    ContextTag([context.CUSTOM, ]),
                    data={"reply": "I have turned the people of {METROSCENE} against {NPC}.".format(**self.elements)},
                    effect=self._win_discredit, dead_end=True
                ))

        return mylist

    def _start_discredit(self, camp):
        self.subplots["DISCREDIT_CHALLENGE"].activate(camp)
        self.started_discredit = True

    def _win_discredit(self, camp: gears.GearHeadCampaign):
        if self.elements["NPC"] is not self.elements["CULPRIT"]:
            # Oops. Someone else was behind this all along.
            self.culprit_succeeded(camp)
        camp.freeze(self.elements["NPC"])
        self.end_plot(camp, True)

    def CULPRIT_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        mystery: pbge.okapipuzzle.OkapiPuzzle = self.elements["MYSTERY"]
        bribe = gears.selector.calc_mission_reward(self.rank, 1000)
        if self.mystery_solved:
            mylist.append(Offer(
                "Wait, we can come to a deal about this... I'll offer you ${:,} to forget you heard anything.".format(
                    bribe),
                ContextTag([context.CUSTOM]), data={"reply": "I know you {}.".format(mystery.solution[1].verbed)},
                subject=self, subject_start=True
            ))
            if self.solution_public:
                mylist.append(Offer(
                    "[I_WOULD_HAVE_GOTTEN_AWAY]",
                    ContextTag([context.CUSTOMREPLY]),
                    data={"reply": "Too late. I've already released the information."},
                    subject=self, effect=self._catch_culprit
                ))
            else:
                mylist.append(Offer(
                    "[I_WOULD_HAVE_GOTTEN_AWAY]",
                    ContextTag([context.CUSTOMREPLY]), data={"reply": "No deal. You're going down."},
                    subject=self, effect=self._catch_culprit, dead_end=True
                ))

                mylist.append(Offer(
                    "[PLEASURE_DOING_BUSINESS]",
                    ContextTag([context.CUSTOMREPLY]), data={"reply": "That sounds like a fair trade."},
                    subject=self, effect=self._release_culprit, dead_end=True
                ))

            mylist.append(Offer(
                "Let me know when you've come to a decision.",
                ContextTag([context.CUSTOMREPLY]), data={"reply": "I'll think about it."},
                subject=self, dead_end=True
            ))

        return mylist

    def _get_generic_offers(self, npc, camp: gears.GearHeadCampaign):
        mylist = list()
        mystery: pbge.okapipuzzle.OkapiPuzzle = self.elements["MYSTERY"]
        reward = gears.selector.calc_mission_reward(self.rank, 165)

        if camp.is_not_lancemate(npc):
            if self.mystery_solved and camp.are_faction_allies(npc, self.elements["METROSCENE"]) and not any(
                    [c.gameob is npc for c in mystery.solution]):
                mylist.append(Offer(
                    "[THIS_CANNOT_BE_ALLOWED] Here is a reward of ${:,} for helping to stop this crime.".format(reward),
                    ContextTag([context.CUSTOM]), data={"reply": mystery.solution_text},
                    effect=self._turn_in_culprit, dead_end=True
                ))
        return mylist

    def _get_dialogue_grammar(self, npc: gears.base.Character, camp: gears.GearHeadCampaign):
        mygram = dict()

        if npc is not self.elements["LEADER"] and self.elements["NPC"] is not self.elements["CULPRIT"]:
            mygram["[CURRENT_EVENTS]"] = [
                "{LEADER} has not been a great leader for {METROSCENE}.".format(**self.elements),
            ]

        return mygram

    def _turn_in_culprit(self, camp):
        camp.credits += gears.selector.calc_mission_reward(self.rank, 165)
        self._catch_culprit(camp)

    def _catch_culprit(self, camp: gears.GearHeadCampaign):
        camp.dole_xp(200)
        camp.freeze(self.elements["CULPRIT"])
        if self.elements["CULPRIT"] is self.elements["LEADER"]:
            self.elements["METRO"].city_leader = None
        pbge.alert(
            "With {CULPRIT} out of the way, life soon returns to normal in {METROSCENE}.".format(**self.elements))
        self.end_plot(camp, True)

    def _release_culprit(self, camp: gears.GearHeadCampaign):
        camp.credits += gears.selector.calc_mission_reward(self.rank, 1000)
        self.culprit_succeeded(camp)
        self.end_plot(camp, True)
