import game.content.plotutility
from pbge.plots import Plot,PlotState
import game
import gears
import pbge
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints,plotutility, adventureseed
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from .dd_main import RoadEdge
from . import missionbuilder
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
    CONCLUSION_IDENT = "FINAL_MISSION"
    CONCLUSION_LABEL = "DZRE_CONCLUSION"

    NUMBER_OF_MISSIONS_BEFORE_CONCLUSION = 3

    def custom_init(self, nart):
        self.register_element(E_MOTIVE,self.STARTING_MOTIVE)
        self.register_element(E_ACE,self.STARTING_ACE)
        self.register_element(E_TOWN,self.STARTING_TOWN)
        self.register_element(E_MISSION_NUMBER, 0)
        self.start_missions = False
        self.final_loaded = False

        return True

    def t_UPDATE(self,camp):
        if self.start_missions:
            if (self.MISSION_IDENTS[0] not in self.subplots or not self.subplots[self.MISSION_IDENTS[0]]) and not self.final_loaded:
                self.load_missions(camp)

    def load_missions(self,camp):
        if self.elements[E_MISSION_NUMBER] >= self.NUMBER_OF_MISSIONS_BEFORE_CONCLUSION:
            init = pbge.plots.PlotState(rank=self.rank + self.elements[E_MISSION_NUMBER] * 3 + 5).based_on(self)
            nart = game.content.GHNarrativeRequest(camp, init, self.CONCLUSION_LABEL, game.content.PLOT_LIST)
            if nart.story:
                nart.build()
                self.subplots[self.CONCLUSION_IDENT] = nart.story
            self.final_loaded = True
        else:
            self.elements[E_MISSION_NUMBER] += 1
            random.shuffle(self.MISSION_LABELS)
            num_miss = 0
            miss_num = 0
            while num_miss < 2 and miss_num < len(self.MISSION_LABELS):
                init = pbge.plots.PlotState(rank=self.rank + self.elements[E_MISSION_NUMBER]*3).based_on(self)
                nart = game.content.GHNarrativeRequest(camp, init, self.MISSION_LABELS[miss_num], game.content.PLOT_LIST)
                if nart.story:
                    nart.build()
                    self.subplots[self.MISSION_IDENTS[num_miss]] = nart.story
                    num_miss += 1
                miss_num += 1
            if num_miss < 1:
                # Drat- we have apparently hit a deadend.
                print("DeadEnd Error!!!")

    def reset_missions(self,camp):
        old_plots = list()
        for mid in self.MISSION_IDENTS:
            if mid in self.subplots and self.subplots[mid]:
                old_plots.append(self.subplots[mid])
                del self.subplots[mid]
        for m in old_plots:
            m.end_plot(camp,True)

    def ALPHA_MISSION_WIN(self,camp):
        self.subplots["ALPHA_MISSION"].alter_the_context(self)
        self.reset_missions(camp)

    def BETA_MISSION_WIN(self,camp):
        self.subplots["BETA_MISSION"].alter_the_context(self)
        self.reset_missions(camp)

    def FINAL_MISSION_WIN(self,camp):
        camp.check_trigger("WIN",self)
        self.elements["METRO"].local_reputation = max(self.elements["METRO"].local_reputation+10,0)
        self.end_plot(camp)

    def FINAL_MISSION_LOSE(self,camp):
        self.elements["METRO"].local_reputation -= 5
        self.final_loaded = False


