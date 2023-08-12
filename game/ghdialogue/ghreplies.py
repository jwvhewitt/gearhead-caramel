from pbge.dialogue import Reply, Cue, ContextTag
from . import context

ACCEPTMISSION_JOIN = Reply("[ACCEPT_MISSION:JOIN]",
                           context=ContextTag([context.ACCEPT, context.MISSION]),
                           destination=Cue(ContextTag([context.JOIN])))

ACCEPTMISSION_GOODBYE = Reply("[ACCEPT_MISSION:GOODBYE]",
                              context=ContextTag([context.ACCEPT, context.MISSION]),
                              destination=Cue(ContextTag([context.GOODBYE])))

ATTACK_CHALLENGE = Reply("[ATTACK:CHALLENGE]",
                         destination=Cue(ContextTag([context.CHALLENGE])),
                         context=ContextTag([context.ATTACK]))

ATTACK_COMBATCUSTOM = Reply("{reply}",
                            destination=Cue(ContextTag([context.COMBAT_CUSTOM])),
                            context=ContextTag([context.ATTACK]))

ATTACK_COMBATINFO = Reply("[ATTACK:COMBAT_INFO]",
                          destination=Cue(ContextTag([context.COMBAT_INFO])),
                          context=ContextTag([context.ATTACK]))

ATTACK_MERCY = Reply("[ATTACK:MERCY]",
                     destination=Cue(ContextTag([context.MERCY])),
                     context=ContextTag([context.ATTACK]))

ATTACK_RETREAT = Reply("[ATTACK:RETREAT]",
                       destination=Cue(ContextTag([context.RETREAT])),
                       context=ContextTag([context.ATTACK]))

ATTACK_WITHDRAW = Reply("[ATTACK:WITHDRAW]",
                        destination=Cue(ContextTag([context.WITHDRAW])),
                        context=ContextTag([context.ATTACK]))

BADCUSTOM_CUSTOMREPLY = Reply(
    "{reply}",
    destination=Cue(ContextTag([context.CUSTOMREPLY])),
    context=ContextTag([context.UNFAVORABLE_CUSTOM])
)

BADHELLO_BADCUSTOM = Reply("{reply}",
                           destination=Cue(ContextTag([context.UNFAVORABLE_CUSTOM])),
                           context=ContextTag([context.UNFAVORABLE_HELLO]))

BADHELLO_REVEAL = Reply("[HELLO:REVEAL]",
                        destination=Cue(ContextTag([context.REVEAL])),
                        context=ContextTag([context.UNFAVORABLE_HELLO]))

CHAT_CHAT = Reply("[CHAT:CHAT]",
                  destination=Cue(ContextTag([context.CHAT])),
                  context=ContextTag([context.CHAT]))

CHAT_GOODBYE = Reply("[CHAT:GOODBYE]",
                     context=ContextTag([context.CHAT]),
                     destination=Cue(ContextTag([context.GOODBYE])))

CHAT_INFO = Reply("[CHAT:INFO]",
                  context=ContextTag([context.CHAT]),
                  destination=Cue(ContextTag([context.INFO])))

CUSTOM_CUSTOMREPLY = Reply("{reply}",
                           destination=Cue(ContextTag([context.CUSTOMREPLY])),
                           context=ContextTag([context.CUSTOM]))

CUSTOM_INFO = Reply("[INFO:INFO]",
                    context=ContextTag([context.CUSTOM]),
                    destination=Cue(ContextTag([context.INFO])))

CUSTOMREPLY_INFO = Reply("[CHAT:INFO]",
                         context=ContextTag([context.CUSTOMREPLY]),
                         destination=Cue(ContextTag([context.INFO])))

CUSTOMREPLY_CUSTOMGOODBYE = Reply("{reply}",
                                  context=ContextTag([context.CUSTOMREPLY]),
                                  destination=Cue(ContextTag([context.CUSTOMGOODBYE])))

HELLO_ASKFORITEM = Reply("[HELLO:ASK_FOR_ITEM]",
                         destination=Cue(ContextTag([context.ASK_FOR_ITEM])),
                         context=ContextTag([context.HELLO]))

HELLO_CHAT = Reply("[HELLO:CHAT]",
                   destination=Cue(ContextTag([context.CHAT])),
                   context=ContextTag([context.HELLO]))

HELLO_CUSTOM = Reply("{reply}",
                     destination=Cue(ContextTag([context.CUSTOM])),
                     context=ContextTag([context.HELLO]))

