import random

import game.content.gharchitecture
import game.content.ghterrain
import game.content.ghwaypoints
import gears
import pbge
from game import teams, ghdialogue
from game.content import adventureseed
from game.content.adventureseed import ComeBackInOnePieceObjective, MAIN_OBJECTIVE_VALUE
from game.ghdialogue import context
from pbge.dialogue import ContextTag, Offer, Reply
from pbge.plots import Plot


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
    CRIME_TAGS = ("DZDCM_DO_CRIMES",)
    def __init__(self, camp, name, adv_return, enemy_faction=None, allied_faction=None, include_war_crimes=False, **kwargs):
        cms_pstate = pbge.plots.PlotState(adv=self, rank=max(camp.pc.renown+1,10))
        # Determine 2 to 3 objectives for the mission.
        if include_war_crimes:
            cms_pstate.elements["OBJECTIVES"] = random.sample(self.OBJECTIVE_TAGS+self.CRIME_TAGS,2)
        else:
            cms_pstate.elements["OBJECTIVES"] = random.sample(self.OBJECTIVE_TAGS,2)
        cms_pstate.elements["enemy_faction"] = enemy_faction
        cms_pstate.elements["allied_faction"] = allied_faction
        self.crimes_happened = False

        super(CombatMissionSeed, self).__init__(camp, name, adv_type="DZD_COMBAT_MISSION", adv_return=adv_return, pstate=cms_pstate, auto_set_rank=False, **kwargs)

        self.rewards.append(adventureseed.CashReward())
        self.rewards.append(adventureseed.ExperienceReward())
        self.rewards.append(adventureseed.RenownReward())

    def end_adventure(self,camp):
        super(CombatMissionSeed, self).end_adventure(camp)
        camp.day += 1


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


#   ********************************
#   ***  DZDCM_DEFEAT_COMMANDER  ***
#   ********************************

