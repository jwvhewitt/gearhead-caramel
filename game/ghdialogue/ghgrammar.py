
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

}
