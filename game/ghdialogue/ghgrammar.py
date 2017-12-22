
#
# Uppercase tokens should expand to a complete sentence
# Lowercase tokens should not
# A standard offer token is generally the context tags of the offer separated
#  by underspaces.
# A standard reply token is generally two offer tokens separated by a colon.
#

DEFAULT_GRAMMAR = {
    # The data block should hold the item name as "item".
    "[DOTHEYHAVEITEM]": [ "Don't they have {item}?",
        "They should have {item}.","What about their {item}?"
        ],

    "[GOODBYE_MISSION:JOIN]": ["Why don't you come with me?"
        ],

    "[GOODLUCK]": ["Good luck.","Good luck with that."
        ],    

    "[HELLO]": ["Hello.","Hello [audience].","Hi."
        ],
    # The data block should hold the item name as "item".
    "[HELLO:ASK_FOR_ITEM]": ["Do you have a {item}?",
        "I'm looking for a {item}. Seen one?"
        ],

    # The data block should include "subject"
    "[HELLO:INFO]": [ "Tell me about the {subject}.",
        "What can you tell me about the {subject}?"
        ],

    # The data block should include "subject"
    "[HELLO:INFO_PERSONAL]": [ "How have you been doing?","What's new?",
        "I hear you have a story about the {subject}."
        ],

    "[HELLO:JOIN]": [ "Would you like to join my lance?",
        "How about joining my lance?"
        ],

    "[INFO_PERSONAL:JOIN]": ["Why don't you join my lance?",
        "Let's go on an adventure together."
        ],

    # The data block should include "mission"
    "[IWILLDOMISSION]": [ "I'll get to work.", "I will do this mission.",
        "I'll {mission}."
        ],

    "[LONGTIMENOSEE]": ["Hello [audience], long time no see.",
        "Long time no see, [audience].","Well there's a face I haven't seen in a while.",
        ],
    "[MISSION_PROBLEM:JOIN]": ["I could really use your help out there.",
        "Sounds like I could use some backup."
        ],


}


