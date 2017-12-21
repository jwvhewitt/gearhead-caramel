from pbge.dialogue import Reply,Cue,ContextTag
import context

HELLO_ASKFORITEM = Reply( "[HELLO:ASK_FOR_ITEM]" ,
            destination = Cue( ContextTag([context.ASK_FOR_ITEM]) ) ,
            context = ContextTag([context.HELLO]) )



