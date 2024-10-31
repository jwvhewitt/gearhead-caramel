from .. import container
import random
import pygame
import math
from ..scenes import animobs, terrain
import inspect


class RoomError(Exception):
    """Something went wrong during room construction."""
    pass


#  *****************
#  ***   ROOMS   ***
#  *****************

class Room(object):
    """A Room is an area on the map. This room is nothing but an area."""
    GAPFILL = None
    MUTATE = None
    DECORATE = None
    DO_DIRECT_CONNECTIONS = False
    ON_THE_EDGE = False
    MIN_RANDOM_SIZE = 7
    MAX_RANDOM_SIZE = 12
    EXPAND_AMOUNT = 5

    def __init__(self, width=None, height=None, tags=(), anchor=None, parent=None, archi=None, decorate=None, **kwargs):
        self.width = width or random.randint(self.MIN_RANDOM_SIZE, self.MAX_RANDOM_SIZE)
        self.height = height or random.randint(self.MIN_RANDOM_SIZE, self.MAX_RANDOM_SIZE)
        self.tags = tags
        self.anchor = anchor
        self.archi = archi
        self.area = None
        self.contents = container.ContainerList(owner=self)
        if parent:
            parent.contents.append(self)
        self.DECORATE = decorate or self.DECORATE
        self.data = kwargs.copy()

    def step_two(self, gb):
        self.arrange_contents(gb)
        if self.GAPFILL:
            self.GAPFILL(gb, self)
        # Prepare any child nodes in self.contents as needed.
        for r in self.contents:
            if isinstance(r, Room):
                r.step_two(gb)

    def step_three(self, gb, archi):
        # Determine what architect we're going to use- if this room has a
        # custom architect defined, use that instead of the default architecture.
        archi = self.archi or archi
        self.connect_contents(gb, archi)
        # Prepare any child nodes in self.contents as needed.
        for r in self.contents:
            if isinstance(r, Room):
                r.step_three(gb, archi)

    def step_four(self, gb):
        if self.archi and self.archi.mutate:
            self.archi.mutate(gb, self.area, self.archi)
        # Prepare any child nodes in self.contents as needed.
        for r in self.contents:
            if isinstance(r, Room):
                r.step_four(gb)

    def step_five(self, gb, archi):
        self.build(gb, archi)
        # Prepare any child nodes in self.contents as needed.
        for r in self.contents:
            if isinstance(r, Room):
                r.step_five(gb, archi)

    def step_six(self, gb, archi):
        self.deploy(gb, archi)
        # Prepare any child nodes in self.contents as needed.
        for r in self.contents:
            if isinstance(r, Room):
                r.step_six(gb, archi)

    def step_seven(self, gb, archi):
        if self.DECORATE:
            self.DECORATE(gb, self, archi)
        # Prepare any child nodes in self.contents as needed.
        for r in self.contents:
            if isinstance(r, Room):
                r.step_seven(gb, archi)

    #def all_rooms(self):
    #    yield self
    #    for r in self.contents:
    #        if isinstance(r, Room):
    #            for rr in r.all_rooms():
    #                yield rr

    def _expand(self):
        # This room isn't big enough. Make it bigger, then raise an error.
        self.width += self.EXPAND_AMOUNT
        self.height += self.EXPAND_AMOUNT
        raise RoomError("ROOM ERROR: {}:{} isn't big enough".format(str(self), str(self.__class__)), self)

    def find_spot_for_room(self, closed_area, myroom):
        myrect = pygame.Rect(0, 0, myroom.width, myroom.height)
        count = 0
        if self.area.width <= myroom.width or self.area.height <= myroom.height:
            self._expand()
        while (count < 100) and not myroom.area:
            myrect.x = random.choice(list(range(self.area.x, self.area.x + self.area.width - myroom.width)))
            myrect.y = random.choice(list(range(self.area.y, self.area.y + self.area.height - myroom.height)))
            if self.ON_THE_EDGE and count < 500:
                if random.randint(1, 2) == 1:
                    myrect.x = random.choice((self.area.x, self.area.x + self.area.width - myroom.width))
                else:
                    myrect.y = random.choice((self.area.y, self.area.y + self.area.height - myroom.height))
            if myrect.inflate(6, 6).collidelist(closed_area) == -1:
                myroom.area = myrect
                closed_area.append(myrect)
            elif count > 200 and myrect.collidelist(closed_area) == -1:
                myroom.area = myrect
                closed_area.append(myrect)
            elif count > 500:
                if random.randint(1, 3) == 3 and myrect.width > myroom.MIN_RANDOM_SIZE:
                    myrect.width -= 1
                if random.randint(1, 3) == 3 and myrect.height > myroom.MIN_RANDOM_SIZE:
                    myrect.height -= 1
            count += 1
        return(bool(myroom.area))

    def arrange_contents(self, gb):
        # Step Two: Arrange subcomponents within this area.
        closed_area = list()
        # Add already placed rooms to the closed_area list.
        for r in self.contents:
            if hasattr(r, "area") and r.area:
                closed_area.append(r.area)
        # Add rooms with defined anchors next
        for r in self.contents:
            if hasattr(r, "anchor") and r.anchor and hasattr(r, "area"):
                myrect = pygame.Rect(0, 0, r.width, r.height)
                r.anchor(self.area, myrect)
                if myrect.collidelist(closed_area) == -1:
                    r.area = myrect
                    closed_area.append(myrect)
        # old_closed = list(closed_area)
        # Assign areas for unplaced rooms.
        unplaced_rooms = [r for r in self.contents if hasattr(r, "area") and not r.area]
        tries = 100
        while tries > 0:
            ok = True
            for r in unplaced_rooms:
                ok = ok and self.find_spot_for_room(closed_area, r)

            if ok:
                break
            else:
                for r in unplaced_rooms:
                    if r.area in closed_area:
                        closed_area.remove(r.area)
                    r.area = None
                    tries -= 1
                    #if (tries < 50 or random.randint(1, 3) == 3) and r.width > r.MIN_RANDOM_SIZE:
                    #    r.width -= 1
                    #if (tries < 50 or random.randint(1, 3) == 3) and r.height > r.MIN_RANDOM_SIZE:
                    #    r.height -= 1
                    #if tries < 10:
                    #    print("Warning: Running out of tries!")
        if tries < 1:
            self._expand()

    def connect_contents(self, gb, archi):
        # Step Three: Connect all rooms in contents, making trails on map.

        # Generate list of rooms.
        myrooms = [r for r in self.contents if hasattr(r, "area")]

        # Process them
        if myrooms:
            prev = myrooms[-1]
            for r in myrooms:
                # Connect r to prev
                if self.DO_DIRECT_CONNECTIONS:
                    self.draw_direct_connection(gb, r.area.centerx, r.area.centery, prev.area.centerx,
                                                prev.area.centery, archi)
                else:
                    self.draw_L_connection(gb, r.area.centerx, r.area.centery, prev.area.centerx, prev.area.centery,
                                           archi)

                # r becomes the new prev
                prev = r

    def dont_touch_edge(self, gb):
        if self.area.x == 0:
            self.area.x += 1
            self.area.width -= 1
        elif self.area.x + self.area.width >= gb.width:
            self.area.width -= 1
        if self.area.y == 0:
            self.area.y += 1
            self.area.height -= 1
        elif self.area.y + self.area.height >= gb.height:
            self.area.height -= 1

    def build(self, gb, archi):
        # Step Five: Actually draw the room, taking into account terrain already on map.
        pass

    def list_good_deploy_spots(self, gb, archi):
        good_spots = list()
        if self.area.width > 6 and self.area.height > 6:
            for x in range(self.area.x + 1, self.area.x + self.area.width - 1):
                for y in range(self.area.y + 1, self.area.y + self.area.height - 1):
                    if not self.probably_blocks_movement(gb, x, y, archi):
                        good_spots.append((x, y))
        else:
            for x in range(self.area.x, self.area.x + self.area.width):
                for y in range(self.area.y, self.area.y + self.area.height):
                    if not self.probably_blocks_movement(gb, x, y, archi):
                        good_spots.append((x, y))
        return good_spots

    def deploy(self, gb, archi):
        # Step Six: Move items and monsters onto the map.
        # Find a list of good spots for stuff that goes in the open.
        good_spots = self.list_good_deploy_spots(gb, archi)

        # Find a list of good walls for stuff that must be mounted on a wall.
        good_walls = [p for p in self.get_west_north_wall_points(gb) if self.is_good_spot_for_wall_decor(gb, p, archi)]

        # First pass- execute any deploy methods in any contents.
        for i in list(self.contents):
            if hasattr(i, "predeploy"):
                i.predeploy(gb, self)

        for i in list(self.contents):
            # Remove the spaces occupied by map contents from the good spots lists.
            if hasattr(i, "pos") and i.pos:
                if hasattr(i, "place"):
                    i.place(gb, i.pos)
                if i.pos in good_walls:
                    good_walls.remove(i.pos)
                if i.pos in good_spots:
                    good_spots.remove(i.pos)

        for i in list(self.contents):
            # Only place contents which can be placed, but haven't yet.
            if hasattr(i, "place"):
                if not (hasattr(i, "pos") and i.pos):
                    if hasattr(i, "anchor"):
                        myrect = pygame.Rect(0, 0, 1, 1)
                        i.anchor(self.area, myrect)
                        i.place(gb, (myrect.x, myrect.y))
                        if (myrect.x, myrect.y) in good_walls:
                            good_walls.remove((myrect.x, myrect.y))
                        if (myrect.x, myrect.y) in good_spots:
                            good_spots.remove((myrect.x, myrect.y))
                    elif hasattr(i, "ATTACH_TO_WALL") and i.ATTACH_TO_WALL and good_walls:
                        p = random.choice(good_walls)
                        good_walls.remove(p)
                        i.place(gb, p)
                    elif good_spots:
                        i.pos = None
                        if hasattr(i, "IMMOVABLE") and i.IMMOVABLE:
                            candidates = list(good_spots)
                            while candidates and not i.pos:
                                p = random.choice(candidates)
                                candidates.remove(p)
                                if gb.wall_wont_block(*p, mmode=archi.mmode):
                                    i.place(gb, p)
                                    good_spots.remove(p)
                            if not i.pos:
                                p = random.choice(good_spots)
                                good_spots.remove(p)
                                i.place(gb, p)

                        else:
                            p = random.choice(good_spots)
                            good_spots.remove(p)
                            i.place(gb, p)
                    else:
                        gb.contents.append(i)
                        print("RandMaps Warning: {} had no place in {}: {}x{}".format(i, gb, self.area.width, self.area.height))
                        print(archi)
                        for y in range(self.area.y, self.area.y + self.area.height):
                            myline = list()
                            for x in range(self.area.x, self.area.x + self.area.width):
                                if self.probably_blocks_movement(gb, x, y, archi):
                                    myline.append('#')
                                else:
                                    myline.append('.')
                            print("".join(myline))

    def fill(self, gb, dest, floor=-1, wall=-1, decor=-1):
        # Fill the provided area with the provided terrain.
        for x in range(dest.x, dest.x + dest.width):
            for y in range(dest.y, dest.y + dest.height):
                if gb.on_the_map(x, y):
                    if floor != -1:
                        gb._map[x][y].floor = floor
                    if wall != -1:
                        gb._map[x][y].wall = wall
                    if decor != -1:
                        gb._map[x][y].decor = decor

    def probably_blocks_movement(self, gb, x, y, archi):
        if not gb.on_the_map(x, y):
            return True
        elif gb._map[x][y].wall is True:
            return True
        elif inspect.isclass(gb.get_wall(x, y)) and issubclass(gb.get_wall(x, y), terrain.DoorTerrain):
            return False
        else:
            return gb.tile_blocks_movement(x,y, archi.mmode)

    def draw_direct_connection(self, gb, x1, y1, x2, y2, archi):
        path = animobs.get_line(x1, y1, x2, y2)
        for p in path:
            for x in range(p[0] - 1, p[0] + 2):
                for y in range(p[1] - 1, p[1] + 2):
                    archi.draw_fuzzy_ground(gb, x, y)

    def draw_L_connection(self, gb, x1, y1, x2, y2, archi):
        if random.randint(1, 2) == 1:
            cx, cy = x1, y2
        else:
            cx, cy = x2, y1
        self.draw_direct_connection(gb, x1, y1, cx, cy, archi)
        self.draw_direct_connection(gb, x2, y2, cx, cy, archi)

    def find_distance_to(self, oroom):
        return round(
            math.sqrt((self.area.centerx - oroom.area.centerx) ** 2 + (self.area.centery - oroom.area.centery) ** 2))

    def is_basic_wall(self, gb, x, y):
        wall = gb.get_wall(x, y)
        if inspect.isclass(wall):
            return issubclass(wall, terrain.WallTerrain) and not issubclass(wall, terrain.DoorTerrain)
        elif wall is True:
            return True

    def is_good_spot_for_wall_decor(self, gb, pos, archi):
        # This is a good spot for wall decor if we have three basic walls in a
        # row, a space out front, and nothing else here.
        x, y = pos
        # if gb.get_bumpable_at_spot(pos) or not gb._map.get_wall(x,y) == maps.BASIC_WALL:
        #    return False
        wall = gb.get_wall(x, y)
        if x >= gb.width - 1 or y >= gb.height - 1:
            return False
        elif inspect.isclass(wall) and issubclass(wall, terrain.DoorTerrain):
            return False
        elif hasattr(wall, "TAKES_WALL_DECOR") and not wall.TAKES_WALL_DECOR:
            return False
        elif (self.is_basic_wall(gb, x - 1, y) and
              self.is_basic_wall(gb, x + 1, y) and
              not gb.tile_blocks_movement(x, y + 1, archi.mmode)):
            return True
        elif (self.is_basic_wall(gb, x, y - 1) and
              self.is_basic_wall(gb, x, y + 1) and
              not gb.tile_blocks_movement(x + 1, y, archi.mmode)):
            return True

    def get_west_north_wall_points(self, gb):
        # The western and northern walls are the two that should be visible to the player, and so this is where
        # wall mounted decor and waypoints will go.
        mylist = [(x, self.area.y) for x in range(self.area.x + 1, self.area.x + self.area.width - 2)]
        mylist += [(self.area.x, y) for y in range(self.area.y + 1, self.area.y + self.area.height - 2)]
        for m in [m for m in gb.contents if hasattr(m, "pos")]:
            if m.pos in mylist:
                mylist.remove(m.pos)
        return mylist

    def all_rooms(self):
        myrooms = list()
        myrooms.append(self)
        for c in self.contents:
            if hasattr(c, "all_rooms"):
                myrooms += c.all_rooms()
        return myrooms


