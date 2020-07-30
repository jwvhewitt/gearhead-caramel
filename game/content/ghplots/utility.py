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
from game.content.ghplots import dd_main
import game.content.plotutility
import game.content.gharchitecture
from . import missionbuilder
import collections


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

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


#  *****************************Town Hall
#  ***   ADD_REMOTE_OFFICE   ***
#  *****************************
#
#   We want to add some NPCs to this location, but we don't want them to be directly accessible to the PC.
#   This sticks the NPCs in a subscene that can't normally be accessed, but provides a method for providing
#   access later if you want.
#
#  FACTION: The Faction to add a remote office for

class BoringRemoteOffice( Plot ):
    LABEL = "ADD_REMOTE_OFFICE"
    active = False
    def custom_init( self, nart ):
        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, "{} Base".format(self.elements["FACTION"]), player_team=team1,
                                       civilian_team=team2, scale=gears.scale.HumanScale, faction=self.elements["FACTION"])
        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.DefaultBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR")

        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,),
                                    dident="INTERIOR")
        foyer.contents.append(team2)
        # Add the NPCs.
        if self.rank > 25 and random.randint(1,3) != 1:
            job = self.elements["FACTION"].choose_job(gears.tags.Commander)
        elif random.randint(1,3) == 1:
            job = self.elements["FACTION"].choose_job(gears.tags.Support)
        elif random.randint(1,20) != 17:
            job = self.elements["FACTION"].choose_job(gears.tags.Trooper)
        else:
            job = random.choice(list(gears.jobs.ALL_JOBS.values()))
        team2.contents.append(gears.selector.random_character(self.rank+10,job=job,combatant=True,faction=self.elements["FACTION"]))

        return True


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

class EnsureJobHaver( Plot ):
    LABEL = "ENSURE_JOB_REPRESENTATION"
    scope = "METRO"
    active = True
    def custom_init( self, nart ):
        myscene = self.elements["METROSCENE"]
        myjob = self.elements["JOB"]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene )
        mynpc = self.register_element("NPC",gears.selector.random_character(
            rank=self.rank, local_tags=myscene.attributes, job=myjob,
        ),dident="_DEST")
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
            mynpc.place(mydest,team=mydest.civilian_team)

    def member_is_present(self,camp):
        scope = self.elements["METROSCENE"]
        for e in camp.all_contents( scope, True ):
            if isinstance(e,gears.base.Character) and str(self.elements["JOB"]) == str(e.job):
                return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes



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

class EnsureAMember( Plot ):
    LABEL = "ENSURE_LOCAL_REPRESENTATION"
    scope = "METRO"
    active = True
    def custom_init( self, nart ):
        myscene = self.elements["METROSCENE"]
        myfac = self.elements["FACTION"]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene, must_find=False)
        if not destscene:
            destscene = self.seek_element(nart, "_DEST", self._is_good_scene, scope=myscene)
        myjob = myfac.choose_job(gears.tags.Commander)
        mynpc = self.register_element("NPC",gears.selector.random_character(rank=random.randint(50,80),job=myjob,local_tags=myscene.attributes,combatant=True,faction=myfac),dident="_DEST")
        destscene.local_teams[mynpc] = destscene.civilian_team
        return True

    def METROSCENE_ENTER(self, camp):
        # Perform the check upon entering the city.
        if not self.member_is_present(camp):
            # Create and deploy a new NPC.
            myscene = self.elements["METROSCENE"]
            mydest = self.elements["_DEST"]
            mynpc = gears.selector.random_character(rank=random.randint(50, 80),
                 local_tags=myscene.attributes, combatant=True, faction=self.elements["FACTION"])
            mynpc.place(mydest,team=mydest.civilian_team)

    def member_is_present(self,camp):
        scope = self.elements["METROSCENE"]
        for e in camp.all_contents( scope, True ):
            if isinstance(e,gears.base.Character) and e.faction is self.elements["FACTION"]:
                return True

    def _is_best_scene(self,nart,candidate):
        return (isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and
                gears.tags.SCENE_BASE in candidate.attributes and
                candidate.faction and nart.camp.are_ally_factions(candidate.faction,self.elements["FACTION"]))

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


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

