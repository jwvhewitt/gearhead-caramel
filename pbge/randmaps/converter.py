import random
from . import plasma

#  **********************
#  ***   CONVERTERS   ***
#  **********************

class BasicConverter( object ):
    """Convert True walls to the provided terrain."""
    def __init__( self, terr ):
        if not terr:
            self.terr = None
        else:
            self.terr = terr

    def __call__( self, mapgen ):
        for x in range( mapgen.width ):
            for y in range( mapgen.height ):
                if mapgen.gb._map[x][y].wall is True:
                    mapgen.gb._map[x][y].wall = self.terr

class PlasmaConverter(object):
    def __init__(self, lowall, medwall, hiwall, loground=0.2, higround=0.7, maxloground=0.4, maxhiground=0.4):
        self.lowall = lowall
        self.medwall = medwall
        self.hiwall = hiwall
        self.loground = loground
        self.higround = higround
        self.maxloground = maxloground
        self.maxhiground = maxhiground

    def __call__(self, mapgen):
        if not hasattr(mapgen,"plasma") or not mapgen.plasma:
            mapgen.plasma = plasma.Plasma(map_width=mapgen.area.w, map_height=mapgen.area.h)
        all_plasma_values = list()
        for column in mapgen.plasma.map[:mapgen.width]:
            all_plasma_values += column[:mapgen.height]
        all_plasma_values.sort()
        self.loground = min(self.loground,all_plasma_values[int(len(all_plasma_values)*self.maxloground)])
        self.higround = max(self.higround,all_plasma_values[int(len(all_plasma_values)*self.maxhiground)])
        for x in range( mapgen.width ):
            for y in range( mapgen.height ):
                if mapgen.gb._map[x][y].wall is True:
                    if mapgen.plasma.map[x][y] < self.loground:
                        mapgen.gb._map[x][y].wall = self.lowall
                    elif mapgen.plasma.map[x][y] < self.higround:
                        mapgen.gb._map[x][y].wall = self.medwall
                    else:
                        mapgen.gb._map[x][y].wall = self.hiwall



class FloorConverter( object ):
    """Convert True walls to the provided terrain."""
    def __init__( self, terr ):
        self.terr = terr

    def __call__( self, mapgen ):
        for x in range( mapgen.width ):
            for y in range( mapgen.height ):
                if mapgen.gb._map[x][y].wall is True:
                    mapgen.gb._map[x][y].wall = None
                    mapgen.gb._map[x][y].floor = self.terr


