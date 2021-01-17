from .rooms import Room
from .. import container,scenes
import inspect
import random
import itertools

class TerrSet( Room ):
    # A Terrainset is a handler for TerrSetTerrain terrain.
    # Terrain Type is the TerrSetTerrain to be used.
    # TerrainMap is a tuple of tuples giving frame numbers for
    # the tiles. If a tile is to be left out, use None.
    TERRAIN_TYPE = None
    TERRAIN_MAP = (
        (None,None,None),
        (None,None),
        (None,None,None),
    )
    WAYPOINT_POS = dict()
    def __init__(self, tags=(), anchor=None, parent=None, archi=None, waypoints=dict(),border=1,
                 dont_calc_dimensions=False, duck_dict=None):
        self.border = border
        if dont_calc_dimensions:
            self.width,self.height = random.randint(7,15), random.randint(7,15)
        else:
            self.width = max([len(a) for a in self.TERRAIN_MAP]) + 2*border
            self.height = len(self.TERRAIN_MAP) + 2*border
        self.tags = tags
        self.anchor = anchor
        self.archi = archi
        self.area = None
        self.contents = container.ContainerList(owner=self)
        self.waypoints = dict()
        self.waypoints.update(waypoints)
        self.duck_dict=duck_dict
        if parent:
            parent.contents.append( self )

    def build( self, scene, archi):
        # x0,y0 is the NorthWest corner of the terrain.
        #x0,y0 = self.area.topleft
        x0 = self.area.x + self.border
        y0 = self.area.y + self.border
        y = y0
        for row in self.TERRAIN_MAP:
            x = x0
            for col in row:
                if scene.on_the_map(x,y) and col is not None:
                    if inspect.isclass( col ) and issubclass(col,scenes.terrain.Terrain):
                        scene._map[x][y].wall = col
                    elif self.duck_dict:
                        scene._map[x][y].wall = scenes.terrain.DuckTerrain(**self.duck_dict, frame=col)
                    else:
                        scene._map[x][y].wall = self.TERRAIN_TYPE
                        scene.data[(x,y)] = col
                x += 1
            y += 1
        for k,v in self.waypoints.items():
            x,y = self.WAYPOINT_POS.get(k,(0,0))
            x += x0
            y += y0
            v.place(scene,(x,y))


