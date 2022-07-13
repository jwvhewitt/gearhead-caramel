import pbge.memos
from pbge.plots import Plot, PlotState, Rumor
import game.content.ghwaypoints
import game.content.ghterrain
import gears
import pbge
from game import teams, ghdialogue
from game.content import gharchitecture
from game.ghdialogue import context
import random
from pbge.dialogue import ContextTag, Offer
from game.content.ghplots import dd_main
from game.content import plotutility
import game.content.gharchitecture
from . import missionbuilder
import collections

Memo = pbge.memos.Memo


#  **************************
#  ***   ADD_BORING_NPC   ***
#  **************************

class BoringRandomNPC(Plot):
    LABEL = "ADD_BORING_NPC"

    def custom_init(self, nart):
        npc = gears.selector.random_character(local_tags=tuple(self.elements["METROSCENE"].attributes))
        self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])
        self.register_element("NPC", npc, dident="LOCALE")
        return True

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


#  *****************************
#  ***   ADD_COMBATANT_NPC   ***
#  *****************************

class FightingRandomNPC(Plot):
    LABEL = "ADD_COMBATANT_NPC"

    def custom_init(self, nart):
        npc = gears.selector.random_character(combatant=True, local_tags=tuple(self.elements["METROSCENE"].attributes))
        self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])
        self.register_element("NPC", npc, dident="LOCALE")
        return True

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


#  *************************************
#  ***   ADD_INSTANT_EGG_LANCEMATE   ***
#  *************************************
#   Add a lancemate from the Egg directly to the party.

class BasicEggLancemate(Plot):
    # Try to load this plot last in the scenario construction because it may attempt to grab a major NPC needed
    # elsewhere.
    LABEL = "ADD_INSTANT_EGG_LANCEMATE"

    def custom_init(self, nart):
        npc = nart.camp.egg.seek_dramatis_person(nart.camp, self._is_good_npc, self)
        if npc:
            plotutility.AutoJoiner(npc)(nart.camp)
        return True

    def _is_good_npc(self, nart, candidate):
        return isinstance(candidate,
                          gears.base.Character) and candidate.relationship and gears.relationships.RT_LANCEMATE in candidate.relationship.tags


#  ********************************
#  ***   ADD_PERSON_TO_LOCALE   ***
#  ********************************
# This is roughly the equivalent of GH2's *CIVILIAN plot. Add a person to the scene passed as LOCALE. Usually
# the person will be an unassuming civilian, but maybe not?

class ThisIsAPersonInYourNeighborhood(Plot):
    LABEL = "ADD_PERSON_TO_LOCALE"

    def custom_init(self, nart):
        npc = gears.selector.random_character(local_tags=tuple(self.elements["METROSCENE"].attributes))
        if "LOCALE" not in self.elements:
            self.seek_element(nart, "LOCALE", self._is_best_scene, scope=self.elements["METROSCENE"])
        self.register_element("NPC", npc, dident="LOCALE")
        return True

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


#  *****************************
#  ***   ADD_REMOTE_OFFICE   ***
#  *****************************
#
#   We want to add some NPCs to this location, but we don't want them to be directly accessible to the PC.
#   This sticks the NPCs in a subscene that can't normally be accessed, but provides a method for providing
#   access later if you want.
#
#  FACTION: The Faction to add a remote office for

class BoringRemoteOffice(Plot):
    LABEL = "ADD_REMOTE_OFFICE"
    active = False

    def custom_init(self, nart):
        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, "{} Base".format(self.elements["FACTION"]), player_team=team1,
                                       civilian_team=team2, scale=gears.scale.HumanScale,
                                       faction=self.elements["FACTION"])
        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.DefaultBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR")

        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south, ),
                                      dident="INTERIOR")
        foyer.contents.append(team2)
        # Add the NPCs.
        if self.rank > 25 and random.randint(1, 3) != 1:
            job = self.elements["FACTION"].choose_job(gears.tags.Commander)
        elif random.randint(1, 3) == 1:
            job = self.elements["FACTION"].choose_job(gears.tags.Support)
        elif random.randint(1, 20) != 17:
            job = self.elements["FACTION"].choose_job(gears.tags.Trooper)
        else:
            job = random.choice(list(gears.jobs.ALL_JOBS.values()))
        team2.contents.append(
            gears.selector.random_character(self.rank + 10, job=job, combatant=True, faction=self.elements["FACTION"]))

        return True


