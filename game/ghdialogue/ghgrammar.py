from gears import personality
#
#   GearHead Grammar
#
# Please note that the master grammar dict operates in a different way
# from the pbge grammar dict. Instead of each item resolving to a list
# of options, each list resolves to a dict of PersonalityTrait: [options,...]
#
# Uppercase tokens should expand to a complete sentence
# Lowercase tokens should not
# A standard offer token is generally the context tags of the offer separated
#  by underspaces.
# A standard reply token is generally two offer tokens separated by a colon.
#

# A meaningless constant
Default = None

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


    "[DOTHEYHAVEITEM]": {
    # The data block should hold the item name as "item".
        Default: [ "Don't they have {item}?",
            "They should have {item}.","What about their {item}?"
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
        personality.Sociable: ["I'll see you later.",
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
            "I'll {mission}."
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
    }

}


