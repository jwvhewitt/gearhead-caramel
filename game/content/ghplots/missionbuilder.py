from pbge.plots import Plot
import game
import gears
import pbge
import pygame
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed

BAMO_DEFEAT_THE_BANDITS = "BAMO_DefeatTheBandits"
BAMO_LOCATE_ENEMY_FORCES = "BAMO_LocateEnemyForces"
BAMO_STORM_THE_CASTLE = "BAMO_StormTheCastle"   # 4 points
BAMO_SURVIVE_THE_AMBUSH = "BAMO_SurviveTheAmbush"


MAIN_OBJECTIVE_VALUE = 100

#   **************************
#   ***  ADVENTURE  SEEDS  ***
#   **************************

class BuildAMissionSeed(adventureseed.AdventureSeed):
    # Optional elements:
    #   ENTRANCE_ANCHOR:    Anchor for the PC's entrance
    def __init__(self, camp, name, adv_return, enemy_faction=None, allied_faction=None, rank=None, objectives=(),
                 adv_type="BAM_MISSION", custom_elements=None,
                 scenegen=pbge.randmaps.SceneGenerator, architecture=gharchitecture.MechaScaleDeadzone,
                 cash_reward=100,experience_reward=100,
                 one_chance=True, data=None, win_message="", loss_message="", **kwargs):
        cms_pstate = pbge.plots.PlotState(adv=self, rank=rank or max(camp.pc.renown+1,10))

        cms_pstate.elements["ENEMY_FACTION"] = enemy_faction
        cms_pstate.elements["ALLIED_FACTION"] = allied_faction
        cms_pstate.elements["OBJECTIVES"] = objectives
        cms_pstate.elements["SCENEGEN"] = scenegen
        cms_pstate.elements["ARCHITECTURE"] = architecture
        cms_pstate.elements["ONE_CHANCE"] = one_chance      # If False, you can return to the combat zone until all objectives are complete.
        cms_pstate.elements["METROSCENE"] = adv_return[0]
        if custom_elements:
            cms_pstate.elements.update(custom_elements)
        if win_message:
            cms_pstate.elements["WIN_MESSAGE"] = win_message
        if loss_message:
            cms_pstate.elements["LOSS_MESSAGE"] = loss_message

        # Data is a dict of stuff that will get used by whatever plot created this adventure seed, or maybe it
        # can be used by some of the objectives. I dunno! It's just a dict of stuff! Do with it as you will.
        # Currently used by DZD tarot cards to record the win,lose outcomes of a mission.
        self.data = dict()
        if data:
            self.data.update(data)

        super(BuildAMissionSeed, self).__init__(camp, name, adv_type=adv_type, adv_return=adv_return, pstate=cms_pstate, auto_set_rank=False, **kwargs)

        if cash_reward > 0:
            self.rewards.append(adventureseed.CashReward(size=cash_reward))
        if experience_reward > 0:
            self.rewards.append(adventureseed.ExperienceReward(size=experience_reward))
        self.rewards.append(adventureseed.RenownReward())

    def end_adventure(self,camp):
        super(BuildAMissionSeed, self).end_adventure(camp)
        camp.day += 1