HELLO_GOODBYE = Reply("[HELLO:GOODBYE]",
                      context=ContextTag([context.HELLO]),
                      destination=Cue(ContextTag([context.GOODBYE])))

HELLO_MISSION = Reply("[HELLO:MISSION]",
                      context=ContextTag([context.HELLO]),
                      destination=Cue(ContextTag([context.MISSION])))

HELLOMISSION_MISSION = Reply("[HELLOMISSION:MISSION]",
                             context=ContextTag([context.HELLO, context.MISSION]),
                             destination=Cue(ContextTag([context.MISSION])))

HELLO_PROPOSAL = Reply("[HELLO:PROPOSAL]",
                       context=ContextTag([context.HELLO]),
                       destination=Cue(ContextTag([context.PROPOSAL])))

HELLO_PROPOSALJOIN = Reply("[DOYOUWANTTOBELANCEMATE]",
                           context=ContextTag([context.HELLO]),
                           destination=Cue(ContextTag([context.PROPOSAL, context.JOIN])))

HELLO_INFO = Reply("[HELLO:INFO]",
                   context=ContextTag([context.HELLO]),
                   destination=Cue(ContextTag([context.INFO])))

HELLO_INFOPERSONAL = Reply("[HELLO:INFO_PERSONAL]",
                           context=ContextTag([context.HELLO]),
                           destination=Cue(ContextTag([context.INFO, context.PERSONAL])))

HELLO_JOIN = Reply("[HELLO:JOIN]",
                   context=ContextTag([context.HELLO]),
                   destination=Cue(ContextTag([context.JOIN])))

HELLO_LEAVEPARTY = Reply("[HELLO:LEAVEPARTY]",
                         context=ContextTag([context.HELLO]),
                         destination=Cue(ContextTag([context.LEAVEPARTY])))

HELLO_OPENSHOP = Reply("[HELLO:OPEN_SHOP]",
                       context=ContextTag([context.HELLO]),
                       destination=Cue(ContextTag([context.OPEN_SHOP])))

HELLO_OPENSCHOOL = Reply("[HELLO:OPEN_SCHOOL]",
                         context=ContextTag([context.HELLO]),
                         destination=Cue(ContextTag([context.OPEN_SCHOOL])))

HELLO_PERSONAL = Reply("[HELLO:PERSONAL]",
                       context=ContextTag([context.HELLO]),
                       destination=Cue(ContextTag([context.PERSONAL])))

HELLO_PROBLEM = Reply("[HELLO:PROBLEM]",
                      context=ContextTag([context.HELLO]),
                      destination=Cue(ContextTag([context.PROBLEM])))

HELLO_QUERY = Reply("[HELLO:QUERY]",
                    context=ContextTag([context.HELLO]),
                    destination=Cue(ContextTag([context.QUERY])))

HELLOQUERY_QUERY = Reply("[HELLOQUERY:QUERY]",
                         context=ContextTag([context.HELLO, context.QUERY]),
                         destination=Cue(ContextTag([context.QUERY])))

HELLO_REVEAL = Reply("[HELLO:REVEAL]",
                     destination=Cue(ContextTag([context.REVEAL])),
                     context=ContextTag([context.HELLO]))

HELLO_SELFINTRO = Reply("[HELLO:SELFINTRO]",
                        destination=Cue(ContextTag([context.SELFINTRO])),
                        context=ContextTag([context.HELLO]))

HELLO_SOLUTION = Reply("[HELLO:SOLUTION]",
                       destination=Cue(ContextTag([context.SOLUTION])),
                       context=ContextTag([context.HELLO]))

INFOPERSONAL_GOODBYE = Reply("[INFO_PERSONAL:GOODBYE]",
                             context=ContextTag([context.INFO, context.PERSONAL]),
                             destination=Cue(ContextTag([context.GOODBYE])))

INFOPERSONAL_JOIN = Reply("[INFO_PERSONAL:JOIN]",
                          context=ContextTag([context.INFO, context.PERSONAL]),
                          destination=Cue(ContextTag([context.JOIN])))

INFOPERSONAL_PROPOSALJOIN = Reply("[INFO_PERSONAL:JOIN]",
                          context=ContextTag([context.INFO, context.PERSONAL]),
                          destination=Cue(ContextTag([context.PROPOSAL, context.JOIN])))

