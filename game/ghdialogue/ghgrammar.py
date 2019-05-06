from gears import personality,tags
#
#   GearHead Grammar
#
# Please note that the master grammar dict operates in a different way
# from the pbge grammar dict. Instead of each item resolving to a list
# of options, each list resolves to a dict of PersonalityTrait: [options,...]
#
# Uppercase tokens should expand to a complete sentence
# Lowercase tokens should not
# Camel Case tokens expand to an independent clause that can be turned
#  into a sentence by adding punctuation to the end, or incorporated
#  into a compound sentence.
# A standard offer token is generally the context tags of the offer separated
#  by underspaces.
# A standard reply token is generally two offer tokens separated by a colon.
#

# A meaningless constant
Default = None
LOVE = "LOVE"
LIKE = "LIKE"
DISLIKE = "DISLIKE"
HATE = "HATE"

DEFAULT_GRAMMAR = {
    "[ACCEPT_MISSION:GOODBYE]": {
        Default: ["I'll be back when I'm finished."
            ],
        personality.Cheerful: ["See you later!",
            ],
        personality.Grim: ["Time to get to work.",
            ],
        personality.Easygoing: [ "Guess I should get started.",
            ],
        personality.Passionate: ["I'll do my best!",
            ],
        personality.Sociable: ["I'll let you know how it goes.",
            ],
        personality.Shy: ["Goodbye.",
            ],
        },

    "[ACCEPT_MISSION:JOIN]": {
        Default: ["Why don't you come with me?"
            ],
        personality.Cheerful: ["Why don't you come too? It'll be fun.",
            ],
        personality.Grim: ["My odds would be better if you came too.",
            ],
        personality.Easygoing: [ "Wanna come with me?",
            ],
        personality.Passionate: ["Would you join me on this glorious mission?",
            ],
        personality.Sociable: ["I could use some company out there.",
            ],
        personality.Shy: ["Will you come too?",
            ],
        },
    "[Adjective]": {
        Default: [
            "Useless","Useful","Artificial","Adorable","Uncomfortable","Comfortable","Good","Bad","Open","Modern",
            "Shiny","Bright","Honorable","Stupid","Smart","Healthy","Sinful","Interesting","Surprising","Bland",
            "Sexy","Loud","Quiet","New","Important","Wonderful","Great","Fun","Beautiful","Pretty","Ugly",
            "Cool","Strange","Fast","Slow","Lucky","Big","Huge","Long","Small","Tiny","Exciting","Gigantic",
            "Cosmic","Natural","Unwanted","Delicate","Stormy","Fragile","Strong","Flexible","Rigid","Cold",
            "Hot","Irradiated","Poor","Living","Dead","Creamy","Delicious","Cool","Excellent","Boring","Happy",
            "Sad","Confusing","Valuable","Old","Young","Loud","Hidden","Bouncy","Magnetic","Smelly","Hard",
            "Easy","Serious","Kind","Gentle","Greedy","Lovely","Cute","Plain","Dangerous","Silly","Smart",
            "Fresh","Obsolete","Perfect","Ideal","Professional","Current","Fat","Rich","Poor","Wise","Absurd",
            "Foolish","Blind","Deaf","Creepy","Nice","Adequate","Expensive","Cheap","Fluffy","Rusted","Hormonal",
            "Lying","Freezing","Acidic","Green","Red","Blue","Yellow","Orange",'Purple',"Grey","Brown","Pink",
            "Dirty","Gothic","Metallic","Mutagenic","Outrageous","Incredible","Miraculous","Unlucky",
            "Hated", "Loved", "Feared"
        ]
    },
    "[adjective]": {
        Default: [
            "useless","useful","artificial","adorable","uncomfortable","comfortable","good","bad","open","modern",
            "shiny","bright","honorable","stupid","smart","healthy","sinful","interesting","surprising","bland",
            "sexy","loud","quiet","new","important","wonderful","great","fun","beautiful","pretty","ugly",
            "cool","strange","fast","slow","lucky","big","huge","long","small","tiny","exciting","gigantic",
            "cosmic","natural","unwanted","delicate","stormy","fragile","strong","flexible","rigid","cold",
            "hot","irradiated","poor","living","dead","creamy","delicious","cool","excellent","boring","happy",
            "sad","confusing","valuable","old","young","loud","hidden","bouncy","magnetic","smelly","hard",
            "easy","serious","kind","gentle","greedy","lovely","cute","plain","dangerous","silly","smart",
            "fresh","obsolete","perfect","ideal","professional","current","fat","rich","poor","wise","absurd",
            "foolish","blind","deaf","creepy","nice","adequate","expensive","cheap","fluffy","rusted","hormonal",
            "lying","freezing","acidic","green","red","blue","yellow","orange",'purple',"grey","brown","pink",
            "dirty","gothic","metallic","mutagenic","outrageous","incredible","miraculous","unlucky",
            "hated","loved","feared"
        ]
    },
    "[ATTACK]": {
        Default: ["I don't know what you're doing here, but you'll feel my wrath. [LETSFIGHT]",
            "You shouldn't have come here. [LETSFIGHT]"
            ],
        personality.Cheerful: ["I was hoping that today would be interesting, and now here you are... [LETSFIGHT]",
            ],
        personality.Grim: ["I'm afraid it's time for you to die... I'll try to make it painless. [LETSFIGHT]",
            "Those who oppose me end up dead. [LETSFIGHT]"
            ],
        personality.Easygoing: [ "And here I thought this was going to be an easy day. [LETSFIGHT]",
            "I don't mean to be unfriendly, but you've ended up in the wrong place at the wrong time. [LETSFIGHT]"
            ],
        personality.Passionate: ["A challenger approaches... do you think you can defeat me? [LETSFIGHT]",
            "I've been looking for someone to battle... [LETSFIGHT]",
            "You dare to challenge me? [LETSFIGHT]"
            ],
        personality.Sociable: ["I've heard of your skills, [audience]... [LETSFIGHT]",
            "Is this a challenge? I accept. [LETSFIGHT]"
            ],
        personality.Shy: ["[LETSFIGHT]",
            ],
        personality.Duty: [ "I can't allow you to interfere with my mission. [LETSFIGHT]",
            ],
        personality.Peace: [ "Though I don't wish to cause harm, I'm going to have to [fight_you]. [LETSFIGHT]",
            ],
        personality.Fellowship: [ "You know the rules... [LETSFIGHT]",
            ],
        personality.Glory: [ "Only one of us is going to leave here victorious. [LETSFIGHT]",
            ],
    },
    
    "[ATTACK:CHALLENGE]": {
        Default: ["I accept your challenge.","This won't go so well for you.",
            "I can take you.","Let's finish this.",
            ],
        personality.Cheerful: ["Sounds like fun.","Don't make me laugh.",
            "This is getting fun!",
            ],
        personality.Grim: ["You will regret challenging me.","This may be your last mistake.",
            "This will end in tears for you...",
            ],
        personality.Easygoing: [ "I guess we could do that.","Sure, I have nothing better to do.",
            ],
        personality.Passionate: ["Prepare to be demolished.","You don't know who you're messing with.",
            "You have no chance of beating me.","WAARGH!!!",
            ],
        personality.Sociable: ["I'm all ready to fight.","You're going to lose.",
            ],
        personality.Shy: ["Enough talk.","Whatever.",
            ],
        personality.Peace: [ "Maybe you should just give up now?",
            ],
        personality.Fellowship: [ "Let's keep this an honorable duel.",
            ],
    },

    "[ATTACK:COMBAT_INFO]": {
    # The data block should include "subject"
        Default: ["{subject}? What's that?","Tell me about {subject}."
            ],
        personality.Cheerful: ["I'd like to hear more about {subject}.",
            ],
        personality.Grim: ["Tell me about {subject} or die.",
            ],
        personality.Easygoing: [ "{subject}, you say?",
            ],
        personality.Passionate: ["What in blazes is {subject}?!",
            ],
        personality.Sociable: ["Tell me more about {subject}.",
            ],
        personality.Shy: ["What is {subject}?",
            ],
    },

    "[ATTACK:MERCY]": {
        Default: ["Get out of here.",
            ],
        personality.Cheerful: ["It's your lucky day, you can go.",
            ],
        personality.Grim: ["Get lost before I change my mind.",
            ],
        personality.Easygoing: [ "You can go home now.",
            ],
        personality.Passionate: ["Let me show you my mercy!",
            ],
        personality.Sociable: ["You can leave if you don't want to fight.",
            ],
        personality.Shy: ["Go.",
            ],
        personality.Peace: [ "I have no desire to fight you.",
            ],
        personality.Duty: [ "Run away now and I won't chase you.",
            ],
        personality.Fellowship: [ "Go on, I won't challenge you.",
            ],
        personality.Glory: [ "Maybe we can duel later, but not today.",
            ],
        personality.Justice: [ "It wouldn't be fair to fight you now.",
            ],
    },

    "[ATTACK:WITHDRAW]": {
        # The PC is withdrawing from combat.
        Default: ["Alright, I'll go.", "Okay, I'm leaving."
                  ],
        personality.Cheerful: ["You're no fun. I'm out of here.",
                               "Ugh, I didn't want to play with you anyhow."
                               ],
        personality.Grim: ["I'll leave... for now.", "I don't feel like [defeating_you] now.",
                           ],
        personality.Easygoing: ["Oh, sorry, I didn't mean to intrude.", "Really? I'd best be off, then.",
                                ],
        personality.Passionate: ["I'll go, but it doesn't mean you won.",
                                 "Take it easy, I'm just looking around.",
                                 ],
        personality.Sociable: ["I didn't know. I'll leave now.",
                               "[GOODBYE]",
                               ],
        personality.Shy: ["I'm leaving.", "So long.",
                          ],
    },

    "[CHALLENGE]": {
        Default: ["[THREATEN]",
            ],
        personality.Cheerful: ["Time to party.",
            ],
        personality.Grim: ["Prepare for death.","You don't stand a chance.",
            ],
        personality.Easygoing: [ "Shall we get started? Alright.",
            ],
        personality.Passionate: ["Show me what you have.",
            ],
        personality.Sociable: ["That's big talk. Prove it to me.",
            "You know what I'm going to do? [THREATEN]",
            ],
        personality.Shy: ["Shut up and fight.",
            ],
        personality.Justice: [ "For great justice!",
            ],
        personality.Glory: [ "May the best fighter win!",
            ],
    },

    "[CHAT]": {
        Default: [
            "[chat_lead_in] [News].",
        ],
    },

    "[chat_lead_in]": {
        Default: [
            "They say that","They say","I've heard that","I've heard","I think that","I think","Someone told me that",
            "A friend told me that","I believe","It's rumored that","People say that","Word around here is that",
            "It's been rumored that","Everyone knows that","Everyone says that","I heard a rumor that",
            "I heard someone say that","You may have heard that","It's common knowledge that","You should know that",
            "It's been said that","I often hear that","Someone said that","In my opinion,","In my humble opinion,",
            "My friend said that","All my friends say that","My friend told me that",
            "You may have heard this already, but","I bet","You'd never guess it, but","I bet you didn't know that",
            "There's been a rumour going around that","For your information,","Don't say I told you so, but",
            "To be completely honest with you,","Word is that"
        ],
    },

    "[CHAT:CHAT]": {
        Default: ["Anything else?", "You don't say."
                  ],
    },

    "[CHAT:GOODBYE]": {
        Default: ["[GOODBYE]",
                  ],
        personality.Cheerful: ["Thanks for letting me know. Goodbye.",
                               ],
        personality.Grim: ["This conversation has become tiresome.",
                           ],
        personality.Easygoing: ["I think we've chatted enough for now.",
                                ],
        personality.Passionate: ["Time to go, I have things to do.",
                                 ],
        personality.Sociable: ["Interesting. Well, I must be off.",
                               ],
        personality.Shy: ["That's all the chatter I can take today.",
                          ],
    },

    "[CHAT:INFO]": {
        # The data block should include "subject"
        Default: ["Tell me more about {subject}.",
                  ],
        personality.Cheerful: ["I'd like to hear more about {subject}.",
                               ],
        personality.Grim: ["Do you know more about {subject}?",
                           ],
        personality.Easygoing: ["Wait, what's this about {subject}?",
                                ],
        personality.Passionate: ["I must know about {subject}.",
                                 ],
        personality.Sociable: ["What more can you tell me about {subject}?",
                               ],
        personality.Shy: ["Tell me about {subject}.",
                          ],
    },

    "[defeating_you]": {
        Default: ["defeating you","beating you"
            ],
        personality.Cheerful: ["winning","kicking your arse"
            ],
        personality.Grim: ["destroying you","crushing you","causing you pain",
            "watching you suffer","killing you",
            ],
        personality.Easygoing: [ "fighting you",
            ],
        personality.Passionate: ["facing a true challenge","annihilating you",
            "showing you my true power",
            ],
        personality.Sociable: ["humiliating you",
            ],
        personality.Shy: ["stopping you",
            ],
    },

    "[DENY_JOIN]": {
        Default: ["That's too bad.","Too bad, I could have been a great help to you."
                  ],
        personality.Cheerful: ["Aw, I was really looking forward to joining you."
                               ],
        personality.Grim: ["This is your loss, not mine.",
                           ],
        personality.Easygoing: ["Yeah, well, I'll be right here if you ever change your mind.",
                                ],
        personality.Passionate: ["You don't know what you're missing.",
                                 ],
        personality.Sociable: ["Maybe we'll get to work together some other time.",
                               ],
        personality.Shy: ["Fair enough.",
                          ],
    },

    "[DOTHEYHAVEITEM]": {
    # The data block should hold the item name as "item".
        Default: [ "Don't they have {item}?",
            "They should have {item}.","What about their {item}?"
            ],
        },

    "[DOYOUACCEPTMYOFFER]": {
        Default: ["Do you accept my offer?",
                  ],
        personality.Cheerful: ["It's your lucky day.",
                               ],
        personality.Grim: ["You won't find a better offer.",
                           ],
        personality.Easygoing: ["So, what do you say?",
                                ],
        personality.Passionate: ["I promise you won't regret it.","You know you want it.",
                                 ],
        personality.Sociable: ["Don't you think that's a fair offer?",
                               ],
        personality.Shy: ["Take it or leave it.",
                          ],
    },

    "[DOYOUWANTTOBELANCEMATE]": {
        Default: ["I'm looking for a new lancemate.",
                  "Would you like to be my lancemate?"
                  ],
        personality.Cheerful: ["Want to join my lance? We have cookies.",
                               ],
        personality.Grim: ["I need a new lancemate. You'll do.",
                           ],
        personality.Easygoing: ["Wanna join my lance?",
                                ],
        personality.Passionate: ["I need your talents in my lance.",
                                 ],
        personality.Sociable: ["How'd you like to be part of my lance?",
                               ],
        personality.Shy: ["I need a new lancemate.",
                          ],

    },

    "[enemy_meks]": {
        # Insert your favorite euphemism or trash talk,
        Default: ["mecha", "enemy mecha",
                  ],
        personality.Cheerful: ["killer garbage cans","giant lawn mowers",
                               ],
        personality.Grim: ["bastards","geared up arseholes",
                           ],
        personality.Easygoing: ["guys","meks",
                                ],
        personality.Passionate: ["losers",
                                 ],
        personality.Sociable: ["hostile mecha",
            ],
        personality.Shy: ["enemies",
                          ],
        tags.Military: [
            "hostiles",
        ],
    },

    "[fight_you]": {
        Default: ["defeat you","fight you","beat you"
            ],
        personality.Cheerful: ["kick your arse",
            ],
        personality.Grim: ["destroy you","crush you","kill you",
            ],
        personality.Easygoing: [ "shoot you",
            ],
        personality.Passionate: ["battle you","challenge you","do battle",
            ],
        personality.Sociable: ["humiliate you",
            ],
        personality.Shy: ["stop you",
            ],
        personality.Peace: [ "stop you","oppose you"
            ],
    },

    "[GOOD]": {
        Default: ["Good.","Great!"
                  ],
        personality.Cheerful: ["Glad to hear it!",
                               ],
        personality.Grim: ["Fine.",
                           ],
        personality.Easygoing: ["Alright!",
                                ],
        personality.Passionate: ["Fantastic!",
                                 ],
        personality.Sociable: ["I'll see you later.",
                               ],
        personality.Shy: ["Okay.",
                          ],
    },

    "[GOODBYE]": {
        Default: ["Goodbye."
            ],
        personality.Cheerful: ["Bye bye.",
            ],
        personality.Grim: ["Until we meet again.",
            ],
        personality.Easygoing: [ "See ya.",
            ],
        personality.Passionate: ["Farewell.",
            ],
        personality.Sociable: ["I'll see you later.","Don't be a stranger."
            ],
        personality.Shy: ["Bye.",
            ],
        },

    "[GOODLUCK]": {
        Default: ["Good luck.","Good luck with that."
            ],
        personality.Cheerful: ["Have fun out there.",
            ],
        personality.Grim: ["Try not to get yourself killed.",
            ],
        personality.Easygoing: [ "Shouldn't be too hard.",
            ],
        personality.Passionate: ["Do your best!", "Give it your all!",
            ],
        personality.Sociable: ["I wish you the best of luck.",
            ],
        personality.Shy: ["Good luck.",
            ],
        },    

    "[HAGOODONE]": {
        Default: ["Ha! That's a good one.","Yeah, right."
            ],
        personality.Cheerful: ["LOL!",
            ],
        personality.Grim: ["Ha ha, very funny.","Was that supposed to be a joke?"
            ],
        personality.Easygoing: [ "You're funny.",
            ],
        personality.Passionate: ["Ha! You should've been a comedian.",
            ],
        personality.Sociable: ["Why don't you pull my other leg.",
            ],
        personality.Shy: ["Ha!",
            ],
        },    

    "[HELLO]": {
        Default: ["Hello.","Hello [audience]."
            ],
        personality.Cheerful: ["Good to see you, [audience].",
            ],
        personality.Grim: ["Oh, it's you.","We meet again."
            ],
        personality.Sociable: ['Hello there, [audience].',
            ],
        personality.Shy: ['Hi.',
            ],
        personality.Easygoing: [ "Yo, [audience].","Hi [audience]."
            ],
        personality.Passionate: ['Hey [audience]!','[audience]!'
            ],
        },

    # The data block should hold the item name as "item".
    "[HELLO:ASK_FOR_ITEM]": {
        Default: ["Do you have a {item}?",
            "I'm looking for a {item}. Seen one?"
            ],
        },

    "[HELLO:CHAT]": {
        Default: ["What's up?", "What's been happening lately?"
                  ],
        personality.Cheerful: ["Hear any good news lately?",
                               ],
        personality.Grim: ["Got any bad news to share?",
                           ],
        personality.Sociable: ["Hi, [audience]. What's new?","Just stopping by to chat.",
                               ],
        personality.Shy: ["I'm looking for information.",
                          ],
        personality.Easygoing: ["Hear anything interesting lately?",
                                ],
        personality.Passionate: ["Hey [audience] , what's the latest news?",
                                 ],
    },

    "[HELLO:GOODBYE]": {
        Default: ["Well, I must be off.","See you later.",
            ],
        },

    # The data block should include "subject"
    "[HELLO:INFO]": {
        Default: [ "Tell me about the {subject}.",
            "What can you tell me about the {subject}?"
            ],
        },

    # The data block should include "subject"
    "[HELLO:INFO_PERSONAL]": {
        Default: [ "How have you been doing?","What's new?",
            "I hear you have a story about the {subject}."
            ],
        },

    "[HELLO:JOIN]": {
        Default: [ "Would you like to join my lance?",
            "How about joining my lance?"
            ],
        personality.Cheerful: ["Come join my lance, it'll be fun.",
            ],
        personality.Grim: ["It will be dangerous, but I need your help.",
            ],
        personality.Easygoing: [ "I could use some help on this mission.",
            ],
        personality.Passionate: ["I'd be honored if you would join my lance.",
            ],
        personality.Sociable: ["I want you to join my lance.",
            ],
        personality.Shy: ["Your skills would be valuable on this mission.",
            ],

        },

    "[HELLO:MISSION]": {
        Default: ["Do you have any missions available?",
                  "I'm looking for a mission."
                  ],
        personality.Cheerful: ["Hey, are you looking for a pilot? It's your lucky day.",
                               ],
        personality.Grim: ["I don't suppose you'd have a mission available?",
                           ],
        personality.Easygoing: ["Know where I could find a mission around here?",
                                ],
        personality.Passionate: ["If you need a pilot, then you need me!",
                                 ],
        personality.Sociable: ["Word is that you need a pilot for a mission.",
                               ],
        personality.Shy: ["I'm here for a mission.",
                          ],

    },

    "[HELLO:OPEN_SHOP]": {
        Default: ["I'd like to see what you have for sale.",
                  "What do you have for sale?"
                  ],
        personality.Cheerful: ["Show me what you have!",
                               ],
        personality.Grim: ["Show me your goods.",
                           ],
        personality.Easygoing: ["Mind if I take a look at your stuff?",
                                ],
        personality.Passionate: ["I'm looking for new equipment.",
                                 ],
        personality.Sociable: ["Tell me about the things you have for sale.",
                               ],
        personality.Shy: ["I'll tell you if I need help.",
                          ],
    },

    "[HELLO:PROPOSAL]": {
        Default: ["I want to talk about {subject}.",
                  "Let's talk about {subject}."
                  ],
    },

    "[HELP_ME]": {
        # Simple request for help; may be a component of other HELP_ME_* patterns.
        Default: ["I need your help.", "Help me!"
                  ],
        personality.Cheerful: ["You've arrived just in time to help me!",
                               ],
        personality.Grim: ["Without your help, the situation looks hopeless.",
                           ],
        personality.Easygoing: ["Think you could help me out?",
                                ],
        personality.Passionate: ["Help me, please!",
                                 ],
        personality.Sociable: ["I could really use your help right about now.",
                               "Any help you could give would be really appreciated."
                               ],
        personality.Shy: ["Assistance required.",
                          ],
    },

    "[HELP_ME_VS_MECHA_COMBAT]": {
        # The NPC is asking the PC with help during mecha combat.
        Default: ["I am currently under attack... [HELP_ME]", "I'm under attack by [enemy_meks]. [HELP_ME]"
                  ],
        personality.Cheerful: ["These [enemy_meks] decided that they want a party. [HELP_ME]",
                               ],
        personality.Grim: ["I'm being attacked by [enemy_meks]... [HELP_ME]",
                           ],
        personality.Easygoing: ["I'm having some trouble with these [enemy_meks] shooting at me. [HELP_ME]",
                                ],
        personality.Passionate: ["[HELP_ME] I'm fighting some [enemy_meks]!",
                                 ],
        personality.Sociable: ["Finally, some reinforcements have arrived... I'm under attack by [enemy_meks]. [HELP_ME]",
                               ],
        personality.Shy: ["I am under attack. [HELP_ME]",
                          ],
    },

    "[ICANDOTHAT]": {
        # Speaker is responding in the affirmative to a request.
        Default: ["I can do that.",
                  ],
        personality.Cheerful: ["I'd be happy to do that.",
                               ],
        personality.Grim: ["I suppose it wouldn't kill me to do that.",
                           ],
        personality.Easygoing: ["I think I can manage that.",
                                ],
        personality.Passionate: ["I'll do it!",
                                 ],
        personality.Sociable: ["I can do that for you.",
                               ],
        personality.Shy: ["Alright.",
                          ],
        LIKE: ["For you, I can do it.",
               ],
        LOVE: ["For you, anything.",
               ],

    },


    "[INFO_PERSONAL]": {
        # This pattern should be supported by IP_* tokens gathered
        # from the plots involving this character. You don't need to
        # provide a complete set, and the bits will likely come from
        # multiple sources.
        #   IP_STATUS: A general platitude, like "I'm fine."
        #   IP_Business: An independent clause about the character's work life.
        #   IP_Pleasure: An independent clause about the character's social life
        #   IP_GoodNews,IP_BadNews: What it says on the tin. Independent clauses.
        #   IP_Worry,IP_Hope: Should be obvious. Independent clauses.
        Default: ["[IP_STATUS]", "[IP_STATUS] [IP_NEWS]", "[IP_STATUS] [IP_NEWS] [IP_OPINION]", "[IP_STATUS] [IP_OPINION]",
            "[IP_STATUS] [IP_Business]. [IP_BadNews], but [IP_GoodNews].",
            "[IP_STATUS] [IP_Pleasure]. [IP_BadNews], but fortunately [IP_GoodNews].",
            "[IP_STATUS] [IP_Business]. [IP_GoodNews]; unfortunately [IP_BadNews].",
            "[IP_STATUS] [IP_Business], and [IP_Pleasure]. [IP_GoodNews].",
            "[IP_STATUS] [IP_Business], and [IP_Pleasure]. [IP_BadNews].",
            "[IP_STATUS] [IP_Pleasure]; also, [IP_GoodNews].",
            "[IP_STATUS] [IP_Business]; unfortunately, [IP_BadNews].",
            "[IP_STATUS] [IP_Pleasure]. [IP_GoodNews]; unfortunately [IP_BadNews].",
            "[IP_STATUS] [IP_Business], and [IP_Pleasure]. [IP_BadNews], but [IP_GoodNews].",
            "[IP_STATUS] [IP_Pleasure], and [IP_Business]. [IP_GoodNews], but [IP_BadNews].",
            "[IP_STATUS] [IP_GoodNews]... [IP_Hope].",
            "[IP_STATUS] [IP_BadNews]... [IP_Worry]."
            ],
        personality.Cheerful: ["[IP_STATUS] [IP_Pleasure], and [IP_GoodNews].",
            "[IP_STATUS] [IP_Pleasure], and [IP_Business]. [IP_GoodNews], which is great.",
            "[IP_STATUS] [IP_Business]. [IP_GoodNews]... [IP_Hope].",
            "[IP_STATUS] [IP_Pleasure]. [IP_BadNews]... Still, [IP_Hope].",
            "[IP_STATUS] [IP_Hope]... [IP_Pleasure], and [IP_GoodNews].",
            "[IP_STATUS] [IP_Hope]... [IP_GoodNews].",
            ],
        personality.Grim: ["[IP_STATUS] [IP_BadNews]... but at least [IP_Business].",
            "[IP_STATUS] [IP_Business]. [IP_GoodNews], but then again [IP_BadNews].",
            "[IP_STATUS] [IP_Business], and [IP_Pleasure]. As you might expect, [IP_BadNews].",
            "[IP_STATUS] [IP_Worry]... [IP_BadNews]. Still, [IP_Pleasure].",
            "[IP_STATUS] [IP_Worry]... [IP_BadNews].",
            ],
        personality.Easygoing: [ "[IP_STATUS] [IP_Business], but in my spare time [IP_Pleasure].",
            "[IP_STATUS] Earlier on [IP_BadNews], but [IP_GoodNews]. You know.",
            "[IP_STATUS] In my free time [IP_Pleasure]. [IP_OPINION]"
            ],
        personality.Passionate: ["[IP_STATUS] [IP_Pleasure], and also [IP_Business]. [IP_BadNews] but that doesn't worry me.",
            "[IP_STATUS] Would you believe that [IP_GoodNews]? Also, [IP_Pleasure]!",
            "[IP_STATUS] [IP_NEWS] [IP_Worry], but [IP_Hope]!"
            "[IP_STATUS] I've been working hard; [IP_Business]. [IP_OPINION]"
            ],
        personality.Sociable: ["[IP_STATUS] [IP_Pleasure], while by day [IP_Business]. [IP_BadNews], but [IP_GoodNews].",
            "[IP_STATUS] The main thing I have to report is that [IP_Pleasure]. Also, [IP_GoodNews].",
            "[IP_STATUS] Did you hear that [IP_BadNews]? I'm afraid it's true. But at least [IP_Pleasure].",
            "[IP_STATUS] [IP_Worry], but also [IP_Hope].",
            "[IP_STATUS] You should know that [IP_NEWS] [IP_OPINION]",
            ],
        personality.Shy: ["[IP_STATUS] [IP_Business].","[IP_STATUS] [IP_Business]. [IP_Pleasure].",
            "[IP_STATUS] [IP_GoodNews], but [IP_BadNews].","[IP_STATUS] [IP_NEWS]",
            ],
        },


    "[INFO_PERSONAL:JOIN]": {
        Default: ["Why don't you join my lance?",
            ],
        personality.Cheerful: ["Let's go on an adventure together.",
            ],
        personality.Grim: ["Let's go wreck some stuff.",
            ],
        personality.Easygoing: [ "That's cool. Wanna join my lance?",
            ],
        personality.Passionate: ["Here's an idea- Why not join my lance?",
            "Join me; together we will be unbeatable!",
            ],
        personality.Sociable: ["You're just the kind of lancemate I need.",
            ],
        personality.Shy: ["Join me.",
            ],
        },
        
    "[INFO_PERSONAL:GOODBYE]": {
        Default: ["Talk with you later.",
            ],
        personality.Cheerful: ["Nice talking to you, but I have to go.",
            ],
        personality.Grim: ["I must go.",
            ],
        personality.Easygoing: [ "I gotta run.",
            ],
        personality.Passionate: ["Wild. I'll see you around.",
            ],
        personality.Sociable: ["See you; we'll talk again later.",
            ],
        personality.Shy: ["Yeah. I've got to go now.",
            ],
        personality.Peace: ["Take care; I'll see you later.",
            ],
        },

    "[instrument]": {
        Default: [
            "guitar", "keytar", "drums", "violin", "bass", "synthesizer", "organ",
            "mandolin", "theremin", "turntable", "piano", "saxophone", "melodica"
        ]
    },


    "[IP_NEWS]": {
        Default: ["[IP_GoodNews].","[IP_BadNews].","[IP_Business].","[IP_Pleasure]."
            ],
        personality.Cheerful: ["[IP_GoodNews]."],
        personality.Grim: ["[IP_BadNews]."],
        personality.Fellowship: ["[IP_Pleasure]."],
        personality.Duty: ["[IP_Business]."],
        },

    "[IP_OPINION]": {
        Default: ["[IP_Hope].","[IP_Worry].",
            ],
        personality.Cheerful: ["[IP_Hope]."],
        personality.Grim: ["[IP_Worry]."],
        },
        
    "[IP_STATUS]": {
        # Opening statement for an INFO_PERSONAL offer.
        Default: ["I'm fine.","Overall, not bad.","It's been alright."
            ],
        personality.Cheerful: ["I've been good.","I've been doing alright.",
            "Things are good.","I'm good."
            ],
        personality.Grim: ["It hasn't been easy.","Nothing I can't handle.",
            "I haven't died yet.","Things could be worse."
            ],
        personality.Easygoing: [ "Same as usual.","I'm keeping at it.",
            "I've been taking it easy.","Trying not to work too hard."
            ],
        personality.Passionate: ["Life never ceases to amaze.","I'm keeping busy.",
            "I've been working out.","I'm great!"
            ],
        personality.Sociable: ["You know how it is.","Let me tell you about it.",
            "You've got to hear this.", "I've been dying to tell you."
            ],
        personality.Shy: ["I don't know what to say.","Where to start...",
            "Um...", "Yeah."
            ],
        },



    # The data block should include "mission"
    "[IWILLDOMISSION]": {
        Default: [ "I'll get to work.",
            "I'll {mission}.", "[ICANDOTHAT]"
            ],
        personality.Cheerful: ["Sounds like fun.",
            ],
        personality.Grim: ["This may get me killed, but I'll do it.",
            ],
        personality.Easygoing: [ "I guess I could {mission}.","Time to {mission}."
            ],
        personality.Passionate: ["I swear to {mission}!","I won't let you down!"
            ],
        personality.Sociable: ["I will do this mission.",
            ],
        personality.Shy: ["I'll do it.","Okay."
            ],

        },

    "[JOIN]": {
        Default: ["Alright, I'll join your lance. [LETSGO]",
                  "Join your lance? [ICANDOTHAT]"
                  ],
        personality.Cheerful: ["Fantastic, I was getting bored just sitting around. [LETSGO]",
                               ],
        personality.Grim: ["To follow you into the jaws of death? [ICANDOTHAT]",
                           ],
        personality.Easygoing: ["Sure, why not? [LETSGO]",
                                ],
        personality.Passionate: ["I've been waiting for another chance to test myself in combat! [LETSGO]",
                                 ],
        personality.Sociable: ["Okay, I'll join your team. [LETSGO]",
                               ],
        personality.Shy: ["Alright. [LETSGO]",
                          ],

    },

    "[LETSFIGHT]": {
        Default: ["Let's fight.","Prepare for battle.","I will [fight_you]."
            ],
        personality.Cheerful: ["Let's fight! This will be fun.","It'll be fun [defeating_you].",
            "Shall we dance?","I can't wait to [fight_you]."
            ],
        personality.Grim: ["Time to finish this.","I will break you.","I will enjoy [defeating_you].",
            "Your story comes to an end now.", "I will teach you what it means to suffer."
            ],
        personality.Easygoing: [ "We might as well start the fight.","Ready to go?",
            "I'm gonna try [defeating_you], okay?","I don't think this battle will last too long.",
            "Might as well get this over with.","The highlight of my day will be [defeating_you].",
            "I think I have to [fight_you]."
            ],
        personality.Passionate: ["Let the battle begin!","I'll show you my true power!",
            "You are about to learn the true meaning of power!", "Let's fight!",
            "Defeat me if you can!", "Show me a real fight!","Just see how I [fight_you]!"
            ],
        personality.Sociable: ["Shall we battle?","Prepare to defend yourself.",
            "I can't wait for everyone to see me [defeating_you].",
            "Now I get to see if you can live up to your reputation.",
            "I'm going to have to [fight_you] now."
            ],
        personality.Shy: ["Let's go.","Let's start.","Defend yourself.",
            "I can take you."
            ],
        personality.Peace: [ "I'm afraid I must [fight_you].",
            ],
        personality.Justice: [ "You're about to get what you deserve.",
            ],
    },

    "[LETSGO]": {
        Default: ["Let's go!",
                  ],
        personality.Cheerful: ["This will be fun!",
                               ],
        personality.Grim: [ "Let's go wreck some stuff.",
                           ],
        personality.Easygoing: ["No worries, right?",
                                ],
        personality.Passionate: ["Excelsior!","Gear up and roll out!"
                                 ],
        personality.Sociable: ["Here we go!","Shall we get started?"
                               ],
        personality.Shy: ["Let's go.",
                          ],
        DISLIKE: [ "Might as well get this over with.",
                ],
        LIKE:   ["It will be a pleasure to go with you.",
                 ]
    },

    "[LONGTIMENOSEE]": {
        Default: ["Hello [audience], long time no see.",
            "Long time no see, [audience].",],
        personality.Sociable: ["Well there's a face I haven't seen in a while.",
            ],
        personality.Shy: ["Long time no see.",
            ],
        },
    "[MISSION_PROBLEM:JOIN]": {
        Default: ["I could really use your help out there.",
            "Sounds like I could use some backup.",
            "This would be easier if you came with me."
            ],
        },

    "[MISSION_PROBLEM:GOODBYE]": {
        Default: ["Well, I've heard enough about that.",
            ],
        },

    "[MISSION:ACCEPT]": {
        Default: ["I accept your mission.", "Alright, I'll get to work."
                  ],
        personality.Cheerful: ["Sounds good to me.",
                               ],
        personality.Grim: ["I'll make sure it gets done."
                           ],
        personality.Easygoing: ["Okay then, I'll do it."
                                ],
        personality.Passionate: ["I will not let you down!",
                                 ],
        personality.Sociable: ["Alright, let's do it.",
                               ],
        personality.Shy: ["I accept.",
                          ],
    },

    "[MISSION:DENY]": {
        Default: ["No, I don't want this mission.", "You'll have to find someone else."
                  ],
        personality.Cheerful: ["I'm going to have to give that a 'no'.",
                               ],
        personality.Grim: ["I reject your offer."
                           ],
        personality.Easygoing: ["Sorry, but I can't do it."
                                ],
        personality.Passionate: ["This job isn't my style.",
                                 ],
        personality.Sociable: ["Find someone else for this job.",
                               ],
        personality.Shy: ["I refuse.",
                          ],
    },

    "[News]": {
        Default: [
            "not much is going on",
        ],
    },

    "[NOEXPOSURE]": {
        Default: ["I can't afford to work for exposure.",
                  ],
        personality.Cheerful: ["I'm willing to be paid in credits, Atheran wine, or vintage PreZero character figures.",
                               ],
        personality.Grim: ["First off, I expect to get paid.",
                           ],
        personality.Easygoing: ["Okay, so let's work out the business part.",
                                ],
        personality.Passionate: ["I'm the best, if you can afford my rates.",
                                 ],
        personality.Sociable: ["I can tell you're not the sort of person who would expect me to work for free.",
                               ],
        personality.Shy: ["I don't work for free.",
                          ],
    },

    "[Noun]": {
        Default: [
            "Hominid","Underwear","Paluke","Artifice","Lie","Knowledge","Battle","Weather","Food","News",
            "Mecha","Fashion","Athlete","Music","Politics","Religion","Love","War","History",
            "Technology","Time","Internet","Literature","Destiny","Romance","Base","Stuff","Agriculture",
            "Sports","Science","Television","Atmosphere","Sky","Color","Sound","Taste","Friendship","Law",
            "Beer","Singing","Cola","Pizza","Vaporware","Buzz","Mood","Dissent","City","House","Town",
            "Village","Country","Planet","Fortress","Universe","Program","Arena","Wangtta","Hospital",
            "Medicine","Therapy","Library","Education","Philosophy","Family","Jive","Feel","Coffee",
            "Hope","Hate","Love","Fear","Sale","Life","Market","Enemy","Data","Fish","Beast",
            "Something","Everything","Nothing","Sabotage","Justice","Fruit","Pocket","Parfait","Flavor",
            "Talent","Prison","Plan","Noise","Bottom","Force","Anything","Top","Appeal","Booster",
            "Complaint","Chatting","Dream","Heart","Secret","Fauna","Desire","Situation","Risk",
            "Crime","Vice","Virtue","Treasure","Storm","Vapor","School","Uniform","World","Body",
            "Pain","Fault","Profit","Business","Prophet","Animal","Bedroom","Kitchen","Home","Apartment",
            "Vehicle","Machine","Bathroom","Fruit","Side","Entertainment","Movie","Game","Chemistry",
            "Synergy","Opinion","Hero","Villain","Thief","Fantasy","Adventure","Mission","Job",
            "Career","Glamour","Diary","Expression","Hairdo","Environment","Wizard","Drug"
        ]
    },
    "[noun]": {
        Default: [
            "[instrument]","underwear","paluke","artifice","lie","knowledge","battle","weather","food","news",
            "mecha","fashion","soccer competition","music","politics","religion","love","war","history",
            "technology","time","internet","literature","destiny","romance","base","stuff","agriculture",
            "sports","science","television","atmosphere","sky","color","sound","taste","friendship","law",
            "beer","singing","cola","pizza","vaporware","buzz","mood","dissent","city","house","town",
            "village","country","planet","fortress","universe","program","arena","wangtta","hospital",
            "medicine","therapy","library","education","philosophy","family","jive","feel","coffee",
            "hope","hate","love","fear","sale","life","market","enemy","data","fish","lion taming",
            "something","everything","nothing","sabotage","justice","fruit","pocket","parfait","flavor",
            "talent","prison","plan","noise","bottom","force","anything","top","appeal","booster",
            "complaint","chatting","dream","heart","secret","fauna","desire","situation","risk",
            "crime","vice","virtue","treasure","storm","vapor","school","uniform","world","body",
            "pain","fault","profit","business","prophet","animal","bedroom","kitchen","home","apartment",
            "vehicle","machine","bathroom","fruit","side","entertainment","movie","game","chemistry",
            "synergy","opinion","hero","villain","thief","fantasy","adventure","mission","job",
            "career","glamour","diary","expression","hairdo","environment","wizard","drug"

        ]
    },

    "[object_pronoun]": {
        Default: [
            "him","her","zem"
        ]
    },

    "[PROPOSAL:ACCEPT]": {
        Default: ["I accept your offer.", "Alright, I'll do it."
                  ],
        personality.Cheerful: ["Sounds good to me.",
                               ],
        personality.Grim: ["Not sure this is a good idea, but I accept."
                           ],
        personality.Easygoing: ["Okay."
                                ],
        personality.Passionate: ["Yes, I'll do it!",
                                 ],
        personality.Sociable: ["Alright, let's do it.",
                               ],
        personality.Shy: ["Yes, I accept.",
                          ],
        personality.Justice: ["That seems fair. I accept.",
                              ],
    },

    "[PROPOSAL_JOIN:ACCEPT]": {
        Default: ["[PROPOSAL:ACCEPT]", "I accept; join me."
                  ],
        personality.Cheerful: ["I'd love for you to join me.",
                               ],
        personality.Grim: ["Alright, as long as you pull your weight.", "You better be worth it."
                           ],
        personality.Easygoing: ["Okay. I could use the help."
                                ],
        personality.Passionate: ["Yes, join me!",
                                 ],
        personality.Sociable: ["Welcome to the team.",
                               ],
        personality.Shy: ["Okay. Come on, then.",
                          ],
        personality.Duty: ["Alright, but I expect you to do your duty.",
                           ],
        personality.Fellowship: ["Alright, the more the merrier.",
                                 ],
    },

    "[PROPOSAL:DENY]": {
        Default: ["I don't think so.","I will come back later."
                  ],
        personality.Cheerful: ["No for now, but maybe later.",
                               ],
        personality.Grim: ["No.","Absolutely not."
                           ],
        personality.Easygoing: ["I need some time to think about this.","Maybe later? I can't now..."
                                ],
        personality.Passionate: ["I reject your offer.",
                                 ],
        personality.Sociable: ["I'll get back to you on that.",
                               ],
        personality.Shy: ["Not right now.",
                          ],
    },

    "[PROPOSAL_JOIN:DENY]": {
        Default: ["[PROPOSAL:DENY]",
                  ],
        personality.Cheerful: ["Maybe you can join someone else's lance?",
                               ],
        personality.Grim: ["You overestimate your importance.",
                           ],
        personality.Easygoing: ["Maybe you can join my lance later?"
                                ],
        personality.Passionate: ["I cannot agree to this at the moment.",
                                 ],
        personality.Sociable: ["Not now, but let's keep in touch.",
                               ],
        personality.Shy: ["On second thought I'm happier alone.",
                          ],
    },

    "[THANK_YOU]": {
        # A simple thank you is appropriate.
        Default: ["Thank you.", "Thanks."
                  ],
    },

    "[THANKS_FOR_CHOOSING_ME]": {
        # The PC is being thanked for choosing the NPC to be a part of the lance or a team or whatever.
        Default: ["[THANK_YOU]", "Thanks for choosing me."
                  ],
        personality.Cheerful: ["We're going to have such fun together."
                               ],
        personality.Grim: ["I will do my best, until one or the other of us bites it. Can't ask for more than that.",
                           ],
        personality.Easygoing: ["Alright!",
                                ],
        personality.Passionate: ["In time you will see the full extent of my power!",
                                 ],
        personality.Sociable: ["Thanks for letting me be a part of your team.",
                               ],
        personality.Shy: ["So I guess I'm part of your team now.",
                          ],
        personality.Duty: ["I will do my best.",
                           ],
        personality.Fellowship: ["So now we're all on the same team.",
                                 ],
        LIKE: ["Thanks. I am looking forward to working with you.",
               ],
        DISLIKE: ["Really? I guess that's good...",
                  ],
    },

    "[THANKS_FOR_HELP]": {
        # The PC is being thanked for doing something.
        Default: ["[THANK_YOU]", "Thanks for your help."
                  ],
        personality.Cheerful: ["I'm glad you decided to help out; thanks!","That went well. Thanks!"
                               ],
        personality.Grim: ["I guess I should thank you.","That could have gone a lot worse; thank you."
                           ],
        personality.Easygoing: ["Thanks.","Hey, thanks for helping me out.",
                                ],
        personality.Passionate: ["Thank you!!!","Thank you so much!",
                                 ],
        personality.Sociable: ["Thank you very much.",
                               ],
        personality.Shy: ["Thanks.",
                          ],
        personality.Duty: ["Thanks; I owe you one.",
                           ],
        LIKE: ["I knew I could depend on you.",
               ],
        DISLIKE: ["I'm surprised you came through.",
                  ],
    },

    "[THANKS_FOR_MECHA_COMBAT_HELP]": {
        # The PC is being thanked for helping with mecha combat.
        Default: ["[THANKS_FOR_HELP]", "Thanks for your help against those [enemy_meks]."
                  ],
        personality.Cheerful: ["You're a pretty good pilot, you know?", "I'm glad to have fought at your side today.",
                               ],
        personality.Grim: ["The battle could have gone differently without you; thanks.",
                           ],
        personality.Easygoing: ["Those [enemy_meks] weren't so tough after all.",
                                ],
        personality.Passionate: ["Those [enemy_meks] didn't stand a chance against our combined might!",
                                "Thanks for the assist against those [enemy_meks]!"
                                 ],
        personality.Sociable: ["Thanks; I don't know if I could have done that by myself.",
                               ],
        personality.Shy: ["I'm thankful you were here today.",
                          ],
        LIKE: ["It was a pleasure to fight at your side",
               ],
        DISLIKE: ["Maybe you're a better pilot than I thought."
                  ],
    },

    "[threat]": {
        Default: ["rend you limb from limb",
            "mop the floor with you","defeat you","humiliate you",
            "beat you","fight you","destroy you","demolish you",
            "wreck you","obliterate you","spank your monkey",
            "spank you","kill you","murder you","knock your clock",
            "knock you down","make you wish you were never born",
            "make you beg for mercy","make you beg for death",
            "stop you","break you","make you cry","make you scream",
            "eviscerate you","snap your neck","crush your bones",
            "take you down","crush you","crush you like a bug",
            "squash you","squash you like a grape","cut you to pieces",
            "pound you","injure you terribly","beat you black and blue",
            "give you a thorough ass-kicking","kick your ass",
            "kick your behind","kick your butt","slap you around",
            "send you to the hospital","be your worst nightmare",
            "wreck your plans","raise a little hell","rant and roar",
            "open a can of whoop-ass","do my limit break",
            "rage like a rabid wolverine","get violent","get VERY violent",
            "power up","go berserk","show you my true skills",
            "demonstrate my fighting power","show you how strong I am",
            "fight like a demon","show no mercy","fight dirty",
            "hold back nothing","call upon my warrior spirit",
            "boot your head","snap you like a twig","ruin your day",
            "shred you","send you to oblivion","send you up the bomb",
            ],
        },
        
    "[THREATEN]": {
        Default: ["I'm going to [threat]!","I will [threat]!",
        ],    
    },

    "[WAITINGFORMISSION]": {
        # Waiting for a mission.
        Default: ["I'm just waiting for my next mission."
                  ],
        personality.Cheerful: ["The time spent waiting between missions is like a mini-vacation, when you think about it."
                               ],
        personality.Grim: ["I'm just temporarily unemployed. I'll find another mission soon.",
                           ],
        personality.Easygoing: ["I should probably be out there looking for a new mission, but whatever...",
                                ],
        personality.Passionate: ["I am currently between missions, but must remain ever vigilant. There could be an emergency at any time.",
                                 ],
        personality.Sociable: ["You wouldn't know of any mission openings, would you? I am between contracts at the moment.",
                               ],
        personality.Shy: ["Just waiting for my next mission.",
                          ],
    },

    "[WITHDRAW]": {
        # The PC is withdrawing from combat.
        Default: ["Off with you, then.", "Don't return to this place."
                  ],
        personality.Cheerful: ["[GOODBYE] Remember, we don't like visitors right here.", "Ding-dong-deng, that's the right answer! [GOODBYE]"
                               ],
        personality.Grim: ["Good, you choose to live.", "Come back again and I will [threat].",
                           ],
        personality.Easygoing: ["No worries. See you around.", "Yeah, I think that'd be easiest for both of us.",
                                ],
        personality.Passionate: ["Too bad; I was looking forward to [defeating_you].", "I can tell you wouldn't have been a true challenge anyhow.",
                                 ],
        personality.Sociable: ["Alright, I'll see you later... just not around here, okay?", "We really ought to put up some signs on the perimeter, keep people like you from wandering in. [GOODBYE]",
                               ],
        personality.Shy: ["Go. Now.", "Smart choice.",
                          ],
    },

}


