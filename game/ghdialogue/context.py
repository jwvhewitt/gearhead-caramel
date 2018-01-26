
# Constants for dialogue contexts.

HELLO,ASK_FOR_ITEM,INFO,MISSION,PROBLEM,GOODBYE,JOIN,PERSONAL,ATTACK,CHALLENGE = range(10)

# HELLO = NPC says hello. Usually the first offer in a peaceful conversation.
# ASK_FOR_ITEM: The NPC gives the PC an item, or at least replies to the request.
#       The data property should contain "item"
# INFO: The NPC offers the PC some information.
#       The data property should contain "subject"
# MISSION: 

# ATTACK: The greeting from a hostile NPC.
# CHALLENGE: The reply from a hostile NPC when challenged by PC.
