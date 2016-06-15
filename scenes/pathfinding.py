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
    def __init__( self, mymap, start, goal ):
        self.goal = goal
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
           current = frontier.get()

           if current == goal:
              break
           
           for next in self.neighbors(mymap,current):
              new_cost = cost_so_far[current] + self.movecost(current, next)
              if next not in cost_so_far or new_cost < cost_so_far[next]:
                 cost_so_far[next] = new_cost
                 priority = new_cost + self.heuristic(goal, next)
                 frontier.put(next, priority)
                 came_from[next] = current

        self.results = list()
        p = goal
        while p:
            self.results.append( p )
            p = came_from.get( p )
        self.results.reverse()
        if self.results[0] != start:
            self.results = list()

    def neighbors(self,mymap,pos):
        x,y = pos
        for dx,dy in mymap.DELTA8:
            x2,y2 = x+dx,y+dy
            if mymap.on_the_map(x2,y2) and not mymap.map[x2][y2].blocks_walking():
                yield (x2,y2)
            elif (x2,y2) == self.goal:
                yield self.goal
    def movecost(self,a,b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) + 1
    def heuristic( self, a, b ):
        # Manhattan distance on a square grid
        return ( abs(a[0] - b[0]) + abs(a[1] - b[1]) ) * 2



