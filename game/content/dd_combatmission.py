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
    def __init__(self, camp, name, adv_return, enemy_faction=None, allied_faction=None, **kwargs):
        cms_pstate = pbge.plots.PlotState(adv=self, rank=max(camp.pc.renown+1,10))
        # Determine 2 to 3 objectives for the mission.
        cms_pstate.elements["OBJECTIVES"] = random.sample(self.OBJECTIVE_TAGS,2)
        cms_pstate.elements["enemy_faction"] = enemy_faction
        cms_pstate.elements["allied_faction"] = allied_faction

        # Create a list in which to store the objectives. We'll use this to determine if the mission is
        # finished or failed or whatnot.
        self.objectives = list()

        super(CombatMissionSeed, self).__init__(camp, name, adv_type="DZD_COMBAT_MISSION", adv_return=adv_return, pstate=cms_pstate, auto_set_rank=False, **kwargs)

    def get_completion(self):
        # Return the percent completion of this mission. Due to optional objectives and whatnot, this may fall
        # outside of the 0..100 range.
        awarded = sum([o.awarded_points for o in self.objectives if not o.failed])
        total = max(sum([o.mo_points for o in self.objectives if not o.optional]),1)
        return (awarded * 100)//total
    def get_grade(self):
        c = self.get_completion()
        if c < 0:
            return "F-"
        elif c <= 50:
            return "F"
        elif c <= 60:
            return "D"
        elif c <= 70:
            return "C"
        elif c <= 80:
            return "B"
        elif c <= 90:
            return "A"
        elif c <= 100:
            return "A+"
        else:
            return "S"
    def is_completed(self):
        return all([(o.optional or o.awarded_points > 0 or o.failed) for o in self.objectives])

class ComeBackInOnePieceObjective(adventureseed.MissionObjective):
    def __init__(self,camp):
        super(ComeBackInOnePieceObjective, self).__init__(name="Come Back in One Piece", mo_points=50, optional=True, secret=True)
        self.camp = camp
    def _set_awarded_points(self,val):
        pass
    def _get_awarded_points(self):
        dstats = list()
        for mek in self.camp.party:
            if mek in self.camp.scene.contents:
                if mek.is_operational():
                    tds = mek.get_total_damage_status()
                    if tds <= 10:
                        dstats.append(100)
                    else:
                        dstats.append(-tds*2)
                else:
                    dstats.append(-200)
        if dstats:
            return ( sum(dstats) * self.mo_points ) // len(dstats)
        else:
            return -2 * self.mo_points
    awarded_points = property(_get_awarded_points,_set_awarded_points)

class ObjectivesInfo(object):
    PADDING = 5
    RED = pygame.Color(255,50,0)
    def __init__(self,mission_seed,font=None,width=300,**kwargs):
        self.mission_seed = mission_seed
        self.width = width
        self.font = font or pbge.BIGFONT
        self.images = dict()
        self.update()
    def update(self):
        self.images = dict()
        for o in self.mission_seed.objectives:
            if not o.secret:
                self.images[o] = pbge.render_text(self.font,self.get_objective_text(o),self.width,self.get_objective_color(o),justify=0)
        self.height = sum(i.get_height() for i in self.images.values()) + self.PADDING * (len(self.images.values())-1)

    def get_objective_text(self,obj):
        if obj.awarded_points == 0 and not obj.failed:
            return '- {} (INCOMPLETE)'.format(obj.name)
        elif obj.awarded_points < obj.mo_points//2 or obj.failed:
            return '- {} (FAILED)'.format(obj.name)
        else:
            return '- {} (COMPLETE)'.format(obj.name)

    def get_objective_color(self,obj):
        if obj.failed:
            return self.RED
        elif obj.optional:
            return pbge.INFO_GREEN
        else:
            return pbge.TEXT_COLOR
    def render(self,x,y):
        mydest = pygame.Rect(x, y, self.width, self.height)
        for obj,img in self.images.items():
            pbge.my_state.screen.blit(img, mydest)
            mydest.y += img.get_height() + self.PADDING


class CombatMissionDisplay(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.TitleBlock,ObjectivesInfo)
    def show(self):
        w,h = self.get_dimensions()
        mydest = pbge.frects.Frect(-w//2,-h//2,w,h).get_rect()
        self.render(mydest.x,mydest.y)

MAIN_OBJECTIVE_VALUE = 100

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

        myroom = self.register_element("_EROOM",pbge.randmaps.rooms.OpenRoom(5,5,anchor=random.choice(pbge.randmaps.anchors.EDGES)),dident="LOCALE")
        myent = self.register_element( "_ENTRANCE", ghwaypoints.Exit(anchor=pbge.randmaps.anchors.middle, plot_locked=True), dident="_EROOM")

        for ob in self.elements["OBJECTIVES"]:
            self.add_sub_plot(nart,ob)
        #self.add_sub_plot(nart, "DZDCM_RECOVER_CARGO")
        self.adv.objectives.append(ComeBackInOnePieceObjective(nart.camp))

        self.mission_entrance = (myscene,myent)
        self.started_mission = False
        self.gave_mission_reminder = False

        return True

    def t_UPDATE(self,camp):
        if not self.started_mission:
            camp.destination,camp.entrance = self.mission_entrance
            self.started_mission = True

    def t_START(self,camp):
        if camp.scene is self.elements["LOCALE"] and not self.gave_mission_reminder:
            mydisplay = CombatMissionDisplay(title=self.adv.name,mission_seed=self.adv,width=400)
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
        completion = self.adv.get_completion()
        if completion > 50:
            mydisplay = CombatMissionDisplay(title="Victory: {}".format(self.adv.get_grade()), mission_seed=self.adv,
                                             width=400)
        else:
            mydisplay = CombatMissionDisplay(title="Failure: {}".format(self.adv.get_grade()),
                                             title_color=pygame.color.Color(250, 50, 0), mission_seed=self.adv,
                                             width=400)
        pbge.alert_display(mydisplay.show)
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
        myunit = gears.selector.RandomMechaUnit(self.rank,100,self.elements.get("enemy_faction"),myscene.environment,add_commander=True)
        team2.contents += myunit.mecha_list
        self.register_element("_commander",myunit.commander)

        self.obj = adventureseed.MissionObjective("Defeat {}".format(myunit.commander),MAIN_OBJECTIVE_VALUE)
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
        myace = gears.selector.generate_ace(self.rank,self.elements.get("enemy_faction"),myscene.environment)
        team2.contents.append(myace)
        self.register_element("_commander",myace.get_pilot())

        self.obj = adventureseed.MissionObjective("Defeat {}".format(myace.get_pilot()),MAIN_OBJECTIVE_VALUE)
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

        self.obj = adventureseed.MissionObjective("Recover lost cargo",MAIN_OBJECTIVE_VALUE)
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

        self.obj = adventureseed.MissionObjective("Find and rescue any survivors.",MAIN_OBJECTIVE_VALUE)
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
