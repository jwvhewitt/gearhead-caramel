import pygame
import random

class Plasma( object ):
    """Creates a plasma; cels have value from 0.0 to 1.0."""
    # Converted to Python from https://github.com/jseyster/plasmafractal/blob/master/Plasma.java
    def __init__( self, noise=5.0, map_width=50, map_height=50 ):
        self.noise = noise
        plasma_size = self.find_power_of_two_plus_one(max(map_width,map_height))
        self.width = plasma_size
        self.height = plasma_size
        self.map = [[ float()
            for y in range(self.height) ]
                for x in range(self.width) ]
        self.divide_grid(0,0,self.width,self.height,random.random(),random.random(),random.random(),random.random())

    @staticmethod
    def find_power_of_two_plus_one(x):
        return 1<<(x-1).bit_length() + 1

    def displace( self, mag ):
        """Provide a random displacement of up to mag magnitude."""
        max_disp = mag * self.noise / ( self.width + self.height )
        return ( random.random() - 0.5 ) * max_disp

    def divide_grid( self,x,y,width,height,c1,c2,c3,c4 ):
        """Recursively divide up the plasma map."""
        # x,y,width,height describe the area currently being developed
        # c1,c2,c3,c4 are the four corner heights.

        nu_width = width/2
        nu_height = height/2

        if (width > 1) or (height > 1):
            middle = sum( (c1,c2,c3,c4) ) / 4 + self.displace( nu_width + nu_height )
            edge1 = sum((c1,c2))/2
            edge2 = sum((c2,c3))/2
            edge3 = sum((c3,c4))/2
            edge4 = sum((c4,c1))/2

            if middle < 0.0:
                middle = 0.0
            elif middle > 1.0:
                middle = 1.0

            self.divide_grid( x, y, nu_width, nu_height, c1, edge1, middle, edge4);
            self.divide_grid( x + nu_width, y, nu_width, nu_height, edge1, c2, edge2, middle);
            self.divide_grid( x + nu_width, y + nu_height, nu_width, nu_height, middle, edge2, c3, edge3);
            self.divide_grid( x, y + nu_height, nu_width, nu_height, edge4, middle, edge3, c4);

        else:
            # We are done! Just set the midpoint as average of 4 corners.
            self.map[int(x)][int(y)] = sum( (c1,c2,c3,c4) ) / 4

    def draw( self, screen ):
        for x in range( self.width ):
            for y in range( self.height ):
                pygame.draw.rect(screen,(255*self.map[x][y],255*self.map[x][y],127+128*self.map[x][y]),pygame.Rect(x*2,y*2,2,2) )

    def draw_layers( self, screen, w_el=0.3, l_el=0.5 ):
        for x in range( self.width ):
            for y in range( self.height ):
                if self.map[x][y] < w_el:
                    pygame.draw.rect(screen,(0,0,150),pygame.Rect(x*2,y*2,2,2) )
                elif self.map[x][y] < l_el:
                    pygame.draw.rect(screen,(150,200,0),pygame.Rect(x*2,y*2,2,2) )
                else:
                    pygame.draw.rect(screen,(50,250,100),pygame.Rect(x*2,y*2,2,2) )