#  ********************************
#  ***   ADD_FROZEN_COMBATANT   ***
#  ********************************
#
#   We want to add a frozen faction member to this adventure, presumably so we'll have someone to show up in random
#   combats and whatever. This frozen member will start frozen and remain frozen until called forth by some other
#   plot.
#
#  FACTION: The Faction to add a frozen member for. May be "None".

class BasicFrozenMember(Plot):
    LABEL = "ADD_FROZEN_COMBATANT"

    def custom_init(self, nart):
        npc = None

        # Check the PC's egg for an appropriate NPC; returning allies and/or arch-enemies are cool.
        if random.randint(1, 6) != 5:
            npc = nart.camp.egg.seek_dramatis_person(nart.camp, self._is_good_npc, self)
            if npc and npc.job and self.rank > (npc.renown - 10):
                npc.job.scale_skills(npc, self.rank + 10)

        # Add the NPC.
        if not npc:
            if self.elements["FACTION"]:
                if self.rank > 25 and random.randint(1, 3) != 1:
                    job = self.elements["FACTION"].choose_job(gears.tags.Commander)
                elif random.randint(1, 3) == 1:
                    job = self.elements["FACTION"].choose_job(gears.tags.Support)
                elif random.randint(1, 20) != 17:
                    job = self.elements["FACTION"].choose_job(gears.tags.Trooper)
                else:
                    job = random.choice(list(gears.jobs.ALL_JOBS.values()))
            else:
                job = random.choice(list(gears.jobs.ALL_JOBS.values()))
            npc = gears.selector.random_character(self.rank + 10, job=job, combatant=True,
                                                  faction=self.elements["FACTION"])
        nart.camp.freeze(npc)
        return True

    def _is_good_npc(self, camp, npc):
        return isinstance(npc, gears.base.Character) and npc.combatant and npc.faction == self.elements["FACTION"]


#  *************************************
#  ***   ENSURE_JOB_REPRESENTATION   ***
#  *************************************
#
#   Make sure there's always at least one NPC with the given job in town. Always.
#
#  JOB: The job to ensure
#  METROSCENE: The city to add the character to
#  METRO: The METRO data block for the city
#

class EnsureJobHaver(Plot):
    LABEL = "ENSURE_JOB_REPRESENTATION"
    scope = "METRO"
    active = True

    def custom_init(self, nart):
        myscene = self.elements["METROSCENE"]
        myjob = self.elements["JOB"]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene)
        mynpc = self.register_element("NPC", gears.selector.random_character(
            rank=self.rank, local_tags=myscene.attributes, job=myjob,
        ), dident="_DEST")
        destscene.local_teams[mynpc] = destscene.civilian_team
        return True

    def METROSCENE_ENTER(self, camp):
        # Perform the check upon entering the city.
        if not self.member_is_present(camp):
            # Create and deploy a new NPC.
            myscene = self.elements["METROSCENE"]
            mydest = self.elements["_DEST"]
            mynpc = gears.selector.random_character(rank=random.randint(1, 50),
                                                    job=self.elements["JOB"], local_tags=myscene.attributes)
            mynpc.place(mydest, team=mydest.civilian_team)

    def member_is_present(self, camp):
        scope = self.elements["METROSCENE"]
        for e in camp.all_contents(scope, True):
            if isinstance(e, gears.base.Character) and str(self.elements["JOB"]) == str(e.job):
                return True

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


#  ***************************************
#  ***   ENSURE_LOCAL_REPRESENTATION   ***
#  ***************************************
#
#   Make sure there's always at least one member of the provided faction in town. Always.
#
#  FACTION: The Faction to add
#  METROSCENE: The city to add the character to
#  METRO: The METRO data block for the city
#

