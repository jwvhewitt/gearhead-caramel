import pygame
import random
from .. import scenes

from . import plasma
from . import anchors
from . import mutator
from . import decor
from . import gapfiller
from . import converter
from . import prep
from . import rooms
from .rooms import Room
from . import architect
from . import terrset
from . import debugviewer


# A scene is constructed in the following steps:
# - The scene calls its PREPARE to initialize the map.
# - The child rooms are arranged; descendants are handled recursively
# - The child rooms are connected; descendants are handled recursively
# - The MUTATE attribute is called; descendants are mutated recursively
# - The render method is called; descendants are handled recursively
# - The WALL_FILTER attribute is called
# - The terrain is validated
# - Map contents are deployed; descendants are handled recursively
# - The DECORATE attribute is called; descendants are handled recursively
# - The contents of the map are cleaned

# Scene/Room options
#  GAPFILL*
#  MUTATE*
#  DECORATE*
#  DEFAULT_ROOM*
#  WALL_FILTER*
#  PREPARE*


#  *****************************
#  ***   SCENE  GENERATORS   ***
#  *****************************

class SceneGenerator(Room):
    """The blueprint for a scene."""

    EXPAND_AMOUNT = 15

    # DEFAULT_ROOM = rooms.FuzzyRoom
    def __init__(self, myscene, archi, default_room=None, gapfill=None, mutate=None, decorate=None, **kwargs):
        super(SceneGenerator, self).__init__(myscene.width, myscene.height, **kwargs)
        self.gb = myscene
        self.area = pygame.Rect(0, 0, myscene.width, myscene.height)
        self.archi = archi
        self.contents = myscene.contents
        if default_room:
            self.DEFAULT_ROOM = default_room
        if gapfill:
            self.GAPFILL = gapfill
        if mutate:
            self.MUTATE = mutate
        if decorate:
            self.DECORATE = decorate
        self.edge_positions = list(anchors.EDGES)
        random.shuffle((self.edge_positions))

    def make(self):
        """Assemble this stuff into a real map."""
        # Conduct the five steps of building a level.
        self._step_two_from_scratch()
        #if self.gb.DEBUG:
        #    self._stamp_debug_info()
        #    yield self.gb

        self.step_three(self.gb, self.archi)  # Connect contents for self, then children
        #if self.gb.DEBUG:
        #    self._stamp_debug_info()
        #    yield self.gb

        self.step_four(self.gb)  # Mutate for self, then children
        self.step_five(self.gb, self.archi)  # Render for self, then children
        #if self.gb.DEBUG:
        #    self._stamp_debug_info()
        #    yield self.gb

        # Convert undefined walls to real walls.
        self.archi.wall_converter(self)
        # self.gb.validate_terrain()

        self.step_six(self.gb, self.archi)  # Deploy for self, then children

        # Decorate for self, then children
        if self.archi and self.archi.decorate:
            self.archi.decorate(self.gb, self, self.archi)
        self.step_seven(self.gb, self.archi)

        self.clean_contents()

        return self.gb

    def _expand(self, raise_exception=True):
        self.gb.width += self.EXPAND_AMOUNT
        self.gb.height += self.EXPAND_AMOUNT
        self.gb.init_map()
        self.width = self.gb.width
        self.height = self.gb.height
        if raise_exception:
            raise rooms.RoomError("ROOM ERROR: {}: Map {} isn't big enough".format(str(self), str(self.__class__)), self)

    def _step_two_from_scratch(self):
        prepped_rooms = list()
        keep_going = True
        tries = 0
        while keep_going:
            try:
                for r in self.all_rooms():
                    r.area = None
                self.area = pygame.Rect(0, 0, self.gb.width, self.gb.height)

                prepped_rooms = self.archi.prepare(self) or ()  # Only the scene generator gets to prepare
                self.step_two(self.gb)  # Arrange contents for self, then children
                keep_going = False
            except rooms.RoomError as re:
                if len(re.args) > 1 and re.args[1] in prepped_rooms:
                    self._expand(False)
                tries += 1
                if tries > 100000:
                    raise RuntimeError("Runtime Error: {} could not generate scene within 100,000 tries. I dunno, this shouldn't be possible. But, I added an exception to prevent the game from locking up. A crash is better than an endless loop, don't you think?".format(self.gb))

    def _stamp_debug_info(self):
        for r in self.all_rooms():
            for x in range(r.area.x, r.area.x + r.area.width):
                for y in range(r.area.y, r.area.y + r.area.height):
                    if self.gb.on_the_map(x, y):
                        self.gb.set_visible(x, y, r)

    def clean_contents(self):
        # Remove unimportant things from the contents.
        for t in self.gb.contents[:]:
            if not hasattr(t, "pos"):
                self.gb.contents.remove(t)
                if isinstance(t, scenes.Scene):
                    self.gb.sub_scenes.append(t)