class BuildingSet( TerrSet ):
    ULT_TILE = (6,)
    UMT_TILE = (5,)
    URT_TILE = (4,14)
    MLT_TILE = (7,)
    MMT_TILE = (8,)
    MRT_TILE = (3,13)
    LLT_TILE = (0,9)
    LMT_TILE = (1,10,)
    LRT_TILE = (2,11,12)
    UF1_TILE = (15,20,)
    UF2_TILE = (16,21)
    UF3_TILE = (17,22)
    UF4_TILE = (18,23)
    UF5_TILE = (19,24)
    GF1_TILE = (15,20,)
    GF2_TILE = (16,21)
    GF3_TILE = (17,22)
    GF4_TILE = (18,23)
    GF5_TILE = (19,24)

    DEFAULT_DECOR_OPTIONS = ()
    def __init__(self, tags=(), anchor=None, parent=None, archi=None, waypoints=dict(), border=1, decor_options=(),
                 door_sign=None, other_sign=None, duck_dict=None):
        # door_sign is a tuple containing the (south,east) versions of terrain to place above the door.
        # other_sign is a tuple containing the (south,east) versions of terrain to place above the other waypoint.
        self.TERRAIN_MAP = list()
        self.door_sign = door_sign
        self.other_sign = other_sign

        self.decor_options = decor_options or self.DEFAULT_DECOR_OPTIONS

        # Create the WAYPOINT_POS dictionary. Add a spot for a door and a spot for some other reachable ground tile.
        self.WAYPOINT_POS = dict()

        super().__init__(tags,anchor,parent,archi,waypoints,border,dont_calc_dimensions=True, duck_dict=duck_dict)

    def design(self):
        # height = dimy + dimz - 1 + 2 * self.border
        # width = dimx + dimz - 1 + 2 * self.border
        dimz = min(random.randint(3,7),random.randint(3,7))
        while ( self.area.w - dimz + 1 - 2 * self.border < 3 or self.area.h - dimz + 1 - 2 * self.border < 3 ) and dimz > 2:
            dimz -= 1

        dimx = self.area.w - dimz + 1 - 2 * self.border
        dimy = self.area.h - dimz + 1 - 2 * self.border

        self.dimz = dimz
        for mapy in range(dimy + dimz - 1):
            myrow = list()
            if mapy == 0:
                myrow.append(random.choice(self.ULT_TILE))
                for t in range(dimx-2):
                    myrow.append(random.choice(self.UMT_TILE))
                myrow.append(random.choice(self.URT_TILE))
            elif mapy < (dimy - 1):
                myrow.append(random.choice(self.MLT_TILE))
                for t in range(dimx-2):
                    myrow.append(random.choice(self.MMT_TILE))
                myrow.append(random.choice(self.MRT_TILE))
            elif mapy == (dimy-1):
                myrow.append(random.choice(self.LLT_TILE))
                for t in range(dimx-2):
                    myrow.append(random.choice(self.LMT_TILE))
                myrow.append(random.choice(self.LRT_TILE))
            elif mapy == dimy + dimz - 2:
                myrow += [None,] * (mapy - dimy + 1)
                myrow.append(random.choice(self.GF1_TILE))
                for t in range(dimx-2):
                    myrow.append(random.choice(self.GF2_TILE))
                myrow.append(random.choice(self.GF3_TILE))

            else:
                myrow += [None,] * (mapy - dimy + 1)
                myrow.append(random.choice(self.UF1_TILE))
                for t in range(dimx-2):
                    myrow.append(random.choice(self.UF2_TILE))
                myrow.append(random.choice(self.UF3_TILE))
            # Start on the East Face of the building, as appropriate.
            if mapy > 0 and mapy < dimz:
                myrow += [random.choice(self.UF4_TILE) for x in range(min(max(mapy-1,0),dimz-1,dimy-2))]
                if mapy == dimz-1:
                    myrow += [random.choice(self.GF5_TILE)]
                else:
                    myrow += [random.choice(self.UF5_TILE)]
            elif mapy >= dimz and dimy + dimz - mapy - 2 > 0:
                myrow += [random.choice(self.UF4_TILE) for x in range(min(max(dimy + dimz - mapy - 2, 0), dimz - 1) - 1)]
                myrow.append(random.choice(self.GF4_TILE))
            self.TERRAIN_MAP.append(myrow)

        # Create the set of all terrain points.
        self.decor_tiles = set()
        for y,row in enumerate(self.TERRAIN_MAP):
            for x,value in enumerate(row):
                if value:
                    self.decor_tiles.add((x,y))

        if random.randint(1,2) == 1:
            self.WAYPOINT_POS["DOOR"] = (random.randint(1,dimx-2)+dimz-1,dimy-2+dimz)
            self.WAYPOINT_POS["OTHER"] = (dimx - 2 + dimz, random.randint(1,dimy-2)+dimz-1)
        else:
            self.WAYPOINT_POS["DOOR"] = (dimx - 2 + dimz, random.randint(1,dimy-2)+dimz-1)
            self.WAYPOINT_POS["OTHER"] = (random.randint(1, dimx - 2) + dimz - 1, dimy - 2 + dimz)
        self.decor_tiles.remove(self.WAYPOINT_POS["DOOR"])
        self.decor_tiles.remove(self.WAYPOINT_POS["OTHER"])

        # Add positions for the optional waypoints.
        if self.door_sign:
            x,y = self.WAYPOINT_POS["DOOR"]
            self.WAYPOINT_POS["DOOR_SIGN"] = (x-1,y-1)
            if self.WAYPOINT_POS["DOOR_SIGN"] in self.decor_tiles:
                self.decor_tiles.remove(self.WAYPOINT_POS["DOOR_SIGN"])
            if self.TERRAIN_MAP[y][x] in self.GF2_TILE:
                self.waypoints["DOOR_SIGN"] = self.door_sign[0]
            else:
                self.waypoints["DOOR_SIGN"] = self.door_sign[1]
        if self.other_sign:
            x,y = self.WAYPOINT_POS["OTHER"]
            self.WAYPOINT_POS["OTHER_SIGN"] = (x-1,y-1)
            if self.WAYPOINT_POS["OTHER_SIGN"] in self.decor_tiles:
                self.decor_tiles.remove(self.WAYPOINT_POS["OTHER_SIGN"])
            if self.TERRAIN_MAP[y][x] in self.GF2_TILE:
                self.waypoints["OTHER_SIGN"] = self.other_sign[0]
            else:
                self.waypoints["OTHER_SIGN"] = self.other_sign[1]


        # Add the decor.
        if self.decor_options:
            for t in range(random.randint(5,10)):
                mydecor = random.choice(self.decor_options)
                self.install_decor(mydecor)


    def install_decor(self,decortype):
        possible_points = [p for p in self.decor_tiles if decortype.is_legal_point(self,p)]
        if possible_points:
            decortype.apply(self,random.choice(possible_points))

    def is_wall_section(self,x,y):
        try:
            return self.TERRAIN_MAP[y][x] in self.GF2_TILE + self.GF4_TILE + self.UF2_TILE + self.UF4_TILE
        except IndexError:
            return False
    def is_ground_level(self,x,y):
        return (y == len(self.TERRAIN_MAP)-1) or ((y < len(self.TERRAIN_MAP)-1) and (y >= self.dimz - 1 ) and (x == len(self.TERRAIN_MAP[y])-1))

    def build( self, scene, archi):
        self.design()
        TerrSet.build(self,scene,archi)


