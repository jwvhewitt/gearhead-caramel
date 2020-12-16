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

FIRST_TIME = "FIRST_TIME"
MET_BEFORE = "MET_BEFORE"

DEFAULT_GRAMMAR = {
    "[ACCEPT_CHALLENGE]": {
        Default: ["I accept your challenge!",
                  ],
        personality.Cheerful: ["Sounds good to me!",
                               ],
        personality.Grim: ["I will make you regret challenging me.",
                           ],
        personality.Easygoing: ["Sure, why not?",
                                ],
        personality.Passionate: ["Of course I accept your challenge! Let's go!",
                                 ],
        personality.Sociable: ["Your challenge has been accepted.",
                               ],
        personality.Shy: ["I accept.",
                          ],
        personality.Glory: ["You know I just can't refuse a challenge!",
                            ],
    },

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

    "[AGREE]": {
        Default: ["I agree with you."
                  ],
        personality.Cheerful: ["Yes, I was thinking that too!"
                               ],
        personality.Grim: ["I see no fault in that.",
                           ],
        personality.Easygoing: ["Sounds alright to me."
                                ],
        personality.Passionate: ["I think that's a fantastic idea!",
                                 ],
        personality.Sociable: ["I think you have the right idea.",
                               ],
        personality.Shy: ["I agree.",
                          ],
    },

    "[as_far_as_I_know]": {
        Default: ["As far as I know"
                  ],
        personality.Cheerful: ["You'll be happy to know","To the best of my knowledge"
                               ],
        personality.Grim: ["I'm afraid that",
                           ],
        personality.Easygoing: ["I kinda think","I could be wrong, but I've heard that"
                                ],
        personality.Passionate: ["I know that",
                                 ],
        personality.Sociable: ["I've heard people saying that",
                               ],
        personality.Shy: ["I believe",
                          ],
    },

    "[ATTACK]": {
        Default: ["I don't know what you're doing here, but you'll feel my wrath. [LETSFIGHT]",
            "You shouldn't have come here. [LETSFIGHT]", "[BATTLE_GREETING] [LETSFIGHT]"
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
            "I can take you.","Let's finish this.", "I must [objective_pp].", "I will [objective_pp]."
            ],
        personality.Cheerful: ["Sounds like fun.","Don't make me laugh.",
            "This is getting fun!", "I'm here to [objective_pp] and crack jokes."
            ],
        personality.Grim: ["You will regret challenging me.","This may be your last mistake.",
            "This will end in tears for you...", "I will [objective_pp] or die trying!"
            ],
        personality.Easygoing: [ "I guess we could do that.","Sure, I have nothing better to do.",
                                 "I'm just gonna [objective_pp]."
            ],
        personality.Passionate: ["Prepare to be demolished.", "You don't know who you're messing with.",
            "You have no chance of beating me.", "WAARGH!!!", "I will [objective_pp]!"
            ],
        personality.Sociable: ["I'm all ready to fight.", "You're going to lose.", "I am here to [objective_pp]."
            ],
        personality.Shy: ["Enough talk.","Whatever.",
            ],
        personality.Peace: [ "Maybe you should just give up now?",
            ],
        personality.Fellowship: [ "Let's keep this an honorable duel.",
            ],
        personality.Duty: [
            "My mission is to [objective_pp]."
        ],
        personality.Glory: [
            "Just watch me [objective_pp]!"
        ],
        LIKE: [
            "I regret that we're on opposite sides, but I will [objective_pp].",
        ],
        LOVE: [
            "I'll try not to kill you.",
        ]
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
    "[BAD_NEWS]": {
        # NPC is about to announce_character_state something bad.
        Default: ["Bad news...","Oh no..."
                  ],
        personality.Cheerful: ["Well that's not good...",
                               ],
        personality.Grim: ["That's just my luck.","Curses!"
                           ],
        personality.Easygoing: ["Guess what?",
                                ],
        personality.Passionate: ["Oh [expletive]...","This is terrible!"
                                 ],
        personality.Sociable: ["Bad news, everyone...",
                               ],
        personality.Shy: ["Bad news."
                          ],
    },

    "[bandit]": {
        Default: [
            "bandit","brigand","thief","ravager","pirate","criminal","crimepunk","raider","blackheart"
        ],
    },
    "[bandits]": {
        Default: [
            "bandits","brigands","thieves","ravagers","pirates","criminals","crimepunks","raiders","blackhearts"
        ],
    },

    "[BATTLE_GREETING]": {
        MET_BEFORE: ["[BATTLE_GREETING_AGAIN]", ],
        FIRST_TIME: ["[BATTLE_GREETING_FIRST]", ],
    },

    "[BATTLE_GREETING_AGAIN]": {
        Default: ["Hello again, [audience].", "Last time [MEM_LoseToPC], but this time I will [defeat_you]!",
                  ],
        personality.Cheerful: ["Back to play, [audience]?",
                               ],
        personality.Grim: ["You have arrived at your doom, [audience]!",
                           "Back for more punishment? Remember that [MEM_DefeatPC]."
                           ],
        personality.Sociable: ['We meet again, [audience].', "I suspected that we would meet again, [audience]."
                               ],
        personality.Shy: ['I did not expect to see you again.',
                          ],
        personality.Easygoing: ["Yo, [audience].", "Hi [audience]."
                                ],
        personality.Passionate: ['[audience]! I challenge you to battle!',
                                 ],
        LOVE: ["We have to stop meeting like this, [audience]!", "I wish I could say I'm glad to see you, [audience]."
               ],
        LIKE: ["You picked a bad time to visit, [audience].", "It's a shame that we are on opposite sides, [audience]."
               ],
        DISLIKE: ["This time I won't go easy on you, [audience].", "Not you again...",
                  ],
        HATE: ["I've been waiting for another chance to [defeat_you], [audience].",
               ],
        personality.Duty: [
            "Prepare for battle, [audience]!",
        ],
        personality.Fellowship: [
            "Our paths cross once again, [audience]!",
        ],
        personality.Glory: [
            "Have you improved your skills since last time, [audience]?",
        ],
        personality.Peace: [
            "Don't you ever tire of this ceaseless conflict, [audience]?",
        ],
        personality.Justice: [
            "This time I'll give you what you deserve, [audience]!"
        ],
    },

    "[BATTLE_GREETING_FIRST]": {
        Default: ["I am [speaker], and I will defeat you!",
                  ],
        personality.Cheerful: ["Hi there, I'm [speaker]!",
                               ],
        personality.Grim: ["My name's [speaker], and I will be your doom.",
                           ],
        personality.Sociable: ["Who are you and what are you doing here?! No matter.",
                               "Allow me to introduce myself: I am [speaker], and I will [defeat_you]!"
                               ],
        personality.Shy: ["You shouldn't be here.",
                          ],
        personality.Easygoing: ["I haven't seen you around before... and now I'm gonna have to [defeat_you].",
                                ],
        personality.Passionate: ["My name is [speaker], and I challenge you to combat!",
                                 ],
        LOVE: ["You look like a nice person, it's a shame I'm going to have to [defeat_you].",
               ],
        DISLIKE: ["Who the blazes are you?",
               ],
        personality.Glory: [
            "A new challenger approaches... My name's [speaker], and I will [defeat_you].",
        ],
        personality.Duty: [
            "Is it not customary to give one's own name before starting battle? I am [speaker], and you will be defeated!",
        ],
    },

    # The data block of this should contain "subject".
    "[BeCarefulOfSubject]": {
        Default: ["Be careful of {subject}",
                  ],
        personality.Cheerful: ["Maybe {subject} could really ruin your day",
                               ],
        personality.Grim: ["You should know that {subject} is dangerous","Keep your eyes on {subject}"
                           ],
        personality.Easygoing: ["You didn't hear this from me, but {subject} is scary",
                                ],
        personality.Passionate: ["Beware of {subject}",
                                 ],
        personality.Sociable: ["You should definitely be careful around {subject}",
                               ],
        personality.Shy: ["Don't trust {subject}",
                          ],
    },
    "[blockhead]": {
        # I looked up synonyms for "Jerk" and chose blockhead as the pattern name in honor of the Dougram mecha and
        # Devo song.
        Default: ["blockhead", "jerk", "arse", "smeghead", "bambo", "chump", "punk", "pongo", "ratfink", "simp",
                  "spug", "dolt", "ninny", "twit", "grexnix", "nonscrot", "nitwit", "jackass", "dipstick", "geekoid",
                  "numpty", "prat", "git", "twerp", "schmuck", "bozo", "boob", "galoot", "lummox", "putz", "dingbat",
                  "spud", "drongo", "asshat", "shazbucket", "grox",
                  ],
    },
    "[body_part]": {
        Default: ["eye","nose","face","throat","groin","duodenum","skull",
                  ],
    },

    "[BrowseWares]": {
        Default: ["Take a look around","Browse my wares"
                  ],
        personality.Cheerful: ["There are so many exciting things here", "Enjoy browsing our selection"
                               ],
        personality.Grim: ["Caveat emptor","Make sure you don't break anything while browsing"
                           ],
        personality.Easygoing: [
            "Take your time browsing", "Have a look around",
            ],
        personality.Passionate: ["Behold my unsurpassed selection", "My wares are glorious"
                                 ],
        personality.Sociable: ["Feel free to browse our excellent selection",
                               "I can tell you all about everything we carry",
                               "Look around all you want"
                               ],
        personality.Shy: ["Look around","Don't touch the merchandise unless you intend to buy"
                          ],
        LOVE: [
            "It's a pleasure to have you in my store",
            "Let me give you the VIP service"
        ],
        LIKE: [
            "Always a pleasure to do business with you"
        ],
        DISLIKE: [
            "Hurry up and find what you need","Browse the wares but don't try anything funny"
        ],
        HATE: [
            "Find what you need and get lost", "I'll be keeping my eye on you", "Don't try any funny business in my shop",
            "I'll sell you crap but don't expect me to be nice about it"
        ],
    },

    "[CAN_I_ASK_A_QUESTION]": {
        Default: ["Can I ask you a question?",
                  ],
        personality.Cheerful: ["Say [audience], seeing as the gang's all here right now, I have something to ask.",
                               ],
        personality.Grim: ["This is probably a bad time, but I have a question to ask you.",
                           ],
        personality.Easygoing: ["Mind if I ask you some stuff?",
                                ],
        personality.Passionate: ["[audience], I need to ask you something immediately.",
                                 ],
        personality.Sociable: ["I've been waiting to talk with you about something. I was wondering if you'd mind answering my questions.",
                               ],
        personality.Shy: ["[audience], I have something to ask.",
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
            "To be completely honest with you,","Word is that", "[as_far_as_I_know]"
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

    "[COMEBACKTOMORROW]": {
        Default: ["Come back and see me tomorrow.", "Come back later and we'll see then."
                  ],
        personality.Cheerful: ["Sounds like fun, but you'll have to come back tomorrow.",
                               ],
        personality.Grim: ["That is not going to happen today.",
                           ],
        personality.Easygoing: ["Sorry, you'll have to come back later."
                                ],
        personality.Passionate: ["Impossible, for now. Come see me tomorrow."
                                 ],
        personality.Sociable: ["I'll make a note on my dataslate that you're going to come back tomorrow.",
                               ],
        personality.Shy: ["Come back tomorrow.",
                          ],
    },

    "[COMEBACKTOMORROW_JOIN]": {
        Default: ["[COMEBACKTOMORROW]",
                  ],
        personality.Cheerful: ["Much as I enjoy going with you, I really can't today.",
                               ],
        personality.Grim: ["I am in no condition to go with you right now... but ask me again tomorrow, if I'm still alive.",
                           ],
        personality.Easygoing: ["Nope. Not right now. But come ask again tomorrow when I'm finished with this."
                                ],
        personality.Passionate: ["Afraid I wouldn't be much help to you in my current condition... come back later."
                                 ],
        personality.Sociable: ["Come back tomorrow and I'll be able to go with you then.",
                               ],
        personality.Shy: ["Not right now. Maybe later.",
                          ],
    },

    "[CRYPTIC_GREETING]": {
        Default: [
            "We live in dangerous times, but there is still a light in the darkness.",
            "We live in [adjective] times, but there is still a [noun] in the darkness.",
            "When you think with your [body_part] you will find the [noun].",
            "The only thing I know for certain is that I know [noun]."
        ],
        personality.Cheerful: [
            "Remember that the [noun] you give always returns in another form.",
            "Embrace the [adjective] [noun], free your [noun]."
        ],
        personality.Grim: [
            "Nothing in life is permanent, not even the [noun].",
            "When you doubt your power, you give power to your doubts.",
            "Don't hate the [noun], hate the [noun]."
            ],
        personality.Easygoing: [
            "Don't worry about the [adjective] [noun] so you can focus on the important things.",
            "Those who grasp the [noun] will lose their [noun]."
        ],
        personality.Passionate: [
            "Remember that if a job is worth doing, it's worth dying for.",
            "Always be [adjective], for the alternative is [adjective]."
        ],
        personality.Sociable: [
            "When you care for what is outside, what is inside cares for you.",
            "If everyone were [adjective], the [noun] would be [adjective]."
        ],
        personality.Shy: [
            "They say even Bernie Taupin had to build a city, once.",
            "Silence is a gift to the [noun]."
        ],
    },

    "[deadzone_residence]": {
        # Some place where people might be living in the dead zone.
        Default: [
            "abandoned factory","prezero ruin","low-rad zone","smuggler point","deserted fortress",
            "ancient fallout shelter","shantytown","ruined city","demolition zone","scavenger camp"
        ]
    },

    "[defeat_you]": {
        Default: ["defeat you", "beat you"
                  ],
        personality.Cheerful: ["win", "kick your arse"
                               ],
        personality.Grim: ["destroy you", "crush you", "cause you agony",
                           "watch you suffer", "kill you",
                           ],
        personality.Easygoing: ["fight you",
                                ],
        personality.Passionate: ["show you a true challenge", "annihilate you",
                                 "show you my true power",
                                 ],
        personality.Sociable: ["humiliate you",
                               ],
        personality.Shy: ["stop you",
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

    "[defeat_them]": {
        Default: ["defeat them", "beat them"
                  ],
        personality.Cheerful: ["kick their arses", "show them a good time"
                               ],
        personality.Grim: ["destroy them", "crush them", "annihilate them", "break them"
                           ],
        personality.Easygoing: ["fight them", "try to defeat them", "show them what we can do"
                                ],
        personality.Passionate: ["show them our full power", "put them in their place", "unleash the fires of destruction"
                                 ],
        personality.Sociable: ["humiliate them",
                               ],
        personality.Shy: ["stop them",
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

    "[direction]": {
        Default: ["north", "south", "west", "east"
                  ],
    },

    "[DISAGREE]": {
        Default: ["I don't agree with you."
                  ],
        personality.Cheerful: ["That's a funny thing to say."
                               ],
        personality.Grim: ["You are talking rubbish.",
                           ],
        personality.Easygoing: ["I don't think so."
                                ],
        personality.Passionate: ["Absolutely not!",
                                 ],
        personality.Sociable: ["I think you are mistaken.",
                               ],
        personality.Shy: ["I disagree.",
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

    "[ENEMIES_HAVE_NOT_DETECTED_US]": {
        # Enemies have been detected nearby. Generally used by a LM with Stealth when battle can be avoided.
        Default: ["[HOLD_ON] There are enemy mecha ahead, but they haven't detected us yet.",
                  "[HOLD_ON] There are [enemy_meks] nearby; they haven't seen us yet."
                  ],
        personality.Cheerful: ["[BAD_NEWS] There's a group of [enemy_meks] just around the turn. The good news is, they haven't spotted us yet.",
                               "[GOOD_NEWS] The [enemy_meks] that are lurking up ahead don't even know we're here."
                               ],
        personality.Grim: ["[LISTEN_UP] There are enemies ahead; one more step and they'll spot the rest of you.",
                           "[HOLD_ON] There's a lance of enemy mecha nearby, and you almost gave away our position."
                           ],
        personality.Easygoing: [
            "Those [enemy_meks] up ahead haven't figured out that we're here yet... it would be a piece of cake to sneak around them.",
            "I don't think the [enemy_meks] over there are paying attention. They don't even know we're here."
            ],
        personality.Passionate: ["They way ahead is choked with enemies. But, there is another way, if you follow me...",
                                 "[LISTEN_UP] Those [enemy_meks] must be asleep at the console. Follow me and I can sneak us all around them."
                                 ],
        personality.Sociable: [
            "[LISTEN_UP] If you don't want to fight those [enemy_meks], I can easily provide us with a way around them.",
            "Did you notice those [enemy_meks] over there? I've been keeping my eye on them, but I don't think they've noticed us yet."
            ],
        personality.Shy: ["[HOLD_ON] They haven't detected us. I can get us around them.",
                          "[GOOD_NEWS] We spotted them before they spotted us. I can get us around them."
                          ],
        personality.Peace: ["[GOOD_NEWS] The mecha up ahead haven't seen us yet; with a bit of trickery, we can find a safe path around them.",
                            ],
        personality.Justice: [
            "The [enemy_meks] over there haven't spotted us yet. It's your call whether we challenge them or just slip by.",
            ],
        personality.Glory: [
            "[LISTEN_UP] The [enemy_meks] over there? They don't even know we're here. We can do whatever we want.",
            ],
        personality.Fellowship: ["There's a group of mecha ahead; they appear to be hostile. They haven't spotted us yet.",
                                 ],
        personality.Duty: ["[HOLD_ON] The [enemy_meks] haven't seen us yet, so technically we could just sneak away.",
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

    "[expletive]": {
        Default: ["ashes","blazes","hell"
                  ],
    },

    "[FACTION_MUST_BE_PUNISHED]": {
        # data must contain "faction" element
        Default: ["{faction} must be punished!",
                  ],
        personality.Cheerful: ["Time to make life very unpleasant for {faction}.",
                               ],
        personality.Grim: ["{faction} must be destroyed.",
                           ],
        personality.Easygoing: ["I guess it's time to go fight {faction}.",
                                ],
        personality.Passionate: ["Now we unleash the hounds of war upon {faction}!",
                                 ],
        personality.Sociable: ["We must take immediate action against {faction}.",
                               ],
        personality.Shy: ["{faction} will pay.",
                          ],
        personality.Duty: ["There is no choice but to move against {faction}.",
                           ],
        personality.Glory: ["It's time to take down {faction}.",
                            ],
        personality.Justice: ["{faction} must be brought to justice.",
                              ],
        personality.Peace: ["To prevent further bloodshed, {faction} must be stopped.",
                            ],
        personality.Fellowship: ["It's time to join together against {faction}.",
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

    "[foaf]": {
        # Need a nameless NPC to send a message via a lancemate or other intermediary? Here you go!
        Default: ["an old friend", "my cousin", "a reliable source", "a person I know", "my contact"
                  ],
        tags.Military: ["an old pal from my unit", "my former seargent"
                               ],
        tags.Adventurer: ["my former lancemate", "a cavalier I know", "a lady I used to get missions from"
                           ],
        tags.Criminal: ["a fixer I used to work with", "an action merchant I know", "one who should not be named"
                                ],
        tags.Police: ["a cop I know", "one of my sources", "the police scanner"
                                 ],
        tags.Media: ["one of my contacts", "an important influencer"
                               ],
        tags.Politician: ["an official I know",
                          ],
        tags.Faithworker: ["the word of the heavens", "a monk"
                            ],
        personality.Sociable: [
            "my ex", "some guy I met last week"
        ],
        tags.Academic: [
            "a grad student I used to teach", "my research associate"
        ]
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

    "[GOOD]": {
        Default: ["That's good.", "Good.", "Great!"
                  ],
        personality.Cheerful: ["Glad to hear it.", "That makes me happy."
                               ],
        personality.Grim: ["Alright, then...", "Fine."
                           ],
        personality.Easygoing: ["Nice.", "Alright!"
                                ],
        personality.Passionate: ["Fantastic!","Amazing!","Wonderful!"
                                 ],
        personality.Sociable: ["That's good to hear.",
                               ],
        personality.Shy: ["Alright.", "Okay."
                          ],
    },

    "[GOOD_IDEA]": {
        Default: ["Good idea.","That's a good idea."
            ],
        personality.Cheerful: ["Great idea, [audience]!",
            ],
        personality.Grim: ["That's not a bad idea.",
            ],
        personality.Easygoing: [ "Yeah, that sounds alright.",
            ],
        personality.Passionate: ["That's a brilliant idea!",
            ],
        personality.Sociable: ["Good thinking, [audience].",
            ],
        personality.Shy: ["Interesting.",
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

    "[GOOD_NEWS]": {
        # NPC is about to announce_character_state something good.
        Default: ["Good news!",
                  ],
        personality.Cheerful: ["Great news!",
                               ],
        personality.Grim: ["I have something good to announce_character_state!",
                           ],
        personality.Easygoing: ["Guess what?",
                                ],
        personality.Passionate: ["This is fantastic!", "This is amazing!", "I have wonderful news!"
                                 ],
        personality.Sociable: ["Good news, everyone!",
                               ],
        personality.Shy: ["Listen up."
                          ],
    },

    "[GOODQUESTION]": {
        Default: ["That's a good question."
                  ],
        personality.Cheerful: ["That's a real puzzler.",
                               ],
        personality.Grim: ["How the [expletive] would I know that?!",
                           ],
        personality.Easygoing: ["I'm not sure I know how to answer that.",
                                ],
        personality.Passionate: ["It's a great mystery!",
                                 ],
        personality.Sociable: ["Now, I don't know anything more than what I've heard.",
                               ],
        personality.Shy: ["Good question.",
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
    "[HELLO_PLUS]": {
        Default: ["[HELLO]","[HELLO] [CURRENT_EVENTS]"]
    },
    "[HELLO]": {
        MET_BEFORE: ["[HELLO_AGAIN]",],
        FIRST_TIME: ["[HELLO_FIRST]",],
    },

    "[HELLO_AGAIN]": {
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
        LOVE: ["Welcome back, [audience]!", "I was hoping to see you today, [audience]."
               ],
        LIKE: ["Glad to see you again, [audience].",
               ],
        DISLIKE: ["What do you want, [audience]?",
                  ],
        HATE: ["Ugh, it's you.",
                  ],
        },

    "[HELLO_FIRST]": {
        Default: ["Hello, I'm [speaker].",
                  ],
        personality.Cheerful: ["Hi there, I'm [speaker]. It's a pleasure to meet you.",
                               ],
        personality.Grim: ["Yes, what do you want? The name's [speaker].",
                           ],
        personality.Sociable: ["Hello, I don't think we've been introduced. My name is [speaker].",
                               ],
        personality.Shy: ['Hey.',
                          ],
        personality.Easygoing: ["I don't believe we've met. My name's [speaker].",
                                ],
        personality.Passionate: ["I haven't seen you around before. I'm [speaker].",
                                 ],
        LOVE: ["Hello there! My name's [speaker], and I've been hoping for the chance to meet you.",
               ],
        LIKE: ["Hi, I'm [speaker]; it's nice to meet you.",
               ],
        HATE: ["Who the blazes are you?",
                  ],
        personality.Glory: [
            "You've got the look of a cavalier about you. My name's [speaker]."
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

    # The data block should include "subject"; if not a proper noun, subject should have "the".
    "[HELLO:INFO]": {
        Default: [ "Tell me about {subject}.",
            "What can you tell me about {subject}?"
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

    "[HELLO:LEAVEPARTY]": {
        Default: ["I need you to leave the [lance].",
                  ],
        personality.Cheerful: ["I'd like you to stay here for a while.",
                               ],
        personality.Grim: ["You're off the [lance], for now.",
                           ],
        personality.Easygoing: ["Sorry, but I need you to stay behind.",
                                ],
        personality.Passionate: ["Your next mission will be to stay here.",
                                 ],
        personality.Sociable: ["Your services won't be needed on our next mission.",
                               ],
        personality.Shy: ["The [lance] will continue without you.",
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

    "[HELLO:PROBLEM]": {
        Default: ["Is there something wrong?",
                  "You look like you have a problem."
                  ],
        personality.Cheerful: ["You don't look like a happy camper today.",
                               ],
        personality.Grim: ["Something is troubling you.",
                           ],
        personality.Easygoing: ["I get the feeling that there's something you want to talk about.",
                                ],
        personality.Passionate: ["If you have a problem, it's important to face it and blast it into submission!",
                                 ],
        personality.Sociable: ["Is there something you need to talk about?",
                               ],
        personality.Shy: ["What's the matter?",
                          ],
    },

    "[HELLO:QUERY]": {
        Default: ["Is there something you want to ask me?",
                  "You look like you have a question."
                  ],
        personality.Cheerful: ["You look like you're wondering something. Is it a riddle?",
                               ],
        personality.Grim: ["If there's something you want to ask, just spit it out already.",
                           ],
        personality.Easygoing: ["Do you have a question? You look like someone with a question.",
                                ],
        personality.Passionate: ["I can tell there's something on your mind. Go ahead and ask your question.",
                                 ],
        personality.Sociable: ["You've got a look like you want to ask me something.",
                               ],
        personality.Shy: ["If you have something to ask, just do it.",
                          ],
    },

    "[HELLOQUERY:QUERY]": {
        Default: ["What do you want to know?",
                  "Go ahead and ask.","[HELLO:QUERY]"
                  ],
        personality.Cheerful: ["Is it a question or a quiz? I love quizzes.",
                               ],
        personality.Grim: ["Go ahead and ask; I can't stop you.",
                           ],
        personality.Easygoing: ["Alright, you can ask me a question.",
                                ],
        personality.Passionate: ["Ask away.",
                                 ],
        personality.Sociable: ["Alright. What is it that you want to know?",
                               ],
        personality.Shy: ["Go ahead.",
                          ],
    },

    # The data block should hold the info to reveal as "reveal".
    "[HELLO:REVEAL]": {
        Default: ["You should know that {reveal}.",
                  "Did you know that {reveal}?"
                  ],
    },

    "[HELLO:SELFINTRO]": {
        Default: ["Could you tell me a bit about yourself?", "Why don't you tell me about yourself?"
                  ],
        personality.Cheerful: ["I'd be glad to learn more about you.",
                               ],
        personality.Grim: ["So what are you good for?",
                           ],
        personality.Easygoing: ["Wanna tell me a bit about yourself?",
                                ],
        personality.Passionate: ["I want to know more about you.",
                                 ],
        personality.Sociable: ["I'd really like to get to know you better.",
                               ],
        personality.Shy: ["Tell me about yourself.",
                          ],
    },

    "[HELLO:SOLUTION]": {
        Default: ["Do you have any bright ideas?",
                  "What do you suggest we do about it?"
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

    "[HELP_ME_BY_DOING_SOMETHING]": {
        # The NPC is going to ask the PC to do some kind of mission, quest, or housework.
        Default: ["You're a cavalier, right? I could use your help...", "[HELP_ME]"
                  ],
        personality.Cheerful: ["Am I glad to see you...",
                               ],
        personality.Grim: ["It seems as though all hope is lost.",
                           ],
        personality.Easygoing: ["Do you think you could help me with something?",
                                ],
        personality.Passionate: ["You look like the type of person who could solve this problem!",
                                 ],
        personality.Sociable: [
            "I've been searching for anybody who can help me...",
            ],
        personality.Shy: ["I hate to ask, but I need help.",
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

    "[Hey]": {
        # An interjection to get someone's attention.
        Default: ["Hey...", "[audience]..."
                  ],
        personality.Cheerful: ["Hey!",
                               ],
        personality.Grim: ["We need to talk;",
                           ],
        personality.Easygoing: ["Hey there..."
                                ],
        personality.Passionate: ["Heya!",
                                 ],
        personality.Sociable: [
            "Hey [audience],",
        ],
        personality.Shy: ["Psst, [audience]...",
                          ],
    },

    "[HOLD_ON]": {
        # Wait a minute...
        Default: ["Hold on...", "Wait a sec..."
                  ],
        personality.Cheerful: ["Yikes!","Jinkies!"
                               ],
        personality.Grim: ["Halt...",
                           ],
        personality.Easygoing: ["Just a sec...","Woah..."
                                ],
        personality.Passionate: ["Stop!",
                                 ],
        personality.Sociable: [
            "Everybody, hold on a second...",
            ],
        personality.Shy: ["Wait...",
                          ],
    },

    "[I_ALREADY_KNOW]": {
        Default: ["I already know.", "Yes, I already know that."
                  ],
        personality.Cheerful: ["Thanks for telling me, but I already knew that."
                               ],
        personality.Grim: ["Stop, I already know what you're going to say.",
                           ],
        personality.Easygoing: ["So you know about that too?"
                                ],
        personality.Passionate: ["Yes, I know, but what are we going to do about it?",
                                 ],
        personality.Sociable: ["Sorry to interrupt, but I already know all about this.",
                               ],
        personality.Shy: ["Yes.",
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

    "[I_DONT_KNOW]": {
        Default: ["I don't know.", "How should I know?"
                  ],
        personality.Cheerful: ["It's funny you say that, because I have no idea."
                               ],
        personality.Grim: ["You are speaking of things beyond my knowledge.",
                           ],
        personality.Easygoing: ["I really have no idea.","Did you really think I'd know that?"
                                ],
        personality.Passionate: ["I must confess my ignorance...",
                                 ],
        personality.Sociable: ["I'm sorry, but I really don't have any clue about this.",
                               ],
        personality.Shy: ["Good question.",
                          ],
    },

    "[I_FORGOT]": {
        # The PC has not even started their task yet. They may need a refresher.
        Default: ["I... what was I supposed to do, again?", "I forgot what I was supposed to do."
                  ],
        personality.Cheerful: ["I can say with full confidence that I don't remember what you're talking about."
                               ],
        personality.Grim: ["I have not failed in this task; I cannot even remember what it is.",
                           ],
        personality.Easygoing: ["Could you refresh my memory about that?",
                                ],
        personality.Passionate: ["I got so excited doing this that I forgot what I was supposed to be doing.",
                                 ],
        personality.Sociable: ["I forgot about it. Could you explain things one more time?",
                               ],
        personality.Shy: ["I forgot.",
                          ],
    },

    "[I_HAVE_DETECTED_ENEMIES]": {
        # Enemies have been detected nearby.
        Default: ["[HOLD_ON] I have detected enemy mecha just ahead of us.",
                  "[HOLD_ON] My sensors show [enemy_meks] nearby."
                  ],
        personality.Cheerful: ["I hate to be the bearer of bad news, but there are [enemy_meks] nearby.",
                               "[GOOD_NEWS] We just avoided stepping right into an ambush."
                               ],
        personality.Grim: ["[HOLD_ON] The way ahead is blocked by [enemy_meks].",
                           "My sensors indicate a significant force of [enemy_meks] nearby."
                           ],
        personality.Easygoing: ["I thought you'd all like to know that we're heading straight towards some [enemy_meks].",
                                "Is anybody else picking up a big group of enemy meks ahead? Because I am picking up a big group of enemy meks ahead."
                                ],
        personality.Passionate: ["[GOOD_NEWS] I have detected our enemies, and they are nearby!",
                                 "[HOLD_ON] According to my sensors, we are surrounded by enemy forces!"
                                 ],
        personality.Sociable: ["[HOLD_ON] We're not alone out here; I'm picking up a group of enemy mecha on my scanner.",
                               "[LISTEN_UP] I just detected some [enemy_meks], and they're nearby."
                               ],
        personality.Shy: ["[HOLD_ON] I'm reading enemy forces ahead.",
                          "There are [enemy_meks] nearby."
                          ],
        personality.Peace: ["[BAD_NEWS] My scanner has picked up some hostile mecha closing in on us.",
                        ],
        personality.Justice: ["[HOLD_ON] I just picked up some mecha ahead. I can't be sure what they want, but it probably isn't good.",
                            ],
        personality.Glory: ["[GOOD_NEWS] If you were looking forward to getting in a fight today, I just detected [enemy_meks].",
                            ],
        personality.Fellowship: ["[HOLD_ON] There's someone else out there; hostile mecha from the look of things.",
                            ],
        personality.Duty: ["[LISTEN_UP] My scanners just picked up some [enemy_meks] approaching our position.",
                            ],
    },

    "[I_MUST_CONSIDER_MY_NEXT_STEP]": {
        Default: ["I must consider what I'm going to do next...",
                  ],
        personality.Cheerful: ["I don't know what I'm going to do next, but I know I'll think of something.",
                               ],
        personality.Grim: ["For now, all I can do is to contemplate my next move.",
                           ],
        personality.Easygoing: ["I'm going to need a bit of time to process all this.",
                                ],
        personality.Passionate: ["What will I do next? I can't say, not yet...",
                                 ],
        personality.Sociable: ["I think I'm going to have to talk this through with some people.",
                               ],
        personality.Shy: ["I need time to think.",
                          ],
        personality.Peace: ["I have to think deeply about how to proceed while minimizing harm.",
                        ],
        personality.Justice: ["I must think about how justice can be achieved.",
                            ],
        personality.Glory: ["It's clear that I'm going to need a new master plan.",
                            ],
        personality.Fellowship: ["After all this, I need to think about where I fit in.",
                            ],
        personality.Duty: ["I'm going to have to think about how best to fulfil my duty.",
                            ],
    },

    "[INFO:INFO]": {
        # The data block should include "subject"
        Default: ["What was that about {subject}?",
                  ],
        personality.Cheerful: ["I'd like to hear about {subject}.",
                               ],
        personality.Grim: ["What does that have to do with {subject}?",
                           ],
        personality.Easygoing: ["Wait, what about {subject}?",
                                ],
        personality.Passionate: ["Tell me about {subject}.",
                                 ],
        personality.Sociable: ["What more can you tell me about {subject}?",
                               ],
        personality.Shy: ["And {subject}?",
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

    "[INTERESTING_NEWS]": {
        # Character has something interesting to reveal.
        Default: ["Very interesting.",
                  "This is interesting."
                  ],
        personality.Cheerful: [
            "Oh, cool!",
        ],
        personality.Grim: ["Fascinating.",
                           ],
        personality.Easygoing: [
            "Neat.",
        ],
        personality.Passionate: [
            "Amazing!",
        ],
        personality.Sociable: [
            "I have something quite interesting to tell you.",
        ],
        personality.Shy: ["Interesting.",
                          ],
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

    "[I_WANT_YOU_TO_INVESTIGATE]": {
        Default: ["I want you to investigate this matter.","I'd appreciate if you could go see what's going on."
                  ],
        personality.Cheerful: ["It'd be super if you could go find out what's going on.",
                               ],
        personality.Grim: ["I would like you to delve this mystery, if you dare.",
                           ],
        personality.Easygoing: ["You should go investigate, see if you can find out anything."
                                ],
        personality.Passionate: ["You may be the only person who can get to the bottom of this!"
                                 ],
        personality.Sociable: ["I would personally appreciate it if you could go see what you can find out.",
                               ],
        personality.Shy: ["I want you to investigate.",
                          ],
    },

    "[IWILLSEEWHATICANDO]": {
        # A vague promise of help for a problem of some kind.
        Default: ["I'll see what I can do about that.", "Maybe I could do something about that."
                  ],
        personality.Cheerful: ["I will do my best to fix this!",
                               ],
        personality.Grim: ["I don't know what I can do to help, but I'll try anyways.",
                           ],
        personality.Easygoing: ["Gimme a while to see what I can do about that."
                                ],
        personality.Passionate: ["I swear to you, this problem will be solved!"
                                 ],
        personality.Sociable: ["I'll ask around and see if there's anything I can do about that.",
                               ],
        personality.Shy: ["I'll see what I can do.",
                          ],
    },

    "[I_WOULD_APPRECIATE_IT]": {
        Default: ["I'd really appreciate it.", "Thanks for your help."
                  ],
        personality.Cheerful: ["If you do this, I will be so happy!",
                               ],
        personality.Grim: ["I would owe you a debt.",
                           ],
        personality.Easygoing: ["It'd be great if you could do this."
                                ],
        personality.Passionate: ["I will be forever in your debt!"
                                 ],
        personality.Sociable: ["I would personally appreciate your help in this matter.",
                               ],
        personality.Shy: ["Thanks.",
                          ],
    },

    "[IWOULDLOVETO]": {
        Default: ["I'd love to.", "Sounds good to me."
                  ],
        personality.Cheerful: ["That sounds like fun!",
                               ],
        personality.Grim: ["I wouldn't miss it for the world.",
                           ],
        personality.Easygoing: ["Sure, why not? I have nothing better to do."
                                ],
        personality.Passionate: ["Yes, I would love to do that!","I have been waiting for this!"
                                 ],
        personality.Sociable: ["Alright, that sounds like a good idea.",
                               ],
        personality.Shy: ["Okay.",
                          ],
    },

    "[IWillSendMissionDetails]": {
        Default: [ "I'll send you the mission details",
            ],
        personality.Cheerful: ["I just sent all the mission details to your navcomp",
            ],
        personality.Grim: ["Pay close attention to the mission data I'm sending",
            ],
        personality.Easygoing: [ "Everything you need to know should already be uploaded to your mek",
            ],
        personality.Passionate: ["All the info you need will be sent to your navcomp",
            ],
        personality.Sociable: ["I've transmitted all the relevant dats to your mek's navcomp",
            ],
        personality.Shy: ["Mission details will be sent to your mek",
            ],

        },

    "[JOIN]": {
        Default: ["Alright, I'll join your [lance]. [LETSGO]",
                  "Join your [lance]? [ICANDOTHAT]"
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

    "[lance]": {
        Default: [
            "lance", "mecha team"
        ],
        personality.Cheerful: [
            "party",
        ],
        personality.Easygoing: [
            "group of meks",
        ],
        tags.Military: [
            "mecha squad", "squad"
        ],
    },

    "[LEAVEPARTY]": {
        Default: ["I'll be around here if you need me again. [GOODBYE]", "[OK] Come back here if you need my services again.",
                  ],
        personality.Cheerful: ["Let me know when you want me to join your lance again. [GOODBYE]",
                               ],
        personality.Grim: ["[THATSUCKS] [GOODBYE]",
                           ],
        personality.Easygoing: ["[GOODLUCK] Come and see me again some time.",
                                "Alright, I could use a bit of a vacation anyhow. [GOODBYE]"
                                ],
        personality.Passionate: ["Understood. [GOODLUCK]",
                                 "It was an honor to fight at your side. [GOODBYE]"
                                 ],
        personality.Sociable: ["[OK] I'll see you later, I guess.",
                               ],
        personality.Shy: ["[OK] [GOODBYE]",
                          ],
        DISLIKE: ["[IWOULDLOVETO] [GOODBYE]",
                  ],
        LIKE: ["Make sure you come back sometime to let me know how you're doing. [GOODBYE]",
               ]
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

    "[LETS_CONTINUE]": {
        Default: ["Let's get going.",
                  ],
        personality.Cheerful: ["I can't wait for our next adventure!",
                               ],
        personality.Grim: ["Let's go wreck some stuff.", "Onward to our next disaster!"
                           ],
        personality.Easygoing: ["Should we get back to work, now? Maybe in a few minutes...",
                                ],
        personality.Passionate: ["Let's get back into the breach!",
                                 ],
        personality.Sociable: ["Let's journey onward.",
                               ],
        personality.Shy: ["Let's get back to work.",
                          ],
        DISLIKE: ["Nothing to do now but keep on going...",
                  ],
        LIKE: ["Wherever we go next, I'm glad to be going with you.",
               ]
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

    "[LETS_START_MECHA_MISSION]": {
        Default: ["I'm ready to start the mission.",
                  ],
        personality.Cheerful: ["I'm all ready to start.",
                               ],
        personality.Grim: ["We must start this mission immediately.",
                           "Time is wasting; let's suit up and go."
                           ],
        personality.Easygoing: ["Yeah, let's go.",
                                "Alright, we might as well start the mission."
                                ],
        personality.Passionate: ["Once more unto the breach!", "Let's get ready to kick some arse!"
                                 ],
        personality.Sociable: ["Let's get this mission started.",
                               ],
        personality.Shy: ["Let's begin.",
                          ],
        DISLIKE: ["Might as well get this over with.",
                  ],
    },

    "[LISTEN_UP]": {
        # The character is about to announce_character_state something important.
        Default: ["Listen up;",
                  ],
        personality.Cheerful: ["Listen up!",
                               ],
        personality.Grim: ["Hear me...", "I am only going to say this once..."
                           ],
        personality.Easygoing: ["Hey...",
                                ],
        personality.Passionate: ["Listen to my words!",
                                 ],
        personality.Sociable: ["Hey everyone, listen up...",
                               ],
        personality.Shy: ["Listen;",
                          ],
    },

    "[LONGTIMENOSEE]": {
        Default: ["Hello [audience], long time no see.",
            "Long time no see, [audience].",],
        personality.Sociable: ["Well there's a face I haven't seen in a while.",
            ],
        personality.Shy: ["Long time no see.",
            ],
        },

    "[LOOK_AT_THIS]": {
        Default: ["Look at this...", "[audience], look at this..."
                  ],
        personality.Cheerful: ["Hey, that's interesting...",
                               ],
        personality.Grim: ["Would you look at that...",
                           ],
        personality.Easygoing: ["Would you get a load of this?",
                                ],
        personality.Passionate: ["Look!", "[audience], look!"
                                 ],
        personality.Sociable: ["Everybody, come here, I found something...",
                               ],
        personality.Shy: ["Look at this.",
                          ],
    },

    "[Luna]": {
        Default: ["Luna", ],
        personality.GreenZone: ["the moon","the moon",],
        personality.DeadZone: ["the moon","the moon","the moon",],
    },

    "[MAYBE_YOU_COULD_HELP]": {
        Default: ["Maybe you could help me with this."
                  ],
        personality.Cheerful: ["It's lucky that you're here, because you're just the sort who could help me with this.",
                               ],
        personality.Grim: ["I had almost given up hope, but maybe you could help me.",
                           ],
        personality.Easygoing: ["Say, I don't suppose you'd be willing to help me with something?",
                                ],
        personality.Passionate: ["You must help me [audience], you're my only hope!",
                                 ],
        personality.Sociable: ["Working together, we might just be able to pull this off.",
                               ],
        personality.Shy: ["Please help me.",
                          ],
    },

    "[mecha]": {
        Default: ["mecha", "mek", "giant robot", "ride"
                  ],
    },

    "[MechaMissionVsEnemyFaction]": {
        # The data block should include enemy_faction
        Default: ["You will be fighting {enemy_faction}"
                  ],
        personality.Cheerful: ["Your targets this time around are from {enemy_faction}",
                               ],
        personality.Grim: ["You must destroy all [enemy_meks] from {enemy_faction}"
                           ],
        personality.Easygoing: ["There are some meks from {enemy_faction} that you need to fight"
                                ],
        personality.Passionate: ["The pilots of {enemy_faction} must pay for crossing us",
                                 "We need to show {enemy_faction} that they can't mess with us"
                                 ],
        personality.Sociable: ["During this mission you will be fighting against a [lance] sent by {enemy_faction}",
                               ],
        personality.Shy: ["This mission is against {enemy_faction}",
                          "A [lance] from {enemy_faction} has gotten too close for comfort"
                          ],
        personality.Justice: [
            "{enemy_faction} must be brought to justice",
            "A [lance] from {enemy_faction} has violated our treaties"
        ],
        personality.Duty: [
            "Mecha from {enemy_faction} have crossed the line into our territory",
            "Our enemies {enemy_faction} have been sighted nearby"
        ],
        personality.Peace: [
            "Our people are being endangered by {enemy_faction}"
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

    "[NO_PROBLEM_FOR_TWO_OF_US]": {
        Default: ["This will be no problem for the two of us."
                  ],
        personality.Cheerful: ["Easy peasy atomic squeegie!",
                               ],
        personality.Grim: ["All will crumble beneath our combined power!",
                           ],
        personality.Easygoing: ["Between the two of us, I'd say we can do it.",
                                ],
        personality.Passionate: ["Together, there's nothing that can stop us!",
                                 ],
        personality.Sociable: ["With you by my side, this will be a piece of cake.",
                               ],
        personality.Shy: ["No problem.",
                          ],
    },

    "[NOTHANKYOU]": {
        # May be coupled with [YESPLEASE]
        Default: ["No thank you.", "No thanks."
                  ],
        personality.Cheerful: ["No, but thanks anyway!",
                               ],
        personality.Grim: ["Not on your life.",
                           ],
        personality.Easygoing: ["Nah.",
                                ],
        personality.Passionate: ["No, absolutely not!",
                                 ],
        personality.Sociable: ["I'm afraid I have to say no.",
                               ],
        personality.Shy: ["No.",
                          ],
    },

    "[NO_TO_COP]": {
        # The speaker is declining to speak to a police officer or other authority figure.
        Default: ["I don't talk to cops.",
                  ],
        personality.Cheerful: ["No way; snitches get stitches.",
                               ],
        personality.Grim: ["Do you know what happened to the last guy who talked to the cops?",
                           ],
        personality.Easygoing: ["I'd really rather not incriminate myself that way.",
                                ],
        personality.Passionate: ["Do I look like a narc to you?!",
                                 ],
        personality.Sociable: ["I'm not speaking.",
                               ],
        personality.Shy: ["I'd rather not.",
                          ],
        personality.Justice: [
            "I'm gonna need my lawyer present before I say anything.",
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

    "[OK]": {
        # A not necessarily enthusiastic agreement or assent...
        Default: ["Okay.","Alright."
                  ],
        personality.Cheerful: ["Okay!",
                               ],
        personality.Grim: ["Whatever...",
                           ],
        personality.Easygoing: ["Sure, why not?", "That's fine by me."
                                ],
        personality.Passionate: ["I, [speaker], assent to this.",
                                 ],
        personality.Sociable: ["If that's what you want.",
                               ],
        personality.Shy: ["OK.",
                          ],
        DISLIKE: ["I guess...",
                  ],
        LIKE: ["As you wish.",
               ]
    },

    "[OPENSHOP]": {
        # The data block should include shop_name, wares (plural or uncountable)
        Default: ["[BrowseWares]; you should find everything you need.",
                  "[BrowseWares]. Remember, {shop_name} is your source for {wares}.",
                  "At {shop_name}, you'll find the {wares} you need.",
                  "[BrowseWares]. There's never a bad time to upgrade your {wares}.",
                  ],
        personality.Cheerful: ["[BrowseWares]; enjoy your shopping experience.",
                               "I hope you enjoy shopping at {shop_name}.",
                               "It's fun getting to play with all these {wares}. I hope you find something you like.",
                               "Don't you enjoy checking out {wares}?",
                               "[BrowseWares]. For this week only, we're offering complimentary gum with every purchase.",
                               "I just know you'll find something you like!"
                               ],
        personality.Grim: ["Take your time. Remember, you get what you pay for.",
                           "[BrowseWares]. Do not be frightened by all the {wares}.",
                           "Remember, {shop_name} has no warranties, expressed or implied.",
                           "[BrowseWares]. At {shop_name}, the lowest price is a happy accident.",
                           "At {shop_name}, we have the {wares} if you have the credits.",
                           "[BrowseWares]. Sometimes I get kind of sick of {wares} but a job's a job.",
                           "I have all the {wares} you could ever need. Just {wares}.",
                           "Having the right {wares} can mean the difference between life and death."
                           ],
        personality.Easygoing: ["If you can't find what you're looking for today, remember that it might be here tomorrow.",
                                "[BrowseWares]. Remember, {shop_name} is chock full of {wares}.",
                                "Do you want {wares}? Because {shop_name} has got a ton of {wares}."
                                ],
        personality.Passionate: ["I think you'll agree this shop has the best selection you've ever seen!",
                                 "Whatever kind of {wares} you're looking for, you can bet that {shop_name} has it!",
                                 "[BrowseWares]. If you love {wares} as much as I do, you will not be disappointed!",
                                 "The best thing in life is {wares}! That's why {shop_name} was built.",
                                 "Remember, you can never spend too much money on {wares}. Never."
                                 ],
        personality.Sociable: ["[BrowseWares], and let me know if you need any help.",
                               "At {shop_name} we have all the {wares} you could ask for.",
                               "I know quite a bit about the {wares} here, so feel free to ask if you have any questions.",
                               "See anything that interests you? At {shop_name} we stock a great variety of {wares}.",
                               "Thanks to my distributor connections, you'll find that the selection of {wares} at {shop_name} is second to none."
                               ],
        personality.Shy: ["Prices should be marked on everything.",
                          "Look at the {wares}; I'll be here when you're ready to check out.",
                          "These are the {wares}. Let me know when you want to pay.",
                          "[BrowseWares]. I'll be here if you need me.",
                          "I don't know what you need, but if it's {wares}, {shop_name} can fix you up.",
                          "Make your selection, please.",
                          ],
        LOVE: [
            "The {wares} of {shop_name} are yours to peruse. Shall I get you a coffee while you're browsing?",
            "[BrowseWares]; {shop_name} welcomes you to examine our {wares}."
        ],
        LIKE: [
            "[BrowseWares]; if you need anything at all then I'm eager to help."
        ],
        DISLIKE: [
            "[BrowseWares]; you can figure out how everything works by yourself.",
            "We sell {wares}. The sooner you buy what you need and get out of here, the happier we'll both be."
        ],
        HATE: [
            "[BrowseWares]; let's just get this over with.",
            "Don't try any funny business in my shop",
            "I'll sell you crap but don't expect me to be nice about it"
        ],
    },

    "[person]": {
        Default: [
            "person", "man", "woman",
        ],
        personality.Grim: [
            "[blockhead]"
        ]
    },

    "[PLEASURE_DOING_BUSINESS]": {
        Default: ["It's been a pleasure doing business with you.",
                  ],
        personality.Cheerful: ["Fantastic! I'm so happy we came to this agreement.",
                               ],
        personality.Grim: ["You will not regret this, I promise."
                           ],
        personality.Easygoing: ["Alright. So I guess we're finished here, now? Great."
                                ],
        personality.Passionate: ["The deal is signed, may fate strike down any who oppose it!",
                                 ],
        personality.Sociable: ["May I just say what a pleasure it is to come to an agreement with a true professional like you.",
                               ],
        personality.Shy: ["So it's agreed.",
                          ],
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

    "[QOL_COMMUNITY_UP]": {
        Default: ["People in [metroscene] can always depend on their community.",
                  ],
        personality.Cheerful: ["We're all friends in [metroscene].",
                               ],
        personality.Grim: ["The community in [metroscene] always pulls together when there's a problem.",
                           ],
        personality.Easygoing: ["This may not be the fanciest place, but we've got a decent art scene."
                                ],
        personality.Passionate: ["I'd punch a morlock for any one of my neighbors.",
                                 ],
        personality.Sociable: ["The community is the best part of [metroscene].",
                               ],
        personality.Shy: ["The people of [metroscene] are an interesting bunch.",
                          ],
    },

    "[QOL_COMMUNITY_DOWN]": {
        Default: ["It's every [person] for themself in [metroscene].",
                  ],
        personality.Cheerful: ["Remember: not everyone in [metroscene] is your friend.",
                               ],
        personality.Grim: [
            "This town has all the personality and sparkle of week-old roadkill.",
            ],
        personality.Easygoing: ["This is a boring and unfriendly town, but at least the rats are small."
                                ],
        personality.Passionate: ["Around here, the only person you can depend on is yourself.",
                                 ],
        personality.Sociable: [
            "This isn't the kind of place where you make friends. This isn't even the kind of place you go by choice.",
                               ],
        personality.Shy: ["Nobody talks to their neighbors anymore. I like that.",
                          ],
    },

    "[QOL_DEFENSE_UP]": {
        Default: ["The [metroscene] Guard can take on all threats.",
                  ],
        personality.Cheerful: ["Our defense force has prettier mecha colors than any other.",
                               ],
        personality.Grim: ["In the event of war, everyone here knows their duty.",
                           ],
        personality.Easygoing: ["I never worry about war coming to [metroscene]."
                                ],
        personality.Passionate: ["If anyone ever tries invading here, we'll show them the gates of hell!",
                                 ],
        personality.Sociable: ["I've heard that our defense force is the best in the region.",
                               ],
        personality.Shy: ["[metroscene]'s defenses are quite good.",
                          ],
    },

    "[QOL_DEFENSE_DOWN]": {
        Default: ["The [metroscene] Guard is unable to protect us.",
                  ],
        personality.Cheerful: ["I heard they were going to upgrade the town militia by giving everyone a cricket bat.",
                               ],
        personality.Grim: [
            "If [metroscene] ever gets invaded, we are basically doomed.",
        ],
        personality.Easygoing: ["The local militia isn't bad, it's just overstreched and underfunded."
                                ],
        personality.Passionate: ["It's shameful how weak our defense force is!",
                                 ],
        personality.Sociable: ["We really need a larger defense force, but have to make do with what we've got.",
                               ],
        personality.Shy: ["Our defense force sucks.",
                          ],
    },

    "[QOL_HEALTH_UP]": {
        Default: ["Health care in [metroscene] is pretty good.",
                  ],
        personality.Cheerful: ["Every day I'm thankful for my good health.",
                               ],
        personality.Grim: ["At least we have our health in [metroscene].",
                           ],
        personality.Easygoing: ["Do you work out? What kind of program do you use?"
                                ],
        personality.Passionate: ["Are you ready to seize the day? I'm gonna live while I'm alive!",
                                 ],
        personality.Sociable: ["Remember that mental stimulation is as important as physical fitness for longevity.",
                               ],
        personality.Shy: ["Good health to you.",
                          ],
    },

    "[QOL_HEALTH_DOWN]": {
        Default: ["People in [metroscene] don't expect to see old age.",
                  ],
        personality.Cheerful: ["It's hard to keep a smile on when everyone around looks like they're dying.",
                               ],
        personality.Grim: [
            "If you don't have your health, you really have nothing.",
            ],
        personality.Easygoing: ["I don't worry about old age... don't expect to see it, honestly."
                                ],
        personality.Passionate: ["I always wanted to live fast and die young, but not this young.",
                                 ],
        personality.Sociable: ["I know too many people who were taken from us too soon...",
                               ],
        personality.Shy: ["Death comes quickly around here.",
                          ],
    },

    "[QOL_PROSPERITY_UP]": {
        Default: ["The economy has been doing well lately.",
                  ],
        personality.Cheerful: ["This is a good time to go shopping.",
                               ],
        personality.Grim: ["For a change of pace, I'm not even broke this month.",
                           ],
        personality.Easygoing: ["Everyone seems pretty well off these days."
                                ],
        personality.Passionate: ["I'm saving my money to buy something I don't even need!",
                                 ],
        personality.Sociable: ["Everybody is wearing the latest fashions... maybe I should update my look?",
                               ],
        personality.Shy: ["I can't complain about money.",
                          ],
    },

    "[QOL_PROSPERITY_DOWN]": {
        Default: ["The economy has been bad lately.",
                  ],
        personality.Cheerful: ["I'd like to go shopping, but who can afford it?",
                               ],
        personality.Grim: ["They say we need to tighten our belts, but how can you do that when you're already starving?",
                           ],
        personality.Easygoing: ["Seems like everyone is either broke or unemployed these days."
                                ],
        personality.Passionate: ["No money, no hope. Maybe I should move somewhere else.",
                                 ],
        personality.Sociable: ["So many of my friends are out of work...",
                               ],
        personality.Shy: ["My only money troubles are that I don't have any.",
                          ],
        personality.Glory: [
            "[metroscene] is way too shabby for my taste."
        ]
    },

    "[QOL_STABILITY_UP]": {
        Default: ["[metroscene] is a relatively safe place to live.",
                  ],
        personality.Cheerful: ["Our town is clean and safe, just the way I like it.",
                               ],
        personality.Grim: ["Not a lot of murders or robberies happen here, or anything exciting like that.",
                           ],
        personality.Easygoing: ["Exciting things always seem to happen somewhere else."
                                ],
        personality.Passionate: ["Life in [metroscene] is a bit boring, but in a good way.",
                                 ],
        personality.Sociable: ["You can feel safe and secure while you're in [metroscene].",
                               ],
        personality.Shy: ["[metroscene] has a low crime rate.",
                          ],
    },

    "[QOL_STABILITY_DOWN]": {
        Default: ["[metroscene] has a lot of crime.",
                  ],
        personality.Cheerful: ["I've been in [metroscene] for a while and nobody has murdered me yet, so...",
                               ],
        personality.Grim: [
            "The muggers aren't that bad; it's the organleggers you really need to watch out for.",
            ],
        personality.Easygoing: ["Some folks out here would steal your arse if it wasn't firmly attached."
                                ],
        personality.Passionate: ["This place is a hive of scum and villainy.",
                                 ],
        personality.Sociable: ["I don't like all the petty crime that happens in [metroscene]. Or the felonies.",
                               ],
        personality.Shy: ["This is a dangerous neighborhood.",
                          ],
    },

    "[SELFINTRO:GOODBYE]": {
        Default: ["[GOODBYE]",
                  ],
        personality.Cheerful: ["Thanks for telling me about yourself.",
                               ],
        personality.Grim: ["I don't think I need your services right now.",
                           ],
        personality.Easygoing: ["Awesome. [GOODBYE]",
                                ],
        personality.Passionate: ["Keep striving to be the best!",
                                 ],
        personality.Sociable: ["I'll let you know if I ever need a lancemate.",
                               ],
        personality.Shy: ["Okay. [GOODBYE]",
                          ],
    },

    "[SELFINTRO:JOIN]": {
        Default: ["Sounds like you'd be a good addition to my lance.",
                  "How about joining my lance?"
                  ],
        personality.Cheerful: ["Sounds like you'd be lots of fun to go on an adventure with.",
                               ],
        personality.Grim: ["It will be dangerous, but I could use your skills.",
                           ],
        personality.Easygoing: ["How would you like to join my lance?",
                                ],
        personality.Passionate: ["You are exactly the type of lancemate I've been seeking.",
                                 ],
        personality.Sociable: ["Based on what you just said, I'd like to offer you a position in my lance.",
                               ],
        personality.Shy: ["Your skills would be valuable in my lance.",
                          ],

    },

    "[SELFINTRO_MECHA]": {
        # data should include "mecha"
        Default: ["My mecha is a {mecha}.", "I pilot a {mecha}."
                  ],
        personality.Cheerful: ["My fav mecha is the {mecha}.",
                               ],
        personality.Grim: ["I ride a {mecha} into battle.",
                           ],
        personality.Easygoing: ["I've got a {mecha}.",
                                ],
        personality.Passionate: ["The {mecha} is my warhorse!",
                                 ],
        personality.Sociable: [
            "I usually pilot a {mecha}.",
        ],
        personality.Shy: ["I've got a {mecha}.",
                          ],
    },

    "[SELFINTRO_RANK_GREEN]": {
        Default: ["I don't have a lot of experience, yet...",
                  "I'm a green pilot."
                  ],
        personality.Cheerful: ["I don't have much adventuring experience, but I'm looking forward to learning!",
                               ],
        personality.Grim: ["I'll level with you- I barely know how to pilot a mecha.",
                           ],
        personality.Easygoing: ["Honestly, I'm a complete noobie.",
                                ],
        personality.Passionate: ["I may lack experience, but I have the warrior spirit!",
                                 ],
        personality.Sociable: ["You probably haven't heard about me before, because I don't have a lot of experience...",
                               ],
        personality.Shy: ["I am a new pilot.",
                          ],

    },

    "[SELFINTRO_RANK_REGULAR]": {
        Default: ["I have a bit of experience as a cavalier.",
                  ],
        personality.Cheerful: ["Happy to say that I have some experience as a cavalier.",
                               ],
        personality.Grim: ["I've been a cavalier for a while now; haven't died yet.",
                           ],
        personality.Easygoing: ["This isn't my first turn at the giant robot rodeo.",
                                "I'd describe my skills as moderately average."
                                ],
        personality.Passionate: ["Being a cavalier is my dream come true!",
                                 ],
        personality.Sociable: [
            "So far I've been able to hold my own as a cavalier.",
            ],
        personality.Shy: ["I've been doing this for some time.",
                          ],

    },

    "[SELFINTRO_RANK_VETERAN]": {
        Default: ["I am a veteran pilot.",
                  ],
        personality.Cheerful: ["I'm lucky enough to have been doing this a long time.",
                               ],
        personality.Grim: ["Most of the other cavaliers I started with are retired or dead by now.",
                           ],
        personality.Easygoing: ["I guess you could say I'm a pretty good pilot... not elite or anything, but good.",
                                ],
        personality.Passionate: ["I've spent years developing my combat skills!",
                                 ],
        personality.Sociable: [
            "They say I'm a veteran rank pilot.",
        ],
        personality.Shy: ["I'm a veteran.",
                          ],
    },

    "[SELFINTRO_RANK_ELITE]": {
        Default: ["I am an elite pilot.",
                  ],
        personality.Cheerful: ["Not to brag, but I'm ranked at elite level.",
                               ],
        personality.Grim: ["My skills are at elite level, which is how I've managed to live so long.",
                           ],
        personality.Easygoing: ["I'm quite a good pilot. Not quite ace level, but close.",
                                ],
        personality.Passionate: ["My combat skills are at the elite level, and someday I plan to be an ace!",
                                 ],
        personality.Sociable: [
            "You may have heard that I'm an elite pilot.",
        ],
        personality.Shy: ['My rank is "elite".',
                          ],
    },

    "[SELFINTRO_RANK_ACE]": {
        Default: ["I am an ace pilot.",
                  ],
        personality.Cheerful: ["You're in luck, because I happen to be an ace pilot.",
                               ],
        personality.Grim: ["I am death incarnate.",
                           ],
        personality.Easygoing: ["You could say that I'm pretty good at piloting.",
                                ],
        personality.Passionate: ["Through practice and conflict I have perfected my skills!",
                                 ],
        personality.Sociable: [
            "You're talking to an ace pilot.",
        ],
        personality.Shy: ["I'm an ace.",
                          ],
    },

    "[SELFINTRO_SKILL]": {
        # data should include "skill"
        Default: ["I've studied {skill}.", "My specialty is {skill}.", "I know {skill}."
                  ],
        personality.Cheerful: ["My favorite subject is {skill}.",
                               ],
        personality.Easygoing: ["I'm sort of good at {skill}.",
                                ],
        personality.Passionate: ["I'm great at {skill}.",
                                 ],
        personality.Sociable: [
            "I'm certified in {skill}.",
        ],
    },

    "[SELFINTRO_SKILLS]": {
        # data should include "skills"
        Default: ["I've studied {skills}.", "My skills include {skills}.", "My skills are {skills}."
                  ],
        personality.Cheerful: ["I love {skills}.",
                               ],
        personality.Grim: ["In addition to combat, I know {skills}.",
                           ],
        personality.Easygoing: ["Plus, I know {skills}.",
                                ],
        personality.Passionate: ["I'm an expert at {skills}.",
                                 ],
        personality.Sociable: [
            "My qualifications include {skills}.",
        ],
        personality.Shy: ["I know {skills}.",
                          ],
    },

    "[shop_slogan]": {
        Default: [
            "[shop_feature] is [shop_descriptive_phrase]",
            "[shop_features] are [shop_descriptive_phrase]",
        ]
    },

    "[shop_feature]": {
        Default: [
            "quality", "good service", "value for money", "the latest gear", "the [adjective] [noun]",
            "your satisfaction", "something"
        ]
    },

    "[shop_features]": {
        Default: [
            "the lowest prices", "happy customers", "great deals", "friendly staff"
        ]
    },

    "[shop_descriptive_phrase]": {
        Default: [
            "our legal obligation", "a happy accident", "an unexpected surprise", "possible", "everything",
            "better than a [noun]", "the law", "truly [adjective]", "job one"
        ]
    },

    "[STILL_WORKING_ON_IT]": {
        # The PC has not completed their task yet.
        Default: ["I'm still working on it."
                  ],
        personality.Cheerful: ["Things are going well, but I'm not quite done..."
                               ],
        personality.Grim: ["That is taking longer than expected.",
                           ],
        personality.Easygoing: ["Oh, right... I should probably get back to work on that.",
                                ],
        personality.Passionate: ["Not done yet, but I swear it will be!",
                                 ],
        personality.Sociable: ["Truth be told, I'm still working on that.",
                               ],
        personality.Shy: ["I'll let you know when I'm done.",
                          ],
    },

    "[subject_pronoun]": {
        Default: [
            "he", "she", "ze"
        ]
    },

    "[THANK_YOU]": {
        # A simple thank you is appropriate.
        Default: ["Thank you.", "Thanks."
                  ],
    },

    "[THANKS_FOR_BAD_NEWS]": {
        # The PC has just delivered some bad, but presumably important, news.
        Default: ["Thank you for letting me know."
                  ],
        personality.Cheerful: ["This is not the news that I had been hoping for."
                               ],
        personality.Grim: ["I should have seen this coming...",
                           ],
        personality.Easygoing: ["Thanks for telling me.",
                                ],
        personality.Passionate: ["You have done well in bringing me this terrible news.",
                                 ],
        personality.Sociable: ["The truth hurts, but I want to thank you for bringing this to me.",
                               ],
        personality.Shy: ["So that's the way it is.",
                          ],
    },

    "[THANKS_FOR_ADVICE]": {
        Default: ["[THANK_YOU]", "Thanks for the advice."
                  ],
        personality.Cheerful: ["Thanks, it all makes perfect sense now!"
                               ],
        personality.Grim: ["Your words have helped me a great deal.",
                           ],
        personality.Easygoing: ["I think I understand now...",
                                ],
        personality.Passionate: ["Yes, you have shown me the way and the light!",
                                 ],
        personality.Sociable: ["It's been a great help talking this out with you.",
                               ],
        personality.Shy: ["Thanks for that.",
                          ],
        LIKE: ["Thanks, I knew I could count on you for good advice.",
               ],
        DISLIKE: ["Amazing. Your advice wasn't as useless as I expected...",
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
        LIKE: ["It was a pleasure to fight at your side.",
               ],
        DISLIKE: ["Maybe you're a better pilot than I thought."
                  ],
    },

    "[THATS_GOOD]": {
        # Character reacts to good news.
        Default: ["Very good.",
                  "That's good."
                  ],
        personality.Cheerful: [
            "Nice!",
        ],
        personality.Grim: ["That is fortunate.",
                           ],
        personality.Easygoing: [
            "Neat.",
        ],
        personality.Passionate: [
            "That's the best news!",
        ],
        personality.Sociable: [
            "I'm glad to hear that.",
        ],
        personality.Shy: ["Good.",
                          ],
    },

    "[THATS_INTERESTING]": {
        # Character reacts to interesting news.
        Default: ["Very interesting.",
                  "This is interesting."
                  ],
        personality.Cheerful: [
            "Oh, cool!",
        ],
        personality.Grim: ["Fascinating.",
                           ],
        personality.Easygoing: [
            "Neat.",
        ],
        personality.Passionate: [
            "Amazing!",
        ],
        personality.Sociable: [
            "That's some very interesting news.",
        ],
        personality.Shy: ["Interesting.",
                          ],
    },

    "[THATSUCKS]": {
        Default: ["Too bad."
                  ],
        personality.Cheerful: [
            "Aww..."
            ],
        personality.Grim: ["Ashes.","Blazes.",
                           ],
        personality.Easygoing: ["Aw, nuts.",
                                ],
        personality.Passionate: [
            "That sucks.",
            ],
        personality.Sociable: [
            "That is unfortunate.",
            ],
        personality.Shy: ["Oh no.",
                          ],
    },

    "[THERE_ARE_ENEMY_TRACKS]": {
        # Enemies have been detected nearby. Not by sensors, but by more obvious signs.
        Default: ["[HOLD_ON] This place bears all the signs of enemy activity.",
                  "[LOOK_AT_THIS] From these tracks, I can tell there are [enemy_meks] nearby."
                  ],
        personality.Cheerful: [
            "[INTERESTING_NEWS] I hope I'm wrong about this, but these tracks look like they came from a whole bunch of meks, and not friendly ones.",
            "[LOOK_AT_THIS] These are definitely mecha tracks, and they're fresh."
            ],
        personality.Grim: ["[HOLD_ON] I've been picking up signs of enemy activity for a while now. We're almost on top of them.",
                           "[LISTEN_UP] This area reeks of enemy activity. Fresh tracks are everywhere."
                           ],
        personality.Easygoing: [
            "I don't want to alarm anyone, but this place has all the signs of recent enemy activity.",
            "[LOOK_AT_THIS] A clear impression of a mecha footprint. Fresh, too. Some people just don't know how to cover their tracks."
        ],
        personality.Passionate: [
            "[GOOD_NEWS] The [enemy_meks] I've been tracking are close now... possibly too close.",
            "[HOLD_ON] There are signs of enemy patrols all over the place. We could be walking straight into a trap!"
            ],
        personality.Sociable: [
            "[LISTEN_UP] I didn't want to say anything before I was sure, but I've been seeing signs of enemy activity, and I'm certain there are [enemy_meks] nearby.",
            "[HOLD_ON] These tracks show signs of recent enemy movement. They are definitely nearby."
        ],
        personality.Shy: ["[LOOK_AT_THIS] Clear signs of enemy activity...",
                          "[LISTEN_UP] There are [enemy_meks] nearby."
                          ],
        personality.Peace: [
            "[BAD_NEWS] According to these tracks, there's an enemy patrol nearby, but we still have a chance to avoid it.",
            ],
        personality.Justice: [
            "[HOLD_ON] I think I've found tracks belonging to an enemy patrol. They are close to here...",
        ],
        personality.Glory: [
            "[LOOK_AT_THIS] These tracks are proof that there's an enemy patrol nearby. We could run into it at any minute.",
        ],
        personality.Fellowship: [
            "[LOOK_AT_THIS] You see that mark? It was made by a mecha, and not one of ours. They must still be close to here.",
            ],
        personality.Duty: ["[LOOK_AT_THIS] I've been keeping an eye out for signs of enemy movement, and this is it. They must be close now.",
                           ],
    },

    "[THEYAREAMYSTERY]": {
        # Those folks we're talking about? All I know is that I know nothing about them.
        # The data block should include "they"
        Default: ["They are a real mystery.", "{they} are a mystery."
                  ],
        personality.Cheerful: [
            "If you find out anything about {they}, you can let the rest of us know."
        ],
        personality.Grim: [
            "{they} keep their secrets well hidden. Nobody knows much about them... or at least, nobody alive.",
        ],
        personality.Easygoing: [
            "I'll be honest, I don't know much about them. I don't think anybody does.",
        ],
        personality.Passionate: [
            "{they} are a mysterious order; no one knows who they are or what they are doing, but their legacy remains.",
        ],
        personality.Sociable: [
            "{they} aren't the most talkative bunch, that's for sure.",
        ],
        personality.Shy: [
            "{they} keep to themselves.",
        ],
    },

    "[THEYARETHIEVES]": {
        # Those folks we're talking about? Keep one hand on your wallet.
        # The data block should include "they"
        Default: ["They are no-good thieves.", "{they} are thieves."
                  ],
        personality.Cheerful: [
            "{they} will steal anything that isn't nailed down, and if they have a claw hammer they'll steal that too."
        ],
        personality.Grim: [
            "They are a gang of petty criminals, the lowest of the low.",
        ],
        personality.Easygoing: [
            "I guess you could say that {they} are criminals.",
        ],
        personality.Passionate: [
            "{they} are dishonorable scoundrels, nothing but robbers and thieves.",
        ],
        personality.Sociable: [
            "{they} are well known as a bunch of crooks.",
        ],
        personality.Shy: [
            "{they} are thieves.",
        ],
        personality.Justice: [
            "{they} are thieves; they steal from the rich. And the poor. And everybody else, for that matter.",
        ],
    },

    "[THEYAREOURENEMY]": {
        # Those folks we're talking about? Me and my folks don't like them.
        # The data block should include "they"
        Default: ["They are our enemies!", "{they} are our enemies."
                  ],
        personality.Cheerful: [
            "[chat_lead_in] {they} are not very popular around here."
        ],
        personality.Grim: [
            "The world would be a better place without them in it.",
            "{they} are truly despicable villains."
        ],
        personality.Easygoing: [
            "{they} are not exactly the nicest group of people...",
        ],
        personality.Passionate: [
            "{they} are our sworn enemy, and soon will taste vengeance!",
        ],
        personality.Sociable: [
            "{they} are the enemies of my people, and we have tolerated them for too long.",
        ],
        personality.Shy: [
            "They are our enemy.",
        ],
    },

    "[THEYWOULDBEFUNNYBUT]": {
        # Those folks we're talking about? Strange, but not in a good way.
        # The data block should include "they"
        Default: ["They would be funny if not for the fact that they're probably going to get someone killed."
                  ],
        personality.Cheerful: [
            "[chat_lead_in] {they} are not nearly as funny as you might think."
        ],
        personality.Grim: [
            "Don't be fooled by their clownish appearance; {they} are dangerous people.",
        ],
        personality.Easygoing: [
            "I hate to say it, but {they} worry me.",
        ],
        personality.Passionate: [
            "There's more to {they} than there seems.",
        ],
        personality.Sociable: [
            "I spoke to a few of them, and my impression is that they're not as harmless as they seem.",
        ],
        personality.Shy: [
            "They are dangerous.",
        ],
    },

    "[THIS_IS_A_SECRET]": {
        # The NPC is about to reveal something they probably shouldn't...
        Default: ["This is a secret, but...", "Remember, you didn't hear this from me..."
                  ],
        personality.Cheerful: ["I'm not one to gossip, but... who am I kidding? I love to gossip!",
                               ],
        personality.Grim: ["What I'm about to tell you is one of those things most people know better than to speak about.",
                           ],
        personality.Easygoing: ["I don't think this is exactly a secret, but it isn't well known either...",
                                ],
        personality.Passionate: ["You must swear that you will tell no-one you heard this from me.",
                                 ],
        personality.Sociable: ["I've heard a lot of things about this, things I'm in no position to confirm or deny...",
                               ],
        personality.Shy: ["I'll just lay this out.",
                          ],
        personality.Duty: ["Normally I wouldn't speak of this, but I fear this time I must.",
                           ],
        personality.Glory: ["When everything blows up, just remember who you heard this from first.",
                            ],
        personality.Justice: ["The truth of this matter has been hidden, but I'm giving it to you right now.",
                              ],
        personality.Peace: ["If word of this were spread around, I hate to think of the consequences, but...",
                            ],
        personality.Fellowship: ["I'm going to let you in on a secret.",
                                 ],
        LIKE: ["I'm only telling you this secret because I like you...",
               ],
    },

    "[THIS_IS_TERRIBLE_NEWS]": {
        # The NPC reacts to news with anger, shock, disgust...
        Default: ["This is terrible news.",
                  ],
        personality.Cheerful: ["I can hardly believe it...",
                               ],
        personality.Grim: ["I should have seen this coming.",
                           ],
        personality.Easygoing: ["Seriously? That is really bad.",
                                ],
        personality.Passionate: ["This is an outrage!",
                                 ],
        personality.Sociable: ["I'd like to thank you for bringing me this horrible news.",
                               ],
        personality.Shy: ["I see.",
                          ],
        personality.Duty: [ "You have done well to report this terrible news.",
                    ],
        personality.Glory: ["This is bad news; but there still may be a way to turn things around.",
                           ],
        personality.Justice: ["This is a travesty!",
                           ],
        personality.Peace: ["Absolutely tragic...",
                           ],
        personality.Fellowship: ["We will all need to come together to deal with this.",
                           ],
        LIKE: ["[THANKS_FOR_BAD_NEWS]",
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

    "[TIME_TO_UPGRADE_MECHA]": {
        # The NPC is going to upgrade their mecha.
        Default: ["I think it's about time for me to upgrade my [mecha]."
                  ],
        personality.Cheerful: [
            "Guess what? It's new [mecha] day!"
        ],
        personality.Grim: ["My current [mecha] is horribly outdated.",
                           ],
        personality.Easygoing: ["I might as well replace my [mecha].",
                                ],
        personality.Passionate: [
            "It's time for me to buy a new [mecha] worthy of my skills!",
        ],
        personality.Sociable: [
            "Time for me to get a new [mecha] that I won't be ashamed to be seen with in public.",
        ],
        personality.Shy: ["I need to upgrade my [mecha].",
                          ],
    },

    "[UNDERSTOOD]": {
        # The NPC understands, but doesn't necessarily agree.
        Default: ["Understood."
                  ],
        personality.Cheerful: [
            "I can accept that."
            ],
        personality.Grim: ["So I see.",
                           ],
        personality.Easygoing: ["Whatever.",
                                ],
        personality.Passionate: [
            "I hear and understand.",
            ],
        personality.Sociable: [
            "I understand what you're saying.",
            ],
        personality.Shy: ["Uh-huh.",
                          ],
    },

    "[vanquished]": {
        Default: ["vanquished", "defeated","wiped out","subjugated","overwhelmed","conquered","trounced",
                  "annihilated","subdued","crushed","demolished","destroyed","slaughtered"
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

    "[weapon]": {
        Default: ["pistol", "sword", "candlestick", "chainsaw", "power tool", "industrial laser", "knife",
                  "plasma cutter", "poisoned apple", "poisoned drink", "assassin droid", "bomb", "salvage crusher",
                  "gas bomb", "hydrospanner",
                  ],
    },

    "[WE_CAN_AVOID_COMBAT]": {
        # Usually for a lancemate who suggests a way around this combat.
        Default: ["We can avoid this combat, if you want."
                  ],
        personality.Cheerful: [
            "Luckily, there's nothing saying that we have to fight these [enemy_meks]."
            ],
        personality.Grim: ["The choice is yours: we can engage in mortal combat, or we can avoid them.",
                           ],
        personality.Easygoing: ["I'd just as soon avoid this conflict, but it's your choice.",
                                ],
        personality.Passionate: [
            "We could just avoid this battle altogether, but I say we attack!",
            ],
        personality.Sociable: [
            "Well, what do you say, [audience]? Do we go around them or do we go through them?",
            ],
        personality.Shy: ["Shall we just go around them?",
                          ],
        personality.Justice: [
            "Do we strike them down, thereby preventing them from harming others; or do we leave them be, and abstain from causing harm ourselves?",
        ],
        personality.Duty: [
            "We have no obligation to fight them now. What do you think?",
        ],
        personality.Peace: [
            "I'd rather not enter combat when we don't absolutely need to, but it's your call.",
        ],
        personality.Glory: [
            "We could just avoid them, but where's the glory in that?",
        ],
        personality.Fellowship: [
            "We can fight them or avoid them. I'll go along with what everyone else wants.",
        ],
    },

    "[WE_MEET_AGAIN]": {
        # A somewhat ominous "Hello again".
        Default: ["We meet again, [audience]."
                  ],
        FIRST_TIME: [
            "We meet again, [audience]... or have we?",
        ],
        personality.Cheerful: ["Imagine that, me finding you here, [audience].",
                               "How nice, it's you again.", "Ready to have some fun, [audience]?"
                               ],
        personality.Grim: ["Fate has reunited us, [audience].",
                           "Someone told me that you had died. I see now they were exaggerating."
                           ],
        personality.Sociable: ["Hello, [audience]. Did you miss me?",
                               "Is this a social call? Or are you here on serious business?"
                               ],
        personality.Shy: ['We meet again.',"I've been expecting you.",
                          ],
        personality.Easygoing: ["I have the wildest case of deja vu right now, [audience].",
                                "This is starting to be a regular thing.",
                                "Hey, there you are. I didn't really expect to see you today."
                                ],
        personality.Passionate: ["[audience]! It seems like I just can't get away from you.",
                                 "[audience]! Have you increased your power level?"
                                 ],
        LOVE: ["We have to stop meeting like this, [audience]!",
               ],
        LIKE: ["It's good to see you again, [audience]! Or at least it would be..."
               ],
        DISLIKE: ["Unfortunately, we meet again, [audience].",
                  ],
        HATE: ["Oh, you've come back. What have I done to deserve this?",
               ],
        personality.Duty: [
            "We face each other once more, [audience].",
        ],
        personality.Fellowship: [
            "This may not be the best time, but it's nice at least to see a familiar face.",
        ],
        personality.Glory: [
            "Welcome, [audience]! Once again you stand before my glory.",
        ],
        personality.Peace: [
            "For good or bad, we meet again.",
        ],
        personality.Justice: [
            "Have you made peace with your past acts, [audience]?",
        ],
    },

    "[WHATAREYOUDOINGHERE]": {
        # The PC has wandered into someplace and is about to get attacked, maybe.
        Default: ["What are you doing here?!",
                  ],
        personality.Cheerful: ["You aren't invited to this party, and we don't deal too kindly with crashers.",
                               ],
        personality.Grim: ["Welcome to your doom, foolish intruder!",
                           ],
        personality.Easygoing: ["You're not supposed to be here right now.",
                                ],
        personality.Passionate: ["I don't know what you're doing here, but I look forward to [defeating_you]!",
                                 ],
        personality.Sociable: ["Sorry to say that I'm not in the mood for visitors right now.",
                               ],
        personality.Shy: ["An intruder!",
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

    "[WOULD_YOU_MIND_ANSWERING_QUESTION]": {
        Default: ["Would you mind answering a few questions?", "Would you mind if I asked you some questions?"
                  ],
        personality.Cheerful: ["I have some questions for you... think of it as a quiz!"
                               ],
        personality.Grim: ["I'm looking for information.",
                           ],
        personality.Easygoing: ["I was wondering if you could maybe answer some questions?",
                                ],
        personality.Passionate: ["I have some questions, and I believe you may be the one who can answer them!",
                                 ],
        personality.Sociable: ["I want to talk with you about a couple of questions I have.",
                               ],
        personality.Shy: ["I have some questions for you.",
                          ],
    },

    "[YESPLEASE]": {
        # May be coupled with [NOTHANKYOU]
        Default: ["Yes, please."
                  ],
        personality.Cheerful: ["Oh yeah!",
                               ],
        personality.Grim: ["By blazes, yes.",
                           ],
        personality.Easygoing: ["Okay.","Alright.",
                                ],
        personality.Passionate: ["Yes, definitely!",
                                 ],
        personality.Sociable: ["Yes, please. That would be good.",
                               ],
        personality.Shy: ["Yes.",
                          ],
    },

    "[YOU_ARE_THE_BOSS]": {
        # Underclassman disagrees with Senpai's decision, but will go along with it.
        Default: ["You're the boss."
                  ],
        personality.Cheerful: ["You're the boss, and what the boss wants the boss gets.",
                               ],
        personality.Grim: ["I submit, begrudgingly, to your leadership.",
                           ],
        personality.Easygoing: ["That's alright, you're the one in charge here.",
                                ],
        personality.Passionate: ["I will defer to your leadership.",
                                 ],
        personality.Sociable: ["I don't like your decision, but you're the boss.",
                               ],
        personality.Shy: ["Fine.",
                          ],
        personality.Duty: [
            "I disagree with your decision, but will not fail in my duty."
        ]
    },

    "[YOU_SEEM_CONNECTED]": {
        # The speaker thinks the audience has knowledge and/or connections
        Default: ["You seem like the type of person who has a lot of connections.",
                  ],
        personality.Cheerful: ["I'll bet you hear all the juciest gossip!",
                               ],
        personality.Grim: ["A person like you hears a lot; maybe you learn some things you wish you hadn't.",
                           ],
        personality.Easygoing: ["You seem pretty connected; you know what's going on.",
                                ],
        personality.Passionate: ["A person like you must hear all kinds of fascinating things.",
                                 ],
        personality.Sociable: ["You are a person who gets around a lot; you must have a lot of connections.",
                               ],
        personality.Shy: ["You hear a lot of interesting things.",
                          ],
        LIKE: [
            "You seem to be pretty popular around these parts.",
        ],
        DISLIKE: [
            "A wangtta like you is sure to hear things that wouldn't be spoken in polite company.",
        ],
    },

    "[FORMAL_MECHA_DUEL]": {
        Default: [ "May your armor break, may your cockpit shatter, may who deserves to win, be who destroys the other."
                 ],
        personality.Glory: [ "Thus today we two meet upon our arena. May victory shine upon me!"
                           , "Glory shine upon the victor; one against one, strong against stronger."
                           , "I formally challenge you to a duel to destruction. Glory upon us both; but I shall be the victor."
                           ],
        personality.Peace: [ "I stand here the champion of my people; I fight against you now, for peace to prevail tomorrow."
                           , "I formally challenge you to a duel to destruction. May this be the final fight against you."
                           ],
        personality.Justice: [ "Well met on this day. Only the righteous shall stand after our fight."
                             , "This duel is my trial. May my victory today show the righteousness I stand for."
                             , "I formally challenge you to a duel to destruction. May my righteous stance shine through my mecha."
                             ],
        personality.Duty: [ "I fight you today for my honor. My obligation shall be what defeats you."
                          , "Thus my duty stands before me: you, and your defeat."
                          , "I formally challenge you to a duel to destruction. My obligation is to defeat you, and none shall stand in my way."
                          ],
        personality.Fellowship: [ "I stand here in the stead of my friends, to fight alone against you, that they may live."
                                , "I formally challenge you to a duel to destruction. My friends shall live, win or lose: and I shall defeat you."
                                ]
    },
    "[FORMAL_LETSFIGHT]": {
        Default: [ "[GOOD] Our destiny awaits. [LETSFIGHT]"
                 , "This duel shall lead to [defeating_you]."
                 , "Let it be remembered that today I [fight_you]."
                 ]
    }

}