class FuzzyRoom(Room):
    """A room without hard walls, with default ground floors."""

    def build(self, gb, archi):
        # Step Five: Actually draw the room, taking into account terrain already on map.
        archi = self.archi or archi
        for x in range(self.area.x + 1, self.area.x + self.area.width - 1):
            for y in range(self.area.y + 1, self.area.y + self.area.height - 1):
                archi.draw_fuzzy_ground(gb, x, y)


class NoWallRoom(Room):
    """A room that doesn't change the floor but gets rid of the walls."""

    def build(self, gb, archi):
        # Step Five: Actually draw the room, taking into account terrain already on map.
        archi = self.archi or archi
        for x in range(self.area.x + 1, self.area.x + self.area.width - 1):
            for y in range(self.area.y + 1, self.area.y + self.area.height - 1):
                gb.set_wall(x, y, None)


class OpenRoom(Room):
    """A room with floor and no walls."""

    def build(self, gb, archi):
        # Verify the area.
        self.dont_touch_edge(gb)
        archi = self.archi or archi
        gb.fill(self.area, floor=archi.floor_terrain, wall=None)

    def get_west_north_wall_points(self, gb):
        # The western and northern walls are the two that should be visible to the player, and so this is where
        # wall mounted decor and waypoints will go.
        mylist = [(x, self.area.y - 1) for x in range(self.area.x, self.area.x + self.area.width - 1)]
        mylist += [(self.area.x - 1, y) for y in range(self.area.y, self.area.y + self.area.height - 1)]
        for m in [m for m in gb.contents if hasattr(m, "pos")]:
            if m.pos in mylist:
                mylist.remove(m.pos)
        return mylist


