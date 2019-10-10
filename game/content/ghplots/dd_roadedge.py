from pbge.plots import Plot,PlotState
import game
import gears
import pbge
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints,plotutility, adventureseed
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from dd_main import RoadEdge
import missionbuilder
import pygame
import collections


#   ***************************************************
#   ***   DZD_ROAD_MISSION  and  SUPPORT  CLASSES   ***
#   ***************************************************

class DeadZoneHighwaySceneGen( pbge.randmaps.SceneGenerator ):
    DO_DIRECT_CONNECTIONS = True
    def build( self, gb, archi ):
        self.fill(gb,pygame.Rect(0,gb.height//2-2,gb.width,5),wall=None)

    def DECORATE( self, gb, scenegen ):
        """
        :type gb: gears.GearHeadScene
        """
        # Draw a gret big highway going from west to east.
        self.fill(gb,pygame.Rect(0,gb.height//2-2,gb.width,5),floor=self.archi.DEFAULT_FLOOR_TERRAIN)
        self.fill(gb,pygame.Rect(0,gb.height//2-1,gb.width,3),floor=ghterrain.Pavement)



class RoadMissionPlot( missionbuilder.BuildAMissionPlot ):
    # based on the regular Build-a-Mission plot, but automatically exits when the mission is complete.
    # Custom element: ADVENTURE_GOAL, the scene and waypoint of the destination node.
    LABEL = "DZD_ROAD_MISSION"

    def t_ENDCOMBAT(self,camp):
        # If the player team gets wiped out, end the mission.
        if not camp.first_active_pc():
            self.exit_the_mission(camp)
        elif self.adv.is_completed():
            self.exit_the_mission(camp)

    def _ENTRANCE_menu(self, camp, thingmenu):
        thingmenu.desc = "Do you want to end this journey and return to {}?".format(self.elements["ADVENTURE_RETURN"][0])

        thingmenu.add_item("Return to {}".format(self.elements["ADVENTURE_RETURN"][0]),self.exit_the_mission)
        thingmenu.add_item("Journey Onward", None)

    def exit_the_mission(self,camp):
        if self.adv.is_won():
            camp.destination, camp.entrance = self.elements["ADVENTURE_GOAL"]
        else:
            camp.destination, camp.entrance = self.elements["ADVENTURE_RETURN"]
        if self.elements["ONE_CHANCE"] or self.adv.is_completed():
            self.adv.end_adventure(camp)


#   *****************************************
#   ***   ROAD  EDGE  PLOT  DESCRIPTORS   ***
#   *****************************************
#
# For the basic "road is dangerous because of giant robots raiding convoys" plots, I'm going to use the random
# story technique I call Propp's Ratchet to generate the missions leading up to the boss fight.

E_MOTIVE = "DZREPR_MOTIVE"
DZRE_MOTIVE_UNKNOWN = "DZRE_EGOAL_UNKNOWN"
DZRE_MOTIVE_PROFIT = "DZRE_MOTIVE_PROFIT"
DZRE_MOTIVE_CONQUEST = "DZRE_MOTIVE_CONQUEST"

E_ACE = "DZREPR_ACE"
DZRE_ACE_UNKNOWN = "DZRE_ACE_UNKNOWN"
DZRE_ACE_HIDDENBASE = "DZRE_ACE_HIDDENBASE"
DZRE_ACE_ZEUSCANNON = "DZRE_ACE_ZEUSCANNON"

E_TOWN = "DZREPR_TOWN"
DZRE_TOWN_NEUTRAL = "DZRE_TOWN_NEUTRAL"
DZRE_TOWN_AGAINST = "DZRE_TOWN_AGAINST"
DZRE_TOWN_AFRAID = "DZRE_TOWN_AFRAID"

E_MISSION_NUMBER = "DZREPR_MISSION_NUMBER"

class DZREPR_BasePlot(Plot):
    # Subclass this plot for the specific starting scenarios. This plot performs the following functions:
    # - After start_missions is set to True, start generating investigation missions.
    # - Update plot state and load new investigation missions after each mission finished
    # - Load the conclusion mission when appropriate
    # - Send a WIN trigger when the conclusion mission is won
    # Required Elements: METRO, LOCALE, MISSION_GATE
    active = True
    scope = "METRO"
    STARTING_MOTIVE = DZRE_MOTIVE_UNKNOWN
    STARTING_ACE = DZRE_ACE_UNKNOWN
    STARTING_TOWN = DZRE_TOWN_NEUTRAL

    MISSION_LABELS = ["DZRE_MOTIVE_ACE","DZRE_ACE_TOWN", "DZRE_MOTIVE_TOWN"]
    MISSION_IDENTS = ("ALPHA_MISSION","BETA_MISSION")

    NUMBER_OF_MISSIONS_BEFORE_CONCLUSION = 3

    def custom_init(self, nart):
        self.register_element(E_MOTIVE,self.STARTING_MOTIVE)
        self.register_element(E_ACE,self.STARTING_ACE)
        self.register_element(E_TOWN,self.STARTING_TOWN)
        self.register_element(E_MISSION_NUMBER, 0)
        self.start_missions = False

        return True

    def t_UPDATE(self,camp):
        if self.start_missions:
            if self.MISSION_IDENTS[0] not in self.subplots or not self.subplots[self.MISSION_IDENTS[0]]:
                self.load_missions(camp)

    def load_missions(self,camp):
        if self.elements[E_MISSION_NUMBER] >= self.NUMBER_OF_MISSIONS_BEFORE_CONCLUSION:
            print "Load the conclusion now!"
        else:
            self.elements[E_MISSION_NUMBER] += 1
            random.shuffle(self.MISSION_LABELS)
            num_miss = 0
            miss_num = 0
            while num_miss < 2 and miss_num < len(self.MISSION_LABELS):
                init = pbge.plots.PlotState().based_on(self)
                nart = game.content.GHNarrativeRequest(camp, init, self.MISSION_LABELS[miss_num], game.content.PLOT_LIST)
                if nart.story:
                    nart.build()
                    self.subplots[self.MISSION_IDENTS[num_miss]] = nart.story
                    num_miss += 1
                miss_num += 1
            if num_miss < 1:
                # Drat- we have apparently hit a deadend.
                print "DeadEnd Error!!!"

    def reset_missions(self,camp):
        for mid in self.MISSION_IDENTS:
            if mid in self.subplots and self.subplots[mid]:
                self.subplots[mid].end_plot(camp,True)
                del self.subplots[mid]

    def ALPHA_MISSION_WIN(self,camp):
        self.subplots["ALPHA_MISSION"].alter_the_context(self)
        self.reset_missions(camp)

    def BETA_MISSION_WIN(self,camp):
        self.subplots["BETA_MISSION"].alter_the_context(self)
        self.reset_missions(camp)

    def FINAL_MISSION_WIN(self,camp):
        camp.check_trigger("WIN",self)
        self.end_plot(camp)

class DZREPR_BaseMission(Plot):
    # Will activate the adventure when property mission_active set to True
    # Required Elements: METRO, LOCALE, MISSION_GATE
    LABEL = "DZRE_MOTIVE_ACE_TOWN"
    active = True
    scope = "METRO"
    REQUIRES = {E_MOTIVE: None, E_ACE: None, E_TOWN: None}
    CHANGES = {E_MOTIVE: None, E_ACE: None, E_TOWN: None}
    MISSION_NAME = "Go do mission"
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_THE_BANDITS,)

    @classmethod
    def matches(cls, pstate):
        """Returns True if this plot matches the current plot state."""
        return all(pstate.elements.get(k,0) == cls.REQUIRES[k] for k in cls.REQUIRES.iterkeys())

    def custom_init(self, nart):
        self.mission_seed = None
        self.mission_active = False
        return True

    def build_mission(self,camp):
        myadv = missionbuilder.BuildAMissionSeed(
            camp, self.MISSION_NAME, (self.elements["LOCALE"],self.elements["MISSION_GATE"]),
            enemy_faction = self.elements["FACTION"], rank=self.rank,
            objectives = self.OBJECTIVES, one_chance=False,
            architecture=gharchitecture.MechaScaleDeadzone,
        )

    def t_UPDATE(self,camp):
        if not self.mission_seed:
            self.build_mission(camp)
        elif self.mission_seed.ended:
            camp.check_trigger("WIN",self)

    def alter_the_context(self,other_plot):
        for k,v in self.CHANGES.items():
            other_plot.elements[k] = v

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed:
            thingmenu.add_item(self.mission_seed.name, self.mission_seed)

#   *****************************************
#   ***   ROAD  EDGE  RATCHET  MISSIONS   ***
#   *****************************************
#
# The missions leading up to the boss fight against the bandits or whoever.


#   ***************************************
#   ***   ROAD  EDGE  RATCHET  SETUPS   ***
#   ***************************************
#
# The base plot that launches the initial missions and eventually sends a win signal to the roadedge plot.
# Mostly, what this plot has to do is provide backstory and set the start_mission property to True.

class DZREPR_NewBanditsWhoThis(DZREPR_BasePlot):
    LABEL = "DZRE_BanditProblem"

    def custom_init(self, nart):
        super(DZREPR_NewBanditsWhoThis,self).custom_init(nart)

        # Add a trucker to town.
        myscene = self.elements["LOCALE"]
        destscene = self.seek_element(nart,"_DEST",self._is_best_scene,scope=myscene,must_find=False)
        if not destscene:
            destscene = self.seek_element(nart,"_DEST",self._is_good_scene,scope=myscene)

        mynpc = self.register_element(
            "NPC", gears.selector.random_character(
                job=gears.jobs.ALL_JOBS["Trucker"], rank=random.randint(self.rank-10,self.rank+10),
                local_tags=(gears.personality.GreenZone,), combatant=True,
            ), dident="_DEST"
        )
        destscene.local_teams[mynpc] = destscene.civilian_team

        self.got_rumor = False

        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and gears.tags.SCENE_GARAGE in candidate.attributes

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if camp.scene.get_root_scene() is self.elements["LOCALE"] and npc is not self.elements["NPC"] and not self.got_rumor:
            mygram["[News]"].append("the trucker {} lost {} convoy on the way into town.".format(self.elements["NPC"],self.elements["NPC"].gender.possessive_determiner))
        if camp.scene.get_root_scene() is self.elements["LOCALE"] and not self.start_missions:
            mygram["[News]"].append("there never used to be bandits between here and {} in the past".format(self.elements["DZ_EDGE"].get_city_link(self.elements["LOCALE"])))
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.got_rumor and camp.scene.get_root_scene() is self.elements["LOCALE"] and npc is not self.elements["NPC"]:
            mynpc = self.elements["NPC"]
            goffs.append(Offer(
                msg="I think you should speak to {} directly about all this; you can probably find {} at {}.".format(mynpc,mynpc.gender.object_pronoun,self.elements["_DEST"]),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))
        if not self.start_missions and camp.scene.get_root_scene() is self.elements["LOCALE"]:
            goffs.append(Offer(
                msg="[as_far_as_I_know] they call themselves {}. Hopefully they will leave this place as quickly as they arrived.".format(self.elements["FACTION"]),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject="bandits", data={"subject": "the bandits"}, no_repeats=True
            ))

        return goffs

    def _get_rumor(self,camp):
        self.got_rumor = True
        mynpc = self.elements["NPC"]
        self.memo = "{} is a trucker who lost {} convoy; {} can be found at {}.".format(mynpc,mynpc.gender.possessive_determiner,mynpc.gender.subject_pronoun,self.elements["_DEST"])


#   *******************************
#   ***   DZD_ROADEDGE_YELLOW   ***
#   *******************************
#
# Yellow road edges have a difficulty rank of around 20.

class BanditsPalooza(Plot):
    LABEL = "DZD_ROADEDGE_YELLOW"

    active = True
    scope = True

    def custom_init(self, nart):
        self.rank = 15 + random.randint(1,6) - random.randint(1,6)
        self.register_element("DZ_EDGE_STYLE",RoadEdge.STYLE_YELLOW)
        self.register_element("FACTION",plotutility.RandomBanditCircle())

        myedge = self.elements["DZ_EDGE"]
        self.add_sub_plot(nart,"DZRE_BanditProblem",ident="MISSION",spstate=PlotState(elements={"METRO":myedge.start_node.destination.metrodat,"LOCALE":myedge.start_node.destination,"MISSION_GATE":myedge.start_node.entrance}).based_on(self))

        return True

    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        myscene = camp.scene.get_root_scene()
        if self.elements["DZ_EDGE"].connects_to_city(myscene):
            # This city is on this road.
            mygram["[News]"] = ["you should beware {} when traveling to {}".format(str(self.elements["FACTION"]),self.elements["DZ_EDGE"].get_city_link(myscene)), ]
        return mygram

    def get_bandit_adventure(self, camp, dest_node):
        start_node = self.elements["DZ_EDGE"].get_link(dest_node)
        if start_node.pos[0] < dest_node.pos[0]:
            myanchor = pbge.randmaps.anchors.west
        else:
            myanchor = pbge.randmaps.anchors.east
        myadv = missionbuilder.BuildAMissionSeed(
            camp, "Bandit Ambush!", (start_node.destination,start_node.entrance),
            enemy_faction = self.elements["FACTION"], rank=self.rank,
            objectives = (missionbuilder.BAMO_DEFEAT_THE_BANDITS,),
            adv_type = "DZD_ROAD_MISSION",
            custom_elements={"ADVENTURE_GOAL": (dest_node.destination,dest_node.entrance),"ENTRANCE_ANCHOR": myanchor},
            scenegen=DeadZoneHighwaySceneGen, architecture=gharchitecture.MechaScaleSemiDeadzone,
            cash_reward=0,
        )
        return myadv

    def get_road_adventure(self, camp, dest_node):
        # Return an adventure if there's going to be an adventure. Otherwise return nothing.
        if self.active and random.randint(1,100) <= 45:
            return self.get_bandit_adventure(camp,dest_node)

