import pbge
import random
import gears


class HaywireTurn(object):
    def __init__(self,pc,camp):
        self.pc = pc
        self.camp = camp
        self.act()

    def bust_a_move(self):
        # Move to a randomly selected accessible tile.
        mynav = pbge.scenes.pathfinding.NavigationGuide(self.camp.scene, self.pc.pos, self.pc.get_current_speed(),
                                                        self.pc.mmode, self.camp.scene.get_blocked_tiles())
        mydest = random.choice(list(mynav.cost_to_tile.keys()))
        self.camp.fight.move_model_to(self.pc, mynav, mydest)

    def act(self):
        if random.randint(1,5) != 1:
            pbge.my_state.view.play_anims(gears.geffects.HaywireAnim(pos=self.pc.pos))
            self.bust_a_move()

            while self.camp.fight.still_fighting() and self.camp.fight.cstat[self.pc].action_points > 0 and random.randint(1,3) == 1:
                self.bust_a_move()


