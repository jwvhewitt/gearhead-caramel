from pbge.plots import Plot, PlotState
import game.content.ghwaypoints
import game.content.ghterrain
import gears
import pbge
from game import teams,ghdialogue
from game.content import gharchitecture
from game.ghdialogue import context
import random
from pbge.dialogue import ContextTag,Offer
from game.content import plotutility, GHNarrativeRequest, PLOT_LIST
import game.content.gharchitecture
from . import missionbuilder
import collections
from game.content.plotutility import LMSkillsSelfIntro

from game import memobrowser
Memo = memobrowser.Memo

# This unit contains plots that handle standard features you may want to add to a campaign or a scene in that campaign.

# Some constants for camp.campdata to let other plots know what features are present in this campaign.
LANCE_HANDLER_ENABLED = "LANCE_HANDLER_ENABLED" # If True, the standard lancemate handler is in effect.
LANCEDEV_ENABLED = "LANCEDEV_ENABLED"   # If this value exists, it will be a function with signature fun(camp)
                                        # that returns True if a lancemate development plot can be loaded now.
WORLD_MAP_ENCOUNTERS = "WORLD_MAP_ENCOUNTERS"   # If exists, this will be a function that returns a MissionSeed.
                                                # See below for the signature; always send named parameters.
                                                # May return None.


class StandardLancemateHandler(Plot):
    LABEL = "CF_STANDARD_LANCEMATE_HANDLER"
    active = True
    scope = True

    def custom_init( self, nart ):
        nart.camp.campdata[LANCE_HANDLER_ENABLED] = True
        nart.camp.campdata[LANCEDEV_ENABLED] = self.can_load_lancedev_plot
        return True

    def can_load_lancedev_plot(self, camp):
        return not any(p for p in camp.all_plots() if hasattr(p, "LANCEDEV_PLOT") and p.LANCEDEV_PLOT)

    def _get_generic_offers( self, npc: gears.base.Character, camp: gears.GearHeadCampaign ):
        """
        :type camp: gears.GearHeadCampaign
        :type npc: gears.base.Character
        """
        mylist = list()
        if npc.relationship and gears.relationships.RT_LANCEMATE in npc.relationship.tags:
            if camp.can_add_lancemate() and npc not in camp.party:
                # If the NPC has the lancemate tag, they might join the party.
                if npc.get_reaction_score(camp.pc, camp) < -20:
                    # A lancemate who is currently upset with the PC will not join the party.
                    mylist.append(Offer("[JOIN_REFUSAL]", is_generic=True,
                                        context=ContextTag([context.JOIN])))
                elif npc.relationship.data.get("LANCEMATE_TIME_OFF",0) <= camp.day:
                    mylist.append(Offer("[JOIN]", is_generic=True,
                                        context=ContextTag([context.JOIN]), effect=game.content.plotutility.AutoJoiner(npc)))
                else:
                    # This NPC is taking some time off. Come back tomorrow.
                    mylist.append(Offer("[COMEBACKTOMORROW_JOIN]", is_generic=True,
                                        context=ContextTag([context.JOIN])))
            elif npc in camp.party and gears.tags.SCENE_PUBLIC in camp.scene.attributes:
                mylist.append(Offer("[LEAVEPARTY]", is_generic=True,
                                    context=ContextTag([context.LEAVEPARTY]), effect=game.content.plotutility.AutoLeaver(npc)))
            mylist.append(LMSkillsSelfIntro(npc))
        return mylist


class MetrosceneRecoveryHandler(Plot):
    LABEL = "CF_METROSCENE_RECOVERY_HANDLER"
    active = True
    scope = "METROSCENE"
    def METROSCENE_ENTER(self, camp: gears.GearHeadCampaign):
        # Upon entering this scene, deal with any dead or incapacitated party members.
        # Also, deal with party members who have lost their mecha. This may include the PC.
        if not camp.is_unfavorable_to_pc(self.elements["METROSCENE"]):
            camp.home_base = self.elements["MISSION_GATE"]
            etlr = plotutility.EnterTownLanceRecovery(camp, self.elements["METROSCENE"], self.elements["METRO"])

            if camp.campdata.get(LANCE_HANDLER_ENABLED, False) and not etlr.did_recovery:
                pass

            if camp.campdata.get(LANCEDEV_ENABLED, False) and random.randint(1, 3) == 2 and not etlr.did_recovery:
                # We can maybe load a lancemate scene here. Yay!
                if camp.campdata[LANCEDEV_ENABLED](camp):
                    nart = GHNarrativeRequest(camp, pbge.plots.PlotState().based_on(self), adv_type="DZD_LANCEDEV", plot_list=PLOT_LIST)
                    if nart.story:
                        nart.build()


