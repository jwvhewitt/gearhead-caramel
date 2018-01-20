
class Beat( object ):
    def __init__(self,needs_reply=False):
        self.children = list()
        self.needs_reply = needs_reply

    def build( self, camp ):
        if self.

class Cutscene( object ):
    def __init__( self ):
        self.library = dict{}
        self.beats = list()

    def play( self, camp ):
        # Generate the beat sequence.

