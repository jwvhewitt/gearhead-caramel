from pbge.plots import Plot
import game
import gears
import pbge
import pygame
import random
from game import teams, ghdialogue
from game.content import gharchitecture, ghwaypoints, plotutility, missiontext
from pbge.dialogue import Offer, ContextTag
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed
from gears import champions
from game.content.dungeonmaker import DG_NAME, DG_ARCHITECTURE, DG_SCENE_TAGS, DG_MONSTER_TAGS, DG_TEMPORARY, \
    DG_PARENT_SCENE, DG_EXPLO_MUSIC, DG_COMBAT_MUSIC, DG_DECOR
import copy

# Mecha Objectives
BAMO_AID_ALLIED_FORCES = "BAMO_AidAlliedForces"
BAMO_CAPTURE_THE_MINE = "BAMO_CaptureMine"
BAMO_CAPTURE_BUILDINGS = "BAMO_CaptureBuildings"
BAMO_DEFEAT_ARMY = "BAMO_DefeatArmy"  # 3 points
BAMO_DEFEAT_BLOCKADE = "BAMO_DefeatBlockade"    # 2 points
BAMO_DEFEAT_COMMANDER = "BAMO_DefeatCommander"  # 2 points
BAMO_DEFEAT_NPC = "BAMO_DefeatNPC"  # 2 points
BAMO_DUEL_NPC = "BAMO_DuelNPC"
BAME_NPC = "BAME_NPC"
BAMO_DEFEAT_THE_BANDITS = "BAMO_DefeatTheBandits"
BAMO_DESTROY_ARTILLERY = "BAMO_Destroy_Artillery"  # 2 points
BAMO_EXTRACT_ALLIED_FORCES = "BAMO_ExtractAlliedForces"
BAMO_EXTRACT_ALLIED_FORCES_VS_DINOSAURS = "BAMO_ExtractAlliedForcesVsDinosaurs"
BAMO_FIGHT_DINOSAURS = "BAMO_FightDinosaurs"
BAMO_FIGHT_MONSTERS = "BAMO_FightMonsters"
BAME_MONSTER_TAGS = "BAME_MONSTER_TAGS"
BAMO_LOCATE_ENEMY_FORCES = "BAMO_LocateEnemyForces"
BAMO_NEUTRALIZE_ALL_DRONES = "BAMO_NeutralizeAllDrones"
BAMO_PROTECT_BUILDINGS = "BAMO_ProtectBuildings"
BAMO_PROTECT_BUILDINGS_FROM_DINOSAURS = "BAMO_ProtectBuildingsFromDinosaurs"
BAMO_RECOVER_CARGO = "BAMO_RecoverCargo"
BAMO_RESCUE_NPC = "BAMO_RescueNPC"
BAME_RESCUENPC = "BAME_RESCUENPC"
BAMO_RESPOND_TO_DISTRESS_CALL = "BAMO_RespondToDistressCall"
BAMO_STORM_THE_CASTLE = "BAMO_StormTheCastle"  # 4 points
BAMO_SURVIVE_THE_AMBUSH = "BAMO_SurviveTheAmbush"

BAME_SCENE_ATTRIBUTES = "SCENE_ATTRIBUTES"

BAMO_TEST_MISSION = "BAMO_TEST_MISSION"

# The following two elements can be passed to conversations. If truthy, don't allow retreat or mercy in the
# conversations. Retreat here means when the PC drives the enemy team away and withdraw means when the enemy commander
# allows the PC to run away.
CONVO_CANT_RETREAT = "CONVO_CANT_RETREAT"
CONVO_CANT_WITHDRAW = "CONVO_CANT_WITHDRAW"

# Personal Scale Objectives
BAMOP_FIND_HERBS = "BAMOP_FIND_HERBS"
BAMOP_DUNGEONLIKE = "BAMOP_DUNGEONLIKE"
BAMEP_MONSTER_TYPE = "BAMEP_MONSTER_TYPE"
BAMOP_EXTERMINATE_MONSTERS = "BAMOP_EXTERMINATE_MONSTERS"
BAMOP_REPAIR_MACHINE = "BAMOP_REPAIR_MACHINE"
BAMOP_RESCUE_VICTIM = "BAMOP_RESCUE_VICTIM"
BAMEP_VICTIM_NAME = "BAMEP_VICTIM_NAME"

MAIN_OBJECTIVE_VALUE = 100


#   ******************************************
#   ***  ADVENTURE  SEEDS  AND  UTILITIES  ***
#   ******************************************

class MissionGrammar(dict):
    # A reminder class so that the text snippets needed by the mission show up as named parameters.
    # The "_pp" and "_ep" indicate Player Perspective and Enemy Perspective
    # objective is a present tense verb phrase describing each team's mission.
    # win is a clause in simple past describing the outcome if the player wins
    # lose is a clause in simple past describing the outcome if the player loses
    def __init__(self, objective_pp="[defeat_you]", objective_ep="[defeat_you]", win_pp="I defeated you",
                 win_ep="you defeated me", lose_pp="you defeated me", lose_ep="I defeated you", **kwargs):
        grammar_tag_kwargs = dict()
        for k, v in kwargs.items():
            grammar_tag_kwargs['[{}]'.format(k)] = [str(v)]
        super().__init__(**grammar_tag_kwargs)
        self["[objective_pp]"] = [objective_pp]
        self["[objective_ep]"] = [objective_ep]
        self["[win_pp]"] = [win_pp]
        self["[win_ep]"] = [win_ep]
        self["[lose_pp]"] = [lose_pp]
        self["[lose_ep]"] = [lose_ep]


class NewMissionNotification(pbge.BasicNotification):
    def __init__(self, mission_name, mission_gate=None):
        if mission_gate:
            text = 'New mission "{}" added to {}.'.format(mission_name, mission_gate.name)
        else:
            text = 'New mission "{}" added.'.format(mission_name)
        super().__init__(w=400, text=text, count=160)


class NewLocationNotification(pbge.BasicNotification):
    def __init__(self, mission_name, mission_gate=None):
        if mission_gate:
            text = 'New location "{}" added to {}.'.format(mission_name, mission_gate.name)
        else:
            text = 'New location "{}" added.'.format(mission_name)
        super().__init__(w=400, text=text, count=160)