class MostlyOpenRoom(OpenRoom):
    """A room with floor and no walls unless it's on the edge, in which case it gets walls."""

    def build(self, gb, archi):
        archi = self.archi or archi
        gb.fill(self.area, floor=archi.floor_terrain, wall=None)
        if self.area.x == 0:
            # Draw a west wall.
            gb.fill(pygame.Rect(0, self.area.y, 0, self.area.y + self.area.height - 1), wall=archi.wall_terrain)
        elif self.area.right == gb.width:
            # Draw an east wall.
            gb.fill(
                pygame.Rect(self.area.right - 1, self.area.y, self.area.right - 1, self.area.y + self.area.height - 1),
                wall=archi.wall_terrain)

        if self.area.y == 0:
            # Draw a north wall.
            gb.fill(pygame.Rect(self.area.x, 0, self.area.x + self.area.width - 1, 0), wall=archi.wall_terrain)
        elif self.area.bottom == gb.width:
            # Draw an south wall.
            gb.fill(pygame.Rect(self.area.x, self.area.bottom - 1, self.area.right - 1, self.area.bottom - 1),
                    wall=archi.wall_terrain)

    def get_west_north_wall_points(self, gb):
        # The western and northern walls are the two that should be visible to the player, and so this is where
        # wall mounted decor and waypoints will go.
        mylist = [(x, max(self.area.y - 1, 0)) for x in range(self.area.x, self.area.x + self.area.width - 1)]
        mylist += [(max(self.area.x - 1, 0), y) for y in range(self.area.y, self.area.y + self.area.height - 1)]
        for m in [m for m in gb.contents if hasattr(m, "pos")]:
            if m.pos in mylist:
                mylist.remove(m.pos)
        return mylist


