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
    # The data block should hold the item name as "item".
    "[DOTHEYHAVEITEM]": {
        Default: [ "Don't they have {item}?",
            "They should have {item}.","What about their {item}?"
            ],
        },

    "[GOODBYE_MISSION:JOIN]": {
        Default: ["Why don't you come with me?"
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
        },

    "[INFO_PERSONAL:JOIN]": {
        Default: ["Why don't you join my lance?",
            "Let's go on an adventure together."
            ],
        },

    # The data block should include "mission"
    "[IWILLDOMISSION]": {
        Default: [ "I'll get to work.", "I will do this mission.",
            "I'll {mission}."
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
            "Sounds like I could use some backup."
            ],
        },


}


