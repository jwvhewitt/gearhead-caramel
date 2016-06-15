"""
    Author:         Aaron MacDonald
    Date:           June 14, 2007

    Description:    An implementation of the precise permissive field
                    of view algorithm for use in tile-based games.
                    Based on the algorithm presented at
                    http://roguebasin.roguelikedevelopment.org/
                      index.php?title=
                      Precise_Permissive_Field_of_View.

    You are free to use or modify this code as long as this notice is
    included.
    This code is released without warranty.


    Modified by Joseph Hewitt on November 30,2012.
    I changed the two provided functions to a single object parameter.
"""

import copy
import math

# For the line drawer, for the Cone object...
import animobs



def fieldOfView(startX, startY, mapWidth, mapHeight, radius, \
  fovthing ):
    """
        Determines which coordinates on a 2D grid are visible from a
        particular coordinate.

        startX, startY:         The (x, y) coordinate on the grid that
                                is the centre of view.

        mapWidth, mapHeight:    The maximum extents of the grid.  The
                                minimum extents are assumed to be both
                                zero.

        radius:                 How far the field of view may extend
                                in either direction along the x and y
                                axis.

        fovthing:               An object or instance which needs the
                                following two methods:

            VisitTile:              Method that takes two integers
                                    representing an (x, y) coordinate.  Is
                                    used to "visit" visible coordinates.

            TileBlocked:            Method that takes two integers
                                    representing an (x, y) coordinate.
                                    Returns True if the coordinate blocks
                                    sight to coordinates "behind" it.
    """

    visited = set() # Keep track of what tiles have been visited so
                    # that no tile will be visited twice.

    # Will always see the centre.
    fovthing.VisitTile(startX, startY)
    visited.add((startX, startY))

    # Ge the dimensions of the actual field of view, making
    # sure not to go off the map or beyond the radius.

    if startX < radius:
        minExtentX = startX
    else:
        minExtentX = radius

    if mapWidth - startX - 1 < radius:
        maxExtentX = mapWidth - startX - 1
    else:
        maxExtentX = radius

    if startY < radius:
        minExtentY = startY
    else:
        minExtentY = radius

    if mapHeight - startY - 1 < radius:
        maxExtentY = mapHeight - startY - 1
    else:
        maxExtentY = radius

    # Northeast quadrant
    __checkQuadrant(visited, startX, startY, 1, 1, \
      maxExtentX, maxExtentY, \
      fovthing)

    # Southeast quadrant
    __checkQuadrant(visited, startX, startY, 1, -1, \
      maxExtentX, minExtentY, \
      fovthing)

    # Southwest quadrant
    __checkQuadrant(visited, startX, startY, -1, -1, \
      minExtentX, minExtentY, \
      fovthing)

    # Northwest quadrant
    __checkQuadrant(visited, startX, startY, -1, 1, \
      minExtentX, maxExtentY, \
      fovthing)

#-------------------------------------------------------------

class __Line(object):
        def __init__(self, xi, yi, xf, yf):
            self.xi = xi
            self.yi = yi
            self.xf = xf
            self.yf = yf

        dx = property(fget = lambda self: self.xf - self.xi)
        dy = property(fget = lambda self: self.yf - self.yi)

        def pBelow(self, x, y):
            return self.relativeSlope(x, y) > 0

        def pBelowOrCollinear(self, x, y):
            return self.relativeSlope(x, y) >= 0

        def pAbove(self, x, y):
            return self.relativeSlope(x, y) < 0

        def pAboveOrCollinear(self, x, y):
            return self.relativeSlope(x, y) <= 0

        def pCollinear(self, x, y):
            return self.relativeSlope(x, y) == 0

        def lineCollinear(self, line):
            return self.pCollinear(line.xi, line.yi) \
              and self.pCollinear(line.xf, line.yf)

        def relativeSlope(self, x, y):
            return (self.dy * (self.xf - x)) \
              - (self.dx * (self.yf - y))

class __ViewBump:
    def __init__(self, x, y, parent):
        self.x = x
        self.y = y
        self.parent = parent

class __View:
    def __init__(self, shallowLine, steepLine):
        self.shallowLine = shallowLine
        self.steepLine = steepLine

        self.shallowBump = None
        self.steepBump = None

