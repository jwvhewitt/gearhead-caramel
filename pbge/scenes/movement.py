from .. import Singleton

class MoveMode( Singleton ):
    climb_penalty = 2.0
    altitude = None

    @classmethod
    def get_short_name(cls):
        return cls.NAME

class Walking( MoveMode ):
    NAME = 'walk'

class Flying( MoveMode ):
    climb_penalty = 1.0
    NAME = 'fly'
    altitude = 25

class Vision( MoveMode ):
    pass
