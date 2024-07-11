from game import teams
import gears

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


class CivilianWaterShip(MegaProp):
    POSITIONS = ((0,0), (0,1), (0,-1), (0,2), (0,-2))
    def __init__(self, *args, rank=50, **kwargs):
        super().__init__(*args, **kwargs)
        self.rank = rank
        size = max(min(rank//10 + 1, 10), 2)
        length = max(min(rank//20 + 1, 5), 2)
        for t in range(length):
            self.contents.append(gears.base.Prop(size=size, name="Ship", imagename="prop_block.png"))

#print(MegaProp._generate_spiral(20))
