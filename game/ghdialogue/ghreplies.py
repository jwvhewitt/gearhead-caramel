from pbge.dialogue import Reply,Cue,ContextTag
import context

ATTACK_CHALLENGE = Reply( "[ATTACK:CHALLENGE]" ,
            destination = Cue( ContextTag([context.CHALLENGE]) ) ,
            context = ContextTag([context.ATTACK]) )

ATTACK_COMBATINFO = Reply( "[ATTACK:COMBAT_INFO]" ,
            destination = Cue( ContextTag([context.COMBAT_INFO]) ) ,
            context = ContextTag([context.ATTACK]) )
            
ATTACK_MERCY = Reply( "[ATTACK:MERCY]" ,
            destination = Cue( ContextTag([context.MERCY]) ) ,
            context = ContextTag([context.ATTACK]) )


HELLO_ASKFORITEM = Reply( "[HELLO:ASK_FOR_ITEM]" ,
            destination = Cue( ContextTag([context.ASK_FOR_ITEM]) ) ,
            context = ContextTag([context.HELLO]) )


HELLO_INFO = Reply( "[HELLO:INFO]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.INFO]) ) )

HELLO_INFOPERSONAL = Reply( "[HELLO:INFO_PERSONAL]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.INFO,context.PERSONAL]) ) )

GOODBYEMISSION_JOIN = Reply( "[GOODBYE_MISSION:JOIN]" ,
            context = ContextTag([context.GOODBYE,context.MISSION]),
            destination = Cue( ContextTag([context.JOIN]) ) )

HELLO_JOIN = Reply( "[HELLO:JOIN]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.JOIN]) ) )

MISSIONPROBLEM_JOIN = Reply( "[MISSION_PROBLEM:JOIN]" ,
            context = ContextTag([context.MISSION,context.PROBLEM]),
            destination = Cue( ContextTag([context.JOIN]) ) )

INFOPERSONAL_JOIN = Reply( "[INFO_PERSONAL:JOIN]" ,
            context = ContextTag([context.INFO,context.PERSONAL]),
            destination = Cue( ContextTag([context.JOIN]) ) )

