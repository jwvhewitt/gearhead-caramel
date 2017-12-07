# Cribbed from the Red Blob Games tutorial.

import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

class AStarPath( object ):
    def __init__( self, mymap, start, goal, movemode, blocked_tiles=set() ):
        self.start = start
        self.goal = goal
        self.movemode = movemode
        self.blocked_tiles = blocked_tiles
        self.mymap = mymap
        frontier = PriorityQueue()
        frontier.put(start, 0)
        self.came_from = {}
        self.cost_to_tile = {}
        self.came_from[start] = None
        self.cost_to_tile[start] = 0

        while not frontier.empty():
           current = frontier.get()

           if current == goal:
              break
           
           for next in self.neighbors(mymap,current):
              new_cost = self.cost_to_tile[current] + self.movecost(current, next)
              if next not in self.cost_to_tile or new_cost < self.cost_to_tile[next]:
                 self.cost_to_tile[next] = new_cost
                 priority = new_cost + self.heuristic(goal, next)
                 frontier.put(next, priority)
                 self.came_from[next] = current

        self.results = self.get_path( goal )

    def get_path( self, goal ):
        results = list()
        p = goal
        while p:
            results.append( p )
            p = self.came_from.get( p )
        results.reverse()
        if results[0] != self.start:
            results = list()
        return results


    def neighbors(self,mymap,pos):
        x,y = pos
        for dx,dy in mymap.DELTA8:
            x2,y2 = x+dx,y+dy
            #if mymap.on_the_map(x2,y2) and not mymap.tile_blocks_walking(x2,y2):
            if not( (x2,y2) in self.blocked_tiles or mymap.tile_blocks_movement(x2,y2,self.movemode) ):
                yield (x2,y2)
            elif (x2,y2) == self.goal:
                yield self.goal
    def movecost(self,a,b):
        return self.mymap.get_move_cost(a,b,self.movemode)
    def heuristic( self, a, b ):
        # Manhattan distance on a square grid
        return ( abs(a[0] - b[0]) + abs(a[1] - b[1]) ) * 10

class NavigationGuide( AStarPath ):
    # Return a set of tiles that can be reached from the start tile.
    def __init__( self, mymap, start, max_mp, movemode, blocked_tiles=set() ):
        # tiers is a list of movement
        self.start = start
        self.movemode = movemode
        self.blocked_tiles = blocked_tiles
        self.mymap = mymap
        frontier = set()
        frontier.add(start)
        self.came_from = {}
        self.cost_to_tile = {}
        self.came_from[start] = None
        self.cost_to_tile[start] = 0
        self.cheapest_move = 100000

        while frontier:
           current = frontier.pop()

           for next in self.neighbors(mymap,current):
              new_cost = self.cost_to_tile[current] + self.movecost(current, next)
              if ( new_cost <= max_mp ) and ( next not in self.cost_to_tile or new_cost < self.cost_to_tile[next] ):
                self.cost_to_tile[next] = new_cost
                frontier.add(next)
                self.came_from[next] = current
                self.cheapest_move = min(new_cost,self.cheapest_move)


    def neighbors(self,mymap,pos):
        x,y = pos
        for dx,dy in mymap.DELTA8:
            x2,y2 = x+dx,y+dy
            if not( (x2,y2) in self.blocked_tiles or mymap.tile_blocks_movement(x2,y2,self.movemode) ):
                yield (x2,y2)

