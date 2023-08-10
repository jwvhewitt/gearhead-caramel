import pbge
from pbge.plots import Plot
import gears
from . import missionbuilder
from game.content import gharchitecture, plotutility, dungeonmaker, ghwaypoints, adventureseed, ghcutscene, ghterrain


def end_mission_lance_recovery(camp):
    creds = camp.totally_restore_party()
    if creds > 0:
        pbge.alert("Repair/Reload: ${}".format(creds))
        camp.credits -= creds
        camp.time += 1


class MultiMissionNodePlot(Plot):
    # Contains one mission or other feature of the multi-mission.
    # Required Elements:
    #   WIN_MISSION_FUN, LOSE_MISSION_FUN: Callables to call in the event of a win or loss.
    #   ONE_SHOT: If True, the mission automatically advances with no rest in between. Defaults to True.
    # Optional Elements:
    #   ENEMY_FACTION, ALLIED_FACTION
    #   COMBAT_MUSIC, EXPLORATION_MUSIC
    #   MISSION_DATA
    #   MISSION_GRAMMAR
    active = True
    scope = True

    NAME_PATTERN = ""
    OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES, missionbuilder.BAMO_CAPTURE_BUILDINGS)

    def custom_init(self, nart):
        if "SCENE_GENERATOR" not in self.elements or "ARCHITECTURE" not in self.elements:
            sgen, archi = gharchitecture.get_mecha_encounter_scenegen_and_architecture(self.elements["METROSCENE"])
            self.elements["SCENE_GENERATOR"] = sgen
            self.elements["ARCHITECTURE"] = archi
        return True

    def create_mission(self, camp):
        return missionbuilder.BuildAMissionSeed(
            camp, self.NAME_PATTERN.format(**self.elements),
            self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            self.elements.get("ENEMY_FACTION"), self.elements.get("ALLIED_FACTION"), self.rank,
            self.OBJECTIVES,
            custom_elements=self.elements.get("CUSTOM_ELEMENTS", None),
            scenegen=self.elements["SCENE_GENERATOR"], architecture=self.elements["ARCHITECTURE"],
            on_win=self._on_win, on_loss=self._on_loss,
            combat_music=self.elements.get("COMBAT_MUSIC"), exploration_music=self.elements.get("EXPLORATION_MUSIC"),
            data=self.elements.get("MISSION_DATA", {}),
            mission_grammar=self.elements.get("MISSION_GRAMMAR", {}),
            restore_at_end=not self.elements.get("ONE_SHOT", True),
            call_win_loss_funs_after_card=True
        )

    @property
    def name(self):
        return self.NAME_PATTERN.format(**self.elements)

    def _on_win(self, camp: gears.GearHeadCampaign):
        myfun = self.elements.get("WIN_MISSION_FUN", None)
        if myfun:
            myfun(camp)

    def _on_loss(self, camp: gears.GearHeadCampaign):
        myfun = self.elements.get("LOSE_MISSION_FUN", None)
        if myfun:
            myfun(camp)

    def call_node(self, camp):
        mymission = self.create_mission(camp)
        mymission(camp)

    def can_do_mission(self, camp):
        return bool(camp.get_usable_party(gears.scale.MechaScale, just_checking=True,
                                          enviro=self.elements["ARCHITECTURE"].ENV))


