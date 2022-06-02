from . import plasma
import pygame
import random

#   ******************
#   ***  PREPPERS  ***
#   ******************
#
# Before map generation proper takes place, the grid must be prepared.
# Generally this will involve setting a terrain for the floor of each tile
# and setting the wall values to True. Note that "True" is not a valid terrain
# type- it will be converted to proper walls later on in the generation process.
#
# The prepper may also set the map generator's plasma attribute.

class BasicPrep( object ):
    """Fill map with True walls and basic floors."""
    def __init__( self, terr ):
        self.terr = terr

    def __call__( self, mapgen ):
        mapgen.fill( mapgen.gb, mapgen.area, floor=self.terr, wall=True )

class HeightfieldPrep( object ):
    """Use a plasma map to fill with three levels of terrain"""
    def __init__( self, loterr, medterr, hiterr, loground=0.2, higround=0.7, maxloground=0.3, maxhiground=0.5 ):
        self.loterr = loterr
        self.medterr = medterr
        self.hiterr = hiterr
        self.loground = loground
        self.higround = higround
        self.maxloground = maxloground
        self.maxhiground = maxhiground
    def __call__( self, mapgen ):
        mapgen.plasma = plasma.Plasma(map_width=mapgen.area.w,map_height=mapgen.area.h)
        all_plasma_values = list()
        for column in mapgen.plasma.map[:mapgen.width]:
            all_plasma_values += column[:mapgen.height]
        all_plasma_values.sort()
        self.loground = min(self.loground,all_plasma_values[int(len(all_plasma_values)*self.maxloground)])
        self.higround = max(self.higround,all_plasma_values[int(len(all_plasma_values)*self.maxhiground)])
        for x in range( mapgen.width ):
            for y in range( mapgen.height ):
                if mapgen.plasma.map[x][y] < self.loground:
                    mapgen.gb._map[x][y].floor = self.loterr
                elif mapgen.plasma.map[x][y] < self.higround:
                    mapgen.gb._map[x][y].floor = self.medterr
                    mapgen.gb._map[x][y].wall = True
                else:
                    mapgen.gb._map[x][y].floor = self.hiterr
                    mapgen.gb._map[x][y].wall = True


class GradientPrep( object ):
    """Make horizontal or vertical bands of terrain with some overlap."""
    def __init__( self, bands, overlap=2, vertical=True ):
        # Bands is a list of (terrain, width) pairs which describe the bands.
        self.bands = bands
        self.overlap = overlap
        self.vertical = vertical

    def adjust_offset(self, offset):
        if random.randint(1,23) == 5:
            offset = 0
        offset = offset + random.randint(0, 1) - random.randint(0, 1)
        return max(min(offset, self.overlap), -self.overlap)

    def __call__( self, mapgen ):
        # First, do the basic filling.
        mapgen.fill( mapgen.gb, mapgen.area, wall=True )
        band_start = 0
        for band in self.bands:
            if self.vertical:
                mydest = pygame.Rect(0, band_start, mapgen.width, band[1])
            else:
                mydest = pygame.Rect(band_start, 0, band[1], mapgen.height)
            if band is self.bands[-1]:
                # Error check- we want to make sure the map is completely filled! So, if this is the last band, make
                # sure that it reaches the bottom right corner of the map.
                mydest.bottomright = (mapgen.width, mapgen.height)
            mapgen.fill(mapgen.gb, mydest, floor=band[0])
            if self.vertical:
                band_start = mydest.bottom
            else:
                band_start = mydest.right

        # Second, randomize those bands up a bit.
        baseline = self.bands[0][1]
        for b in range(len(self.bands)-1):
            offset = random.randint(0, self.overlap) - random.randint(0, self.overlap)
            b0,b1 = self.bands[b], self.bands[b+1]
            if self.vertical:
                for x in range(mapgen.width):
                    if offset < 0:
                        for dy in range(abs(offset-1)):
                            mapgen.gb.set_floor(x, baseline - dy, b1[0])
                    elif offset > 0:
                        for dy in range(offset+1):
                            mapgen.gb.set_floor(x, baseline + dy, b0[0])
                    offset = self.adjust_offset(offset)
            else:
                for y in range(mapgen.height):
                    if offset < 0:
                        for dx in range(abs(offset-1)):
                            mapgen.gb.set_floor(baseline - dx, y, b1[0])
                    elif offset > 0:
                        for dx in range(offset+1):
                            mapgen.gb.set_floor(baseline + dx, y, b0[0])
                    offset = self.adjust_offset(offset)
            baseline += b1[1]

