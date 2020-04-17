import gears
from pbge.plots import Plot, Adventure, NarrativeRequest, PlotState
import pbge
from game.content import plotutility
from game.content.ghcutscene import SimpleMonologueDisplay

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
    def custom_init( self, nart ):
        """Find a hospital, move the PC to there."""
        myscene = self.seek_element(nart,"HOSPITAL",self._is_good_scene,scope=self.elements["METROSCENE"])
        myent = self.seek_element(nart,"BED",self._is_good_bed,scope=myscene,check_subscenes=False)
        self.mission_entrance = (myscene,myent)
        self.started_mission = False
        self.plots_to_run = list()
        if nart.camp.dead_party:
            self.plots_to_run.append(self.add_sub_plot(nart,"RECOVERY_DEAD_PARTY"))
        return True

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,gears.GearHeadScene) and gears.tags.SCENE_HOSPITAL in candidate.attributes

    def _is_good_bed(self,nart,candidate):
        return isinstance(candidate,pbge.scenes.waypoints.Waypoint) and hasattr(candidate,"recovery_entrance") and candidate.recovery_entrance

    def start_recovery(self,camp):
        """

        :type camp: gears.GearHeadCampaign
        """
        camp.destination, camp.entrance = self.mission_entrance
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
            self.plots_to_run.append(self.add_sub_plot(nart,"LANCEMATE_NEEDS_HOSPITAL",spstate=PlotState().based_on(self,{"NPC":pc})))

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
    # This plot just loads the plots that do the actual work.
    LABEL = "LANCEMATE_NEEDS_MECHA"
    def custom_init( self, nart ):
        myscene = self.seek_element(nart,"GARAGE",self._is_good_scene,scope=self.elements["METROSCENE"])
        return True

    def _is_good_scene(self,nart,candidate):
        return isinstance(candidate,gears.GearHeadScene) and gears.tags.SCENE_GARAGE in candidate.attributes and gears.tags.SCENE_PUBLIC in candidate.attributes

    def start_recovery(self,camp):
        npc = self.elements["NPC"]
        garage = self.elements["GARAGE"]
        SimpleMonologueDisplay("My mecha was destroyed... I'm going to go to {} and get a new one.".format(garage),npc)(camp)
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
        if len(camp.dead_party) > 2:
            msg = ', '.join(dead_names[:-2]) + ', and ' + dead_names[-1]
        elif len(camp.dead_party) > 1:
            msg = ' and '.join(dead_names)
        else:
            msg = dead_names[0]
        pbge.alert('{} did not survive the last mission.'.format(msg))
        for npc in camp.dead_party:
            for pc in list(camp.party):
                if hasattr(pc,"owner") and pc.owner is npc:
                    camp.party.remove(pc)
                if hasattr(pc,"pilot") and pc.pilot is npc:
                    pc.pilot = None
        camp.dead_party = list()

