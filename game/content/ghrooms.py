import pbge
import pygame

from pbge.randmaps.decor import OmniDec
from pbge.randmaps.rooms import FuzzyRoom
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
        for t in range(random.randint(3,10)):
            x = random.randint(self.area.left+1,self.area.right-2)
            y = random.randint(self.area.top+1,self.area.bottom-2)
            gb.fill(pygame.Rect(x-1,y-1,3,3),wall=ghterrain.Forest)

class LakeRoom(FuzzyRoom):
    def build( self, gb, archi ):
        super().build(gb,archi)

        # Add some random forest blobs.
        for t in range(random.randint(1,3)):
            x = random.randint(self.area.left+3,self.area.right-4)
            y = random.randint(self.area.top+3,self.area.bottom-4)
            s = random.randint(3,5)
            gb.fill_blob(pygame.Rect(x-1,y-1,s,s),floor=ghterrain.Water)

class WreckageRoom(FuzzyRoom):
    DECORATE = MSWreckageDecor(floor_fill_factor=0.2)

class DragonToothRoom(FuzzyRoom):
    DECORATE = DragonToothDecor()