class WorldMapEncounterHandler(Plot):
    LABEL = "CF_WORLD_MAP_ENCOUNTER_HANDLER"
    active = True
    scope = True

    def custom_init( self, nart ):
        nart.camp.campdata[WORLD_MAP_ENCOUNTERS] = self.choose_world_map_encounter
        return True

    def choose_world_map_encounter(
            self, camp: gears.GearHeadCampaign, metroscene, return_wp, encounter_chance=25, dest_scene=None,
            dest_wp=None,
            rank=None, scenegen=pbge.randmaps.SceneGenerator, architecture=gharchitecture.MechaScaleDeadzone,
            environment=gears.tags.GroundEnv, **kwargs
    ):
        candidate_seeds = list()
        # Step one: harvest any world map encounters that may exist within this adventure already.
        for p in camp.active_plots():
            if p is not self and hasattr(p, "generate_world_map_encounter"):
                myseed = p.generate_world_map_encounter(camp, metroscene, return_wp, dest_scene=dest_scene, dest_wp=dest_wp,
                                                        rank=rank, scenegen=scenegen, architecture=architecture,
                                                        environment=environment, **kwargs)

                if myseed:
                    if hasattr(myseed, "priority"):
                        candidate_seeds += [myseed,] * myseed.priority
                    else:
                        candidate_seeds.append(myseed)

                    if hasattr(myseed, "mandatory") and myseed.mandatory:
                        encounter_chance = 100

        # Step two: Attempt to load a generic world map encounter plot.
        for t in range(random.randint(2,6)):
            myplotstate = PlotState(
                rank=rank, elements={"METROSCENE": metroscene, "DEST_SCENE": dest_scene, "KWARGS": kwargs.copy()}
            )
            myplot = game.content.load_dynamic_plot(camp, "RWMENCOUNTER", myplotstate)
            if myplot:
                myseed = myplot.generate_world_map_encounter(
                    camp, metroscene, return_wp, dest_scene=dest_scene, dest_wp=dest_wp,
                    rank=rank, scenegen=scenegen, architecture=architecture,
                    environment=environment, **kwargs
                )
                if myseed:
                    if hasattr(myseed, "priority"):
                        candidate_seeds += [myseed,] * myseed.priority
                    else:
                        candidate_seeds.append(myseed)

                    if hasattr(myseed, "mandatory") and myseed.mandatory:
                        encounter_chance = 100


        if candidate_seeds and random.randint(1,100) <= encounter_chance:
            return random.choice(candidate_seeds)


class MetrosceneWMEDefenseHandler(Plot):
    # This plot works with the above plot
    LABEL = "CF_METROSCENE_WME_DEFENSE_HANDLER"
    active = True
    scope = True
    def generate_world_map_encounter(self, camp: gears.GearHeadCampaign, metroscene, return_wp,
                                     dest_scene: gears.GearHeadScene, dest_wp,
                                     scenegen=gharchitecture.DeadZoneHighwaySceneGen,
                                     architecture=gharchitecture.MechaScaleSemiDeadzone,
                                     environment=gears.tags.GroundEnv, **kwargs):
        if camp.is_unfavorable_to_pc(dest_scene):
            myanchor = kwargs.get("entrance_anchor", None)
            if not myanchor:
                myanchor = pbge.randmaps.anchors.east
            myrank = self.rank
            dest_metro = dest_scene.get_metro_scene()
            if dest_metro and dest_metro.metrodat:
                myqol = dest_metro.metrodat.get_quality_of_life()
                myrank += myqol.defense * 10
            myadv = missionbuilder.BuildAMissionSeed(
                camp, "{} Militia".format(dest_scene), metroscene, return_wp,
                enemy_faction = dest_scene.faction, rank=myrank,
                objectives = (missionbuilder.BAMO_DEFEAT_COMMANDER,),
                adv_type = "BAM_ROAD_MISSION",
                custom_elements={"ADVENTURE_GOAL": dest_wp, "ENTRANCE_ANCHOR": myanchor},
                scenegen=scenegen,
                architecture=architecture(room_classes=(pbge.randmaps.rooms.FuzzyRoom,)),
                environment=environment,
                cash_reward=0,
                mission_grammar=missionbuilder.MissionGrammar(
                    objective_ep="keep you out of {}".format(dest_scene),
                    win_pp="I got past your militia",
                    win_ep="you fought your way into {}".format(dest_scene),
                    lose_pp="you stopped me from entering {}".format(dest_scene),
                    lose_ep="I drove you out of {}".format(dest_scene)
                )
            )
            myadv.priority = 50
            myadv.mandatory = True
            return myadv


class MetrosceneRandomPlotHandler(Plot):
    # Keep this metro area stocked with random plots.Deadzone
    LABEL = "CF_METROSCENE_RANDOM_PLOT_HANDLER"
    active = True
    scope = "METRO"

    MAX_PLOTS = 5
    SUBPLOT_LABEL = "RANDOM_PLOT"

    def custom_init( self, nart ):
        self.adv = pbge.plots.Adventure(name="Plot Handler")
        return True

    def t_START(self, camp):
        while self.should_load_plot(camp):
            myplot = game.content.load_dynamic_plot(
                camp, self.SUBPLOT_LABEL, pstate=PlotState(
                    rank=self.calc_rank(camp)
                ).based_on(self)
            )
            if not myplot:
                print("Warning: No plot found for {}".format(self.SUBPLOT_LABEL))
                break

    def should_load_plot(self, camp):
        mymetro: gears.MetroData = self.elements["METRO"]
        return len([p for p in mymetro.scripts if p.LABEL == self.SUBPLOT_LABEL]) < self.MAX_PLOTS

    def calc_rank(self, camp: gears.GearHeadCampaign):
        return camp.renown

