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
from .dd_roadedge import DZDREBasicPlotWithEncounterStuff, DeadZoneHighwaySceneGen
from game import memobrowser
from game.memobrowser import Memo


#   *********************************
#   ***   DZD_ROADEDGE_KERBEROS   ***
#   *********************************
#

class KerberosEncounterPlot(DZDREBasicPlotWithEncounterStuff):
    LABEL = "DZD_ROADEDGE_KERBEROS"

    active = True
    scope = True
    UNIQUE = True
    BASE_RANK = 10
    ENCOUNTER_CHANCE = BASE_RANK + 30
    ENCOUNTER_ARCHITECTURE = gharchitecture.MechaScaleDeadzone

    def custom_init(self, nart):
        super().custom_init(nart)
        myedge = self.elements["DZ_EDGE"]
        self.add_sub_plot(nart, "DZRE_KERBEROS_ATTACKS", ident="MISSION", spstate=PlotState(
            elements={"METRO": myedge.start_node.destination.metrodat, "METROSCENE": myedge.start_node.destination,
                      "MISSION_GATE": myedge.start_node.entrance}).based_on(self))
        self._got_rumor = False
        mysp = self.add_sub_plot(
            nart,"ADD_EXPERT",elements={"METRO": myedge.start_node.destination.metrodat, "METROSCENE": myedge.start_node.destination}
        )
        self.elements["NPC"] = mysp.elements["NPC"]
        self.elements["EXPERT_LOC"] = mysp.elements["LOCALE"]
        return True

    def get_enemy_encounter(self, camp, dest_node):
        start_node = self.elements["DZ_EDGE"].get_link(dest_node)
        if start_node.pos[0] < dest_node.pos[0]:
            myanchor = pbge.randmaps.anchors.west
        else:
            myanchor = pbge.randmaps.anchors.east
        myadv = missionbuilder.BuildAMissionSeed(
            camp, "Kerberos Attacks", (start_node.destination, start_node.entrance),
            enemy_faction=None, rank=self.rank,
            objectives=(dd_customobjectives.DDBAMO_KERBEROS,),
            adv_type="DZD_ROAD_MISSION",
            custom_elements={"ADVENTURE_GOAL": (dest_node.destination, dest_node.entrance), "ENTRANCE_ANCHOR": myanchor,
                             missionbuilder.BAME_MONSTER_TAGS: ("ZOMBOT",)},
            scenegen=DeadZoneHighwaySceneGen,
            architecture=self.ENCOUNTER_ARCHITECTURE(room_classes=(pbge.randmaps.rooms.FuzzyRoom,)),
            cash_reward=0,
            combat_music="Komiku_-_03_-_Battle_Theme.ogg",
            exploration_music="Komiku_-_01_-_Ancient_Heavy_Tech_Donjon.ogg"
        )
        return myadv

    def get_road_adventure(self, camp, dest_node):
        # Return an adventure if there's going to be an adventure. Otherwise return nothing.
        if self.active and camp.has_mecha_party():
            if random.randint(1, 100) <= self.ENCOUNTER_CHANCE and not self.road_cleared:
                return self.get_enemy_encounter(camp, dest_node)
            elif random.randint(1, 100) <= 15:
                return self.get_random_encounter(camp, dest_node)

    def MISSION_WIN(self, camp):
        self.elements["DZ_EDGE"].style = self.elements["DZ_EDGE"].STYLE_SAFE
        self.road_cleared = True

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        myscene = camp.scene.get_root_scene()
        if self.elements["DZ_EDGE"].connects_to_city(myscene) and not self.road_cleared:
            # This city is on this road.
            mygram["[News]"] = ["kerberos deathworms have been sighted on the road to {}".format(
                self.elements["DZ_EDGE"].get_city_link(myscene)), ]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        myscene = camp.scene.get_root_scene()
        myedge = self.elements["DZ_EDGE"]
        if npc is not self.elements["NPC"]:
            if myedge.start_node.destination is myscene and not self.road_cleared and not self._got_rumor:
                goffs.append(Offer(
                    msg="The Kerberos has lived here forever. No-one knows if it is one monster with many heads or many monsters acting together, but we do know it cannot be killed. You ought to ask {NPC} for more info. {NPC.gender.subject_pronoun} knows more about it than anyone else alive.".format(**self.elements),
                    context=ContextTag((context.INFO,)), effect=self._get_rumor,
                    subject="kerberos", data={"subject": "the kerberos deathworm"}, no_repeats=True
                ))
            elif myedge.end_node.destination is myscene and not self.road_cleared and not self._got_rumor:
                goffs.append(Offer(
                    msg="They're big, they're dangerous, and they can swallow a mecha whole. You should ask someone from {} if you want to know more... Usually the deathworms don't come out this far.".format(myedge.start_node.destination),
                    context=ContextTag((context.INFO,)),
                    subject="kerberos", data={"subject": "the kerberos deathworm"}, no_repeats=True
                ))
        return goffs

    def _get_rumor(self, camp):
        self._got_rumor = True
        self.memo = Memo("{NPC} at {EXPERT_LOC} knows more about the Kerberos Deathworm than anyone else.".format(**self.elements),
                         self.elements["EXPERT_LOC"])

    def NPC_offers(self, camp):
        mylist = list()



        return mylist


