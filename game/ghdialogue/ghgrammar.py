from re import L
import gears.factions
from gears import personality, relationships, tags

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

FAVORABLE = "FAVORABLE"
UNFAVORABLE = "UNFAVORABLE"

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
        personality.Easygoing: ["Guess I should get started.",
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
        personality.Easygoing: ["Wanna come with me?",
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
            "Useless", "Useful", "Artificial", "Adorable", "Uncomfortable", "Comfortable", "Good", "Bad", "Open",
            "Modern",
            "Shiny", "Bright", "Honorable", "Stupid", "Smart", "Healthy", "Sinful", "Interesting", "Surprising",
            "Bland",
            "Sexy", "Loud", "Quiet", "New", "Important", "Wonderful", "Great", "Fun", "Beautiful", "Pretty", "Ugly",
            "Cool", "Strange", "Fast", "Slow", "Lucky", "Big", "Huge", "Long", "Small", "Tiny", "Exciting", "Gigantic",
            "Cosmic", "Natural", "Unwanted", "Delicate", "Stormy", "Fragile", "Strong", "Flexible", "Rigid", "Cold",
            "Hot", "Irradiated", "Poor", "Living", "Dead", "Creamy", "Delicious", "Cool", "Excellent", "Boring",
            "Happy",
            "Sad", "Confusing", "Valuable", "Old", "Young", "Loud", "Hidden", "Bouncy", "Magnetic", "Smelly", "Hard",
            "Easy", "Serious", "Kind", "Gentle", "Greedy", "Lovely", "Cute", "Plain", "Dangerous", "Silly", "Smart",
            "Fresh", "Obsolete", "Perfect", "Ideal", "Professional", "Current", "Fat", "Rich", "Poor", "Wise", "Absurd",
            "Foolish", "Blind", "Deaf", "Creepy", "Nice", "Adequate", "Expensive", "Cheap", "Fluffy", "Rusted",
            "Hormonal",
            "Lying", "Freezing", "Acidic", "Green", "Red", "Blue", "Yellow", "Orange", 'Purple', "Grey", "Brown",
            "Pink",
            "Dirty", "Gothic", "Metallic", "Mutagenic", "Outrageous", "Incredible", "Miraculous", "Unlucky",
            "Hated", "Loved", "Feared"
        ]
    },
    "[adjective]": {
        Default: [
            "useless", "useful", "artificial", "adorable", "uncomfortable", "comfortable", "good", "bad", "open",
            "modern",
            "shiny", "bright", "honorable", "stupid", "smart", "healthy", "sinful", "interesting", "surprising",
            "bland",
            "sexy", "loud", "quiet", "new", "important", "wonderful", "great", "fun", "beautiful", "pretty", "ugly",
            "cool", "strange", "fast", "slow", "lucky", "big", "huge", "long", "small", "tiny", "exciting", "gigantic",
            "cosmic", "natural", "unwanted", "delicate", "stormy", "fragile", "strong", "flexible", "rigid", "cold",
            "hot", "irradiated", "poor", "living", "dead", "creamy", "delicious", "cool", "excellent", "boring",
            "happy",
            "sad", "confusing", "valuable", "old", "young", "loud", "hidden", "bouncy", "magnetic", "smelly", "hard",
            "easy", "serious", "kind", "gentle", "greedy", "lovely", "cute", "plain", "dangerous", "silly", "smart",
            "fresh", "obsolete", "perfect", "ideal", "professional", "current", "fat", "rich", "poor", "wise", "absurd",
            "foolish", "blind", "deaf", "creepy", "nice", "adequate", "expensive", "cheap", "fluffy", "rusted",
            "hormonal",
            "lying", "freezing", "acidic", "green", "red", "blue", "yellow", "orange", 'purple', "grey", "brown",
            "pink",
            "dirty", "gothic", "metallic", "mutagenic", "outrageous", "incredible", "miraculous", "unlucky",
            "hated", "loved", "feared"
        ]
    },

    "[AEGIS_PROPAGANDA]": {
        # The NPC is going to say one of the foundational myths of Aegis Overlord.
        Default: ["Aegis only seeks to unite the human species in prosperity."
                  ],
        personality.Cheerful: ["Luna is much better off under Aegis than all the other places in the solar system."
                               ],
        personality.Grim: [
            "The only way to avoid human extinction lies in strength through unity; that strength is Aegis!",
        ],
        personality.Easygoing: ["If everyone submitted to Aegis, there'd be no more war."
                                ],
        personality.Passionate: ["The power of Aegis Overlord will overcome all!",
                                 ],
        personality.Sociable: ["The future of humanity lies in unity, not in senseless division.",
                               ],
        personality.Shy: ["Aegis will rule all.",
                          ],
        personality.Glory: [
            "We are the inheritors of Pax Europa, and therefore the rightful rulers of human space!"
        ],
        personality.Duty: [
            "You are fractured and divided, while we are duty-bound to Aegis; this is why you will lose."
        ],
        personality.Justice: [
            "Aegis only seeks to bring order to this chaotic world."
        ],
        personality.Peace: [
            "Aegis brought peace and unity to Luna; it can do the same for all of human space."
        ],
        personality.Fellowship: [
            "What you call freedom is mere perversity; join Aegis and discover your true will!"
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

    "[ANNOUNCE_GRUDGE]": {
        Default: ["I have a score to settle with you.",
                  "I haven't forgiven you for when [MEM_LoseToPC]!",
                  "I haven't forgotten that [MEM_Clash].",
                  "Remember when [MEM_DefeatPC]?"
                  ],
        personality.Cheerful: ["I'm happy to see you today, so I can [fight_you]!"
                               ],
        personality.Grim: ["Today's the day that I will [defeat_you].",
                           ],
        personality.Easygoing: ["Don't think I've given up on [defeating_you].",
                                "Why did [MEM_LoseToPC]? Now I have to [fight_you]."
                                ],
        personality.Passionate: ["I'm going to [fight_you], and this time it's personal!",
                                 "You think you're so good just because [MEM_LoseToPC]; it's about time I [defeat_you]!",
                                 "The moment [MEM_Clash], I knew that fate had bonded our destinies."
                                 ],
        personality.Sociable: ["Everybody knows why I need to [defeat_you].",
                               "People have been talking about the time [MEM_LoseToPC]; this time I [defeat_you].",
                               "Ever since [MEM_Clash], I knew that I would have to [defeat_you]."
                               ],
        personality.Shy: ["Prepare to die.",
                          "Remember when [MEM_LoseToPC]? Today I [defeat_you].",
                          "I won't forget [MEM_Clash]."
                          ],
    },

    # The data block should include "subject"; if not a proper noun, subject should have "the".
    "[ANY:OPINION]": {
        Default: ["What's your opinion about {subject}?",
                  "Tell me what you think about {subject}."
                  ],
        personality.Cheerful: [
            "So, do you like {subject} or what?",
        ],
        personality.Grim: [
            "Give me your unvarnished opinion about {subject}.",
        ],
        personality.Easygoing: [
            "What do you think about {subject}?",
        ],
        personality.Passionate: [
            "I must know your opinion of {subject}!",
        ],
        personality.Sociable: [
            "I hear that you have some feelings about {subject}.",
        ],
        personality.Shy: [
            "Tell me about {subject}.",
        ],
    },

    "[ARE_YOU_SURE_YOU_WANT_TO]": {
        Default: ["Are you certain?", "Are you sure you want to do that?"
                  ],
        personality.Cheerful: ["Hold on; you better make sure you're truly happy with this choice."
                               ],
        personality.Grim: ["Be careful; once you commit to this action, there is no backing out.",
                           ],
        personality.Easygoing: ["Doesn't that seem a little bit extreme to you?"
                                ],
        personality.Passionate: ["You are walking a dangerous path.",
                                 ],
        personality.Sociable: ["Have you consulted with others to see how your decision will affect them?",
                               ],
        personality.Shy: ["Seriously?",
                          ],
    },

    "[ARE_YOU_WILLING_TO_BET_YOUR_LIFE_ON_THAT]": {
        Default: ["Are you willing to bet your life on that?"
                  ],
        personality.Cheerful: ["If you're so sure, why don't we have a little game?"
                               ],
        personality.Grim: ["Are you truly willing to die for your belief?",
                           ],
        personality.Easygoing: ["Strange hill to die on, but if you wanna die..."
                                ],
        personality.Passionate: ["Your ignorance will get you killed, likely by my hand!",
                                 ],
        personality.Sociable: ["Are you willing to settle our differences on the field of battle?",
                               ],
        personality.Shy: ["Want to bet your life on that?",
                          ],
    },

    "[as_far_as_I_know]": {
        Default: ["As far as I know"
                  ],
        personality.Cheerful: ["You'll be happy to know", "To the best of my knowledge"
                               ],
        personality.Grim: ["I'm afraid that",
                           ],
        personality.Easygoing: ["I kinda think", "I could be wrong, but I've heard that"
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
                  "You shouldn't have come here. [LETSFIGHT]", "[BATTLE_GREETING] [LETSFIGHT]",
                  "Do you remember that [MEM_Clash]? [LETSFIGHT]", "Today I will [objective_ep]; [LETSFIGHT]"
                  ],
        personality.Cheerful: ["I was hoping that today would be interesting, and now here you are... [LETSFIGHT]",
                               ],
        personality.Grim: ["I'm afraid it's time for you to die... I'll try to make it painless. [LETSFIGHT]",
                           "Those who oppose me end up dead. [LETSFIGHT]"
                           ],
        personality.Easygoing: ["And here I thought this was going to be an easy day. [LETSFIGHT]",
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
        personality.Duty: ["I can't allow you to interfere with my mission. [LETSFIGHT]",
                           ],
        personality.Peace: ["Though I don't wish to cause harm, I'm going to have to [fight_you]. [LETSFIGHT]",
                            ],
        personality.Fellowship: ["You know the rules... [LETSFIGHT]",
                                 ],
        personality.Glory: ["Only one of us is going to leave here victorious. [LETSFIGHT]",
                            ],
        personality.Justice: [
            "I'm going to give you what you deserve... [LETSFIGHT]",
            "Remember when [MEM_LoseToPC]? Now you will taste justice."
        ]
    },

    "[ATTACK:CHALLENGE]": {
        Default: ["I accept your challenge.", "This won't go so well for you.",
                  "I can take you.", "Let's finish this.", "I must [objective_pp].", "I will [objective_pp]."
                  ],
        personality.Cheerful: ["Sounds like fun.", "Don't make me laugh.",
                               "This is getting fun!", "I'm here to [objective_pp] and crack jokes."
                               ],
        personality.Grim: ["You will regret challenging me.", "This may be your last mistake.",
                           "This will end in tears for you...", "I will [objective_pp] or die trying!"
                           ],
        personality.Easygoing: ["I guess we could do that.", "Sure, I have nothing better to do.",
                                "I'm just gonna [objective_pp]."
                                ],
        personality.Passionate: ["Prepare to be demolished.", "You don't know who you're messing with.",
                                 "You have no chance of beating me.", "WAARGH!!!", "I will [objective_pp]!"
                                 ],
        personality.Sociable: ["I'm all ready to fight.", "You're going to lose.", "I am here to [objective_pp]."
                               ],
        personality.Shy: ["Enough talk.", "Whatever.",
                          ],
        personality.Peace: ["Maybe you should just give up now?",
                            ],
        personality.Fellowship: ["Let's keep this an honorable duel.",
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
        Default: ["{subject}? What's that?", "Tell me about {subject}."
                  ],
        personality.Cheerful: ["I'd like to hear more about {subject}.",
                               ],
        personality.Grim: ["Tell me about {subject} or die.",
                           ],
        personality.Easygoing: ["{subject}, you say?",
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
        personality.Easygoing: ["You can go home now.",
                                ],
        personality.Passionate: ["Let me show you my mercy!",
                                 ],
        personality.Sociable: ["You can leave if you don't want to fight.",
                               ],
        personality.Shy: ["Go.",
                          ],
        personality.Peace: ["I have no desire to fight you.",
                            ],
        personality.Duty: ["Run away now and I won't chase you.",
                           ],
        personality.Fellowship: ["Go on, I won't challenge you.",
                                 ],
        personality.Glory: ["Maybe we can duel later, but not today.",
                            ],
        personality.Justice: ["It wouldn't be fair to fight you now.",
                              ],
    },

    "[ATTACK:RETREAT]": {
        Default: ["Leave before I [fight_you].", "I'll give you one chance to back out now."
                  ],
        personality.Cheerful: ["[HAGOODONE] You think you stand a chance?",
                               ],
        personality.Grim: ["So you choose to die by my hand? A brave choice, but a stupid one.",
                           ],
        personality.Easygoing: [
            "I mean, I'll [defeat_you] if you want, but you could save us all some time if you just run away now.",
        ],
        personality.Passionate: ["You dare to challenge me?! Turn back now, before I [defeat_you]!",
                                 ],
        personality.Sociable: ["If you insist on fighting, I don't mind showing everyone just how pitiful you are.",
                               ],
        personality.Shy: ["Back off, or I'll [defeat_you].",
                          ],
        personality.Peace: ["Leave this place before you get hurt.",
                            ],
        personality.Duty: ["It's my duty to [defeat_you].",
                           ],
        personality.Fellowship: ["You can save yourself now if you get out of here.",
                                 ],
        personality.Glory: ["A pest like you is no challenge for my skills.",
                            ],
        personality.Justice: ["Get out of my face before I give you what you deserve.",
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
        Default: ["Bad news...", "Oh no...", "[SWEAR]"
                  ],
        personality.Cheerful: ["Well that's not good...",
                               ],
        personality.Grim: ["That's just my luck.", "Curses!"
                           ],
        personality.Easygoing: ["Guess what?",
                                ],
        personality.Passionate: ["Oh [expletive]...", "This is terrible!"
                                 ],
        personality.Sociable: ["Bad news, everyone...",
                               ],
        personality.Shy: ["Bad news."
                          ],
    },

    "[bandit]": {
        Default: [
            "bandit", "brigand", "thief", "ravager", "pirate", "criminal", "crimepunk", "raider", "blackheart"
        ],
    },
    "[bandits]": {
        Default: [
            "bandits", "brigands", "thieves", "ravagers", "pirates", "criminals", "crimepunks", "raiders", "blackhearts"
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
        personality.Grim: ["You should know that {subject} is dangerous", "Keep your eyes on {subject}"
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
    "[BETRAYAL]": {
        # The NPC is betraying the PC.
        Default: [
            "Did you believe you could trust me? Pathetic.",
            "Surprise! I've been working against you this whole time."
        ],
        personality.Cheerful: [
            "Sorry, [audience], but this mission? It's a trap.",
            "Surprise! You're getting betrayed."
        ],
        personality.Grim: [
            "Now, I have you exactly where I want you... at my mercy!",
            "I suppose my betrayal comes as a surprise to you... you never were very observant."
        ],
        personality.Easygoing: [
            "Hey, so all this while I've just been pretending to be on your side.",
            "Yeah, you might have noticed that I'm pointing my guns at you right now..."
                                ],
        personality.Passionate: [
            "[Hey] the time has come for me to spring my trap!!!",
            "It's been killing me to pretend to be on your side. Thank [God] that ruse is over."
        ],
        personality.Sociable: [
            "Oh, how I've waited to reveal my true alleigance to you, [audience]...",
        ],
        personality.Shy: [
            "It's time to reveal how things really are.",
            "You're getting betrayed, [audience]."
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
        Default: ["eye", "nose", "face", "throat", "groin", "duodenum", "skull", "heart", "liver", "spine"
                  ],
    },

    "[BrowseWares]": {
        Default: ["Take a look around", "Browse my wares"
                  ],
        personality.Cheerful: ["There are so many exciting things here", "Enjoy browsing our selection"
                               ],
        personality.Grim: ["Caveat emptor", "Make sure you don't break anything while browsing"
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
        personality.Shy: ["Look around", "Don't touch the merchandise unless you intend to buy"
                          ],
        LOVE: [
            "It's a pleasure to have you in my store",
            "Let me give you the VIP service"
        ],
        LIKE: [
            "Always a pleasure to do business with you"
        ],
        DISLIKE: [
            "Hurry up and find what you need", "Browse the wares but don't try anything funny"
        ],
        HATE: [
            "Find what you need and get lost", "I'll be keeping my eye on you",
            "Don't try any funny business in my shop",
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
        personality.Sociable: [
            "I've been waiting to talk with you about something. I was wondering if you'd mind answering my questions.",
        ],
        personality.Shy: ["[audience], I have something to ask.",
                          ],
    },

    "[CHALLENGE]": {
        # NOTE: This grammar tag is for opponent NPC use only! It calls on the [objective_ep] tag.
        Default: [
            "[THREATEN]", "To [objective_ep] I will [defeat_you]!",
            "This will be payback for the time [MEM_LoseToPC]!",
            "Before [MEM_LoseToPC], but this time I will [defeat_you]!",
            "Remember when [MEM_DefeatPC]? I'm going to [defeat_you] again.",
        ],
        personality.Cheerful: [
            "Time to party.", "You can't stop me now; I will [objective_ep]!",
            "Remember when [MEM_LoseToPC]? I've been waiting for payback!",
            "Remember when [MEM_DefeatPC]? I'll enjoy doing that again."
        ],
        personality.Grim: [
            "Prepare for death.", "You don't stand a chance.",
            "If I have to kill you to [objective_ep], I will!",
            "I will [defeat_you] or die trying!",
            "I haven't forgiven you for [MEM_LoseToPC]..."
        ],
        personality.Easygoing: [
            "Shall we get started? Alright.",
            "You might not like it, but I will [objective_ep].",
            "You know, [speaker_faction] gave me a hard time when [MEM_LoseToPC]. This time I'll [defeat_you].",
        ],
        personality.Passionate: [
            "Show me what you have.",
            "I will unleash my full power to [objective_ep]!",
            "While you were wandering around, I was studying the [weapon]!",
            "My purpose in life is to flip out and [defeat_you]!",
        ],
        personality.Sociable: [
            "That's big talk. Prove it to me.",
            "You know what I'm going to do? [THREATEN]",
            "You think you can defeat me, but I will [objective_ep]. Would I waste time talking to you if I thought you had a chance of winning?",
            "[THREATEN] That's right, I said it.",
            "[chat_lead_in] you're about to get your arse kicked.",
        ],
        personality.Shy: [
            "Shut up and fight.",
            "I'll [defeat_you]."
        ],
        personality.Justice: [
            "For great justice!",
            "You deserve a thwomping for that time [MEM_LoseToPC]!",
        ],
        personality.Glory: [
            "May the best fighter win!",
            "I've been practicing since [MEM_LoseToPC]; this time I'll come out on top!",
            "Have you improved since [MEM_DefeatPC]? Let's find out.",
        ],
        personality.Duty: [
            "I will [objective_ep], as is my duty!",
            "In the name of [speaker_faction], I will not be defeated!",
        ],
        personality.Fellowship: [
            "I cannot disappoint [speaker_faction]; I must [defeat_you].",
        ],
        LIKE: [
            "It's sad that we're on differtent sides, but I must [objective_ep].",
            "I like you, but [speaker_faction] pays the bills, so... [THREATEN]",
        ],
        DISLIKE: [
            "It'll be my pleasure to [defeat_you].",
            "I want to [defeat_you] for that time [MEM_LoseToPC].",
        ]
    },

    "[CHANGE_MIND_AND_RETREAT]": {
        Default: ["[OnSecondThought], I don't really want to fight today...",
                  ],
        personality.Cheerful: ["[OnSecondThought], why ruin a beautiful day with a senseless battle?",
                               ],
        personality.Grim: ["[OnSecondThought]... I think I would prefer to live.",
                           ],
        personality.Easygoing: ["[OnSecondThought]... I'm just going to get out of here while I still can.",
                                ],
        personality.Passionate: ["[OnSecondThought], I need to train harder before facing you again.",
                                 ],
        personality.Sociable: ["[OnSecondThought], the last thing I need right now is another loss on my record.",
                               ],
        personality.Shy: ["[OnSecondThought], I'm just going to go.",
                          ],
        personality.Peace: ["[OnSecondThought], fighting has never really solved anything, has it?",
                            ],
        personality.Glory: ["[OnSecondThought], there is no glory to be had in getting my arse handed to me.",
                            ],
        personality.Duty: [
            "[OnSecondThought], this is a new mecha and it would be irresponsible of me to damage the paint job."
        ],
        personality.Fellowship: [
            "[OnSecondThought], there's no good reason for us to fight right now..."
        ],
        personality.Justice: [
            "[OnSecondThought], maybe you're in the right on this one. I'll just leave you to it."
        ]
    },

    "[CHAT]": {
        Default: [
            "[chat_lead_in] not much is going on.",
            "Is this [noun] the [noun] of the [adjective] [noun]?",
            "Anyone [adjective] can be [adjective].",
            "Anything [adjective] must be [adjective].",
            "Goodbye [noun], you were [adjective].",
            "You are so [adjective], I'll bet that you're never [adjective].",
            "The [noun] has been [adjective] lately, don't you think?",
            "There's been a lot of talk about [noun] but I don't think it's as [adjective] as they say.",
            "What do you think about [noun]?",
            "I'd like to try something [adjective] tonight.",
            "Do you prefer your [noun] [adjective] or [adjective]?",
            "Have you ever seen a [adjective] [noun]? All the ones I've seen are [adjective].",
            "Sometimes I feel very [adjective].",
            "What kind of [noun] do you like?",
            "I want to learn all I can about [noun], it'll be very [adjective] in the future.",
            "Are you as [adjective] as you look?",
            "I think this [noun] is [adjective].",
            "I think every [noun] is [adjective].",
            "Do you think I'm [adjective]?",
            "Have you heard about [adjective] [noun]?",
            "I sometimes wish every [noun] could be [adjective].",
            "Most of the time, [noun] is [adjective].",
            "Hear any [adjective] news lately?",
            "Don't be [adjective]. Let's be [adjective]!",
            "There was an article about [noun] on thrunet this morning.",
            "Did you see the [adjective] [noun] on TV this morning?",
            "All your [noun] are [adjective] to us.",
            "Not every [noun] is [adjective]; some are [adjective].",
            "That's the difference between [noun] and [noun]... one is [adjective] while the other is [adjective].",
            "That's the similarity between [noun] and [noun]... they're both [adjective].",
            "You know, [noun] is like [noun].",
            "I'm a real [adjective] fan of [noun].",
            "I'm a big fan of [adjective] [noun].",
            "A [adjective] [noun] is like [noun]... you know, it's [adjective].",
            "All the [adjective] [noun] are [adjective].",
            "Any [adjective] person can see that [noun] is [adjective].",
            "I was much more [adjective] when I was [adjective].",
            "A [adjective] [noun] is no substitute for a [adjective] [noun].",
            "A [adjective] [noun] is as [adjective] as a [adjective] [noun], as long as it's [adjective].",
            "The [adjective] [noun] is [adjective] if you're [adjective].",
            "Looking for [noun]? Try the [adjective] [noun].",
            "My [noun] is [adjective].",
            "No [noun] has ever been more [adjective] than [noun].",
            "You don't have to be [adjective] to get [adjective].",
            "Try to be [adjective] when you're [adjective].",
            "We'll be [adjective] when the [noun] is [adjective].",
            "You wouldn't know a [adjective] [noun] if it slapped you in the face.",
            "All things can be [adjective].",
            "Every [noun] can be [adjective].",
            "Your [noun] has [adjective], [adjective], and it had [noun] with that [noun].",
            "I'm a [adjective] [noun] with nothing but [noun]!",
            "I'm very [adjective]! I won't forget the [noun].",
            "You are [adjective] of course, but their [noun] is worse than that.",
            "There's [noun] in my [noun] for every [noun].",
            "Is that a [noun] in your [noun] or are you just [adjective] today?",
            "There's no [noun] for the [adjective] [noun].",
            "Do you think we can find [adjective] [noun] in the [noun]?",
            "I think [noun]'s looking out for [noun].",
            "The [noun] is a [noun].",
            "It's like a [noun] out there.",
            "But if [noun] can be built according to your [noun], that would be [adjective].",
            "Just leave this [noun] to me!",
            "It's good to know your [noun] is a [noun].",
            "What did you say? You can't be [adjective]!",
            "But what about the [adjective] [noun]? Oh, never mind.",
            "It must be [adjective] to have your own [noun].",
            "The [noun] used to be more [adjective] than it is now.",
            "Everyone says that the [noun] is famous for being [adjective].",
            "If ever you are [adjective], put a [noun] in your [noun].",
            "Tell me about the [adjective] [noun].",
            "Do you know much about the [noun]? I thought it was [adjective].",
            "There are two kinds of [noun] in this world- the [adjective] ones and the [adjective] ones.",
            "What's your [adjective] [noun] like?",
            "Sometimes you aren't [adjective] enough.",
            "At times you're too [adjective], in my opinion.",
            "I wish I could be more [adjective].",
            "I think I'm too [adjective].",
            "When I was [adjective] I used to think about [adjective] [noun] all the time.",
            "For every [adjective] [noun] there must be a [adjective] [noun].",
            "Before the [noun] can be [adjective], first the [noun] must be [adjective].",
            "Is there any [noun] in the [noun]?",
            "Is the [adjective] [noun] part of the [noun]?",
            "In my opinion, [adjective] [noun] isn't [adjective].",
            "I believe in the [noun].",
            "Do you have a [noun]?",
            "What [noun] is the [noun] in your [noun]?",
            "I believe the [noun] is very [adjective].",
            "The [adjective] [noun] is going to be [noun].",
            "That [adjective] [adjective] [noun] is far too [adjective] to be [adjective]. Seriously.",
            "If your [noun] was meant to be [adjective], it would've been a [noun] instead.",
            "There's a [noun] in my [noun].",
            "Behind every [adjective] [noun] is a [adjective] [noun].",
            "Is it getting [adjective] in here?",
            "Your [noun] is [adjective].",
            "That's a [adjective] [noun] that you have there.",
            "I know what you think about [noun], but in my opinion it's [adjective].",
            "Really? I have a [adjective] [noun] too!",
            "It's easy to tell that my [noun] is [adjective].",
            "It's obvious that your [noun] is [adjective].",
            "What did you expect? You already knew that the [noun] was [adjective].",
            "Could you possibly be any more [adjective]?",
            "I should let you know that the [noun] is [adjective].",
            "There's no such thing as a [adjective] [noun].",
            "That's a [adjective] [noun] if ever I saw one.",
            "In my opinion, this [noun] is slightly [adjective].",
            "In my [adjective] opinion, the [noun] is [adjective].",
            "In my [adjective] [noun] there would be no [noun].",
            "What good is a [adjective] [noun] to a [adjective] [adjective] [noun]?",
            "If the [noun] is both [adjective] and [adjective], why have a [noun]?",
            "I heard that when the [noun] was [adjective] a lot of the [noun] became [adjective].",
            "Someone said that you were a real [adjective] [noun].",
            "There's a rumor going around that his [noun] is [adjective].",
            "Wait a minute! How did I become the [adjective] [noun]?",
            "Hold your [noun] there, what are you talking about?",
            "Do you love [noun] too? At least, in a [adjective] way.",
            "A [noun] by any other [noun] would still smell as [adjective].",
            "Take your [noun] off my [noun].",
            "Please move your [adjective] [noun] to my [noun].",
            "Is your [noun] more [adjective] than my [noun]?",
            "Every [adjective] [noun] needs a [noun] to make it [adjective].",
            "The [noun] is my [noun].",
            "What was that again? About your [adjective] [noun]?",
            "Could you repeat what you just said about my [noun]?",
            "Alright, what I meant to say was that your [noun] is [adjective].",
            "Do you need to know my [adjective] [adjective] [noun]?",
            "You can't be serious! That [noun] is very [adjective].",
            "Put that [noun] in your [noun]... It's far too [adjective] for my [noun].",
            "Where's a [adjective] [noun] when you need one?",
            "You know what they say. All the [adjective] ones are either [adjective] or [adjective].",
            "I should let you know that this [noun] is extremely [adjective].",
            "If it's [adjective], it could very well be the [noun].",
            "Touch the [adjective] [noun].",
            "Don't be afraid of the [adjective] [noun].",
            "Seize the [noun].",
            "Be as [adjective] as you want. It's no [noun] to me.",
            "Everyone says to grab the [noun], but I think that's [adjective].",
            "What [noun] have you seen lately?",
            "What [noun] has been [adjective] lately?",
            "It's getting [adjective] [adjective] around here. Must be the [noun].",
            "My [noun] is getting [adjective].",
            "The [noun] is becoming [adjective].",
            "You need a [noun] for your [noun].",
            "The [adjective] [noun] really should have a [noun].",
            "Why be [adjective]? That's just [adjective].",
            "Want to be [adjective]? It looks [adjective]!",
            "This [adjective] [noun] is [adjective], my [noun] is [adjective] with the [noun].",
            "If it looks like a [noun], it's probably a [noun].",
            "If the [noun] is [adjective], wear it.",
            "If the [noun] is [adjective], shake it until it's [adjective].",
            "Touch my [noun].",
            "This town is famous for its [adjective] [noun].",
            "Are you looking for some [adjective] [noun]?",
            "I want a bit of [adjective] [noun].",
            "I'm going to put your [noun] in a [adjective] [noun].",
            "It's kind of [adjective], but mostly just [adjective].",
            "Every [noun] in the [noun] is [adjective].",
            "In summary, it's [adjective], [adjective], and [adjective].",
            "Is my [noun] too [adjective]?",
            "Do you think your [noun] is too [adjective]?",
            "Is your [adjective] [noun] too [adjective]?",
            "It's a [adjective] state of [noun] when the [noun] gets [adjective] from the [noun].",
            "That's the way it is. The [adjective] get [adjective] and the [adjective] get [adjective].",
            "In the [noun] of this [noun], any [noun] can be [adjective].",
            "Does your [noun] look [adjective]?",
            "It's a [noun] of some kind.",
            "Make the [noun] [adjective] or there'll be a [noun] in the [noun].",
            "It's a [adjective] sort of [noun], I think.",
            "I said, put that [adjective] [noun] in the [noun].",
            "You're [adjective] if you think that the [noun] is a [noun].",
            "It's as [adjective] as a [noun].",
            "That's my [noun], just as [adjective] as a [adjective] [noun].",
            "Is that [adjective] enough? Try the [noun] instead.",
            "It's a [adjective] [noun] that doesn't have a [noun].",
            "Are you [adjective] with the [adjective] [noun]?",
            "Do I look [adjective] with this [adjective] [noun]?",
            "Does it seem [adjective] when the [noun] is [adjective]?",
            "I always feel [adjective] on [adjective] days.",
            "The [adjective] [noun] is [adjective] every [adjective] day.",
            "This [noun] goes by in a [adjective] [noun].",
            "Oh, [noun]. It looks too [adjective] to be [adjective].",
            "How much [noun] would it take to become [adjective]?",
            "My [noun] is full of [adjective] [noun].",
            "I told him, \"if you touch my [noun] one more time, I'm going to [threat]!\"",
            "It's a [adjective] [noun] with some [noun] out there.",
            "That [noun] has extra [adjective] on the [noun].",
            "If you say my [noun] is [adjective] I might have to [threat].",
            "She's a [adjective] [noun] with extra [adjective].",
            "When the [noun] gets [adjective], it really goes [adjective].",
            "Do you want your [adjective] [noun] to be extra [adjective]?",
            "Play it [adjective] on the [noun].",
            "I'll [threat] if your [noun] is [adjective].",
            "Get your [adjective] [noun] out of my [noun] or I'll [threat].",
            "How [adjective] is your [noun]?",
            "Her [noun] is [adjective], but mine is more [adjective].",
            "His [noun] is more [adjective] than my [noun].",
            "My doctor said I need more [adjective] [noun] in my [noun].",
            "According to the [noun], it's [adjective] to be [adjective].",
            "I need a seven letter word for a [adjective] [noun].",
            "It's a thin line between [adjective] and [adjective].",
            "There's a [adjective] [noun] between [adjective] and [adjective].",
            "That [adjective] [noun] is really [adjective].",
            "Forget the [noun]; that's [adjective]. Now is the time for [adjective] [noun]!",
            "This [adjective] [adjective] [noun] makes me [adjective].",
            "It's no [noun] being [adjective] when all the [noun] are [adjective] [adjective].",
            "Use your [noun] on the [noun] and [noun] should be [adjective].",
            "I know the [noun] is [adjective], but is it [adjective]?",
            "I could [threat] or [threat] if I were a [adjective] [noun].",
            "Over the [noun] is the [noun] for being [adjective].",
            "The [adjective] [adjective] [noun] jumped over the [adjective] [noun].",
            "Is your [noun] at one hundred percent?",
            "It's [adjective] that you think so, considering the [adjective] [noun].",
            "It's [adjective] in the [noun] but [adjective] in the [adjective] [noun].",
            "Run through the [noun] with a [adjective] [noun].",
            "On a [adjective] [noun] I want to see the [noun].",
            "Give the [adjective] [noun] a try.",
            "Give the [adjective] [noun] some [noun].",
            "When in [noun] act [adjective].",
            "Remember, it's not [adjective] unless it's a [adjective] [noun].",
            "You may have heard that the [noun] is the most [adjective] [noun] around here.",
            "If it's [adjective] it might as well be a [adjective] [noun] too.",
            "I heard there's a [adjective] [noun] in the [noun].",
            "It sounds [adjective]! I want to see the [noun].",
            "I should tell you that the [noun] is [adjective].",
            "Her [noun] of [noun] was really [adjective].",
            "If you're [adjective] and you know it bang your [noun].",
            "I'm reading a book about [noun]. It's a little [adjective] but mostly [adjective].",
            "You can buy anything on thrunet these days. I want to get a [adjective] [noun].",
            "How much [noun] would a [adjective] [noun] chuck?",
            "He'll never get a [noun] if he stays [adjective] like that.",
            "She's trying to act [adjective], but we all know that she's actually [adjective].",
            "He got a [adjective] [noun] last year and now he thinks he's [adjective].",
            "I'm [adjective]! That [noun] is [adjective]!",
            "Her boyfriend left the [adjective] [noun] for the [noun]. Now they're both [adjective].",
            "It's a [adjective] [adjective] [noun] out there.",
            "It's not very [adjective]. It could be more [adjective] if the [noun] were here.",
            "His uncle died and left them a [adjective] [noun]. Does that make any sense?",
            "[foaf] said that you were [adjective], but you aren't.",
            "She said you were [adjective], but I told her you weren't.",
            "No, I'm not really a [adjective] [noun]. I just like being [adjective].",
            "To be [adjective] is to be one with the [noun].",
            "There was a contest once to find the most [adjective] [noun].",
            "The [noun] will be [adjective] if they try that again.",
            "Someone has set us up the [noun]!",
            "Yes, it's a real [noun]. Why, does it look [adjective]?",
            "His [adjective] [noun] is [adjective].",
            "Her [adjective] [adjective] [noun] is a [adjective] [noun].",
            "Our [noun] should be [adjective] and [adjective].",
            "Their [noun] will be [adjective] and [adjective].",
            "Open the [noun] and make [noun] for the [adjective] [noun].",
            "This [noun] could use a bit of [adjective] [noun].",
            "It's not [adjective] enough. Give me a [noun] instead.",
            "I used to study [noun], but now I play [adjective] [noun].",
            "I think the [noun] is very [adjective].",
            "[foaf] told me that the [noun] is [adjective].",
            "Be [adjective] if you must.",
            "Word around here is that the [noun] is [adjective].",
            "I often hear that his [noun] is [adjective].",
            "I sometimes hear that her [adjective] [noun] used to be [adjective].",
            "I usually hear that it's [adjective].",
            "It's already [adjective]. I tried the [noun] to be [adjective].",
            "That depends on whether you're a [adjective] [noun] or a [adjective] [adjective] [noun].",
            "That depends on the [noun].",
            "It's a [adjective] question as to which [noun] to choose.",
            "People say he has a [adjective] [noun].",
            "People say she's a [adjective] [noun].",
            "How much [noun] can they fit in the [adjective] [noun]?",
            "It's [adjective] when you're [adjective].",
            "I don't believe in [adjective] [noun].",
            "Everyone on TV has a [adjective] [noun] but I just want a [noun].",
        ],
    },

    "[chat_lead_in]": {
        Default: [
            "They say that", "They say", "I've heard that", "I've heard", "I think that", "I think",
            "Someone told me that",
            "A friend told me that", "I believe", "It's rumored that", "People say that", "Word around here is that",
            "It's been rumored that", "Everyone knows that", "Everyone says that", "I heard a rumor that",
            "I heard someone say that", "You may have heard that", "It's common knowledge that", "You should know that",
            "It's been said that", "I often hear that", "Someone said that", "In my opinion,", "In my humble opinion,",
            "My friend said that", "All my friends say that", "My friend told me that",
            "You may have heard this already, but", "I bet", "You'd never guess it, but", "I bet you didn't know that",
            "There's been a rumour going around that", "For your information,", "Don't say I told you so, but",
            "To be completely honest with you,", "Word is that", "[as_far_as_I_know]"
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
        personality.Grim: [
            "I am in no condition to go with you right now... but ask me again tomorrow, if I'm still alive.",
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

    "[CONTROVERSIAL_OPINION]": {
        # data block needs {opinion}
        Default: ["I think {opinion}.",
                  ],
        personality.Cheerful: ["I honestly believe {opinion}.",
                               ],
        personality.Grim: [
            "There's no denying that {opinion}.",
        ],
        personality.Easygoing: ["In my opinion, {opinion}."
                                ],
        personality.Passionate: ["It's undeniable that {opinion}!"
                                 ],
        personality.Sociable: ["It is a truth universally acknowledged that {opinion}.",
                               ],
        personality.Shy: ["{opinion}.",
                          ],
    },

    "[CORPORATE_JOB_SPIEL]": {
        # data block needs {corporate_faction}
        Default: [
            "{corporate_faction} pays top dollar for qualified applicants.",
            "[CORPORATE_SPIEL]",
        ],
        personality.Cheerful: ["It's a joy working for {corporate_faction}.",
                               ],
        personality.Grim: [
            "You could do much worse than working for {corporate_faction}.",
        ],
        personality.Easygoing: ["{corporate_faction} is an alright company.",
                                ],
        personality.Passionate: ["To fight for {corporate_faction} is to fight for the future of humanity!",
                                 ],
        personality.Sociable: ["You could be a valued member of our team at {corporate_faction}.",
                               ],
        personality.Shy: ["Consider {corporate_faction}.",
                          ],
        gears.factions.RegExCorporation: [
            "RegEx is always looking for freelance cavaliers to do something or another.",
        ],
        gears.factions.KettelIndustries: [
            "Through its corporate and philanthropic activities, Kettel Industries seeks to restore the golden age of humanity.",
        ],
        gears.factions.BioCorp: [
            "Biocorp provides the tools and technology you need to survive in an ever changing world.",
        ]
    },

    "[CORPORATE_SPIEL]": {
        # data block needs {corporate_faction}
        Default: ["{corporate_faction} is the greatest corporation.",
                  ],
        personality.Cheerful: ["{corporate_faction} produces great ideas and great products.",
                               ],
        personality.Grim: [
            "{corporate_faction} is not as bad as those other corporations.",
        ],
        personality.Easygoing: ["{corporate_faction} makes neat stuff.",
                                ],
        personality.Passionate: ["I am proud to work for {corporate_faction}!",
                                 ],
        personality.Sociable: ["Remember, {corporate_faction} is your friend.",
                               ],
        personality.Shy: ["{corporate_faction} is good.",
                          ],
        gears.factions.RegExCorporation: [
            "RegEx Corporation is the corporation of the people!",
        ],
        gears.factions.KettelIndustries: [
            "Kettel Industries is the largest business conglomerate in the solar system."
        ],
        gears.factions.BioCorp: [
            "Biocorp harnesses the power of nature for the future of humanity."
        ]
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
            "abandoned factory", "prezero ruin", "low-rad zone", "smuggler point", "deserted fortress",
            "ancient fallout shelter", "shantytown", "ruined city", "demolition zone", "scavenger camp"
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
        Default: ["defeating you", "beating you"
                  ],
        personality.Cheerful: ["winning", "kicking your arse"
                               ],
        personality.Grim: ["destroying you", "crushing you", "causing you pain",
                           "watching you suffer", "killing you",
                           ],
        personality.Easygoing: ["fighting you",
                                ],
        personality.Passionate: ["facing a true challenge", "annihilating you",
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
        personality.Passionate: ["show them our full power", "put them in their place",
                                 "unleash the fires of destruction"
                                 ],
        personality.Sociable: ["humiliate them",
                               ],
        personality.Shy: ["stop them",
                          ],
    },

    "[DENY_JOIN]": {
        Default: ["That's too bad.", "Too bad, I could have been a great help to you."
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

    "[DISCOVERY_AFTER_MECHA_COMBAT]": {
        Default: [
            "After the battle, you make an interesting discovery.",
            "You find some useful information from the navcomp of one of the defeated mecha."
        ],
    },

    "[DISTRACTION]": {
        Default: ["[LOOK_AT_THIS] A [adjective] [noun]!"
                  ],
        personality.Cheerful: ["[LOOK_AT_THIS] Someone brought a cake!"
                               ],
        personality.Grim: ["[LOOK_AT_THIS] We're under sttack!",
                           ],
        personality.Easygoing: ["Say, is that a [adjective] [noun] over there?"
                                ],
        personality.Passionate: ["Stop! Did you hear something suspicious!?",
                                 ],
        personality.Sociable: [
            "Look, I know you're busy, but are you sure this area is secure? I saw some suspicious people milling around.",
        ],
        personality.Shy: ["[LOOK_AT_THIS]",
                          ],
    },

    "[DISTRESS_CALL]": {
        Default: [
            "I am under attack by [enemy_meks]... If there are any friendly units in the area, I could use some backup."
        ],
        personality.Cheerful: ["Hey, any cavaliers out there! Wanna come help me fight some [enemy_meks]?"
                               ],
        personality.Grim: [
            "The situation is dire. If there are any friendly units in the nearby area, I need backup immediately.",
        ],
        personality.Easygoing: ["Hey, if there's anyone listening to this, I could really use a bit of help right now."
                                ],
        personality.Passionate: ["This is an emergency... I'm outgunned, outnumbered, and need aid immediately!",
                                 ],
        personality.Sociable: ["Calling all cavaliers in the area... I'm under attack and need backup.",
                               ],
        personality.Shy: ["This is a distress call. [HELP_ME]",
                          ],
    },

    "[DOTHEYHAVEITEM]": {
        # The data block should hold the item name as "item".
        Default: ["Don't they have {item}?",
                  "They should have {item}.", "What about their {item}?"
                  ],
    },

    "[DOYOUACCEPTMISSION]": {
        Default: ["Do you accept this mission?",
                  ],
        personality.Cheerful: ["This could be a great opportunity for you.",
                               ],
        personality.Grim: ["You look like you could use the money.",
                           ],
        personality.Easygoing: ["If you're interested, this mission is yours.",
                                ],
        personality.Passionate: ["Are you prepared to face this challenge?!",
                                 ],
        personality.Sociable: ["What do you think? Are you willing to do this mission?",
                               ],
        personality.Shy: ["Can you do this?",
                          ],
        LIKE: ["I'd really appreciate it if you could do this."],
        LOVE: ["It would mean a lot to me if you accept this mission."],
        DISLIKE: ["I wouldn't be asking you if I wasn't desperate for help."],
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
        personality.Passionate: ["I promise you won't regret it.", "You know you want it.",
                                 ],
        personality.Sociable: ["Don't you think that's a fair offer?",
                               ],
        personality.Shy: ["Take it or leave it.",
                          ],
    },

    "[DOYOUWANTAJOB]": {
        Default: ["Are you looking for work?",
                  "Do you want a job?"
                  ],
        personality.Cheerful: ["Looking for some easy money? It's your lucky day!",
                               ],
        personality.Grim: ["I have a task for you; it will not be easy.",
                           ],
        personality.Easygoing: ["Hey, are you busy right now?",
                                ],
        personality.Passionate: ["I need you for a very important task!",
                                 ],
        personality.Sociable: ["How'd you like to help me out with something?",
                               ],
        personality.Shy: ["I have a job available.",
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

    "[DUEL_GREETING]": {
        Default: ["May the best pilot win!",
                  ],
        personality.Cheerful: ["Let's try to have fun out there.",
                               ],
        personality.Grim: ["You have no chance to survive, make your time.",
                           "Only one of us is going to leave this place intact, and it isn't going to be you!"
                           ],
        personality.Easygoing: ["Might as well get started.",
                                ],
        personality.Passionate: ["You don't know it yet, but I've already won!",
                                 "I'm a hot blooded pilot, all ready to [defeat_you]!"
                                 ],
        personality.Sociable: ["Make sure to give my fans a good show!",
                               ],
        personality.Shy: ["En garde!",
                          ],
        personality.Glory: [
            "For the glory of [speaker_faction]!",
        ],
        personality.Justice: [
            "In the name of [speaker_faction], I will punish you!"
        ],
        personality.Duty: [
            "I fight in the name of [speaker_faction]!"
        ],
        personality.Fellowship: [
            "I salute you, my worthy opponent!"
        ]

    },

    "[EJECT]": {
        # This character is going to eject from their mecha.
        Default: ["I'm getting out of here!",
                  "This is enough damage for me...",
                  "I'm not sticking around!"
                  ],
        personality.Cheerful: [
            "I'd love to stick around some more, but I really must be going...",
        ],
        personality.Grim: [
            "Like tears in the rain. Time to eject.",
        ],
        personality.Easygoing: [
            "I don't like this mecha anymore. You can have it.",
        ],
        personality.Passionate: [
            "I have seen the true meaning of power!",
        ],
        personality.Sociable: [
            "Tell everyone I put up a good fight!",
        ],
        personality.Shy: [
            "I'm ejecting.",
        ],
        personality.Fellowship: [
            "There's nothing more I can do."
        ],
        personality.Peace: [
            "Life is not something to be thrown away lightly."
        ],
        personality.Duty: [
            "Discretion is the better part of valor..."
        ],
        personality.Justice: [
            "I won't throw my life away in vain."
        ],
        personality.Glory: [
            "I did my best; I have no regrets."
        ],
        tags.Faithworker: [
            "Heaven can wait."
        ],
        tags.Media: [
            "I'm too fabulous to die just yet...",
        ]
    },

    "[EJECT_AFTER_INTIMIDATION]": {
        # This character is going to eject from their mecha after being intimidated by a PC.
        Default: ["Looks like I have no choice. [EJECT]",
                  "[EJECT]", "First [MEM_LoseToPC], and now this... [EJECT]",
                  "Before [MEM_DefeatPC], but this time you win. [EJECT]"
                  ],
        personality.Cheerful: [
            "This is no fun anymore... [EJECT]",
            "No fair! I got completely pummeled! [EJECT]"
        ],
        personality.Grim: [
            "I'm not getting paid enough to die for this... [EJECT]",
        ],
        personality.Easygoing: [
            "Well, maybe I'll do better next time. [EJECT]",
            "I didn't really want to [objective_ep] anyhow. [EJECT]",
        ],
        personality.Passionate: [
            "This isn't the last you've heard of [speaker]! [EJECT]",
        ],
        personality.Sociable: [
            "You make some good points. [EJECT]",
        ],
        personality.Shy: ["You're right. [EJECT]",
                          ],
        personality.Fellowship: [
            "Maybe we'll face each other again, someday... [EJECT]"
        ],
        personality.Peace: [
            "Your mercy has been noted. [EJECT]"
        ],
        personality.Duty: [
            "I hate to abandon my post, but... [EJECT]"
        ],
        personality.Justice: [
            "Nothing would be accomplished by my death. [EJECT]"
        ],
        personality.Glory: [
            "I will take what I've learned from this battle and come back stronger. [EJECT]"
        ]
    },

    "[ENEMIES_HAVE_NOT_DETECTED_US]": {
        # Enemies have been detected nearby. Generally used by a LM with Stealth when battle can be avoided.
        Default: ["[HOLD_ON] There are enemy mecha ahead, but they haven't detected us yet.",
                  "[HOLD_ON] There are [enemy_meks] nearby; they haven't seen us yet."
                  ],
        personality.Cheerful: [
            "[BAD_NEWS] There's a group of [enemy_meks] just around the turn. The good news is, they haven't spotted us yet.",
            "[GOOD_NEWS] The [enemy_meks] that are lurking up ahead don't even know we're here."
        ],
        personality.Grim: ["[LISTEN_UP] There are enemies ahead; one more step and they'll spot the rest of you.",
                           "[HOLD_ON] There's a lance of enemy mecha nearby, and you almost gave away our position."
                           ],
        personality.Easygoing: [
            "Those [enemy_meks] up ahead haven't figured out that we're here yet... it would be a piece of cake to sneak around them.",
            "I don't think the [enemy_meks] over there are paying attention. They don't even know we're here."
        ],
        personality.Passionate: [
            "They way ahead is choked with enemies. But, there is another way, if you follow me...",
            "[LISTEN_UP] Those [enemy_meks] must be asleep at the console. Follow me and I can sneak us all around them."
        ],
        personality.Sociable: [
            "[LISTEN_UP] If you don't want to fight those [enemy_meks], I can easily provide us with a way around them.",
            "Did you notice those [enemy_meks] over there? I've been keeping my eye on them, but I don't think they've noticed us yet."
        ],
        personality.Shy: ["[HOLD_ON] They haven't detected us. I can get us around them.",
                          "[GOOD_NEWS] We spotted them before they spotted us. I can get us around them."
                          ],
        personality.Peace: [
            "[GOOD_NEWS] The mecha up ahead haven't seen us yet; with a bit of trickery, we can find a safe path around them.",
        ],
        personality.Justice: [
            "The [enemy_meks] over there haven't spotted us yet. It's your call whether we challenge them or just slip by.",
        ],
        personality.Glory: [
            "[LISTEN_UP] The [enemy_meks] over there? They don't even know we're here. We can do whatever we want.",
        ],
        personality.Fellowship: [
            "There's a group of mecha ahead; they appear to be hostile. They haven't spotted us yet.",
        ],
        personality.Duty: ["[HOLD_ON] The [enemy_meks] haven't seen us yet, so technically we could just sneak away.",
                           ],
    },

    "[enemy_is_going_to]": {
        # lead in to describing opponent's aims or methods as a simple present verb phrase
        Default: ["enemy forces are going to",
                  ],
        personality.Cheerful: ["your competition is going to",
                               ],
        personality.Grim: ["our dire foes plan to",
                           ],
        personality.Easygoing: ["they are trying to",
                                ],
        personality.Passionate: ["the enemy has mobilized and is going to",
                                 ],
        personality.Sociable: [
            "the enemy plan is to", "our enemy is going to"
                               ],
        personality.Shy: ["the enemy is going to",
                          ],
    },

    "[enemy_meks]": {
        # Insert your favorite euphemism or trash talk,
        Default: ["mecha", "enemy mecha",
                  ],
        personality.Cheerful: ["killer garbage cans", "giant lawn mowers",
                               ],
        personality.Grim: ["bastards", "geared up arseholes",
                           ],
        personality.Easygoing: ["guys", "meks",
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

    "[EULOGY]": {
        # Press F to Pay Respects
        Default: ["We pay our respects to this fallen comrade.",
                  ],
        personality.Cheerful: ["I'm not very good at this, but... it's sad this person died.",
                               ],
        personality.Grim: ["Everyone dies someday. May we all hope for such a glorious death.",
                           ],
        personality.Easygoing: ["This person died. That sucks. Better luck next life.",
                                ],
        personality.Passionate: ["Fly to [God], fallen warrior! Your mighty deeds will not be forgotten.",
                                 ],
        personality.Sociable: [
            "This could have been any one of us. May the life and deeds of the deceased live on forever in memory.",
            ],
        personality.Shy: ["Rest in peace.",
                          ],
        tags.Military: [
            "Salute! May the fallen be honored forever in our memory.",
        ],
        tags.Faithworker: [
            "We commend this fallen soul unto [God] and pray for those left behind."
        ]
    },

    "[expletive]": {
        Default: ["ashes", "blazes", "hell",
                  ],
        personality.Cheerful: [
            "flipping fire penguins",
        ]
    },

    "[FACTION_DEFEATED_ME]": {
        # data must contain "faction" element
        Default: ["Earlier, I was defeated by {faction} in combat.",
                  ],
        personality.Cheerful: ["I had a bad time fighting {faction} earlier...",
                               ],
        personality.Grim: ["I was fighting {faction}, and they nearly killed me.",
                           ],
        personality.Easygoing: ["Meh, I lost a battle to {faction}.",
                                ],
        personality.Passionate: ["I got my arse handed to me by {faction}!",
                                 ],
        personality.Sociable: [
            "I was running a routine mission against {faction}, but they've gotten far more powerful than I expected.",
        ],
        personality.Shy: ["{faction} defeated me.",
                          ],
        personality.Duty: ["I failed in my duty to defeat {faction}.",
                           ],
        personality.Glory: ["I hate to admit it, but {faction} beat me in combat.",
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
        Default: ["defeat you", "fight you", "beat you"
                  ],
        personality.Cheerful: ["kick your arse",
                               ],
        personality.Grim: ["destroy you", "crush you", "kill you",
                           ],
        personality.Easygoing: ["shoot you",
                                ],
        personality.Passionate: ["battle you", "challenge you", "do battle",
                                 ],
        personality.Sociable: ["humiliate you",
                               ],
        personality.Shy: ["stop you",
                          ],
        personality.Peace: ["stop you", "oppose you"
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

    "[Fortune_cookie]": {
        # Need a nameless NPC to send a message via a lancemate or other intermediary? Here you go!
        Default: [
            "if you specialize in armed combat, you might want to think about getting a boomerang or a spear so you'll have a ranged attack which uses your best skill",
            "the higher a shield's defense bonus, the harder it is to attack with that arm",
            "puffins fly, penguins plummet",
            "you don't have to do everything people tell you to do",
            "the more difficult the fight, the more you'll learn from it",
            "if you would be a great warrior, you must battle through the cave naked, armed only with a fondue fork",
            "an honest shopkeeper won't buy stolen goods",
            "there are no mistakes, only happy accidents",
            "only highly skilled foes can afford highly expensive mecha",
            "having a scout on your team is very useful for avoiding unnecessary fights",
            "survivalists know 101 uses for a dead monster",
            "scientists love disassembling machines for the spare parts",
            "the only defense against a big computer is an even bigger computer",
            "the memo pad is the most useful feature of your phone",
            "you should know what's going on before you pick a side in a fight",
            "you can't believe what everyone tells you, not even this",
            "accuracy counteracts mobility but doesn't help at all against targets with no mobility to speak of",
            "penetration counteracts armor but won't do a thing if your target has no armor to begin with",
            "the computers skill is much more useful if your mecha actually has a computer",
            "technology is our friend but also sometimes our enemy",
            "time is measured not in hours but in deeds",
            "you should definitely try not to die",
            "no cavalier is undefeatable, but some of them do a pretty good job pretending",
            "the best tactic when you are outnumbered and outgunned is to run away",
            "a wilderness guide can make long distance travel much easier",
            "a sneaky lancemate can help keep you out of trouble, as well as get you into trouble",
            "knowing the repair skill improves your odds of finding good salvage",
            "the first job of a cavalier is to survive",
            "the more you move the harder you are to hit",
            "running around the battlefield doesn't help when you run straight into a [mecha] with a laser axe",
            "it's hard to shoot fast moving opponents, which is why you should also pack a big stick",
        ],
        personality.Cheerful: [
            "everybody likes cookies"
        ],
        personality.Grim: [
            "there actually is such a thing as a stupid question",
        ],
        personality.Glory: [
            "if you keep trying to do better, eventually you'll get there",
        ],
        personality.Justice: [
            "it's a cavalier's duty to make the world a better place instead of a worse one",
        ],
        personality.Duty: [
            "once you've given your word there's no backing out",
        ],
        personality.Fellowship: [
            "you should leave fighting behind you on the battlefield",
        ],
        personality.Peace: [
            "every life is worth defending",
        ],
        tags.Criminal: [
            "a dishonest shopkeeper can be a good person to know",
        ],
        tags.Academic: [
            "this sentence is false",
        ],
        tags.Medic: [
            "every team needs a medic",
        ],
        tags.Craftsperson: [
            "every team needs a repairperson",
        ],
    },

    "[GIVE_PEACE_WITH_ENEMY_FACTION_A_CHANCE]": {
        # Data block should include enemy_faction
        Default: ["Have you considered making peace with {enemy_faction}?"
                  ],
        personality.Cheerful: ["What's so funny about making peace with {enemy_faction}?",
                               ],
        personality.Grim: ["Fighting {enemy_faction} will only lead to more bloodshed.",
                           ],
        personality.Easygoing: ["Instead of fighting, why not negotiate with {enemy_faction}?",
                                ],
        personality.Passionate: ["Your stupid war will be the end of you! Negotiate peace with {enemy_faction}.",
                                 ],
        personality.Sociable: ["This war must end; you should talk to {enemy_faction} and make peace."
                               ],
        personality.Shy: ["You should make peace with {enemy_faction}.",
                          ],
        personality.Peace: [
            "Give peace with {enemy_faction} a chance!"
        ],
    },

    "[God]": {
        # Insert an appropriate deity name
        Default: ["God", "Goddess"
                  ],
        tags.COMBATANT: [
            "Atan", "Mighty Atan"
        ],
        tags.Adventurer: [
            "Blessed Atan", "Atan"
        ],
        tags.Military: [
            "Loyal Atan", "Atan"
        ],
        personality.Duty: [
            "the Lord"
        ],
        personality.Peace: [
            "the Protector"
        ],
        personality.Justice: [
            "the Heavenly Judge"
        ],
        personality.Fellowship: [
            "the Universal Soul"
        ],
        personality.Cheerful: [
            "Heaven"
        ],
        personality.Grim: [
            "Crom"
        ],
        tags.Faithworker: [
            "the Almighty", "the All-knowing", "the Creator", "the Teacher"
        ],
        "Robot": [
            "the Maker"
        ],
        tags.Craftsperson: [
            "the Maker"
        ],
        personality.DeadZone: [
            "Kerberos", "Jore Mumbo", "Wise Trejhex", "Dread Abreldo", "Cursed Yatyzhar", 'Athogdoss',
            "the Nameless One", "the Corpse King", "the Electric Whisper", "the Eye in the Ziggurat",
            'Mother Zoklo', "the Core Demon"
        ],
        personality.GreenZone: [
            "the Earthmother", "the Skyfather"
        ],
        personality.Luna: [
            "Great Cesar's Ghost", "Europa", "Artemis", "Diana", "Jovus"
        ],
        personality.L5Spinners: [
            "Jovus", "the Omnifriend"
        ],
        personality.FelineMutation: [
            "Bast"
        ],
        personality.DraconicMutation: [
            "Bahamut"
        ],
        personality.GeneralMutation: [
            "Eris"
        ],
        personality.L5DustyRing: [
            "Jovus", "Eris", "the Omnifriend"
        ],
        gears.factions.ProDuelistAssociation: [
            "Atan Almighty", "Atan"
        ],
        gears.factions.BladesOfCrihna: [
            "the Ghosts of Crihna", "the Ghost of Space"
        ],
        gears.factions.AegisOverlord: [
            "Aegis Incarnate", "Hecate"
        ],
        tags.Criminal: [
            "the Trickster"
        ]
    },

    "[GOODBYE]": {
        Default: ["Goodbye."
                  ],
        personality.Cheerful: ["Bye bye.", "Gotta bounce!"
                               ],
        personality.Grim: ["Until we meet again.",
                           ],
        personality.Easygoing: ["See ya.", "So long!"
                                ],
        personality.Passionate: ["Farewell.",
                                 ],
        personality.Sociable: ["I'll see you later.", "Don't be a stranger."
                               ],
        personality.Shy: ["Bye.", "I'm out of here."
                          ],
        tags.Faithworker: [
            "[God] go with you.",
        ],
        tags.Police: [
            "Catch you later.",
        ],
        tags.Military: [
            "Over and out."
        ],
        personality.DeadZone: [
            "Survive and stay hydrated.",
        ],
        personality.Peace: [
            "Peace out.",
        ],
        personality.Fellowship: [
            "Take care!",
        ],
        personality.Glory: [
            "Gotta go."
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
        personality.Passionate: ["Fantastic!", "Amazing!", "Wonderful!"
                                 ],
        personality.Sociable: ["That's good to hear.",
                               ],
        personality.Shy: ["Alright.", "Okay."
                          ],
    },

    "[GOOD_GAME]": {
        # A good sport reply to a duel, contest, or game
        Default: ["Good match.", "Well done."
                  ],
        personality.Cheerful: ["Good game, [audience]!", "That was fun!"
                               ],
        personality.Grim: ["You did better than I expected.",
                           ],
        personality.Easygoing: ["Hey, well done or something.",
                                ],
        personality.Passionate: ["That was an amazing match!",
                                 ],
        personality.Sociable: ["Thanks for the good match, [audience].",
                               ],
        personality.Shy: ["Well done.",
                          ],
        personality.Glory: [
            "If you always do your best, it doesn't matter if you win or lose."
        ]
    },

    "[GOOD_IDEA]": {
        Default: ["Good idea.", "That's a good idea."
                  ],
        personality.Cheerful: ["Great idea, [audience]!",
                               ],
        personality.Grim: ["That's not a bad idea.",
                           ],
        personality.Easygoing: ["Yeah, that sounds alright.",
                                ],
        personality.Passionate: ["That's a brilliant idea!",
                                 ],
        personality.Sociable: ["Good thinking, [audience].",
                               ],
        personality.Shy: ["Interesting.",
                          ],
    },

    "[GOOD_JOB]": {
        Default: ["[GOOD]", "Good job!", 
                  ],
        personality.Cheerful: ["Good going, [audience]!",
                               ],
        personality.Grim: ["For a while I doubted you'd pull it off.",
                           ],
        personality.Easygoing: ["Nice; I hope it wasn't too much trouble.",
                                ],
        personality.Passionate: ["Fantastic work!",
                                 ],
        personality.Sociable: ["You've got a talent for this sort of thing, [audience].",
                               ],
        personality.Shy: ["Good work.",
                          ],
        personality.Duty: [
            "Well done.",
        ]
    },

    "[GOODLUCK]": {
        Default: ["Good luck.", "Good luck with that."
                  ],
        personality.Cheerful: ["Have fun out there.",
                               ],
        personality.Grim: ["Try not to get yourself killed.",
                           ],
        personality.Easygoing: ["Shouldn't be too hard.",
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
        Default: ["Ha! That's a good one.", "Yeah, right."
                  ],
        personality.Cheerful: ["LOL!",
                               ],
        personality.Grim: ["Ha ha, very funny.", "Was that supposed to be a joke?"
                           ],
        personality.Easygoing: ["You're funny.",
                                ],
        personality.Passionate: ["Ha! You should've been a comedian.",
                                 ],
        personality.Sociable: ["Why don't you pull my other leg.",
                               ],
        personality.Shy: ["Ha!",
                          ],
    },

    "[HALT]": {
        Default: ["Halt.", "Stop right there.", "I know you; [MEM_Clash]."
                  ],
        personality.Cheerful: ["Hey, where do you think you're going?",
                               ],
        personality.Grim: ["Don't move or you're dead."
                           ],
        personality.Easygoing: ["I'm afraid I'm gonna have to stop you right there.",
                                ],
        personality.Passionate: ["Halt!!!",
                                 ],
        personality.Sociable: ["Halt; come any closer and I'll be forced to attack.",
                               ],
        personality.Shy: ["Stop.",
                          ],
    },

    "[harm_you]": {
        Default: [
            "[defeat_you]", "harm you", "hurt you"
        ],
        personality.Cheerful: [
            "make you cry", "stick your head up your own butt"
        ],
        personality.Grim: [
            "teach you the true meaning of agony",
            "make you suffer", "obliterate you",
        ],
        personality.Easygoing: [
            "do some unpleasant stuff to you",
            "ruin your day, and possibly your face too"
        ],
        personality.Passionate: [
            "unleash my full power",
            "give you a lesson in pain",
        ],
        personality.Sociable: [
            "show you what I can do with a [weapon]",
            "show you how I earned my brutal reputation",
        ],
        personality.Shy: [
            "get violent",
        ],
        tags.Faithworker: [
            "send you to meet [God]"
        ],
    },

    "[HAVE_YOU_CONSIDERED]": {
        # Speaker is floating an idea for consideration.
        # data should include "consider_this"
        Default: ["Have you considered that {consider_this}?"
                  ],
        personality.Cheerful: ["Here's an idea: {consider_this}!",
                               ],
        personality.Grim: ["You've obviously failed to consider that {consider_this}."
                           ],
        personality.Easygoing: ["Maybe {consider_this}.",
                                ],
        personality.Passionate: ["But {consider_this}!!!",
                                 ],
        personality.Sociable: [
            "I would suggest that {consider_this}.",
        ],
        personality.Shy: ["I think {consider_this}.",
                          ],
        DISLIKE: ["But actually, {consider_this}."]
    },

    "[HAVE_YOU_TRIED_PEACE]": {
        # data should include "enemy_faction"
        Default: ["Have you tried negotiating for peace with {enemy_faction}?"
                  ],
        personality.Cheerful: ["Maybe you can end this thing with {enemy_faction} without hurting anyone else.",
                               ],
        personality.Grim: ["Seems to me you can keep fighting {enemy_faction}, or you can work out a deal."
                           ],
        personality.Easygoing: ["Wouldn't it be easier to just talk through your problems with {enemy_faction}?",
                                ],
        personality.Passionate: ["You will never end this conflict through further violence!",
                                 ],
        personality.Sociable: [
            "It seems to me that your conflict with {enemy_faction} requires talking, not more fighting.",
        ],
        personality.Shy: ["There might be a diplomatic solution to your conflict with {enemy_faction}.",
                          ],
    },

    "[HELLO_PLUS]": {
        Default: [
            "[HELLO]", "[HELLO]", "[HELLO]", "[HELLO]", "[HELLO]",
            "[HELLO] [CURRENT_EVENTS]", "[HELLO] [CURRENT_EVENTS]", "[HELLO] [CURRENT_EVENTS]",
            "[HELLO] [CURRENT_EVENTS]", "[HELLO] [CURRENT_EVENTS]", "[HELLO] [CURRENT_EVENTS]",
            "[HELLO] [CURRENT_EVENTS]", "[HELLO] [CURRENT_EVENTS]", "[HELLO] [CURRENT_EVENTS]",
            "[HELLO] [CHAT]"
        ]
    },

    "[HELLO]": {
        MET_BEFORE: ["[HELLO_AGAIN]", ],
        FIRST_TIME: ["[HELLO_FIRST]", ],
    },

    "[HELLO_AGAIN]": {
        Default: ["Hello.", "Hello [audience]."
                  ],
        personality.Cheerful: ["Good to see you, [audience].",
                               ],
        personality.Grim: ["Oh, it's you.", "We meet again."
                           ],
        personality.Sociable: ['Hello there, [audience].',
                               ],
        personality.Shy: ['Hi.',
                          ],
        personality.Easygoing: ["Yo, [audience].", "Hi [audience]."
                                ],
        personality.Passionate: ['Hey [audience]!', '[audience]!'
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

    "[HELLO_UNFAV]": {
        Default: ["Get lost.", "Go away."
                  ],
        personality.Cheerful: ["Are you trying to ruin my day?",
                               ],
        personality.Grim: ["Drop dead.",
                           ],
        personality.Sociable: ["I have nothing to say to you.",
                               ],
        personality.Shy: ['...',
                          ],
        personality.Easygoing: ["I think it would be better if you leave now.",
                                ],
        personality.Passionate: ["You've got a lot of nerve showing up here.",
                                 ],
        LOVE: ["This isn't a safe place for you, [audience].",
               ],
        LIKE: ["You shouldn't be here, [audience], but don't worry. I won't tell on you.",
               ],
        DISLIKE: ["Get out of here, while you still can.",
                  ],
        HATE: ["I know you can't be [audience] because [audience] wouldn't have the nerve to show up here.",
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
        personality.Sociable: ["Hi, [audience]. What's new?", "Just stopping by to chat.",
                               ],
        personality.Shy: ["I'm looking for information.",
                          ],
        personality.Easygoing: ["Hear anything interesting lately?",
                                ],
        personality.Passionate: ["Hey [audience] , what's the latest news?",
                                 ],
    },

    "[HELLO:GOODBYE]": {
        Default: ["Well, I must be off.", "See you later.",
                  ],
    },

    # The data block should include "subject"; if not a proper noun, subject should have "the".
    "[HELLO:INFO]": {
        Default: ["Tell me about {subject}.",
                  "What can you tell me about {subject}?"
                  ],
    },

    # The data block should include "subject"
    "[HELLO:INFO_PERSONAL]": {
        Default: ["How have you been doing?", "What's new?",
                  "I hear you have a story about the {subject}."
                  ],
    },

    "[HELLO:JOIN]": {
        Default: ["Would you like to join my lance?",
                  "How about joining my lance?"
                  ],
        personality.Cheerful: ["Come join my lance, it'll be fun.",
                               ],
        personality.Grim: ["It will be dangerous, but I need your help.",
                           ],
        personality.Easygoing: ["I could use some help on this mission.",
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

    "[HELLOMISSION:MISSION]": {
        Default: ["Tell me the mission details.",
                  "[HELLO:MISSION]"
                  ],
        personality.Cheerful: ["[GOOD] Tell me about it.",
                               ],
        personality.Grim: ["Tell me your terms, then I'll decide.",
                           ],
        personality.Easygoing: ["What kind of mission are we talking about here?",
                                ],
        personality.Passionate: ["You need the best, and that means me!",
                                 ],
        personality.Sociable: ["[GOOD] Let me know about it.",
                               ],
        personality.Shy: ["I'm listening.",
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

    "[HELLO:OPEN_SCHOOL]": {
        Default: ["I'd like to train with you.",
                  "Can you help me improve my skills?"
                  ],
        personality.Cheerful: ["Let's study together!",
                               ],
        personality.Grim: ["Teach me what you know.",
                           ],
        personality.Easygoing: ["How'd you like to teach me something?",
                                ],
        personality.Passionate: ["I have come here to train under you.",
                                 ],
        personality.Sociable: ["I've heard that you can teach me something.",
                               ],
        personality.Shy: ["I am here to train.",
                          ],
    },

    "[HELLO:PERSONAL]": {
        Default: ["How have you been these days?",
                  "What have you been doing lately?"
                  ],
        personality.Cheerful: ["Good to see you! How are things?",
                               ],
        personality.Grim: ["Good to see that you're still alive. How are you?",
                           ],
        personality.Easygoing: ["So, how's it been this past while?",
                                ],
        personality.Passionate: ["You must tell me about the adventures you've had!",
                                 ],
        personality.Sociable: ["I'd love to catch up with eveyrthing you've been doing.",
                               ],
        personality.Shy: ["What's up?",
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
                  "Go ahead and ask.", "[HELLO:QUERY]"
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
        personality.Sociable: [
            "Finally, some reinforcements have arrived... I'm under attack by [enemy_meks]. [HELP_ME]",
        ],
        personality.Shy: ["I am under attack. [HELP_ME]",
                          ],
    },

    "[HELP_WITH_MOBILITY_KILL]": {
        Default: ["I'm going to need some help to get moving again."
                  ],
        personality.Cheerful: ["Would anybody like to help me fix this?"
                               ],
        personality.Grim: ["Just leave me behind; I'd only show you down...",
                           ],
        personality.Easygoing: ["I don't know if we can fix it now. I'll just stay here.",
                                ],
        personality.Passionate: ["We must repair this damage!",
                                 ],
        personality.Sociable: [
            "We could try to repair the movement systems, but if it doesn't work we've just wasted precious time and energy...",
            ],
        personality.Shy: ["Could anybody help?",
                          ],
    },

    "[HERE_YOU_GO]": {
        # Giving something to someone.
        Default: ["Here you go.", "Here you are."
                  ],
        personality.Cheerful: ["You're going to like this."
                               ],
        personality.Grim: ["Hopefully this will meet your expectations.",
                           ],
        personality.Easygoing: ["Here ya go.",
                                ],
        personality.Passionate: ["This is especially for you!",
                                 ],
        personality.Sociable: [
            "Here, this is for you.",
        ],
        personality.Shy: ["Here it is.",
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
        tags.Military: ["Heads up;",],
    },

    "[HOLD_ON]": {
        # Wait a minute...
        Default: ["Hold on...", "Wait a sec..."
                  ],
        personality.Cheerful: ["Yikes!", "Jinkies!"
                               ],
        personality.Grim: ["Halt...",
                           ],
        personality.Easygoing: ["Just a sec...", "Woah..."
                                ],
        personality.Passionate: ["Stop!",
                                 ],
        personality.Sociable: [
            "Everybody, hold on a second...",
        ],
        personality.Shy: ["Wait...",
                          ],
    },

    "[I_ACCLAIM_GLORY]": {
        # This character will speak the praises of cavalier virtue Glory.
        Default: [
            "My goal is to keep on improving my skills every day.",
        ],
        personality.Cheerful: [
            "It's fun to challenge yourself; win or lose, it's the only way to grow."
        ],
        personality.Grim: [
            "When death comes for me, let no one say that I didn't give this life my all.",
        ],
        personality.Easygoing: [
            "The trick to getting better at stuff is to keep on trying, even if you kinda suck."
        ],
        personality.Passionate: [
            "I face every day as a challenge to be overcome!",
        ],
        personality.Sociable: [
            "Many people think there's glory in victory; that's wrong. The glory comes from the perseverance needed to reach victory!",
        ],
        personality.Shy: [
            "I don't compare myself to others, but try every day to do better than I did yesterday.",
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

    "[I_AM_STILL_STANDING]": {
        # A person is injured or sick, but minimizing it.
        Default: ["I'm still standing up.", "I'm still conscious."
                  ],
        personality.Cheerful: ["I'm sure if I were really hurt I would have fainted."
                               ],
        personality.Grim: ["I'm still breathing.", "I've been in worse shape before."
                           ],
        personality.Easygoing: ["I'm okay... just... dandy."
                                ],
        personality.Passionate: ["I'm fine, and I refuse to let my body tell me otherwise!",
                                 ],
        personality.Sociable: ["Someone would have told me if I were that badly off.",
                               ],
        personality.Shy: ["I'm okay.",
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

    "[I_CAN_PICK_LOCK]": {
        Default: ["I can pick that lock.",
                  ],
        personality.Cheerful: ["Betcha I can pick that lock."
                               ],
        personality.Grim: ["I can't believe they're still using this kind of lock; I can bypass it easily.",
                           ],
        personality.Easygoing: ["I think I can probably pick the lock."
                                ],
        personality.Passionate: ["I can definitely pick this lock!!!",
                                 ],
        personality.Sociable: ["I've heard about this kind of lock, and I know how to bypass it.",
                               ],
        personality.Shy: ["Let me unlock it.",
                          ],
    },

    "[I_DONT_CARE]": {
        Default: ["I don't care."
                  ],
        personality.Cheerful: ["[HAGOODONE]"
                               ],
        personality.Grim: ["Your words mean nothing to me."
                           ],
        personality.Easygoing: ["Whatever."
                                ],
        personality.Passionate: ["And why should I care what you think?!",
                                 ],
        personality.Sociable: ["Nobody cares.",
                               ],
        personality.Shy: ["Shut up.",
                          ],
    },

    "[I_DONT_FEEL_WELCOME]": {
        # The speaker feels distinctly unwelcome, possibly threatened, in this place.
        Default: ["I really don't feel welcome here."
                  ],
        personality.Cheerful: ["I get the feeling that I'm not going to have a good time here."
                               ],
        personality.Grim: ["I fear I may not leave this place alive.",
                           ],
        personality.Easygoing: ["Did you ever get the feeling that you don't really belong somewhere?"
                                ],
        personality.Passionate: ["I feel threatened by this place...",
                                 ],
        personality.Sociable: ["I get the distinct impression that I'm not going to fit in here.",
                               ],
        personality.Shy: ["Let's get out of here.",
                          ],
    },

    "[I_DONT_FEEL_WELL]": {
        Default: ["I don't really feel well..."
                  ],
        personality.Cheerful: ["I don't want to worry anyone, but I feel sick."
                               ],
        personality.Grim: ["I am going to die, there is no point in denying it...",
                           ],
        personality.Easygoing: ["Well, I have been strangely [adjective] lately..."
                                ],
        personality.Passionate: ["There is a virus in my blood. It must be destroyed!",
                                 ],
        personality.Sociable: ["I'll be honest with you, I have been feeling a bit off.",
                               ],
        personality.Shy: ["I don't feel good.",
                          ],
    },

    "[I_DECLARE_WAR]": {
        # NOTE: This tag is for PC use only! It uses the objective_pp tag.
        Default: [
            "I declare war! [LETSFIGHT]", "I'm here to [threat]!", "I will [defeat_you]!",
            "I'll [defeat_you] to [objective_pp]!"
        ],
        personality.Cheerful: ["I thought it'd be fun to [defeat_you]."
                               ],
        personality.Grim: ["I come bearing gifts of destruction and decimation!",
                           ],
        personality.Easygoing: ["Maybe instead of talking we could fight this out?"
                                ],
        personality.Passionate: ["I'm here to show you my combat skills! [LETSFIGHT]",
                                 ],
        personality.Sociable: ["You must know that I'm here to fight you.",
                               ],
        personality.Shy: ["I declare war.",
                          ],
    },

    "[I_DONT_KNOW]": {
        Default: ["I don't know.", "How should I know?"
                  ],
        personality.Cheerful: ["It's funny you say that, because I have no idea."
                               ],
        personality.Grim: ["You are speaking of things beyond my knowledge.",
                           ],
        personality.Easygoing: ["I really have no idea.", "Did you really think I'd know that?"
                                ],
        personality.Passionate: ["I must confess my ignorance...",
                                 ],
        personality.Sociable: ["I'm sorry, but I really don't have any clue about this.",
                               ],
        personality.Shy: ["Good question.",
                          ],
    },

    "[I_DONT_KNOW_MUCH]": {
        Default: ["[I_DONT_KNOW]"
                  ],
        personality.Cheerful: ["I'd love to tell you all about it, but I don't know any more than you."
                               ],
        personality.Grim: ["I'm afraid you're out of luck. I know almost nothing about it.",
                           ],
        personality.Easygoing: ["Well, there's not much that I can really tell you..."
                                ],
        personality.Passionate: ["It pains me to admit that I don't know much about this...",
                                 ],
        personality.Sociable: ["I'm not sure anyone really knows much about that...",
                               ],
        personality.Shy: ["I don't know much.",
                          ],
    },

    "[I_DONT_WANT_TROUBLE]": {
        # Expresses a desire to not fight anyone.
        Default: ["I'm not looking for any trouble."
                  ],
        personality.Cheerful: [
            "I'm here for a good time, not a violent time."
        ],
        personality.Grim: ["You can relax; I'm not here to fight.",
                           ],
        personality.Easygoing: ["Take it easy, I don't want any trouble.",
                                ],
        personality.Passionate: [
            "My purpose today is not to do battle!",
        ],
        personality.Sociable: [
            "Can we talk this over? I'm not here to fight.",
        ],
        personality.Shy: ["I come in peace.",
                          ],
        personality.Justice: [
            "I have no reason to fight you.",
        ],
        personality.Duty: [
            "Relax, I haven't been sent to fight you.",
        ],
        personality.Peace: [
            "I have no intention of fighting today.",
        ],
        personality.Glory: [
            "As much as I'd love a quick battle, that's not what I'm here for.",
        ],
        personality.Fellowship: [
            "Calm down, nobody here wants to hurt anyone.",
        ],
    },

    "[I_FEEL_BETTER_NOW]": {
        Default: ["I feel much better now."
                  ],
        personality.Cheerful: ["Wow, I feel great now!"
                               ],
        personality.Grim: ["I no longer feel like I am going to die. Not soon, anyhow.",
                           ],
        personality.Easygoing: ["Yeah, I feel a lot better now."
                                ],
        personality.Passionate: ["Yes, I feel my power returning!",
                                 ],
        personality.Sociable: ["I have to tell you. that really made me feel better.",
                               ],
        personality.Shy: ["I feel better.",
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

    "[IF_YOU_WANT_MISSION_GO_ASK_ABOUT_IT]": {
        # A generic suggestion for the PC to go apply for a mission. Remember, you will never win a mission that you
        # don't apply for. And if you never try anything, you will never fail!
        Default: ["If you're interested in the mission you should go ask about it."
                  ],
        personality.Cheerful: ["This could be a good opportunity for you if you go ask about it in time.",
                               "If you want the mission, go ask about it."
                               ],
        personality.Grim: ["Try a mission and you might fail. Don't try and you will definitely fail.",
                           "Go apply for the mission; you have nothing to lose but your life."
                           ],
        personality.Easygoing: ["Remember, you only fail the missions that you try.",
                                ],
        personality.Passionate: ["Head over there and get that mission!",
                                 "This could be the start of a thrilling adventure!"
                                 ],
        personality.Sociable: ["If I were you, I'd go ask if the mission is still available. It could be a good opportunity.",
                               ],
        personality.Shy: ["You can go ask about it if you want.",
                          ],
        DISLIKE: [
            "This mission is probably beyond your abilities but you can try if you like.",
        ],
        HATE: [
            "This mission may very well kill you. I say you should apply for it.",
        ],
    },

    "[I_GOT_A_MISSION_OFFER]": {
        # A lancemate is telling the PC that they just received a mission offer.
        Default: ["I just got a mission offer.", "I've received a mission offer.",
                  "I got an urgent message from [foaf]..."
                  ],
        personality.Cheerful: ["We're in luck; someone wants to hire us."
                               ],
        personality.Grim: ["There's trouble afoot... and we've been asked to deal with it.",
                           ],
        personality.Easygoing: ["Hey, if you're interested, [foaf] just sent me a mission offer.",
                                ],
        personality.Passionate: ["I just got a message- someone needs our talents!",
                                 ],
        personality.Sociable: ["[audience], I was chatting with [foaf] and [subject_pronoun] has a mission we might be able to do.",
                               ],
        personality.Shy: ["I received a mission offer.",
                          ],
        personality.Duty: [
            "[Hey] I've been asked to perform a mission.",
        ],
        personality.Justice: [
            "I think you should hear about this mission offer.",
        ],
        personality.Fellowship: [
            "[Hey] [foaf] contacted me about an urgent mission.",
        ],
        personality.Glory: [
            "[Hey] I just got word of an exciting opportunity!",
        ],
        personality.Peace: [
            "[Hey] [foaf] needs our help.",
        ],
    },

    "[I_HAVE_BEEN_IMMOBILIZED]": {
        # A lancemate has suffered a mobility kill.
        Default: ["I have been immobilized!", "[SWEAR] I can't move this thing."
                  ],
        personality.Cheerful: ["Um, my mecha doesn't seem to be working right. I can't move.",
                               "I hope it isn't a big problem, but my mecha can't move."
                               ],
        personality.Grim: ["I'm afraid I have taken a mobility kill...", "[SWEAR] My movement systems are destroyed."
                           ],
        personality.Easygoing: ["Hey, don't want to be a bummer, but I can't get this thing moving.",
                                "I don't know if it's me doing something wrong or if it's all the damage I just took, but I can't move."
                                ],
        personality.Passionate: ["I can't move... my mecha is hurt!!!", "[SWEAR] My mecha is immobilized!"
                                 ],
        personality.Sociable: ["I don't want to alarm any of you, but my mecha can't move.",
                               "[Hey] My movement systems are offline. I think this is what soldiers call a mobility kill."
                               ],
        personality.Shy: ["I'm immobilized.", "My mecha can't move."
                          ],
        tags.Military: [
            "[SWEAR] I've just taken a mobility kill.",
        ]
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
        personality.Easygoing: [
            "I thought you'd all like to know that we're heading straight towards some [enemy_meks].",
            "Is anybody else picking up a big group of enemy meks ahead? Because I am picking up a big group of enemy meks ahead."
        ],
        personality.Passionate: ["[GOOD_NEWS] I have detected our enemies, and they are nearby!",
                                 "[HOLD_ON] According to my sensors, we are surrounded by enemy forces!"
                                 ],
        personality.Sociable: [
            "[HOLD_ON] We're not alone out here; I'm picking up a group of enemy mecha on my scanner.",
            "[LISTEN_UP] I just detected some [enemy_meks], and they're nearby."
        ],
        personality.Shy: ["[HOLD_ON] I'm reading enemy forces ahead.",
                          "There are [enemy_meks] nearby."
                          ],
        personality.Peace: ["[BAD_NEWS] My scanner has picked up some hostile mecha closing in on us.",
                            ],
        personality.Justice: [
            "[HOLD_ON] I just picked up some mecha ahead. I can't be sure what they want, but it probably isn't good.",
        ],
        personality.Glory: [
            "[GOOD_NEWS] If you were looking forward to getting in a fight today, I just detected [enemy_meks].",
        ],
        personality.Fellowship: ["[HOLD_ON] There's someone else out there; hostile mecha from the look of things.",
                                 ],
        personality.Duty: ["[LISTEN_UP] My scanners just picked up some [enemy_meks] approaching our position.",
                           ],
    },

    "[I_HAVE_HEARD_ENOUGH]": {
        # End a conversation that has already gone on too long.
        Default: ["I think I've heard enough about that."
                  ],
        personality.Cheerful: ["It's been fun talking, but I have to go."
                               ],
        personality.Grim: ["You are boring me. [GOODBYE]",
                           ],
        personality.Easygoing: ["Yeah, I don't think we have anything more to talk about.",
                                ],
        personality.Passionate: ["Stop; I have heard enough!",
                                 ],
        personality.Sociable: ["Yeah, I think I've heard enough about that for right now.",
                               ],
        personality.Shy: ["That's all the info I need.",
                          ],
    },

    "[I_HAVE_TRACKED_ENEMY_MECHA]": {
        # The enemy mecha's path has been discovered.
        Default: ["[HOLD_ON] I'm picking up the path these mecha took.",
                  "[LOOK_AT_THIS] These mecha didn't do a good job at covering their tracks."
                  ],
        personality.Cheerful: [
            "[GOOD_NEWS] I've got a sensor lock on the path these mecha took!",
        ],
        personality.Grim: [
            "[HOLD_ON] I'm getting strong readings from that direction...",
        ],
        personality.Easygoing: [
            "[LOOK_AT_THIS] I think I've found the direction these mecha came from.",
        ],
        personality.Passionate: [
            "[INTERESTING_NEWS] The [enemy_meks] left an obvious trail...",
        ],
        personality.Sociable: [
            "[HOLD_ON] I'm pretty sure I can track where these [enemy_meks] came from.",
        ],
        personality.Shy: [
            "[LISTEN_UP] The [enemy_meks] came from that direction."
        ]
    },

    "[I_HOPE_THIS_HELPS]": {
        # Expressing hope that the performed action has been helpful.
        Default: ["I hope this helps.",
                  "[GOODLUCK]"
                  ],
        personality.Cheerful: [
            "I'm sure this will be a great help to you!",
        ],
        personality.Grim: [
            "I know it's not much, but it's the best I can do.",
        ],
        personality.Easygoing: [
            "Maybe this'll help you out.",
        ],
        personality.Passionate: [
            "I am glad to have solved your problem!",
        ],
        personality.Sociable: [
            "I really hope that this will be helpful for you.",
        ],
        personality.Shy: [
            "Hopefully this will help."
        ]
    },

    "[I_KNOW_THINGS_ABOUT_STUFF]": {
        # Data must include "stuff"
        Default: [
            "I know things about {stuff}.",
            "I know certain things about {stuff}...",
            "[THIS_IS_A_SECRET]",
        ],
        personality.Cheerful: [
            "I have some funny stories about {stuff}...",
        ],
        personality.Grim: [
            "Long have I carried the burden of knowing too much about {stuff}...",
        ],
        personality.Easygoing: [
            "You wanna know about {stuff}?",
        ],
        personality.Passionate: [
            "I'm practically the solar system's leading expert in {stuff}!",
        ],
        personality.Sociable: [
            "You haven't heard about {stuff} yet? I can fill you in.",
        ],
        personality.Shy: [
            "Yeah, I know about {stuff}.",
        ],
        personality.Peace: [
            "If it will prevent future harm, I can tell you about {stuff}.",
        ],
        personality.Justice: [
            "You deserve to know about {stuff}.",
        ],
        personality.Glory: [
            "Oh yeah, do I ever know about {stuff}!",
        ],
        personality.Fellowship: [
            "I can share what I know about {stuff}.",
        ],
        personality.Duty: [
            "[LISTEN_UP] It is my duty to let you know everything I've heard about {stuff}.",
        ],
    },

    "[I_LEARNED_NOTHING]": {
        Default: ["I don't think I learned anything.", "I have learned nothing."
                  ],
        personality.Cheerful: ["That was fun, but I don't think I learned anything."
                               ],
        personality.Grim: ["I'm afraid this is beyond my abilities.",
                           ],
        personality.Easygoing: ["This stuff is way too hard for me."
                                ],
        personality.Passionate: ["I have failed! I am never going to master this...",
                                 ],
        personality.Sociable: ["I really don't think that I've learned anything from this experience.",
                               ],
        personality.Shy: ["I learned nothing.",
                          ],
    },

    "[I_LEARNED_SOMETHING]": {
        Default: ["I think I learned something.", "I feel like I'm better than before."
                  ],
        personality.Cheerful: ["Wow, I think I have a natural aptitude for this!"
                               ],
        personality.Grim: ["I can't believe it, but I seem to be improving.",
                           ],
        personality.Easygoing: ["Hey, this stuff isn't as hard as I thought."
                                ],
        personality.Passionate: ["I have increased my power level!",
                                 ],
        personality.Sociable: ["I can tell that my abilities have improved.",
                               ],
        personality.Shy: ["I learned something.",
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

    "[I_NEED_MORE_PRACTICE]": {
        Default: ["I need more practice.", "I should probably practice more."
                  ],
        personality.Cheerful: ["I'd really like to practice."
                               ],
        personality.Grim: ["I'm afraid that I need more practice.",
                           ],
        personality.Easygoing: ["Yeah, I guess I could use some practice."
                                ],
        personality.Passionate: ["I am always ready to improve my skills!",
                                 ],
        personality.Sociable: ["I think that I should proabably get some pactice.",
                               ],
        personality.Shy: ["I need to practice.",
                          ],
    },

    "[I_SAW_SOMETHING_YOU_WOULDNT_BELIEVE]": {
        Default: ["I saw something you wouldn't believe.",
                  ],
        personality.Cheerful: ["I saw something really funny a little while ago... not ha ha funny, either."
                               ],
        personality.Grim: ["I have seen things which chill me to even think about...",
                           ],
        personality.Easygoing: ["I don't think I'm crazy, but I've seen some crazy stuff."
                                ],
        personality.Passionate: ["I have seen things that were never meant for mortal eyes!",
                                 ],
        personality.Sociable: ["You wouldn't believe me if I told you about the things I've seen.",
                               ],
        personality.Shy: ["I have seen the impossible.",
                          ],
    },

    "[I_WANT_TO_TEST_PILOT_SKILLS]": {
        # This character expresses a desire to test their piloting skills.
        # Like Jiwoo, but with mecha instead of Pokemons.
        Default: [
            "I want to be the very best pilot.", "I want to see how my piloting skills rank."
        ],
        personality.Cheerful: [
            "Today I feel like I could take on an army!"
        ],
        personality.Grim: [
            "I need to test my mettle in brutal combat.",
        ],
        personality.Easygoing: [
            "I wanna see how I rank, piloting-wise."
        ],
        personality.Passionate: [
            "My heart craves the thrill of mecha combat!",
        ],
        personality.Sociable: [
            "I want to test my piloting skills, to see how I compare to the very best!",
        ],
        personality.Shy: [
            "I want to test my skills.",
        ],
    },


    "[i_want_you_to]": {
        # Sentence lead-in for a request or a mission description; followed by an infinitive verb phrase
        Default: ["I want you to",
                  ],
        personality.Cheerful: ["I'd be delighted if you could"
                               ],
        personality.Grim: ["I need you to",
                           ],
        personality.Easygoing: ["It'd be great if you could"
                                ],
        personality.Passionate: ["You must",
                                 ],
        personality.Sociable: ["I'd like to ask you to",
                               ],
        personality.Shy: ["You should",
                          ],
    },

    "[INFO:GOODBYE]": {
        Default: ["Well, that's enough talking for now.", "[GOODBYE]"
                  ],
        personality.Cheerful: ["That's fascinating. [GOODBYE]",
                               ],
        personality.Grim: ["Your chatter has started to bore me.",
                           ],
        personality.Easygoing: ["Y'know, I really better get going.",
                                ],
        personality.Passionate: ["Thanks for the info! [GOODBYE]",
                                 ],
        personality.Sociable: ["Well, I've enjoyed talking with you, but I really need to go now.",
                               ],
        personality.Shy: ["This is when I leave.",
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
        Default: ["[IP_STATUS]", "[IP_STATUS] [IP_NEWS]", "[IP_STATUS] [IP_NEWS] [IP_OPINION]",
                  "[IP_STATUS] [IP_OPINION]",
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
        personality.Easygoing: ["[IP_STATUS] [IP_Business], but in my spare time [IP_Pleasure].",
                                "[IP_STATUS] Earlier on [IP_BadNews], but [IP_GoodNews]. You know.",
                                "[IP_STATUS] In my free time [IP_Pleasure]. [IP_OPINION]"
                                ],
        personality.Passionate: [
            "[IP_STATUS] [IP_Pleasure], and also [IP_Business]. [IP_BadNews] but that doesn't worry me.",
            "[IP_STATUS] Would you believe that [IP_GoodNews]? Also, [IP_Pleasure]!",
            "[IP_STATUS] [IP_NEWS] [IP_Worry], but [IP_Hope]!",
            "[IP_STATUS] I've been working hard; [IP_Business]. [IP_OPINION]"
        ],
        personality.Sociable: [
            "[IP_STATUS] [IP_Pleasure], while by day [IP_Business]. [IP_BadNews], but [IP_GoodNews].",
            "[IP_STATUS] The main thing I have to report is that [IP_Pleasure]. Also, [IP_GoodNews].",
            "[IP_STATUS] Did you hear that [IP_BadNews]? I'm afraid it's true. But at least [IP_Pleasure].",
            "[IP_STATUS] [IP_Worry], but also [IP_Hope].",
            "[IP_STATUS] You should know that [IP_NEWS] [IP_OPINION]",
        ],
        personality.Shy: ["[IP_STATUS] [IP_Business].", "[IP_STATUS] [IP_Business]. [IP_Pleasure].",
                          "[IP_STATUS] [IP_GoodNews], but [IP_BadNews].", "[IP_STATUS] [IP_NEWS]",
                          ],
    },

    "[INFO_PERSONAL:JOIN]": {
        Default: ["Why don't you join my lance?",
                  ],
        personality.Cheerful: ["Let's go on an adventure together.",
                               ],
        personality.Grim: ["Let's go wreck some stuff.",
                           ],
        personality.Easygoing: ["That's cool. Wanna join my lance?",
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
        personality.Easygoing: ["I gotta run.",
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

    "[insult]": {
        # Noun phrase describing a character unfavorably.
        Default: [
            "jerk", "arsehole",
        ],
        personality.Cheerful: [
            "killjoy", "downer", "asshat"
        ],
        personality.Grim: [
            "pain in the arse", "waste of carbon", "ash-gibbon"
        ],
        personality.Easygoing: [
            "bad person", "doody head", "numbskull"
        ],
        personality.Passionate: [
            "sniveling worm", "abomination", "coward", "jackass"
        ],
        personality.Sociable: [
            "nobody", "brat", "piece of trash", "undesirable"
        ],
        personality.Shy: [
            "loudmouth", "git"
        ],
        personality.Justice: [
            "scoundrel", "scumbag"
        ],
        personality.Peace: [
            "meanie", "brute",
        ],
        personality.Glory: [
            "lowlife", "gorf herder", "wannabe"
        ],
        personality.Fellowship: [
            "creep", "slimeball"
        ],
        personality.Duty: [
            "weasel", "delinquent"
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

    "[INTIMIDATION_MECHA_COMBAT]": {
        # A PC is about to intimidate an NPC into ejecting from their mecha.
        Default: ["You have no chance of winning this battle; you might as well eject now.",
                  "One more shot and you're going to be destroyed. [YOU_SHOULD_EJECT]",
                  "Your [mecha] is in no state to keep fighting. [YOU_SHOULD_EJECT]"
                  ],
        personality.Cheerful: [
            "As fun as it would be to blow you up, I thought I should give you one last chance to eject.",
        ],
        personality.Grim: [
            "Your death approaches. [YOU_SHOULD_EJECT].",
        ],
        personality.Easygoing: [
            "I'm pretty sure your [mecha] isn't going to make it through this battle. [YOU_SHOULD_EJECT]",
        ],
        personality.Passionate: [
            "You have fallen before my superior skill! [YOU_SHOULD_EJECT]",
        ],
        personality.Sociable: [
            "It's clear to everybody that you have already lost this battle. [YOU_SHOULD_EJECT]",
        ],
        personality.Shy: ["Hey. [YOU_SHOULD_EJECT]",
                          ],
        personality.Fellowship: [
            "Hey, some friendly advice from a fellow cavalier: [YOU_SHOULD_EJECT]"
        ],
        personality.Peace: [
            "Remember, your life is worth more than your [mecha]. [YOU_SHOULD_EJECT]"
        ],
        personality.Duty: [
            "A warrior's first duty is to survive. [YOU_SHOULD_EJECT]"
        ],
        personality.Justice: [
            "This might not seem fair, but you're in no condition to keep fighting. [YOU_SHOULD_EJECT]"
        ],
        personality.Glory: [
            "There's no dishonor in being defeated by me. [YOU_SHOULD_EJECT]"
        ]
    },

    "[intimidation_concession]": {
        # An attempt at intimidation is being made. The speaker lets the listener know what WON'T happen if they
        # agree to the speaker's demands.
        Default: [
            "you can leave here with all your teeth",
            "I won't have to [harm_you]",
            "there doesn't have to be any violence"
        ],
        personality.Cheerful: [
            "we can both leave here happy and alive",
        ],
        personality.Grim: [
            "you get to see another day",
            "I won't [harm_you]"
        ],
        personality.Easygoing: [
            "nobody has to get hurt",
        ],
        personality.Passionate: [
            "I won't do what I'm thinking right now",
        ],
        personality.Sociable: [
            "I won't have to tell your family what happened to you",
        ],
        personality.Shy: [
            "you can live",
        ],
    },

    "[IP_NEWS]": {
        Default: ["[IP_GoodNews].", "[IP_BadNews].", "[IP_Business].", "[IP_Pleasure]."
                  ],
        personality.Cheerful: ["[IP_GoodNews]."],
        personality.Grim: ["[IP_BadNews]."],
        personality.Fellowship: ["[IP_Pleasure]."],
        personality.Duty: ["[IP_Business]."],
    },

    "[IP_OPINION]": {
        Default: ["[IP_Hope].", "[IP_Worry].",
                  ],
        personality.Cheerful: ["[IP_Hope]."],
        personality.Grim: ["[IP_Worry]."],
    },

    "[IP_STATUS]": {
        # Opening statement for an INFO_PERSONAL offer.
        Default: ["I'm fine.", "Overall, not bad.", "It's been alright."
                  ],
        personality.Cheerful: ["I've been good.", "I've been doing alright.",
                               "Things are good.", "I'm good."
                               ],
        personality.Grim: ["It hasn't been easy.", "Nothing I can't handle.",
                           "I haven't died yet.", "Things could be worse."
                           ],
        personality.Easygoing: ["Same as usual.", "I'm keeping at it.",
                                "I've been taking it easy.", "Trying not to work too hard."
                                ],
        personality.Passionate: ["Life never ceases to amaze.", "I'm keeping busy.",
                                 "I've been working out.", "I'm great!"
                                 ],
        personality.Sociable: ["You know how it is.", "Let me tell you about it.",
                               "You've got to hear this.", "I've been dying to tell you."
                               ],
        personality.Shy: ["I don't know what to say.", "Where to start...",
                          "Um...", "Yeah."
                          ],
    },

    "[I_PROPOSE_BATTLE]": {
        # Speaker is challenging the opponent to battle; there's an implied option to decline.
        Default: ["[BATTLE_GREETING] I challenge you to a fight!",
                  ],
        personality.Cheerful: ["[BATTLE_GREETING] It's a good day for a friendly battle, don't you think?",
                               ],
        personality.Grim: ["If you have the courage, I challenge you to battle! [LETSFIGHT]",
                           ],
        personality.Easygoing: ["[BATTLE_GREETING] Wanna fight?",
                                ],
        personality.Passionate: ["I challenge you to honorable combat! [LETSFIGHT]",
                                 ],
        personality.Sociable: ["[HELLO] If you have the time, I challenge you and your lance to battle.",
                               ],
        personality.Shy: ["[HELLO] I propose that we battle.",
                          ],
    },

    "[I_PROPOSE_DUEL]": {
        # Speaker is challenging the opponent to a pro duelist association regulations duel. PC can refuse.
        Default: ["I challenge you to a one on one duel! Do you think you can defeat me?",
                  ],
        personality.Cheerful: ["How'd you like to play a game? I challenge you to a one-on-one duel!",
                               ],
        personality.Grim: ["[BATTLE_GREETING] Are you brave enough to face me in single combat?",
                           ],
        personality.Easygoing: [
            "Hey, I've been looking for someone to challenge to a duel, and you'll do. Standard Pro Duelist Association rules, of course.",
        ],
        personality.Passionate: ["[BATTLE_GREETING] Do you accept or deny my challenge to a one-on-one duel?",
                                 ],
        personality.Sociable: [
            "[HELLO] I wish to challenge you to a one-on-one duel; there are no stakes but your reputation.",
        ],
        personality.Shy: ["[HELLO] I challenge you to a duel.",
                          ],
        gears.factions.ProDuelistAssociation: [
            "As a member of the Pro Duelist Association, I challenge you to a one on one duel! You are free to deny this challenge; if you accept, we will fight using standard association rules.",
            "It's a tradition of the Pro Duelist Association to challenge great mecaha pilots whenever we meet! I propose a one on one duel, which you are of course free to refuse."
        ],
        personality.Glory: [
            "[BATTLE_GREETING] I challenge you to a solo duel; the only stakes to this battle will be the glory of winning!"
        ]
    },

    "[I_REMEMBER_NOW]": {
        # The speaker has just remembered something.
        Default: ["Ah yes, now I remember."
                  ],
        personality.Cheerful: [
            "Oh yeah, I can remember all about that."
        ],
        personality.Grim: ["The memories come flooding back, overwhelming my senses.",
                           ],
        personality.Easygoing: ["I think I remember something about that...",
                                ],
        personality.Passionate: [
            "I can picture the memories with crystal clarity.",
        ],
        personality.Sociable: [
            "I believe I remember some things that you might find useful, or at the very least interesting.",
        ],
        personality.Shy: ["Yes, I remember now.",
                          ],
    },

    "[IT_IS_GOOD]": {
        # That thing we're talking about? It's good.
        # The data block should include "it"
        Default: ["It's good.", "I like {it}."
                  ],
        personality.Cheerful: [
            "I really like it.", "I think it's fantastic!", "{it} is wonderful."
        ],
        personality.Grim: [
            "I hate to admit, {it} is alright.",
            "It is far better than I expected.",
            "Well, {it} has been good so far, but we'll see how things go."
        ],
        personality.Easygoing: [
            "Yeah, I guess {it} is pretty good.",
            "It's alright. Maybe better than alright.",
            "Haven't really thought about it... I guess it's good?"
        ],
        personality.Passionate: [
            "I love {it}!", "It's the best!", "{it} is awesome!"
        ],
        personality.Sociable: [
            "In my opinion, {it} is good.",
            "I was talking with [foaf] recently, and we both agree it's good.",
            "As far as I'm concerned, it's good."
        ],
        personality.Shy: [
            "It's good.", "{it} is good."
        ],
    },

    "[IT_IS_OK]": {
        # That thing we're talking about? It's good.
        # The data block should include "it"
        Default: ["It's ok.", "{it} is ok."
                  ],
        personality.Cheerful: [
            "It's not bad.", "{it} is alright.",
        ],
        personality.Grim: [
            "{it} is bad, but better than some of the alternatives.",
            "I don't like {it}, but things could be worse.",
            "I guess it's the best we could hope for."
        ],
        personality.Easygoing: [
            "I don't have much of an opinion about {it}.",
            "{it} could be better, but could be worse.",
            "I don't know... I guess {it} doesn't bother me much?"
        ],
        personality.Passionate: [
            "I have no strong feelings about {it}, which is odd.",
            "It's bland. Boring. Neither this way nor the other."
        ],
        personality.Sociable: [
            "In my opinion, it's mediocre.",
            "According to [foaf], people don't care about {it} much.",
            "As far as I'm concerned, {it} is acceptable."
        ],
        personality.Shy: [
            "{it} is what it is."
        ],
    },

    "[IT_IS_OK_OR_BETTER]": {
        # The data block should include "it"
        Default: ["[IT_IS_OK]", "[IT_IS_GOOD]"
                  ],
        personality.Cheerful: ["[IT_IS_GOOD]",],
        personality.Grim: ["[IT_IS_OK]",],
    },

    "[IWILLDOMISSION]": {
        # The data block should include "mission", which is a verb phrase
        Default: ["I'll get to work.",
                  "I'll {mission}.", "[ICANDOTHAT]"
                  ],
        personality.Cheerful: ["Sounds like fun.",
                               ],
        personality.Grim: ["This may get me killed, but I'll do it.",
                           ],
        personality.Easygoing: ["I guess I could {mission}.", "Time to {mission}."
                                ],
        personality.Passionate: ["I swear to {mission}!", "I won't let you down!"
                                 ],
        personality.Sociable: ["I will do this mission.",
                               ],
        personality.Shy: ["I'll do it.", "Okay."
                          ],

    },

    "[I_WANT_YOU_TO_INVESTIGATE]": {
        Default: ["I want you to investigate this matter.", "I'd appreciate if you could go see what's going on."
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

    "[I_WILL_COME_BACK_LATER]": {
        # Speaker cannot deal with this right now, but will come back later.
        Default: ["I'll come back later.",
                  ],
        personality.Cheerful: ["No hard feelings, but I'm going to have to get back to you on that.",
                               ],
        personality.Grim: ["Hmmm... I am going to need some time to deal with this.",
                           ],
        personality.Easygoing: ["Do you mind if I get back to you on that?",
                                ],
        personality.Passionate: ["I will return later!",
                                 ],
        personality.Sociable: ["You're going to have to give me some time to think about this.",
                               ],
        personality.Shy: ["I'll be back.",
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

    "[I_worry_that]": {
        # The beginning of a sentence expressing worry about a dependent clause
        Default: ["I worry that",
                  ],
        personality.Cheerful: ["I'm not feeling optimistic that"
                               ],
        personality.Grim: ["It is inevitable that",
                           ],
        personality.Easygoing: ["I'm kinda nervous that"
                                ],
        personality.Passionate: ["I will face the danger that",
                                 ],
        personality.Sociable: ["I've heard people worrying that",
                               ],
        personality.Shy: ["It seems that",
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

    "[I_WOULD_HAVE_GOTTEN_AWAY]": {
        Default: ["I would have gotten away with it too, if not for you damn cavaliers!"
                  ],
        personality.Cheerful: ["This is not making me happy!!!",
                               "Alright, you caught me. Are you happy?"
                               ],
        personality.Grim: ["This is just my luck.",
                           ],
        personality.Easygoing: ["Oh well. It's a fair cop."
                                ],
        personality.Passionate: ["It's impossible, my plan was foolproof! How did you figure it out?"
                                 ],
        personality.Sociable: ["You may have caught me, but remember that I have powerful friends...",
                               ],
        personality.Shy: ["[SWEAR]",
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
        personality.Passionate: ["Yes, I would love to do that!", "I have been waiting for this!"
                                 ],
        personality.Sociable: ["Alright, that sounds like a good idea.",
                               ],
        personality.Shy: ["Okay.",
                          ],
    },

    "[I_WOULD_NOT_HAVE_LOST]": {
        # Taunting the other person about losing a mission or somesuch.
        Default: ["I wouldn't have lost."
                  ],
        personality.Cheerful: ["Ha! There's no way I would have gotten my arse kicked as badly as you.",
                               ],
        personality.Grim: ["That's what you deserve for overestimating your skill. I would not have made that mistake.",
                           ],
        personality.Easygoing: ["Sounds like someone is still butthurt over getting their arse kicked."
                                ],
        personality.Passionate: ["Accept your loss with dignity. I could have succeeded, where you have only failed."
                                 ],
        personality.Sociable: ["Based on what I've heard, I'm not surprised you lost. I would have done much better.",
                               ],
        personality.Shy: ["You lost. I wouldn't have.",
                          ],
    },

    "[IWillSendMissionDetails]": {
        Default: ["I'll send you the mission details",
                  ],
        personality.Cheerful: ["I just sent all the mission details to your navcomp",
                               ],
        personality.Grim: ["Pay close attention to the mission data I'm sending",
                           ],
        personality.Easygoing: ["Everything you need to know should already be uploaded to your mek",
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

    "[JOIN_REFUSAL]": {
        Default: ["Actually I'm kind of busy at the moment.",
                  "Join your [lance]? No thanks."
                  ],
        personality.Cheerful: ["I've got better things to do than join your [lance].",
                               ],
        personality.Grim: ["Blazes no. Go find someone else.",
                           ],
        personality.Easygoing: ["Nah, I don't really want to.",
                                ],
        personality.Passionate: ["I haven't forgiven you yet.",
                                 ],
        personality.Sociable: ["I'm still too upset to join your [lance].",
                               ],
        personality.Shy: ["No.",
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
        Default: ["I'll be around here if you need me again. [GOODBYE]",
                  "[OK] Come back here if you need my services again.",
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

    "[LEAVE_THIS_BATTLE]": {
        Default: [
            "Leave now while you're still alive.",
            "You have two choices- get out of here or die.",
        ],
        personality.Cheerful: [
            "Luckily enough, you can save yourself if you just turn around and go.",
        ],
        personality.Grim: [
            "To remain in this [territory] would mean certain death.",
        ],
        personality.Easygoing: [
            "If I were you, I'd get out while I still can.",
        ],
        personality.Passionate: [
            "I won't give another warning; turn around now or feel my wrath!",
        ],
        personality.Sociable: [
            "",
        ],
        personality.Shy: [
            "Leave this [territory] now.",
        ],
        LIKE: [
            "I like you, but that's not going to stop me from [defeating_you].",
        ]
    },

    "[LET_ME_GET_THIS_STRAIGHT]": {
        Default: ["Let me get this straight.",
                  ],
        personality.Cheerful: ["Humor me for a bit; I want to make sure I understand.",
                               ],
        personality.Grim: ["Are you seriously saying what I think you are?",
                           ],
        personality.Easygoing: ["Hey, I just want to make sure we're both clear about this.",
                                ],
        personality.Passionate: ["There can be no mistakes about this!"
                                 ],
        personality.Sociable: ["Let me make sure that I'm understanding you correctly."
                               ],
        personality.Shy: ["Ok, so...",
                          ],
    },

    "[LET_ME_KNOW_IF_YOU_HEAR_ANYTHING]": {
        Default: ["Let me know if you hear anything about this.",
                  ],
        personality.Cheerful: ["I'd be thrilled if you could find out something about this.",
                               ],
        personality.Grim: ["It's a long shot, but let me know if you hear anything.",
                           ],
        personality.Easygoing: ["If you hear anything about this, could you let me know?",
                                ],
        personality.Passionate: ["I must know more about this!"
                                 ],
        personality.Sociable: ["Somebody has to know more about this; please tell me if you hear anything."
                               ],
        personality.Shy: ["Let me know if you hear anything.",
                          ],
    },

    "[LETSFIGHT]": {
        Default: ["Let's fight.", "Prepare for battle.", "I will [fight_you]."
                  ],
        personality.Cheerful: ["Let's fight! This will be fun.", "It'll be fun [defeating_you].",
                               "Shall we dance?", "I can't wait to [fight_you]."
                               ],
        personality.Grim: ["Time to finish this.", "I will break you.", "I will enjoy [defeating_you].",
                           "Your story comes to an end now.", "I will teach you what it means to suffer."
                           ],
        personality.Easygoing: ["We might as well start the fight.", "Ready to go?",
                                "I'm gonna try [defeating_you], okay?", "I don't think this battle will last too long.",
                                "Might as well get this over with.", "The highlight of my day will be [defeating_you].",
                                "I think I have to [fight_you]."
                                ],
        personality.Passionate: ["Let the battle begin!", "I'll show you my true power!",
                                 "You are about to learn the true meaning of power!", "Let's fight!",
                                 "Defeat me if you can!", "Show me a real fight!", "Just see how I [fight_you]!"
                                 ],
        personality.Sociable: ["Shall we battle?", "Prepare to defend yourself.",
                               "I can't wait for everyone to see me [defeating_you].",
                               "Now I get to see if you can live up to your reputation.",
                               "I'm going to have to [fight_you] now."
                               ],
        personality.Shy: ["Let's go.", "Let's start.", "Defend yourself.",
                          "I can take you."
                          ],
        personality.Peace: ["I'm afraid I must [fight_you].",
                            ],
        personality.Justice: ["You're about to get what you deserve.",
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

    "[LETS_GET_STARTED]": {
        Default: ["Let's get started!",
                  ],
        personality.Cheerful: ["Let's get this party started!",
                               ],
        personality.Grim: ["Are you prepared for the challenges ahead? I am.",
                           ],
        personality.Easygoing: ["We can start whenever you're ready.",
                                ],
        personality.Passionate: ["Let's rev up and get to it!"
                                 ],
        personality.Sociable: ["Here we go!", "Shall we get started?"
                               ],
        personality.Shy: ["Let us begin.",
                          ],
        DISLIKE: ["I guess I don't have much choice about this.",
                  ],
        LIKE: ["I'm looking forward to getting started.",
               ]
    },

    "[LETSGO]": {
        Default: ["Let's go!",
                  ],
        personality.Cheerful: ["This will be fun!",
                               ],
        personality.Grim: ["Let's go wreck some stuff.",
                           ],
        personality.Easygoing: ["No worries, right?",
                                ],
        personality.Passionate: ["Excelsior!", "Gear up and roll out!"
                                 ],
        personality.Sociable: ["Here we go!", "Shall we get started?"
                               ],
        personality.Shy: ["Let's go.",
                          ],
        DISLIKE: ["Might as well get this over with.",
                  ],
        LIKE: ["It will be a pleasure to go with you.",
               ]
    },

    "[LETS_KEEP_THIS_A_SECRET]": {
        Default: ["Let's keep this a secret between you and me...",
                  ],
        personality.Cheerful: ["I'd be happiest if you didn't mention this to anyone else.",
                               ],
        personality.Grim: ["These are grave words; it would be best to keep them between you and I.",
                           ],
        personality.Easygoing: ["Yeah, I'd rather for people to not know about that.",
                                ],
        personality.Passionate: ["That is a secret and must remain so!",
                                 ],
        personality.Sociable: ["I think it would be best for everyone if this remained a secret between you and I.",
                               ],
        personality.Shy: ["Let's not mention this to anyone else.",
                          ],
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

    "[LISTEN_TO_MY_INFO]": {
        # The character is about to pass on some info.
        Default: ["Let me tell you about it.",
                  ],
        personality.Cheerful: ["I think you're going to find this interesting.",
                               ],
        personality.Grim: ["Remember that once you hear my tale, you will never be able to un-hear it.",
                           ],
        personality.Easygoing: ["If I remember correctly it went something like this...",
                                ],
        personality.Passionate: ["I will now tell you this vital information!",
                                 ],
        personality.Sociable: ["This might end up being a long story, but I think you'll find it worthwhile...",
                               ],
        personality.Shy: ["Here's what I know...",
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
        DISLIKE: [
            "Listen here, [audience]:"
        ],
        HATE: [
            "Listen here, you maggot:"
        ],
    },

    "[LONGTIMENOSEE]": {
        Default: ["Hello [audience], long time no see.",
                  "Long time no see, [audience].", ],
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

    "[LOOKING_FOR_CAVALIER]": {
        # The NPC has a mission for a cavalier.
        Default: [
            "I need a cavalier for an upcoming mission.",
            "I'm looking for a mecha pilot to do a mission.",
            "I have a job available for a cavalier."
        ],
        personality.Cheerful: [
            "This could be your lucky day; I'm looking to hire a cavalier...",
            "Do you want more money? Of course, we all do. Why not try this mission?",
            "Good news! I have a job opening for a pilot just like you."
        ],
        personality.Grim: [
            "I need to find a cavalier for this mission, since the last one I hired died...",
            "I need a highly skilled cavalier for a dangerous mission.",
            "I have a job available, but there's no guarantee you'll come back alive."
        ],
        personality.Easygoing: [
            "Hey, are you looking for work?",
            "I gotta find a cavalier to do a mission for me...",
            "Wanna do a mission for me?"
        ],
        personality.Passionate: [
            "I need a hot-blooded pilot for an urgent mission!",
            "There's an emergency, and I need to find a cavalier immediately!",
            "Hey, do you want to prove yourself by doing this mission?"
        ],
        personality.Sociable: [
            "I suppose you've heard that I'm looking for a pilot.",
            "I've been going through my contacts to find a skilled pilot for an upcoming mission.",
            "I should tell you that I need a pilot for an upcoming mission, if you're interested."
        ],
        personality.Shy: [
            "I'm looking for a pilot.",
            "I need a pilot to do a mission.",
            "Are you looking for a job?",
        ],
        MET_BEFORE: [
            "I know you're not someone to turn down a mission, and I have one available.",
        ],
        LOVE: [
            "I've got a mission contract and you'd be the perfect cavalier for the job."
        ],
        LIKE: [
            "I think you'd be an ideal pilot for the mission I have."
        ],
        DISLIKE: [
            "I've been searching for a competent mecha pilot but I guess you could do this mission too.",
        ],
        personality.Glory: [
            "Fame and riches await any cavalier who can complete my mission!",
            "You look like you're up for a challenge; I have a mission available...",
        ],
        personality.Duty: [
            "I need a responsible pilot to carry out this mission.",
            "I have a mission for a dependable cavalier.",
        ],
        personality.Fellowship: [
            "Could you help me out by doing a mission?",
            "It'd be a great help to me if you could do this job..."
        ],
        personality.Peace: [
            "Are you willing to fight for peace?",
        ],
        tags.Adventurer: [
            "Looking for adventure? Do I have a job for you!",
        ],
        tags.Military: [
            "I need a soldier for an upcoming operation.",
        ],
    },

    "[Luna]": {
        Default: ["Luna", ],
        personality.GreenZone: ["the moon", "the moon", ],
        personality.DeadZone: ["the moon", "the moon", "the moon", ],
    },

    "[MAYBE_YOU_ARE_RIGHT]": {
        Default: ["Maybe you're right."
                  ],
        personality.Cheerful: ["I'm glad to admit I could be wrong.",
                               ],
        personality.Grim: ["It appears that you may be right about this...",
                           ],
        personality.Easygoing: ["Yeah, probably.",
                                ],
        personality.Passionate: ["I am willing to admit you could be right!",
                                 ],
        personality.Sociable: ["I suppose it's possible that you're right about this.",
                               ],
        personality.Shy: ["Maybe.",
                          ],
    },

    "[MAYBE_YOU_ARE_RIGHT_ABOUT_OPINION]": {
        # data block must include "opinion"
        Default: ["Maybe you're right; {opinion}.", "[MAYBE_YOU_ARE_RIGHT]"
                  ],
        personality.Cheerful: ["So really {opinion}?",
                               ],
        personality.Grim: ["It appears I've misjudged things horribly; {opinion}.",
                           ],
        personality.Easygoing: ["So {opinion}? Sounds legit.",
                                ],
        personality.Passionate: ["Could it be? {opinion}!",
                                 ],
        personality.Sociable: ["You may very well be right that {opinion}.",
                               ],
        personality.Shy: ["So, {opinion}.",
                          ],
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

    "[MEDICAL_GREETING]": {
        Default: ["And how are you feeling today?"
                  ],
        personality.Cheerful: ["You appear to be in good health today.",
                               ],
        personality.Grim: [
            "Don't forget to schedule a regular checkup; that's the only way to catch serious problems before they become terminal problems.",
            "Good to see that you're still alive."
        ],
        personality.Easygoing: [
            "And how can I help you today?", "Being ill is worse than a [adjective] [noun]."
        ],
        personality.Passionate: ["Remember- take care of your body, since it's all you have in this world!"
                                 ],
        personality.Sociable: ["Is there anything you'd like to speak with me about?",
                               ],
        personality.Shy: ["If you aren't feeling well I'll get you some forms to fill out."
                          ],
        personality.Glory: [
            "I have a wide supply of pharmaceuticals that could come in handy on your next mission.",
        ],
        personality.Duty: [
            "I will do everything in my power to ensure your good health.",
        ],
        personality.Peace: [
            "Health is the best thing a person can have; that's why we work so hard to protect it."
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

    "[MY_MECHA_WAS_DESTROYED]": {
        Default: ["My mecha was destroyed...", "I lost my mecha..."
                  ],
        personality.Cheerful: ["Saying goodbye to my old mek makes me sad...",
                               ],
        personality.Grim: ["All things eventually die, even meks."
                           ],
        personality.Easygoing: ["Guess my mecha isn't coming back from this one."
                                ],
        personality.Passionate: ["No!!! My mecha was demolished! This cannot be...",
                                 ],
        personality.Sociable: ["I guess everybody loses their mecha sometimes...",
                               ],
        personality.Shy: ["My mek is gone.",
                          ],
        tags.Military: [
            "My mecha served me well; it rests in a place of honor."
        ],
        tags.Adventurer: [
            "When my mecha was destroyed, it felt like part of me was too..."
        ],
        tags.Craftsperson: [
            "I did my best to save my mecha, but sometimes there's nothing you can do."
        ],
        tags.Criminal: [
            "Guess I should be happy that all the evidence on my mecha's compsys has been destroyed..."
        ],
        tags.Faithworker: [
            "Let us pray for the machine spirit of my departed mecha."
        ],
        tags.Media: [
            "I hope no-one got a video of my mecha getting blown up out there..."
        ],
        tags.Medic: [
            "I know it was an unfeeling machine, but I mourn the death of my mecha."
        ],
        tags.Academic: [
            "The data I gained from losing my mecha will hopefully help me to not lose my next one."
        ],
        personality.Duty: [
            "I have no-one but myself to blame for the loss of my mecha."
        ],
        personality.Glory: [
            "I need to improve my skills so next time I won't lose my mecha so easily."
        ]
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
            "Hominid", "Underwear", "Paluke", "Artifice", "Lie", "Knowledge", "Battle", "Weather", "Food", "News",
            "Mecha", "Fashion", "Athlete", "Music", "Politics", "Religion", "Love", "War", "History",
            "Technology", "Time", "Internet", "Literature", "Destiny", "Romance", "Base", "Stuff", "Agriculture",
            "Sports", "Science", "Television", "Atmosphere", "Sky", "Color", "Sound", "Taste", "Friendship", "Law",
            "Beer", "Singing", "Cola", "Pizza", "Vaporware", "Buzz", "Mood", "Dissent", "City", "House", "Town",
            "Village", "Country", "Planet", "Fortress", "Universe", "Program", "Arena", "Wangtta", "Hospital",
            "Medicine", "Therapy", "Library", "Education", "Philosophy", "Family", "Jive", "Feel", "Coffee",
            "Hope", "Hate", "Love", "Fear", "Sale", "Life", "Market", "Enemy", "Data", "Fish", "Beast",
            "Something", "Everything", "Nothing", "Sabotage", "Justice", "Fruit", "Pocket", "Parfait", "Flavor",
            "Talent", "Prison", "Plan", "Noise", "Bottom", "Force", "Anything", "Top", "Appeal", "Booster",
            "Complaint", "Chatting", "Dream", "Heart", "Secret", "Fauna", "Desire", "Situation", "Risk",
            "Crime", "Vice", "Virtue", "Treasure", "Storm", "Vapor", "School", "Uniform", "World", "Body",
            "Pain", "Fault", "Profit", "Business", "Prophet", "Animal", "Bedroom", "Kitchen", "Home", "Apartment",
            "Vehicle", "Machine", "Bathroom", "Fruit", "Side", "Entertainment", "Movie", "Game", "Chemistry",
            "Synergy", "Opinion", "Hero", "Villain", "Thief", "Fantasy", "Adventure", "Mission", "Job",
            "Career", "Glamour", "Diary", "Expression", "Hairdo", "Environment", "Wizard", "Drug"
        ]
    },
    "[noun]": {
        Default: [
            "[instrument]", "underwear", "paluke", "artifice", "lie", "knowledge", "battle", "weather", "food", "news",
            "mecha", "fashion", "soccer competition", "music", "politics", "religion", "love", "war", "history",
            "technology", "time", "internet", "literature", "destiny", "romance", "base", "stuff", "agriculture",
            "sports", "science", "television", "atmosphere", "sky", "color", "sound", "taste", "friendship", "law",
            "beer", "singing", "cola", "pizza", "vaporware", "buzz", "mood", "dissent", "city", "house", "town",
            "village", "country", "planet", "fortress", "universe", "program", "arena", "wangtta", "hospital",
            "medicine", "therapy", "library", "education", "philosophy", "family", "jive", "feel", "coffee",
            "hope", "hate", "love", "fear", "sale", "life", "market", "enemy", "data", "fish", "lion taming",
            "something", "everything", "nothing", "sabotage", "justice", "fruit", "pocket", "parfait", "flavor",
            "talent", "prison", "plan", "noise", "bottom", "force", "anything", "top", "appeal", "booster",
            "complaint", "chatting", "dream", "heart", "secret", "fauna", "desire", "situation", "risk",
            "crime", "vice", "virtue", "treasure", "storm", "vapor", "school", "uniform", "world", "body",
            "pain", "fault", "profit", "business", "prophet", "animal", "bedroom", "kitchen", "home", "apartment",
            "vehicle", "machine", "bathroom", "fruit", "side", "entertainment", "movie", "game", "chemistry",
            "synergy", "opinion", "hero", "villain", "thief", "fantasy", "adventure", "mission", "job",
            "career", "glamour", "diary", "expression", "hairdo", "environment", "wizard", "drug"

        ]
    },

    "[object_pronoun]": {
        Default: [
            "him", "her", "zem"
        ]
    },

    "[OF_COURSE]": {
        Default: ["Of course.",
                  ],
        personality.Cheerful: ["Absolutely!",
                               ],
        personality.Grim: ["What do you think?",
                           ],
        personality.Easygoing: ["No problem."
                                ],
        personality.Passionate: ["That is a certainty!",
                                 ],
        personality.Sociable: ["But of course.",
                               ],
        personality.Shy: ["OK.",
                          ],
        DISLIKE: ["Yeah, I guess...",
                  ],
        LIKE: ["As you say.",
               ]
    },

    "[OK]": {
        # A not necessarily enthusiastic agreement or assent...
        Default: ["Okay.", "Alright."
                  ],
        personality.Cheerful: ["Okay!", "Good enough."
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

    "[OnSecondThought]": {
        Default: ["On second thought", "On the other hand"
                  ],
        personality.Cheerful: ["I just had a better idea",
                               ],
        personality.Grim: ["I think I have erred",
                           ],
        personality.Easygoing: ["Uh", "Er"
                                ],
        personality.Passionate: ["I have changed my mind",
                                 ],
        personality.Sociable: ["Something just occurred to me",
                               ],
        personality.Shy: ["Well",
                          ],
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
        personality.Easygoing: [
            "If you can't find what you're looking for today, remember that it might be here tomorrow.",
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

    "[OPEN_TO_PEACE_WITH_ENEMY_FACTION]": {
        # Data block should include enemy_faction
        Default: ["I am open to peace with {enemy_faction}."
                  ],
        personality.Cheerful: ["It would be a happy day if {enemy_faction} agreed to a peace deal.",
                               ],
        personality.Grim: [
            "Do you really think {enemy_faction} is open to peace? I would agree, but I doubt that'll happen.",
        ],
        personality.Easygoing: ["Yeah, if {enemy_faction} accepted a peace deal, that'd make life easier for everyone.",
                                ],
        personality.Passionate: ["You expect us to lay down our arms?! Only if {enemy_faction} agrees first!",
                                 ],
        personality.Sociable: [
            "We would be willing to consider peace with {enemy_faction}, if they were willing to accept."
        ],
        personality.Shy: ["I would accept a treaty with {enemy_faction}.",
                          ],
        personality.Peace: [
            "Of course I want peace with {enemy_faction}!"
        ],
    },

    # The data block should include "subject"; if not a proper noun, subject should have "the".
    "[OPINION:OPINION]": {
        Default: ["In that case, what do you think about {subject}?",
                  "So how do you feel about {subject}?"
                  ],
        personality.Cheerful: [
            "I'd also love to hear your thoughts on {subject}.",
        ],
        personality.Grim: [
            "Well where does that leave {subject}?",
        ],
        personality.Easygoing: [
            "Neat. So do you feel the same about {subject}?",
        ],
        personality.Passionate: [
            "So, you must hold a different view about {subject}!",
        ],
        personality.Sociable: [
            "I see; so how do you feel about {subject}, then?",
        ],
        personality.Shy: [
            "What about {subject}, then?",
        ],
    },

    "[pc]": {
        relationships.A_JUNIOR: [
            "Boss"
        ],
        relationships.R_CREATION: [
            "Creator",
        ],
        relationships.RT_FAMILY: [
            "Cuz"
        ],
        relationships.R_ADVERSARY: [
            "[blockhead]",
        ],
        relationships.R_NEMESIS: [
            "[blockhead]", "my arch-enemy"
        ],
        relationships.A_DISRESPECT: [
            "[blockhead]",
        ]
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
        personality.Sociable: [
            "May I just say what a pleasure it is to come to an agreement with a true professional like you.",
        ],
        personality.Shy: ["So it's agreed.",
                          ],
    },

    "[PRETEXT_FOR_GOING_THERE]": {
        # When the PC or someone else needs an excuse for going somewhere.
        Default: ["I am supposed to deliver a package there."
                  ],
        personality.Cheerful: ["Someone ordered a pizza, and I'll get in trouble if it doesn't arrive in 30 minutes.",
                               ],
        personality.Grim: ["I have important business there; you don't want to be the one responsible for making me late."
                           ],
        personality.Easygoing: ["We're having a Pony Pusher card game tournament. You're welcome to join us."
                                ],
        personality.Passionate: ["I have legitimate reasons for going there!!!",
                                 ],
        personality.Sociable: ["I've been invited by the commander for some highly delicate negotiations.",
                               ],
        personality.Shy: ["I have business there.",
                          ],
        tags.Craftsperson: [
            "Apparently the toilets aren't working and I've been hired to repair them.",
        ],
        tags.Laborer: [
            "I've been hired to fix some cracks in the wall. Whoever did the original work didn't know what they were doing.",
        ],
        tags.Faithworker: [
            "I will be holding a 3AM service for the faithful. You are more than welcome to attend."
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
        Default: ["I don't think so.", "I will come back later."
                  ],
        personality.Cheerful: ["No for now, but maybe later.",
                               ],
        personality.Grim: ["No.", "Absolutely not."
                           ],
        personality.Easygoing: ["I need some time to think about this.", "Maybe later? I can't now..."
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
        personality.Cheerful: ["This is a good day to go shopping.",
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
        personality.Grim: [
            "They say we need to tighten our belts, but how can you do that when you're already starving?",
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
        personality.Sociable: [
            "You probably haven't heard about me before, because I don't have a lot of experience...",
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
            "your satisfaction", "something", "a great selection"
        ]
    },

    "[shop_features]": {
        Default: [
            "the lowest prices", "happy customers", "great deals", "friendly staff", "[adjective] products"
        ]
    },

    "[shop_descriptive_phrase]": {
        Default: [
            "our legal obligation", "a happy accident", "an unexpected surprise", "possible", "everything",
            "better than a [noun]", "the law", "truly [adjective]", "job one", "mandatory", "not impossible",
            "relatively likely", "guaranteed"
        ]
    },

    "[SORRY_I_CANT]": {
        # Speaker is responding in the negative to a request.
        Default: ["Sorry, I can't.",
                  ],
        personality.Cheerful: ["Sadly, I can't do that.",
                               ],
        personality.Grim: ["I hate to admit that I can't.",
                           ],
        personality.Easygoing: ["I don't think I can do that.",
                                ],
        personality.Passionate: ["No, I can't!",
                                 ],
        personality.Sociable: ["I'm afraid that I can't do that right now.",
                               ],
        personality.Shy: ["No, I can't.",
                          ],
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

    "[SURRENDER_TO_FACTION]": {
        # data needs "faction"
        Default: ["Surrender to {faction} at once!",
                  "Your only hope is to surrender to {faction}."
                  ],
        personality.Cheerful: ["It's your lucky day; {faction} is willing to let you surrender."
                               ],
        personality.Grim: ["You have just one chance to survive, and that is to surrender to {faction}.",
                           ],
        personality.Easygoing: ["It'd be a lot easier for everyone if you just surrendered to {faction}.",
                                ],
        personality.Passionate: ["You can surrender to {faction}, or be crushed without mercy!",
                                 ],
        personality.Sociable: ["I demand right now that you surrender to {faction}!",
                               ],
        personality.Shy: ["Surrender to {faction}.",
                          ],
    },

    "[SWEAR]": {
        Default: ["Well [expletive] on that...", "Oh [expletive]!",
                  "[God] smite it!"
                  ],
    },

    "[REALLY?]": {
        Default: ["Really?", "Is that so?"
                  ],
        personality.Cheerful: ["[HAGOODONE]"
                               ],
        personality.Grim: ["You can't seriously believe that.",
                           ],
        personality.Easygoing: ["Are you being serious?",
                                ],
        personality.Passionate: ["I don't think so.",
                                 ],
        personality.Sociable: ["And, this is something you actually believe?",
                               ],
        personality.Shy: ["Huh.",
                          ],
    },

    "[territory]": {
        # Another word for land that belongs to us, from the speaker's point of view.
        Default: [
            "territory", "land", "area", "region"
        ],
        tags.Criminal: [
            "turf",
        ],
        tags.CorporateWorker: [
            "property",
        ],
        personality.DeadZone: [
            "stomping ground",
        ],
        tags.Academic: [
            "zone",
        ]
    },

    "[THANK_YOU]": {
        # A simple thank you is appropriate.
        Default: ["Thank you.", "Thanks."
                  ],
    },

    "[THANK_GOODNESS_YOU_ARE_ALIVE]": {
        Default: ["Thank goodness you're alive.", "Thank goodness you're okay."
                  ],
        personality.Cheerful: ["I knew you wouldn't die that easily!"
                               ],
        personality.Grim: ["I thought you were dead...",
                           ],
        personality.Easygoing: ["Hey, you made it!",
                                ],
        personality.Passionate: ["Thank [God] that you're still alive!",
                                 ],
        personality.Sociable: ["[audience]! They said that you were dead.",
                               ],
        personality.Shy: ["You're alive!",
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
        personality.Cheerful: ["I'm glad you decided to help out; thanks!", "That went well. Thanks!"
                               ],
        personality.Grim: ["I guess I should thank you.", "That could have gone a lot worse; thank you."
                           ],
        personality.Easygoing: ["Thanks.", "Hey, thanks for helping me out.",
                                ],
        personality.Passionate: ["Thank you!!!", "Thank you so much!",
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

    "[THAT_IS_A_SERIOUS_ALLEGATION]": {
        # Character reacts to a serious allegation with gravitas but caution.
        Default: [
            "That is a serious allegation.",
            "That is important news, if true."
        ],
        personality.Cheerful: [
            "This is not the sort of thing you ought to joke about.",
        ],
        personality.Grim: [
            "If what you say is true, this could be a disaster.",
        ],
        personality.Easygoing: [
            "Is that so? Interesting.",
        ],
        personality.Passionate: [
            "What?! I can't believe it... but I can't deny it, either."
        ],
        personality.Sociable: [
            "Who told you that?! This could be very serious.",
        ],
        personality.Shy: [
            "I see.",
        ],
        personality.Peace: [
            "This is disturbing news.",
        ],
        personality.Glory: [
            "It's a good thing you brought this to me; it may not be too late.",
        ],
        personality.Justice: [
            "Do you have proof? We must discern the truth of this matter.",
        ],
        personality.Duty: [
            "I can hardly believe it, but must take your words seriously.",
        ],
        personality.Fellowship: [
            "This news could tear us apart.",
        ],
        tags.Police: [
            "An investigation must begin at once.",
        ]
    },

    "[THAT_IS_FUNNY]": {
        Default: [
            "Ha! That's funny.", "Really? That's hilarious."
        ],
        personality.Cheerful: [
            "BWA HA HA!!!", "ROFL!!!", "OMG WOW LMAO!"
        ],
        personality.Grim: [
            "Heh... that is amusing.",
        ],
        personality.Easygoing: [
            "Ha!", "This brings a smile to my face."
        ],
        personality.Passionate: [
            "Just a minute... BWAA HA HA HA BWA HA HA!!!",
        ],
        personality.Sociable: [
            "Oh, that's funny. I can't wait to tell everyone about this.",
        ],
        personality.Shy: [
            "Amusing.",
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
            "That's the best news!", "Excelsior!"
        ],
        personality.Sociable: [
            "I'm glad to hear that.",
        ],
        personality.Shy: ["Good.",
                          ],
        DISLIKE: ["Okay, I guess..."],
        LIKE: ["Fantastic!"]
    },

    "[THATS_GREAT]": {
        # Character reacts to *very* good news.
        Default: ["Very good!",
                  "That's great!", "[THATS_GOOD]"
                  ],
        personality.Cheerful: [
            "Very nice!",
        ],
        personality.Grim: ["Huh, I did not see that coming.",
                           ],
        personality.Easygoing: [
            "Neat-o!",
        ],
        personality.Passionate: [
            "That's amazing!", "Absolutely blazing fantastic!"
        ],
        personality.Sociable: [
            "You don't know how glad I am to hear that!",
        ],
        personality.Shy: ["Good to know!",
                          ],
        LOVE: ["That's such great news I could kiss you!",],
        LIKE: ["Thank you so much for letting me know!"]
    },

    "[THATS_INTERESTING]": {
        # Character reacts to interesting news.
        Default: ["Very interesting.",
                  "This is interesting."
                  ],
        personality.Cheerful: [
            "Oh, cool!",
        ],
        personality.Grim: ["Fascinating.", "Important news, if true."
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

    "[THATS_RIGHT]": {
        # Character confirms an assertion.
        Default: ["That's right.",
                  "That's correct."
                  ],
        personality.Cheerful: [
            "Right you are!",
        ],
        personality.Grim: [
            "Yes, that's true.",
        ],
        personality.Easygoing: [
            "Yeah, you're right.",
        ],
        personality.Passionate: [
            "You speak the truth!",
            "It's a fact!",
        ],
        personality.Sociable: [
            "You heard correct.",
        ],
        personality.Shy: [
            "You are correct.",
        ],
        DISLIKE: ["Yeah, I have to admit you're right..."],
    },

    "[THATSUCKS]": {
        Default: ["Too bad.", "[SWEAR]"
                  ],
        personality.Cheerful: [
            "Aww..."
        ],
        personality.Grim: ["Ashes.", "Blazes.",
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

    "[THAT_WAS_INCREDIBLE]": {
        # Praise incredible performance
        Default: ["That was incredible!"
                  ],
        personality.Cheerful: [
            "You were amazing!"
        ],
        personality.Grim: ["Can't complain about that!",
                           ],
        personality.Easygoing: ["You did pretty good, I think!",
                                ],
        personality.Passionate: [
            "Yes! Yes! Ha ha ha!",
        ],
        personality.Sociable: [
            "You really did a wonderful job with that.",
        ],
        personality.Shy: ["Incredible work.",
                          ],
    },

    "[THAT_WAS_THE_WORST]": {
        # Criticize bad performance
        Default: ["That was the worst!"
                  ],
        personality.Cheerful: [
            "You have made me sad."
        ],
        personality.Grim: ["That has to be one of the worst things I've ever seen.",
                           ],
        personality.Easygoing: ["I don't want to say you suck, but right now? You suck.",
                                ],
        personality.Passionate: [
            "You have failed in the greatest possible sense of the word.",
        ],
        personality.Sociable: [
            "When word of your failure gets around, it's going to destroy your rep.",
        ],
        personality.Shy: ["You did a bad thing.",
                          ],
        LIKE: [
            "I know you tried your best, but that was not good."
        ],
        DISLIKE: [
            "And as expected, you blew it."
        ]
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
        personality.Grim: [
            "[HOLD_ON] I've been picking up signs of enemy activity for a while now. We're almost on top of them.",
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
        personality.Duty: [
            "[LOOK_AT_THIS] I've been keeping an eye out for signs of enemy movement, and this is it. They must be close now.",
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

    "[THINK_ABOUT_THIS]": {
        # The speaker needs a moment to collect their thoughts.
        Default: ["Let me think about this for a moment..."
                  ],
        personality.Cheerful: [
            "Well, you know, that's a real puzzle."
        ],
        personality.Grim: ["This is something I must consider seriously.",
                           ],
        personality.Easygoing: ["Umm... Just a sec.",
                                ],
        personality.Passionate: [
            "The answer to this is somewhere in my mind!",
        ],
        personality.Sociable: [
            "I'm going to have to think about things for a minute.",
        ],
        personality.Shy: ["Let me think.",
                          ],
    },

    "[THIS_AREA_IS_UNDER_OUR_CONTROL]": {
        Default: [
            "This [territory] is under our control.",
            "This [territory] is controlled by [speaker_faction].",
            "You have intruded on the [territory] of [speaker_faction]."
        ],
        personality.Cheerful: [
            "I don't have the signs up yet, but this is our [territory].",
            "I know our name's not marked on it, but this [territory] belongs to [speaker_faction]."
        ],
        personality.Grim: [
            "You have crossed into a forbidden area.",
            "This [territory] belongs to [speaker_faction]; you are an intruder."
        ],
        personality.Easygoing: [
            "I don't think you belong here.",
            "So [speaker_faction] told me to keep folks like you out."
        ],
        personality.Passionate: [
            "How dare you intrude unto our [territory]?!",
            "You are not of [speaker_faction]; this [territory] is ours!"
        ],
        personality.Sociable: [
            "It's my job to keep unauthorized people like you out of our [territory].",
        ],
        personality.Shy: [
            "You should not be here.",
        ],
    },

    "[THIS_CANNOT_BE_ALLOWED]": {
        # The NPC has just been informed that someone is breaking the rules.
        Default: ["This cannot be allowed."
                  ],
        personality.Cheerful: [
            "Well, I guess someone really wants to get punished!"
        ],
        personality.Grim: ["They have crossed the line that must not be crossed.",
                           ],
        personality.Easygoing: ["You know, you wouldn't think it'd be hard to just follow the rules...",
                                ],
        personality.Passionate: [
            "They have violated the pact! They must be made to pay.",
        ],
        personality.Sociable: [
            "I should have known they would try something like this.",
        ],
        personality.Shy: ["I see.",
                          ],
    },

    "[THIS_IS_AN_EMERGENCY]": {
        # The NPC is going to tell the PC about an emergency.
        Default: ["This is an emergency."
                  ],
        personality.Cheerful: [
            "Bad news- this is an emergency."
        ],
        personality.Grim: ["Something terrible is happening...",
                           ],
        personality.Easygoing: ["I don't want to worry you, but we have a bit of an emergency...",
                                ],
        personality.Passionate: [
            "Red alert- we have an emergency to deal with!",
        ],
        personality.Sociable: [
            "We've got an emergency on our hands!",
        ],
        personality.Shy: ["This could be trouble.",
                          ],
    },

    "[THIS_IS_A_SECRET]": {
        # The NPC is about to reveal something they probably shouldn't...
        Default: ["This is a secret, but...", "Remember, you didn't hear this from me..."
                  ],
        personality.Cheerful: ["I'm not one to gossip, but... who am I kidding? I love to gossip!",
                               ],
        personality.Grim: [
            "What I'm about to tell you is one of those things most people know better than to speak about.",
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
        personality.Duty: ["You have done well to report this terrible news.",
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

    "[THIS_WILL_BE_DEALT_WITH]": {
        # The NPC will deal with a problem.
        Default: ["This will have to be dealt with."
                  ],
        personality.Cheerful: [
            "I'll make sure this problem gets dealt with."
        ],
        personality.Grim: ["I will deal with this; you no longer have to concern yourself.",
                           ],
        personality.Easygoing: ["I guess I should get somebody to do something about that.",
                                ],
        personality.Passionate: [
            "This problem will be dealt with immediately!",
        ],
        personality.Sociable: [
            "I know some people who can deal with this problem for us.",
        ],
        personality.Shy: ["It will be dealt with.",
                          ],
    },

    "[threat]": {
        Default: ["rend you limb from limb",
                  "mop the floor with you", "defeat you", "humiliate you",
                  "beat you", "fight you", "destroy you", "demolish you",
                  "wreck you", "obliterate you", "spank your monkey",
                  "spank you", "kill you", "murder you", "knock your clock",
                  "knock you down", "make you wish you were never born",
                  "make you beg for mercy", "make you beg for death",
                  "stop you", "break you", "make you cry", "make you scream",
                  "eviscerate you", "snap your neck", "crush your bones",
                  "take you down", "crush you", "crush you like a bug",
                  "squash you", "squash you like a grape", "cut you to pieces",
                  "pound you", "injure you terribly", "beat you black and blue",
                  "give you a thorough ass-kicking", "kick your ass",
                  "kick your behind", "kick your butt", "slap you around",
                  "send you to the hospital", "be your worst nightmare",
                  "wreck your plans", "raise a little hell", "rant and roar",
                  "open a can of whoop-ass", "do my limit break",
                  "rage like a rabid wolverine", "get violent", "get VERY violent",
                  "power up", "go berserk", "show you my true skills",
                  "demonstrate my fighting power", "show you how strong I am",
                  "fight like a demon", "show no mercy", "fight dirty",
                  "hold back nothing", "call upon my warrior spirit",
                  "boot your head", "snap you like a twig", "ruin your day",
                  "shred you", "send you to oblivion", "send you up the bomb",
                  ],
    },

    "[THREATEN]": {
        Default: ["I'm going to [threat]!", "I will [threat]!",
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
        personality.Grim: ["So I see.", "[THATSUCKS]"
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

    "[VAGUE_MISSION_DESCRIPTION]": {
        # You're being offered a mission of some sort. I dunno. Take it or leave it.
        Default: [
            "Our team has reported some problems in the field; [your_job] solve the issue.",
            "There is a matter which requires the attention of a cavalier; [You_have_the_needed_skills].",
        ],
        personality.Cheerful: [
            "This mission could really be a lot of fun for you.",
            "If you could sort out the problems we've been having that would look really good on your record.",
        ],
        personality.Grim: [
            "You will not be the first cavalier we sent to sort this out; [You_have_the_needed_skills].",
            "The previous troubleshooters did not return from this mission. [your_job] do better than them.",
        ],
        personality.Easygoing: [
            "I don't remember all the details but you'll be doing some kind of cavalier work.",
            "This should be a nice, straightforward mission. [You_have_the_needed_skills].",
        ],
        personality.Passionate: [
            "There are people out there who wish to see our enterprise fail; [your_job] deal with them",
            "This mission will be a brilliant opportunity to show the world your prowress!",
        ],
        personality.Sociable: [
            "The details surrounding this mission are kind of sensitive; as a cavalier, I'm sure you're familiar with such things.",
            "I've been reviwing the case files of local cavaliers. [You_have_the_needed_skills].",
        ],
        personality.Shy: [
            "This should be a pretty standard mission.",
            "This mission is pretty straightforward."
        ],
    },

    "[vanquished]": {
        Default: ["vanquished", "defeated", "wiped out", "subjugated", "overwhelmed", "conquered", "trounced",
                  "annihilated", "subdued", "crushed", "demolished", "destroyed", "slaughtered"
                  ],
    },

    "[WAITINGFORMISSION]": {
        # Waiting for a mission.
        Default: ["I'm just waiting for my next mission."
                  ],
        personality.Cheerful: [
            "The time spent waiting between missions is like a mini-vacation, when you think about it."
        ],
        personality.Grim: ["I'm just temporarily unemployed. I'll find another mission soon.",
                           ],
        personality.Easygoing: ["I should probably be out there looking for a new mission, but whatever...",
                                ],
        personality.Passionate: [
            "I am currently between missions, but must remain ever vigilant. There could be an emergency at any time.",
        ],
        personality.Sociable: [
            "You wouldn't know of any mission openings, would you? I am between contracts at the moment.",
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

    "[WE_ARE_DOOMED]": {
        Default: ["We are doomed.", "All hope is lost."
                  ],
        personality.Cheerful: [
            "I can't see any way for this to have a happy ending."
        ],
        personality.Grim: ["Nothing can save us now.",
                           "There is nothing left for us to do but die.",
                           ],
        personality.Easygoing: ["I hate to say it, but we might be doomed.",
                                ],
        personality.Passionate: [
            "All hope is lost, but at least we can die dramatically!",
        ],
        personality.Sociable: [
            "Is there no-one left to save us now?",
        ],
        personality.Shy: ["We're done for.",
                          ],
    },

    "[WE_ARE_IN_DANGER]": {
        # The NPC expresses the danger of the current situation. Useful for lancemates.
        Default: ["This is bad news.", "I think we're in danger..."
                  ],
        personality.Cheerful: [
            "I think we might be in trouble..."
        ],
        personality.Grim: ["This could be the end of us...",
                           "We might not be making it out of this one...",
                           ],
        personality.Easygoing: ["I don't want to worry you, but we may be in danger now...",
                                ],
        personality.Passionate: [
            "This is peril! Danger! A truly worthy challenge!",
        ],
        personality.Sociable: [
            "We are almost certainly in grave danger right now...",
        ],
        personality.Shy: ["This is bad.",
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
        personality.Shy: ['We meet again.', "I've been expecting you.",
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

    "[WE_SHOULD_HAVE_HELPED_THEM]": {
        # A lancemate disagrees with the PC's decision to not aid someone.
        Default: ["We should have helped them."
                  ],
        personality.Cheerful: ["I'm not happy about your decision.",
                               ],
        personality.Grim: ["I can't believe you'd just abandon someone like that.",
                           ],
        personality.Sociable: ["Let's hope that no-one hears about this.",
                               ],
        personality.Shy: ["It may be none of my business, but I think we should have helped them.",
                          ],
        personality.Easygoing: ["Wow. I didn't expect you to just give up like that.",
                                ],
        personality.Passionate: ["[audience]! How could you refuse someone in need?",
                                 ],
        personality.Duty: [
            "It's a cavalier's duty to help people in need, whoever they are.",
        ],
        personality.Fellowship: [
            "What good is it being a cavalier if you aren't even going to help people who need it?",
        ],
        personality.Glory: [
            "It's your decision, but I really don't like passing up on a good fight.",
        ],
        personality.Peace: [
            "Cavaliers are supposed to protect people. We really should have helped them.",
        ],
        personality.Justice: [
            "Hopefully if we ever need help, we won't be abandoned.",
        ],
    },

    "[WHAT_ARE_YOU_DOING]": {
        # An expression of incredulity at the audience's actions (or lack thereof)
        Default: [
            "What are you doing?!", "[Hey] what do you think you're doing?"
        ],
        personality.Cheerful: [
            "Are you trying to be funny right now?",
            "Did you misplace your brain this morning?",
        ],
        personality.Grim: [
            "What the blazes, [audience]?!",
            "Is that the best you can do?!",
        ],
        personality.Easygoing: [
            "Um, excuse me, but what do you think you're doing?",
            "Are you... is that all you're going to do?!"
        ],
        personality.Passionate: [
            "[Hey] what the blazes are you doing?!",
            "Come on, [audience], you need to do better than that!"
        ],
        personality.Sociable: [
            "Explain to me, [audience], what exactly you think you're doing...",
            "Please help me to understand what you are doing..."
        ],
        personality.Shy: [
            "What the what?!", "Huh?!", "Um..."
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

    "[WHAT_SHOULD_I_DO_NEXT]": {
        # The PC seeks guidance on what they are supposed to be doing.
        Default: ["What should I do next?",
                  ],
        personality.Cheerful: ["This is fun! So what's the next part of my quest?",
                               ],
        personality.Grim: ["What's the next thing I have to blow up?",
                           ],
        personality.Easygoing: ["Could you remind me what I'm supposed to be doing?",
                                ],
        personality.Passionate: ["I seek guidance in what to do next...",
                                 ],
        personality.Sociable: ["Sorry, but what am I supposed to be doing now, exactly?",
                               ],
        personality.Shy: ["What's my next task?",
                          ],
    },

    "[WHY_SHOULD_I]": {
        # A suggestion has been made which the speaker finds unreasonable.
        Default: ["Why should I?",
                  ],
        personality.Cheerful: ["[HAGOODONE]",
                               ],
        personality.Grim: ["Your suggestion fills me with disgust.",
                           ],
        personality.Easygoing: ["No, I don't think so.",
                                ],
        personality.Passionate: ["And why the blazes should I?!",
                                 ],
        personality.Sociable: ["I'm afraid I don't understand why you would suggest that.",
                               ],
        personality.Shy: ["Why?",
                          ],
    },

    "[WILL_YOU_AVENGE_ME]": {
        # The NPC will ask the PC to avenge something. Probably not their death, since they're still talking.
        Default: ["Will you avenge me?"
                  ],
        personality.Cheerful: ["It'd really cheer me up if you could go avenge me."
                               ],
        personality.Grim: ["I have failed, but you can make sure this tragedy does not go unavenged!",
                           ],
        personality.Easygoing: ["I don't suppose you'd be able to go avenge this mess?",
                                ],
        personality.Passionate: ["And now, only you are capable of avenging me!",
                                 ],
        personality.Sociable: [
            "This is an insult that must not go unpunished; will you take up the cause and avenge me?",
        ],
        personality.Shy: ["Please avenge me.",
                          ],
    },

    "[WILL_YOU_HELP]": {
        Default: ["Will you help me?", "Can you help out?"
                  ],
        personality.Cheerful: ["It's be super if you could help with this."
                               ],
        personality.Grim: ["I know you have your own problems, but I need your help.",
                           ],
        personality.Easygoing: ["No pressure, but it'd be a big deal if you could help.",
                                ],
        personality.Passionate: ["You are the only one who can do this! Will you aid me?!",
                                 ],
        personality.Sociable: [
            "I'd really appreciate it if you could help us.", "Would you consider helping us?"
        ],
        personality.Shy: ["Please help.",
                          ],
        tags.Faithworker: [
            "It would please [God] if you could help.",
        ],
    },

    "[WITHDRAW]": {
        # The PC is withdrawing from combat.
        Default: ["Off with you, then.", "Don't return to this place."
                  ],
        personality.Cheerful: ["[GOODBYE] Remember, we don't like visitors right here.",
                               "Ding-dong-deng, that's the right answer! [GOODBYE]"
                               ],
        personality.Grim: ["Good, you choose to live.", "Come back again and I will [threat].",
                           ],
        personality.Easygoing: ["No worries. See you around.", "Yeah, I think that'd be easiest for both of us.",
                                ],
        personality.Passionate: ["Too bad; I was looking forward to [defeating_you].",
                                 "I can tell you wouldn't have been a true challenge anyhow.",
                                 ],
        personality.Sociable: ["Alright, I'll see you later... just not around here, okay?",
                               "We really ought to put up some signs on the perimeter, keep people like you from wandering in. [GOODBYE]",
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
        personality.Easygoing: ["Okay.", "Alright.",
                                ],
        personality.Passionate: ["Yes, definitely!",
                                 ],
        personality.Sociable: ["Yes, please. That would be good.",
                               ],
        personality.Shy: ["Yes.",
                          ],
    },

    "[YES_YOU_CAN]": {
        # Permission is granted to do something.
        Default: ["Yes, you can."
                  ],
        personality.Cheerful: ["You have my enthusiastic permission.",
                               ],
        personality.Grim: ["By blazes, yes.",
                           ],
        personality.Easygoing: ["I'm not going to stop you.",
                                ],
        personality.Passionate: ["I couldn't stop you if I wanted to!",
                                 ],
        personality.Sociable: ["Yes, you absolutely can do that.",
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

    "[YOU_BELIEVE_THE_HYPE]": {
        # The audience is accused of believing lies.
        Default: ["Your beliefs are lies.", "[DISAGREE]", "You've been deceived."
                  ],
        personality.Cheerful: ["You really drank their bouncy bubbly beverage, didn't you?",
                               ],
        personality.Grim: [
            "You are talking [expletive]. I've heard enough.",
            "Why is it that the most ignorant people are always the most certain?"
        ],
        personality.Easygoing: [
            "You don't really believe that, do you?",
            "You really are a true believer, ain't ya?"
        ],
        personality.Passionate: ["Lies! My actions will show you the truth.",
                                 ],
        personality.Sociable: [
            "As they say, don't believe the hype.",
            "I don't know who told you that, but they were lying."
        ],
        personality.Shy: [
            "You are wrong.",
        ],
        personality.Duty: [
            "It's my duty to inform you that you've been misinformed."
        ],
        personality.Glory: [
            "Oh come on. If that were true, I would have known about it before you."
        ],
        personality.Peace: [
            "I don't want to hurt your feelings, but you're talking nonsense."
        ],
        personality.Justice: [
            "I cannot allow you to speak these lies unchallenged."
        ],
        personality.Fellowship: [
            "If you believe those obvious lies, you really need to get out more often."
        ]
    },

    "[YOU_COULD_BE_RIGHT]": {
        # Different from MAYBE_YOU_ARE_RIGHT_ABOUT_OPINION because no opinion is given.
        Default: ["You could be right."
                  ],
        personality.Cheerful: ["That's definitely possible.",
                               ],
        personality.Grim: ["I hate to say it, but you may be right.",
                           ],
        personality.Easygoing: ["Maybe.",
                                ],
        personality.Passionate: ["Your idea, that could be it!",
                                 ],
        personality.Sociable: ["I have to admit that you could be right.",
                               ],
        personality.Shy: ["I won't say that you're wrong.",
                          ],
    },

    "[YOU_DONT_UNDERSTAND]": {
        # The speaker is about to question the audience's understanding of this situation.
        Default: ["You don't understand...",
                  ],
        personality.Cheerful: ["Are you kidding me?",
                               ],
        personality.Grim: ["Your words betray how little you know about this.",
                           ],
        personality.Easygoing: ["I'm not sure that you understand.",
                                ],
        personality.Passionate: ["You could not be more wrong about that!",
                                 ],
        personality.Sociable: ["It seems to me that you don't understand this situation as well as you think you do.",
                               ],
        personality.Shy: ["You're wrong.",
                          ],
    },

    "[You_have_the_needed_skills]": {
        # The speaker wishes to express that the PC has the needed skills for a given mission or job
        Default: ["you have the necessary skills for this job",
                  ],
        personality.Cheerful: ["this could be a great opportunity for you",
                               ],
        personality.Grim: ["you could do this if you want",
                           ],
        personality.Easygoing: ["it shouldn't be a problem for someone with your skills",
                                ],
        personality.Passionate: ["think of it as a specialist mission",
                                 ],
        personality.Sociable: ["I've heard that you have the skills needed to do this",
                               ],
        personality.Shy: ["you have the needed skills",
                          ],
        LIKE: [
            "you would be absolutely perfect for this",
        ],
        DISLIKE: [
            "unfortunately you're the best person I could find",
        ],
    },

    "[You_heard_right]": {
        # The speaker confirms a rumor.
        Default: ["you heard right",
                  ],
        personality.Cheerful: ["it's a lucky thing that you heard about it",
                               ],
        personality.Grim: ["I can't deny it",
                           ],
        personality.Easygoing: ["you could say that",
                                ],
        personality.Passionate: ["destiny has led you to me today",
                                 ],
        personality.Sociable: ["the rumors you heard are correct",
                               ],
        personality.Shy: ["yes",
                          ],
        LIKE: [
            "I'm glad you got the message",
        ],
        DISLIKE: [
            "yeah, I hate admitting this to you but you heard right",
        ],
    },

    "[You_look_grim]": {
        # Often used in cutscenes when a lancemate notices the PC having grim thoughts.
        Default: ["you look grim",
                  ],
        personality.Cheerful: ["you don't look happy",
                               ],
        personality.Grim: ["I recognize that look",
                           ],
        personality.Easygoing: ["it seems like something's bothering you",
                                ],
        personality.Passionate: ["you seem depressed",
                                 ],
        personality.Sociable: ["you're being unusually quiet",
                               ],
        personality.Shy: ["you look sad",
                          ],
        LIKE: [
            "I can tell you're having painful thoughts",
        ],
    },

        "[your_job]": {
        # A lead-in where the NPC will explain the PC's mission as a simple present verb phrase
        Default: ["your job is to",
                  ],
        personality.Cheerful: ["you get to",
                               ],
        personality.Grim: ["to avoid disaster you must",
                           ],
        personality.Easygoing: ["you should",
                                ],
        personality.Passionate: ["you must",
                                 ],
        personality.Sociable: ["I want you to",
                               ],
        personality.Shy: ["the job is to",
                          ],
        personality.Duty: [
            "the purpose of this mission is to",
            "your duty is to",
        ],
        personality.Glory: ["to succeed you must",
                            ],
        personality.Fellowship: ["let me describe your mission-",
                                 ],
    },


    "[YOUR_PLAN_IS_HOPELESS]": {
        # The NPC expresses a lack of hope about the suggested plan.
        Default: ["This is hopeless.", "Your plan is hopeless."
                  ],
        personality.Cheerful: ["You're talking nonsense, but not the ha-ha kind.",
                               "Are you serious? I was waiting for the punchline."
                               ],
        personality.Grim: ["I'd admire your bravery if I weren't more concerned about my own survival.",
                           "I love a doomed quest as much as anyone but you're taking it too far."
                           ],
        personality.Easygoing: ["Wait, no. That's not going to work.",
                                ],
        personality.Passionate: ["You're talking cringe.",
                                 "There's a fine line between a glorious death and simply throwing your life away."
                                 ],
        personality.Sociable: ["I hate to say this, but your plan is hopeless.",
                               "Have you discussed this with anyone else? Because I really think it's a bad idea."
                               ],
        personality.Shy: ["It won't work.",
                          ],
        personality.Duty: ["I think we should consider alternatives before throwing our lives away.",
                           ],
        personality.Glory: ["Remember that no-one will sing about your heroic deeds if we all die.",
                            ],
        personality.Justice: ["And what's to be gained, a symbolic victory at the cost of our lives?",
                              ],
        personality.Peace: ["Hasn't there been enough death already?",
                            ],
        personality.Fellowship: ["You may view your own life as cheap, but I don't.",
                                 ],
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

    "[YOU_SEEM_NICE_BUT_ENEMY]": {
        # An expression of regret that we have to fight.
        Default: ["You seem nice.", "You seem nice, but I have to [defeat_you]."
                  ],
        personality.Cheerful: ["It's sad that we're on opposite sides, but we are.",
                               "You're nice. Too nice. That's going to get you killed."
                               ],
        personality.Grim: ["Don't expect any sympathy from me; feelings have nothing to do with this.",
                           ],
        personality.Easygoing: ["You seem okay, but...",
                                ],
        personality.Passionate: ["The hearts of two people cannot change the winds of fate!",
                                 ],
        personality.Sociable: ["I'm sure we could be friends if we weren't on different sides.",
                               ],
        personality.Shy: ["Why even bother talking when we're on opposite teams?",
                          ],
        LIKE: [
            "I like you, but right now we both have a job to do.",
        ],
        DISLIKE: [
            "[SWEAR] I'm sure you're a nice person, but I'm just here to [defeat_you].",
        ],
    },

    "[YOU_SHOULD_EJECT]": {
        # A PC is about to intimidate an NPC into ejecting from their mecha.
        Default: ["You should eject.",
                  "I'll give you one last chance to eject."
                  ],
        personality.Cheerful: [
            "Luckily, you still have time to get the [expletive] out of here.",
        ],
        personality.Grim: [
            "One more hit and you'll be nothing but a memory.",
        ],
        personality.Easygoing: [
            "If I were you, I'd seriously think about ejecting right now.",
        ],
        personality.Passionate: [
            "You have no chance to survive; eject or die!",
        ],
        personality.Sociable: [
            "I have to tell you, your situation is hopeless.",
        ],
        personality.Shy: ["Eject. Now.",
                          ],
        personality.Peace: [
            "There's no reason for you to die senselessly."
        ],
        personality.Duty: [
            "One way or the other, it's my job to finish you off."
        ],
        personality.Fellowship: [
            "I'm giving you this chance to save your own life."
        ],
        personality.Justice: [
            "What happens next is up to you; eject or be destroyed."
        ],
        personality.Glory: [
            "I know it's embarrassing to eject, but it beats dying."
        ]
    },

    "[YOU_WILL_NEVER_DEFEAT_US]": {
        # A final cry of defiance. Or a promise to be kept.
        Default: ["You will never defeat us!",
                  "We cannot be defeated so easily!"
                  ],
        personality.Cheerful: [
            "You look pretty smug for someone who doesn't realize the tacnuke of worms you've just unleashed!",
        ],
        personality.Grim: [
            "Some of us may die, but we will never be defeated!",
        ],
        personality.Easygoing: [
            "Yeah, you know we don't give up easy, right?",
        ],
        personality.Passionate: [
            "I pledge with my burning heart that we will never be defeated!",
        ],
        personality.Sociable: [
            "Our allegiance is unshakable; so long as one of us lives, we can never be defeated!",
        ],
        personality.Shy: ["We aren't going to be defeated.",
                          ],
        personality.Peace: [
            "We will never admit defeat to barbarians like you."
        ],
        personality.Duty: [
            "As long as I draw breath, I will not admit defeat."
        ],
        personality.Fellowship: [
            "We stand together, and together we will be victorious!"
        ],
        personality.Glory: [
            "You are not worthy of defeating us."
        ]
    },

    "[FORMAL_MECHA_DUEL]": {
        Default: ["May your armor break, may your cockpit shatter, may who deserves to win, be who destroys the other."
                  ],
        personality.Glory: ["Thus today we two meet upon our arena. May victory shine upon me!"
            , "Glory shine upon the victor; one against one, strong against stronger."
            , "I formally challenge you to a duel to destruction. Glory upon us both; but I shall be the victor."
                            ],
        personality.Peace: [
            "I stand here the champion of my people; I fight against you now, for peace to prevail tomorrow."
            , "I formally challenge you to a duel to destruction. May this be the final fight against you."
        ],
        personality.Justice: ["Well met on this day. Only the righteous shall stand after our fight."
            , "This duel is my trial. May my victory today show the righteousness I stand for."
            , "I formally challenge you to a duel to destruction. May my righteous stance shine through my mecha."
                              ],
        personality.Duty: ["I fight you today for my honor. My obligation shall be what defeats you."
            , "Thus my duty stands before me: you, and your defeat."
            ,
                           "I formally challenge you to a duel to destruction. My obligation is to defeat you, and none shall stand in my way."
                           ],
        personality.Fellowship: [
            "I stand here in the stead of my friends, to fight alone against you, that they may live."
            ,
            "I formally challenge you to a duel to destruction. My friends shall live, win or lose: and I shall defeat you."
        ]
    },
    "[FORMAL_LETSFIGHT]": {
        Default: ["[GOOD] Our destiny awaits. [LETSFIGHT]"
            , "This duel shall lead to [defeating_you]."
            , "Let it be remembered that today I [fight_you]."
                  ]
    }

}
