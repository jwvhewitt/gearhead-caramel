import random

import game.content.gharchitecture
import game.content.ghterrain
import game.content.ghwaypoints
import gears
import pbge
from game import teams, ghdialogue
from game.content import adventureseed
from game.content.adventureseed import MAIN_OBJECTIVE_VALUE
from game.content.plotutility import CargoContainer
from game.ghdialogue import context
from pbge.dialogue import ContextTag, Offer, Reply
from pbge.plots import Plot
import missionbuilder


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

class CombatMissionSeed(missionbuilder.BuildAMissionSeed):
    OBJECTIVE_TAGS = (missionbuilder.BAMO_DEFEAT_COMMANDER,missionbuilder.BAMO_RESPOND_TO_DISTRESS_CALL,missionbuilder.BAMO_EXTRACT_ALLIED_FORCES)
    CRIME_TAGS = ("DZDCM_DO_CRIMES",)
    def __init__(self, camp, name, adv_return, enemy_faction=None, allied_faction=None, include_war_crimes=False, **kwargs):
        cms_pstate = pbge.plots.PlotState(adv=self, rank=max(camp.pc.renown+1,10))
        # Determine 2 to 3 objectives for the mission.
        if include_war_crimes:
            cms_pstate.elements["OBJECTIVES"] = random.sample(self.OBJECTIVE_TAGS+self.CRIME_TAGS,2)
        else:
            cms_pstate.elements["OBJECTIVES"] = random.sample(self.OBJECTIVE_TAGS,2)
        self.crimes_happened = False

        super(CombatMissionSeed, self).__init__(camp, name, adv_return=adv_return, pstate=cms_pstate,
                                                enemy_faction=enemy_faction, allied_faction=allied_faction, **kwargs)



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
        myscenegen = pbge.randmaps.SceneGenerator(myscene, game.content.gharchitecture.MechaScaleDeadzone())
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True)
        self.adv.world = myscene

        self.register_element("_EROOM",pbge.randmaps.rooms.OpenRoom(5,5,anchor=random.choice(pbge.randmaps.anchors.EDGES)),dident="LOCALE")
        myent = self.register_element( "_ENTRANCE", game.content.ghwaypoints.Exit(anchor=pbge.randmaps.anchors.middle, plot_locked=True), dident="_EROOM")

        for ob in self.elements["OBJECTIVES"]:
            self.add_sub_plot(nart,ob)
        #self.add_sub_plot(nart, "DZDCM_RECOVER_CARGO")
        #self.adv.objectives.append(ComeBackInOnePieceObjective(nart.camp))

        self.mission_entrance = (myscene,myent)
        self.started_mission = False
        self.gave_mission_reminder = False

        return True

    def start_mission(self,camp):
        if not self.started_mission:
            camp.destination,camp.entrance = self.mission_entrance
            self.started_mission = True

    def t_START(self,camp):
        if camp.scene is self.elements["LOCALE"] and not self.gave_mission_reminder:
            mydisplay = adventureseed.CombatMissionDisplay(title=self.adv.name,mission_seed=self.adv,width=400)
            pbge.alert_display(mydisplay.show)
            self.gave_mission_reminder = True

    def t_ENDCOMBAT(self,camp):
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


#   *************************
#   ***  DZDCM_DO_CRIMES  ***
#   *************************

class EliminateWitnesses( Plot ):
    LABEL = "DZDCM_DO_CRIMES"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        self.register_element("ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        myace = gears.selector.generate_ace(self.rank,self.elements.get("ALLIED_FACTION"),myscene.environment)
        team2.contents.append(myace)
        self.register_element("_commander",myace.get_pilot())

        self.obj = adventureseed.MissionObjective("Defeat {}".format(myace.get_pilot()), MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)
        self.intro_ready = True

        return True
    def _eteam_ACTIVATETEAM(self,camp):
        if self.intro_ready:
            npc = self.elements["_commander"]
            ghdialogue.start_conversation(camp,camp.pc,npc,cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False
            self.adv.crimes_happened = True
    def _commander_offers(self,camp):
        mylist = list()
        myfac = self.elements["allied_faction"]
        mylist.append(Offer("Hold your fire- I'm not an enemy! You were sent by {}, weren't you?! I know about their secret agenda, and they're trying to keep the word from getting out...".format(myfac),
            context=ContextTag([context.ATTACK,])))
        mylist.append(Offer("Very well, you've made it clear what side you're on. [CHALLENGE]",
            context=ContextTag([context.CHALLENGE,])))
        mylist.append(Offer("They've been taken over by extremists; {} is no longer taking orders from {}. I was ordered to attack a village, but refused... now they're after me. Be careful, they're going to come after you too.".format(myfac,myfac.parent_faction.name),
            context=ContextTag([context.COMBAT_INFO,]), data={"subject":"Secret Agenda"}, effect=self._get_info))
        return mylist
    def _get_info(self,camp):
        self.obj.failed = True
        self.elements["_eteam"].retreat(camp)
        camp.dole_xp(100)
    def t_ENDCOMBAT(self,camp):
        myteam = self.elements["_eteam"]
        if len(myteam.get_active_members(camp)) < 1:
            self.obj.win(camp,100)


