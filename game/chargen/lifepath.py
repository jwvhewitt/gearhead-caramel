import pbge
import gears
from gears import personality,tags,stats
from gears.meritbadges import TagReactionBadge
import pygame

from gears.oldghloader import BADGE_CRIMINAL
from .. import ghdialogue
from ..ghdialogue.ghgrammar import Default
import random

BADGE_ACADEMIC = TagReactionBadge("Academic","You are familiar with the language and culture of academia.",remods={tags.Academic:10})
BADGE_GEARHEAD = TagReactionBadge("Gearhead","You are obsessed with mecha and anything having to do with mecha.",remods={tags.Craftsperson:10})
BADGE_POPSTAR = TagReactionBadge("Pop Star","You released a few songs and attained some notoriety as a pop star.",remods={tags.Media:10})
BADGE_SOLDIER = TagReactionBadge("Soldier","Your time in the army taught you camraderie with all who serve.",remods={tags.Military:10})

# Character generation is lifepath based.

class LifePathOption(object):
    def __init__(self,name,desc,personality_tags=(),stat_mods=None,badges=(),biomessage="",biogram=None):
        self.name = name
        self.desc = desc
        self.personality_tags = list(personality_tags)
        self.stat_mods = dict()
        if stat_mods:
            self.stat_mods.update(stat_mods)
        self.badges = list(badges)
        self.biomessage = biomessage
        self.biogram = dict()
        if biogram:
            self.biogram.update(biogram)
    def apply(self,cgen):
        ghdialogue.trait_absorb(cgen.biogram,self.biogram,cgen.pc.get_tags())
        if self.biomessage:
            nugramdict = cgen.biogram.copy()
            ghdialogue.trait_absorb(nugramdict,ghdialogue.ghgrammar.DEFAULT_GRAMMAR,cgen.pc.get_tags())
            cgen.pc.bio += ' ' + pbge.dialogue.grammar.convert_tokens(self.biomessage,nugramdict,allow_maybe=False)
        for k,v in self.stat_mods.items():
            cgen.bio_bonuses[k] += v
        cgen.bio_badges += self.badges
        cgen.bio_personality += self.personality_tags

class LPIdealistBonus(object):
    def __init__(self,name,desc,biomessage='',biogram=None):
        self.name = name
        self.desc = desc
        self.biomessage = biomessage
        self.biogram = dict()
        if biogram:
            self.biogram.update(biogram)
    def apply(self,cgen):
        ghdialogue.trait_absorb(cgen.biogram,self.biogram,cgen.pc.get_tags())
        if self.biomessage:
            nugramdict = cgen.biogram.copy()
            ghdialogue.trait_absorb(nugramdict,ghdialogue.ghgrammar.DEFAULT_GRAMMAR,cgen.pc.get_tags())
            cgen.pc.bio += ' ' + pbge.dialogue.grammar.convert_tokens(self.biomessage,nugramdict,allow_maybe=False)
        stat_list = random.sample(gears.stats.PRIMARY_STATS,3)
        for s in stat_list:
            cgen.bio_bonuses[s] += 1
        cgen.bio_personality.append(personality.Idealist)


class LPRandomMutation(object):
    def __init__(self,name,desc,biomessage='',biogram=None):
        self.name = name
        self.desc = desc
        self.biomessage = biomessage
        self.biogram = dict()
        if biogram:
            self.biogram.update(biogram)
    def apply(self,cgen):
        mutation = random.choice(personality.MUTATIONS)
        cgen.bio_personality.append(mutation)
        mutation.apply(cgen.pc,cgen.bio_bonuses)
        ghdialogue.trait_absorb(cgen.biogram,self.biogram,cgen.pc.get_tags())
        if self.biomessage:
            nugramdict = cgen.biogram.copy()
            ghdialogue.trait_absorb(nugramdict,ghdialogue.ghgrammar.DEFAULT_GRAMMAR,cgen.pc.get_tags())
            cgen.pc.bio += ' ' + pbge.dialogue.grammar.convert_tokens(self.biomessage,nugramdict,allow_maybe=False)


CHOOSE_PEACE = LifePathOption("Peace", "You vow to protect the weak, and prevent tragedies like those you've witnessed from happening again.", personality_tags = (personality.Peace,),
                             biomessage = "[LPE_INTRO]",
                             biogram={
                                 "[LPE_INTRO]": {
                                     Default: [
                                         "Now, you have dedicated your life to peace and protecting the powerless.",
                                         "These days you work to protect people and stop tragedies like those you've witnessed from happening again."
                                     ]
                                 }
                             })
CHOOSE_GLORY = LifePathOption("Glory", "You seek a life of danger and excitement. Riches and fame would be pretty good too.", personality_tags = (personality.Glory,),
                             biomessage = "[LPE_INTRO]",
                             biogram={
                                 "[LPE_INTRO]": {
                                     Default: [
                                         "Now, you have dedicated your life to seeking adventure and glory.",
                                         "So far you haven't had great success, but you know it's only a matter of time before you're number one!"
                                     ]
                                 }
                             })
