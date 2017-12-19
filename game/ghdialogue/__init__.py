
import pbge
import ghgrammar
import context
import ghdview

def build_grammar( mygram, camp, speaker, audience ):
    mygram.absorb(ghgrammar.DEFAULT_GRAMMAR)


pbge.dialogue.GRAMMAR_BUILDER = build_grammar

HELLO_STARTER = pbge.dialogue.Cue(pbge.dialogue.ContextTag((context.HELLO,)))