class MultiMissionMenu(pbge.rpgmenu.Menu):
    WIDTH = 350
    HEIGHT = 250
    MENU_HEIGHT = 75

    FULL_RECT = pbge.frects.Frect(-175, -75, 350, 250)
    TEXT_RECT = pbge.frects.Frect(-175, -75, 350, 165)
    FRAME_WIDTH = 64

    def __init__(self, mmission, desc):
        self.mmission = mmission
        super().__init__(
            -self.WIDTH // 2, self.HEIGHT // 2 - self.MENU_HEIGHT + 75, self.WIDTH, self.MENU_HEIGHT, predraw=self.pre,
            no_escape=True, border=None, font=pbge.MEDIUMFONT
        )
        self.desc = desc
        self.img = pbge.image.Image("sys_multimissionstages.png", self.FRAME_WIDTH, self.FRAME_WIDTH)

        sdrw = (len(mmission.mission_stages) * 2 - 1) * self.FRAME_WIDTH
        self.stages_display_rect = pbge.frects.Frect(-sdrw//2, -175, sdrw, self.FRAME_WIDTH)

    def pre(self):
        if pbge.my_state.view:
            pbge.my_state.view()
        pbge.default_border.render(self.FULL_RECT.get_rect())

        mydest = self.stages_display_rect.get_rect()
        pbge.default_border.render(mydest)
        num_stages = len(self.mmission.mission_stages)
        for t in range(num_stages):
            t_stage = self.mmission.mission_stages[t]
            myframe = t_stage.stage_frame
            if t < self.mmission.mission_number:
                myframe += 10
            elif t > self.mmission.mission_number:
                myframe += 5
            self.img.render(mydest, myframe)
            mydest.x += self.FRAME_WIDTH
            if (t+1) < num_stages:
                self.img.render(mydest, 15)
                mydest.x += self.FRAME_WIDTH

        pbge.draw_text(pbge.my_state.medium_font, self.desc, self.TEXT_RECT.get_rect(), justify=0)



class MultiMissionStagePlot(Plot):
    # This plot describes a stage of the multi-mission. It will contain one or more nodes, which are usually individual
    # missions but hey feel free to go nuts.
    # Required Elements:
    #   WIN_MISSION_FUN, LOSE_MISSION_FUN: Get passed on to the nodes.
    #   ONE_SHOT: If True, the mission automatically advances with no rest in between. Defaults to True.
    # Optional Elements:
    #   COMBAT_MUSIC, EXPLORATION_MUSIC
    #   MISSION_DATA
    #   MISSION_GRAMMAR
    active = True
    scope = True

    DESC_PATTERN = ""

    STAGE_NORMAL = 0
    STAGE_HARD = 1
    STAGE_RESTORE = 2
    STAGE_BOSS = 3
    STAGE_CONCLUSION = 4
    stage_frame = STAGE_NORMAL

    def custom_init(self, nart):
        self.nodes = list()
        self._build_stage(nart)
        return True

    def _build_stage(self, nart):
        raise NotImplementedError("No build stage method declared for {}".format(self.LABEL))

    def _add_stage_node(self, nart, nodelabel: str, necessary: bool = True):
        mynode = self.add_sub_plot(nart, nodelabel, necessary=necessary)
        self.nodes.append(mynode)

    def _get_stage_desc(self, camp):
        return self.DESC_PATTERN.format(**self.elements)

    def _create_node_menu(self, camp, mmission):
        mymenu = MultiMissionMenu(mmission, self._get_stage_desc(camp))
        for node in self.nodes:
            if node.can_do_mission(camp):
                mymenu.add_item(node.name, node.call_node)
        mymenu.sort()
        if mmission.mission_number > 0:
            mymenu.add_item("Abort the mission", None)
        return mymenu

    def call_stage(self, camp, mmission):
        mymenu = self._create_node_menu(camp, mmission)
        dest = mymenu.query()
        if dest:
            dest(camp)
        elif mmission.elements.get("ONE_SHOT", True):
            print("Losing mission!")
            mmission._lose_mission(camp)


class MultiMission(Plot):
    # Required Elements:
    #   METROSCENE, MISSION_GATE, WIN_FUN, LOSS_FUN
    #   ONE_SHOT: If True, the mission automatically advances with no rest in between. Defaults to True.
    # Optional Elements:
    #   COMBAT_MUSIC, EXPLORATION_MUSIC
    #   MISSION_GRAMMAR
    active = True
    scope = True

    mission_stages = None
    mission_number = 0

    def custom_init(self, nart):
        self.mission_stages = list()
        self.mission_number = 0
        self.elements["WIN_MISSION_FUN"] = self._win_mission
        self.elements["LOSE_MISSION_FUN"] = self._lose_mission
        self._build_mission_graph(nart)
        return True

    def _win_mission(self, camp: gears.GearHeadCampaign):
        self.mission_number += 1
        if self.mission_number >= len(self.mission_stages):
            myfun = self.elements.get("WIN_FUN", None)
            if myfun:
                myfun(camp)

            self.end_plot(camp, True)

        else:
            if self.elements.get("ONE_SHOT", True):
                self(camp)

    def _lose_mission(self, camp: gears.GearHeadCampaign):
        if self.elements.get("ONE_SHOT", True):
            # The player has failed this multi-mission. End now.
            end_mission_lance_recovery(camp)
            myfun = self.elements.get("LOSS_FUN", None)
            if myfun:
                myfun(camp)
            self.end_plot(camp, True)

    def _build_mission_graph(self, nart):
        raise NotImplementedError("No build mission graph method declared for {}".format(self.LABEL))

    def _add_stage(self, nart, stagelabel: str, necessary: bool = True):
        mynode = self.add_sub_plot(nart, stagelabel, necessary=necessary)
        self.mission_stages.append(mynode)

    def can_do_mission(self, camp):
        # Defaults to True, feel free to change this one.
        return True

    def __call__(self, camp):
        # Display the menu, go to the next encounter as appropriate.
        self.mission_stages[self.mission_number].call_stage(camp, self)
