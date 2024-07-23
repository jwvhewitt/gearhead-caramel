from game import teams
import gears
import pbge
import random

class MegaProp(teams.Team):
    POSITIONS = ((0,0), (1,0), (0,1), (-1,0), (0,-1))

    @staticmethod
    def _generate_spiral(n):
        # The Junji Ito algorithm.
        my_coords = list()
        x = y = 0
        dx = 0
        dy = -1
        while n > 0:
            my_coords.append((x,y))
            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
                dx, dy = -dy, dx
            x += dx
            y += dy
            n -= 1
        return my_coords

    def predeploy(self, gb, room):
        if len(self.POSITIONS) < len(self.contents):
            self.POSITIONS = self._generate_spiral(len(self.contents))
        ox,oy = room.area.center
        for n, part in enumerate(self.contents):
            part.pos = (self.POSITIONS[n][0]+ox, self.POSITIONS[n][1]+oy)

        super().predeploy(gb, room)

    def move(self, camp: gears.GearHeadCampaign, dx=0, dy=0):
        # Locate all the parts of this prop.
        prop_parts = [p for p in camp.scene.contents if camp.scene.local_teams.get(p) is self]

        # Locate all the positions where this prop is gonna be after the move.
        destination_positions = {(p.pos[0] + dx, p.pos[1] + dy) for p in prop_parts}
        blocked_tiles = camp.scene.get_blocked_tiles()
        move_ok = True
        collisions = list()
        for actr in camp.scene.get_operational_actors():
            if hasattr(actr, "pos") and actr not in prop_parts and actr.pos in destination_positions:
                candidates = [vec for vec in camp.scene.ANGDIR if (actr.pos[0] + vec[0], actr.pos[1] + vec[1]) not in blocked_tiles]
                if candidates:
                    push_vec = random.choice(candidates)
                    pbge.my_state.view.anim_list.append(
                        pbge.scenes.animobs.MoveModel(actr, dest=(actr.pos[0] + push_vec[0], actr.pos[1] + push_vec[1]))
                    )
                    blocked_tiles.add((actr.pos[0] + push_vec[0], actr.pos[1] + push_vec[1]))
                    collisions.append(actr)
                else:
                    move_ok = False
                    collisions.append(actr)

        if move_ok:
            for p in prop_parts:
                pbge.my_state.view.anim_list.append(pbge.scenes.animobs.MoveModel(p, dest=(p.pos[0] + dx, p.pos[1] + dy)))
            pbge.my_state.view.handle_anim_sequence()
            #self.deal_with_collisions(camp, collisions)
        else:
            pbge.my_state.view.anim_list.clear()
            self.deal_with_collisions(camp, collisions)

    def deal_with_collisions(self, camp, collisions):
        invo = pbge.effects.Invocation(
            name="Crash!!!",
            fx=gears.geffects.DoDamage(
                len(self.get_members_in_play(camp)), 10,
                scatter=True, is_brutal=True, anim=gears.geffects.BigBoom
            ), area=pbge.scenes.targetarea.SingleTarget(),
        )
        invo.invoke(camp, None, [c.pos for c in collisions], pbge.my_state.view.anim_list)


NORTHWARD = (0,-1)
SOUTHWARD = (0,1)
EASTWARD = (1,0)
WESTWARD = (-1,0)


class CivilianWaterShip(MegaProp):
    POSITIONS = ((0,0), (0,1), (0,-1), (0,2), (0,-2))
    def __init__(self, *args, rank=50, **kwargs):
        super().__init__(*args, **kwargs)
        self.rank = rank
        size = max(min(rank//10 + 1, 10), 2)
        length = max(min(rank//20 + 1, 5), 2)
        for t in range(length):
            self.contents.append(gears.base.Prop(size=size, name="Ship", imagename="prop_block.png", altitude=0))

#print(MegaProp._generate_spiral(20))
