from pbge.dialogue import Reply,Cue,ContextTag
import context

ACCEPTMISSION_JOIN = Reply( "[ACCEPT_MISSION:JOIN]" ,
            context = ContextTag([context.ACCEPT,context.MISSION]),
            destination = Cue( ContextTag([context.JOIN]) ) )
            
ACCEPTMISSION_GOODBYE = Reply( "[ACCEPT_MISSION:GOODBYE]" ,
            context = ContextTag([context.ACCEPT,context.MISSION]),
            destination = Cue( ContextTag([context.GOODBYE]) ) )

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

HELLO_GOODBYE = Reply( "[HELLO:GOODBYE]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.GOODBYE]) ) )

HELLO_INFO = Reply( "[HELLO:INFO]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.INFO]) ) )

HELLO_INFOPERSONAL = Reply( "[HELLO:INFO_PERSONAL]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.INFO,context.PERSONAL]) ) )

HELLO_JOIN = Reply( "[HELLO:JOIN]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.JOIN]) ) )

INFOPERSONAL_GOODBYE = Reply( "[INFO_PERSONAL:GOODBYE]" ,
            context = ContextTag([context.INFO,context.PERSONAL]),
            destination = Cue( ContextTag([context.GOODBYE]) ) )

INFOPERSONAL_JOIN = Reply( "[INFO_PERSONAL:JOIN]" ,
            context = ContextTag([context.INFO,context.PERSONAL]),
            destination = Cue( ContextTag([context.JOIN]) ) )

MISSIONPROBLEM_JOIN = Reply( "[MISSION_PROBLEM:JOIN]" ,
            context = ContextTag([context.MISSION,context.PROBLEM]),
            destination = Cue( ContextTag([context.JOIN]) ) )

MISSIONPROBLEM_GOODBYE = Reply( "[MISSION_PROBLEM:GOODBYE]" ,
            context = ContextTag([context.MISSION,context.PROBLEM]),
            destination = Cue( ContextTag([context.GOODBYE]) ) )