class DZREPR_BaseMission(Plot):
    # Will activate the adventure when property mission_active set to True
    # Required Elements: METRO, LOCALE, MISSION_GATE, FACTION
    LABEL = "DZRE_MOTIVE_ACE_TOWN"
    active = True
    scope = "METRO"
    REQUIRES = {E_MOTIVE: None, E_ACE: None, E_TOWN: None}
    CHANGES = {E_MOTIVE: None, E_ACE: None, E_TOWN: None}
    MISSION_NAME = "The Mission"
    MISSION_PROMPT = "Go do mission"
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_THE_BANDITS,)
    WIN_MESSAGE = ""

    @classmethod
    def matches(cls, pstate):
        """Returns True if this plot matches the current plot state."""
        return all(pstate.elements.get(k,0) == cls.REQUIRES[k] for k in cls.REQUIRES.keys()) or cls.LABEL == "DZRE_TEST"

    def custom_init(self, nart):
        self.mission_seed = None
        self.mission_active = False
        return True

    def build_mission(self,camp):
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, self.MISSION_NAME, (self.elements["LOCALE"],self.elements["MISSION_GATE"]),
            enemy_faction = self.elements["FACTION"], rank=self.rank,
            objectives = self.OBJECTIVES, one_chance=False,
            architecture=gharchitecture.MechaScaleDeadzone,
            win_message=self.WIN_MESSAGE.format(**self.elements)
        )

    def t_UPDATE(self,camp):
        if not self.mission_seed:
            self.build_mission(camp)
        elif self.mission_seed.ended:
            camp.check_trigger("WIN",self)

    def alter_the_context(self,other_plot):
        for k,v in list(self.CHANGES.items()):
            other_plot.elements[k] = v

    def activate_mission(self,camp):
        self.mission_active = True
        missionbuilder.NewMissionNotification(self.MISSION_NAME,self.elements["MISSION_GATE"])
        camp.check_trigger("UPDATE")

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed and self.mission_active:
            thingmenu.add_item(self.MISSION_PROMPT.format(**self.elements), self.mission_seed)


