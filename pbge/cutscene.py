import random
from . import alert

class Beat( object ):
    def __init__(self,display,prep=None,effect=None,children=[],needs_reply=False):
        # "prep" is a callable that takes (camp,cutscene) and returns
        # True if everything went okay.
        # "display" is a callable that takes (camp,cutscene) and handles
        # one part of the cutscene, such as a line of dialogue.
        self.prep = prep
        self.display = display
        self.effect = effect
        self.children = children
        self.needs_reply = needs_reply
        self.reply = None

    def build( self, camp, cutscene ):
        ok = True
        if self.prep:
            ok = self.prep(camp,cutscene)
        if ok:
            candidates = list(self.children)
            random.shuffle(candidates)
            while candidates and not self.reply:
                c = candidates.pop()
                self.reply = c.build(camp,cutscene)
            if self.reply or not self.needs_reply:
                return self
                
    def run( self, camp, cutscene ):
        if self.display:
            self.display(camp,cutscene)
        if self.effect:
            self.effect(camp)

class Cutscene( object ):
    def __init__( self, library=dict(),beats=()):
        self.library = dict()
        self.library.update(library)
        self.beats = list(beats)
    def play_list(self,camp,beats):
        # Generate the beat sequence.
        candidates = list(beats)
        random.shuffle(candidates)
        start_beat = None
        while candidates and not start_beat:
            c = candidates.pop()
            start_beat = c.build(camp,self)
        while start_beat:
            start_beat.run(camp,self)
            start_beat = start_beat.reply
    def __call__( self, camp ):
        self.play_list(camp,self.beats)
        
class AlertDisplay( object ):
    def __init__(self,text):
        self.text=text
    def __call__(self,camp,cutscene):
        alert(self.text.format(**cutscene.library))
        