class EnsureAMember(Plot):
    LABEL = "ENSURE_LOCAL_REPRESENTATION"
    scope = "METRO"
    active = True

    def custom_init(self, nart):
        myscene = self.elements["METROSCENE"]
        myfac = self.elements["FACTION"]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene, must_find=False)
        if not destscene:
            destscene = self.seek_element(nart, "_DEST", self._is_good_scene, scope=myscene)
        myjob = myfac.choose_job(gears.tags.Commander)
        mynpc = self.register_element("NPC", gears.selector.random_character(rank=random.randint(50, 80), job=myjob,
                                                                             local_tags=myscene.attributes,
                                                                             combatant=True, faction=myfac),
                                      dident="_DEST")
        destscene.local_teams[mynpc] = destscene.civilian_team
        return True

    def METROSCENE_ENTER(self, camp):
        # Perform the check upon entering the city.
        if not self.member_is_present(camp):
            # Create and deploy a new NPC.
            myscene = self.elements["METROSCENE"]
            mydest = self.elements["_DEST"]
            mynpc = gears.selector.random_character(rank=random.randint(50, 80),
                                                    local_tags=myscene.attributes, combatant=True,
                                                    faction=self.elements["FACTION"])
            mynpc.place(mydest, team=mydest.civilian_team)

    def member_is_present(self, camp):
        scope = self.elements["METROSCENE"]
        for e in camp.all_contents(scope, True):
            if isinstance(e, gears.base.Character) and e.faction is self.elements["FACTION"]:
                return True

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and
                gears.tags.SCENE_BASE in candidate.attributes and
                candidate.faction and nart.camp.are_faction_allies(candidate.faction, self.elements["FACTION"]))

    def _is_good_scene(self, nart, candidate):
        return isinstance(candidate, pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


#  ***************************************
#  ***   ENSURE_TRAIT_REPRESENTATION   ***
#  ***************************************
#
#   Make sure there's always at least one NPC with the given personality trait in town. Always.
#
#  TRAIT: The trait to ensure
#  METROSCENE: The city to add the character to
#  METRO: The METRO data block for the city
#

class EnsureOneTraitHaver(Plot):
    LABEL = "ENSURE_TRAIT_REPRESENTATION"
    scope = "METRO"
    active = True

    def custom_init(self, nart):
        myscene = self.elements["METROSCENE"]
        mytrait = self.elements["TRAIT"]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene)
        if not destscene:
            destscene = self.seek_element(nart, "_DEST", self._is_good_scene, scope=myscene)
        mynpc = self.register_element("NPC", gears.selector.random_character(
            rank=self.rank, local_tags=myscene.attributes,
        ), dident="_DEST")
        mynpc.personality.add(mytrait)
        destscene.local_teams[mynpc] = destscene.civilian_team
        return True

    def METROSCENE_ENTER(self, camp):
        # Perform the check upon entering the city.
        if not self.member_is_present(camp):
            # Create and deploy a new NPC.
            myscene = self.elements["METROSCENE"]
            mydest = self.elements["_DEST"]
            mynpc = gears.selector.random_character(rank=random.randint(1, 50),
                                                    local_tags=myscene.attributes)
            mynpc.personality.add(self.elements["TRAIT"])
            mynpc.place(mydest, team=mydest.civilian_team)

    def member_is_present(self, camp):
        scope = self.elements["METROSCENE"]
        for e in camp.all_contents(scope, True):
            if isinstance(e, gears.base.Character) and self.elements["TRAIT"] in e.personality:
                return True

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


#  ************************
#  ***   NPC_VACATION   ***
#  ************************
# Freeze the provided NPC for a number of days, then bring them back.
# Call the "freeze_now" method to start the vacation.
#  NPC: The NPC to be frozen
#  DAYS: The number of days to be frozen. Defaults to 5.

class NPCVacationToTheFreezer(Plot):
    LABEL = "NPC_VACATION"
    active = False
    scope = "LOCALE"

    def custom_init(self, nart):
        npc = self.elements["NPC"]
        self.elements["LOCALE"] = npc.scene
        self.vacation_end = 0
        self.frozen = False
        return True

    def freeze_now(self, camp: gears.GearHeadCampaign):
        camp.freeze(self.elements["NPC"])
        self.frozen = True
        self.vacation_end = camp.day + self.elements.get("DAYS", 5)
        self.activate(camp)

    def t_START(self, camp: gears.GearHeadCampaign):
        if self.frozen and camp.day >= self.vacation_end:
            npc = self.elements["NPC"]
            locale = self.elements["LOCALE"]
            npc.place(locale)
            self.end_plot(camp)