class DZREPR_NPCMission(DZREPR_BaseMission):
    # As above, but includes a specific NPC who gives the PC the mission.
    DEFAULT_NEWS = "{NPC} knows something about {FACTION}"
    DEFAULT_INFO = "You can ask {NPC.gender.object_pronoun} about {FACTION} yourself; speak to {NPC.gender.object_pronoun} at {NPC_SCENE}."
    DEFAULT_MEMO = "You can ask {NPC} about {FACTION} at {NPC_SCENE}."
    CUSTOM_REPLY = "What do you know about {FACTION}?"
    CUSTOM_OFFER = "I can tell you that you can go do a mission in {LOCALE} so go do it."
    def custom_init(self, nart):
        super(DZREPR_NPCMission,self).custom_init(nart)
        mynpc = self.seek_element(nart, "NPC", self._npc_matches, scope=self.elements["LOCALE"])
        npcscene = self.register_element("NPC_SCENE",mynpc.container.owner)
        self.got_rumor = False
        return True
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character)
    def t_UPDATE(self,camp):
        if not self.elements["NPC"].is_not_destroyed():
            self.activate_mission(camp)
        super(DZREPR_NPCMission,self).t_UPDATE(camp)
    def NPC_offers(self, camp):
        mylist = list()
        if not self.mission_active:
            mylist.append(Offer(self.CUSTOM_OFFER.format(**self.elements),
                            context=ContextTag((context.CUSTOM,)), effect=self.activate_mission,
                            data={"reply": self.CUSTOM_REPLY.format(**self.elements)},
                            no_repeats=True
                            ))
        return mylist
    def get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if npc is not self.elements["NPC"] and not self.got_rumor:
            mygram["[News]"].append(self.DEFAULT_NEWS.format(**self.elements))
        return mygram
    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        mynpc = self.elements["NPC"]
        if self.DEFAULT_INFO and not self.got_rumor and npc is not mynpc:
            goffs.append(Offer(
                msg=self.DEFAULT_INFO.format(**self.elements),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": str(mynpc)}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self,camp):
        self.got_rumor = True
        self.memo = self.DEFAULT_MEMO.format(**self.elements)


#   *****************************************
#   ***   ROAD  EDGE  RATCHET  MISSIONS   ***
#   *****************************************
#
# The missions leading up to the boss fight against the bandits or whoever.

class DZREPR_LookForTrouble(DZREPR_BaseMission):
    LABEL = "DZRE_MOTIVE_ACE"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_UNKNOWN, E_ACE: DZRE_ACE_UNKNOWN}
    CHANGES = {E_ACE: DZRE_ACE_HIDDENBASE}
    MISSION_NAME = "Looking for Trouble"
    MISSION_PROMPT = "Search the backroads for {FACTION}"
    OBJECTIVES = (missionbuilder.BAMO_SURVIVE_THE_AMBUSH,missionbuilder.BAMO_LOCATE_ENEMY_FORCES)
    WIN_MESSAGE = "After the battle, you find no tracks indicating where {FACTION} came from. It's clear that they know this area and their hideout must be well hidden."

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and npc.combatant and npc not in camp.party:
            goffs.append(Offer(
                msg="[GOODQUESTION] My best guess would be to check the backroads [direction] of town.",
                context=ContextTag((context.CUSTOM,)), effect=self.activate_mission,
                data={"reply": "Do you have any idea where {} have their base?".format(self.elements["FACTION"])}, no_repeats=True
            ))
        return goffs

    def get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not npc.combatant and not self.mission_active:
            mygram["[News]"].append("maybe a pilot would know how to find {}.".format(self.elements["FACTION"]))
        return mygram

class DZREPR_HighwayPatrol(DZREPR_BaseMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_UNKNOWN, E_TOWN: DZRE_TOWN_NEUTRAL}
    CHANGES = {E_MOTIVE: DZRE_MOTIVE_PROFIT}
    MISSION_NAME = "Highway Patrol"
    MISSION_PROMPT = "Patrol highway for {FACTION}"
    OBJECTIVES = (missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL,missionbuilder.BAMO_LOCATE_ENEMY_FORCES)
    WIN_MESSAGE = "You have confirmed that {FACTION} are targeting convoys along the highway."

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and gears.tags.Politician in npc.get_tags() and npc not in camp.party:
            goffs.append(Offer(
                msg="Since {} showed up, several convoys have gone missing between here and {}. If you patrol the highway you might be able to catch them in the act.".format(self.elements["FACTION"],self.elements["DZ_EDGE"].get_city_link(self.elements["LOCALE"])),
                context=ContextTag((context.CUSTOM,)), effect=self.activate_mission,
                data={"reply": "Do you know what {} want?".format(self.elements["FACTION"])}, no_repeats=True
            ))
        return goffs

    def get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if gears.tags.Politician not in npc.get_tags() and not self.mission_active:
            mygram["[News]"].append("the people in charge know more about {} than they're letting on.".format(self.elements["FACTION"]))
        return mygram

class DZREPR_NoBigDealMaybe(DZREPR_NPCMission):
    LABEL = "DZRE_ACE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_ACE: DZRE_ACE_UNKNOWN, E_TOWN: DZRE_TOWN_NEUTRAL}
    CHANGES = {E_TOWN: DZRE_TOWN_AGAINST}
    MISSION_NAME = "The Patrol Patrol"
    MISSION_PROMPT = "Investigate {NPC}'s missing patrol"
    OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES,missionbuilder.BAMO_EXTRACT_ALLIED_FORCES)
    WIN_MESSAGE = ""
    DEFAULT_NEWS = "{NPC} says that {FACTION} are nothing to be worried about"
    DEFAULT_INFO = "You can ask {NPC} about {FACTION} yourself; speak to {NPC.gender.object_pronoun} at {NPC_SCENE}."
    DEFAULT_MEMO = "{NPC} said that {FACTION} is nothing to worry about; you can ask {NPC.gender.object_pronoun} about this at {NPC_SCENE}."
    CUSTOM_REPLY = "What can you tell me about {FACTION}?"
    CUSTOM_OFFER = "The highway outside {LOCALE} is full of bandits and raiders and whoever; {FACTION} is nothing special. A patrol went out to check on them this morning... they should be reporting back any time now."
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job.tags.intersection((gears.tags.Police,gears.tags.Military,gears.tags.Politician)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])

class DZREPR_MedicineShipment(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_PROFIT, E_TOWN: DZRE_TOWN_NEUTRAL}
    CHANGES = {E_TOWN: DZRE_TOWN_AGAINST}
    MISSION_NAME = "Medicine Shipment"
    MISSION_PROMPT = "Protect {NPC}'s medicine shipment"
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_THE_BANDITS,missionbuilder.BAMO_RECOVER_CARGO)
    WIN_MESSAGE = ""
    DEFAULT_NEWS = "{NPC} at {NPC_SCENE} is waiting on a shipment of medicine"
    DEFAULT_INFO = None
    CUSTOM_REPLY = "Have you had any trouble getting supplies lately?"
    CUSTOM_OFFER = "Yes, actually. Thanks to {FACTION} shipments from the green zone have become iffy. I'm waiting on a vital order of medicine, but I don't know if it's going to get through."
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job.tags.intersection((gears.tags.Medic,)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])

