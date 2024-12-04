from .. import Singleton

class MoveMode( Singleton ):
    climb_penalty = 2.0
    altitude = None

    @classmethod
    def get_short_name(cls):
        return cls.name

class Walking( MoveMode ):
    name = 'walk'

class Flying( MoveMode ):
    climb_penalty = 1.0
    name = 'fly'
    altitude = 25

class Swimming( MoveMode ):
    climb_penalty = 1.0
    name = 'swim'
    altitude = 1

class Vision( MoveMode ):
    pass
