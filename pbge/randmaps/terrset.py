from rooms import Room
from .. import container,scenes
import inspect
import random

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
    def __init__(self,tags=(), anchor=None, parent=None, archi=None, waypoints=dict()):
        self.width = max([len(a) for a in self.TERRAIN_MAP]) + 2
        self.height = len(self.TERRAIN_MAP) + 2
        self.tags = tags
        self.anchor = anchor
        self.archi = archi
        self.area = None
        self.contents = container.ContainerList(owner=self)
        self.waypoints = dict()
        self.waypoints.update(waypoints)
        if parent:
            parent.contents.append( self )

    def build( self, scene, archi):
        # x0,y0 is the NorthWest corner of the terrain.
        #x0,y0 = self.area.topleft
        x0 = self.area.x + 1
        y0 = self.area.y + 1
        y = y0
        for row in self.TERRAIN_MAP:
            x = x0
            for col in row:
                if scene.on_the_map(x,y) and col is not None:
                    if inspect.isclass( col ) and issubclass(col,scenes.terrain.Terrain):
                        scene._map[x][y].wall = col
                    else:
                        scene._map[x][y].wall = self.TERRAIN_TYPE
                        scene.data[(x,y)] = col
                x += 1
            y += 1
        for k,v in self.waypoints.iteritems():
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
    GF1_TILE = (15,20,)
    GF2_TILE = (16,21)
    GF3_TILE = (17,22)
    GF4_TILE = (18,23)
    GF5_TILE = (19,24)
    def __init__(self,tags=(), dimx=0,dimy=0,dimz=0,anchor=None, parent=None, archi=None, waypoints=dict()):
        self.TERRAIN_MAP = list()
        dimx = dimx or random.randint(5,8)
        dimy = dimy or random.randint(5,8)
        dimz = dimz or random.randint(2,5)
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
            else:
                myrow += [None,] * (mapy - dimy + 1)
                myrow.append(random.choice(self.GF1_TILE))
                for t in range(dimx-2):
                    myrow.append(random.choice(self.GF2_TILE))
                myrow.append(random.choice(self.GF3_TILE))
            # Start on the East Face of the building, as appropriate.
            if mapy > 0 and mapy < dimz:
                myrow += [random.choice(self.GF4_TILE) for x in range(min(max(mapy-1,0),dimz-1))]
                myrow += [random.choice(self.GF5_TILE)]
            elif mapy >= dimz:
                myrow += [random.choice(self.GF4_TILE) for x in range(min(max(dimy + dimz - mapy - 2, 0), dimz - 1))]
            self.TERRAIN_MAP.append(myrow)
        super(BuildingSet,self).__init__(tags,anchor,parent,archi,waypoints)
