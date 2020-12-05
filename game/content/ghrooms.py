import pbge
import pygame

from pbge.randmaps.decor import OmniDec
from pbge.randmaps.rooms import FuzzyRoom, OpenRoom
from . import ghterrain
import random


class MSWreckageDecor(OmniDec):
    FLOOR_DECOR = (ghterrain.MSWreckage,)
    FLOOR_FILL_FACTOR = 0.15


class DragonToothDecor(OmniDec):
    FLOOR_DECOR = (ghterrain.DragonTeethWall,ghterrain.DragonTeethWall,ghterrain.Forest)
    FLOOR_FILL_FACTOR = 0.25


class ForestRoom(FuzzyRoom):
    def build( self, gb, archi ):
        super().build(gb,archi)

        # Add some random forest blobs.
        if self.area.width > 4 and self.area.height > 4:
            for t in range(random.randint(3,10)):
                x = random.randint(self.area.left+1,self.area.right-2)
                y = random.randint(self.area.top+1,self.area.bottom-2)
                gb.fill(pygame.Rect(x-1,y-1,3,3),wall=ghterrain.Forest)
        else:
            mydest = pygame.Rect(0,0,3,3)
            mydest.center = self.area.center
            gb.fill(mydest,wall=ghterrain.Forest)


class LakeRoom(FuzzyRoom):
    def build( self, gb, archi ):
        super().build(gb,archi)

        # Add some random forest blobs.
        if self.area.width > 8 and self.area.height > 8:
            for t in range(random.randint(1,3)):
                x = random.randint(self.area.left+3,self.area.right-4)
                y = random.randint(self.area.top+3,self.area.bottom-4)
                s = random.randint(3,5)
                gb.fill_blob(pygame.Rect(x-1,y-1,s,s),floor=ghterrain.Water)
        else:
            mydest = pygame.Rect(0,0,3,3)
            mydest.center = self.area.center
            gb.fill(mydest,floor=ghterrain.Water)


class WreckageRoom(FuzzyRoom):
    DECORATE = MSWreckageDecor(floor_fill_factor=0.2)


class DragonToothRoom(FuzzyRoom):
    DECORATE = DragonToothDecor()


class MSRuinsRoom(FuzzyRoom):
    DECORATE = MSWreckageDecor(floor_fill_factor=0.05)

    def build(self, gb, archi):
        super().build(gb, archi)

        # Add some random ruins.
        ruin_list = list()
        safe_area = self.area.inflate(-4,-4)
        if safe_area.width > 8 and safe_area.height > 8:
            for t in range(random.randint(3,8)):
                x = random.randint(self.area.left+3,self.area.right-4)
                y = random.randint(self.area.top+3,self.area.bottom-4)
                myroomdest = pygame.Rect(0,0,random.randint(2,4),random.randint(2,4))
                myroomdest.center = (x,y)
                myroomdest = myroomdest.clamp(safe_area)
                if myroomdest.inflate(2,2).collidelist(ruin_list) == -1:
                    gb.fill(myroomdest,wall=ghterrain.MSRuinedWall)
                    ruin_list.append(myroomdest)
        else:
            mydest = pygame.Rect(0, 0, 3, 3)
            mydest.center = self.area.center
            gb.fill(mydest, wall=ghterrain.MSRuinedWall)

class BarArea(OpenRoom):
    def build(self, gb, archi):
        super().build(gb, archi)

        # Add a bar along the south and maybe along one side.
        mydest = pygame.Rect(self.area.left, self.area.bottom-1, self.area.width, 1)
        gb.fill(mydest, wall=ghterrain.BarTerrain)

        if random.randint(1,3) == 1:
            mydest = pygame.Rect(self.area.left, self.area.top, 1, self.area.height)
            gb.fill(mydest, wall=ghterrain.BarTerrain)
        elif random.randint(1,2) == 1:
            mydest = pygame.Rect(self.area.right, self.area.top, 1, self.area.height)
            gb.fill(mydest, wall=ghterrain.BarTerrain)