CHOOSE_JUSTICE = LifePathOption("Justice", "You have sworn to uphold the principles of justice, to see the good rewarded and the guilty punished.", personality_tags = (personality.Justice,),
                             biomessage = "[LPE_INTRO]",
                             biogram={
                                 "[LPE_INTRO]": {
                                     Default: [
                                         "Now, you have dedicated your life to the pursuit of justice.",
                                         "Following that, you pledged yourself to the quest for justice. This is the principle that motivates you as a cavalier."
                                     ]
                                 }
                             })
CHOOSE_FELLOWSHIP = LifePathOption("Fellowship", "You want to build bridges instead of just blowing them up.", personality_tags=(personality.Fellowship,),
                             biomessage = "[LPE_INTRO]",
                             biogram={
                                 "[LPE_INTRO]": {
                                     Default: [
                                         "If life has taught you anything, it's that we're all in this together. You strive to honor this fellowship with other cavaliers.",
                                         "These days, you enjoy being a cavalier mostly for the fellowship."
                                     ]
                                 }
                             })
CHOOSE_DUTY = LifePathOption("Duty", "You know no life other than being a cavalier, and live in strict adherence to the Cavalier Code.", personality_tags = (personality.Duty,),
                             biomessage = "[LPE_INTRO]",
                             biogram={
                                 "[LPE_INTRO]": {
                                     Default: [
                                         "You strive every day to fulfil your duty as a cavalier.",
                                         "Life so far has taught you the importance of responsibility. You accept your duty with steely resolve."
                                     ]
                                 }
                             })

class LifePathChoice(object):
    def __init__(self,prompt,options=()):
        self.prompt = prompt
        self.options = options

class LifePathNode(object):
    def __init__(self,name,desc,choices=(),next=(),next_prompt='',auto_fx=None):
        self.name = name
        self.desc = desc
        self.choices = choices
        self.next = next
        self.next_prompt = next_prompt
        self.auto_fx = auto_fx

FAIL_POPSTAR = LifePathOption("One Hit Wonder","My music career went nowhere. (Performance skill, Pop Star merit badge)",
                              stat_mods={stats.Performance:1},badges=(BADGE_POPSTAR,),
                              biomessage="[LPD_FAIL]",
                              biogram={
                                  "[LPD_FAIL]": {
                                      Default: [
                                          "You decided to start a band. Your one and only single ended up the most hated song of NT154.",
                                          "You accepted a recording contract before you were ready for the bigtime and ended up a has-been before you even got a chance to start."
                                      ]
                                  }
                              })
FAIL_FRIENDDIED = LifePathOption("Shadow of Death","My friend died and I couldn't save them. (Medicine skill, Grim trait)",
                                 stat_mods={stats.Medicine:1},personality_tags=(personality.Grim,),
                              biomessage="[LPD_FAIL]",
                              biogram={
                                  "[LPD_FAIL]": {
                                      Default: [
                                          "A routine mission went bad. One of your lancemates was critically injured, and you couldn't save [object_pronoun].",
                                          "Your friend got shot during a mission. You tried to save [object_pronoun], but failed."
                                      ]
                                  }
                              })

D_FAILURE = LifePathNode(
    "Failure","You failed at an important task, and now bear the responsibility for the consequences.",
    choices=(
        LifePathChoice("What sort of failure did you experience?",(FAIL_POPSTAR,FAIL_FRIENDDIED)),
        LifePathChoice("How do you choose to deal with this failure?",(CHOOSE_PEACE,CHOOSE_JUSTICE,CHOOSE_DUTY)),
    ),
    auto_fx=LifePathOption("Failure Auto","...",
        biomessage="[LPD_INTRO]",
        biogram={
            "[LPD_INTRO]": {
                Default: [
                    "Unfortunately, your plans for life were upturned by a single mistake.",
                    "Just when your life started looking up, a single accident turned everything upside down."
                ]
            }
        })
)

BETR_MENTOR = LifePathOption("Caution","I must never let my guard down again. (Scouting skill)",
                             stat_mods={stats.Scouting:1},
                              biomessage="[LPD_BETR]",
                              biogram={
                                  "[LPD_BETR]": {
                                      Default: [
                                          "Following this, you swore to never let your guard down again.",
                                          "Since that time you've been cautious about other people.",
                                          "You never saw it coming."
                                      ]
                                  }
                              })


BETR_LABMATE = LifePathOption("Revenge","I will get strong enough to defeat them. (Mecha Fighting bonus)",
                             stat_mods={stats.MechaFighting:1},
                              biomessage="[LPD_BETR]",
                              biogram={
                                  "[LPD_BETR]": {
                                      Default: [
                                          "You swore to train until you are strong enough to enact revenge.",
                                          "You promised that one day you will defeat them."
                                      ]
                                  }
                              })

D_BETRAYAL = LifePathNode(
    "Betrayal","You were betrayed by someone close to you.",
    choices=(
        LifePathChoice("What was your reaction to this betrayal?",(BETR_MENTOR,BETR_LABMATE)),
        LifePathChoice("What will you do moving forward?",(CHOOSE_PEACE,CHOOSE_JUSTICE,CHOOSE_FELLOWSHIP)),
    ),
    auto_fx=LifePathOption("Betrayal Auto","...",
        biomessage="[LPD_INTRO]",
        biogram={
            "[LPD_INTRO]": {
                Default: [
                    "During an important mission, you were betrayed by a friend.",
                    "On your first mission as a cavalier, you were betrayed by your mentor."
                ]
            }
        })
)

