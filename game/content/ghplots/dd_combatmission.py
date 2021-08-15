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
from . import missionbuilder


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
    def __init__(self, camp, name, metroscene, return_wp, enemy_faction=None, allied_faction=None, include_war_crimes=False, **kwargs):
        # Determine 2 to 3 objectives for the mission.
        if include_war_crimes:
            objs = random.sample(self.OBJECTIVE_TAGS+self.CRIME_TAGS,2)
        else:
            objs = random.sample(self.OBJECTIVE_TAGS,2)
        self.crimes_happened = False

        super(CombatMissionSeed, self).__init__(camp, name, metroscene=metroscene, return_wp=return_wp, rank=max(camp.pc.renown + 1, 10),
                                                objectives=objs, win_message="You have completed the mission.",
                                                enemy_faction=enemy_faction, allied_faction=allied_faction, **kwargs)





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
        myfac = self.elements["ALLIED_FACTION"]
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
        if len(myteam.get_members_in_play(camp)) < 1:
            self.obj.win(camp,100)