def __checkQuadrant(visited, startX, startY, dx, dy, \
  extentX, extentY, fovthing):
    activeViews = []

    shallowLine = __Line(0, 1, extentX, 0)
    steepLine = __Line(1, 0, 0, extentY)

    activeViews.append( __View(shallowLine, steepLine) )
    viewIndex = 0

    # Visit the tiles diagonally and going outwards
    #
    # .
    # .
    # .           .
    # 9        .
    # 5  8  .
    # 2  4  7
    # @  1  3  6  .  .  .
    maxI = extentX + extentY
    i = 1
    while i != maxI + 1 and len(activeViews) > 0:
        if 0 > i - extentX:
            startJ = 0
        else:
            startJ = i - extentX

        if i < extentY:
            maxJ = i
        else:
            maxJ = extentY

        j = startJ
        while j != maxJ + 1 and viewIndex < len(activeViews):
            x = i - j
            y = j
            __visitCoord(visited, startX, startY, x, y, dx, dy, \
              viewIndex, activeViews, \
              fovthing)

            j += 1

        i += 1

def __visitCoord(visited, startX, startY, x, y, dx, dy, viewIndex, \
  activeViews, fovthing):
    # The top left and bottom right corners of the current coordinate.
    topLeft = (x, y + 1)
    bottomRight = (x + 1, y)

    while viewIndex < len(activeViews) \
      and activeViews[viewIndex].steepLine.pBelowOrCollinear( \
       bottomRight[0], bottomRight[1]):
        # The current coordinate is above the current view and is
        # ignored.  The steeper fields may need it though.
        viewIndex += 1

    if viewIndex == len(activeViews) \
      or activeViews[viewIndex].shallowLine.pAboveOrCollinear( \
       topLeft[0], topLeft[1]):
        # Either the current coordinate is above all of the fields
        # or it is below all of the fields.
        return

    # It is now known that the current coordinate is between the steep
    # and shallow lines of the current view.

    isBlocked = False

    # The real quadrant coordinates
    realX = x * dx
    realY = y * dy

    if (startX + realX, startY + realY) not in visited:
        visited.add((startX + realX, startY + realY))
        fovthing.VisitTile(startX + realX, startY + realY)
    """else:
        # Debugging
        print (startX + realX, startY + realY)"""

    isBlocked = fovthing.TileBlocked(startX + realX, startY + realY)

    if not isBlocked:
        # The current coordinate does not block sight and therefore
        # has no effect on the view.
        return

    if activeViews[viewIndex].shallowLine.pAbove( \
       bottomRight[0], bottomRight[1]) \
      and activeViews[viewIndex].steepLine.pBelow( \
       topLeft[0], topLeft[1]):
        # The current coordinate is intersected by both lines in the
        # current view.  The view is completely blocked.
        del activeViews[viewIndex]
    elif activeViews[viewIndex].shallowLine.pAbove( \
      bottomRight[0], bottomRight[1]):
        # The current coordinate is intersected by the shallow line of
        # the current view.  The shallow line needs to be raised.
        __addShallowBump(topLeft[0], topLeft[1], \
          activeViews, viewIndex)
        __checkView(activeViews, viewIndex)
    elif activeViews[viewIndex].steepLine.pBelow( \
      topLeft[0], topLeft[1]):
        # The current coordinate is intersected by the steep line of
        # the current view.  The steep line needs to be lowered.
        __addSteepBump(bottomRight[0], bottomRight[1], activeViews, \
          viewIndex)
        __checkView(activeViews, viewIndex)
    else:
        # The current coordinate is completely between the two lines
        # of the current view.  Split the current view into two views
        # above and below the current coordinate.

        shallowViewIndex = viewIndex
        viewIndex += 1
        steepViewIndex = viewIndex

        activeViews.insert(shallowViewIndex, \
          copy.deepcopy(activeViews[shallowViewIndex]))

        __addSteepBump(bottomRight[0], bottomRight[1], \
          activeViews, shallowViewIndex)
        if not __checkView(activeViews, shallowViewIndex):
            viewIndex -= 1
            steepViewIndex -= 1

        __addShallowBump(topLeft[0], topLeft[1], activeViews, \
          steepViewIndex)
        __checkView(activeViews, steepViewIndex)

def __addShallowBump(x, y, activeViews, viewIndex):
    activeViews[viewIndex].shallowLine.xf = x
    activeViews[viewIndex].shallowLine.yf = y

    activeViews[viewIndex].shallowBump = __ViewBump(x, y, \
      activeViews[viewIndex].shallowBump)

    curBump = activeViews[viewIndex].steepBump
    while curBump is not None:
        if activeViews[viewIndex].shallowLine.pAbove( \
          curBump.x, curBump.y):
            activeViews[viewIndex].shallowLine.xi = curBump.x
            activeViews[viewIndex].shallowLine.yi = curBump.y

        curBump = curBump.parent