DEST_MECHALOVE = LifePathOption("Mecha Mania","I was born to pilot mecha. (Repair skill, Gearhead badge)",
                                stat_mods={stats.Repair:1},badges=(BADGE_GEARHEAD,),
                                biomessage="[LPD_DEST]",
                                biogram={
                                    "[LPD_DEST]": {
                                        Default: [
                                            "You spent your life savings on a new mecha and became a cavalier."
                                        ]
                                    }
                                })
DEST_GOLDENTONGUE = LifePathOption("Golden Tongue","I am both a problem solver and a troublemaker. (Negotiation skill)",
                                   stat_mods={stats.Negotiation:1},
                                   biomessage="[LPD_DEST]",
                                   biogram={
                                       "[LPD_DEST]": {
                                           Default: [
                                               "You talked a [client] into giving you a free mecha, and set out to become a cavalier."
                                           ]
                                       },
                                       "[client]": {
                                           Default: [
                                               "recruiter", "corporate executive", "friend", "trucker", "mechanic"
                                           ]
                                       }
                                   })

D_DESTINY = LifePathNode(
    "Destiny","I felt a calling that I couldn't ignore.",
    choices=(
        LifePathChoice("What is your great destiny?",(DEST_MECHALOVE,DEST_GOLDENTONGUE)),
        LifePathChoice("How do you choose to deal with this destiny?",(CHOOSE_GLORY,CHOOSE_JUSTICE,CHOOSE_FELLOWSHIP)),
    ),
    auto_fx=LifePathOption("Destiny Auto","...",
        biomessage="[LPD_INTRO]",
        biogram={
            "[LPD_INTRO]": {
                Default: [
                    "You always felt that you were destined for greater things.",
                    "One day, you left all of that to go fulfil your destiny."
                ]
            }
        })

)

POVE_CRIME = LifePathOption("Turn to Crime","I stole what I needed to survive. (Stealth skill, Criminal badge)",
                            stat_mods={stats.Stealth:1}, badges=(BADGE_CRIMINAL,),
                            biomessage="[LPD_POVE]",
                            biogram={
                                "[LPD_POVE]": {
                                    Default: [
                                        "During this time, you did some things you aren't proud of just to survive.",
                                        "Around this time, you did a number of things that aren't technically legal."
                                    ]
                                }
                            })
POVE_MERCENARY = LifePathOption("Mercenary","I became a soldier of fortune. (Ranged Combat bonus)",
                                  stat_mods={stats.RangedCombat:1},
                                  biomessage="[LPD_POVE]",
                                  biogram={
                                      "[LPD_POVE]": {
                                          Default: [
                                              "You became a mercenary, selling your skills to the highest bidder.",
                                              "You traveled the solar system as a mercenary, seeking out trouble spots for your next big contract."
                                          ]
                                      }
                                  })

D_POVERTY = LifePathNode(
    "Poverty","You lost whatever money you may once have had, and are now in dire straits.",
    choices=(
        LifePathChoice("How did you survive during this time?",(POVE_CRIME,POVE_MERCENARY)),
        LifePathChoice("How do you choose to deal with your poverty?",(CHOOSE_GLORY,CHOOSE_DUTY,CHOOSE_FELLOWSHIP)),
    ),
    auto_fx=LifePathOption("Poverty Auto","...",
                           biomessage="[LPD_INTRO]",
                           biogram={
                               "[LPD_INTRO]": {
                                   Default: [
                                       "With no money and no options, you were forced to leave home.",
                                       "Unfortunately, the money you were counting on never started to pour in."
                                   ]
                               }
                           })

)

WAR_SPECIALIST = LifePathOption("Mecha Specialist","I fought, using my talents as an EW specialist. (Computers skill)",
                                stat_mods={stats.Computers:1},
                                biomessage="[LPD_WAR]",
                                biogram={
                                    "[LPD_WAR]": {
                                        Default: [
                                            "Your expertise at electronic warfare came in handy during the fighting.",
                                            "You joined a defense squad as their ECM specialist."
                                        ]
                                    }
                                })
WAR_BIOTECH = LifePathOption("Lostech Hunting","I sought info about PreZero bioweapons to aid my side. (Biotechnology skill)",
                             stat_mods={stats.Biotechnology:1},
                             biomessage="[LPD_WAR]",
                             biogram={
                                 "[LPD_WAR]": {
                                     Default: [
                                         "Hearing rumors of reawakened bioweapons, you were sent to learn what you could about these ancient threats.",
                                         "As news arrived of reawakened bioweapons, your knowledge of lost technology became highly valuable."
                                     ]
                                 }
                             })

