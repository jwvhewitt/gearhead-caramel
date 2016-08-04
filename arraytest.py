
import random

class SingTerrain( object ):
    # A singleton terrain class; use these objects as tokens for maps.
    def __init__( self, ident, spritesheet = "", block_vision = False, block_walk = False, block_fly = False, frame = 0 ):
        # ident should be the module-level name of this stat.
        self.ident = ident
        self.spritesheet = spritesheet
        self.block_vision = block_vision
        self.block_walk = block_walk
        self.block_fly = block_fly
        self.frame = frame
    def render( self, screen, dest, view, data ):
        view.sprites[ self.spritesheet ].render( screen, dest, self.frame )
    def prerender( self, screen, dest, view, data ):
        """Some wall types need a border that gets drawn first."""
        pass
    def get_data( self, view, x, y ):
        """Pre-generate display data for this tile."""
        return None
    def place( self, scene, pos ):
        if scene.on_the_map( *pos ):
            scene.map[pos[0]][pos[1]].decor = self
    def __str__( self ):
        return self.ident
    def __reduce__( self ):
        return self.ident

HIHILL = SingTerrain( "HIHILL", frame = 22, block_walk = True )

class ObjTile( object ):
    def __init__(self, floor=HIHILL, wall=None, decor=None, visible=False):
        self.floor = floor
        self.wall = wall
        self.decor = decor
        self.visible = visible

    def blocks_vision( self ):
        return ( self.floor and self.floor.block_vision ) or (self.wall and self.wall.block_vision ) or ( self.decor and self.decor.block_vision )

    def blocks_walking( self ):
        return ( self.floor and self.floor.block_walk ) or (self.wall and ( self.wall is True or self.wall.block_walk )) or ( self.decor and self.decor.block_walk )

class IntTile( object ):
    def __init__(self, floor=0, wall=-1, decor=-1, visible=False):
        self.floor = floor
        self.wall = wall
        self.decor = decor
        self.visible = visible

    def blocks_vision( self ):
        return ( self.floor and self.floor.block_vision ) or (self.wall and self.wall.block_vision ) or ( self.decor and self.decor.block_vision )

    def blocks_walking( self ):
        return ( self.floor and self.floor.block_walk ) or (self.wall and ( self.wall is True or self.wall.block_walk )) or ( self.decor and self.decor.block_walk )

class LisTile( object ):
    def __init__(self, visible=False):
        self.terrain = [HIHILL]
        if random.randint(1,3) != 1:
            self.terrain.append(HIHILL)
        self.visible = visible

    def blocks_vision( self ):
        return ( self.floor and self.floor.block_vision ) or (self.wall and self.wall.block_vision ) or ( self.decor and self.decor.block_vision )

    def blocks_walking( self ):
        return ( self.floor and self.floor.block_walk ) or (self.wall and ( self.wall is True or self.wall.block_walk )) or ( self.decor and self.decor.block_walk )

import timeit
import numpy
import cPickle

mapsize = 500

# Fill the map with empty tiles
print "Creating objmap..."
objmap = [[ ObjTile()
    for y in range(mapsize) ]
        for x in range(mapsize) ]
print "Creating intmap..."
intmap = [[ IntTile()
    for y in range(mapsize) ]
        for x in range(mapsize) ]
print "Creating lismap..."
lismap = [[ LisTile()
    for y in range(mapsize) ]
        for x in range(mapsize) ]
print "Done creating."

def pickleobj():
    with open( "objmap.sav" , "wb" ) as f:
        cPickle.dump( objmap , f, -1 )

def pickleint():
    with open( "intmap.sav" , "wb" ) as f:
        cPickle.dump( intmap , f, -1 )

def picklelis():
    with open( "lismap.sav" , "wb" ) as f:
        cPickle.dump( lismap , f, -1 )


print "Pickling objmap..."
print timeit.timeit( pickleobj, number=100 )

print "Pickling intmap..."
print timeit.timeit( pickleint, number=100 )

print "Pickling lismap..."
print timeit.timeit( picklelis, number=100 )

print "Done pickling."