def __addSteepBump(x, y, activeViews, viewIndex):
    activeViews[viewIndex].steepLine.xf = x
    activeViews[viewIndex].steepLine.yf = y

    activeViews[viewIndex].steepBump = __ViewBump(x, y, \
      activeViews[viewIndex].steepBump)

    curBump = activeViews[viewIndex].shallowBump
    while curBump is not None:
        if activeViews[viewIndex].steepLine.pBelow( \
          curBump.x, curBump.y):
            activeViews[viewIndex].steepLine.xi = curBump.x
            activeViews[viewIndex].steepLine.yi = curBump.y

        curBump = curBump.parent

def __checkView(activeViews, viewIndex):
    """
        Removes the view in activeViews at index viewIndex if
            - The two lines are coolinear
            - The lines pass through either extremity
    """

    shallowLine = activeViews[viewIndex].shallowLine
    steepLine = activeViews[viewIndex].steepLine

    if shallowLine.lineCollinear(steepLine) \
      and ( shallowLine.pCollinear(0, 1) \
       or shallowLine.pCollinear(1, 0) ):
        del activeViews[viewIndex]
        return False
    else:
        return True   

class PointOfView( object ):
    # This class constructs a field of vision.
    def __init__(self, scene, x0, y0, radius, manhattan=False):
        self.x = x0
        self.y = y0
        self.scene = scene
        self.radius = radius
        self.manhattan = manhattan
        self.tiles = set()
        fieldOfView( x0 , y0 , scene.width , scene.height , radius , self )

    def VisitTile( self , x , y ):
        if self.manhattan or ( self.radius == 1 ) or ( round( math.sqrt( ( x-self.x )**2 + ( y-self.y )**2 ) ) <= self.radius ):
            self.tiles.add( ( x , y ) )

    def TileBlocked( self , x , y ):
        if self.scene.on_the_map( x , y ):
            return self.scene.map[x][y].blocks_vision()
        else:
            return True

class AttackReach( PointOfView ):
    # This class constructs an attack radius. Like PFOV, but excludes obstacles
    # and the originator's own tile.
    def VisitTile( self , x , y ):
        if self.manhattan or ( self.radius == 1 ) or ( round( math.sqrt( ( x-self.x )**2 + ( y-self.y )**2 ) ) <= self.radius ):
            if ( x != self.x or y != self.y ) and not self.scene.tile_blocks_walking(x,y):
                self.tiles.add( ( x , y ) )

class WalkReach( AttackReach ):
    # This class constructs a placement radius.
    def TileBlocked( self , x , y ):
        return self.scene.tile_blocks_walking(x,y)


class PCPointOfView( PointOfView ):
    # This class also constructs a field of vision, but automatically adds
    # the tiles it sees to the visible area of the map.
    def VisitTile( self , x , y ):
        if self.manhattan or ( self.radius == 1 ) or ( round( math.sqrt( ( x-self.x )**2 + ( y-self.y )**2 ) ) <= self.radius ):
            self.tiles.add( ( x , y ) )
            if self.scene.on_the_map( x , y ):
                self.scene.map[x][y].visible = True

class Cone( PointOfView ):
    """Create a cone shaped template."""
    def __init__(self, scene, start, end, manhattan=False):
        self.x,self.y = start
        self.scene = scene
        self.endradius = max( int( scene.distance( start, end ) // 3 ) , 1 )
        self.radius = int( scene.distance( start, end ) + self.endradius )
        self.manhattan = manhattan

        # Start with a ball
        proto_cone = set()
        for x in range( end[0]-self.endradius, end[0]+self.endradius+1):
            for y in range( end[1]-self.endradius, end[1]+self.endradius+1):
                if scene.distance( (x,y), end ) <= self.endradius:
                    proto_cone.add( (x,y) )

        # Draw lines back to origin.
        for t in range( -self.endradius, self.endradius+1 ):
            h_line = animobs.get_line( start[0], start[1], end[0]+t, end[1] )
            proto_cone.update( h_line )
            if t != 0:
                v_line = animobs.get_line( start[0], start[1], end[0], end[1]+t )
                proto_cone.update( v_line )

        # Determine the PFOV from origin.
        self.tiles = set()
        fieldOfView( start[0] , start[1] , scene.width , scene.height , self.radius , self )

        # The finished cone is the intersection of the two.
        self.tiles.intersection_update( proto_cone )
        self.tiles.remove( start )


if __name__=="__main__":
    import timeit

    class UseRound( object ):
        def __call__(self):
            return round( 3.14152 )

    class UseInt( object ):
        def __call__(self):
            return int( 3.14152 + 0.5 )


    t1 = timeit.Timer( UseRound() )
    t2 = timeit.Timer( UseInt() )

    print t1.timeit(10000000)
    print t2.timeit(10000000)