class BuildAMissionSeed(adventureseed.AdventureSeed):
    # Optional elements:
    #   ENTRANCE_ANCHOR:    Anchor for the PC's entrance
    def __init__(self, camp, name, metroscene, return_wp, enemy_faction=None, allied_faction=None, rank=None,
                 objectives=(),
                 adv_type="BAM_MISSION", custom_elements=None, auto_exit=False, solo_mission=False,
                 scenegen=pbge.randmaps.SceneGenerator, 
                 architecture: gears.GearHeadArchitecture=None,
                 cash_reward=100, experience_reward=100, salvage_reward=True, on_win=None, on_loss=None,
                 combat_music=None, exploration_music=None,
                 one_chance=True, data=None, win_message="", loss_message="", mission_grammar=None,
                 make_enemies=True, defeat_trigger_on=True, scale=gears.scale.MechaScale, desc="",
                 call_win_loss_funs_after_card=False,
                 **kwargs):
        self.rank = rank or max(camp.pc.renown + 1, 10)
        cms_pstate = pbge.plots.PlotState(adv=self, rank=self.rank)
        cms_pstate.elements["METROSCENE"] = metroscene
        cms_pstate.elements["ADVENTURE_RETURN"] = return_wp
        cms_pstate.elements["ENEMY_FACTION"] = enemy_faction
        self.enemy_faction = enemy_faction
        cms_pstate.elements["ALLIED_FACTION"] = allied_faction
        self.allied_faction = allied_faction
        cms_pstate.elements["OBJECTIVES"] = objectives
        cms_pstate.elements["SCENEGEN"] = scenegen
        architecture = architecture or gharchitecture.MechaScaleDeadzone()
        cms_pstate.elements["ARCHITECTURE"] = architecture
        cms_pstate.elements[
            "ONE_CHANCE"] = one_chance  # If False, you can return to the combat zone until all objectives are complete.
        cms_pstate.elements["AUTO_EXIT"] = auto_exit
        if custom_elements:
            _=cms_pstate.elements.update(custom_elements)
        if win_message:
            cms_pstate.elements["WIN_MESSAGE"] = win_message
        if loss_message:
            cms_pstate.elements["LOSS_MESSAGE"] = loss_message
        cms_pstate.elements["COMBAT_MUSIC"] = combat_music or camp.campdata.get(
            gears.CAMPDATA_DEFAULT_MISSION_COMBAT_MUSIC) or "Komiku_-_03_-_Battle_Theme.ogg"
        cms_pstate.elements["EXPLO_MUSIC"] = exploration_music or camp.campdata.get(
            gears.CAMPDATA_DEFAULT_MISSION_EXPLO_MUSIC) or "Chronos.ogg"
        self.solo_mission = solo_mission
        if not mission_grammar:
            mission_grammar = MissionGrammar(**missiontext.MissionText(
                camp, objectives, metroscene, allied_faction, enemy_faction).get_mission_grammar_dict()
            )
        self.mission_grammar = mission_grammar
        self.make_enemies = make_enemies
        self.defeat_trigger_on = defeat_trigger_on
        self.scale = scale

        # Data is a dict of stuff that will get used by whatever plot created this adventure seed, or maybe it
        # can be used by some of the objectives. I dunno! It's just a dict of stuff! Do with it as you will.
        # Currently used by DZD tarot cards to record the win,lose outcomes of a mission.
        self.data = dict()
        if data:
            self.data.update(data)

        self.on_win = on_win
        self.on_loss = on_loss

        super().__init__(camp, name, adv_type=adv_type, pstate=cms_pstate, auto_set_rank=False, **kwargs)

        if cash_reward > 0:
            self.rewards.append(adventureseed.CashReward(size=cash_reward))
        if experience_reward > 0:
            self.rewards.append(adventureseed.ExperienceReward(size=experience_reward))
        if salvage_reward:
            self.rewards.append(adventureseed.SalvageReward())
        self.rewards.append(adventureseed.RenownReward())

        self.environment = architecture.ENV

        self.desc = desc
        self.call_win_loss_funs_after_card = call_win_loss_funs_after_card

    def copy(self):
        mycopy: BuildAMissionSeed = copy.copy(self)
        mycopy.pstate = pbge.plots.PlotState(adv=mycopy, rank=self.rank)
        _=mycopy.pstate.elements.update(self.pstate.elements)
        mycopy.objectives = copy.deepcopy(self.objectives)
        mycopy.results = list()
        mycopy.data = dict()
        mycopy.data.update(self.data)

    def end_adventure(self, camp: gears.GearHeadCampaign):
        # Update before ending, and again after.
        camp.check_trigger("UPDATE")
        if not self.call_win_loss_funs_after_card:
            if self.on_win and self.is_won():
                self.on_win(camp)
            elif self.on_loss and not self.is_won():
                self.on_loss(camp)
        if self.is_won() and self.enemy_faction:
            if self.defeat_trigger_on:
                camp.check_trigger("DEFEAT", self.enemy_faction)
            if self.make_enemies:
                camp.set_faction_as_pc_enemy(self.enemy_faction)
        super(BuildAMissionSeed, self).end_adventure(camp)
        if self.call_win_loss_funs_after_card:
            if self.on_win and self.is_won():
                self.on_win(camp)
            elif self.on_loss and not self.is_won():
                self.on_loss(camp)
        camp.time += 1

    def can_do_mission(self, camp: gears.GearHeadCampaign):
        return bool(camp.get_usable_party(self.scale, self.solo_mission, just_checking=True, enviro=self.environment))

    @staticmethod
    def _combatant_name(camp: gears.GearHeadCampaign, pc):
        if hasattr(pc, "pilot"):
            return "{}'s {}".format(pc.pilot, pc)
        else:
            return str(pc)

    def __call__(self, camp: gears.GearHeadCampaign):
        # Start with the total party list for this map scale.
        total_party = camp.get_usable_party(self.scale, self.solo_mission, just_checking=True, enviro=None)
        if total_party:
            usable_party = camp.get_usable_party(self.scale, self.solo_mission, just_checking=True,
                                                 enviro=self.environment)
            benchwarmers = [pc for pc in total_party if pc not in usable_party]
            if benchwarmers:
                mymenu = pbge.rpgmenu.AlertMenu(
                    "{} will be left behind. The environment for this mission is {} so all combatants must be able to {}.".format(
                        pbge.dialogue.list_nouns([self._combatant_name(camp, bw) for bw in benchwarmers]), self.environment,
                        pbge.dialogue.list_nouns(self.environment.LEGAL_MOVEMODES, conjunction="or")))
                mymenu.add_item("Do the mission without them.", True)
                mymenu.add_item("Come back to the mission later", False)
                if mymenu.query():
                    return super().__call__(camp)
            else:
                return super().__call__(camp)
        else:
            if self.scale is gears.scale.MechaScale:
                pbge.alert("You cannot proceed on this mission without a mecha.")
            else:
                pbge.alert("You cannot proceed on this mission.")

    def is_good_enemy_npc(self, nart, candidate):
        # Utility function for doing an enemy search. If the enemy_faction is a base faction, this function
        # will accept any child circles of that faction as well.
        return (
                isinstance(candidate, gears.base.Character) and candidate.combatant and
                (candidate.faction == self.enemy_faction or
                 (candidate.faction and candidate.faction.get_faction_tag() == self.enemy_faction)) and
                (not nart.camp.are_faction_allies(candidate, self.allied_faction)) and
                nart.camp.is_not_lancemate(candidate) and candidate.renown <= (self.rank + 25)
        )

    def is_good_backup_enemy(self, nart, candidate):
        # Backup seek function; will accept any faction ally.
        return (
                isinstance(candidate, gears.base.Character) and candidate.combatant and
                nart.camp.are_faction_allies(candidate, self.enemy_faction) and
                (not nart.camp.are_faction_allies(candidate, self.allied_faction)) and
                candidate not in nart.camp.party and candidate.renown <= (self.rank + 25)
        )

    def __setstate__(self, state):
        self.__dict__.update(state)
        # for saves from v0.950 or earlier:
        if "call_win_loss_funs_after_card" not in state:
            self.call_win_loss_funs_after_card = False
        # For saves from v0.612 or earlier, make sure there's an environment.
        if "environment" not in state:
            self.environment = gears.tags.GroundEnv
        # From v0.905 or earlier, make sure we have a scale.
        if "scale" not in state:
            self.scale = gears.scale.MechaScale


