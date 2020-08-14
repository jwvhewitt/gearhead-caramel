from . import converter
from . import mutator
from . import prep
import random
from . import decor
from . import rooms

# An Architecture defines a style for a random map. The same architecture can
# be shared across several scenes, ensuring a consistent style throughout.
#
# IMPORTANT: You **MUST** define a floor terrain, at the very least! Otherwise you'll get a void.

class Architecture( object ):
    DEFAULT_BIOME = None
    DEFAULT_GAPFILL = None
    DEFAULT_MUTATE = None
    DEFAULT_DECORATE = None
    DEFAULT_CONVERTER = None
    DEFAULT_FLOOR_TERRAIN = None
    DEFAULT_PREPARE = None
    DEFAULT_WALL_TERRAIN = None
    DEFAULT_OPEN_DOOR_TERRAIN = None
    DEFAULT_DOOR_CLASS = None
    DEFAULT_ROOM_CLASSES = ()
    def __init__(self, floor_terrain=None, wall_converter=None, prepare=None, biome=None, desctags=None, gapfill=None,
                 mutate=None, decorate=None, wall_terrain=None, open_door_terrain=None, door_class=None, room_classes=None):
        self.biome = biome or self.DEFAULT_BIOME
        if not desctags:
            desctags = list()
        self.desctags = desctags
        self.gapfill = gapfill or self.DEFAULT_GAPFILL
        self.mutate = mutate or self.DEFAULT_MUTATE
        self.decorate = decorate or self.DEFAULT_DECORATE
        self.floor_terrain = floor_terrain or self.DEFAULT_FLOOR_TERRAIN
        self.prepare = prepare or self.DEFAULT_PREPARE
        if not self.prepare:
            self.prepare = prep.BasicPrep( self.floor_terrain )
        self.wall_terrain = wall_terrain or self.DEFAULT_WALL_TERRAIN
        self.wall_converter = wall_converter or self.DEFAULT_CONVERTER
        if not self.wall_converter:
            self.wall_converter = converter.BasicConverter(self.wall_terrain)
        self.open_door_terrain = open_door_terrain or self.DEFAULT_OPEN_DOOR_TERRAIN
        self.door_class = door_class or self.DEFAULT_DOOR_CLASS
        self.room_classes = room_classes or self.DEFAULT_ROOM_CLASSES

    def draw_fuzzy_ground( self, gb, x, y ):
        # In general, just erase the wall to expose the floor underneath,
        # adding a floor if need be.
        if gb.on_the_map(x,y):
            gb._map[x][y].wall = None
            if gb._map[x][y].blocks_walking() or gb._map[x][y].altitude != 0:
                gb._map[x][y].floor = self.floor_terrain

    def place_a_door(self, gb, x, y):
        if self.door_class and random.randint(1,10) != 4:
            mydoors = gb.get_waypoints((x,y))
            if not any(isinstance(wp,self.door_class) for wp in mydoors):
                door = self.door_class()
                door.place(gb,(x,y))
        else:
            gb.set_wall(x,y,self.open_door_terrain)

    def get_a_room(self):
        if self.room_classes:
            return random.choice(self.room_classes)
        else:
            return rooms.FuzzyRoom