D_WAR = LifePathNode(
    "War","Everything got put on hold when open warfare broke out.",
    choices=(
        LifePathChoice("What did you do during the war?",(WAR_SPECIALIST,WAR_BIOTECH)),
        LifePathChoice("How do you choose to deal with this conflict?",(CHOOSE_GLORY,CHOOSE_DUTY,CHOOSE_PEACE)),
    ),
    auto_fx=LifePathOption("War Auto","...",
                           biomessage="[LPD_INTRO]",
                           biogram={
                               "[LPD_INTRO]": {
                                   Default: [
                                       "You fought against [enemies].",
                                       "Your home was destroyed in an enemy attack, forcing you to fight for your life.",
                                       "When [enemies] attacked your neighborhood, fighting became a matter of survival."
                                   ]
                               },
                               "[enemies]": {
                                   personality.GreenZone: [
                                       "Typhon", "Aegis commandoes"
                                   ],
                                   personality.DeadZone: [
                                       "Typhon", "Aegis infiltrators"
                                   ]
                               }
                           })

)

SURV_PET = LifePathOption("Animal Companion","I had a dog who kept me safe. (Dominate Animal skill)",
                          stat_mods={stats.DominateAnimal:1},
                          biomessage="[LPC_SURV]",
                          biogram={
                              "[LPC_SURV]": {
                                  Default: [
                                      "Fortunately, you had a big dog who protected you until you were big enough to look after yourself.",
                                      "When you were targeted by [badguys], it was a stray dog that came to your defense."
                                  ]
                              },
                              "[badguys]": {
                                  Default: [
                                      "bullies","muggers","thieves"
                                  ]
                              }
                          })
SURV_TALK = LifePathOption("Fast Talker","I learned to talk my way out of bad situations. (Negotiation skill)",
                           stat_mods={stats.Negotiation:1},
                           biomessage="[LPC_SURV]",
                           biogram={
                               "[LPC_SURV]": {
                                   Default: [
                                       "Thanks to your fast wits, you could talk your way out of most bad situations.",
                                       "You discovered a talent for negotiation. With nothing more than a golden tongue, you soon began to climb the heap."
                                   ]
                               }
                           })

C_SURVIVAL = LifePathNode(
    "Survival","Life was tough. All you could do was to survive, and then just barely. (+2 Vitality)",
    choices=(
        LifePathChoice("What allowed you to get through this period?",(SURV_PET,SURV_TALK)),
    ),
    next_prompt="Pick a crisis.",
    next=(D_WAR,D_FAILURE,D_POVERTY),
    auto_fx = LifePathOption("Survival Bonus","Vitality + 2",
                             stat_mods={stats.Vitality:2},
                             biomessage="[LPC_INTRO]",
                             biogram={
                                 "[LPC_INTRO]": {
                                     Default: [
                                         "Despite all the obstacles the world threw at you, you refused to give up.",
                                         "Through perserverance you managed to survive and prosper under terrible circumstances."
                                     ]
                                 }
                             })
)

HAKN_THIEF = LifePathOption("Stealing Things","I was a thief. (Stealth skill)",
                            stat_mods={stats.Stealth:1},
                            biomessage="[LPC_HAKN]",
                            biogram={
                                "[LPC_HAKN]": {
                                    Default: [
                                        "You became a notorious thief, easily able to slip past guards."
                                    ],
                                    personality.Passionate: [
                                        "You became a cat burgular, stealing priceless treasures as their owners slept just meters away."
                                    ],
                                    personality.Easygoing: [
                                        "You took up shoplifting. Although this wasn't a lucrative career, it paid the bills."
                                    ]
                                }
                            })
HAKN_HACKER = LifePathOption("Hacking","I was a computer hacker. (Computers skill)",
                             stat_mods={stats.Computers:1},
                             biomessage="[LPC_HAKN]",
                             biogram={
                                 "[LPC_HAKN]": {
                                     Default: [
                                         "Online you were known as [Adjective] [Noun], [LPC_HAKN_DESC]."
                                     ]
                                 },
                                 "[LPC_HAKN_DESC]": {
                                     Default: [
                                         "the infamous hacker","[city]'s greatest hacker",
                                         "the feared cybercriminal"
                                     ]
                                 }
                             })

C_HARDKNOCKS = LifePathNode(
    "Hard Knocks","As a youth, you got mixed up in some dangerous times. (Athletics + 2, Criminal badge)",
    choices=(
        LifePathChoice("What sort of criminal activity were you involved in?",(HAKN_HACKER,HAKN_THIEF)),
    ),
    next_prompt="Pick a crisis.",
    next=(D_FAILURE,D_POVERTY,D_DESTINY),
    auto_fx=LifePathOption("Hard Knocks Bonus", "Athletics + 2",
                           stat_mods={stats.Athletics: 2}, badges=(BADGE_CRIMINAL,),
                           biomessage="[LPC_INTRO]",
                           biogram={
                               "[LPC_INTRO]": {
                                   Default: [
                                       "To make ends meet, you got involved in crime.",
                                       "You started committing crimes before you were old enough to really understand the consequences."
                                   ]
                               }
                           })
)

AUTO_SCIENCE = LifePathOption("The Sciences","Science, especially the lost art of biotech. (Biotechnology skill)",
                                stat_mods={stats.Biotechnology:1},
                              biomessage="[LPC_AUTO]",
                              biogram={
                                  "[LPC_AUTO]": {
                                      Default: [
                                          "You sought out esoteric tomes to learn the forbidden art of biotechnology.",
                                          "Your search for the lost science of biotechnology took you to ancient libraries and prezero ruins."
                                      ]
                                  }
                              })
