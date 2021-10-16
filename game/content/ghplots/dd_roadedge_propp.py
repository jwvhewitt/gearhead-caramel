import collections
import random

import game.content
import gears
import pbge
from game.content import gharchitecture
from game.content.ghplots import missionbuilder
from game.ghdialogue import context
from pbge.dialogue import Offer, ContextTag
from pbge.plots import Plot
from . import dd_customobjectives

from game import memobrowser
Memo = memobrowser.Memo


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
DZRE_MOTIVE_TREASURE = "DZRE_MOTIVE_TREASURE"   # There's some kind of hidden treasure they're after. Lostech?

E_ACE = "DZREPR_ACE"
DZRE_ACE_UNKNOWN = "DZRE_ACE_UNKNOWN"
DZRE_ACE_HIDDENBASE = "DZRE_ACE_HIDDENBASE"
DZRE_ACE_ZEUSCANNON = "DZRE_ACE_ZEUSCANNON"
DZRE_ACE_SPONSOR = "DZRE_ACE_SPONSOR"

E_TOWN = "DZREPR_TOWN"
DZRE_TOWN_NEUTRAL = "DZRE_TOWN_NEUTRAL"
DZRE_TOWN_AGAINST = "DZRE_TOWN_AGAINST"
DZRE_TOWN_AFRAID = "DZRE_TOWN_AFRAID"
DZRE_TOWN_DEVASTATED = "DZRE_TOWN_DEVASTATED"
DZRE_TOWN_INSPIRED = "DZRE_TOWN_INSPIRED"

E_MISSION_NUMBER = "DZREPR_MISSION_NUMBER"
E_MISSION_WINS = "DZREPR_MISSION_WINS"


class DZREPR_BasePlot(Plot):
    # Subclass this plot for the specific starting scenarios. This plot performs the following functions:
    # - After start_missions is set to True, start generating investigation missions.
    # - Update plot state and load new investigation missions after each mission finished
    # - Load the conclusion mission when appropriate
    # - Send a WIN trigger when the conclusion mission is won
    # Required Elements: METRO, METROSCENE, MISSION_GATE
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
        self.register_element(E_MISSION_WINS, 0)
        self.start_missions = False
        self.final_loaded = False

        return True

    def t_UPDATE(self,camp):
        if self.start_missions:
            if (self.MISSION_IDENTS[0] not in self.subplots or not self.subplots[self.MISSION_IDENTS[0]]) and not self.final_loaded:
                self.load_missions(camp)

    def load_missions(self,camp):
        if self.elements[E_MISSION_NUMBER] >= self.NUMBER_OF_MISSIONS_BEFORE_CONCLUSION:
            init = pbge.plots.PlotState(rank=max(self.rank,camp.renown-3) + self.elements[E_MISSION_WINS] * 3 + 5).based_on(self)
            nart = game.content.GHNarrativeRequest(camp, init, self.CONCLUSION_LABEL, game.content.PLOT_LIST)
            if nart.story:
                nart.build()
                self.subplots[self.CONCLUSION_IDENT] = nart.story
            self.final_loaded = True
        else:
            random.shuffle(self.MISSION_LABELS)
            num_miss = 0
            miss_num = 0
            while num_miss < 2 and miss_num < len(self.MISSION_LABELS):
                init = pbge.plots.PlotState(rank=max(self.rank,camp.renown-3) + self.elements[E_MISSION_WINS]*3).based_on(self)
                nart = game.content.GHNarrativeRequest(camp, init, self.MISSION_LABELS[miss_num], game.content.PLOT_LIST)
                if nart.story:
                    nart.build()
                    self.subplots[self.MISSION_IDENTS[num_miss]] = nart.story
                    num_miss += 1
                miss_num += 1
            if num_miss < 1:
                # Drat- we have apparently hit a deadend.
                print("DeadEnd Error!!! {DZREPR_MOTIVE} {DZREPR_ACE} {DZREPR_TOWN}".format(**self.elements))
            elif num_miss < 2:
                # We have fewer plots than we wanted.
                print("Only one plot warning! {DZREPR_MOTIVE} {DZREPR_ACE} {DZREPR_TOWN}".format(**self.elements))
            else:
                self.elements[E_MISSION_NUMBER] += 1

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
        self.elements["METRO"].local_reputation += 5
        self.elements[E_MISSION_WINS] += 1
        self.reset_missions(camp)

    def ALPHA_MISSION_LOSE(self,camp):
        self.subplots["ALPHA_MISSION"].alter_the_context(self)
        self.elements["METRO"].local_reputation -= 5
        self.reset_missions(camp)

    def BETA_MISSION_WIN(self,camp):
        self.subplots["BETA_MISSION"].alter_the_context(self)
        self.elements["METRO"].local_reputation += 5
        self.elements[E_MISSION_WINS] += 1
        self.reset_missions(camp)

    def BETA_MISSION_LOSE(self,camp):
        self.subplots["BETA_MISSION"].alter_the_context(self)
        self.elements["METRO"].local_reputation -= 5
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
    # Required Elements: METRO, METROSCENE, MISSION_GATE, FACTION
    LABEL = "DZRE_MOTIVE_ACE_TOWN"
    active = True
    scope = "METRO"
    REQUIRES = {E_MOTIVE: None, E_ACE: None, E_TOWN: None}
    REQUIRED_FACTAGS = set()
    CHANGES = {E_MOTIVE: None, E_ACE: None, E_TOWN: None}
    MISSION_NAME = "The Mission"
    MISSION_PROMPT = "Go do mission"
    MISSION_ARCHITECTURE = gharchitecture.MechaScaleDeadzone
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_THE_BANDITS,)
    WIN_MESSAGE = ""
    LOSS_MESSAGE = ""
    MISSION_GRAMMAR = None

    @classmethod
    def matches(cls, pstate):
        """Returns True if this plot matches the current plot state."""
        return (all(pstate.elements.get(k,0) == cls.REQUIRES[k] for k in cls.REQUIRES.keys()) and cls.REQUIRED_FACTAGS.issubset(pstate.elements["FACTION"].factags)) or cls.LABEL == "DZRE_TEST"

    def custom_init(self, nart):
        self.mission_seed = None
        self.mission_active = False
        return True

    def build_mission(self,camp):
        if self.MISSION_GRAMMAR:
            mgram = dict()
            for k,vs in self.MISSION_GRAMMAR.items():
                mgram[k] = list()
                for v in vs:
                    mgram[k].append(v.format(**self.elements))
        else:
            mgram = None
        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, self.MISSION_NAME, self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            enemy_faction = self.elements["FACTION"], rank=self.rank,
            objectives = self.OBJECTIVES, one_chance=True,
            architecture=self.MISSION_ARCHITECTURE(), mission_grammar=mgram,
            win_message=self.WIN_MESSAGE.format(**self.elements),
            loss_message=self.LOSS_MESSAGE.format(**self.elements),
            cash_reward=100 + self.elements[E_MISSION_WINS] ** 2 * 25
        )

    def t_START(self,camp):
        if self.LABEL == "DZRE_TEST" and not self.mission_active:
            self.activate_mission(camp)

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
    DEFAULT_MEMO = "You can ask {NPC} about {FACTION}."
    CUSTOM_REPLY = "What do you know about {FACTION}?"
    CUSTOM_OFFER = "I can tell you that you can go do a mission in {METROSCENE} so go do it."
    def custom_init(self, nart):
        super().custom_init(nart)
        if not self.LABEL == "DZRE_TEST":
            mynpc = self.seek_element(nart, "NPC", self._npc_matches, scope=self.elements["METROSCENE"])
            npcscene = self.register_element("NPC_SCENE",mynpc.container.owner)
        else:
            self.register_element("NPC",gears.selector.random_character())
            self.register_element("NPC_SCENE", self.elements["METROSCENE"])
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
    def _get_dialogue_grammar(self, npc, camp):
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
        self.memo = Memo( self.DEFAULT_MEMO.format(**self.elements)
                        , self.elements["NPC_SCENE"]
                        )