class BuildAMissionPlot(Plot):
    # Go fight mecha. Repeatedly.
    LABEL = "BAM_MISSION"
    active = True
    scope = "LOCALE"

    DEFAULT_SCENE_WIDTH = 50
    DEFAULT_SCENE_HEIGHT = 50

    def custom_init(self, nart):
        """An empty map that will add subplots for the mission's objectives."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(
            self.DEFAULT_SCENE_WIDTH, self.DEFAULT_SCENE_HEIGHT,
            "Combat Zone", player_team=team1, scale=self.adv.scale,
            combat_music=self.elements["COMBAT_MUSIC"], exploration_music=self.elements["EXPLO_MUSIC"],
            environment=self.adv.environment,
            attributes=self.elements.get(BAME_SCENE_ATTRIBUTES, (gears.tags.SCENE_OUTDOORS,))
        )
        if self.adv.solo_mission:
            myscene.attributes.add(gears.tags.SCENE_SOLO)
        myscenegen = self.elements["SCENEGEN"](myscene, self.elements["ARCHITECTURE"])
        self.register_scene(nart, myscene, myscenegen, ident="LOCALE", temporary=True, dident="METROSCENE")
        self.adv.world = myscene

        self._generate_entrance_room()

        for ob in self.elements["OBJECTIVES"]:
            self.add_sub_plot(nart, ob)

        self.started_mission = False
        self.gave_mission_reminder = False
        self.gave_ending_message = False
        self.exited_mission = False

        self.memo = adventureseed.CombatMissionMemo(self.adv)

        return True

    def _generate_entrance_room(self):
        # Set ENTRANCE_ANCHOR, ENTRANCE_ROOM, and _ENTRANCE
        myanchor = self.elements.setdefault("ENTRANCE_ANCHOR", random.choice(pbge.randmaps.anchors.EDGES))
        self.register_element("ENTRANCE_ROOM", pbge.randmaps.rooms.OpenRoom(7, 7, anchor=myanchor), dident="LOCALE")
        self.register_element("_ENTRANCE", game.content.ghwaypoints.Exit(anchor=pbge.randmaps.anchors.middle,
                                                                         plot_locked=True),
                              dident="ENTRANCE_ROOM")

    def start_mission(self, camp):
        camp.go(self.elements["_ENTRANCE"])
        if not self.started_mission:
            self.started_mission = True

    def t_START(self, camp):
        if camp.scene is self.elements["LOCALE"] and not self.gave_mission_reminder:
            mydisplay = adventureseed.CombatMissionDisplay(title=self.adv.name, mission_seed=self.adv, width=400)
            pbge.alert_display(mydisplay.show)
            if self.elements.get("ENEMY_FACTION"):
                camp.add_faction_score(self.elements.get("ENEMY_FACTION"), -5)
            self.gave_mission_reminder = True

    def t_ENDCOMBAT(self, camp):
        # If the player team gets wiped out, end the mission.
        if not camp.first_active_pc():
            self.exit_the_mission(camp)

    def t_FORCE_EXIT(self, camp):
        # If the player leaves the scene for whatever reason, end the mission.
        self.exit_the_mission(camp)

    def t_EXIT(self, camp):
        # If the player leaves the scene for whatever reason, end the mission.
        self.exit_the_mission(camp)

    def t_UPDATE(self, camp):
        if self.adv.is_completed():
            if not self.gave_ending_message:
                if self.adv.is_won():
                    if "WIN_MESSAGE" in self.elements:
                        pbge.alert(self.elements["WIN_MESSAGE"])
                    pbge.BasicNotification("Mission Complete", count=160)
                elif "LOSS_MESSAGE" in self.elements:
                    pbge.alert(self.elements["LOSS_MESSAGE"])
                    pbge.BasicNotification("Mission Failed", count=160)
                self.gave_ending_message = True
            if self.elements.get("AUTO_EXIT", False) and not self.exited_mission:
                self.exit_the_mission(camp)

    def _ENTRANCE_menu(self, camp, thingmenu):
        if self.adv.is_completed():
            thingmenu.desc = "Your mission is finished. Are you ready to return to {}?".format(
                self.elements["METROSCENE"])
            thingmenu.add_item("End Mission", self.exit_the_mission)
            thingmenu.add_item("Stay Here Longer", None)
        else:
            thingmenu.desc = "Do you want to abort this mission and return to {}?".format(
                self.elements["METROSCENE"])
            thingmenu.add_item("Cancel Mission", self.exit_the_mission)
            thingmenu.add_item("Continue Mission", None)

    def exit_the_mission(self, camp: gears.GearHeadCampaign):
        camp.go(self.elements["ADVENTURE_RETURN"])
        self.exited_mission = True
        if self.elements["ONE_CHANCE"] or self.adv.is_completed():
            if self.elements.get("ALLIED_FACTION"):
                if self.adv.is_won():
                    camp.add_faction_score(self.elements.get("ALLIED_FACTION"), random.randint(1, 6))
                else:
                    camp.add_faction_score(self.elements.get("ALLIED_FACTION"), -3)

            self.adv.end_adventure(camp)
        elif not self.elements["ONE_CHANCE"]:
            # Restore the mission for next time.
            self.adv.restore_party(camp)
            mydisplay = adventureseed.CombatResultsDisplay(title="Failure: {}".format(self.adv.get_grade()),
                                                           title_color=pygame.color.Color(250, 50, 0),
                                                           mission_seed=self.adv,
                                                           width=400)
            pbge.alert_display(mydisplay.show)
            self.adv.results = list()

            for npc in [n for n in camp.scene.contents if isinstance(n, gears.base.BaseGear)]:
                if npc not in camp.party:
                    npc.restore_all()
            for o in self.adv.objectives:
                o.reset_objective()

    def _get_dialogue_grammar(self, npc, camp):
        return self.adv.mission_grammar.copy()


class RoadMissionPlot(BuildAMissionPlot):
    # based on the regular Build-a-Mission plot, but automatically exits when the mission is complete.
    # Custom element: ADVENTURE_GOAL, the waypoint of the destination node.
    LABEL = "BAM_ROAD_MISSION"

    def t_ENDCOMBAT(self, camp):
        # If the player team gets wiped out, end the mission.
        # If the player team wins, also end the mission.
        if not camp.first_active_pc():
            self.exit_the_mission(camp)
        elif self.adv.is_completed():
            self.exit_the_mission(camp)

    def _ENTRANCE_menu(self, camp, thingmenu):
        thingmenu.desc = "Do you want to end this journey and return to {}?".format(self.elements["METROSCENE"])

        thingmenu.add_item("Return to {}".format(self.elements["METROSCENE"]), self.exit_the_mission)
        thingmenu.add_item("Journey Onward", None)

    def exit_the_mission(self, camp):
        if self.adv.is_won():
            camp.go(self.elements["ADVENTURE_GOAL"])
        else:
            camp.go(self.elements["ADVENTURE_RETURN"])
        self.adv.end_adventure(camp)


class EscortMissionPlot(BuildAMissionPlot):
    # Kinda like the road mission, but we've got a ESCORT_ROOM in which to deploy whatever we're escorting and a
    # clear path to the other side of the map.
    LABEL = "BAM_ESCORT_MISSION"
    DEFAULT_SCENE_WIDTH = 60
    DEFAULT_SCENE_HEIGHT = 60

    def _generate_entrance_room(self):
        # Set ENTRANCE_ANCHOR, ENTRANCE_ROOM, and _ENTRANCE
        myanchor = self.elements.setdefault("ENTRANCE_ANCHOR", random.choice(pbge.randmaps.anchors.CARDINALS))
        if myanchor not in pbge.randmaps.anchors.CARDINALS:
            myanchor = random.choice(pbge.randmaps.anchors.CARDINALS)
            self.elements["ENTRANCE_ANCHOR"] = myanchor
        myscene: gears.GearHeadScene = self.elements["LOCALE"]
        if myanchor in (pbge.randmaps.anchors.east, pbge.randmaps.anchors.west):
            corridor = pbge.randmaps.rooms.OpenRoom(width=myscene.width, height=15, anchor=pbge.randmaps.anchors.west)
        else:
            corridor = pbge.randmaps.rooms.OpenRoom(width=15, height=myscene.height, anchor=pbge.randmaps.anchors.north)
        self.register_element("ESCORT_PATH", corridor, dident="LOCALE")
        interior_anchors = list(pbge.randmaps.anchors.ADJACENT_ANCHORS[myanchor])
        random.shuffle(interior_anchors)
        self.register_element("ENTRANCE_ROOM", pbge.randmaps.rooms.OpenRoom(5, 5, anchor=interior_anchors[0]), dident="ESCORT_PATH")
        self.register_element("_ENTRANCE",
                              game.content.ghwaypoints.Exit(anchor=pbge.randmaps.anchors.middle, plot_locked=True),
                              dident="ENTRANCE_ROOM")
        self.register_element("ESCORT_ROOM", pbge.randmaps.rooms.OpenRoom(8, 8, anchor=interior_anchors[1]), dident="ESCORT_PATH")


#   ****************************
#   ***   OBJECTIVE MIXINS   ***
#   ****************************

class Championify(object):
    '''
    Modifies an objective so that it has a champion.
    If there is a _commander element that is a character,
    its mek gets upgraded, and any _assistant element as well
    has 50% chance of getting its mek upgraded.
    If there is no commander but there is an _eteam element
    that is a team, a random member of the eteam gets it.

    To use, define a normal championless plot, then
    define a new plot that mixes this in, but as the first
    base class:

    class BAM_DoAnObjective(Plot):
        LABEL = BAM_DO_AN_OBJECTIVE
        active = True
        scope = "LOCALE"

        def custom_init(self, nart):
            pass     # whatever

    # Now this has a champion as well:
    class BAM_ChampionDoAnObjective(Championify, BAM_DoAnObjective):
        pass


    NOTE: This is not compatible with any other mixins.
    '''
    championify_commander_element = "_commander"
    championify_assistant_element = "_assistant"
    championify_eteam_element = "_eteam"

    def custom_init(self, nart):
        # Introspect.
        # Final derived class.
        dcls = self.__class__
        # Original class that was mixed in.
        ocls = None

        # Identify the class being mixed in.
        for c in dcls.mro():
            if c is Championify or c is dcls:
                continue
            ocls = c
            break
        # No class?  Fail.
        if not ocls:
            return False

        # Execute the original class custom_init.
        if not ocls.custom_init(self, nart):
            # Original custom init failed, so fail this one too.
            return False

        def upgrade_mek_of(char):
            mek = char.get_root()
            if not isinstance(mek, gears.base.Mecha):
                return
            # TODO: Add a persistent pref_champion to character?
            champions.upgrade_to_champion(mek)

        commander = self.elements.get(self.championify_commander_element, None)
        if commander and isinstance(commander, gears.base.Character):
            upgrade_mek_of(commander)
            if random.randint(1, 2) == 1:
                return True
            assistant = self.elements.get(self.championify_assistant_element, None)
            if assistant and isinstance(assistant, gears.base.Character):
                upgrade_mek_of(assistant)
            return True

        eteam = self.elements.get(self.championify_eteam_element, None)
        if eteam and isinstance(eteam, teams.Team):
            mek = random.choice(eteam.contents)
            if isinstance(mek, gears.base.Mecha):
                champions.upgrade_to_champion(mek)

        return True


#   **********************
#   ***   OBJECTIVES   ***
#   **********************

class BAM_AidAlliedForces(Plot):
    LABEL = BAMO_AID_ALLIED_FORCES
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        self.num_battles = random.randint(2, 3)
        self.enemy_team_ok = dict()
        for t in range(self.num_battles):
            roomtype = self.elements["ARCHITECTURE"].get_a_room()
            myroom = self.register_element("_room_{}".format(t), roomtype(6, 6), dident="LOCALE")
            eteam = self.register_element("_eteam_{}".format(t), teams.Team(enemies=(myscene.player_team,)),
                                          dident="_room_{}".format(t))
            ateam = self.register_element("_ateam_{}.format(t)",
                                          teams.Team(enemies=(eteam,), allies=(myscene.player_team,)),
                                          dident="_room_{}".format(t))
            eunit = gears.selector.RandomMechaUnit(self.rank, 400 // self.num_battles,
                                                   self.elements.get("ENEMY_FACTION"), myscene.environment,
                                                   add_commander=False)
            eteam.contents += eunit.mecha_list
            aunit = gears.selector.RandomMechaUnit(self.rank - 10, 150 // self.num_battles,
                                                   self.elements.get("ALLIED_FACTION"), myscene.environment,
                                                   add_commander=False)
            ateam.contents += aunit.mecha_list
            self.enemy_team_ok[eteam] = True

        self.obj = adventureseed.MissionObjective("Aid allied forces", MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)

        return True

    def t_ENDCOMBAT(self, camp):
        num_destroyed_teams = 0
        for eteam, etact in self.enemy_team_ok.items():
            if len(eteam.get_members_in_play(camp)) < 1:
                if self.enemy_team_ok[eteam]:
                    self.enemy_team_ok[eteam] = False
                    pbge.alert("Area secured.")
                num_destroyed_teams += 1

        if num_destroyed_teams >= self.num_battles:
            self.obj.win(camp, 100)


class BAM_CaptureMine(Plot):
    LABEL = BAMO_CAPTURE_THE_MINE
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(10, 10), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank, 100, self.elements.get("ENEMY_FACTION"), myscene.environment,
                                                add_commander=True)
        team2.contents += myunit.mecha_list

        team3 = self.register_element("_propteam", teams.Team(), dident="ROOM")
        team3.contents += [gears.selector.get_design_by_full_name("Mine Entrance"),
                           gears.selector.get_design_by_full_name("Chemical Tanks")]
        # Oh yeah, when using PyCharm, why not use ludicrously long variable names?
        self.starting_number_of_props = len(team3.contents)

        self.obj = adventureseed.MissionObjective("Capture the mine", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)
        self.combat_entered = False
        self.combat_finished = False

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if not self.combat_entered:
            self.combat_entered = True

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        propteam = self.elements["_propteam"]
        if len(propteam.get_members_in_play(camp)) < 1:
            self.obj.failed = True
        elif len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, (sum([(100 - c.get_percent_damage_over_health()) for c in
                                     propteam.get_members_in_play(camp)])) // self.starting_number_of_props)
            if not self.combat_finished:
                pbge.alert("The mine has been secured.")
                self.combat_finished = True


class BAM_CaptureBuildings(Plot):
    LABEL = BAMO_CAPTURE_BUILDINGS
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(10, 10), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank, 100, self.elements.get("ENEMY_FACTION"), myscene.environment,
                                                add_commander=True)
        team2.contents += myunit.mecha_list

        team3 = self.register_element("_propteam", teams.Team(), dident="ROOM")
        for t in range(random.randint(1, 2 + self.rank // 25)):
            team3.contents.append(gears.selector.get_design_by_full_name("Concrete Building"))
        # Oh yeah, when using PyCharm, why not use ludicrously long variable names?
        self.starting_number_of_props = len(team3.contents)

        self.obj = adventureseed.MissionObjective("Capture the buildings", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)
        self.combat_entered = False
        self.combat_finished = False

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if not self.combat_entered:
            self.combat_entered = True

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        propteam = self.elements["_propteam"]
        if len(propteam.get_members_in_play(camp)) < 1:
            self.obj.failed = True
        elif len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, (sum([(100 - c.get_percent_damage_over_health()) for c in
                                     propteam.get_members_in_play(camp)])) // self.starting_number_of_props)
            if not self.combat_finished:
                pbge.alert("The complex has been secured.")
                self.combat_finished = True


class BAM_DefeatArmy(Plot):
    LABEL = BAMO_DEFEAT_ARMY
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        npc1 = self.seek_element(nart, "_commander", self.adv.is_good_enemy_npc, must_find=False, lock=True,
                                 backup_seek_func=self.adv.is_good_backup_enemy)
        if npc1:
            plotutility.CharacterMover(nart.camp, self, npc1, myscene, team2)
            myunit = gears.selector.RandomMechaUnit(self.rank, 120, myfac, myscene.environment, add_commander=False)
        else:
            myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=True)
            self.register_element("_commander", myunit.commander, lock=True)

        team2.contents += myunit.mecha_list

        npc2 = self.seek_element(nart, "_assistant", self.adv.is_good_enemy_npc, must_find=False, lock=True,
                                 backup_seek_func=self.adv.is_good_backup_enemy)
        if npc2:
            plotutility.CharacterMover(nart.camp, self, npc2, myscene, team2)
        else:
            mek = gears.selector.generate_ace(self.rank, myfac, myscene.environment)
            team2.contents.append(mek)
            npc2 = self.register_element("_assistant",
                                         mek.get_pilot(), lock=True)

        self.obj = adventureseed.MissionObjective("Defeat {_commander} and {_assistant}".format(**self.elements),
                                                  MAIN_OBJECTIVE_VALUE * 3)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def _commander_offers(self, camp):
        mylist = list()
        mylist.append(Offer("Hey {_assistant}, why don't we [defeat_them]?".format(**self.elements),
                            effect=self._assistant_monologue,
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def _assistant_monologue(self, camp):
        SimpleMonologueDisplay("[NO_PROBLEM_FOR_TWO_OF_US]", self.elements["_assistant"])(camp)

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class BAM_DefeatBlockade(Plot):
    LABEL = BAMO_DEFEAT_BLOCKADE
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        if myfac:
            mynpc = self.seek_element(nart, "_commander", self.adv.is_good_enemy_npc, must_find=False, lock=True,
                                      backup_seek_func=self.adv.is_good_backup_enemy)
        else:
            mynpc = None
        if mynpc:
            unit_size = 120
            if mynpc.renown > self.rank:
                unit_size = max(unit_size + self.rank - mynpc.renown, 50)
            plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
            myunit = gears.selector.RandomMechaUnit(self.rank, unit_size, myfac, myscene.environment,
                                                    add_commander=False)
            self.add_sub_plot(nart, "MC_ENEMY_DEVELOPMENT", elements={"NPC": mynpc})

        else:
            myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=True)
            mynpc = self.register_element("_commander", myunit.commander)
            self.add_sub_plot(nart, "MC_NDBCONVERSATION", elements={"NPC": myunit.commander.get_pilot()})

        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Defeat {}'s Lance".format(mynpc.get_pilot()), MAIN_OBJECTIVE_VALUE*2)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class BAM_DefeatCommander(Plot):
    LABEL = BAMO_DEFEAT_COMMANDER
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc = self.register_element("_commander", nart.camp.cast_a_combatant(
            myfac, self.rank, opposed_faction=self.elements["ALLIED_FACTION"], myplot=self
        ), lock=True)
        plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
        myunit = gears.selector.RandomMechaUnit(self.rank, 120, myfac, myscene.environment, add_commander=False)
        self.elements["CONVO_CANT_RETREAT"] = True
        self.add_sub_plot(nart, "MC_ENEMY_DEVELOPMENT", elements={"NPC": mynpc})

        # mynpc = self.seek_element(nart, "_commander", self.adv.is_good_enemy_npc, must_find=False, lock=True,
        #                          backup_seek_func=self.adv.is_good_backup_enemy)
        # if mynpc:
        #    plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
        #    myunit = gears.selector.RandomMechaUnit(self.rank, 120, myfac, myscene.environment, add_commander=False)
        #    self.add_sub_plot(nart, "MC_ENEMY_DEVELOPMENT", elements={"NPC": mynpc})
        # else:
        #    myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=True)
        #    self.register_element("_commander", myunit.commander, lock=True)
        #    self.add_sub_plot(nart, "MC_NDBCONVERSATION", elements={"NPC": myunit.commander.get_pilot()})

        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Defeat enemy commander {}".format(self.elements["_commander"]),
                                                  MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class BAM_DefeatNPC(Plot):
    LABEL = BAMO_DEFEAT_NPC
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc = self.elements.get(BAME_NPC)
        if mynpc:
            self.locked_elements.add(BAME_NPC)
            plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
            myunit = gears.selector.RandomMechaUnit(self.rank, 120, myfac, myscene.environment, add_commander=False)
            self.add_sub_plot(nart, "MC_ENEMY_DEVELOPMENT", elements={"NPC": mynpc})
        else:
            myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=True)
            self.register_element(BAME_NPC, myunit.commander.get_pilot())
            self.add_sub_plot(nart, "MC_NDBCONVERSATION", elements={"NPC": myunit.commander.get_pilot()})

        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Defeat enemy pilot {}".format(self.elements[BAME_NPC]),
                                                  MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements[BAME_NPC]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class BAM_DuelNPC(Plot):
    LABEL = BAMO_DUEL_NPC
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc = self.elements.get(BAME_NPC)
        if mynpc:
            if mynpc.renown < self.rank:
                if not mynpc.job:
                    mynpc.job = gears.jobs.ALL_JOBS["Arena Pilot"]
                mynpc.job.scale_skills(mynpc, min(mynpc.renown + random.randint(1, 10), self.rank))
            self.locked_elements.add(BAME_NPC)
            plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
        else:
            mynpc = self.register_element(BAME_NPC, gears.selector.random_character(
                self.rank, faction=myfac, current_year=nart.camp.year, combatant=True
            ), lock=True)
            team2.contents.append(mynpc)
        self.add_sub_plot(nart, "MC_DUEL_DEVELOPMENT", elements={"NPC": mynpc})

        self.obj = adventureseed.MissionObjective("Duel {}".format(self.elements[BAME_NPC]),
                                                  MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements[BAME_NPC]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class BAM_DefeatTheBandits(Plot):
    LABEL = BAMO_DEFEAT_THE_BANDITS
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        if myfac:
            mynpc = self.seek_element(nart, "_commander", self.adv.is_good_enemy_npc, must_find=False, lock=True,
                                      backup_seek_func=self.adv.is_good_backup_enemy)
        else:
            mynpc = None
        if mynpc:
            unit_size = 120
            if mynpc.renown > self.rank:
                unit_size = max(unit_size + self.rank - mynpc.renown, 50)
            plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
            myunit = gears.selector.RandomMechaUnit(self.rank, unit_size, myfac, myscene.environment,
                                                    add_commander=False)
            self.add_sub_plot(nart, "MC_ENEMY_DEVELOPMENT", elements={"NPC": mynpc})

        else:
            myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=True)
            self.register_element("_commander", myunit.commander)
            self.add_sub_plot(nart, "MC_NDBCONVERSATION", elements={"NPC": myunit.commander.get_pilot()})

        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Defeat the bandits".format(myfac), MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class BAM_DefeatTheBandits_NoCommander(Plot):
    LABEL = BAMO_DEFEAT_THE_BANDITS
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=False)

        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Defeat the bandits".format(myfac), MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class BAM_DestroyArtillery(Plot):
    LABEL = BAMO_DESTROY_ARTILLERY
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15, anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc = self.seek_element(nart, "_commander", self.adv.is_good_enemy_npc, must_find=False, lock=True,
                                  backup_seek_func=self.adv.is_good_backup_enemy)
        if mynpc:
            plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
            myunit = gears.selector.RandomMechaUnit(self.rank, 70, myfac, myscene.environment, add_commander=False)
            self.add_sub_plot(nart, "MC_ENEMY_DEVELOPMENT", elements={"NPC": mynpc})

        else:
            myunit = gears.selector.RandomMechaUnit(self.rank, 100, myfac, myscene.environment, add_commander=True)
            self.register_element("_commander", myunit.commander, lock=True)
            self.add_sub_plot(nart, "MC_NDBCONVERSATION", elements={"NPC": myunit.commander.get_pilot()})

        team2.contents += myunit.mecha_list

        myfac = self.elements.get("ENEMY_FACTION")
        if myfac:
            colors = myfac.mecha_colors
        else:
            colors = gears.color.random_mecha_colors()

        for t in range(random.randint(1, 2) + max(self.rank // 20, 0)):
            team2.contents.append(gears.selector.get_design_by_full_name("HAL-82 Artillery"))
            team2.contents[-1].colors = colors

        self.obj = adventureseed.MissionObjective("Destroy enemy artillery", MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class BAM_ExtractAllies(Plot):
    LABEL = BAMO_EXTRACT_ALLIED_FORCES
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(10, 10), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team3 = self.register_element("_ateam", teams.Team(enemies=(team2,), allies=(myscene.player_team,)),
                                      dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank, 200, self.elements.get("ENEMY_FACTION"), myscene.environment,
                                                add_commander=False)
        team2.contents += myunit.mecha_list

        mynpc = self.seek_element(nart, "PILOT", self._npc_is_good, must_find=False, lock=True)
        if mynpc:
            plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team3)
            mek = mynpc.get_root()
            self.register_element("SURVIVOR", mek)
            self.add_sub_plot(nart, "MT_TEAMUP_DEVELOPMENT", ident="NPC_TALK", elements={"NPC": mynpc, })
        else:
            mysurvivor = self.register_element("SURVIVOR", gears.selector.generate_ace(self.rank, self.elements.get(
                "ALLIED_FACTION"), myscene.environment))
            mynpc = mysurvivor.get_pilot()
            self.register_element("PILOT", mynpc, lock=True)
            team3.contents.append(mysurvivor)
            self.add_sub_plot(nart, "MT_NDDEV", ident="NPC_TALK", elements={"NPC": mynpc, })

        self.obj = adventureseed.MissionObjective("Extract allied pilot {}".format(self.elements["PILOT"]),
                                                  MAIN_OBJECTIVE_VALUE, can_reset=False)
        self.adv.objectives.append(self.obj)
        self.intro_ready = True
        self.eteam_activated = False
        self.eteam_defeated = False
        self.pilot_fled = False

        return True

    def _npc_is_good(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.combatant and \
            nart.camp.are_faction_allies(candidate.faction, self.elements["ALLIED_FACTION"]) and \
            candidate not in nart.camp.party

    def PILOT_offers(self, camp):
        mylist = list()
        mylist.append(Offer(self.subplots["NPC_TALK"].START_COMBAT_MESSAGE,
                            context=ContextTag([context.HELLO, ]), ))
        if not camp.fight:
            mylist.append(
                Offer("[THANK_YOU] I need to get back to base.",
                      context=ContextTag([context.CUSTOM, ]), data={"reply": "Get out of here, I can handle this."},
                      effect=self.pilot_leaves_before_combat, dead_end=True)
            )

        return mylist

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            self.eteam_activated = True
            if not self.pilot_fled:
                npc = self.elements["PILOT"]
                camp.check_trigger("START", npc)
                camp.fight.active.append(self.elements["SURVIVOR"])
            self.intro_ready = False

    def pilot_leaves_before_combat(self, camp):
        self.obj.win(camp, 105)
        self.pilot_leaves_combat(camp)

    def pilot_leaves_combat(self, camp: gears.GearHeadCampaign):
        if not self.pilot_fled:
            npc = self.elements["PILOT"]
            if not npc.relationship:
                npc.relationship = camp.get_relationship(npc)
            npc.relationship.reaction_mod += 10
        if self.elements["SURVIVOR"] in camp.scene.contents:
            camp.scene.contents.remove(self.elements["SURVIVOR"])
        self.pilot_fled = True

    def t_ENDCOMBAT(self, camp):
        if self.eteam_activated and not self.pilot_fled:
            myteam = self.elements["_ateam"]
            eteam = self.elements["_eteam"]
            npc = self.elements["PILOT"]
            if len(myteam.get_members_in_play(camp)) < 1:
                self.obj.failed = True
                camp.check_trigger("LOSE", npc)
            elif len(myteam.get_members_in_play(camp)) > 0 and len(eteam.get_members_in_play(camp)) < 1:
                self.eteam_defeated = True
                self.obj.win(camp, 100 - self.elements["SURVIVOR"].get_percent_damage_over_health())
                camp.check_trigger("WIN", npc)
                self.pilot_leaves_combat(camp)


class BAM_ChampionExtractAllies(Championify, BAM_ExtractAllies):
    active = True


class BAM_ExtractAlliesVsDinosaurs(Plot):
    LABEL = BAMO_EXTRACT_ALLIED_FORCES_VS_DINOSAURS
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(10, 10), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team3 = self.register_element("_ateam", teams.Team(enemies=(team2,), allies=(myscene.player_team,)),
                                      dident="ROOM")

        myunit = gears.selector.RandomMonsterUnit(self.rank, random.randint(100, 120), myscene.environment,
                                                  ("DINOSAUR",), myscene.scale)
        team2.contents += myunit.contents

        mynpc = self.seek_element(nart, "PILOT", self._npc_is_good, must_find=False, lock=True)
        if mynpc:
            plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team3)
            mek = mynpc.get_root()
            self.register_element("SURVIVOR", mek)
            self.add_sub_plot(nart, "MT_TEAMUP_DEVELOPMENT", ident="NPC_TALK", elements={"NPC": mynpc, })
        else:
            mysurvivor = self.register_element("SURVIVOR", gears.selector.generate_ace(self.rank, self.elements.get(
                "ALLIED_FACTION"), myscene.environment))
            mynpc = mysurvivor.get_pilot()
            self.register_element("PILOT", mynpc, lock=True)
            team3.contents.append(mysurvivor)
            self.add_sub_plot(nart, "MT_NDDEV", ident="NPC_TALK", elements={"NPC": mynpc, })

        self.obj = adventureseed.MissionObjective("Rescue allied pilot {}".format(self.elements["PILOT"]),
                                                  MAIN_OBJECTIVE_VALUE, can_reset=False)
        self.adv.objectives.append(self.obj)
        self.intro_ready = True
        self.eteam_activated = False
        self.eteam_defeated = False
        self.pilot_fled = False

        return True

    def _npc_is_good(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.combatant and \
            nart.camp.are_faction_allies(candidate.faction, self.elements["ALLIED_FACTION"]) and \
            candidate not in nart.camp.party

    def PILOT_offers(self, camp):
        mylist = list()
        mylist.append(Offer(self.subplots["NPC_TALK"].START_COMBAT_MESSAGE,
                            context=ContextTag([context.HELLO, ]), ))
        if not camp.fight:
            mylist.append(
                Offer("[THANK_YOU] I need to get back to base.",
                      context=ContextTag([context.CUSTOM, ]), data={"reply": "Get out of here, I can handle this."},
                      effect=self.pilot_leaves_before_combat, dead_end=True)
            )

        return mylist

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            self.eteam_activated = True
            if not self.pilot_fled:
                npc = self.elements["PILOT"]
                camp.check_trigger("START", npc)
                camp.fight.active.append(self.elements["SURVIVOR"])
            self.intro_ready = False

    def pilot_leaves_before_combat(self, camp):
        self.obj.win(camp, 105)
        self.pilot_leaves_combat(camp)

    def pilot_leaves_combat(self, camp):
        if not self.pilot_fled:
            npc = self.elements["PILOT"]
            npc.relationship.reaction_mod += 10
        camp.scene.contents.remove(self.elements["SURVIVOR"])
        self.pilot_fled = True

    def t_ENDCOMBAT(self, camp):
        if self.eteam_activated and not self.pilot_fled:
            myteam = self.elements["_ateam"]
            eteam = self.elements["_eteam"]
            npc = self.elements["PILOT"]
            if len(myteam.get_members_in_play(camp)) < 1:
                self.obj.failed = True
                camp.check_trigger("LOSE", npc)
            elif len(myteam.get_members_in_play(camp)) > 0 and len(eteam.get_members_in_play(camp)) < 1:
                self.eteam_defeated = True
                self.obj.win(camp, 100 - self.elements["SURVIVOR"].get_percent_damage_over_health())
                camp.check_trigger("WIN", npc)
                self.pilot_leaves_combat(camp)


class BAM_FightDinosaurs(Plot):
    LABEL = BAMO_FIGHT_DINOSAURS
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        myunit = gears.selector.RandomMonsterUnit(self.rank, random.randint(100, 120), myscene.environment,
                                                  ("DINOSAUR",), myscene.scale)
        team2.contents += myunit.contents

        self.obj = adventureseed.MissionObjective("Defeat the dinosaurs", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        return True

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class BAM_FightMonsters(Plot):
    LABEL = BAMO_FIGHT_MONSTERS
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        myunit = gears.selector.RandomMonsterUnit(self.rank, random.randint(100, 120), myscene.environment,
                                                  self.elements.get(BAME_MONSTER_TAGS), myscene.scale)
        team2.contents += myunit.contents

        self.obj = adventureseed.MissionObjective("Defeat the monsters", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        return True

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class BAM_LocateEnemyForces(Plot):
    LABEL = BAMO_LOCATE_ENEMY_FORCES
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15), dident="LOCALE")
        self.register_element("DUD_ROOM", pbge.randmaps.rooms.FuzzyRoom(5, 5), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank, 100, myfac, myscene.environment, add_commander=True)
        team2.contents += myunit.mecha_list
        self.register_element("_commander", myunit.commander)

        if myfac:
            self.obj = adventureseed.MissionObjective("Locate {} forces".format(myfac), MAIN_OBJECTIVE_VALUE)
        else:
            self.obj = adventureseed.MissionObjective("Locate enemy forces", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def _commander_offers(self, camp):
        mylist = list()
        mylist.append(Offer("[CHALLENGE]",
                            context=ContextTag([context.CHALLENGE, ])))
        return mylist

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class BAM_NeutralizeAllDrones(Plot):
    LABEL = BAMO_NEUTRALIZE_ALL_DRONES
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        if myfac:
            colors = myfac.mecha_colors
        else:
            colors = gears.color.random_mecha_colors()
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(8, 8),
                              dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        for t in range(random.randint(3, 4)):
            mydrone = gears.selector.get_design_by_full_name("DZD-01 Sentry Drone")
            mydrone.colors = colors
            team2.contents.append(mydrone)

        self.obj = adventureseed.MissionObjective("Neutralize all security drones".format(myfac), MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        return True

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class BAM_ProtectBuildings(Plot):
    LABEL = BAMO_PROTECT_BUILDINGS
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(15, 15), dident="LOCALE")
        eroom = self.register_element("EROOM", pbge.randmaps.rooms.Room(6, 6), dident="ROOM")
        b_room = self.register_element("BROOM", pbge.randmaps.rooms.FuzzyRoom(4, 4), dident="ROOM")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="EROOM")
        myfac = self.elements.get("ENEMY_FACTION")

        myunit = gears.selector.RandomMechaUnit(self.rank, 100, myfac, myscene.environment, add_commander=True)
        team2.contents += myunit.mecha_list

        team3 = self.register_element("_propteam", teams.Team(enemies=(team2,), ), dident="BROOM")
        for t in range(random.randint(2, 3 + self.rank // 25)):
            team3.contents.append(gears.selector.get_design_by_full_name("Concrete Building"))
        # Oh yeah, when using PyCharm, why not use ludicrously long variable names?
        self.starting_number_of_props = len(team3.contents)

        self.obj = adventureseed.MissionObjective("Protect the buildings", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)
        self.combat_entered = False
        self.combat_finished = False

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if not self.combat_entered:
            self.combat_entered = True

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        propteam = self.elements["_propteam"]
        if len(propteam.get_members_in_play(camp)) < 1:
            self.obj.failed = True
        elif len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, (sum([(100 - c.get_percent_damage_over_health()) for c in
                                     propteam.get_members_in_play(camp)])) // self.starting_number_of_props)
            if not self.combat_finished:
                pbge.alert("The buildings have been secured.")
                self.combat_finished = True


class BAM_ProtectBuildingsFromDinos(Plot):
    LABEL = BAMO_PROTECT_BUILDINGS_FROM_DINOSAURS
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(10, 10), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        myunit = gears.selector.RandomMonsterUnit(self.rank, random.randint(100, 120), myscene.environment,
                                                  ("DINOSAUR",), myscene.scale)
        team2.contents += myunit.contents

        team3 = self.register_element("_propteam", teams.Team(enemies=(team2,), ), dident="ROOM")
        for t in range(random.randint(1, 2 + self.rank // 25)):
            team3.contents.append(gears.selector.get_design_by_full_name("Concrete Building"))
        # Oh yeah, when using PyCharm, why not use ludicrously long variable names?
        self.starting_number_of_props = len(team3.contents)

        self.obj = adventureseed.MissionObjective("Protect the buildings", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)
        self.combat_entered = False
        self.combat_finished = False

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if not self.combat_entered:
            self.combat_entered = True

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        propteam = self.elements["_propteam"]
        if len(propteam.get_members_in_play(camp)) < 1:
            self.obj.failed = True
        elif len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, (sum([(100 - c.get_percent_damage_over_health()) for c in
                                     propteam.get_members_in_play(camp)])) // self.starting_number_of_props)
            if not self.combat_finished:
                pbge.alert("The buildings have been secured.")
                self.combat_finished = True


class BAM_RecoverCargo(Plot):
    LABEL = BAMO_RECOVER_CARGO
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(10, 10), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank, 100, self.elements.get("ENEMY_FACTION"), myscene.environment,
                                                add_commander=True)
        team2.contents += myunit.mecha_list

        team3 = self.register_element("_cargoteam", teams.Team(), dident="ROOM")
        team3.contents += game.content.plotutility.CargoContainer.generate_cargo_fleet(self.rank)
        # Oh yeah, when using PyCharm, why not use ludicrously long variable names?
        self.starting_number_of_containers = len(team3.contents)

        self.obj = adventureseed.MissionObjective("Recover missing cargo", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)
        self.combat_entered = False
        self.combat_finished = False

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if not self.combat_entered:
            self.combat_entered = True

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        cargoteam = self.elements["_cargoteam"]
        if len(cargoteam.get_members_in_play(camp)) < 1:
            self.obj.failed = True
        elif len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, (sum([(100 - c.get_percent_damage_over_health()) for c in
                                     cargoteam.get_members_in_play(camp)])) // self.starting_number_of_containers)
            if not self.combat_finished:
                pbge.alert("The missing cargo has been secured.")
                self.combat_finished = True


class BAM_RescueSomeone(Plot):
    LABEL = BAMO_RESCUE_NPC
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(10, 10), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team3 = self.register_element("_ateam", teams.Team(enemies=(team2,), allies=(myscene.player_team,)),
                                      dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank, 200, self.elements.get("ENEMY_FACTION"), myscene.environment,
                                                add_commander=False)
        team2.contents += myunit.mecha_list

        mynpc = self.elements.get(BAME_RESCUENPC)
        if mynpc:
            self.register_element("PILOT", mynpc, lock=True)
            plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team3)
            mek = mynpc.get_root()
            self.register_element("SURVIVOR", mek)
            self.add_sub_plot(nart, "MT_TEAMUP_DEVELOPMENT", ident="NPC_TALK", elements={"NPC": mynpc, })
        else:
            mysurvivor = self.register_element("SURVIVOR", gears.selector.generate_ace(self.rank, self.elements.get(
                "ALLIED_FACTION"), myscene.environment))
            mynpc = mysurvivor.get_pilot()
            self.register_element("PILOT", mynpc, lock=True)
            team3.contents.append(mysurvivor)
            self.add_sub_plot(nart, "MT_NDDEV", ident="NPC_TALK", elements={"NPC": mynpc, })

        self.obj = adventureseed.MissionObjective("Rescue {}".format(self.elements["PILOT"]),
                                                  MAIN_OBJECTIVE_VALUE, can_reset=False)
        self.adv.objectives.append(self.obj)
        self.intro_ready = True
        self.eteam_activated = False
        self.eteam_defeated = False
        self.pilot_fled = False

        return True

    def PILOT_offers(self, camp):
        mylist = list()
        mylist.append(Offer(self.subplots["NPC_TALK"].START_COMBAT_MESSAGE,
                            context=ContextTag([context.HELLO, ]), ))
        if not camp.fight:
            mylist.append(
                Offer("[THANK_YOU] I need to get back to base.",
                      context=ContextTag([context.CUSTOM, ]), data={"reply": "Get out of here, I can handle this."},
                      effect=self.pilot_leaves_before_combat, dead_end=True)
            )

        return mylist

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            self.eteam_activated = True
            if not self.pilot_fled:
                npc = self.elements["PILOT"]
                camp.check_trigger("START", npc)
                camp.fight.active.append(self.elements["SURVIVOR"])
            self.intro_ready = False

    def pilot_leaves_before_combat(self, camp):
        self.obj.win(camp, 105)
        self.pilot_leaves_combat(camp)

    def pilot_leaves_combat(self, camp: gears.GearHeadCampaign):
        if not self.pilot_fled:
            npc = self.elements["PILOT"]
            if not npc.relationship:
                npc.relationship = camp.get_relationship(npc)
            npc.relationship.reaction_mod += 10
        camp.scene.contents.remove(self.elements["SURVIVOR"])
        self.pilot_fled = True

    def t_ENDCOMBAT(self, camp):
        if self.eteam_activated and not self.pilot_fled:
            myteam = self.elements["_ateam"]
            eteam = self.elements["_eteam"]
            npc = self.elements["PILOT"]
            if len(myteam.get_members_in_play(camp)) < 1:
                self.obj.failed = True
                camp.check_trigger("LOSE", npc)
            elif len(myteam.get_members_in_play(camp)) > 0 and len(eteam.get_members_in_play(camp)) < 1:
                self.eteam_defeated = True
                self.obj.win(camp, 100 - self.elements["SURVIVOR"].get_percent_damage_over_health())
                camp.check_trigger("WIN", npc)
                self.pilot_leaves_combat(camp)


class BAM_RespondToDistressCall(Plot):
    LABEL = BAMO_RESPOND_TO_DISTRESS_CALL
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(10, 10), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank, 120, self.elements.get("ENEMY_FACTION"), myscene.environment,
                                                add_commander=False)
        team2.contents += myunit.mecha_list

        team3 = self.register_element("_cargoteam", teams.Team(), dident="ROOM")
        team3.contents += game.content.plotutility.CargoContainer.generate_cargo_fleet(self.rank)
        # Oh yeah, when using PyCharm, why not use ludicrously long variable names?
        self.starting_number_of_containers = len(team3.contents)

        self.obj = adventureseed.MissionObjective("Respond to convoy distress call", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)
        self.combat_entered = False
        self.combat_finished = False

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if not self.combat_entered:
            self.combat_entered = True

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        cargoteam = self.elements["_cargoteam"]
        if len(cargoteam.get_members_in_play(camp)) < 1:
            self.obj.failed = True
        elif len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, (sum([(100 - c.get_percent_damage_over_health()) for c in
                                     cargoteam.get_members_in_play(camp)])) // self.starting_number_of_containers)
            if not self.combat_finished:
                pbge.alert("The missing cargo has been secured.")
                self.combat_finished = True


class BAM_ExtractTrucker(Plot):
    LABEL = BAMO_RESPOND_TO_DISTRESS_CALL
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(10, 10), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team3 = self.register_element("_ateam", teams.Team(enemies=(team2,), allies=(myscene.player_team,)),
                                      dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank, 200, self.elements.get("ENEMY_FACTION"), myscene.environment,
                                                add_commander=False)
        team2.contents += myunit.mecha_list

        mynpc = self.seek_element(nart, "PILOT", self._npc_is_good, must_find=True, lock=True)
        plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team3)
        mek = mynpc.get_root()
        self.register_element("SURVIVOR", mek)
        self.add_sub_plot(nart, "MT_TEAMUP_DEVELOPMENT", ident="NPC_TALK", elements={"NPC": mynpc, })

        self.obj = adventureseed.MissionObjective("Respond to {}'s distress call".format(self.elements["PILOT"]),
                                                  MAIN_OBJECTIVE_VALUE, can_reset=False)
        self.adv.objectives.append(self.obj)
        self.intro_ready = True
        self.eteam_activated = False
        self.eteam_defeated = False
        self.pilot_fled = False

        return True

    def PILOT_offers(self, camp):
        mylist = list()
        mylist.append(Offer(self.subplots["NPC_TALK"].START_COMBAT_MESSAGE,
                            context=ContextTag([context.HELLO, ]), ))
        if not camp.fight:
            mylist.append(
                Offer("[THANK_YOU] I need to get back to base.",
                      context=ContextTag([context.CUSTOM, ]), data={"reply": "Get out of here, I can handle this."},
                      effect=self.pilot_leaves_before_combat, dead_end=True)
            )

        return mylist

    def _npc_is_good(self, nart, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.combatant and candidate.faction != \
            self.elements["ENEMY_FACTION"] and candidate not in nart.camp.party and candidate.job.name == "Trucker"

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            self.eteam_activated = True
            if not self.pilot_fled:
                npc = self.elements["PILOT"]
                camp.check_trigger("START", npc)
                camp.fight.active.append(self.elements["SURVIVOR"])
            self.intro_ready = False

    def pilot_leaves_before_combat(self, camp):
        self.obj.win(camp, 105)
        self.pilot_leaves_combat(camp)

    def pilot_leaves_combat(self, camp):
        if not self.pilot_fled:
            npc = self.elements["PILOT"]
            npc.relationship.reaction_mod += 10
        camp.scene.contents.remove(self.elements["SURVIVOR"])
        self.pilot_fled = True

    def t_ENDCOMBAT(self, camp):
        if self.eteam_activated and not self.pilot_fled:
            myteam = self.elements["_ateam"]
            eteam = self.elements["_eteam"]
            npc = self.elements["PILOT"]
            if len(myteam.get_members_in_play(camp)) < 1:
                self.obj.failed = True
                camp.check_trigger("LOSE", npc)
            elif len(myteam.get_members_in_play(camp)) > 0 and len(eteam.get_members_in_play(camp)) < 1:
                self.eteam_defeated = True
                self.obj.win(camp, 100 - self.elements["SURVIVOR"].get_percent_damage_over_health())
                camp.check_trigger("WIN", npc)
                self.pilot_leaves_combat(camp)


class BAM_StormTheCastle(Plot):
    LABEL = BAMO_STORM_THE_CASTLE
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(10, 10), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        mynpc = self.seek_element(nart, "_commander", self.adv.is_good_enemy_npc, must_find=False, lock=True,
                                  backup_seek_func=self.adv.is_good_backup_enemy)
        if mynpc:
            plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
            myunit = gears.selector.RandomMechaUnit(self.rank, 120, myfac, myscene.environment, add_commander=False)
            myunit = gears.selector.RandomMechaUnit(self.rank, 120, myfac, myscene.environment, add_commander=False)
            self.add_sub_plot(nart, "MC_ENEMY_DEVELOPMENT", elements={"NPC": mynpc, CONVO_CANT_RETREAT: True})
        else:
            myunit = gears.selector.RandomMechaUnit(self.rank, 150, myfac, myscene.environment, add_commander=True)
            self.register_element("_commander", myunit.commander, lock=True)
            self.add_sub_plot(nart, "MC_NDBCONVERSATION", elements={"NPC": myunit.commander.get_pilot()})

        team2.contents += myunit.mecha_list
        self.starting_guards = len(team2.contents)

        myfort = self.register_element("_FORT",
                                       gears.selector.generate_fortification(self.rank, myfac, myscene.environment))
        team2.contents.append(myfort)

        self.obj1 = adventureseed.MissionObjective("Destroy {} command center".format(myfac), MAIN_OBJECTIVE_VALUE * 3)
        self.adv.objectives.append(self.obj1)

        self.obj2 = adventureseed.MissionObjective("Defeat command center guards", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj2)

        self.intro_ready = True

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]
        myboss = self.elements["_FORT"]
        myguards = [npc for npc in myteam.get_members_in_play(camp) if npc is not myboss]

        if len(myguards) < self.starting_guards:
            self.obj2.win(camp, 100 * (self.starting_guards - len(myguards)) // self.starting_guards)
        if not myboss.is_operational():
            self.obj1.win(camp, 100)


class BAM_ChampionStormTheCastle(Championify, BAM_StormTheCastle):
    active = True


class BAM_SurviveTheAmbush(Plot):
    LABEL = BAMO_SURVIVE_THE_AMBUSH
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ENTRANCE_ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank, 100, myfac, myscene.environment, add_commander=False)
        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Survive the ambush".format(myfac), MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def t_START(self, camp):
        if self.intro_ready:
            myfac = self.elements.get("ENEMY_FACTION")
            if myfac:
                pbge.alert("Without warning, you are ambushed by {}!".format(myfac))
            else:
                pbge.alert("Without warning, you are ambushed by enemy mecha!")
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


#   ********************************
#   ***   PERSONAL  OBJECTIVES   ***
#   ********************************

class BAM_FindHerbs(Plot):
    LABEL = BAMOP_FIND_HERBS
    active = True
    scope = "LOCALE"

    HERB_DESC = (
        "You stand before a patch of herbs.",
        "These appear to be the herbs you're looking for.",
        "These plants don't look like much, but they are definitely the herbs you need.",
        "You have located the herbs that you need."
    )

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(5, 5), dident="LOCALE")

        myherbs = self.register_element("HERBS", ghwaypoints.Herbs(
            name="Herbs", plot_locked=True, anchor=pbge.randmaps.anchors.middle,
            desc=random.choice(self.HERB_DESC)
        ), dident="ROOM")

        self.obj = adventureseed.MissionObjective("Locate herbs", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        self.collected_herbs = False

        return True

    def HERBS_menu(self, camp, thingmenu):
        if not self.collected_herbs:
            thingmenu.add_item("Collect some herbs.", self._collect_herbs)

    def _collect_herbs(self, camp):
        pbge.alert("You collect the herbs that you need.")
        self.obj.win(camp, 100)
        self.collected_herbs = True


class BAM_Dungeonlike(Plot):
    # This is not really an objective; it's just a request to make the mission area dungeonlike.
    LABEL = BAMOP_DUNGEONLIKE
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene: gears.GearHeadScene = self.elements["LOCALE"]

        self.elements[DG_NAME] = self.adv.name
        self.elements[DG_ARCHITECTURE] = self.elements["ARCHITECTURE"]
        self.elements[DG_SCENE_TAGS] = myscene.attributes
        self.elements[DG_MONSTER_TAGS] = self.elements.get(BAMEP_MONSTER_TYPE, ("ANIMAL", "MUTANT", "ROBOT", "SYNTH"))
        self.elements[DG_TEMPORARY] = True
        self.elements[DG_PARENT_SCENE] = self.elements["METROSCENE"]
        self.elements[DG_EXPLO_MUSIC] = myscene.exploration_music
        self.elements[DG_COMBAT_MUSIC] = myscene.combat_music
        self.elements[DG_DECOR] = None

        for t in range(random.randint(3, 4)):
            self.add_sub_plot(nart, "MONSTER_ENCOUNTER", elements={"TYPE_TAGS": self.elements[DG_MONSTER_TAGS]})

        if random.randint(1, 3) == 2:
            self.add_sub_plot(nart, "DUNGEON_EXTRA", necessary=False)

        return True


class BAMP_ExterminateMonsters(Plot):
    LABEL = BAMOP_EXTERMINATE_MONSTERS
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(20, 20), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        myunit = gears.selector.RandomMonsterUnit(self.rank, random.randint(120, 150), myscene.environment,
                                                  self.elements.get(BAMEP_MONSTER_TYPE), myscene.scale)
        team2.contents += myunit.contents

        self.obj = adventureseed.MissionObjective("Exterminate the monsters", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        return True

    def t_ENDCOMBAT(self, camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp, 100)


class BAM_RepairMachine(Plot):
    LABEL = BAMOP_REPAIR_MACHINE
    active = True
    scope = "LOCALE"

    MACHINE_DESC = (
        "This machine is oozing black fluid. That can't possibly be good.",
        "This machine is completely shut down. It does not appear to be receiving power.",
        "Someone or something smashed this machine real good. It's going to take a lot of work to put it back together.",
        "This machine appears to be in perfect working order except for the flashing red light on top."
    )

    MACHINE_CLASSES = (
        ghwaypoints.OldTerminal, ghwaypoints.OldMainframe
    )

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(
            random.randint(5,10), random.randint(5,10), decorate=gharchitecture.DefiledFactoryDecor()
        ), dident="LOCALE")

        myteam = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")

        myclass = random.choice(self.MACHINE_CLASSES)
        mymachine = self.register_element("MACHINE", myclass(
            name="Machine", plot_locked=True, anchor=pbge.randmaps.anchors.middle,
            desc=random.choice(self.MACHINE_DESC)
        ), dident="ROOM")

        self.obj = adventureseed.MissionObjective("Locate and repair the broken machinery", MAIN_OBJECTIVE_VALUE*2)
        self.adv.objectives.append(self.obj)

        self.repaired_machine = False
        self.tries = random.randint(1,3)

        return True

    def MACHINE_menu(self, camp, thingmenu):
        if not self.repaired_machine and not camp.fight:
            thingmenu.add_item("Repair machine", self._repair_machine)

    def _repair_machine(self, camp: gears.GearHeadCampaign):
        if camp.do_skill_test(
            gears.stats.Craft, gears.stats.Repair, self.rank, difficulty=gears.stats.DIFFICULTY_HARD
        ):
            pbge.alert("You have repaired the machine.")
            self.elements["MACHINE"].desc = "The machine appears to be working normally now."
            self.repaired_machine = True
            self.obj.win(camp, 100)
            camp.dole_xp(100, gears.stats.Repair)
        elif self.tries < 1:
            pbge.alert("After several failed attempts, you have bodged this machine into a semblance of normal operation. Hopefully it will keep running long enough for you to get out of here.")
            self.elements["MACHINE"].desc = "The machine appears to be working now. Mostly. You hope."
            self.repaired_machine = True
            self.obj.win(camp, 65)
            camp.dole_xp(100, gears.stats.Repair)
        else:
            self.tries -= 1
            pbge.alert("You attempt to repair the machine. The noise you make attracts monsters!")
            myunit = gears.selector.RandomMonsterUnit(
                self.rank, random.randint(90, 120), camp.scene.environment,
                self.elements.get(BAMEP_MONSTER_TYPE, ("ROBOT", "FACTORY")), camp.scene.scale
            )
            mek1 = myunit.contents[0]
            team2 = self.elements.get("_eteam")
            camp.scene.deploy_team(myunit.contents, team2, self.elements["ROOM"].area)
            game.combat.enter_combat(camp, mek1)


class BAM_RescueVictim(Plot):
    LABEL = BAMOP_RESCUE_VICTIM
    active = True
    scope = "LOCALE"

    VICTIM_DESC = (
        "{} is exhausted and dehydrated but otherwise in good condition.",
        "{} is slightly injured but should make a complete recovery back in town.",
        "You arrived just in time; {} is severely injured and immobilized.",
        "At first you think you arrived too late, but soon realize that {} is still alive."
    )

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(5, 5), dident="LOCALE")

        name = self.elements.get(BAMEP_VICTIM_NAME, "") or gears.selector.GENERIC_NAMES.gen_word()
        myvictim = self.register_element("VICTIM", ghwaypoints.Victim(
            name=name, plot_locked=True, anchor=pbge.randmaps.anchors.middle,
            desc=random.choice(self.VICTIM_DESC).format(name)
        ), dident="ROOM")

        self.obj = adventureseed.MissionObjective("Locate and rescue {}".format(name), MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        self.rescued_npc = False

        return True

    def VICTIM_menu(self, camp, thingmenu):
        if not self.rescued_npc:
            thingmenu.add_item("Rescue {VICTIM}".format(**self.elements), self._rescue_victim)

    def _rescue_victim(self, camp: gears.GearHeadCampaign):
        pbge.alert("You have rescued {VICTIM}.".format(**self.elements))
        self.obj.win(camp, 100)
        camp.dole_xp(100, gears.stats.Medicine)
        self.rescued_npc = True
        self.elements["VICTIM"].remove_victim()


class BAM_TestMissionStub(Plot):
    LABEL = None
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        myroom = self.register_element("ROOM", roomtype(10, 10), dident="LOCALE")
        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team3 = self.register_element("_ateam", teams.Team(enemies=(team2,), allies=(myscene.player_team,)),
                                      dident="ROOM")
        # myunit = gears.selector.RandomMechaUnit(self.rank, 200, self.elements.get("ENEMY_FACTION"), myscene.environment,
        #                                        add_commander=False)
        # team2.contents += myunit.mecha_list

        mysurvivor = self.register_element("SURVIVOR", gears.selector.generate_ace(25, None, myscene.environment))
        mynpc = mysurvivor.get_pilot()
        self.register_element("PILOT", mynpc)
        team3.contents.append(mysurvivor)
        self.add_sub_plot(nart, "MT_NDDEV", ident="NPC_TALK", elements={"NPC": mynpc, })

        self.obj = adventureseed.MissionObjective("Rescue {}".format(self.elements["PILOT"]),
                                                  MAIN_OBJECTIVE_VALUE, can_reset=False)
        self.adv.objectives.append(self.obj)
        self.intro_ready = True
        self.eteam_activated = False
        self.eteam_defeated = False
        self.pilot_fled = False

        return True

    def PILOT_offers(self, camp):
        mylist = list()
        mylist.append(Offer(self.subplots["NPC_TALK"].START_COMBAT_MESSAGE,
                            context=ContextTag([context.HELLO, ]), ))
        if not camp.fight:
            mylist.append(
                Offer("[THANK_YOU] I need to get back to base.",
                      context=ContextTag([context.CUSTOM, ]), data={"reply": "Get out of here, I can handle this."},
                      effect=self.pilot_leaves_before_combat, dead_end=True)
            )

        return mylist

    def t_START(self, camp: gears.GearHeadCampaign):
        npc = self.elements["PILOT"]
        mek = self.elements["SURVIVOR"]
        camp.freeze(npc)
        # ghdialogue.start_conversation(camp, camp.pc, self.adv, cue=ghdialogue.ATTACK_STARTER)

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            self.eteam_activated = True
            if not self.pilot_fled:
                npc = self.elements["PILOT"]
                camp.check_trigger("START", npc)
                camp.fight.active.append(self.elements["SURVIVOR"])
            self.intro_ready = False

    def pilot_leaves_before_combat(self, camp):
        self.obj.win(camp, 105)
        self.pilot_leaves_combat(camp)

    def pilot_leaves_combat(self, camp: gears.GearHeadCampaign):
        if not self.pilot_fled:
            npc = self.elements["PILOT"]
            if not npc.relationship:
                npc.relationship = camp.get_relationship(npc)
            npc.relationship.reaction_mod += 10
        camp.scene.contents.remove(self.elements["SURVIVOR"])
        self.pilot_fled = True

    def t_ENDCOMBAT(self, camp):
        if self.eteam_activated and not self.pilot_fled:
            myteam = self.elements["_ateam"]
            eteam = self.elements["_eteam"]
            npc = self.elements["PILOT"]
            if len(myteam.get_members_in_play(camp)) < 1:
                self.obj.failed = True
                camp.check_trigger("LOSE", npc)
            elif len(myteam.get_members_in_play(camp)) > 0 and len(eteam.get_members_in_play(camp)) < 1:
                self.eteam_defeated = True
                self.obj.win(camp, 100 - self.elements["SURVIVOR"].get_percent_damage_over_health())
                camp.check_trigger("WIN", npc)
                self.pilot_leaves_combat(camp)