class ClosedRoom(Room):
    """A room with hard walls."""

    def deal_with_empties(self, gb, empties, archi):
        """Fill this line with a wall, leaving at least one door or opening."""
        p2 = random.choice(empties)
        empties.remove(p2)
        archi.place_a_door(gb, p2[0], p2[1])
        if len(empties) > random.randint(1, 6):
            p2 = random.choice(empties)
            if self.no_door_nearby(gb, p2):
                empties.remove(p2)
                archi.place_a_door(gb, p2[0], p2[1])
        for pp in empties:
            gb.set_wall(pp[0], pp[1], archi.wall_terrain)
        del empties[:]

    def no_door_nearby(self, gb, p):
        door_found = False
        x, y = p
        for vec in gb.DELTA8:
            dx, dy = vec
            wall = gb.get_wall(x + dx, y + dy)
            if wall and wall is not True and issubclass(wall, terrain.DoorTerrain):
                door_found = True
                break
        return not door_found

    def probably_an_entrance(self, gb, p, vec, archi):
        return not self.probably_blocks_movement(gb, *p, archi) and not self.probably_blocks_movement(gb, p[0] + vec[0],
                                                                                               p[1] + vec[1], archi)

    def draw_wall(self, gb, points, vec, archi):
        empties = list()
        for p in points:
            if not gb.on_the_map(p[0] + vec[0], p[1] + vec[1]):
                gb.set_wall(p[0], p[1], archi.wall_terrain)
            elif self.probably_an_entrance(gb, p, vec, archi):
                empties.append(p)
            else:
                gb.set_wall(p[0], p[1], archi.wall_terrain)
                if empties:
                    self.deal_with_empties(gb, empties, archi)
        if empties:
            self.deal_with_empties(gb, empties, archi)

    def build(self, gb, archi):
        if not self.area:
            raise RoomError("ROOM ERROR: No area found for {} in {}".format(self, gb))
        archi = self.archi or archi
        self.dont_touch_edge(gb)

        # Fill the floor with BASIC_FLOOR, and clear room interior
        self.fill(gb, self.area, floor=archi.floor_terrain)
        self.fill(gb, self.area, wall=None)
        # Set the four corners to basic walls
        gb.set_wall(self.area.x - 1, self.area.y - 1, archi.wall_terrain)
        gb.set_wall(self.area.x + self.area.width, self.area.y - 1, archi.wall_terrain)
        gb.set_wall(self.area.x - 1, self.area.y + self.area.height, archi.wall_terrain)
        gb.set_wall(self.area.x + self.area.width, self.area.y + self.area.height, archi.wall_terrain)

        # Draw each wall. Harder than it sounds.
        if gb.on_the_map(self.area.x - 1, self.area.y):
            self.draw_wall(gb, animobs.get_line(self.area.x - 1, self.area.y, self.area.x - 1,
                                                self.area.y + self.area.height - 1), (-1, 0), archi)
        else:
            self.draw_wall(gb,
                           animobs.get_line(self.area.x, self.area.y, self.area.x, self.area.y + self.area.height - 1),
                           (-1, 0), archi)
        if gb.on_the_map(self.area.x + self.area.width, self.area.y):
            self.draw_wall(gb,
                           animobs.get_line(self.area.x + self.area.width, self.area.y, self.area.x + self.area.width,
                                            self.area.y + self.area.height - 1), (1, 0), archi)
        else:
            self.draw_wall(gb,
                           animobs.get_line(self.area.x + self.area.width - 1, self.area.y,
                                            self.area.x + self.area.width - 1,
                                            self.area.y + self.area.height - 1), (1, 0), archi)
        if gb.on_the_map(self.area.x, self.area.y - 1):
            self.draw_wall(gb, animobs.get_line(self.area.x, self.area.y - 1, self.area.x + self.area.width - 1,
                                                self.area.y - 1), (0, -1), archi)
        else:
            self.draw_wall(gb,
                           animobs.get_line(self.area.x, self.area.y, self.area.x + self.area.width - 1, self.area.y),
                           (0, -1), archi)
        if gb.on_the_map(self.area.x, self.area.y + self.area.height):
            self.draw_wall(gb, animobs.get_line(self.area.x, self.area.y + self.area.height,
                                                self.area.x + self.area.width - 1, self.area.y + self.area.height),
                           (0, 1), archi)
        else:
            self.draw_wall(gb, animobs.get_line(self.area.x, self.area.y + self.area.height - 1,
                                                self.area.x + self.area.width - 1, self.area.y + self.area.height - 1),
                           (0, 1), archi)

    def get_west_north_wall_points(self, gb):
        # The western and northern walls are the two that should be visible to the player, and so this is where
        # wall mounted decor and waypoints will go.
        mylist = [(x, self.area.y - 1) for x in range(self.area.x, self.area.x + self.area.width - 1)]
        mylist += [(self.area.x - 1, y) for y in range(self.area.y, self.area.y + self.area.height - 1)]
        for m in [m for m in gb.contents if hasattr(m, "pos")]:
            if m.pos in mylist:
                mylist.remove(m.pos)
        return mylist