class KerberosAttacks(Plot):
    LABEL = "DZRE_KERBEROS_ATTACKS"
    active = True
    scope = True
    UNIQUE = True

    def custom_init(self, nart):
        self.kerberos_active = True

        # Add the Kerberos interior dungeon
        mydungeon = dungeonmaker.DungeonMaker(
            nart, self, self.elements["METROSCENE"], "Kerberos Facility", gharchitecture.OrganicBuilding(),
            self.rank,
            monster_tags=("MUTANT", "VERMIN", "SYNTH", "CREEPY"),
            explo_music="Komiku_-_01_-_Ancient_Heavy_Tech_Donjon.ogg",
            combat_music="Komiku_-_03_-_Battle_Theme.ogg",
            connector=plotutility.StairsDownToStairsUpConnector,
            scene_tags=(gears.tags.SCENE_DUNGEON, gears.tags.SCENE_RUINS,),
            decor=gharchitecture.OrganicStructureDecor()
        )
        self.register_element("DUNGEON_ENTRANCE", mydungeon.entry_level)
        d_entrance_room = self.register_element("ENTRANCE_ROOM", pbge.randmaps.rooms.OpenRoom(12, 12))
        mydungeon.entry_level.contents.append(d_entrance_room)

        myent = self.register_element(
            "ENTRANCE", game.content.ghwaypoints.StairsUp(
                anchor=pbge.randmaps.anchors.middle,
                dest_scene=self.elements["METROSCENE"],
                dest_entrance=self.elements["MISSION_GATE"]),
            dident="ENTRANCE_ROOM"
        )

        # Add the kidnap room and kidnap room waypoint.
        d_kidnap_room = self.register_element("KIDNAP_ROOM", pbge.randmaps.rooms.OpenRoom(12, 12))
        mydungeon.entry_level.contents.append(d_kidnap_room)
        self.register_element("KIDNAP_ROOM_WP", pbge.scenes.waypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="KIDNAP_ROOM")
        self.register_element("KIDNAP_TEAM", game.teams.Team(), dident="KIDNAP_ROOM")
        self.kidnapped_pilots = list()

        d_kidnap_room.contents.append(ghwaypoints.PZHolo())

        nart.camp.campdata["KERBEROS_GRAB_FUN"] = self._get_grabbed_by_kerberos
        nart.camp.campdata["KERBEROS_DUNGEON_OPEN"] = False

        # Add the lore bits. In this case, biomachines that might reveal Kerberos's purpose.
        lore_room = pbge.randmaps.rooms.OpenRoom(5,5,parent=random.choice(mydungeon.levels))
        #lore_room = pbge.randmaps.rooms.OpenRoom(10, 10, parent=mydungeon.entry_level)
        biomachine = self.register_element(
            "BIOMACHINE", ghwaypoints.OrganicTube(
                name="Bioprocessor", plot_locked=True,
                desc="A biomechanical tube extends from the ceiling of this chamber to the floor."
            )
        )
        lore_room.contents.append(biomachine)

        # Add the boss room.
        d_boss_level = self.register_element("BOSS_LEVEL", mydungeon.goal_level)
        d_boss_room = self.register_element("BOSS_ROOM", pbge.randmaps.rooms.OpenRoom(10,10), dident="BOSS_LEVEL")
        self.add_sub_plot(nart, "DZRE_KERBEROS_BOSSFIGHT", ident="BOSSFIGHT")

        self.intro_ready = True

        return True

    def _get_grabbed_by_kerberos(self, camp: gears.GearHeadCampaign, pc):
        camp.scene.contents.remove(pc)
        pilot = pc.get_pilot()
        if pilot is camp.pc:
            camp.destination, camp.entrance = self.elements["DUNGEON_ENTRANCE"], self.elements["KIDNAP_ROOM_WP"]
            camp.campdata["KERBEROS_DUNGEON_OPEN"] = True
        else:
            plotutility.AutoLeaver(pilot)(camp)
            self.elements["DUNGEON_ENTRANCE"].deploy_team([pilot,],self.elements["KIDNAP_TEAM"])
            self.kidnapped_pilots.append(pilot)

    def MISSION_GATE_menu(self, camp, thingmenu):
        if camp.campdata["KERBEROS_DUNGEON_OPEN"]:
            thingmenu.add_item("Go to the Kerberos Facility.", self.go_to_locale)

    def BIOMACHINE_menu(self, camp: gears.GearHeadCampaign, thingmenu):
        if camp.party_has_skill(gears.stats.Biotechnology) or camp.party_has_skill(gears.stats.Science):
            thingmenu.desc = "{} It seems to be a detoxification processor; perhaps Kerberos has been removing contaminants from the soil it consumes.".format(thingmenu.desc)
        else:
            thingmenu.desc = "{} It seems to be digesting something.".format(thingmenu.desc)

    def BOSSFIGHT_WIN(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)

    def go_to_locale(self, camp):
        camp.destination, camp.entrance = self.elements["DUNGEON_ENTRANCE"], self.elements["ENTRANCE"]

    def t_START(self, camp):
        if self.intro_ready and camp.scene is self.elements["DUNGEON_ENTRANCE"]:
            pbge.alert("You are dropped into a deep underground chamber. You're not sure whether this is inside Kerberos or some adjoining complex.")
            self.intro_ready = False