class DZREPRC_ConclusionTemplate(Plot):
    # Just add a call to activate_mission
    # Required Elements: METRO, METROSCENE, MISSION_GATE, FACTION
    LABEL = "DZRE_CONCLUSION_removetag"
    active = True
    scope = "METRO"
    MISSION_NAME = ""
    MISSION_PROMPT = ""
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER,missionbuilder.BAMO_DEFEAT_ARMY)
    WIN_MESSAGE = ""
    LOSS_MESSAGE = ""
    DEFAULT_MEMO = ""
    REQUIRES = {}
    REQUIRED_FACTAGS = set()
    SOLO_MISSION = False
    MISSION_GRAMMAR = None

    @classmethod
    def matches(cls, pstate):
        """Returns True if this plot matches the current plot state."""
        return (all(pstate.elements.get(k,0) == cls.REQUIRES[k] for k in cls.REQUIRES.keys()) and cls.REQUIRED_FACTAGS.issubset(pstate.elements["FACTION"].factags)) or cls.LABEL == "DZRE_TEST"

    def custom_init(self, nart):
        self.build_mission(nart.camp)
        self.mission_active = False
        return True

    def build_mission(self,camp):
        if self.MISSION_GRAMMAR:
            mgram = dict()
            for k,vs in self.MISSION_GRAMMAR.items():
                mgram[k] = list()
                for v in vs:
                    mgram[k].append(v.format(**self.elements))
        else:
            mgram = None

        self.mission_seed = missionbuilder.BuildAMissionSeed(
            camp, self.MISSION_NAME, self.elements["METROSCENE"], self.elements["MISSION_GATE"],
            enemy_faction = self.elements["FACTION"], rank=self.rank,
            objectives = self.OBJECTIVES, one_chance=True, mission_grammar=mgram,
            architecture=gharchitecture.MechaScaleDeadzone(),
            win_message=self.WIN_MESSAGE.format(**self.elements),
            loss_message=self.LOSS_MESSAGE.format(**self.elements),
            cash_reward=200 + self.elements[E_MISSION_WINS] ** 2 * 25,
            solo_mission=self.SOLO_MISSION
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
        self.memo = Memo( self.DEFAULT_MEMO.format(**self.elements)
                        , self.elements["METROSCENE"]
                        )
        missionbuilder.NewMissionNotification(self.MISSION_NAME,self.elements["MISSION_GATE"])
        camp.check_trigger("UPDATE")

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.mission_seed and self.mission_active:
            thingmenu.add_item(self.MISSION_PROMPT.format(**self.elements), self.mission_seed)



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
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="find your base",
        lose_pp="tried to find your base", lose_ep="tried to find our base"
    )

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

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not npc.combatant and not self.mission_active:
            mygram["[News]"].append("maybe a pilot would know how to find {}.".format(self.elements["FACTION"]))
        return mygram


class DZREPR_ShootThemInTheGun(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_ACE"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_PROFIT, E_ACE: DZRE_ACE_ZEUSCANNON}
    CHANGES = {E_ACE: DZRE_ACE_SPONSOR}
    MISSION_NAME = "Disable Their Guns"
    MISSION_PROMPT = "Strike against {FACTION}'s artillery"
    OBJECTIVES = (missionbuilder.BAMO_DESTROY_ARTILLERY,)
    WIN_MESSAGE = "Examining the wreckage of the artillery, it's clear that these pieces were not locally made. Someone else must be backing {FACTION}."
    DEFAULT_NEWS = "after the recent artillery attack, {NPC} knows where {FACTION}'s cannons are"
    DEFAULT_INFO = "You can talk to {NPC} at {NPC_SCENE} to learn more information."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} may know where {FACTION}'s artillery is."
    CUSTOM_REPLY = "What do you know about {FACTION}'s artillery?"
    CUSTOM_OFFER = "They've got powerful weapons, but it seems like they don't really know how to use them. I've examined the trajectories and all of their attacks have come from the same site. If you hurry there, you may be able to disable their heavy weapons."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="disable your artillery",
        win_pp="I destroyed your artillery", win_ep="you destroyed some of my artillery",
        lose_ep="my artillery was too powerful for you"
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and nart.camp.are_faction_allies(candidate,self.elements["METROSCENE"]) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_HighwayPatrol(DZREPR_BaseMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_UNKNOWN, E_TOWN: DZRE_TOWN_NEUTRAL}
    CHANGES = {E_MOTIVE: DZRE_MOTIVE_PROFIT}
    MISSION_NAME = "Highway Patrol"
    MISSION_PROMPT = "Patrol highway for {FACTION}"
    OBJECTIVES = (missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL,missionbuilder.BAMO_LOCATE_ENEMY_FORCES)
    WIN_MESSAGE = "You have confirmed that {FACTION} are targeting convoys along the highway."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="defend the highway", objective_ep="raid some convoys",
        win_ep="you screwed up my raid",
        lose_ep="you couldn't stop me"
    )

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and gears.tags.Politician in npc.get_tags() and npc not in camp.party:
            goffs.append(Offer(
                msg="Since {} showed up, several convoys have gone missing between here and {}. If you patrol the highway you might be able to catch them in the act.".format(self.elements["FACTION"],self.elements["DZ_EDGE"].get_city_link(self.elements["METROSCENE"])),
                context=ContextTag((context.CUSTOM,)), effect=self.activate_mission,
                data={"reply": "Do you know what {} want?".format(self.elements["FACTION"])}, no_repeats=True
            ))
        return goffs

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if gears.tags.Politician not in npc.get_tags() and not self.mission_active:
            mygram["[News]"].append("the people in charge know more about {} than they're letting on.".format(self.elements["FACTION"]))
        return mygram


class DZREPR_SeeWhatTheyreMadeOf(DZREPR_BaseMission):
    LABEL = "DZRE_MOTIVE_ACE"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST, E_ACE: DZRE_ACE_UNKNOWN}
    CHANGES = {E_ACE: DZRE_ACE_ZEUSCANNON}
    MISSION_NAME = "Test Their Metal"   # I trust my audience to recognize a pun when they see one.
    MISSION_PROMPT = "Launch a surprise attack against {FACTION}"
    OBJECTIVES = (missionbuilder.BAMO_DESTROY_ARTILLERY,missionbuilder.BAMO_DEFEAT_COMMANDER)
    WIN_MESSAGE = "From this battle, it's clear that {FACTION} are far better equipped than you had expected."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        win_ep="you saw that we have more guns than you know",
        lose_pp="I got beaten by your artillery", lose_ep="I showed you just how much firepower we have"
    )

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and npc not in camp.party and not camp.are_faction_allies(npc,self.elements["FACTION"]):
            goffs.append(Offer(
                msg="So far our town has mainly been on the defensive; I say it's time to take the fight to {FACTION}. You should go out there and find out what they're made of.".format(**self.elements),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": str(self.elements["FACTION"])}, subject=str(self.elements["FACTION"]), no_repeats=True
            ))
        return goffs

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not self.mission_active and npc not in camp.party and not camp.are_faction_allies(npc,self.elements["FACTION"]):
            if npc.combatant:
                mygram["[News]"].append("we need to get more proactive about {FACTION}".format(**self.elements))
            else:
                mygram["[News]"].append("all the pilots in town are busy dealing with {FACTION}".format(**self.elements))
        return mygram


