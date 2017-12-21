
#
# Uppercase tokens should expand to a complete sentence
# Lowercase tokens should not
# A standard offer token is generally the context tags of the offer separated
#  by underspaces.
# A standard reply token is generally two offer tokens separated by a colon.
#

DEFAULT_GRAMMAR = {
    "[HELLO]": ["Hello.","Hello [pc]."
        ],
    # The data block should hold the item name.
    "[HELLO:ASK_FOR_ITEM]": ["Do you have a {item}?",
        "I'm looking for a {item}. Seen one?"
        ],

}