class DZREPR_SeekAndDestroy(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_ACE"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_PROFIT, E_ACE: DZRE_ACE_UNKNOWN}
    CHANGES = {E_ACE: DZRE_ACE_HIDDENBASE}
    MISSION_NAME = "Highway Patrol"
    MISSION_PROMPT = "Search the highway looking for {FACTION}"
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_THE_BANDITS,missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL)
    WIN_MESSAGE = "Following the battle, you are no closer to finding the base of {FACTION} than you were before. Perhaps a change of tactics will be needed."
    DEFAULT_NEWS = "{NPC} at {NPC_SCENE} has been trying to find the {FACTION} base"
    DEFAULT_INFO = None
    CUSTOM_REPLY = "Have you found where the {FACTION} base is?"
    CUSTOM_OFFER = "No, and I'm beginning to think they can just disappear into thin air. {FACTION} has been raiding convoys up and down the highway then disappearing into the deadzone like ghosts. Maybe if I were lucky enough to stumble across them right as they're on the move I could figure out where they're coming from."
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.combatant and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])

class DZREPR_ThoseAreNotBandits(DZREPR_BaseMission):
    LABEL = "DZRE_MOTIVE_ACE"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_UNKNOWN, E_ACE: DZRE_ACE_HIDDENBASE}
    CHANGES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST}
    MISSION_NAME = "Defend the Defenders"
    MISSION_PROMPT = "Go see if the {LOCALE} defense force needs any help against {FACTION}"
    OBJECTIVES = (missionbuilder.BAMO_EXTRACT_ALLIED_FORCES,missionbuilder.BAMO_LOCATE_ENEMY_FORCES)
    WIN_MESSAGE = "The actions of {FACTION} point to one conclusion- that they are planning a takeover of {LOCALE}."

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and npc.combatant and npc not in camp.party:
            goffs.append(Offer(
                msg="For one thing, they spend at least as much time fighting the {LOCALE} defense force as they do stealing things.".format(**self.elements ),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": str(self.elements["FACTION"])}, subject="regular bandits", no_repeats=True
            ))
        return goffs

    def get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if npc.combatant and not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("{FACTION} aren't acting like regular bandits".format(**self.elements))
        return mygram

class DZREPR_DefendOurSoverignty(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST, E_TOWN: DZRE_TOWN_NEUTRAL}
    CHANGES = {E_TOWN: DZRE_TOWN_AGAINST}
    MISSION_NAME = "Strike Back"
    MISSION_PROMPT = "Launch a strike against {FACTION} for {NPC}"
    OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES,missionbuilder.BAMO_DEFEAT_COMMANDER)
    WIN_MESSAGE = ""
    DEFAULT_NEWS = "{NPC} is coordinating defense against {FACTION}"
    DEFAULT_INFO = "You can ask {NPC} about {FACTION} yourself; speak to {NPC.gender.object_pronoun} at {NPC_SCENE}."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} is coordinating defenses against {FACTION}."
    CUSTOM_REPLY = "I've come to help you against {FACTION}."
    CUSTOM_OFFER = "Good; {LOCALE} needs all the help it can get, and I'm not sure that anyone else in this town is taking {FACTION} seriously. Scouts have been following one of their commanders. If you hurry to this location, you might be able to deal them a crushing blow."
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job.tags.intersection((gears.tags.Police,gears.tags.Military,gears.tags.Politician)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])

