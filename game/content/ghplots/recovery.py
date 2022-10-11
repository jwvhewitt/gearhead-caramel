import gears
from pbge.plots import Plot, Adventure, NarrativeRequest, PlotState
import pbge
from game.content import plotutility
from game.content.ghcutscene import SimpleMonologueDisplay
import random

#  **********************
#  ***   RECOVER_PC   ***
#  **********************
#
#  Elements:
#   METRO: The local metro scene's metrodat, or camp if not applicable
#   METROSCENE: The scope for scene search

class PC_HospitalRecovery( Plot ):
    # The PC has been knocked out; recover everyone else and send the PC to the hospital.
    LABEL = "RECOVER_PC"
    active = True
    scope = True
    COMMON = True
    def custom_init( self, nart ):
        """Find a hospital, move the PC to there."""
        myscene = self.seek_element(nart,"HOSPITAL",self._is_good_scene,scope=self.elements["METROSCENE"], backup_seek_func=self._is_public_scene)
        myent = self.seek_element(nart,"BED",self._is_good_bed,scope=myscene,check_subscenes=False, backup_seek_func=self._is_any_waypoint)
        self.mission_entrance = myent
        self.started_mission = False
        self.plots_to_run = list()
        if nart.camp.dead_party:
            self.plots_to_run.append(self.add_sub_plot(nart,"RECOVER_DEAD_PARTY"))
        return True

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,gears.GearHeadScene) and gears.tags.SCENE_HOSPITAL in candidate.attributes

    def _is_public_scene(self,nart,candidate):
        return isinstance(candidate,gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def _is_good_bed(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.waypoints.Waypoint) and hasattr(candidate,"recovery_entrance") and candidate.recovery_entrance

    def _is_any_waypoint(self, nart, candidate):
        return isinstance(candidate,pbge.scenes.waypoints.Waypoint)

    def start_recovery(self,camp):
        """

        :type camp: gears.GearHeadCampaign
        """
        camp.go(self.mission_entrance)
        if not self.started_mission:
            if camp.pc in camp.incapacitated_party:
                camp.incapacitated_party.remove(camp.pc)
            elif camp.pc in camp.dead_party:
                camp.dead_party.remove(camp.pc)
            if camp.pc not in camp.party:
                camp.party.append(camp.pc)
            # If the PC was knocked out, all the lancemates recover/repair while the PC is being treated.
            for pc in list(camp.incapacitated_party):
                camp.incapacitated_party.remove(pc)
                camp.party.append(pc)
            for pc in camp.get_lancemates():
                if not camp.get_pc_mecha(pc):
                    mek = camp.get_backup_mek(pc)
                    if mek:
                        camp.assign_pilot_to_mecha(pc,mek)
                    else:
                        mek = plotutility.AutoJoiner.get_mecha_for_character(pc)
                        if mek:
                            camp.party.append(mek)
                            camp.assign_pilot_to_mecha(pc, mek)
                            for part in mek.get_all_parts():
                                part.owner = pc

            self.started_mission = True

    def HOSPITAL_ENTER(self, camp):
        pbge.alert("You wake up in the hospital.")

        for p in self.plots_to_run:
            p.start_recovery(camp)

        self.end_plot(camp)


#  *************************
#  ***   RECOVER_LANCE   ***
#  *************************
#
#  Elements:
#   METRO: The local metro scene's metrodat, or camp if not applicable
#   METROSCENE: The scope for scene search

class LanceRecoveryStub( Plot ):
    # This plot just loads the plots that do the actual work.
    LABEL = "RECOVER_LANCE"
    active = False
    def custom_init( self, nart ):
        self.plots_to_run = list()
        if nart.camp.dead_party:
            self.plots_to_run.append(self.add_sub_plot(nart,"RECOVER_DEAD_PARTY"))

        # Deal with dispossessed lancemates.
        for pc in [pc for pc in nart.camp.get_lancemates() if not nart.camp.get_pc_mecha(pc)]:
            mek = nart.camp.get_backup_mek(pc)
            if mek:
                nart.camp.assign_pilot_to_mecha(pc, mek)
            else:
                self.plots_to_run.append(self.add_sub_plot(nart,"LANCEMATE_NEEDS_MECHA",spstate=PlotState().based_on(self,{"NPC":pc})))

        # Deal with incapacitated lancemates.
        for pc in list(nart.camp.incapacitated_party):
            nart.camp.incapacitated_party.remove(pc)
            nart.camp.party.append(pc)
            myplot = self.add_sub_plot(nart,"LANCEMATE_NEEDS_HOSPITAL", elements={"NPC":pc}, necessary=False)
            if myplot:
                self.plots_to_run.append(myplot)

        return True

    def start_recovery(self,camp):
        for p in self.plots_to_run:
            p.start_recovery(camp)

#  *********************************
#  ***   LANCEMATE_NEEDS_MECHA   ***
#  *********************************
#
#   One of your lancemates has lost their mecha.
#
#  Elements:
#   METRO: The local metro scene's metrodat, or camp if not applicable
#   METROSCENE: The scope for scene search
#   NPC: The lancemate in question

class BeBackAfterShopping( Plot ):
    LABEL = "LANCEMATE_NEEDS_MECHA"
    COMMON = True
    def custom_init( self, nart ):
        myscene = self.seek_element(nart,"GARAGE",self._is_good_scene,scope=self.elements["METROSCENE"])
        return True

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,gears.GearHeadScene) and gears.tags.SCENE_GARAGE in candidate.attributes and gears.tags.SCENE_PUBLIC in candidate.attributes

    def start_recovery(self,camp):
        npc = self.elements["NPC"]
        garage = self.elements["GARAGE"]
        if npc.relationship:
            npc.relationship.reaction_mod -= random.randint(1,10)
        SimpleMonologueDisplay("[MY_MECHA_WAS_DESTROYED] I'm going to go to {} and get a new one.".format(garage),npc)(camp)
        if random.randint(1,10) == 1:
            # Random chance that instead of getting the same mecha, they'll look for a new kind.
            npc.mecha_pref = None
        plotutility.AutoLeaver(npc)(camp)
        npc.place(garage)


