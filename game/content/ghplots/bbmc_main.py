import gears
from pbge.plots import Plot, Adventure, PlotState
from game.content.plotutility import LMSkillsSelfIntro
import pbge
from pbge.dialogue import Offer,ContextTag
from game import teams,ghdialogue
from game.ghdialogue import context
import pygame
import random
from game.content.plotutility import AdventureModuleData
from game.content import gharchitecture, ghterrain, ghrooms, ghwaypoints

class BearBastardMechaCampStub( Plot ):
    LABEL = "SCENARIO_BEARBASTARDSMECHACAMP"
    active = True
    scope = True
    # Creates a Bear Bastard's Mecha Camp adventure.

    ADVENTURE_MODULE_DATA = AdventureModuleData(
        "Bear Bastard's Mecha Camp",
        "Learn everything you need to know about being a mecha pilot from a notorious bandit hoping to cash in on his involvement in the Typhon Incident. Fun and educational!",
        (157, 9, 9), "VHS_BearBastardsMechaCamp.png",
    )

    def custom_init( self, nart ):
        """Load the features."""
        self.add_first_locale_sub_plot( nart, locale_type="BBMC_SceneOne", ident="SCENE_ONE" )
        return True


class SceneOne(Plot):
    LABEL = "BBMC_SceneOne"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")

        myscene = gears.GearHeadScene(
            25, 25, "Last Hope Memorial Park", player_team=team1,
            scale=gears.scale.HumanScale, civilian_team=team2, attributes=(gears.personality.DeadZone,),
            exploration_music='A wintertale.ogg', combat_music='Chronos.ogg'
        )
        myscenegen = pbge.randmaps.PartlyUrbanGenerator(
            myscene, gharchitecture.HumanScaleDeadzone(), road_terrain=ghterrain.Flagstone,
            urban_area=ghrooms.GrassRoom(13, 13, anchor=pbge.randmaps.anchors.middle), road_thickness=3
        )
        statue_room = pbge.randmaps.rooms.OpenRoom(
            7, 7, (pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM),
            archi=pbge.randmaps.architect.Architecture(floor_terrain=ghterrain.Flagstone),
            anchor=pbge.randmaps.anchors.middle
        )
        myscene.contents.append(statue_room)
        statue_room.contents.append(team2)

        entry_room = pbge.randmaps.rooms.Room(
            3, 3, (pbge.randmaps.IS_CONNECTED_ROOM,),
            anchor=pbge.randmaps.anchors.south
        )
        myscene.contents.append(entry_room)
        my_exit = self.register_element(
            "ENTRANCE", ghwaypoints.Exit(plot_locked=True, anchor=pbge.randmaps.anchors.middle)
        )
        entry_room.contents.append(my_exit)

        self.register_scene( nart, myscene, myscenegen, ident="LOCALE",)

        npc: gears.base.Character = self.register_element("NPC", nart.camp.get_major_npc("Bear Bastard"))
        npc.place(myscene, team=team2)

        return True