class DZREPR_TheyHaveUsSurrounded(DZREPR_BaseMission):
    LABEL = "DZRE_ACE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_ACE: DZRE_ACE_HIDDENBASE, E_TOWN: DZRE_TOWN_NEUTRAL}
    CHANGES = {E_TOWN: DZRE_TOWN_AFRAID}
    MISSION_NAME = "They Have Us Surrounded"
    MISSION_PROMPT = "Scout for agents of {FACTION} near {LOCALE}"
    OBJECTIVES = (missionbuilder.BAMO_SURVIVE_THE_AMBUSH,missionbuilder.BAMO_LOCATE_ENEMY_FORCES)
    WIN_MESSAGE = ""

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and not npc.combatant and npc not in camp.party:
            goffs.append(Offer(
                msg="I've heard they have a hidden base, and are keeping watch over all the traffic that comes into or out of {LOCALE}. We're essentially at their mercy.".format(**self.elements ),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": str(self.elements["FACTION"])}, subject="get nervous about {FACTION}".format(**self.elements), no_repeats=True
            ))
        return goffs

    def get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not npc.combatant and not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("people are starting to get nervous about {FACTION}".format(**self.elements))
        return mygram

class DZREPR_ClarifyTheirMotives(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_UNKNOWN, E_TOWN: DZRE_TOWN_AGAINST}
    CHANGES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST}
    MISSION_NAME = "Clarifying Their Motives"
    MISSION_PROMPT = "Scout out {FACTION} for {NPC}"
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_THE_BANDITS,missionbuilder.BAMO_LOCATE_ENEMY_FORCES)
    WIN_MESSAGE = "From the amount of force they have deployed, it seems clear that {FACTION} are not ordinary bandits. They are planning something big."
    DEFAULT_NEWS = "we ought to attack {FACTION} as soon as possible, but {NPC} says more information is needed first"
    DEFAULT_INFO = "You can ask {NPC} about {FACTION} yourself; speak to {NPC.gender.object_pronoun} at {NPC_SCENE}."
    DEFAULT_MEMO = "{NPC} wants to understand the threat posed by {FACTION}; you can ask {NPC.gender.object_pronoun} about this at {NPC_SCENE}."
    CUSTOM_REPLY = "I heard you are collecting information about {FACTION}?"
    CUSTOM_OFFER = "I know that most people in town expect the militia to act right away, but first I think we ought to know what {FACTION} wants. I would be grateful if you could scout out their position and see what they're up to."
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job.tags.intersection((gears.tags.Police,gears.tags.Politician)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])

class DZREPR_TheConflictIntensifies(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST, E_TOWN: DZRE_TOWN_AGAINST}
    CHANGES = {E_TOWN: DZRE_TOWN_AFRAID}
    MISSION_NAME = "The Conflict Intensifies"
    MISSION_PROMPT = "Strike {FACTION} for {NPC}"
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER,missionbuilder.BAMO_LOCATE_ENEMY_FORCES)
    WIN_MESSAGE = ""
    DEFAULT_NEWS = "{FACTION} are planning to take over {LOCALE} but {NPC} has a plan to stop them"
    DEFAULT_INFO = "Maybe {NPC} will have a mission for you? You can find {NPC.gender.object_pronoun} at {NPC_SCENE}."
    DEFAULT_MEMO = "{NPC} is organizing defense against {FACTION}; you can ask {NPC.gender.object_pronoun} about this at {NPC_SCENE}."
    CUSTOM_REPLY = "Do you have a plan to defeat {FACTION}?"
    CUSTOM_OFFER = "Not exactly. The {LOCALE} militia is overwhelmed; the most we can do right now is try to keep them at bay with the few resources we have available. The situation doesn't look good. We could use all the help we can get."
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job.tags.intersection((gears.tags.Police,gears.tags.Politician,gears.tags.Military)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])

class DZREPR_BanditAbductions(DZREPR_BaseMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_UNKNOWN, E_TOWN: DZRE_TOWN_AFRAID}
    CHANGES = {E_MOTIVE: DZRE_MOTIVE_PROFIT}
    MISSION_NAME = "Respond to Distress Call"
    MISSION_PROMPT = "Patrol highway for travelers being attacked by {FACTION}"
    OBJECTIVES = (missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL,missionbuilder.BAMO_RECOVER_CARGO)
    WIN_MESSAGE = ""

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and not npc.combatant and npc not in camp.party:
            goffs.append(Offer(
                msg="If you spend any time at all on the highway leading into town, you're certain to receive a distress call from someone being attacked by {FACTION}.".format(**self.elements ),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": "these abductions"}, subject="{FACTION} has been abducting".format(**self.elements), no_repeats=True
            ))
        return goffs

    def get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not npc.combatant and not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("{FACTION} has been abducting travelers coming into or leaving {LOCALE}".format(**self.elements))
        return mygram