# The following rooms are not meant to be used directly; subclass them and change the constants.

class ClumpyRoom(FuzzyRoom):
    CLUMP_FLOOR = -1
    CLUMP_WALL = -1
    CLUMP_DECOR = -1
    def build( self, gb, archi ):
        super().build(gb,archi)

        # Add some random blobs.
        if self.area.width > 4 and self.area.height > 4:
            max_clumps = (self.area.width * self.area.height)//2
            for t in range(random.randint(max_clumps//4,max_clumps)):
                x = random.randint(self.area.left+1,self.area.right-2)
                y = random.randint(self.area.top+1,self.area.bottom-2)
                gb.fill(pygame.Rect(x-1,y-1,random.randint(1,3),random.randint(1,3)),floor=self.CLUMP_FLOOR, wall=self.CLUMP_WALL, decor=self.CLUMP_DECOR)
        else:
            mydest = pygame.Rect(0,0,3,3)
            mydest.center = self.area.center
            gb.fill(mydest,floor=self.CLUMP_FLOOR, wall=self.CLUMP_WALL, decor=self.CLUMP_DECOR)


class MiniCityRoom(FuzzyRoom):
    ROAD_TERRAIN = -1
    ROADSIDE_TERRAIN = ()

    NODE_SIZE = 3

    MONKEY_HALL_WIDTH = 1
    CONNECTION_TARGET = 0.75

    ROADSIDE_FILL_TARGET = 0.6

    DIRS = ((1,0), (-1,0), (0,1), (0,-1))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connected_monkey_nodes = set()

    # Once again, I am implementing the Dungeon Monkey map generator.
    def mnode_to_map(self, x, y):
        x = x * self.NODE_SIZE + (self.NODE_SIZE - self.MONKEY_HALL_WIDTH)//2 + self.area.left
        y = y * self.NODE_SIZE + (self.NODE_SIZE - self.MONKEY_HALL_WIDTH)//2 + self.area.top
        return x, y

    @property
    def mnode_width(self):
        return self.area.width // self.NODE_SIZE

    @property
    def mnode_height(self):
        return self.area.height // self.NODE_SIZE

    def get_random_mnode(self):
        return random.randint(0, self.mnode_width - 1), random.randint(0, self.mnode_height - 1)

    def draw_mline(self, gb, mx1, my1, mx2, my2):
        # Draw a monkey line connecting the two monkey nodes.
        x1, y1 = self.mnode_to_map(mx1, my1)
        x2, y2 = self.mnode_to_map(mx2, my2)
        gb.fill(pygame.Rect(x1 - self.MONKEY_HALL_WIDTH//2, y1 - self.MONKEY_HALL_WIDTH//2, x2-x1+self.MONKEY_HALL_WIDTH, y2-y1+self.MONKEY_HALL_WIDTH), floor=self.ROAD_TERRAIN, wall=None)
        for x in range(mx1, mx2+1):
            for y in range(my1, my2+1):
                self._connected_monkey_nodes.add((x,y))

    def draw_random_l(self, gb):
        ox, oy = self.get_random_mnode()
        if (ox > 0 and random.randint(1,2) == 1) or ox == self.mnode_width - 1:
            x1 = max((ox - random.randint(1,4)), 0)
            x2 = ox
        else:
            x1 = ox
            x2 = min((ox + random.randint(1,4)), self.mnode_width - 1)
        self.draw_mline(gb, x1, oy, x2, oy)

        if (oy > 0 and random.randint(1,2) == 1) or oy == self.mnode_height - 1:
            y1 = max((oy - random.randint(1,4)), 0)
            y2 = oy
        else:
            y1 = oy
            y2 = min((oy + random.randint(1,4)), self.mnode_height - 1)
        self.draw_mline(gb, ox, y1, ox, y2)

    def is_valid_monkey_node(self, mx, my):
        return mx >= 0 and mx < self.mnode_width and my >= 0 and my < self.mnode_height

    def draw_random_line(self, gb, ox, oy):
        dirs = list(self.DIRS)
        random.shuffle(dirs)
        while dirs:
            dx, dy = dirs.pop()
            x2 = ox + dx
            y2 = oy + dy
            if (x2, y2) not in self._connected_monkey_nodes and self.is_valid_monkey_node(x2, y2):
                goal_length = random.randint(1,5)
                while goal_length > 0 and (x2,y2) not in self._connected_monkey_nodes and self.is_valid_monkey_node(x2 + dx, y2 + dy):
                    x2 += dx
                    y2 += dy
                    goal_length -= 1
                self.draw_mline(gb, min(ox,x2), min(oy,y2), max(ox,x2), max(oy,y2))

    def build(self, gb, archi):
        super().build(gb, archi)
        self._connected_monkey_nodes.clear()
        self.draw_random_l(gb)
        target = int(self.CONNECTION_TARGET * self.mnode_height * self.mnode_width)
        tries = 500
        while tries > 0 and len(self._connected_monkey_nodes) < target:
            origin = random.choice(list(self._connected_monkey_nodes))
            self.draw_random_line(gb, *origin)
            tries -= 1

        if self.ROADSIDE_TERRAIN:
            roadside_tiles = list()
            for x in range(self.area.left, self.area.left + self.area.width):
                for y in range(self.area.top, self.area.top + self.area.height):
                    if gb.get_floor(x,y) is not self.ROAD_TERRAIN:
                        for d in self.DIRS:
                            if gb.get_floor(x+d[0], y+d[1]) is self.ROAD_TERRAIN:
                                roadside_tiles.append((x, y))
                                break

            random.shuffle(roadside_tiles)
            target = int(self.ROADSIDE_FILL_TARGET * len(roadside_tiles))
            while target > 0 and roadside_tiles:
                x,y = roadside_tiles.pop()
                if gb.wall_wont_block(x, y, archi.mmode):
                    gb.set_wall(x, y, random.choice(self.ROADSIDE_TERRAIN))
                    target -= 1