class BasicCommanderFight( Plot ):
    LABEL = "DZDCM_DEFEAT_COMMANDER"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        self.register_element("ROOM",pbge.randmaps.rooms.FuzzyRoom(10,10),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank,100,self.elements.get("enemy_faction"),myscene.environment,add_commander=True)
        team2.contents += myunit.mecha_list
        self.register_element("_commander",myunit.commander)

        self.obj = adventureseed.MissionObjective("Defeat {}".format(myunit.commander), MAIN_OBJECTIVE_VALUE)
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
        self.register_element("ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        myace = gears.selector.generate_ace(self.rank,self.elements.get("enemy_faction"),myscene.environment)
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
    def _commander_offers(self,camp):
        mylist = list()
        mylist.append(Offer("[CHALLENGE]",
            context=ContextTag([context.CHALLENGE,])))
        return mylist
    def t_ENDCOMBAT(self,camp):
        myteam = self.elements["_eteam"]
        if len(myteam.get_active_members(camp)) < 1:
            self.obj.win(100)

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
        myace = gears.selector.generate_ace(self.rank,self.elements.get("allied_faction"),myscene.environment)
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
            self.obj.win(100)


#   *****************************
#   ***  DZDCM_RECOVER_CARGO  ***
#   *****************************

class CargoContainer(gears.base.Prop):
    DEFAULT_COLORS = (gears.color.White,gears.color.Aquamarine,gears.color.DeepGrey,gears.color.Black,gears.color.GullGrey)
    def __init__(self,name="Shipping Container",size=1,colors=None,imagename="prop_shippingcontainer.png",**kwargs):
        super(CargoContainer, self).__init__(name=name,size=size,imagename=imagename,**kwargs)
        self.colors = colors or self.DEFAULT_COLORS

    @staticmethod
    def random_fleet_colors():
        return [random.choice(gears.color.MECHA_COLORS),
                random.choice(gears.color.DETAIL_COLORS),
                random.choice(gears.color.METAL_COLORS),
                gears.color.Black,
                random.choice(gears.color.MECHA_COLORS)]
    @classmethod
    def generate_cargo_fleet(cls,rank,colors=None):
        if not colors:
            colors = cls.random_fleet_colors()
        myfleet = [cls(colors=colors) for t in range(random.randint(2,3)+max(0,rank//25))]
        return myfleet



class BasicRecoverCargo( Plot ):
    LABEL = "DZDCM_RECOVER_CARGO"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("ROOM",pbge.randmaps.rooms.FuzzyRoom(10,10),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank,120,self.elements.get("enemy_faction"),myscene.environment,add_commander=False)
        team2.contents += myunit.mecha_list

        team3 = self.register_element("_cargoteam",teams.Team(),dident="ROOM")
        team3.contents += CargoContainer.generate_cargo_fleet(self.rank)
        # Oh yeah, when using PyCharm, why not use ludicrously long variable names?
        self.starting_number_of_containers = len(team3.contents)

        self.obj = adventureseed.MissionObjective("Recover lost cargo", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)
        self.combat_entered = False
        self.combat_finished = False

        return True
    def _eteam_ACTIVATETEAM(self,camp):
        if not self.combat_entered:
            self.combat_entered = True
    def t_ENDCOMBAT(self,camp):
        myteam = self.elements["_eteam"]
        cargoteam = self.elements["_cargoteam"]
        if len(cargoteam.get_active_members(camp)) < 1:
            self.obj.failed = True
        elif len(myteam.get_active_members(camp)) < 1:
            self.obj.win((sum([(100-c.get_total_damage_status()) for c in cargoteam.get_active_members(camp)]))//self.starting_number_of_containers )
            if not self.combat_finished:
                pbge.alert("The missing cargo has been secured.")
                self.combat_finished = True

#print BasicRecoverCargo.__module__

#   ********************************
#   ***  DZDCM_RESCUE_SURVIVORS  ***
#   ********************************

class BasicRescueSurvivors( Plot ):
    LABEL = "DZDCM_RESCUE_SURVIVORS"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        myscene = self.elements["LOCALE"]
        myroom = self.register_element("ROOM",pbge.randmaps.rooms.FuzzyRoom(10,10),dident="LOCALE")
        team2 = self.register_element("_eteam",teams.Team(enemies=(myscene.player_team,)),dident="ROOM")
        team3 = self.register_element("_ateam",teams.Team(enemies=(team2,),allies=(myscene.player_team,)),dident="ROOM")
        myunit = gears.selector.RandomMechaUnit(self.rank,200,self.elements.get("enemy_faction"),myscene.environment,add_commander=False)
        team2.contents += myunit.mecha_list

        mysurvivor = self.register_element("SURVIVOR",gears.selector.generate_ace(self.rank,self.elements.get("allied_faction"),myscene.environment))
        self.register_element("PILOT", mysurvivor.get_pilot())
        team3.contents.append(mysurvivor)

        self.obj = adventureseed.MissionObjective("Find and rescue any survivors.", MAIN_OBJECTIVE_VALUE)
        self.adv.objectives.append(self.obj)
        self.intro_ready = True
        self.eteam_activated = False
        self.eteam_defeated = False
        self.pilot_fled = False

        return True
    def _eteam_ACTIVATETEAM(self,camp):
        if self.intro_ready:
            self.eteam_activated = True
            if not self.pilot_fled:
                npc = self.elements["PILOT"]
                ghdialogue.start_conversation(camp,camp.pc,npc,cue=ghdialogue.HELLO_STARTER)
                camp.fight.active.append(self.elements["SURVIVOR"])
            self.intro_ready = False
    def PILOT_offers(self,camp):
        mylist = list()
        if self.eteam_defeated:
            mylist.append(Offer("[THANKS_FOR_MECHA_COMBAT_HELP] I better get back to base.",dead_end=True,context=ContextTag([ghdialogue.context.HELLO,]),
                                effect=self.pilot_leaves_combat))
        else:
            myoffer = Offer("[HELP_ME_VS_MECHA_COMBAT]",dead_end=True,
                context=ContextTag([ghdialogue.context.HELLO,]))
            if not self.eteam_activated:
                myoffer.replies.append(Reply("Get out of here, I can handle this.",destination=Offer("[THANK_YOU] I need to get back to base.",effect=self.pilot_leaves_before_combat,dead_end=True)))
            mylist.append(myoffer)
        return mylist
    def pilot_leaves_before_combat(self,camp):
        self.obj.win(105)
        self.pilot_leaves_combat(camp)
    def pilot_leaves_combat(self,camp):
        camp.scene.contents.remove(self.elements["SURVIVOR"])
        self.pilot_fled = True
    def t_ENDCOMBAT(self,camp):
        if self.eteam_activated and not self.pilot_fled:
            myteam = self.elements["_ateam"]
            eteam = self.elements["_eteam"]
            if len(myteam.get_active_members(camp)) < 1:
                self.obj.failed = True
            elif len(myteam.get_active_members(camp)) > 0 and len(eteam.get_active_members(camp)) < 1:
                self.eteam_defeated = True
                self.obj.win(100 - self.elements["SURVIVOR"].get_total_damage_status())
                npc = self.elements["PILOT"]
                ghdialogue.start_conversation(camp,camp.pc,npc,cue=ghdialogue.HELLO_STARTER)
