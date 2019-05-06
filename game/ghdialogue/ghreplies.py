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

ATTACK_WITHDRAW = Reply( "[ATTACK:WITHDRAW]" ,
            destination = Cue( ContextTag([context.WITHDRAW]) ) ,
            context = ContextTag([context.ATTACK]) )

CHAT_CHAT = Reply( "[CHAT:CHAT]" ,
            destination = Cue( ContextTag([context.CHAT]) ) ,
            context = ContextTag([context.CHAT]) )

CHAT_GOODBYE = Reply( "[CHAT:GOODBYE]" ,
            context = ContextTag([context.CHAT]),
            destination = Cue( ContextTag([context.GOODBYE]) ) )

CHAT_INFO = Reply( "[CHAT:INFO]" ,
            context = ContextTag([context.CHAT]),
            destination = Cue( ContextTag([context.INFO]) ) )


HELLO_ASKFORITEM = Reply( "[HELLO:ASK_FOR_ITEM]" ,
            destination = Cue( ContextTag([context.ASK_FOR_ITEM]) ) ,
            context = ContextTag([context.HELLO]) )

HELLO_CHAT = Reply( "[HELLO:CHAT]" ,
            destination = Cue( ContextTag([context.CHAT]) ) ,
            context = ContextTag([context.HELLO]) )

HELLO_GOODBYE = Reply( "[HELLO:GOODBYE]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.GOODBYE]) ) )

HELLO_MISSION = Reply( "[HELLO:MISSION]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.MISSION]) ) )

HELLO_PROPOSAL = Reply( "[HELLO:PROPOSAL]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.PROPOSAL]) ) )

HELLO_PROPOSALJOIN = Reply( "[DOYOUWANTTOBELANCEMATE]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.PROPOSAL,context.JOIN]) ) )

HELLO_INFO = Reply( "[HELLO:INFO]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.INFO]) ) )

HELLO_INFOPERSONAL = Reply( "[HELLO:INFO_PERSONAL]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.INFO,context.PERSONAL]) ) )

HELLO_JOIN = Reply( "[HELLO:JOIN]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.JOIN]) ) )

HELLO_OPENSHOP = Reply( "[HELLO:OPEN_SHOP]" ,
            context = ContextTag([context.HELLO]),
            destination = Cue( ContextTag([context.OPEN_SHOP]) ) )

INFOPERSONAL_GOODBYE = Reply( "[INFO_PERSONAL:GOODBYE]" ,
            context = ContextTag([context.INFO,context.PERSONAL]),
            destination = Cue( ContextTag([context.GOODBYE]) ) )

INFOPERSONAL_JOIN = Reply( "[INFO_PERSONAL:JOIN]" ,
            context = ContextTag([context.INFO,context.PERSONAL]),
            destination = Cue( ContextTag([context.JOIN]) ) )

MISSION_ACCEPT = Reply( "[MISSION:ACCEPT]" ,
            context = ContextTag([context.MISSION]),
            destination = Cue( ContextTag([context.ACCEPT]) ) )

MISSION_DENY = Reply( "[MISSION:DENY]" ,
            context = ContextTag([context.MISSION]),
            destination = Cue( ContextTag([context.DENY]) ) )

MISSIONPROBLEM_JOIN = Reply( "[MISSION_PROBLEM:JOIN]" ,
            context = ContextTag([context.MISSION,context.PROBLEM]),
            destination = Cue( ContextTag([context.JOIN]) ) )

MISSIONPROBLEM_GOODBYE = Reply( "[MISSION_PROBLEM:GOODBYE]" ,
            context = ContextTag([context.MISSION,context.PROBLEM]),
            destination = Cue( ContextTag([context.GOODBYE]) ) )

PROPOSAL_ACCEPT = Reply( "[PROPOSAL:ACCEPT]" ,
            context = ContextTag([context.PROPOSAL]),
            destination = Cue( ContextTag([context.ACCEPT]) ) )

PROPOSALJOIN_ACCEPT = Reply( "[PROPOSAL_JOIN:ACCEPT]" ,
            context = ContextTag([context.PROPOSAL,context.JOIN]),
            destination = Cue( ContextTag([context.ACCEPT]) ) )


PROPOSAL_DENY = Reply( "[PROPOSAL:DENY]" ,
            context = ContextTag([context.PROPOSAL]),
            destination = Cue( ContextTag([context.DENY]) ) )

PROPOSALJOIN_DENY = Reply( "[PROPOSAL_JOIN:DENY]" ,
            context = ContextTag([context.PROPOSAL,context.JOIN]),
            destination = Cue( ContextTag([context.DENY]) ) )