class KerberosBossFight(Plot):
    LABEL = "DZRE_KERBEROS_BOSSFIGHT"
    active = True
    scope = "BOSS_LEVEL"
    UNIQUE = True

    def custom_init(self, nart):
        myscene = self.elements["BOSS_LEVEL"]
        myteam = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="BOSS_ROOM")
        mycompy = self.register_element("_core", gears.selector.get_design_by_full_name("K1 Bio-Computer"), dident="_eteam")
        serv1 = self.register_element("_serv1", gears.selector.get_design_by_full_name("Servitor"), dident="_eteam")
        serv2 = self.register_element("_serv2", gears.selector.get_design_by_full_name("Servitor"), dident="_eteam")
        serv1.colors = (gears.color.Twilight,gears.color.Black,gears.color.Black,gears.color.Black,gears.color.Black)
        serv2.colors = (gears.color.Saffron,gears.color.Black,gears.color.Black,gears.color.Black,gears.color.Black)

        return True

    def t_COMBATROUND(self, camp: gears.GearHeadCampaign):
        mycompy: gears.base.Prop = self.elements["_core"]
        serv1: gears.base.Monster = self.elements["_serv1"]
        serv2: gears.base.Monster = self.elements["_serv2"]

        if mycompy.is_destroyed() and not (serv1.is_destroyed() and serv2.is_destroyed()):
            # If you destroy the compy before the servitors, it gets repaired.
            mycompy.restore_all()
            pbge.my_state.view.play_anims(gears.geffects.BiotechnologyAnim(pos=mycompy.pos))

    def t_ENDCOMBAT(self, camp: gears.GearHeadCampaign):
        mycompy: gears.base.Prop = self.elements["_core"]
        serv1: gears.base.Monster = self.elements["_serv1"]
        serv2: gears.base.Monster = self.elements["_serv2"]

        if mycompy.is_destroyed() and serv1.is_destroyed() and serv2.is_destroyed():
            pbge.alert("As the biocomputer dies, the chamber is shaken by a powerful rumble. The tremors last for a short time before fading into silence. Whatever just happened, you assume that Kerberos will no longer trouble travelers on the highway.")
            camp.check_trigger("WIN", self)
            self.end_plot(camp)