class UseTheBackupMek( Plot ):
    LABEL = "LANCEMATE_NEEDS_MECHA"
    def start_recovery(self,camp: gears.GearHeadCampaign):
        npc = self.elements["NPC"]
        npc.relationship = camp.get_relationship(npc)
        npc.relationship.reaction_mod -= random.randint(5, 20)
        npc.relationship.data["mecha_level_bonus"] = max(npc.relationship.data.get("mecha_level_bonus",0)-10, -25)
        npc.mecha_pref = None
        mek = plotutility.AutoJoiner.get_mecha_for_character(npc, True)
        SimpleMonologueDisplay("[MY_MECHA_WAS_DESTROYED] I guess I'm going to have to get my old {} out of storage.".
                               format(mek.get_full_name()), npc)(camp)
        plotutility.AutoJoiner.add_lancemate_mecha_to_party(camp, npc, mek)


class INeedAnUpgrade( Plot ):
    LABEL = "LANCEMATE_NEEDS_MECHA"
    @classmethod
    def matches( cla, pstate: PlotState ):
        lm = pstate.elements["NPC"]
        return lm.relationship and lm.relationship.can_do_development() and lm.relationship.data.get("mecha_level_bonus",0) < 50

    def custom_init( self, nart ):
        myscene = self.seek_element(nart,"GARAGE",self._is_good_scene,scope=self.elements["METROSCENE"])
        return True

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,gears.GearHeadScene) and gears.tags.SCENE_GARAGE in candidate.attributes and gears.tags.SCENE_PUBLIC in candidate.attributes

    def start_recovery(self,camp):
        npc = self.elements["NPC"]
        garage = self.elements["GARAGE"]
        SimpleMonologueDisplay("[TIME_TO_UPGRADE_MECHA] I'm going to {} to see what they have.".format(garage),npc)(camp)
        npc.relationship.development_plots += 1
        npc.relationship.data["mecha_level_bonus"] = npc.relationship.data.get("mecha_level_bonus",0)+10
        npc.mecha_pref = None
        plotutility.AutoLeaver(npc)(camp)
        npc.place(garage)


#  ************************************
#  ***   LANCEMATE_NEEDS_HOSPITAL   ***
#  ************************************
#
#   One of your lancemates has been seriously injured, and will probably have to spend some time in the hospital.
#
#  Elements:
#   METRO: The local metro scene's metrodat, or camp if not applicable
#   METROSCENE: The scope for scene search
#   NPC: The lancemate in question

class GoToHospital( Plot ):
    # This plot just loads the plots that do the actual work.
    LABEL = "LANCEMATE_NEEDS_HOSPITAL"
    COMMON = True

    def custom_init( self, nart ):
        myscene = self.seek_element(nart,"HOSPITAL",self._is_good_scene,scope=self.elements["METROSCENE"])
        return True

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,gears.GearHeadScene) and gears.tags.SCENE_HOSPITAL in candidate.attributes and gears.tags.SCENE_PUBLIC in candidate.attributes

    def start_recovery(self,camp):
        npc = self.elements["NPC"]
        hospital = self.elements["HOSPITAL"]
        pbge.alert("{} is rushed to {}.".format(npc,hospital))
        plotutility.AutoLeaver(npc)(camp)
        npc.place(hospital)


#  ******************************
#  ***   RECOVER_DEAD_PARTY   ***
#  ******************************
#
#  Elements:
#   METRO: The local metro scene's metrodat, or camp if not applicable
#   METROSCENE: The scope for scene search

class BoringDeathNotification( Plot ):
    # Inform the PC of who died, then end.
    LABEL = "RECOVER_DEAD_PARTY"
    active = False
    def start_recovery(self,camp):
        dead_names = [str(npc) for npc in camp.dead_party]
        msg = pbge.dialogue.list_nouns(dead_names)
        pbge.alert('{} did not survive the last mission.'.format(msg))
        for npc in camp.dead_party:
            for pc in list(camp.party):
                if hasattr(pc,"owner") and pc.owner is npc:
                    camp.party.remove(pc)
                elif hasattr(pc,"pet_data") and pc.pet_data and pc.pet_data.handler is npc:
                    camp.party.remove(pc)
                if hasattr(pc,"pilot") and pc.pilot is npc:
                    pc.pilot = None
        camp.dead_party = list()

