from pbge.plots import Plot, Adventure, PlotState
import ghwaypoints
import ghterrain
import gharchitecture
import gears
import pbge
import pygame
from .. import teams,ghdialogue
from ..ghdialogue import context
from pbge.scenes.movement import Walking, Flying, Vision
from gears.geffects import Skimming, Rolling
import random
import copy
import os
from pbge.dialogue import Cue,ContextTag,Offer,Reply
from gears import personality,color,stats
import ghcutscene
import adventureseed

# Mission Objectives:
# - Defeat Enemy Commander
# - Destroy Structure
# - Defend Location
# - Capture Location
# - Rescue Survivors
# - Recover Cargo
# - Extract Team
# - Scout Location
# - Patrol Checkpoints

class CombatMissionSeed(adventureseed.AdventureSeed):
    OBJECTIVE_TAGS = ("DZDCM_DEFEAT_COMMANDER","DZDCM_RESCUE_SURVIVORS","DZDCM_RECOVER_CARGO")
    def __init__(self, camp, name, adv_return, **kwargs):
        cms_pstate = pbge.plots.PlotState(adv=self, rank=camp.pc.renown)
        # Determine 2 to 3 objectives for the mission.
        cms_pstate.elements["OBJECTIVES"] = random.sample(self.OBJECTIVE_TAGS,2)

        # Create a Circle for the enemy team.

        # Create a list in which to store the objectives. We'll use this to determine if the mission is
        # finished or failed or whatnot.
        self.objectives = list()

        super(CombatMissionSeed, self).__init__(camp, name, adv_type="DZD_COMBAT_MISSION", adv_return=adv_return, pstate=cms_pstate, **kwargs)

    def get_completion(self):
        # Return the percent completion of this mission. Due to optional objectives and whatnot, this may fall
        # outside of the 0..100 range.
        awarded = sum([o.awarded_points for o in self.objectives if not o.failed])
        total = max(sum([o.mo_points for o in self.objectives if not o.optional]),1)
        return (awarded * 100)//total
    def is_completed(self):
        return all([(o.optional or (o.awarded_points > 0 and not o.failed)) for o in self.objectives])

#   ****************************
#   ***  DZD_COMBAT_MISSION  ***
#   ****************************

class DeadZoneCombatMission( Plot ):
    # Go fight mecha. Repeatedly.
    LABEL = "DZD_COMBAT_MISSION"
    active = True
    scope = True
    def custom_init( self, nart ):
        """An empty map that will add subplots for the mission's objectives."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(50,50,"Combat Zone",player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = pbge.randmaps.SceneGenerator(myscene,gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True)
        self.adv.world = myscene

        #mygoal = self.register_element("ROOM",pbge.randmaps.rooms.FuzzyRoom(10,10,parent=myscene))
        #team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        #team2.contents += gears.selector.RandomMechaUnit(self.rank,100,None,myscene.environment).mecha_list

        myroom = self.register_element("_EROOM",pbge.randmaps.rooms.OpenRoom(5,5,anchor=random.choice(pbge.randmaps.anchors.EDGES)),dident="LOCALE")
        myent = self.register_element( "_ENTRANCE", ghwaypoints.Exit(anchor=pbge.randmaps.anchors.middle, plot_locked=True), dident="_EROOM")

        #for ob in self.elements["OBJECTIVES"]:
        #    self.add_sub_plot(nart,ob)
        self.add_sub_plot(nart, "DZDCM_DEFEAT_COMMANDER")

        self.mission_entrance = (myscene,myent)
        self.started_mission = False
        self.gave_mission_reminder = False

        return True

    def t_UPDATE(self,camp):
        if not self.started_mission:
            camp.destination,camp.entrance = self.mission_entrance
            self.started_mission = True
        if camp.scene is self.elements["LOCALE"] and not self.gave_mission_reminder:
            pbge.alert("Start the mission, I guess. Get on with it you lout.",pbge.MEDIUMFONT)
            self.gave_mission_reminder = True

    def t_END(self,camp):
        # If the player team gets wiped out, end the mission.
        if not camp.first_active_pc():
            self.end_the_mission(camp)

    def _ENTRANCE_menu(self, camp, thingmenu):
        if self.adv.is_completed():
            thingmenu.desc = "Are you ready to return to {}?".format(self.elements["ADVENTURE_RETURN"][0])
        else:
            thingmenu.desc = "Do you want to abort this mission and return to {}?".format(self.elements["ADVENTURE_RETURN"][0])

        thingmenu.add_item("End Mission",self.end_the_mission)
        thingmenu.add_item("Continue Mission", None)

    def end_the_mission(self,camp):
        camp.destination, camp.entrance = self.elements["ADVENTURE_RETURN"]
        self.adv.end_adventure(camp)

#   ********************************
#   ***  DZDCM_DEFEAT_COMMANDER  ***
#   ********************************

class BasicCommanderFight( Plot ):
    LABEL = "DZDCM_DEFEAT_COMMANDER"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("ROOM",pbge.randmaps.rooms.FuzzyRoom(10,10),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank,100,None,myscene.environment,add_commander=True)
        team2.contents += myunit.mecha_list
        self.register_element("_commander",myunit.commander)

        self.obj = adventureseed.MissionObjective("Defeat {}".format(myunit.commander),50)
        self.adv.objectives.append(self.obj)
        self.intro_ready = True

        return True
    def _eteam_ACTIVATETEAM(self,camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False
    def _commander_offers(self,camp):
        mylist = list()
        mylist.append(Offer("[CHALLENGE]",
            context=ContextTag([context.CHALLENGE,])))
        return mylist
    def t_ENDCOMBAT(self,camp):
        myteam = self.elements["_eteam"]
        myboss = self.elements["_commander"].get_root()
        if len(myteam.get_active_members(camp)) < 1:
            self.obj.win(100)
        elif not myboss.is_operational():
            self.obj.win(80)

class AceCommanderFight( Plot ):
    LABEL = "DZDCM_DEFEAT_COMMANDER"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        myace = gears.selector.generate_ace(self.rank,None,myscene.environment)
        team2.contents.append(myace)
        self.register_element("_commander",myace.get_pilot())

        self.obj = adventureseed.MissionObjective("Defeat {}".format(myace.get_pilot()),50)
        self.adv.objectives.append(self.obj)
        self.intro_ready = True

        return True
    def _eteam_ACTIVATETEAM(self,camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False
    def _commander_offers(self,camp):
        mylist = list()
        mylist.append(Offer("[CHALLENGE]",
            context=ContextTag([context.CHALLENGE,])))
        return mylist
    def t_ENDCOMBAT(self,camp):
        myteam = self.elements["_eteam"]
        if len(myteam.get_active_members(camp)) < 1:
            self.obj.win(100)
