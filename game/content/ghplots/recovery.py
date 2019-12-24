import gears
from pbge.plots import Plot, Adventure, NarrativeRequest, PlotState
import pbge
from game.content import plotutility

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
            camp.pc.container.remove(camp.pc)
            camp.party.append(camp.pc)
            # If the PC was knocked out, all the lancemates recover/repair while the PC is being treated.
            for pc in list(camp.incapacitated_party):
                camp.incapacitated_party.remove(pc)
                camp.party.append(pc)
            for pc in list(camp.party):
                if pc is not camp.pc and isinstance(pc,gears.base.Character) and not camp.get_pc_mecha(pc):
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
            self.plots_to_run.append(self.add_sub_plot(nart,"RECOVERY_DEAD_PARTY"))

        return True

    def start_recovery(self,camp):
        for p in self.plots_to_run:
            p.start_recovery(camp)

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
        camp.dead_party = list()

