from pbge.dialogue import Offer,Reply,Cue,ContextTag
from . import context


HELLO = Offer('[HELLO_PLUS]',context=ContextTag([context.HELLO,]))

BADHELLO = Offer('[HELLO_UNFAV]',context=ContextTag([context.UNFAVORABLE_HELLO,]))

ATTACK = Offer('[ATTACK]',context=ContextTag([context.ATTACK,]))

CHALLENGE = Offer('[CHALLENGE]',context=ContextTag([context.CHALLENGE,]))

GOODBYE = Offer('[GOODBYE]',context=ContextTag([context.GOODBYE,]), is_generic=True)

CHAT = Offer('[CHAT]',context=ContextTag([context.CHAT,]), is_generic=True)


