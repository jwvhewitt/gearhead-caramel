import pygame
import random
from .. import scenes
import math
from .. import container

import plasma
import anchors
import mutator
import decor
import gapfiller
import converter
import prep
import rooms
from rooms import Room
import architect


# A scene is constructed in the following steps:
# - The scene calls its PREPARE to initialize the map.
# - The child rooms are arranged; descendants are handled recursively
# - The child rooms are connected; descendants are handled recursively
# - The MUTATE attribute is called; descendants are mutated recursively
# - The render method is called; descendants are handled recursively
# - The WALL_FILTER attribute is called
# - The terrain is validated
# - Map contents are deployed; descendants are handled recursively
# - The DECORATE attribute is called; descendants are handled recursively
# - The contents of the map are cleaned

# Scene/Room options
#  GAPFILL*
#  MUTATE*
#  DECORATE*
#  DEFAULT_ROOM*
#  WALL_FILTER*
#  PREPARE*


#  *****************************
#  ***   SCENE  GENERATORS   ***
#  *****************************

class SceneGenerator( Room ):
    """The blueprint for a scene."""
    #DEFAULT_ROOM = rooms.FuzzyRoom
    def __init__( self, myscene, archi, default_room=None, gapfill=None, mutate=None, decorate=None ):
        super(SceneGenerator,self).__init__( myscene.width, myscene.height )
        self.gb = myscene
        self.area = pygame.Rect(0,0,myscene.width,myscene.height)
        self.archi = archi
        self.contents = myscene.contents
        if default_room:
            self.DEFAULT_ROOM = default_room
        if gapfill:
            self.GAPFILL = gapfill
        if mutate:
            self.MUTATE = mutate
        if decorate:
            self.DECORATE = decorate

    def make( self ):
        """Assemble this stuff into a real map."""
        # Conduct the five steps of building a level.
        self.archi.prepare( self ) # Only the scene generator gets to prepare
        self.step_two( self.gb ) # Arrange contents for self, then children
        self.step_three( self.gb, self.archi ) # Connect contents for self, then children
        self.step_four( self.gb ) # Mutate for self, then children
        self.step_five( self.gb, self.archi ) # Render for self, then children

        # Convert undefined walls to real walls.
        self.archi.wall_filter( self )
        #self.gb.validate_terrain()

        self.step_six( self.gb ) # Deploy for self, then children
        self.step_seven( self.gb ) # Decorate for self, then children

        self.clean_contents()

        return self.gb

    def clean_contents( self ):
        # Remove unimportant things from the contents.
        for t in self.gb.contents[:]:
            if not hasattr( t, "pos" ):
                self.gb.contents.remove( t )
                #if isinstance( t, maps.Scene ):
                #    t.parent_scene = self.gb
                #    self.gb.sub_scenes.append( t )
                #elif isinstance( t, Room ):
                #    self.gb.sub_scenes.append( t )