class BuildAMissionPlot( Plot ):
    # Go fight mecha. Repeatedly.
    LABEL = "BAM_MISSION"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        """An empty map that will add subplots for the mission's objectives."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(50,50,"Combat Zone",player_team=team1,scale=gears.scale.MechaScale)
        myscenegen = self.elements["SCENEGEN"](myscene, self.elements["ARCHITECTURE"]() )
        self.register_scene( nart, myscene, myscenegen, ident="LOCALE", temporary=True, dident="METROSCENE")
        self.adv.world = myscene

        myanchor = self.elements.get("ENTRANCE_ANCHOR",None) or random.choice(pbge.randmaps.anchors.EDGES)
        self.register_element("ENTRANCE_ROOM",pbge.randmaps.rooms.OpenRoom(7,7,anchor=myanchor),dident="LOCALE")
        myent = self.register_element( "_ENTRANCE", game.content.ghwaypoints.Exit(anchor=pbge.randmaps.anchors.middle, plot_locked=True), dident="ENTRANCE_ROOM")

        for ob in self.elements["OBJECTIVES"]:
            self.add_sub_plot(nart,ob)

        self.mission_entrance = (myscene,myent)
        self.started_mission = False
        self.gave_mission_reminder = False
        self.gave_ending_message = False

        return True

    def start_mission(self,camp):
        camp.destination, camp.entrance = self.mission_entrance
        if not self.started_mission:
            self.started_mission = True

    def t_START(self,camp):
        if camp.scene is self.elements["LOCALE"] and not self.gave_mission_reminder:
            mydisplay = adventureseed.CombatMissionDisplay(title=self.adv.name,mission_seed=self.adv,width=400)
            pbge.alert_display(mydisplay.show)
            self.gave_mission_reminder = True

    def t_ENDCOMBAT(self,camp):
        # If the player team gets wiped out, end the mission.
        if not camp.first_active_pc():
            self.exit_the_mission(camp)

    def t_UPDATE(self,camp):
        if self.adv.is_completed() and not self.gave_ending_message:
            if self.adv.is_won():
                if "WIN_MESSAGE" in self.elements:
                    pbge.alert(self.elements["WIN_MESSAGE"])
            elif "LOSS_MESSAGE" in self.elements:
                pbge.alert(self.elements["LOSS_MESSAGE"])
            self.gave_ending_message = True

    def _ENTRANCE_menu(self, camp, thingmenu):
        if self.adv.is_completed():
            thingmenu.desc = "Are you ready to return to {}?".format(self.elements["ADVENTURE_RETURN"][0])
        else:
            thingmenu.desc = "Do you want to abort this mission and return to {}?".format(self.elements["ADVENTURE_RETURN"][0])

        thingmenu.add_item("End Mission",self.exit_the_mission)
        thingmenu.add_item("Continue Mission", None)

    def exit_the_mission(self,camp):
        camp.destination, camp.entrance = self.elements["ADVENTURE_RETURN"]
        if self.elements["ONE_CHANCE"] or self.adv.is_completed():
            self.adv.end_adventure(camp)
        elif not self.elements["ONE_CHANCE"]:
            # Restore the mission for next time.
            self.adv.restore_party(camp)
            mydisplay = adventureseed.CombatResultsDisplay(title="Failure: {}".format(self.adv.get_grade()),
                                                 title_color=pygame.color.Color(250, 50, 0), mission_seed=self.adv,
                                                 width=400)
            pbge.alert_display(mydisplay.show)
            self.adv.results = list()

            for npc in [n for n in camp.scene.contents if isinstance(n,gears.base.BaseGear)]:
                if npc not in camp.party:
                    if hasattr(npc,"wipe_damage"):
                        npc.wipe_damage()
                    if hasattr(npc, "mp_spent"):
                        npc.mp_spent = 0
                    if hasattr(npc, "sp_spent"):
                        npc.sp_spent = 0
                    for part in npc.descendants():
                        if hasattr(part, "get_reload_cost"):
                            part.spent = 0
                        if hasattr(part, "mp_spent"):
                            part.mp_spent = 0
                        if hasattr(part, "sp_spent"):
                            part.sp_spent = 0
            for o in self.adv.objectives:
                o.reset_objective()


#   **********************
#   ***   OBJECTIVES   ***
#   **********************

class BAM_DefeatTheBandits( Plot ):
    LABEL = BAMO_DEFEAT_THE_BANDITS
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        self.register_element("ROOM",pbge.randmaps.rooms.FuzzyRoom(15,15,anchor=pbge.randmaps.anchors.middle),dident="LOCALE")

        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank,100,myfac,myscene.environment,add_commander=True)
        team2.contents += myunit.mecha_list
        self.register_element("_commander",myunit.commander)

        self.obj = adventureseed.MissionObjective("Defeat the bandits".format(myfac), MAIN_OBJECTIVE_VALUE)
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
            self.obj.win(camp,100)


class BAM_LocateEnemyForces( Plot ):
    LABEL = BAMO_LOCATE_ENEMY_FORCES
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        self.register_element("ROOM",pbge.randmaps.rooms.FuzzyRoom(15,15),dident="LOCALE")
        self.register_element("DUD_ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5),dident="LOCALE")

        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank,100,myfac,myscene.environment,add_commander=True)
        team2.contents += myunit.mecha_list
        self.register_element("_commander",myunit.commander)

        if myfac:
            self.obj = adventureseed.MissionObjective("Locate {} forces".format(myfac), MAIN_OBJECTIVE_VALUE)
        else:
            self.obj = adventureseed.MissionObjective("Locate enemy forces", MAIN_OBJECTIVE_VALUE)
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
            self.obj.win(camp,100)


class BAM_StormTheCastle( Plot ):
    LABEL = BAMO_STORM_THE_CASTLE
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")
        self.register_element("ROOM",pbge.randmaps.rooms.FuzzyRoom(10,10),dident="LOCALE")

        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank,150,myfac,myscene.environment,add_commander=True)
        team2.contents += myunit.mecha_list
        self.register_element("_commander",myunit.commander)
        self.starting_guards = len(team2.contents)

        myfort = self.register_element("_FORT",gears.selector.generate_fortification(self.rank,myfac,myscene.environment))
        team2.contents.append( myfort)

        self.obj1 = adventureseed.MissionObjective("Destroy {} command center".format(myfac), MAIN_OBJECTIVE_VALUE*3)
        self.adv.objectives.append(self.obj1)

        self.obj2 = adventureseed.MissionObjective("Defeat command center guards".format(myunit.commander), MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj2)

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
        myboss = self.elements["_FORT"]
        myguards = [npc for npc in myteam.get_active_members(camp) if npc is not myboss]

        if len(myguards) < self.starting_guards:
            self.obj2.win(camp,100 * (self.starting_guards - len(myguards)) // self.starting_guards)
        if not myboss.is_operational():
            self.obj1.win(camp,100)


class BAM_SurviveTheAmbush( Plot ):
    LABEL = BAMO_SURVIVE_THE_AMBUSH
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        myfac = self.elements.get("ENEMY_FACTION")

        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ENTRANCE_ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank,100,myfac,myscene.environment,add_commander=False)
        team2.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Survive the ambush".format(myfac), MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True

        return True

    def t_START(self,camp):
        if self.intro_ready:
            myfac = self.elements.get("ENEMY_FACTION")
            if myfac:
                pbge.alert("Without warning, you are ambushed by {}!".format(myfac))
            else:
                pbge.alert("Without warning, you are ambushed by enemy mecha!")
            self.intro_ready = False

    def t_ENDCOMBAT(self,camp):
        myteam = self.elements["_eteam"]

        if len(myteam.get_active_members(camp)) < 1:
            self.obj.win(camp,100)