CITY_GRID_ROAD_OVERLAP = "Overlap the Road, Y'All!"


class CityGridGenerator(SceneGenerator):
    def __init__(self, myscene, archi, road_terrain, road_thickness=3, **kwargs):
        super(CityGridGenerator, self).__init__(myscene, archi, **kwargs)
        self.road_terrain = road_terrain
        self.road_thickness = road_thickness

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

        # Next we're gonna draw the road grid. I know that drawing is usually saved for near the end, but eff
        # that, I'm the programmer. I can do whatever I like.
        blocks = list()
        column_info = list()
        x = random.randint(2, 4)
        while x < (self.width - self.road_thickness):
            # Draw a N-S road here.
            self.fill(self.gb, pygame.Rect(x, 0, self.road_thickness, self.height), floor=self.road_terrain, wall=None)
            room_width = random.randint(7, 12)
            if x + room_width + self.road_thickness < self.width:
                column_info.append((x + self.road_thickness, room_width))
            x += self.road_thickness + room_width

        y = random.randint(2, 4)
        while y < (self.height - self.road_thickness - 7):
            # Draw a W-E road here.
            self.fill(self.gb, pygame.Rect(0, y, self.width, self.road_thickness), floor=self.road_terrain, wall=None)
            room_height = random.randint(7, 12)
            # Add the rooms.
            for col_x, col_width in column_info:
                myroom = pygame.Rect(col_x, y + self.road_thickness, col_width, room_height)
                if self.area.contains(myroom):
                    blocks.append(myroom)
            y += self.road_thickness + room_height

        # Assign areas for unplaced rooms.
        for r in self.contents:
            if hasattr(r, "area") and not r.area:
                if blocks:
                    myblock = random.choice(blocks)
                    blocks.remove(myblock)
                    if CITY_GRID_ROAD_OVERLAP in r.tags:
                        myblock.x -= 2
                        myblock.y -= 2
                        myblock.w += 2
                        myblock.h += 2
                    r.area = myblock
                else:
                    self._expand()

    def connect_contents(self, gb, archi):
        pass


IS_CITY_ROOM = "This room is part of the city"
IS_CONNECTED_ROOM = "This room is connected to the road network"