class DZREPR_FaultyIntel(DZREPR_NPCMission):
    LABEL = "DZRE_ACE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_ACE: DZRE_ACE_UNKNOWN, E_TOWN: DZRE_TOWN_AFRAID}
    CHANGES = {E_ACE: DZRE_ACE_HIDDENBASE}
    MISSION_NAME = "Strike Their Base"
    MISSION_PROMPT = "Strike the alleged site of {FACTION}'s base"
    OBJECTIVES = (missionbuilder.BAMO_SURVIVE_THE_AMBUSH,missionbuilder.BAMO_CAPTURE_BUILDINGS)
    WIN_MESSAGE = "Following the battle, you quickly realize that this site is not the main base for {FACTION}. Whoever fed {NPC} the intel was leading you into a trap."
    DEFAULT_NEWS = "{NPC} has information about {FACTION} that could change everything"
    DEFAULT_INFO = "You can ask {NPC} about {FACTION} yourself; speak to {NPC.gender.object_pronoun} at {NPC_SCENE}."
    DEFAULT_MEMO = "{NPC} has new information about {FACTION}; you can ask {NPC.gender.object_pronoun} about this at {NPC_SCENE}."
    CUSTOM_REPLY = "What have you learned about {FACTION}?"
    CUSTOM_OFFER = "A very reliable source has given me the location of {FACTION}'s base. One solid strike there and they'll never be able to recover. People in {METROSCENE} are getting nervous; we have to do something."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="capture your base", objective_ep="defend our base",
        win_pp="I captured one of your bases", win_ep="you captured one of our bases",
        lose_pp="I couldn't capture your base", lose_ep="you failed to capture our base"
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job.tags.intersection((gears.tags.Police,gears.tags.Military,gears.tags.Politician)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


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
    CUSTOM_OFFER = "The highway outside {METROSCENE} is full of bandits and raiders and whoever; {FACTION} is nothing special. A patrol went out to check on them this morning... they should be reporting back any time now."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="extract {NPC}'s patrol", objective_ep="destroy {NPC}'s militia",
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job and candidate.job.tags.intersection((gears.tags.Police,gears.tags.Military,gears.tags.Politician)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_MedicineShipment(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #TODO: Add a non-bandit mission for this Propp State
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_PROFIT, E_TOWN: DZRE_TOWN_NEUTRAL}
    REQUIRED_FACTAGS = {gears.tags.Criminal,}
    CHANGES = {E_TOWN: DZRE_TOWN_AGAINST}
    MISSION_NAME = "Medicine Shipment"
    MISSION_PROMPT = "Protect {NPC}'s medicine shipment"
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_THE_BANDITS,missionbuilder.BAMO_RECOVER_CARGO)
    WIN_MESSAGE = ""
    DEFAULT_NEWS = "{NPC} at {NPC_SCENE} is waiting on a shipment of medicine"
    DEFAULT_INFO = None
    CUSTOM_REPLY = "Have you had any trouble getting supplies lately?"
    CUSTOM_OFFER = "Yes, actually. Thanks to {FACTION} shipments from the green zone have become iffy. I'm waiting on a vital order of medicine, but I don't know if it's going to get through."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="recover {NPC}'s medicine", objective_ep="loot this caravan",
        win_pp="I recovered the medicine {METROSCENE} needed", win_ep="you stole my rightfully looted cargo",
        lose_pp="you stole medicine that {METROSCENE} needed", lose_ep="you couldn't stop me"
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job and candidate.job.tags.intersection((gears.tags.Medic,)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_SeekAndDestroy(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_ACE"
    #TODO: Add a non-bandit mission for this Propp State
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_PROFIT, E_ACE: DZRE_ACE_UNKNOWN}
    REQUIRED_FACTAGS = {gears.tags.Criminal,}
    CHANGES = {E_ACE: DZRE_ACE_HIDDENBASE}
    MISSION_NAME = "Highway Patrol"
    MISSION_PROMPT = "Search the highway looking for {FACTION}"
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_THE_BANDITS,missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL)
    WIN_MESSAGE = "Following the battle, you are no closer to finding the base of {FACTION} than you were before. Perhaps a change of tactics will be needed."
    DEFAULT_NEWS = "{NPC} at {NPC_SCENE} has been trying to find the {FACTION} base"
    DEFAULT_INFO = None
    CUSTOM_REPLY = "Have you found where the {FACTION} base is?"
    CUSTOM_OFFER = "No, and I'm beginning to think they can just disappear into thin air. {FACTION} has been raiding convoys up and down the highway then disappearing into the deadzone like ghosts. Maybe if I were lucky enough to stumble across them right as they're on the move I could figure out where they're coming from."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="locate your base",
        win_ep="you won the battle but learned nothing from it",
        lose_ep="you failed to find our hidden base"
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.combatant and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_NotSoHiddenIzzit(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_ACE"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_PROFIT, E_ACE: DZRE_ACE_HIDDENBASE}
    CHANGES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST}
    MISSION_NAME = "Strike Their Base"
    MISSION_PROMPT = "Strike the alleged site of {FACTION}'s base"
    OBJECTIVES = (missionbuilder.BAMO_STORM_THE_CASTLE,)
    WIN_MESSAGE = "Judging by the stockpiles of weapons and equipment at the captured base, it seems that {FACTION} are planning something bigger than just raiding the highway."
    DEFAULT_NEWS = "{NPC} at {NPC_SCENE} may have located the {FACTION} base"
    DEFAULT_INFO = None
    CUSTOM_REPLY = "Do you know where {FACTION} are hiding?"
    CUSTOM_OFFER = "As you well know, {FACTION} are very good at covering their tracks, but I think we've got a solid lead on where their hidden base is. It's important that we strike fast- if they figure out that we know where they are, they'll abandon the current site and find another one."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="capture your base", objective_ep="protect our base",
        win_pp="I destroyed your base", win_ep="you destroyed our base",
        lose_ep="you failed to capture our base"
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.combatant and candidate not in nart.camp.party and nart.camp.are_faction_allies(candidate,self.elements["METROSCENE"]) and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_ThoseAreNotBandits(DZREPR_BaseMission):
    LABEL = "DZRE_MOTIVE_ACE"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_UNKNOWN, E_ACE: DZRE_ACE_HIDDENBASE}
    CHANGES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST}
    MISSION_NAME = "Defend the Defenders"
    MISSION_PROMPT = "Go see if the {METROSCENE} defense force needs any help against {FACTION}"
    OBJECTIVES = (missionbuilder.BAMO_EXTRACT_ALLIED_FORCES,missionbuilder.BAMO_AID_ALLIED_FORCES)
    WIN_MESSAGE = "The actions of {FACTION} point to one conclusion- that they are planning a takeover of {METROSCENE}."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="defend {METROSCENE}", objective_ep="destroy the {METROSCENE} militia",
        win_pp="I protected {METROSCENE} from you", win_ep="you saved the {METROSCENE} militia",
        lose_pp="you destroyed the {METROSCENE} militia", lose_ep="I destroyed the {METROSCENE} militia"
    )

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and npc.combatant and npc not in camp.party:
            goffs.append(Offer(
                msg="For one thing, they spend at least as much time fighting the {METROSCENE} defense force as they do stealing things.".format(**self.elements ),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": str(self.elements["FACTION"])}, subject="regular bandits", no_repeats=True
            ))
        return goffs

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if npc.combatant and not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("{FACTION} aren't acting like regular bandits".format(**self.elements))
        return mygram


class DZREPR_WhyDoYouNeedAGiantCannon(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_ACE"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_UNKNOWN, E_ACE: DZRE_ACE_ZEUSCANNON}
    CHANGES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST}
    MISSION_NAME = "Recon by Force"
    MISSION_PROMPT = "Search for the patrol sent out by {NPC}"
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER,missionbuilder.BAMO_EXTRACT_ALLIED_FORCES)
    WIN_MESSAGE = ""
    DEFAULT_NEWS = "{NPC} has been sending patrols to keep tabs on {FACTION}, but most of them haven't come back"
    DEFAULT_INFO = "If you'd like to join the next patrol, you can ask {NPC} at {NPC_SCENE}."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} may have a mission for you."
    CUSTOM_REPLY = "[HELLO:MISSION]"
    CUSTOM_OFFER = "We know that {FACTION} has a lot more heavy artillery than we normally see in these parts. I've been sending patrols out to check up on them, but we've been losing pilots at an alarming rate. [I_WANT_YOU_TO_INVESTIGATE]"
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="recover {NPC}'s patrol",
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and nart.camp.are_faction_allies(candidate,self.elements["METROSCENE"]) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


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
    CUSTOM_OFFER = "Good; {METROSCENE} needs all the help it can get, and I'm not sure that anyone else in this town is taking {FACTION} seriously. Scouts have been following one of their commanders. If you hurry to this location, you might be able to deal them a crushing blow."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="defend {METROSCENE}", objective_ep="conquer {METROSCENE}",
        win_pp="I drove you out of {METROSCENE}", win_ep="you drove me away from {METROSCENE}",
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job.tags.intersection((gears.tags.Police,gears.tags.Military,gears.tags.Politician)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_TheyHaveUsSurrounded(DZREPR_BaseMission):
    LABEL = "DZRE_ACE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_ACE: DZRE_ACE_HIDDENBASE, E_TOWN: DZRE_TOWN_NEUTRAL}
    CHANGES = {E_TOWN: DZRE_TOWN_AFRAID}
    MISSION_NAME = "They Have Us Surrounded"
    MISSION_PROMPT = "Scout for agents of {FACTION} near {METROSCENE}"
    OBJECTIVES = (missionbuilder.BAMO_SURVIVE_THE_AMBUSH,missionbuilder.BAMO_LOCATE_ENEMY_FORCES)
    WIN_MESSAGE = ""
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="clear you out of {METROSCENE}", objective_ep="infiltrate {METROSCENE}",
    )

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and not npc.combatant and npc not in camp.party:
            goffs.append(Offer(
                msg="I've heard they have a hidden base, and are keeping watch over all the traffic that comes into or out of {METROSCENE}. We're essentially at their mercy.".format(**self.elements ),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": str(self.elements["FACTION"])}, subject="get nervous about {FACTION}".format(**self.elements), no_repeats=True
            ))
        return goffs

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not npc.combatant and not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("people are starting to get nervous about {FACTION}".format(**self.elements))
        return mygram


class DZREPR_ClarifyTheirMotives(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_UNKNOWN, E_TOWN: DZRE_TOWN_AGAINST}
    REQUIRED_FACTAGS = {gears.tags.Criminal,}
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
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="test your capabilities", objective_ep="take over {METROSCENE}",
        win_pp="I defeated your bandits",
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job.tags.intersection((gears.tags.Police,gears.tags.Politician)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_GetTheVotesKillTheBaddies(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_UNKNOWN, E_TOWN: DZRE_TOWN_AGAINST}
    CHANGES = {E_TOWN: DZRE_TOWN_AFRAID}
    MISSION_NAME = "Eliminate the Problem"
    MISSION_PROMPT = "Get rid of {FACTION} for {NPC}"
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER,missionbuilder.BAMO_LOCATE_ENEMY_FORCES)
    WIN_MESSAGE = "As the battle ends, you receive news over the comms that {FACTION} have struck the {METROSCENE} Militia headquarters. This mission was merely a diversion."
    DEFAULT_NEWS = "{NPC} has promised to get rid of {FACTION}"
    DEFAULT_INFO = "You can ask {NPC} about {FACTION} yourself; speak to {NPC.gender.object_pronoun} at {NPC_SCENE}."
    DEFAULT_MEMO = "{NPC} wants to rid {METROSCENE} of {FACTION}; you can ask {NPC.gender.object_pronoun} about this at {NPC_SCENE}."
    CUSTOM_REPLY = "What are you going to do about {FACTION}?"
    CUSTOM_OFFER = "People in town expect me to get rid of them, and that's what I'm going to do. I happen to know the current whereabouts of their commander."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="get rid of you", objective_ep="keep you busy",
        win_ep="you fell for our trap",
        lose_ep="I bombed the {METROSCENE} Militia headquarters"
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job.tags.intersection((gears.tags.Police,gears.tags.Politician)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_JustThwackThem(DZREPR_BaseMission):
    LABEL = "DZRE_ACE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_ACE: DZRE_ACE_UNKNOWN, E_TOWN: DZRE_TOWN_AGAINST}
    CHANGES = {E_ACE: DZRE_ACE_ZEUSCANNON}
    MISSION_NAME = "Just Fight Them"
    MISSION_PROMPT = "Attack the camp occupied by {FACTION}"
    OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES,missionbuilder.BAMO_CAPTURE_BUILDINGS)
    WIN_MESSAGE = "As the battle ends, news comes in over the comms that {METROSCENE} has been hit by artillery fire. Clearly, {FACTION} have an ace up their sleeve."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        win_pp="I captured your base",win_ep="I bombed {METROSCENE}",
        lose_ep="you failed to capture our base"
    )

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and npc not in camp.party:
            goffs.append(Offer(
                msg="Everybody knows that {FACTION} has a camp in a [deadzone_residence] just [direction] of here. I don't understand why we can't simply attack them there.".format(**self.elements ),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": str(self.elements["FACTION"])}, subject="go and fight {FACTION}".format(**self.elements), no_repeats=True
            ))
        return goffs

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("someone should just go and fight {FACTION}".format(**self.elements))
        return mygram


