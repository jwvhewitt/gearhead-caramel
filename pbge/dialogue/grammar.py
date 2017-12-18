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

def absorb( gram, othergram ):
    for k,v in othergram.iteritems():
        if k not in gram:
            gram[k] = list()
        gram[k] += v
    return gram

def base_grammar( pc, npc, explo ):
    # Build a default grammar with the required elements.
    mygram = collections.defaultdict(list)
    absorb( mygram, GRAM_DATABASE )
    mygram["[pc]"].append( str( pc ) )
    mygram["[npc]"].append( str( npc ) )
    mygram["[scene]"].append( str( explo.scene ) )
    mygram["[city]"].append( str( explo.camp.current_root_scene() ) )

    if npc:
        friendliness = npc.get_friendliness( explo.camp )
        if friendliness < -50:
            absorb( mygram, DISLIKE_GRAMMAR )
            absorb( mygram, HATE_GRAMMAR )
        elif friendliness < -20:
            absorb( mygram, DISLIKE_GRAMMAR )
        elif friendliness > 50:
            absorb( mygram, LIKE_GRAMMAR )
            absorb( mygram, LOVE_GRAMMAR )
        elif friendliness > 20:
            absorb( mygram, LIKE_GRAMMAR )

    return mygram

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

def convert_tokens( in_text, gramdb, allow_maybe=True ):
    all_words = list()
    for word in in_text.split():
        if word[0] == "[":
            if allow_maybe:
                word = maybe_expand_token( word, gramdb )
            else:
                word = expand_token( word, gramdb )
        if word:
            all_words.append( word )
    return " ".join( all_words )