class DZREPR_HuntingForSecretBase(DZREPR_NPCMission):
    LABEL = "DZRE_ACE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_ACE: DZRE_ACE_HIDDENBASE, E_TOWN: DZRE_TOWN_AGAINST}
    CHANGES = {E_TOWN: DZRE_TOWN_AFRAID}
    MISSION_NAME = "Hunting for Secret Base"
    MISSION_PROMPT = "Join {NPC}'s search for the hidden base"
    OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES,missionbuilder.BAMO_EXTRACT_ALLIED_FORCES)
    WIN_MESSAGE = "The patrol sent by {NPC} didn't turn up anything. This failure is sure to raise tensions in {LOCALE}."
    DEFAULT_NEWS = "{NPC} is organizing a patrol to find the hidden base belonging to {FACTION}"
    DEFAULT_INFO = "If you want to join {NPC}'s mission, you can find {NPC.gender.object_pronoun} at {NPC_SCENE}."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} is organizing a mission to locate the hidden base belonging to {FACTION}."
    CUSTOM_REPLY = "I heard that you're looking for {FACTION}."
    CUSTOM_OFFER = "People in town are starting to get nervous because it seems like {FACTION} can strike from anywhere. I've dispatched search parties to try and find their hidden base; you can join them, if you have time."
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job.tags.intersection((gears.tags.Military,gears.tags.Politician)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


#   *******************************************
#   ***   ROAD  EDGE  RATCHET  CONCLUSION   ***
#   *******************************************

class DZREPRC_CallOutBattle(Plot):
    # Will activate the adventure when property mission_active set to True
    # Required Elements: METRO, LOCALE, MISSION_GATE, FACTION
    LABEL = "DZRE_CONCLUSION"
    active = True
    scope = "METRO"
    MISSION_NAME = "Ultimate Challenge"
    MISSION_PROMPT = "Go meet {FACTION}'s challenge."
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER,)
    WIN_MESSAGE = "With their leaders defeated and their mecha forces destroyed, {FACTION} cease to be a danger to travelers in the dead zone."

    def custom_init(self, nart):
        self.build_mission(nart.camp)
        self.mission_active = False
        return True

    def build_mission(self,camp):
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, self.MISSION_NAME, (self.elements["LOCALE"],self.elements["MISSION_GATE"]),
            enemy_faction = self.elements["FACTION"], rank=self.rank,
            objectives = self.OBJECTIVES, one_chance=False,
            architecture=gharchitecture.MechaScaleDeadzone,
            win_message=self.WIN_MESSAGE.format(**self.elements)
        )

    def t_UPDATE(self,camp):
        if self.mission_seed.ended:
            if self.mission_seed.is_won():
                camp.check_trigger("WIN",self)
            else:
                camp.check_trigger("LOSE",self)
            self.end_plot(camp,True)

    def activate_mission(self,camp):
        self.mission_active = True
        self.memo = "You learned that {FACTION} are waiting just outside of {LOCALE} to challenge you to a final battle.".format(**self.elements)
        missionbuilder.NewMissionNotification(self.MISSION_NAME,self.elements["MISSION_GATE"])
        camp.check_trigger("UPDATE")

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed and self.mission_active:
            thingmenu.add_item(self.MISSION_PROMPT.format(**self.elements), self.mission_seed)

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and npc not in camp.party:
            goffs.append(Offer(
                msg="You've caused a lot of trouble for {FACTION}, so they've mobilized all of their forces in {LOCALE} to finish you off once and for all.".format(**self.elements ),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": "this challenge"}, subject="{FACTION} have challenged".format(**self.elements),
                no_repeats=True
            ))
        return goffs

    def get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("{FACTION} have challenged you to one final battle".format(**self.elements))
            mygram["[HELLO_AGAIN]"].append("What are you doing here, [audience]?! Didn't you hear that {FACTION} have challenged you to one final battle?".format(**self.elements))
            mygram["[HELLO_FIRST]"].append(
                "You're [audience], aren't you? [chat_lead_in] {FACTION} have challenged you to one final battle.".format(**self.elements)
            )
        return mygram


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
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene, must_find=False)
        if not destscene:
            destscene = self.seek_element(nart, "_DEST", self._is_good_scene, scope=myscene)

        mynpc = self.register_element(
            "NPC", gears.selector.random_character(
                job=gears.jobs.ALL_JOBS["Trucker"], rank=random.randint(self.rank-10,self.rank+10),
                local_tags=(gears.personality.GreenZone,), combatant=True,
            ), dident="_DEST"
        )
        destscene.local_teams[mynpc] = destscene.civilian_team

        self.got_rumor = False
        self.offered_services = False

        return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and (gears.tags.SCENE_GARAGE in candidate.attributes or gears.tags.SCENE_TRANSPORT in candidate.attributes)

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
        if not self.start_missions and npc is not self.elements["NPC"] and npc not in camp.party:
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

    def NPC_offers(self, camp):
        mylist = list()

        if not self.start_missions:
            mylist.append(Offer("[HELLO] While bringing in a convoy from {}, I got attacked by bandits and lost everything.".format(self.elements["DZ_EDGE"].get_city_link(self.elements["LOCALE"])),
                                context=ContextTag([context.HELLO]),
                                ))

            mylist.append(Offer("I can tell you that {} haven't been around for long- if I knew there were raiders working this stretch I would have brought along more muscle. If you can find their base it shouldn't be hard to get rid of them.".format(self.elements["FACTION"]),
                                context=ContextTag([context.INFO]), effect=self._get_briefed,
                                data={"subject": "the bandits"}, no_repeats=True
                                ))

        elif self.elements[E_MISSION_NUMBER] > 1 and self.elements["NPC"].get_reaction_score(camp.pc, camp) > 0 and not self.offered_services:
            mylist.append(Offer(
                "[HELLO] Now that my mek's repaired, I'd love a chance to take on {} myself.".format(self.elements["FACTION"]),
                context=ContextTag([context.HELLO]),
                ))
            if camp.can_add_lancemate():
                mylist.append(Offer(
                    "[THANKS_FOR_CHOOSING_ME] Let's roll out.", context=ContextTag((context.JOIN,)),
                    effect=self._join_lance
                    ))
            else:
                mylist.append(Offer(
                    "Seems like it'd be a little crowded to join your [lance] now, but if you need my help in the future come back and find me.", context=ContextTag((context.JOIN,)),
                    effect=self._join_lance
                    ))
        else:
            mylist.append(Offer("[HELLO] Give {} hell.".format(self.elements["FACTION"]),
                                context=ContextTag([context.HELLO]),
                                ))
        return mylist

    def _get_briefed(self,camp):
        self.start_missions = True
        camp.check_trigger("UPDATE")
        self.memo = "You learned that {} must have a base near {}.".format(self.elements["FACTION"],self.elements["LOCALE"])

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        self.offered_services = True
        if camp.can_add_lancemate():
            effect = game.content.plotutility.AutoJoiner(npc)
            effect(camp)


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
        myedge = self.elements["DZ_EDGE"]
        self.rank = 15 + random.randint(1,6) - random.randint(1,6)
        self.register_element("DZ_EDGE_STYLE",RoadEdge.STYLE_YELLOW)
        self.register_element("FACTION",plotutility.RandomBanditCircle(nart.camp,enemies=(myedge.start_node.destination.faction,)))

        self.add_sub_plot(nart,"ADD_REMOTE_OFFICE",ident="BANDITRO",spstate=PlotState(rank=self.rank+5,elements={"METRO":myedge.start_node.destination.metrodat,"LOCALE":myedge.start_node.destination,"MISSION_GATE":myedge.start_node.entrance}).based_on(self))
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

    def MISSION_WIN(self,camp):
        self.elements["DZ_EDGE"].style = self.elements["DZ_EDGE"].STYLE_SAFE