class DZREPR_TheConflictIntensifies(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST, E_TOWN: DZRE_TOWN_AGAINST}
    CHANGES = {E_TOWN: DZRE_TOWN_AFRAID}
    MISSION_NAME = "The Conflict Intensifies"
    MISSION_PROMPT = "Strike {FACTION} for {NPC}"
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER,missionbuilder.BAMO_LOCATE_ENEMY_FORCES)
    WIN_MESSAGE = ""
    DEFAULT_NEWS = "{FACTION} are planning to take over {METROSCENE} but {NPC} has a plan to stop them"
    DEFAULT_INFO = "Maybe {NPC} will have a mission for you? You can find {NPC.gender.object_pronoun} at {NPC_SCENE}."
    DEFAULT_MEMO = "{NPC} is organizing defense against {FACTION}; you can ask {NPC.gender.object_pronoun} about this at {NPC_SCENE}."
    CUSTOM_REPLY = "Do you have a plan to defeat {FACTION}?"
    CUSTOM_OFFER = "Not exactly. The {METROSCENE} militia is overwhelmed; the most we can do right now is try to keep them at bay with the few resources we have available. The situation doesn't look good. We could use all the help we can get."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="stop you from attacking {METROSCENE}", objective_ep="attack {METROSCENE}",
        win_pp="I stopped you from attacking {METROSCENE}", win_ep="you delayed my plans for {METROSCENE}",
        lose_ep="you failed to stop me"
    )
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
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="recover the trucks you stole", objective_ep="rob this place blind",
        win_pp="I put a halt to your crime spree", win_ep="you interfered with my banditry",
    )

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

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not npc.combatant and not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("{FACTION} has been abducting travelers coming into or leaving {METROSCENE}".format(**self.elements))
        return mygram


class DZREPR_HuntingForSecretBase(DZREPR_NPCMission):
    LABEL = "DZRE_ACE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_ACE: DZRE_ACE_HIDDENBASE, E_TOWN: DZRE_TOWN_AGAINST}
    CHANGES = {E_TOWN: DZRE_TOWN_AFRAID}
    MISSION_NAME = "Hunting for Secret Base"
    MISSION_PROMPT = "Join {NPC}'s search for the hidden base"
    OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES,missionbuilder.BAMO_EXTRACT_ALLIED_FORCES)
    WIN_MESSAGE = "The patrol sent by {NPC} didn't turn up anything. This failure is sure to raise tensions in {METROSCENE}."
    DEFAULT_NEWS = "{NPC} is organizing a patrol to find the hidden base belonging to {FACTION}"
    DEFAULT_INFO = "If you want to join {NPC}'s mission, you can find {NPC.gender.object_pronoun} at {NPC_SCENE}."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} is organizing a mission to locate the hidden base belonging to {FACTION}."
    CUSTOM_REPLY = "I heard that you're looking for {FACTION}."
    CUSTOM_OFFER = "People in town are starting to get nervous because it seems like {FACTION} can strike from anywhere. I've dispatched search parties to try and find their hidden base; you can join them, if you have time."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="locate your base", objective_ep="stop you",
        win_ep="you tried in vain to find our base",
        lose_pp="I couldn't find your base", lose_ep="you failed to find our base"
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job.tags.intersection((gears.tags.Military,gears.tags.Politician)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_JustMakeThemGoAway(DZREPR_NPCMission):
    LABEL = "DZRE_ACE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_ACE: DZRE_ACE_ZEUSCANNON, E_TOWN: DZRE_TOWN_AGAINST}
    CHANGES = {E_TOWN: DZRE_TOWN_AFRAID}
    MISSION_NAME = "Just Make Them Go Away"
    MISSION_PROMPT = "Attempt to destroy {FACTION}'s formidable artillery"
    OBJECTIVES = (missionbuilder.BAMO_DESTROY_ARTILLERY,missionbuilder.BAMO_NEUTRALIZE_ALL_DRONES)
    WIN_MESSAGE = ""
    DEFAULT_NEWS = "{NPC} needs to do something about {FACTION}; we've been living in fear of their cannons for too long"
    DEFAULT_INFO = "You should go to {NPC_SCENE} and convince {NPC.gender.object_pronoun} to authorize a strike against {FACTION}. We've tried doing noting but that isn't working."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} should do something about {FACTION}'s artillery."
    CUSTOM_REPLY = "Do you have a plan for dealing with {FACTION}'s artillery?"
    CUSTOM_OFFER = "Every time we've attempted a strike, they've managed to shell {METROSCENE} in retaliation. It seems like our only hope is to disable their cannons one by one and pray the town isn't destroyed in the process. If you think you can do this, the job is yours."
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.job.tags.intersection((gears.tags.Military,gears.tags.Politician)) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_HiddenNoLonger(DZREPR_NPCMission):
    LABEL = "DZRE_ACE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_ACE: DZRE_ACE_HIDDENBASE, E_TOWN: DZRE_TOWN_AFRAID}
    CHANGES = {E_ACE: DZRE_ACE_ZEUSCANNON}
    MISSION_NAME = "Hidden No Longer"
    MISSION_PROMPT = "Launch a strike against {FACTION}'s hidden base"
    OBJECTIVES = (missionbuilder.BAMO_STORM_THE_CASTLE,)
    WIN_MESSAGE = "As the battle ends, news comes in over the comms that {METROSCENE} has been hit by artillery fire. Clearly, {FACTION} relocated their big guns shortly before you arrived."
    DEFAULT_NEWS = "{NPC} has been attempting to locate {FACTION}"
    DEFAULT_INFO = "Go to {NPC_SCENE} and ask {NPC.gender.object_pronoun} for a mission. I'm sure there'll be a big reward for whoever finds the hidden base."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} is attempting to locate {FACTION}."
    CUSTOM_REPLY = "[HELLO:MISSION]"
    CUSTOM_OFFER = "I've been trying to find {FACTION}'s hidden base, and I think we are closing in on them. I can offer you a big reward for blowing it off the map."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="destroy your base", objective_ep="defend our base",
        win_pp="I destroyed your hidden base", win_ep="you destroyed our base",
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.combatant and nart.camp.are_faction_allies(candidate,self.elements["METROSCENE"]) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_JustifiedParanoia(DZREPR_BaseMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_PROFIT, E_TOWN: DZRE_TOWN_AFRAID}
    CHANGES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST}
    MISSION_NAME = "Justified Paranoia"
    MISSION_PROMPT = "Check for suspicious activity by {FACTION} near {METROSCENE}"
    OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES,missionbuilder.BAMO_DEFEAT_ARMY)
    WIN_MESSAGE = "Given the amount of firepower {FACTION} have deployed, the suspicions of the townsfolk seem justified. This is clearly more than a simple raiding operation."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="keep you from causing trouble", objective_ep="show {METROSCENE} its place",
    )

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and not npc.combatant and npc not in camp.party:
            goffs.append(Offer(
                msg="I know this is going to sound paranoid, but I don't think they're just here to raid the highways. I've heard they have a huge number of mecha just [direction] of town. Maybe {FACTION} is getting ready to take over.".format(**self.elements ),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": "the weird stuff"}, subject="{FACTION} has been doing some weird stuff".format(**self.elements), no_repeats=True
            ))
        return goffs

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not npc.combatant and not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("{FACTION} has been doing some weird stuff near {METROSCENE}".format(**self.elements))
        return mygram