AUTO_ART = LifePathOption("The Arts","Art, especially music. (Performance skill)",
                          stat_mods={stats.Performance:1},
                          biomessage="[LPC_AUTO]",
                          biogram={
                              "[LPC_AUTO]": {
                                  Default: [
                                      "Every night you practiced the [instrument], working hard to perfect your technique.",
                                  ]
                              },
                          })

C_AUTODIDACT = LifePathNode(
    "Autodidact","You taught yourself everything you know, and were a very good teacher. (Concentration + 2)",
    choices=(
        LifePathChoice("What subject captivated your interest?",(AUTO_ART,AUTO_SCIENCE)),
    ),
    next_prompt="Pick a crisis.",
    next=(D_BETRAYAL,D_DESTINY,D_POVERTY),
    auto_fx=LifePathOption("Autodidact Bonus", "Concentration + 2",
                           stat_mods={stats.Concentration: 2},
                           biomessage="[LPC_INTRO]",
                           biogram={
                               "[LPC_INTRO]": {
                                   Default: [
                                       "You completed your education using books and old datafiles.",
                                       "You spurned higher education in favor of studying by yourself."
                                   ]
                               }
                           })
)

UNI1_SCIENCE = LifePathOption("Science.","(Science skill)",
                              stat_mods={stats.Science:1},
                              biogram={
                                  "[major]": {
                                      Default: [
                                          "science"
                                      ]
                                  }
                              })
UNI1_MEDICINE = LifePathOption("Medicine.","(Medicine skill)",
                              stat_mods={stats.Medicine:1},
                               biogram={
                                   "[major]": {
                                       Default: [
                                           "medicine"
                                       ]
                                   }
                               })

UNI2_ENGINEERING = LifePathOption("Engineering.","(Repair skill)",
                                  stat_mods={stats.Repair:1},
                                  biomessage="[LPC_OUTRO]",
                                  biogram={
                                      "[minor]": {
                                          Default: [
                                              "engineering"
                                          ]
                                      }
                                  })
UNI2_COMPSCI = LifePathOption("Computer Science.","(Computers skill)",
                                  stat_mods={stats.Computers:1},
                              biomessage="[LPC_OUTRO]",
                              biogram={
                                  "[minor]": {
                                      Default: [
                                          "computer science"
                                      ]
                                  }
                              })

UNI2_MUSIC = LifePathOption("Music.","(Performance skill)",
                                  stat_mods={stats.Performance:1},
                                biomessage="[LPC_OUTRO]",
                                  biogram={
                                      "[minor]": {
                                          Default: [
                                              "music"
                                          ]
                                      }
                                  }
                            )

UNI2_POLYSCI = LifePathOption("Management.","(Negotiation skill)",
                                  stat_mods={stats.Negotiation:1},
                                biomessage = "[LPC_OUTRO]",
                                biogram = {
                                    "[minor]": {
                                        Default: [
                                            "management"
                                        ]
                                    }
                                })

UNI2_PHYSED = LifePathOption("Physical Education.","(Athletics skill bonus)",
                                  stat_mods={stats.Athletics:1},
                             biomessage="[LPC_OUTRO]",
                             biogram={
                                 "[minor]": {
                                     Default: [
                                         "physical education"
                                     ]
                                 }
                             })


C_UNIVERSITY = LifePathNode(
    "University","You studied at a prestigious university. (Choose two skills, Academics badge)",
    choices=(
        LifePathChoice("What was your major in university?",(UNI1_SCIENCE,UNI1_MEDICINE)),
        LifePathChoice("What was your minor in university?", (UNI2_COMPSCI,UNI2_ENGINEERING,UNI2_MUSIC,UNI2_PHYSED,UNI2_POLYSCI)),
    ),
    next_prompt="Pick a crisis.",
    next=(D_DESTINY,D_BETRAYAL,D_WAR),
    auto_fx=LifePathOption("University Bonus", "Academics badge",
                           badges=(BADGE_ACADEMIC,),
                           biomessage="[LPC_INTRO]",
                           biogram={
                               "[LPC_INTRO]": {
                                   Default: [
                                       "After high school you went to university."
                                   ],
                                   personality.Idealist: [
                                       "You finished high school early and entered university in your mid teens."
                                   ],
                                   personality.DeadZone: [
                                       "You were accepted into a university in the green zone."
                                   ]
                               },
                               "[LPC_OUTRO]": {
                                   Default: [
                                       "You majored in [major] and minored in [minor].",
                                       "You studied [major] and [minor]."
                                   ]
                               }
                           }
                           )
)

MILI_SCOUT = LifePathOption("Scout","I was a recon pilot. (Scouting skill)",
                            stat_mods={stats.Scouting:1},
                            biomessage="[LPC_MILI]",
                            biogram={
                                "[LPC_MILI]": {
                                    Default: [
                                        "Your skill as a recon pilot saved your lance on several occassions.",
                                        "You infiltrated enemy lines as a recon pilot."
                                    ]
                                }
                            })
