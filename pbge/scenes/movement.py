from .. import Singleton

class MoveMode( Singleton ):
    climb_penalty = 2.0

class Walking( MoveMode ):
    NAME = 'walk'
    pass

class Flying( MoveMode ):
    climb_penalty = 1.0
    NAME = 'fly'

class Vision( MoveMode ):
    pass
