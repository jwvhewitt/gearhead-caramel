import pbge
import gears

class MoveModelToPos:
    def __init__(self, camp, chara, nav, dest):
        self.camp = camp
        self.chara = chara
        self.nav = nav
        self.dest = dest
        self.is_player_model = chara in self.camp.party
        self.path = self.nav.get_path(dest)[1:]

    def __call__(self):
        if self.path:
            p = self.path.pop(0)
            self.camp.fight.step(self.chara, p)
            if self.is_player_model:
                self.camp.scene.update_party_position(self.camp)
            if not self.path:
                # Spend the movement points.
                self.camp.fight.cstat[self.chara].spend_mp(self.nav.cost_to_tile[self.chara.pos])
                return False
            else:
                return True


def get_jump_points(camp: gears.GearHeadCampaign, mover: gears.base.Mover):
    # Return a set of points this mover can jump to.
    mypoints = set()
    jump_speed = mover.get_speed(gears.tags.Jumping)
    if jump_speed > 10:
        max_map_dist = (jump_speed + 9)//10

        for dx in range(-max_map_dist, max_map_dist+1):
            for dy in range(-max_map_dist, max_map_dist+1):
                x, y = mover.pos[0]+dx, mover.pos[1]+dy
                if not camp.scene.tile_blocks_movement(x, y, mover.mmode) and camp.scene.distance((x,y), mover.pos) <= max_map_dist and (x,y) != mover.pos:
                    mypoints.add((x,y))

        mypoints = mypoints.difference(camp.scene.get_blocked_tiles())

    return mypoints


class JumpModelToPos:
    def __init__(self, camp, chara, dest):
        self.camp = camp
        self.chara = chara
        self.dest = dest
        self.is_player_model = chara in self.camp.party

    def __call__(self):
        distance = self.camp.scene.distance(self.chara.pos, self.dest)

        pbge.my_state.view.play_anims(
            gears.geffects.JumpModel(
                self.camp.scene, self.chara, dest=self.dest
            )
        )

        if self.camp.fight:
            self.camp.fight.cstat[self.chara].moves_this_round += distance
            self.camp.fight.cstat[self.chara].spend_ap(1)
        if self.is_player_model:
            self.camp.scene.update_party_position(self.camp)


class InvokeInvocation:
    def __init__(self, camp, invo: pbge.effects.Invocation, firing_pos, chara, targets, data):
        self.camp = camp
        self.invo = invo
        self.firing_pos = firing_pos
        self.chara = chara
        self.targets = targets
        self.data = data

    def __call__(self):
        if self.chara.pos == self.firing_pos:
            # Spend the movement points.
            _=self.invo.invoke(self.camp, self.chara, self.targets, pbge.my_state.view.anim_list, data=self.data)
            self.camp.fight.cstat[self.chara].spend_ap(1)


class BumpWaypoint:
    # This should only get called for PCs, right now.
    def __init__(self, camp, chara, wpoint):
        self.camp = camp
        self.chara = chara
        self.wpoint = wpoint

    @staticmethod
    def _are_adjacent(pos1, pos2):
        return abs(pos1[0]-pos2[0]) <= 1 and abs(pos1[1]-pos2[1]) <= 1

    def __call__(self):
        if self._are_adjacent(self.chara.pos, self.wpoint.pos):
            self.wpoint.combat_bump(self.camp, self.mover)
            self.camp.fight.cstat[self.chara].spend_ap(1)


class BuyBonusActions:
    # This should only get called for NPCs, right now.
    def __init__(self, camp, chara):
        self.camp = camp
        self.chara = chara

    def __call__(self):
        self.camp.fight.cstat[self.chara].buy_bonus_action()