class DZREPR_HowitzerShotFirst(DZREPR_NPCMission):
    LABEL = "DZRE_ACE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_ACE: DZRE_ACE_ZEUSCANNON, E_TOWN: DZRE_TOWN_NEUTRAL}
    CHANGES = {E_TOWN: DZRE_TOWN_AGAINST}
    MISSION_NAME = "Howitzer Shot First"
    MISSION_PROMPT = "Help {METROSCENE} scouts to withdraw so artillery can fire on {FACTION}'s base"
    OBJECTIVES = (missionbuilder.BAMO_EXTRACT_ALLIED_FORCES,missionbuilder.BAMO_SURVIVE_THE_AMBUSH)
    WIN_MESSAGE = "As you withdraw from the battlefield, you hear the mighty cannons of {METROSCENE} shelling {FACTION}. Moments later, the enemy begins to return fire. From your position it's not clear which side is winning this encounter."
    DEFAULT_NEWS = "{FACTION} are no match against {NPC}'s artillery"
    DEFAULT_INFO = "Go to {NPC_SCENE} and ask {NPC.gender.object_pronoun} for a mission."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} is defending {METROSCENE} against {FACTION}."
    CUSTOM_REPLY = "[HELLO:MISSION]"
    CUSTOM_OFFER = "So far we haven't had to worry much about {FACTION} since {METROSCENE} has enough firepower to keep them well outside of town. Lately, though, they've been getting bolder. I sent some scouts to locate their main base; I need you to extract those scouts so we can start shelling the enemy."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="clear this area",
        win_ep="you helped {NPC} find our base",
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.combatant and nart.camp.are_faction_allies(candidate,self.elements["METROSCENE"]) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_FallingStarSponsorship(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_ACE"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST, E_ACE: DZRE_ACE_ZEUSCANNON}
    CHANGES = {E_ACE: DZRE_ACE_SPONSOR}
    MISSION_NAME = "A Falling Star"
    MISSION_PROMPT = "Investigate the site where {NPC} saw the falling star."
    OBJECTIVES = (dd_customobjectives.DDBAMO_INVESTIGATE_METEOR,)
    DEFAULT_NEWS = "{NPC} said {NPC.gender.subject_pronoun} saw a meteor land outside of town"
    DEFAULT_INFO = "You can go to {NPC_SCENE} and ask {NPC.gender.object_pronoun} about it. I'm sure {NPC.gender.subject_pronoun} will be overjoyed that someone is interested."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} saw something land outside of town."
    CUSTOM_REPLY = "Did I hear you saw a falling star last night?"
    CUSTOM_OFFER = "Yes, I did! Nobody wants to talk about it because of all the drama with {FACTION}, but I'm quite sure it landed just outside of town. I'd go looking for it myself if I had a mecha."
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and not candidate.combatant and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_InspireTheMilitia(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST, E_TOWN: DZRE_TOWN_AFRAID}
    CHANGES = {E_TOWN: DZRE_TOWN_INSPIRED}
    MISSION_NAME = "A New Hope?"
    MISSION_PROMPT = "Help the {METROSCENE} militia to turn back {FACTION}."
    OBJECTIVES = (missionbuilder.BAMO_AID_ALLIED_FORCES,missionbuilder.BAMO_DEFEAT_COMMANDER)
    DEFAULT_NEWS = "{FACTION} are beginning their final invasion; {NPC} is trying to fight them but it's hopeless"
    DEFAULT_INFO = "You can go to {NPC_SCENE} and ask {NPC.gender.object_pronoun} about it. Maybe with your help it wouldn't be so hopeless?"
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} is coordinating defense against {FACTION}."
    CUSTOM_REPLY = "[HELLO:MISSION]"
    CUSTOM_OFFER = "It's clear that {FACTION} are closing in on us. The militia has lost too many good pilots already. With your help maybe we can hold them back for just one more day... or maybe not."
    WIN_MESSAGE = "With {FACTION} driven back, the people of {METROSCENE} regain their will to fight."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="banish you", objective_ep="take over {METROSCENE}",
        win_pp="I banished you from {METROSCENE}", win_ep="you drove me from {METROSCENE}",
        lose_ep="I decimated the {METROSCENE} Militia"
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and nart.camp.are_faction_allies(candidate,self.elements["METROSCENE"]) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_AngryAtSponsorship(DZREPR_BaseMission):
    LABEL = "DZRE_ACE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_ACE: DZRE_ACE_SPONSOR, E_TOWN: DZRE_TOWN_NEUTRAL}
    CHANGES = {E_TOWN: DZRE_TOWN_AGAINST}
    MISSION_NAME = "Knock Them Down"
    MISSION_PROMPT = "Go demonstrate to {FACTION} that they don't own {METROSCENE}"
    OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES,missionbuilder.BAMO_DEFEAT_COMMANDER)
    WIN_MESSAGE = "That'll show them."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="show you that {METROSCENE} will never give in", objective_ep="break {METROSCENE}",
        win_ep="you inspired {METROSCENE} to stand against me",
    )

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and not npc.combatant and npc not in camp.party:
            goffs.append(Offer(
                msg="[THEYAREOURENEMY] They think that just because they're strong, they can do what they like in {METROSCENE}. I say it's time to knock them down a peg.".format(**self.elements ),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": "{FACTION}'s attitude".format(**self.elements),
                      "they": str(self.elements["FACTION"])},
                subject="{FACTION} have been acting like they own".format(**self.elements), no_repeats=True
            ))
        return goffs

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not npc.combatant and not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("{FACTION} have been acting like they own {METROSCENE}".format(**self.elements))
        return mygram


class DZREPR_OldNewYork(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_ACE"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST, E_ACE: DZRE_ACE_UNKNOWN}
    CHANGES = {E_ACE: DZRE_ACE_HIDDENBASE}
    MISSION_NAME = "Going Underground"
    MISSION_PROMPT = "Explore the ruins around {METROSCENE} to search for {FACTION}"
    MISSION_ARCHITECTURE = gharchitecture.MechaScaleRuins
    OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES,missionbuilder.BAMO_DEFEAT_COMMANDER)
    DEFAULT_NEWS = "{NPC} has a theory about why {FACTION} are so hard to find"
    DEFAULT_INFO = "Go ask {NPC.gender.object_pronoun} about it at {NPC_SCENE}."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} has a theory about {FACTION}."
    CUSTOM_REPLY = "What do you think about {FACTION}?"
    CUSTOM_OFFER = "Well, they're definitely getting resupplied from somewhere, and no-one has been able to figure out where their main base is. The land around here used to be a PreZero megacity. I think they've found one of the big underground sections, and that's where they're hiding out."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="find and defeat you",
        win_ep="you invaded our underground domain",
        lose_ep="you tried to invade our underground domain"
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.combatant and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])

class DZREPR_FearOfTheInvaders(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST, E_TOWN: DZRE_TOWN_NEUTRAL}
    CHANGES = {E_TOWN: DZRE_TOWN_AFRAID}
    MISSION_NAME = "A New Hope?"
    MISSION_PROMPT = "Help the {METROSCENE} militia to turn back {FACTION}."
    OBJECTIVES = (missionbuilder.BAMO_AID_ALLIED_FORCES,missionbuilder.BAMO_DEFEAT_COMMANDER)
    DEFAULT_NEWS = "{FACTION} are beginning their final invasion; {NPC} is trying to fight them but it's hopeless"
    DEFAULT_INFO = "You can go to {NPC_SCENE} and ask {NPC.gender.object_pronoun} about it. Maybe with your help it wouldn't be so hopeless?"
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} is coordinating defense against {FACTION}."
    CUSTOM_REPLY = "[HELLO:MISSION]"
    CUSTOM_OFFER = "It's clear that {FACTION} are closing in on us. The militia has lost too many good pilots already. With your help maybe we can hold them back for just one more day... or maybe not."
    WIN_MESSAGE = "With {FACTION} driven back, the people of {METROSCENE} regain their will to fight."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="support the {METROSCENE} militia", objective_ep="destroy the {METROSCENE} militia",
        win_pp="I helped the {METROSCENE} militia to defeat you", win_ep="you and the {METROSCENE} militia defeated me",
        lose_ep="I defeated you and the {METROSCENE} militia combined"
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and nart.camp.are_faction_allies(candidate,self.elements["METROSCENE"]) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])

class DZREPR_FOTIBountyHunt(DZREPR_BaseMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST, E_TOWN: DZRE_TOWN_NEUTRAL}
    CHANGES = {E_TOWN: DZRE_TOWN_AGAINST}
    MISSION_NAME = "Bounty Hunting"
    MISSION_PROMPT = "Search for {FACTION} and try to collect that bounty"
    OBJECTIVES = (missionbuilder.BAMO_SURVIVE_THE_AMBUSH,missionbuilder.BAMO_DEFEAT_ARMY)
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="collect the bounty on you",
    )

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and not npc.combatant and npc not in camp.party:
            goffs.append(Offer(
                msg="Whatever they're up to, I'm sure it's dreadful. The leaders of {METROSCENE} have offered a bounty for anyone who can defeat {FACTION}, but I doubt it's going to do any good.".format(**self.elements ),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": "{FACTION}'s plans".format(**self.elements)}, subject="{FACTION} has in store".format(**self.elements), no_repeats=True
            ))
        return goffs

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not npc.combatant and not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("nobody knows what {FACTION} has in store for {METROSCENE}".format(**self.elements))
        return mygram