class PartlyUrbanGenerator(SceneGenerator):
    # Make a scene that is partly urban and partly not. Maybe it's partly wilderness. Maybe it's partly a cave system.
    # Only the architecture knows. Anyhow, it's similar to the CityGridGenerator but limits the city parts to a
    # limited rect.
    DO_DIRECT_CONNECTIONS = True

    def __init__(self, myscene, archi, road_terrain, road_thickness=2, urban_area=None, **kwargs):
        super().__init__(myscene, archi, **kwargs)
        self.road_terrain = road_terrain
        self.road_thickness = road_thickness
        if not urban_area:
            self.urban_area = rooms.Room(25, 25, anchor=anchors.middle, parent=self)
        else:
            self.urban_area = urban_area
            self.contents.append(urban_area)
            if not (hasattr(urban_area, "area") and urban_area.area):
                self.urban_area.area = pygame.Rect(0, 0, urban_area.width, urban_area.height)
                self.urban_area.area.center = self.area.center

        self.done_rooms = list()

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

        # Assign areas for unplaced rooms.
        ok = True
        for r in list(self.contents):
            if hasattr(r, "area") and not r.area:
                if IS_CITY_ROOM in r.tags:
                    self.contents.remove(r)
                    self.urban_area.contents.append(r)
                else:
                    ok = ok and self.find_spot_for_room(closed_area, r)
        if not ok:
            self._expand()

    def build(self, gb, archi):
        super().build(gb, archi)
        frontier = [r for r in self.all_rooms() if IS_CONNECTED_ROOM in r.tags]
        if frontier:
            start_point = random.choice(frontier)
            frontier.remove(start_point)
            self.done_rooms.append(start_point)
            frontier.sort(key=lambda r: gb.distance(start_point.area.center, r.area.center))
            while frontier:
                nuroom = frontier.pop(0)
                connect_to = min(self.done_rooms, key=lambda r: gb.distance(nuroom.area.center, r.area.center))
                self.draw_road(gb, nuroom.area.centerx, nuroom.area.centery, connect_to.area.centerx, connect_to.area.centery)
                if nuroom.anchor:
                    #print("Anchoring...")
                    self.draw_road_segment(gb, nuroom.area.centerx, nuroom.area.centery, *nuroom.anchor(nuroom.area, None))
                self.done_rooms.append(nuroom)

    def step_five(self, gb, archi):
        # Overriding this method because we can only draw the walking areas after the buildings have been built.
        super().step_five(gb, archi)
        for myroom in self.done_rooms:
            self.draw_walking_area(myroom)


    def draw_walking_area(self, myroom):
        if hasattr(myroom, "footprint") and myroom.footprint:
            self.fill(self.gb, myroom.footprint.inflate(2,2), floor=self.road_terrain)

    def draw_road_segment(self, gb, x1, y1, x2, y2):
        path = scenes.animobs.get_line(x1, y1, x2, y2)
        for p in path:
            mydest = pygame.Rect(0,0,self.road_thickness, self.road_thickness)
            mydest.center = p
            self.fill(gb, mydest, floor=self.road_terrain, wall=None, decor=None)

    def draw_road(self, gb: scenes.Scene, x1, y1, x2, y2):
        if random.randint(1, 2) == 1:
            cx, cy = x1, y2
        else:
            cx, cy = x2, y1
        self.draw_road_segment(gb, x1, y1, cx, cy)
        self.draw_road_segment(gb, x2, y2, cx, cy)


class PackedBuildingGenerator(SceneGenerator):
    def put_room_north(self, closed_room, open_room):
        open_room.midbottom = closed_room.midtop
        open_room.y -= 1
        open_room.clamp_ip(self.area)

    def put_room_south(self, closed_room, open_room):
        open_room.midtop = closed_room.midbottom
        open_room.y += 1
        open_room.clamp_ip(self.area)

    def put_room_west(self, closed_room, open_room):
        open_room.midright = closed_room.midleft
        open_room.x -= 1
        open_room.clamp_ip(self.area)

    def put_room_east(self, closed_room, open_room):
        open_room.midleft = closed_room.midright
        open_room.x += 1
        open_room.clamp_ip(self.area)

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

        # Assign areas for unplaced rooms.
        positions = (self.put_room_east, self.put_room_north, self.put_room_south, self.put_room_west)
        rooms_to_add = [r for r in self.contents if hasattr(r, "area") and not r.area]
        random.shuffle(rooms_to_add)
        for r in rooms_to_add:
            myrect = pygame.Rect(0, 0, r.width, r.height)
            candidates = list()
            for croom in closed_area:
                for dirf in positions:
                    dirf(croom, myrect)
                    if myrect.inflate(2, 2).collidelist(closed_area) == -1:
                        candidates.append((dirf, croom))
            if candidates:
                dirf, croom = random.choice(candidates)
                dirf(croom, myrect)
                r.area = myrect
                closed_area.append(myrect)
            else:
                self._expand()

    def connect_contents(self, gb, archi):
        # Step Three: Connect all rooms in contents, making trails on map.

        # Generate list of rooms.
        connected = list()
        unconnected = [r for r in self.contents if hasattr(r, "area")]
        if unconnected:
            room1 = random.choice(unconnected)
            unconnected.remove(room1)
            connected.append(room1)
            unconnected.sort(key=room1.find_distance_to)

        # Process them
        for r in unconnected:
            # Connect r to a connected room
            croom = min(connected, key=r.find_distance_to)
            self.draw_L_connection(gb, r.area.centerx, r.area.centery, croom.area.centerx, croom.area.centery, archi)
            connected.append(r)

    def thin_draw_direct_connection(self, gb, x1, y1, x2, y2, archi):
        # Paths between rooms will only be one block wide.
        path = scenes.animobs.get_line(x1, y1, x2, y2)
        for p in path:
            archi.draw_fuzzy_ground(gb, p[0], p[1])


