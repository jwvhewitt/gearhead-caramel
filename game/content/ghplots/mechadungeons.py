from pbge.plots import Plot
from game import teams
import gears
import pbge
from game.content import ghwaypoints, gharchitecture, plotutility, dungeonmaker
import random
from game.content.dungeonmaker import DG_NAME, DG_ARCHITECTURE, DG_SCENE_TAGS, DG_TEMPORARY, DG_PARENT_SCENE, DG_EXPLO_MUSIC, DG_COMBAT_MUSIC, DG_DECOR


class GenericMechaDungeonLevel(Plot):
    LABEL = "MECHA_DUNGEON_GENERIC"

    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        intscene = gears.GearHeadScene(65, 65, self.elements[DG_NAME], player_team=team1,
                                       attributes=self.elements[DG_SCENE_TAGS],
                                       combat_music=self.elements[DG_COMBAT_MUSIC],
                                       exploration_music=self.elements[DG_EXPLO_MUSIC],
                                       scale=gears.scale.MechaScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, self.elements[DG_ARCHITECTURE],
                                                   decorate=self.elements.get(DG_DECOR))
        self.register_scene(nart, intscene, intscenegen, ident="LOCALE", dident=DG_PARENT_SCENE,
                            temporary=self.elements.get(DG_TEMPORARY,False))

        self.last_update = 0

        for t in range(random.randint(3,5)):
            self.add_sub_plot(nart, "MECHA_OUTPOST",)

        #self.add_sub_plot(nart, "DUNGEON_EXTRA", necessary=False)

        return True

    def t_ENDCOMBAT(self, camp:gears.GearHeadCampaign):
        camp.bring_out_your_dead(True)
        if camp.pc not in camp.party:
            pbge.alert("Your lance retreats...")
            camp.go(camp.home_base)

    def LOCALE_ENTER(self, camp: gears.GearHeadCampaign):
        if camp.time > self.last_update:
            dungeonmaker.dungeon_cleaner(camp.scene)
            self.last_update = camp.time