MILI_TECH = LifePathOption("Technician","I was a field tech. (Repair skill)",
                            stat_mods={stats.Repair:1},
                           biomessage="[LPC_MILI]",
                           biogram={
                               "[LPC_MILI]": {
                                   Default: [
                                       "Your skill as a field tech helped keep your lance in the fight.",
                                       "As a technician you didn't see much action, you just had to clean up the mess when it was over."
                                   ]
                               }
                           })
MILI_GRUNT = LifePathOption("Mecha Pilot","I was just a grunt. (Mecha Gunnery bonus)",
                            stat_mods={stats.MechaGunnery:1},
                            biomessage="[LPC_MILI]",
                            biogram={
                                "[LPC_MILI]": {
                                    Default: [
                                        "You helped defend [town] against [enemies].",
                                        "You fought [enemies]."
                                    ]
                                }
                            })


C_MILITIA = LifePathNode(
    "Militia","You joined the military and learned how to fight. (Mecha Piloting bonus, Soldier badge)",
    choices=(
        LifePathChoice("What was your position in the army?",(MILI_SCOUT,MILI_TECH,MILI_GRUNT)),
    ),
    next_prompt="Pick a crisis.",
    next=(D_BETRAYAL,D_WAR,D_FAILURE),
    auto_fx=LifePathOption("Militia Bonus", "Mecha Piloting bonus, Soldier badge",
                            stat_mods={stats.MechaPiloting:1},
                           badges=(BADGE_SOLDIER,),
                           biomessage="[LPC_INTRO]",
                           biogram={
                               "[LPC_INTRO]": {
                                   Default: [
                                       "When [crisis], you joined the militia in [city].",
                                       "As soon as you were old enough to pilot a mecha, you signed up with the militia."
                                   ],
                                   personality.GreenZone: [
                                       "You joined the Terran Defense Force.",
                                       "You learned mecha piloting in the Solar Navy."
                                   ],
                                   personality.DeadZone: [
                                       "You were conscripted into the militia."
                                   ]
                               }
                           }
                           )
)

ORPH_LONER = LifePathOption("Loner","I kept to myself, and still don't get close to people. (Shy trait)",
                                 personality_tags=(personality.Shy,),
                            biomessage="[LPB_ORPH]",
                            biogram={
                                "[LPB_ORPH]": {
                                    Default: [
                                        "You were adopted by a family that neglected you.",
                                        "You shut yourself off from human connections."
                                    ]
                                }
                            })

ORPH_SOCIABLE = LifePathOption("New Family","I took comfort in my friends and caretakers. (Sociable trait)",
                                 personality_tags=(personality.Shy,),
                               biomessage="[LPB_ORPH]",
                               biogram={
                                   "[LPB_ORPH]": {
                                       Default: [
                                           "You were like a surrogate parent to the other orphans.",
                                           "Over time, you found a new family in your friends and caretakers.",
                                           "You were adopted by a family who cared for you deeply."
                                       ]
                                   }
                               })

B_ORPHAN = LifePathNode(
    "Orphan","You lost your parents at a young age. (+1 Ego, +1 Speed)",
    choices=(
        LifePathChoice("How did you cope with the loss of your parents?",(ORPH_LONER,ORPH_SOCIABLE)),
    ),
    next_prompt="How did you learn to be a cavalier?",
    next=(C_MILITIA,C_SURVIVAL,C_HARDKNOCKS),
    auto_fx=LifePathOption("Orphan Bonus", "+1 Ego, +1 Speed",
                           stat_mods={stats.Ego:1,stats.Speed:1},
                           biomessage="[LPB_INTRO]",
                           biogram={
                               "[LPB_INTRO]": {
                                   Default: [
                                       "Your parents died when you were very young.",
                                       "You were raised in an orphanage and never knew your parents.",
                                       "You were left on the doorstop of an orphanage in [town].",
                                       "Your parents were killed in an attack by [enemies]."
                                   ]
                               }
                           }
                           )
)

OUTC_MUTANT = LPRandomMutation("Obvious Mutation", "I have visible genetic mutations. (Mutant trait)",
                               biomessage="[LPB_OUTC]",
                               biogram={
                                   "[LPB_OUTC]": {
                                       Default: [
                                           "You were born with [mutation].", "As you grew up, you developed [mutation]."
                                       ]
                                   },
                                   "[mutation]": {
                                       Default: [
                                           "visible mutations",
                                       ],
                                       personality.FelineMutation: [
                                           "feline features", "cat ears", "feline ears"
                                       ],
                                       personality.DraconicMutation: [
                                           "scaly skin", "armored plates on your skin"
                                       ],
                                       personality.GeneralMutation: [
                                           "brightly colored skin",
                                       ]
                                   }
                               }
                             )

OUTC_CRIMINAL = LifePathOption("Juvenile Delinquent", "I got started in crime at a young age. (Criminal badge)",
                               badges=(BADGE_CRIMINAL,),
                               biomessage="[LPB_OUTC]",
                               biogram={
                                   "[LPB_OUTC]": {
                                       Default: [
                                           "Even as a child you were constantly in trouble with the law.",
                                           "You joined a gang and started committing petty crimes.",
                                       ]
                                   }
                               })