#  ***************************************
#  ***   PLACE_LOCAL_REPRESENTATIVES   ***
#  ***************************************
#
#  LOCALE: The city/neighborhood in which the commander will be placed
#  FACTION: The faction to which the new NPCs will belong.

class PlaceACommander(Plot):
    LABEL = "PLACE_LOCAL_REPRESENTATIVES"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements["FACTION"]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene,
                                      backup_seek_func=self._is_good_scene)
        myjob = myfac.choose_job(gears.tags.Commander)
        mynpc = self.register_element("NPC", gears.selector.random_character(rank=random.randint(50, 80), job=myjob,
                                                                             local_tags=myscene.attributes,
                                                                             combatant=True, faction=myfac),
                                      dident="_DEST")
        destscene.local_teams[mynpc] = destscene.civilian_team
        return True

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and
                gears.tags.SCENE_BASE in candidate.attributes and
                candidate.faction and nart.camp.are_faction_allies(candidate.faction, self.elements["FACTION"]))

    def _is_good_scene(self, nart, candidate):
        return isinstance(candidate, pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


class PlaceAMember(Plot):
    LABEL = "PLACE_LOCAL_REPRESENTATIVES"

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        myfac = self.elements["FACTION"]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene,
                                      backup_seek_func=self._is_good_scene)
        mynpc = self.register_element("NPC", gears.selector.random_character(
            rank=random.randint(20, 70), local_tags=myscene.attributes, combatant=True, faction=myfac), dident="_DEST"
                                      )
        destscene.local_teams[mynpc] = destscene.civilian_team
        return True

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and
                gears.tags.SCENE_BASE in candidate.attributes and
                candidate.faction and nart.camp.are_faction_allies(candidate.faction, self.elements["FACTION"]))

    def _is_good_scene(self, nart, candidate):
        return isinstance(candidate, pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


#   **************************
#   ***  POST_PLOT_REWARD  ***
#   **************************
#
# Sometimes you want to end a plot but also you want to give the player a reward. This is an extra plot that will allow
# the reward to be given.
#
# Needed Elements: NPC, PC_REPLY

class PostPlotReward(Plot):
    LABEL = "POST_PLOT_REWARD"
    active = True
    scope = True

    def custom_init(self, nart):
        self.reward = gears.selector.calc_mission_reward(self.rank, random.randint(100,300))
        self.memo = Memo("You helped {NPC} at {NPC.scene}".format(**self.elements), self.elements["NPC"].scene)
        return True

    def NPC_offers(self, camp):
        mylist = list()

        mylist.append(Offer(
            "[THANKS_FOR_HELP] Here's a reward of ${:,} for your actions.".format(self.reward),
            ContextTag([context.CUSTOM,]), data={"reply": self.elements["PC_REPLY"]},
            effect=self.get_reward
        ))

        return mylist

    def get_reward(self, camp: gears.GearHeadCampaign):
        camp.credits += self.reward
        self.elements["NPC"].relationship.reaction_mod += 10
        self.end_plot(camp, True)

    def t_UPDATE(self, camp):
        # If this NPC dies, no reward. :(
        if not self.elements["NPC"].is_operational():
            self.end_plot(camp, True)


#  ************************
#  ***   QOL_REPORTER   ***
#  ************************

class QualityOfLifeReporter(Plot):
    # Provide CURRENT_EVENT
    LABEL = "QOL_REPORTER"
    active = True
    scope = "METRO"

    def _get_dialogue_grammar(self, npc, camp):
        mygram = collections.defaultdict(list)
        qol: gears.QualityOfLife = self.elements["METRO"].get_quality_of_life()
        mygram["[metroscene]"].append(str(self.elements["METROSCENE"]))
        if qol.prosperity > 0:
            mygram["[CURRENT_EVENTS]"].append("[QOL_PROSPERITY_UP]")
        elif qol.prosperity < 0:
            mygram["[CURRENT_EVENTS]"].append("[QOL_PROSPERITY_DOWN]")

        if qol.community > 0:
            mygram["[CURRENT_EVENTS]"].append("[QOL_COMMUNITY_UP]")
        elif qol.community < 0:
            mygram["[CURRENT_EVENTS]"].append("[QOL_COMMUNITY_DOWN]")

        if qol.stability > 0:
            mygram["[CURRENT_EVENTS]"].append("[QOL_STABILITY_UP]")
        elif qol.stability < 0:
            mygram["[CURRENT_EVENTS]"].append("[QOL_STABILITY_DOWN]")

        if qol.health > 0:
            mygram["[CURRENT_EVENTS]"].append("[QOL_HEALTH_UP]")
        elif qol.health < 0:
            mygram["[CURRENT_EVENTS]"].append("[QOL_HEALTH_DOWN]")

        if qol.defense > 0:
            mygram["[CURRENT_EVENTS]"].append("[QOL_DEFENSE_UP]")
        elif qol.defense < 0:
            mygram["[CURRENT_EVENTS]"].append("[QOL_DEFENSE_DOWN]")

        return mygram


#  ***************************
#  ***   REVEAL_LOCATION   ***
#  ***************************
#
#  METROSCENE: The city where the reveal will take place.
#  LOCALE: The location to be revealed.
#  INTERESTING_POINT: A sentence describing what's interesting about the location.

class EverybodyKnows(Plot):
    # Everybody but you, that is.
    LABEL = "REVEAL_LOCATION"
    active = True
    scope = "METRO"

    def _get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        mygram["[News]"] = ["there's something unusual at {LOCALE}".format(**self.elements)]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        goffs.append(Offer(
            msg="There's always been a bit of a mystery about {LOCALE}. {INTERESTING_POINT}".format(**self.elements),
            context=ContextTag((context.INFO,)), effect=self._get_rumor,
            subject=str(self.elements["LOCALE"]), data={"subject": str(self.elements["LOCALE"])}, no_repeats=True
        ))
        return goffs

    def _get_rumor(self, camp):
        camp.check_trigger("WIN", self)
        missionbuilder.NewLocationNotification(self.elements["LOCALE"], self.elements["MISSION_GATE"])
        self.end_plot(camp)


class TruckerKnowledge(Plot):
    LABEL = "REVEAL_LOCATION"
    active = True
    scope = "METRO"

    RUMOR = Rumor(
        "{NPC} saw something unusual outside of town",
        offer_msg="You can ask {NPC} about that; {NPC}'s usually at {_DEST}.",
        memo="{NPC} saw something unusual outside of town.", memo_location="_DEST",
        prohibited_npcs=("NPC",), offer_subject_data="what {NPC} saw"
    )

    def custom_init(self, nart):
        myscene = self.elements["METROSCENE"]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene, must_find=False)
        if not destscene:
            destscene = self.seek_element(nart, "_DEST", self._is_good_scene, scope=myscene)
        mynpc = self.register_element(
            "NPC", gears.selector.random_character(rank=random.randint(10, 50), job=gears.jobs.ALL_JOBS["Trucker"],
                                                   local_tags=myscene.attributes), dident="_DEST"
        )
        destscene.local_teams[mynpc] = destscene.civilian_team
        self.got_rumor = False
        return True

    def _is_best_scene(self, nart, candidate):
        return (isinstance(candidate, pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and
                gears.tags.SCENE_TRANSPORT in candidate.attributes)

    def _is_good_scene(self, nart, candidate):
        return isinstance(candidate, pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def NPC_offers(self, camp):
        mylist = list()
        mylist.append(Offer(
            msg="[HELLO] During my last trip into town I saw something really strange out there...",
            context=ContextTag((context.HELLO,)),
        ))
        mylist.append(Offer(
            msg="I was driving through {LOCALE}, like I usually do. {INTERESTING_POINT}".format(**self.elements),
            context=ContextTag((context.INFO,)), effect=self._get_info,
            data={"subject": "what you saw outside of town"}, no_repeats=True
        ))

        return mylist

    def _get_info(self, camp):
        camp.check_trigger("WIN", self)
        missionbuilder.NewLocationNotification(self.elements["LOCALE"], self.elements["MISSION_GATE"])
        self.end_plot(camp)