class DZREPR_StealTheirThunder(DZREPR_NPCMission):
    LABEL = "DZRE_ACE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_ACE: DZRE_ACE_ZEUSCANNON, E_TOWN: DZRE_TOWN_AFRAID}
    CHANGES = {E_TOWN: DZRE_TOWN_INSPIRED}
    MISSION_NAME = "Steal Their Thunder"
    MISSION_PROMPT = "Help the {METROSCENE} militia to destroy {FACTION}'s artillery"
    OBJECTIVES = (missionbuilder.BAMO_AID_ALLIED_FORCES,missionbuilder.BAMO_DESTROY_ARTILLERY)
    DEFAULT_NEWS = "{NPC}'s attempt to destroy {FACTION}'s artillery isn't going well"
    DEFAULT_INFO = "You can go to {NPC_SCENE} and ask {NPC.gender.object_pronoun} about it. Between you and me {NPC.gender.subject_pronoun} could use some reinforcements."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} is attempting to destroy {FACTION}'s artillery."
    CUSTOM_REPLY = "How is the fight against {FACTION} going?"
    CUSTOM_OFFER = "Terrible; {FACTION} has been able to outmaneuver us at every turn. I sent the militia to disable their artillery, thinking that would help to even the odds. Unfortunately, their base is better guarded than I expected, and we're losing the battle. If you would be willing to aid us..."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="disable your artillery", objective_ep="bomb you into the dust",
        win_pp="I destroyed your artillery", win_ep="you blew up my big guns",
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.combatant and nart.camp.are_faction_allies(candidate,self.elements["METROSCENE"]) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_GoneToGround(DZREPR_NPCMission):
    LABEL = "DZRE_ACE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_ACE: DZRE_ACE_UNKNOWN, E_TOWN: DZRE_TOWN_INSPIRED}
    CHANGES = {E_ACE: DZRE_ACE_HIDDENBASE}
    MISSION_NAME = "Gone To Ground"
    MISSION_PROMPT = "Patrol the highway around {METROSCENE} for {FACTION} strike teams"
    OBJECTIVES = (missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL,missionbuilder.BAMO_LOCATE_ENEMY_FORCES)
    DEFAULT_NEWS = "{NPC} is leading the fight to wipe out {FACTION} once and for all"
    DEFAULT_INFO = "{NPC.gender.subject_pronoun} is at {NPC_SCENE}."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} is leading the fight to wipe out {FACTION}."
    CUSTOM_REPLY = "How is the fight against {FACTION} going?"
    CUSTOM_OFFER = "Due to our recent victories, {FACTION} have gone to ground. Instead of operating in broad daylight they've been reduced to petty raiding along the highway. Still, they remain a threat to {METROSCENE}. I want you to go patrol the area for them. Make sure they aren't causing any trouble."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="hunt you down",
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.combatant and nart.camp.are_faction_allies(candidate,self.elements["METROSCENE"]) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])


class DZREPR_TheyWantItBad(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST, E_TOWN: DZRE_TOWN_INSPIRED}
    CHANGES = {E_MOTIVE: DZRE_MOTIVE_TREASURE}
    MISSION_NAME = "Seeking Secrets"
    MISSION_PROMPT = "Explore the ruins for {FACTION} activity"
    MISSION_ARCHITECTURE = gharchitecture.MechaScaleRuins
    OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES,missionbuilder.BAMO_CAPTURE_BUILDINGS)
    WIN_MESSAGE = "A quick search of the encampment confirms that {FACTION} are searching the ruins for something, though you still don't know exactly what."
    DEFAULT_NEWS = "{NPC} has a theory for why {FACTION} are still sticking around"
    DEFAULT_INFO = "You can go to {NPC_SCENE} and ask {NPC.gender.object_pronoun} about it."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} has a theory about {FACTION}."
    CUSTOM_REPLY = "What is your theory about {FACTION}?"
    CUSTOM_OFFER = "Everyone always thought that {FACTION} was trying to invade {METROSCENE}; if that were true, they would have packed up and left once it became obvious that wasn't going to happen. I think they're searching the ruins around town for some kind of hidden treasure or lost technology."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="stop whatever you're planning", objective_ep="capture the hidden treasure",
        win_pp="I stopped your treasure hunt", win_ep="you interfered in my treasure hunt",
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and nart.camp.are_faction_allies(candidate,self.elements["METROSCENE"]) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])

class DZREPR_UndergroundConstruction(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_ACE"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST, E_ACE: DZRE_ACE_HIDDENBASE}
    CHANGES = {E_ACE: DZRE_ACE_ZEUSCANNON}
    MISSION_NAME = "Underground Construction"
    MISSION_PROMPT = "Explore the ruins for {FACTION}'s hidden base"
    MISSION_ARCHITECTURE = gharchitecture.MechaScaleRuins
    OBJECTIVES = (missionbuilder.BAMO_CAPTURE_THE_MINE,missionbuilder.BAMO_DESTROY_ARTILLERY)
    WIN_MESSAGE = "You have disabled this production center belonging to {FACTION}, but who knows how much artillery they have already produced?"
    DEFAULT_NEWS = "{NPC} thinks {FACTION} are up to something in their base"
    DEFAULT_INFO = "Just go to {NPC_SCENE} and ask {NPC.gender.object_pronoun} about {FACTION}; maybe you can get a mission out of it."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} believes {FACTION} are up to something."
    CUSTOM_REPLY = "What do you think {FACTION} are doing?"
    CUSTOM_OFFER = "Based on their history of raids, it seems like {FACTION} are building something big. In PreZero times this was an industrial area; it's possible they've found some autofac equipment in the ruins and have gotten it back online."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="find your base", objective_ep="build some new toys",
        win_pp="I captured your underground base", win_ep="you ruined my factory",
        lose_ep="you couldn't stop me from building artillery"
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and nart.camp.are_faction_allies(candidate,self.elements["METROSCENE"]) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])

class DZREPR_TheSponsorWantsSomething(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_ACE"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_CONQUEST, E_ACE: DZRE_ACE_SPONSOR}
    CHANGES = {E_MOTIVE: DZRE_MOTIVE_TREASURE}
    MISSION_NAME = "Sponsor Message"
    MISSION_PROMPT = "Deliver a message to {FACTION}'s bosses from {METROSCENE}"
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_ARMY,missionbuilder.BAMO_CAPTURE_BUILDINGS)
    DEFAULT_NEWS = "{NPC} wants to send {FACTION} a message"
    DEFAULT_INFO = "I think you're just the sort of person to deliver this message... go to {NPC_SCENE} and ask {NPC} for a mission."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} wants to send {FACTION} a message."
    CUSTOM_REPLY = "I hear you have a message for {FACTION}."
    CUSTOM_OFFER = "It's obvious that the forces providing {FACTION} with equipment want more than just to take over {METROSCENE}. They're probably searching for PreZero treasure, maybe something to do with the biomonsters that have been showing up lately. Well, I want you to send them a message- whatever they're up to, we aren't going to let them do it."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="send you a message", objective_ep="test our new equipment",
        win_ep="you blew up my new mecha",
        lose_ep="my new mecha made short work of you"
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and nart.camp.are_faction_allies(candidate,self.elements["METROSCENE"]) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])

class DZREPR_LegendaryTreasure(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_PROFIT, E_TOWN: DZRE_TOWN_AGAINST}
    CHANGES = {E_MOTIVE: DZRE_MOTIVE_TREASURE}
    MISSION_NAME = "Legendary Treasure"
    MISSION_PROMPT = "Protect {METROSCENE}'s legendary treasure from {FACTION}"
    OBJECTIVES = (missionbuilder.BAMO_CAPTURE_THE_MINE,missionbuilder.BAMO_CAPTURE_BUILDINGS)
    WIN_MESSAGE = "It's pretty clear that whatever the legendary treasure is, {FACTION} didn't find it here. Hopefully there is still time to beat them to it."
    DEFAULT_NEWS = "{NPC} says {FACTION} are after our treasure"
    DEFAULT_INFO = "I don't know why {FACTION} would be after anything we have in {METROSCENE}; it never did us any good. But you can go ask {NPC} about it at {NPC_SCENE}."
    DEFAULT_MEMO = "{NPC} at {NPC_SCENE} says {FACTION} are after {METROSCENE}'s legendary treasure."
    CUSTOM_REPLY = "What do you think {FACTION} are looking for?"
    CUSTOM_OFFER = "Isn't it obvious? Legends say that there is an ancient treasure buried in the ruins beneath {METROSCENE}. Some think it's a miraculous supercomputer, while others believe it's a biomonster of unbelievable power. Whatever it is, {FACTION} have been hunting high and low to find it!"
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="protect {METROSCENE}", objective_ep="pillage {METROSCENE}",
        win_ep="you interfered with my search for {METROSCENE}'s legendary treasure",
        lose_pp="I couldn't protect {METROSCENE}", lose_ep="you failed to protect {METROSCENE}"
    )
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and not candidate.combatant and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])

class DZREPR_HelpFromAbove(DZREPR_NPCMission):
    LABEL = "DZRE_MOTIVE_ACE"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_TREASURE, E_ACE: DZRE_ACE_UNKNOWN}
    CHANGES = {E_ACE: DZRE_ACE_SPONSOR}
    MISSION_NAME = "Unidentified Falling Object"
    MISSION_PROMPT = "Investigate the spot where {NPC} got the strange readings."
    OBJECTIVES = (missionbuilder.BAMO_SURVIVE_THE_AMBUSH,dd_customobjectives.DDBAMO_INVESTIGATE_METEOR,)
    WIN_MESSAGE = "As the smoke clears from the battlefield, one thing becomes clear: there are some powerful forces that want {FACTION} to find whatever it is they're looking for."
    DEFAULT_NEWS = "{NPC} said {NPC.gender.subject_pronoun} saw something weird last night"
    DEFAULT_INFO = "You can go to {NPC_SCENE} and ask {NPC.gender.object_pronoun} about it."
    DEFAULT_MEMO = "{NPC} is at {NPC_SCENE}, if you want to ask {NPC.gender.object_pronoun} about the mysterious thing {NPC.gender.subject_pronoun} saw."
    CUSTOM_REPLY = "Have you seen anything odd recently?"
    CUSTOM_OFFER = "As a matter of fact, I did. While I was out last night my mecha's sensors picked up a large flying object just outside of town. It was only on screen for a second, then it disappeared. I thought I saw something falling in the distance but I was too slow to take a video with my phone."
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.combatant and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])

