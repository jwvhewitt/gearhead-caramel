from pbge.plots import Plot
import game
import gears
import pbge
import pygame
import random
from game import teams,ghdialogue
from game.content import gharchitecture,ghterrain,ghwaypoints,plotutility,ghcutscene
from pbge.dialogue import Offer, ContextTag, Reply
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed
from . import missionbuilder
from gears import champions

QOBJ_ARTILLERY_STRIKE = "QOBJ_ARTILLERY_STRIKE"


class QO_ArtilleryStrike( Plot ):
    LABEL = QOBJ_ARTILLERY_STRIKE
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        self.intro_ready = True
        return True

    def LOCALE_ENTER(self,camp: gears.GearHeadCampaign):
        if self.intro_ready:
            self.intro_ready = False
            targets = list()
            for pc in camp.get_active_party():
                if (random.randint(1,100) + pc.get_skill_score(gears.stats.Ego, gears.stats.Stealth)) < (50 + self.rank):
                    targets.append(pc)

            if targets:
                pbge.alert("As you approach the mission site, you are targeted by artillery fire!")
                anims = list()
                for pc in targets:
                    total_damage = 0
                    for limb in pc.sub_com:
                        if hasattr(limb, "hp_damage") and random.randint(1,4) != 2:
                            limb.hp_damage = max(limb.hp_damage, max(1, (limb.max_health * random.randint(10,50))//100))
                            total_damage += limb.hp_damage
                    anims.append(gears.geffects.BigBoom(
                        pos=pc.pos,
                        y_off=-camp.scene.model_altitude(pc, *pc.pos)
                    ))
                    anims.append(pbge.scenes.animobs.Caption(
                        str(total_damage), pos=pc.pos, delay=5,
                        y_off=-camp.scene.model_altitude(pc, *pc.pos)
                    ))
                pbge.my_state.view.play_anims(*anims)

