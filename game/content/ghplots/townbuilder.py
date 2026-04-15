import gears
from pbge.plots import Plot
import pbge
from pbge.dialogue import Offer, ContextTag
from game import teams, ghdialogue
from game.ghdialogue import context
import random
from game.content.plotutility import AdventureModuleData
from game.content import gharchitecture, ghterrain, ghrooms, ghwaypoints, ghcutscene, plotutility


class RandomDeadZoneTown(Plot):
    LABEL = "TOWNBUILDER"

    def custom_init(self, nart):
        # Determine the town's geographic status
        # Deep Deadzone, Semi Deadzone, Oasis, Ruins
        town_name = self._generate_town_name()
        town_fac = self.register_element("METRO_FACTION",
                                         gears.factions.Circle(nart.camp,
                                                               parent_faction=gears.factions.DeadzoneFederation,
                                                               name="the {} Council".format(town_name))
                                         )
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1,), faction=town_fac)

        _=self.register_element("CITY_COLORS", gears.color.random_building_colors())

        myscene = gears.GearHeadScene(
            50, 50, town_name, player_team=team1, civilian_team=team2,
            scale=gears.scale.HumanScale, is_metro=True, faction=town_fac,
            attributes=(gears.personality.DeadZone, gears.tags.City, gears.tags.SCENE_PUBLIC)
        )
        myscene.exploration_music = 'Komiku_-_06_-_Friendss_theme.ogg'

        myscenegen = pbge.randmaps.CityGridGenerator(myscene, gharchitecture.HumanScaleUrbanDeadzone(),
                                                     road_terrain=ghterrain.Flagstone)

        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")

        _=self.register_element("METRO", myscene.metrodat)
        _=self.register_element("METROSCENE", myscene)

        # Add the mission gate/town entrance.
        _=self.register_element(
            "_ROOM2", pbge.randmaps.rooms.Room(3, 3, anchor=pbge.randmaps.anchors.east),
            dident="LOCALE"
        )
        towngate = self.register_element("ENTRANCE", ghwaypoints.Exit(
            name="The Highway", plot_locked=True, anchor=pbge.randmaps.anchors.middle,
            desc="The highway stretches far beyond {} to the horizon.".format(town_name)
        ), dident="_ROOM2")
        # Gonna register the entrance under another name for the subplots.
        _=self.register_element("MISSION_GATE", towngate)

        # Add NPCs
        npc = gears.selector.random_character(50, local_tags=myscene.attributes)
        npc.place(myscene, team=team2)
        npc2 = gears.selector.random_character(50, local_tags=myscene.attributes,
                                               job=gears.jobs.choose_random_job((gears.tags.Laborer,),
                                                                                self.elements["LOCALE"].attributes))
        npc2.place(myscene, team=team2)
        self.add_sub_plot(nart, "RANDOM_LANCEMATE")

        defender = self.register_element(
            "DEFENDER", gears.selector.random_character(
                self.rank, local_tags=self.elements["LOCALE"].attributes,
                job=gears.jobs.choose_random_job((gears.tags.Police,), self.elements["LOCALE"].attributes),
                faction=town_fac
            ))
        defender.place(myscene, team=team2)


        # Add the local problem.
        self.add_sub_plot(nart, "LOCAL_PROBLEM")

        # Add the features
        self.add_sub_plot(nart, "QOL_REPORTER")
        self.add_sub_plot(nart, "CF_METROSCENE_RECOVERY_HANDLER")
        self.add_sub_plot(nart, "CF_METROSCENE_WME_DEFENSE_HANDLER")
        self.add_sub_plot(nart, "CF_METROSCENE_RANDOM_PLOT_HANDLER", elements={"USE_PLOT_RANK": True})

        return True

    TOWN_NAME_PATTERNS = ("Fort {}", "{} Fortress", "{} Oasis", "Mount {}", "{}",
                          "Castle {}", "{} Ruins", "{} Spire", "{} Village", "{} Town")

    def _generate_town_name(self):
        return random.choice(self.TOWN_NAME_PATTERNS).format(gears.selector.DEADZONE_TOWN_NAMES.gen_word())