B_OUTCAST = LifePathNode(
    "Outcast","You have always lived on the fringes of society. (+1 Reflexes, +1 Craft)",
    choices=(
        LifePathChoice("What is it that set you apart from your peers?",(OUTC_CRIMINAL,OUTC_MUTANT)),
    ),
    next_prompt="How did you learn to be a cavalier?",
    next=(C_SURVIVAL,C_HARDKNOCKS,C_AUTODIDACT),
    auto_fx=LifePathOption("Outcast Bonus", "+1 Reflexes, +1 Craft",
                           stat_mods={stats.Reflexes:1,stats.Craft:1},
                           biomessage="[LPB_INTRO]",
                           biogram={
                               "[LPB_INTRO]": {
                                   Default: [
                                       "From birth, you never really fit in with your peers.",
                                       "Your early life was spent on the fringes of society."
                                   ]
                               }
                           }
                           )
)

IDEA_EASY = LifePathOption("Lazy Student","My natural talents made me lazy at school. (Easygoing trait)",
                                 personality_tags=(personality.Easygoing,),
                           biomessage="[LPB_IDEA]",
                           biogram = {
                               "[LPB_IDEA]": {
                                   Default: [
                                       "Because of your natural talents, you never had to work as hard as your peers.",
                                       "Your genetic enhancements meant you never had to push yourself."
                                   ]
                               }
                           }                           )

IDEA_HARD = LifePathOption("Overachiever","I was very competitive; Every subject was a challenge to be mastered. (Passionate trait)",
                                 personality_tags=(personality.Passionate,),
                           biomessage="[LPB_IDEA]",
                           biogram = {
                               "[LPB_IDEA]": {
                                   Default: [
                                       "In school you were very competitive. Every subject was a challenge to be mastered."
                                   ]
                               }
                           })

B_IDEALIST = LifePathNode(
    "Idealist","Your heritage includes a significant amount of genetic engineering. (+1 to three random stats)",
    choices=(
        LifePathChoice("How did you perform in school?",(IDEA_EASY,IDEA_HARD)),
    ),
    next_prompt="How did you learn to be a cavalier?",
    next=(C_HARDKNOCKS,C_AUTODIDACT,C_UNIVERSITY),
    auto_fx=LPIdealistBonus("Idealist Bonus", "+1 to three random stats",
                            biomessage="[LPB_INTRO]",
                            biogram={
                                "[LPB_INTRO]": {
                                    Default: [
                                        "As a child, you began to show exceptional abilities.",
                                        "You come from a long line of idealists, and your family had great expectations for you."
                                    ]
                                }
                            }
                           )
)

CITY_PROSPEROUS = LifePathOption("Good Neighborhood","I lived on the good side of town. (Cheerful trait)",
                                 personality_tags=(personality.Cheerful,),
                                 biomessage="[LPB_CITY]",
                                 biogram={
                                     "[LPB_CITY]": {
                                         Default: [
                                             "Your neighborhood was nice enough.",
                                             "Your family's home was on the rich side of town."
                                         ]
                                     }
                                 })

CITY_SLUMS = LifePathOption("Slums", "I lived in the slums. (Grim trait)",
                 personality_tags=(personality.Grim,),
                            biomessage="[LPB_CITY]",
                            biogram = {
                                "[LPB_CITY]": {
                                    Default: [
                                        "Your home was in the bad side of town.",
                                        "Your neighborhood was riddled with crime."
                                    ]
                                }
                            })

B_CITY = LifePathNode(
    "City","You were born in a city and led an average life there. (+1 Knowledge, +1 Charm)",
    choices=(
        LifePathChoice("What part of the city were you raised in?",(CITY_PROSPEROUS,CITY_SLUMS)),
    ),
    next_prompt="How did you learn to be a cavalier?",
    next=(C_AUTODIDACT,C_UNIVERSITY,C_MILITIA),
    auto_fx=LifePathOption("City Bonus", "+1 Knowledge, +1 Charm",
                           stat_mods={stats.Knowledge:1,stats.Charm:1},
                           biomessage="[LPB_INTRO]",
                           biogram = {
                               "[LPB_INTRO]": {
                                   Default: [
                                       "You grew up in [city].", "You were born in [city]."
                                   ]
                               }
                           }
                           )
)

FRON_WARZONE = LifePathOption("Dangerous Place","Our village was always under attack by bandits or raiders. (Grim trait)",
                                 personality_tags=(personality.Grim,),
                              biomessage="[LPB_FRON]",
                              biogram={
                                  "[LPB_FRON]": {
                                      Default: [
                                          "Your community was under constant attack by [enemies]."
                                      ]
                                  }
                              }
                              )

FRON_BORING = LifePathOption("Boring Life","Mostly it was boring; I longed to escape. (Passionate trait)",
                                 personality_tags=(personality.Passionate,),
                             biomessage="[LPB_FRON]",
                             biogram={
                                 "[LPB_FRON]": {
                                     Default: [
                                         "As a child you dreamed of going on big adventures.",
                                         "Growing up, you always dreamed of becoming a mecha pilot."
                                     ]
                                 }
                             }
                             )

