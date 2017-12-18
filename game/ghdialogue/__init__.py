
import pbge
import ghgrammar

def build_grammar( mygram, camp, speaker, audience ):
    mygram.absorb(ghgrammar.DEFAULT_GRAMMAR)


pbge.dialogue.GRAMMAR_BUILDER = build_grammar