class DZREPR_SleepingGiant(DZREPR_BaseMission):
    LABEL = "DZRE_MOTIVE_TOWN"
    #LABEL = "DZRE_TEST"
    REQUIRES = {E_MOTIVE: DZRE_MOTIVE_TREASURE, E_TOWN: DZRE_TOWN_AGAINST}
    CHANGES = {E_TOWN: DZRE_TOWN_AFRAID}
    MISSION_NAME = "Sleeping Giants"
    MISSION_PROMPT = "Try to prevent {FACTION} from unleashing anything locked in the ruins"
    OBJECTIVES = (missionbuilder.BAMO_LOCATE_ENEMY_FORCES,missionbuilder.BAMO_DEFEAT_ARMY)
    MISSION_ARCHITECTURE = gharchitecture.MechaScaleRuins
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="stop you from making a big mistake", objective_ep="unleash ultimate power",
        win_ep="you denied me the ultimate power source",
        lose_pp="I couldn't stop you",
    )

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and not npc.combatant and npc not in camp.party:
            goffs.append(Offer(
                msg="I know that every deadzone town has a legend like this, but our elders used to say that there's something extremely dangerous locked down under there. I hate to think what would happen if {FACTION} find it.".format(**self.elements ),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": "the undercity".format(**self.elements)}, subject="the {METROSCENE} undercity".format(**self.elements), no_repeats=True
            ))
        return goffs

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not npc.combatant and not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("they say {FACTION} has been searching the {METROSCENE} undercity".format(**self.elements))
        return mygram


#   *******************************************
#   ***   ROAD  EDGE  RATCHET  CONCLUSION   ***
#   *******************************************


class DZREPRC_CallOutBattle(DZREPRC_ConclusionTemplate):
    # Will activate the adventure when property mission_active set to True
    # Required Elements: METRO, METROSCENE, MISSION_GATE, FACTION
    LABEL = "DZRE_CONCLUSION"
    MISSION_NAME = "Ultimate Challenge"
    MISSION_PROMPT = "Go meet {FACTION}'s challenge."
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER,missionbuilder.BAMO_DEFEAT_ARMY)
    WIN_MESSAGE = "With their leaders defeated and their mecha forces destroyed, {FACTION} cease to be a danger to travelers in the dead zone."
    DEFAULT_MEMO = "You learned that {FACTION} are waiting just outside of {METROSCENE} to challenge you to a final battle."
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="end this", objective_ep="defeat you",
        win_pp="I utterly defeated you",
    )

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and npc not in camp.party:
            goffs.append(Offer(
                msg="You've caused a lot of trouble for {FACTION}, so they've mobilized all of their forces in {METROSCENE} to finish you off once and for all.".format(**self.elements ),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": "this challenge"}, subject="{FACTION} have challenged".format(**self.elements),
                no_repeats=True
            ))
        return goffs

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("{FACTION} have challenged you to one final battle".format(**self.elements))
            mygram["[HELLO_AGAIN]"].append("What are you doing here, [audience]?! Didn't you hear that {FACTION} have challenged you to one final battle?".format(**self.elements))
            mygram["[HELLO_FIRST]"].append(
                "You're [audience], aren't you? [chat_lead_in] {FACTION} have challenged you to one final battle.".format(**self.elements)
            )
        return mygram


class DZREPC_CallOutChampionFight(DZREPRC_ConclusionTemplate):
    LABEL = "DZRE_CONCLUSION"
    #LABEL = "DZRE_TEST"
    MISSION_NAME = "Duel Between Champions"
    MISSION_PROMPT = "Go meet {FACTION}'s champion, alone, for a duel."
    OBJECTIVES = (dd_customobjectives.DDBAMO_CHAMPION_1V1,)
    WIN_MESSAGE = "With their champion defeated, {FACTION} scatters, no longer a danger to travelers in the dead zone."
    DEFAULT_MEMO = "You learned that {FACTION}'s champion is waiting just outside of {METROSCENE} to challenge you to a final duel."
    SOLO_MISSION = True

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.mission_active and npc not in camp.party:
            goffs.append(Offer(
                msg="You've caused a lot of trouble for {FACTION}, so they've chosen a champion in {METROSCENE} to challenge you in single mecha combat.".format(**self.elements ),
                context=ContextTag((context.INFO,)), effect=self.activate_mission,
                data={"subject": "this challenge"}, subject="{FACTION} have challenged".format(**self.elements),
                no_repeats=True
            ))
        return goffs

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if not self.mission_active and npc not in camp.party:
            mygram["[News]"].append("{FACTION} have challenged you to one final duel".format(**self.elements))
            mygram["[HELLO_AGAIN]"].append("What are you doing here, [audience]?! Didn't you hear that {FACTION} have challenged you to a one-on-one duel against their champion?".format(**self.elements))
            mygram["[HELLO_FIRST]"].append(
                "You're [audience], aren't you? [chat_lead_in] {FACTION} have challenged you to a one-on-one duel against their champion.".format(**self.elements)
            )
        return mygram


class DZREPRC_RazeTheFortress(DZREPRC_ConclusionTemplate):
    # Will activate the adventure when property mission_active set to True
    # Required Elements: METRO, METROSCENE, MISSION_GATE, FACTION
    LABEL = "DZRE_CONCLUSION"
    MISSION_NAME = "Storm the Castle"
    MISSION_PROMPT = "Launch an assault against {FACTION}'s fortress."
    OBJECTIVES = (missionbuilder.BAMO_DEFEAT_COMMANDER,missionbuilder.BAMO_STORM_THE_CASTLE)
    WIN_MESSAGE = "With their leader defeated and their stronghold destroyed, {FACTION} cease to be a danger to travelers in the dead zone."
    LOSS_MESSAGE = ""
    DEFAULT_MEMO = "You now know the location of {FACTION}'s base.'"
    REQUIRES = {E_ACE: DZRE_ACE_HIDDENBASE}
    MISSION_GRAMMAR = missionbuilder.MissionGrammar(
        objective_pp="destroy your fortress", objective_ep="defend our fortress",
        win_pp="I destroyed your fortress", win_ep="you destroyed my fortress",
    )

    def custom_init(self, nart):
        super().custom_init(nart)
        if not self.LABEL == "DZRE_TEST":
            mynpc = self.seek_element(nart, "NPC", self._npc_matches, scope=self.elements["METROSCENE"])
            npcscene = self.register_element("NPC_SCENE",mynpc.container.owner)
        else:
            self.register_element("NPC",gears.selector.random_character())
            self.register_element("NPC_SCENE", self.elements["METROSCENE"])
        return True
    def _npc_matches(self,nart,candidate):
        return isinstance(candidate,gears.base.Character) and candidate.combatant and nart.camp.are_faction_allies(candidate,self.elements["METROSCENE"]) and candidate not in nart.camp.party and not nart.camp.are_faction_allies(candidate,self.elements["FACTION"])
    def t_UPDATE(self,camp):
        if not self.elements["NPC"].is_not_destroyed():
            self.activate_mission(camp)
        super().t_UPDATE(camp)
    def NPC_offers(self, camp):
        mylist = list()
        if not self.mission_active:
            mylist.append(Offer("[audience], I was hoping to find you. We have finally discovered the location of {FACTION}'s base.".format(**self.elements),
                            context=ContextTag((context.HELLO,)), no_repeats=True
                            ))
            mylist.append(Offer("You are authorized to attack immediately. If we can disable their base, we can stop their operation dead in its tracks. [IWillSendMissionDetails]".format(**self.elements),
                            context=ContextTag((context.CUSTOM,)), effect=self.activate_mission,
                            data={"reply": "When do we attack {FACTION}?".format(**self.elements)},
                            no_repeats=True
                            ))
        return mylist
    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if npc is not self.elements["NPC"] and not self.mission_active:
            mygram["[News]"].append("{NPC} at {NPC_SCENE} has been looking for you".format(**self.elements))
        return mygram



#   ***************************************
#   ***   ROAD  EDGE  RATCHET  SETUPS   ***
#   ***************************************
#
# The base plot that launches the initial missions and eventually sends a win signal to the roadedge plot.
# Mostly, what this plot has to do is provide backstory and set the start_mission property to True.

#   ******************************
#   ***   DZRE_BanditProblem   ***
#   ******************************

class DZREPR_PrettyStandardBandits(DZREPR_BasePlot):
    LABEL = "DZRE_BanditProblem"

    STARTING_MOTIVE = DZRE_MOTIVE_PROFIT

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if npc not in camp.party and not self.start_missions:
            mygram["[News]"].append("{FACTION} have been robbing travelers from {METROSCENE}".format(**self.elements))
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.start_missions and npc not in camp.party and not camp.are_faction_allies(npc,self.elements["FACTION"]):
            goffs.append(Offer(
                msg="[THEYARETHIEVES] They work the highway between here and {}, taking what they can from who they can.".format(self.elements["DZ_EDGE"].get_city_link(self.elements["METROSCENE"])),
                context=ContextTag((context.INFO,)), effect=self._get_briefed,
                subject=str(self.elements["FACTION"]),
                data={"subject": str(self.elements["FACTION"]),"they":str(self.elements["FACTION"])}, no_repeats=True
            ))
        return goffs

    def _get_briefed(self,camp):
        self.start_missions = True
        camp.check_trigger("UPDATE")
        self.memo = "You learned that {} have been robbing travelers near {}.".format(self.elements["FACTION"],self.elements["METROSCENE"])