FRON_COMMUNITY = LifePathOption("Close Community","Life was hard, but everyone helped everyone else out. (Sociable trait)",
                                 personality_tags=(personality.Sociable,),
                                biomessage="[LPB_FRON]",
                                biogram={
                                    "[LPB_FRON]": {
                                        Default: [
                                            "Your community was very close knit."
                                        ]
                                    }
                                }
                                )

B_FRONTIER = LifePathNode(
    "Frontier","You were born in a small town on the edge of civilization. (+1 Body, +1 Perception)",
    choices=(
        LifePathChoice("How was growing up in your frontier town?",(FRON_BORING,FRON_COMMUNITY,FRON_WARZONE)),
    ),
    next_prompt="How did you learn to be a cavalier?",
    next=(C_UNIVERSITY,C_MILITIA,C_SURVIVAL),
    auto_fx=LifePathOption("Frontier Bonus", "+1 Body, +1 Perception",
                           stat_mods={stats.Body:1,stats.Perception:1},
                           biomessage="[LPB_INTRO]",
                           biogram = {
                               "[LPB_INTRO]": {
                                   Default: [
                                       "You grew up in [village].", "You were born in [village]."
                                   ]
                               }
                           }
                           )
)

EART_GREENZONE = LifePathOption("The Green Zone","The Terran Federation green zone, where there is at least some semblance of peace and stability.",
                                 personality_tags=(personality.GreenZone,),
                                biogram={
                                    "[village]": {
                                        Default: [
                                            "Last Hope", "Hogye", "Ipshil", "Nara"
                                        ]
                                    },
                                    "[city]": {
                                        Default: [
                                            "Snake Lake", "Wujung", "Gyori", "Namok", "Norstead"
                                        ]
                                    },
                                    "[crisis]": {
                                        Default: [
                                            "Typhon awakened", "[enemies] attacked"
                                        ]
                                    },
                                    '[enemies]': {
                                        Default: [
                                            "Aegis Overlord", "bandits", "Clan Ironwind", "the Bone Devils",
                                        ]
                                    },
                                    "[town]": {
                                        Default: [
                                            "[village]", "[city]"
                                        ]
                                    }
                                }
                                )

EART_DEADZONE = LifePathOption("The Dead Zone","One of the fortresses in the dead zone. Food is scarce and life is precarious.",
                                 personality_tags=(personality.DeadZone,),
                               biogram={
                                   "[village]": {
                                       Default: [
                                           "Last Hope", "Kist", "Markheim Fortress"
                                       ]
                                   },
                                   "[city]": {
                                       Default: [
                                           "Ironwind Fortress", "Pirate Point"
                                       ]
                                   },
                                   "[crisis]": {
                                       Default: [
                                           "Typhon awakened", "[enemies] attacked"
                                       ]
                                   },
                                   '[enemies]': {
                                       Default: [
                                           "ravagers", "bandits", "rival fortresses", "the Bone Devils",
                                       ]
                                   },
                                   "[town]": {
                                       Default: [
                                           "[village]","[city]"
                                       ]
                                   }
                               })

A_EARTH = LifePathNode(
    "Earth","You are from Earth.",
    choices=(
        LifePathChoice("Which part of Earth are you from?",(EART_DEADZONE,EART_GREENZONE)),
    ),
    next_prompt="How was your early life?",
    next=(B_CITY,B_FRONTIER,B_IDEALIST,B_ORPHAN,B_OUTCAST),
)

STARTING_CHOICES = (A_EARTH,)

class BioBlock( object ):
    def __init__(self,model,width=220,bio_font=None,**kwargs):
        self.model = model
        self.width = width
        self.image=None
        self.font = bio_font or pbge.MEDIUMFONT
        self.update()

    def update(self):
        self.image = pbge.render_text(self.font, self.model.bio, self.width, justify=-1)
        self.height = self.image.get_height()

    def render(self,x,y):
        pbge.my_state.screen.blit(self.image,pygame.Rect(x,y,self.width,self.height))

class CGNonComSkillBlock(object):
    def __init__(self,cgen,width=220,skill_font=None,**kwargs):
        self.cgen = cgen
        self.width = width
        self.image=None
        self.font = skill_font or pbge.MEDIUMFONT
        self.update()
        self.height = self.image.get_height()

    def update(self):
        skillz = [sk.name for sk in self.cgen.bio_bonuses.keys() if sk in stats.NONCOMBAT_SKILLS]
        self.image = pbge.render_text(self.font, 'Skills: {}'.format(', '.join(skillz or ["None"])), self.width, justify=-1)

    def render(self,x,y):
        pbge.my_state.screen.blit(self.image,pygame.Rect(x,y,self.width,self.height))


class LifePathStatusPanel(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (BioBlock,CGNonComSkillBlock)

def generate_random_lifepath(cgen):
    current = random.choice(STARTING_CHOICES)
    while current:
        if current.auto_fx:
            current.auto_fx.apply(cgen)

        for c in current.choices:
            myop = random.choice(c.options)
            myop.apply(cgen)

        if current.next:
            current = random.choice(current.next)
        else:
            break
