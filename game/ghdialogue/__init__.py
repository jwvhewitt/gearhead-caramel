
import pbge
import ghgrammar
import context
import ghdview
import ghreplies
import ghoffers


def build_grammar( mygram, camp, speaker, audience ):
    for pat,gramdic in ghgrammar.DEFAULT_GRAMMAR.iteritems():
        for k,v in gramdic.iteritems():
            if k is ghgrammar.Default:
                if pat not in mygram:
                    mygram[pat] = list()
                mygram[pat] += v
            elif k in speaker.personality:
                if pat not in mygram:
                    mygram[pat] = list()
                mygram[pat] += v

    mygram.absorb({"[speaker]":(str(speaker),),"[audience]":(str(audience),)})

def harvest( mod, class_to_collect ):
    mylist = []
    for name in dir( mod ):
        o = getattr( mod, name )
        if isinstance( o , class_to_collect ):
            mylist.append( o )
    return mylist

pbge.dialogue.GRAMMAR_BUILDER = build_grammar
pbge.dialogue.STANDARD_REPLIES = harvest(ghreplies,pbge.dialogue.Reply)
pbge.dialogue.STANDARD_OFFERS = harvest(ghoffers,pbge.dialogue.Offer)

HELLO_STARTER = pbge.dialogue.Cue(pbge.dialogue.ContextTag((context.HELLO,)))
