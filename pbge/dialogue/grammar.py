import collections
import random

""" The grammar/token expander takes generic tokens and expands them into
    appropriate words or sentences. With the exception of hard coded plot based
    dialogue lines, it's this system which decides what gets said.

"""

#
# Uppercase tokens should expand to a complete sentence
# Lowercase tokens should not
# A standard offer token is generally the context tags of the offer separated
#  by underspaces.
# A standard reply token is generally two offer tokens separated by a colon.
#

class Grammar( dict ):
    def absorb( self, othergram ):
        for k,v in othergram.items():
            if k not in self:
                self[k] = list()
            self[k] += v



def expand_token( token_block, gramdb ):
    """Return an expansion of token according to gramdb. If no expansion possible, return token."""
    a,b,suffix = token_block.partition("]")
    token = a + b
    if token in gramdb:
        ex = random.choice( gramdb[token] )
        all_words = list()
        for word in ex.split():
            if word[0] == "[":
                word = expand_token( word, gramdb )
            all_words.append( word )
        if suffix and all_words:
            all_words[-1] += suffix
        return " ".join( all_words )
    else:
        return token

def maybe_expand_token( token_block, gramdb ):
    """Return an expansion of token according to gramdb if possible."""
    a,b,suffix = token_block.partition("]")
    token = a + b
    if token in gramdb:
        possibilities = list( gramdb[token] )
        random.shuffle( possibilities )
        while possibilities:
            all_ok = True
            all_words = list()
            ex = possibilities.pop()
            for word in ex.split():
                if word[0] == "[":
                    word = maybe_expand_token( word, gramdb )
                if isinstance( word, str ):
                    all_words.append( word )
                else:
                    all_ok = False
            if all_ok:
                break
        if all_words:
            if suffix:
                all_words[-1] += suffix
            return " ".join( all_words )


def convert_tokens( in_text, gramdb, allow_maybe=True, auto_format = True, start_on_capital=True ):
    all_words = list()
    for word in in_text.split():
        if word[0] == "[":
            if allow_maybe:
                word = maybe_expand_token( word, gramdb )
            else:
                word = expand_token( word, gramdb )
        if word:
            all_words.append( word )
    if auto_format:
        original_words = list()
        for w in all_words:
            original_words += w.split()
        all_words = list()
        capitalize = start_on_capital
        while original_words:
            word = original_words.pop(0)
            if word == "a" or word =="A":
                if original_words and original_words[0][0] in "aeiouAEIOU":
                    word = word + 'n'
            if capitalize:
                word = word.capitalize()
                capitalize = False
            if word[-1] in ".\n":
                capitalize = True
            all_words.append(word)
    return " ".join( all_words )


