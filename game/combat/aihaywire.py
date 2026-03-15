import pbge
import random
import gears
from . import actions


class HaywireTurn(object):
    def __init__(self,pc: gears.base.Being,camp):
        self.pc = pc
        self.current_pos = self.pc.pos
        self.camp = camp
        self.mp = self.camp.fight.cstat[self.pc].mp_remaining
        self.ap = self.camp.fight.cstat[self.pc].action_points

    def bust_a_move(self) -> list:
        my_actions = list()

        my_actions.append(actions.Faff(self.camp, self.pc, gears.geffects.HaywireAnim))
        self.ap -= 1
    
        # Move to a randomly selected accessible tile.
        if self.mp > 10:
            mynav = pbge.scenes.pathfinding.NavigationGuide(self.camp.scene, self.current_pos, self.mp,
                                                            self.pc.mmode, self.camp.scene.get_blocked_tiles())
            mydest = random.choice(list(mynav.cost_to_tile.keys()))

            self.mp -= mynav.cost_to_tile[mydest]
            self.current_pos = mydest
            my_actions.append(actions.MoveModelToPos(self.camp, self.pc, mynav, mydest))

        return my_actions

    def get_actions(self) -> list:
        my_actions = list()
        if random.randint(1,5) != 1:
            my_actions += self.bust_a_move()
            while self.ap > 0 and random.randint(1,5) == 2:
                my_actions += self.bust_a_move()

        return my_actions