class EnsureOneTraitHaver( Plot ):
    LABEL = "ENSURE_TRAIT_REPRESENTATION"
    scope = "METRO"
    active = True
    def custom_init( self, nart ):
        myscene = self.elements["METROSCENE"]
        mytrait = self.elements["TRAIT"]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene )
        if not destscene:
            destscene = self.seek_element(nart, "_DEST", self._is_good_scene, scope=myscene)
        mynpc = self.register_element("NPC",gears.selector.random_character(
            rank=self.rank, local_tags=myscene.attributes,
        ),dident="_DEST")
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
            mynpc.place(mydest,team=mydest.civilian_team)

    def member_is_present(self,camp):
        scope = self.elements["METROSCENE"]
        for e in camp.all_contents( scope, True ):
            if isinstance(e,gears.base.Character) and self.elements["TRAIT"] in e.personality:
                return True

    def _is_best_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes



#  ***************************************
#  ***   PLACE_LOCAL_REPRESENTATIVES   ***
#  ***************************************
#
#  FACTION: The faction to which the new NPCs will belong.

class PlaceACommander( Plot ):
    LABEL = "PLACE_LOCAL_REPRESENTATIVES"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        myfac = self.elements["FACTION"]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene, must_find=False)
        if not destscene:
            destscene = self.seek_element(nart, "_DEST", self._is_good_scene, scope=myscene)
        myjob = myfac.choose_job(gears.tags.Commander)
        mynpc = self.register_element("NPC",gears.selector.random_character(rank=random.randint(50,80),job=myjob,local_tags=myscene.attributes,combatant=True,faction=myfac),dident="_DEST")
        destscene.local_teams[mynpc] = destscene.civilian_team
        return True
    def _is_best_scene(self,nart,candidate):
        return (isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and
                gears.tags.SCENE_BASE in candidate.attributes and
                candidate.faction and nart.camp.are_ally_factions(candidate.faction,self.elements["FACTION"]))
    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes


#  ************************
#  ***   QOL_REPORTER   ***
#  ************************

class QualityOfLifeReporter(Plot):
    # Provide CURRENT_EVENT
    LABEL = "QOL_REPORTER"
    active = True
    scope = "METRO"

    def get_dialogue_grammar(self, npc, camp):
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

class EverybodyKnows( Plot ):
    # Everybody but you, that is.
    LABEL = "REVEAL_LOCATION"
    active = True
    scope = "METRO"
    def get_dialogue_grammar(self, npc, camp):
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

    def _get_rumor(self,camp):
        camp.check_trigger("WIN", self)
        missionbuilder.NewLocationNotification(self.elements["LOCALE"],self.elements["MISSION_GATE"])
        self.end_plot(camp)


class TruckerKnowledge( Plot ):
    LABEL = "REVEAL_LOCATION"
    active = True
    scope = "METRO"
    def custom_init( self, nart ):
        myscene = self.elements["METROSCENE"]
        destscene = self.seek_element(nart, "_DEST", self._is_best_scene, scope=myscene, must_find=False)
        if not destscene:
            destscene = self.seek_element(nart, "_DEST", self._is_good_scene, scope=myscene)
        mynpc = self.register_element(
            "NPC",gears.selector.random_character(rank=random.randint(10,50),job=gears.jobs.ALL_JOBS["Trucker"],
            local_tags=myscene.attributes), dident="_DEST"
        )
        destscene.local_teams[mynpc] = destscene.civilian_team
        self.got_rumor = False
        return True
    def _is_best_scene(self,nart,candidate):
        return (isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes and
                gears.tags.SCENE_TRANSPORT in candidate.attributes)
    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.Scene) and gears.tags.SCENE_PUBLIC in candidate.attributes
    def get_dialogue_grammar(self, npc, camp):
        mygram = dict()
        if npc is not self.elements["NPC"] and not self.got_rumor:
            mygram["[News]"] = ["{NPC} saw something unusual outside of town".format(**self.elements)]
        return mygram

    def _get_generic_offers(self, npc, camp):
        """Get any offers that could apply to non-element NPCs."""
        goffs = list()
        if not self.got_rumor and npc is not self.elements["NPC"]:
            mynpc = self.elements["NPC"]
            goffs.append(Offer(
                msg="You can ask {} about that; {}'s usually at {}.".format(mynpc,mynpc.gender.subject_pronoun,self.elements["_DEST"]),
                context=ContextTag((context.INFO,)), effect=self._get_rumor,
                subject=str(mynpc), data={"subject": "what {} saw".format(mynpc)}, no_repeats=True
            ))
        return goffs

    def _get_rumor(self,camp):
        self.got_rumor = True
        self.memo = "{} at {} saw something unusual outside of town.".format(self.elements["NPC"],self.elements["_DEST"])

    def NPC_offers(self,camp):
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

    def _get_info(self,camp):
        camp.check_trigger("WIN", self)
        missionbuilder.NewLocationNotification(self.elements["LOCALE"],self.elements["MISSION_GATE"])
        self.end_plot(camp)