INFO_CUSTOM = Reply("{reply}",
                    destination=Cue(ContextTag([context.CUSTOM])),
                    context=ContextTag([context.INFO]))

INFO_CUSTOMREPLY = Reply("{reply}",
                         destination=Cue(ContextTag([context.CUSTOMREPLY])),
                         context=ContextTag([context.INFO]))

INFO_GOODBYE = Reply("[INFO:GOODBYE]",
                  context=ContextTag([context.INFO]),
                  destination=Cue(ContextTag([context.GOODBYE])))

INFO_INFO = Reply("[INFO:INFO]",
                  context=ContextTag([context.INFO]),
                  destination=Cue(ContextTag([context.INFO])))

MISSION_ACCEPT = Reply("[MISSION:ACCEPT]",
                       context=ContextTag([context.MISSION]),
                       destination=Cue(ContextTag([context.ACCEPT])))

MISSION_DENY = Reply("[MISSION:DENY]",
                     context=ContextTag([context.MISSION]),
                     destination=Cue(ContextTag([context.DENY])))

MISSION_CUSTOMREPLY = Reply("{reply}",
                         destination=Cue(ContextTag([context.CUSTOMREPLY])),
                         context=ContextTag([context.MISSION]))

MISSIONPROBLEM_JOIN = Reply("[MISSION_PROBLEM:JOIN]",
                            context=ContextTag([context.MISSION, context.PROBLEM]),
                            destination=Cue(ContextTag([context.JOIN])))

MISSIONPROBLEM_GOODBYE = Reply("[MISSION_PROBLEM:GOODBYE]",
                               context=ContextTag([context.MISSION, context.PROBLEM]),
                               destination=Cue(ContextTag([context.GOODBYE])))

PERSONAL_GOODBYE = Reply("[INFO_PERSONAL:GOODBYE]",
                         context=ContextTag([context.PERSONAL]),
                         destination=Cue(ContextTag([context.GOODBYE])))

PERSONAL_JOIN = Reply("[INFO_PERSONAL:JOIN]",
                      context=ContextTag([context.PERSONAL]),
                      destination=Cue(ContextTag([context.JOIN])))

PROPOSAL_ACCEPT = Reply("[PROPOSAL:ACCEPT]",
                        context=ContextTag([context.PROPOSAL]),
                        destination=Cue(ContextTag([context.ACCEPT])))

PROPOSALJOIN_ACCEPT = Reply("[PROPOSAL_JOIN:ACCEPT]",
                            context=ContextTag([context.PROPOSAL, context.JOIN]),
                            destination=Cue(ContextTag([context.ACCEPT])))

PROPOSAL_DENY = Reply("[PROPOSAL:DENY]",
                      context=ContextTag([context.PROPOSAL]),
                      destination=Cue(ContextTag([context.DENY])))

PROPOSALJOIN_DENY = Reply("[PROPOSAL_JOIN:DENY]",
                          context=ContextTag([context.PROPOSAL, context.JOIN]),
                          destination=Cue(ContextTag([context.DENY])))

QUERY_ANSWER = Reply("{reply}",
                     destination=Cue(ContextTag([context.ANSWER])),
                     context=ContextTag([context.QUERY]))

SELFINTRO_CUSTOM = Reply("{reply}",
                    destination=Cue(ContextTag([context.CUSTOM])),
                    context=ContextTag([context.SELFINTRO]))

SELFINTRO_GOODBYE = Reply("[SELFINTRO:GOODBYE]",
                          context=ContextTag([context.SELFINTRO]),
                          destination=Cue(ContextTag([context.GOODBYE])))

SELFINTRO_JOIN = Reply("[SELFINTRO:JOIN]",
                       context=ContextTag([context.SELFINTRO]),
                       destination=Cue(ContextTag([context.JOIN])))

SELFINTRO_LEAVEPARTY = Reply("[HELLO:LEAVEPARTY]",
                             context=ContextTag([context.SELFINTRO]),
                             destination=Cue(ContextTag([context.LEAVEPARTY])))

SELFINTRO_PROPOSALJOIN = Reply("[DOYOUWANTTOBELANCEMATE]",
                               context=ContextTag([context.SELFINTRO]),
                               destination=Cue(ContextTag([context.PROPOSAL, context.JOIN])))

SOLUTION_ACCEPT = Reply("[ICANDOTHAT]",
                        context=ContextTag([context.SOLUTION]),
                        destination=Cue(ContextTag([context.ACCEPT])))
