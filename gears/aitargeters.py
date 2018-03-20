

class TargetEnemy( object ):
    # This targeter will attempt to use its invocation against an enemy model.
    def __init__( self, ally_targetability=-1 ):
        self.ally_targetability = ally_targetability
        self.min_distance = min_distance
    def get_impulse( self ):
        # Return an integer rating how desirable this action is.
        # An impulse of 10 is the default attack action.

    def can_use_immediately( self ):
        # Return True if this invocation can be used right away.