class WallDecor(object):
    def __init__(self,south_terrain=(),east_terrain=()):
        self.south_terrain = south_terrain
        self.east_terrain = east_terrain
    def is_legal_point(self,terrset,p):
        x,y= p
        return terrset.is_wall_section(x,y)
    def apply(self,terrset,p):
        id = "{}_{}_{}".format(hash(self),hash(terrset),len(terrset.WAYPOINT_POS))
        x,y = p
        if terrset.TERRAIN_MAP[y][x] in terrset.GF2_TILE + terrset.UF2_TILE:
            terrset.waypoints[id] = random.choice(self.south_terrain)
        else:
            terrset.waypoints[id] = random.choice(self.east_terrain)
        terrset.WAYPOINT_POS[id] = p
        terrset.decor_tiles.remove(p)

class RoofDecor(object):
    def __init__(self,terrain_list=()):
        self.terrain_list = terrain_list
    def is_legal_point(self,terrset,p):
        x,y= p
        return terrset.TERRAIN_MAP[y][x] in terrset.MMT_TILE
    def apply(self,terrset,p):
        id = "{}_{}_{}".format(hash(self),hash(terrset),len(terrset.WAYPOINT_POS))
        terrset.waypoints[id] = random.choice(self.terrain_list)
        terrset.WAYPOINT_POS[id] = p
        terrset.decor_tiles.remove(p)

class WallHanger(object):
    def __init__(self,south_top,south_mid,south_bottom,east_top,east_mid,east_bottom):
        self.south_top = south_top
        self.south_mid = south_mid
        self.south_bottom = south_bottom
        self.east_top = east_top
        self.east_mid = east_mid
        self.east_bottom = east_bottom

    def get_terrain_points(self,terrset,x,y):
        mylist = [(x,y)]
        while (y < len(terrset.TERRAIN_MAP)) and not terrset.is_ground_level(x,y):
            x += 1
            y += 1
            mylist.append((x,y))
        return mylist

    def is_legal_point(self,terrset,p):
        x,y= p
        if terrset.is_wall_section(x,y):
            all_ok = True
            for p in self.get_terrain_points(terrset,x,y):
                if p not in terrset.decor_tiles:
                    all_ok = False
                    break
            return all_ok

    def apply(self,terrset,op):
        x,y = op
        for p in self.get_terrain_points(terrset, x, y):
            id = "{}_{}_{}_{}".format(hash(self),hash(terrset),len(terrset.WAYPOINT_POS),p)
            if terrset.TERRAIN_MAP[y][x] in terrset.GF2_TILE + terrset.UF2_TILE:
                if p == op:
                    terrset.waypoints[id] = self.south_top
                elif terrset.is_ground_level(*p):
                    terrset.waypoints[id] = self.south_bottom
                else:
                    terrset.waypoints[id] = self.south_mid
            else:
                if p == op:
                    terrset.waypoints[id] = self.east_top
                elif terrset.is_ground_level(*p):
                    terrset.waypoints[id] = self.east_bottom
                else:
                    terrset.waypoints[id] = self.east_mid
            terrset.WAYPOINT_POS[id] = p
            terrset.decor_tiles.remove(p)