class HallwayBuildingGenerator(SceneGenerator):
    def __init__(self, myscene, archi, hall_terrain, **kwargs):
        super().__init__(myscene, archi, **kwargs)
        self.hall_terrain = hall_terrain

    def divide(self, myrect: pygame.Rect):
        if myrect.w >= 19 and (random.randint(1,2) == 1 or myrect.h < 19):
            # Divide horizontally.
            x = random.randint(7, myrect.w-12)
            self.gb.fill(pygame.Rect(myrect.x+1, myrect.y, 3, myrect.h), floor=self.hall_terrain, wall=None)
            return self.divide(pygame.Rect(myrect.x, myrect.y, x, myrect.h)) + \
                   self.divide(pygame.Rect(myrect.x+x+5, myrect.y, myrect.w-x-5, myrect.h))

        elif myrect.h >= 19:
            # Divide vertically.
            y = random.randint(7, myrect.h-12)
            self.gb.fill(pygame.Rect(myrect.x, myrect.y+y, myrect.w, 3), floor=self.hall_terrain, wall=None)
            return self.divide(pygame.Rect(myrect.x, myrect.y, myrect.w, y)) + \
                   self.divide(pygame.Rect(myrect.x, myrect.y+y+5, myrect.w, myrect.h-y-5))

        else:
            # No divisions possible.
            return [myrect]

    def connect_to_hallway(self, myrect: pygame.Rect):
        possible_exits = list()
        for x in range(myrect.left+1, myrect.right):
            if self.gb.on_the_map(x, myrect.top-2) and not self.gb.get_wall(x, myrect.top-2):
                possible_exits.append((x, myrect.top-1))
            if self.gb.on_the_map(x, myrect.bottom+2) and not self.gb.get_wall(x, myrect.bottom+2):
                possible_exits.append((x, myrect.bottom+1))
        for y in range(myrect.top+1, myrect.bottom):
            if self.gb.on_the_map(myrect.left-2, y) and not self.gb.get_wall(myrect.left-2, y):
                possible_exits.append((myrect.left-1, y))
            if self.gb.on_the_map(myrect.right+2, y) and not self.gb.get_wall(myrect.right+2, y):
                possible_exits.append((myrect.right+1, y))
        if possible_exits:
            e = random.choice(possible_exits)
            self.archi.place_a_door(self.gb, *e)
            if random.randint(1,2) == 1:
                e2 = random.choice(possible_exits)
                if abs(e[0] - e2[0]) + abs(e[1] - e2[1]) > 3:
                    self.archi.place_a_door(self.gb, *e2)
        else:
            print("ERROR: No possible exits found for a room!")

    def arrange_contents(self, gb):
        # Step Two: Arrange subcomponents within this area.
        # Because this is a special map type, we're gonna play by our own rules.
        closed_area = list()
        # Pre-placed rooms? Don't exist.
        for r in self.contents:
            if hasattr(r, "area") and r.area:
                r.area = None

        # Step two- lay out the rooms first.
        rooms = self.divide(self.area.inflate(-2,-2))

        # Rooms with defined anchors? Do exist. Stick them in the closest room possible.
        for r in self.contents:
            if hasattr(r, "anchor") and r.anchor and hasattr(r, "area"):
                myrect = pygame.Rect(0, 0, r.width, r.height)
                r.anchor(self.area, myrect)
                for rarea in rooms:
                    if rarea.colliderect(myrect):
                        r.area = rarea
                        closed_area.append(rarea)
                        rooms.remove(rarea)
                        self.connect_to_hallway(rarea)
                        break

        # Assign areas for unplaced rooms.
        for r in self.contents:
            if hasattr(r, "area") and not r.area:
                if rooms:
                    myblock = random.choice(rooms)
                    rooms.remove(myblock)
                    r.area = myblock
                    self.connect_to_hallway(myblock)
                else:
                    self._expand()

    def connect_contents(self, gb, archi):
        pass