class DZREPR_HiddenBandits(DZREPR_BasePlot):
    LABEL = "DZRE_BanditProblem"

    STARTING_ACE = DZRE_ACE_HIDDENBASE

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if npc not in camp.party and not self.start_missions:
            mygram["[News]"].append("nobody knows much about {FACTION}, except that they can seemingly strike from nowhere ".format(**self.elements))
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.start_missions and npc not in camp.party and not camp.are_faction_allies(npc,self.elements["FACTION"]):
            goffs.append(Offer(
                msg="[THEYAREAMYSTERY] They've been raiding between here and {} but nobody knows where their base is.".format(self.elements["DZ_EDGE"].get_city_link(self.elements["METROSCENE"])),
                context=ContextTag((context.INFO,)), effect=self._get_briefed,
                subject=str(self.elements["FACTION"]),
                data={"subject": str(self.elements["FACTION"]),"they":str(self.elements["FACTION"])}, no_repeats=True
            ))
        return goffs

    def _get_briefed(self,camp):
        self.start_missions = True
        camp.check_trigger("UPDATE")
        self.memo = "You learned that {} must have have a hidden base near {}.".format(self.elements["FACTION"],self.elements["METROSCENE"])


class DZREPR_ToleratedBandits(DZREPR_BasePlot):
    LABEL = "DZRE_BanditProblem"
    UNIQUE = True

    STARTING_MOTIVE = DZRE_MOTIVE_PROFIT

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if npc not in camp.party and not self.start_missions:
            mygram["[News]"].append("{} have been raiding convoys between here and {}".format(self.elements["FACTION"],self.elements["DZ_EDGE"].get_city_link(self.elements["METROSCENE"])))
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.start_missions and npc not in camp.party and not camp.are_faction_allies(npc,self.elements["FACTION"]):
            goffs.append(Offer(
                msg="The dead zone has always been full of bandits; {FACTION} may be a big deal now, but in time they will fade away or get taken out by a bigger gang.".format(**self.elements),
                context=ContextTag((context.INFO,)), effect=self._get_briefed,
                subject=str(self.elements["FACTION"]),
                data={"subject": str(self.elements["FACTION"]),"they":str(self.elements["FACTION"])}, no_repeats=True
            ))
        return goffs

    def _get_briefed(self,camp):
        self.start_missions = True
        camp.check_trigger("UPDATE")
        self.memo = "You learned that {} have been raiding convoys near {}.".format(self.elements["FACTION"],self.elements["METROSCENE"])


class DZREPR_DislikedBandits(DZREPR_BasePlot):
    LABEL = "DZRE_BanditProblem"

    STARTING_MOTIVE = DZRE_MOTIVE_UNKNOWN
    STARTING_ACE = DZRE_ACE_UNKNOWN
    STARTING_TOWN = DZRE_TOWN_AGAINST

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if npc not in camp.party and not self.start_missions:
            mygram["[News]"].append("{FACTION} have been causing a lot of problems in {METROSCENE}".format(**self.elements))
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.start_missions and npc not in camp.party and not camp.are_faction_allies(npc,self.elements["FACTION"]):
            goffs.append(Offer(
                msg="[THEYAREOURENEMY] It's because of their raids that we can't trade freely with {}.".format(self.elements["DZ_EDGE"].get_city_link(self.elements["METROSCENE"])),
                context=ContextTag((context.INFO,)), effect=self._get_briefed,
                subject=str(self.elements["FACTION"]),
                data={"subject": str(self.elements["FACTION"]),"they":str(self.elements["FACTION"])}, no_repeats=True
            ))
        return goffs

    def _get_briefed(self,camp):
        self.start_missions = True
        camp.check_trigger("UPDATE")
        self.memo = "You learned that {} have been causing trouble in {}.".format(self.elements["FACTION"],self.elements["METROSCENE"])


class DZREPR_NewBanditsWhoThis(DZREPR_BasePlot):
    LABEL = "DZRE_BanditProblem"
    UNIQUE = True

    def custom_init(self, nart):
        super(DZREPR_NewBanditsWhoThis,self).custom_init(nart)

        # Add a trucker to town.
        myscene = self.elements["METROSCENE"]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene, must_find=False)
        if not destscene:
            destscene = self.seek_element(nart, "_DEST", self._is_good_scene, scope=myscene)

        mynpc = self.register_element(
            "NPC", gears.selector.random_character(
                job=gears.jobs.ALL_JOBS["Trucker"], rank=random.randint(self.rank-10,self.rank+20),
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

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"] and not self.got_rumor:
            mygram["[News]"].append("the trucker {} lost {} convoy on the way into town.".format(self.elements["NPC"],self.elements["NPC"].gender.possessive_determiner))
        if camp.scene.get_root_scene() is self.elements["METROSCENE"] and not self.start_missions:
            mygram["[News]"].append("there never used to be bandits between here and {} in the past".format(self.elements["DZ_EDGE"].get_city_link(self.elements["METROSCENE"])))
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.got_rumor and camp.scene.get_root_scene() is self.elements["METROSCENE"] and npc is not self.elements["NPC"]:
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
        self.memo = Memo( "{} is a trucker who lost {} convoy.".format(mynpc,mynpc.gender.possessive_determiner)
                        , self.elements["_DEST"]
                        )

    def NPC_offers(self, camp):
        mylist = list()

        if not self.start_missions:
            mylist.append(Offer("[HELLO] While bringing in a convoy from {}, I got attacked by bandits and lost everything.".format(self.elements["DZ_EDGE"].get_city_link(self.elements["METROSCENE"])),
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
        self.memo = "You learned that {} must have a base near {}.".format(self.elements["FACTION"],self.elements["METROSCENE"])

    def _join_lance(self, camp):
        npc = self.elements["NPC"]
        npc.relationship.tags.add(gears.relationships.RT_LANCEMATE)
        self.offered_services = True
        if camp.can_add_lancemate():
            effect = game.content.plotutility.AutoJoiner(npc)
            effect(camp)

#   ******************************
#   ***   DZRE_InvaderProblem   ***
#   ******************************

class DZREPR_PrettyStandardInvaders(DZREPR_BasePlot):
    LABEL = "DZRE_InvaderProblem"

    STARTING_MOTIVE = DZRE_MOTIVE_CONQUEST

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        if npc not in camp.party and not self.start_missions:
            mygram["[News]"].append("{FACTION} have been trying to establish a stronghold nearby".format(**self.elements))
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.start_missions and npc not in camp.party and not camp.are_faction_allies(npc,self.elements["FACTION"]):
            goffs.append(Offer(
                msg="[THEYAREOURENEMY] They want to take over this area, but we will fight them to the last.",
                context=ContextTag((context.INFO,)), effect=self._get_briefed,
                subject=str(self.elements["FACTION"]),
                data={"subject": str(self.elements["FACTION"]),"they":str(self.elements["FACTION"])}, no_repeats=True
            ))
        return goffs

    def _get_briefed(self,camp):
        self.start_missions = True
        camp.check_trigger("UPDATE")
        self.memo = "You learned that {} are trying to establish a stronghold near {}.".format(self.elements["FACTION"],self.elements["METROSCENE"])


def _typecheck():
    """ Make sure there is no mixup i.e. E_ACE: E_MOTIVE_CONQUEST
    """
    def get_all_subclasses(cls):
        yield cls
        for sc in cls.__subclasses__():
            for sc in get_all_subclasses(sc):
                yield sc
    def keys_correct(cname, pname, d):
        for k in d.keys():
            v = d[k]
            if not v:
                continue
            desc = "{}.{}: '{}' has invalid '{}'".format(cname, pname, k, v)
            if k == E_MOTIVE:
                assert "DZRE_EGOAL_" in v or "DZRE_MOTIVE_" in v, desc
            elif k == E_ACE:
                assert "DZRE_ACE_" in v, desc
            elif k == E_TOWN:
                assert "DZRE_TOWN_" in v, desc
            else:
                # invalid key!
                assert False, "{}.{}: invalid '{}'".format(cname, pname, k)
    def label_correct(cname, label, requires):
        desc = "{}.LABEL = {}: invalid {}".format(cname, label, requires)
        if label == "DZRE_TEST":
            # for testing
            return
        elif label == "DZRE_MOTIVE_ACE_TOWN":
            assert E_MOTIVE in requires and E_ACE in requires and E_TOWN in requires, desc
        elif label == "DZRE_MOTIVE_ACE":
            assert E_MOTIVE in requires and E_ACE in requires and E_TOWN not in requires, desc
        elif label == "DZRE_ACE_TOWN":
            assert E_MOTIVE not in requires and E_ACE in requires and E_TOWN in requires, desc
        elif label == "DZRE_MOTIVE_TOWN":
            assert E_MOTIVE in requires and E_ACE not in requires and E_TOWN in requires, desc
        else:
            assert False, "{}.LABEL = invalid {}".format(cname, label)
    for c in get_all_subclasses(DZREPR_BaseMission):
        # Ensure correctness.
        keys_correct(c.__name__, 'REQUIRES', c.REQUIRES)
        keys_correct(c.__name__, 'CHANGES', c.CHANGES)
        label_correct(c.__name__, c.LABEL, c.REQUIRES)
        for k in c.CHANGES.keys():
            assert k in c.REQUIRES, "{}.CHANGES: key {} not in .REQUIRES".format(c.__name__, k)

_typecheck()
