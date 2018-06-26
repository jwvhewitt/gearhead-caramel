#  *******************
#  ***   ANCHORS   ***
#  *******************
# Each anchor function takes two rects: a parent and a child.
# The child is arranged relative to the parent.

def northwest(par,chi):
    if chi:
        chi.topleft = par.topleft
    else:
        return par.topleft

def north( par,chi ):
    if chi:
        chi.midtop = par.midtop
    else:
        return par.midtop

def northeast(par,chi):
    if chi:
        chi.topright = par.topright
    else:
        return par.topright

def west(par,chi):
    if chi:
        chi.midleft = par.midleft
    else:
        return par.midleft

def middle( par,chi):
    if chi:
        chi.center = par.center
    else:
        return par.center

def east(par,chi):
    if chi:
        chi.midright = par.midright
    else:
        return par.midright

def southwest(par,chi):
    if chi:
        chi.bottomleft = par.bottomleft
    else:
        return par.bottomleft

def south( par,chi ):
    if chi:
        chi.midbottom = par.midbottom
    else:
        return par.midbottom

def southeast(par,chi):
    if chi:
        chi.bottomright = par.bottomright
    else:
        return par.bottomright



EDGES = (west,northwest,north,northeast,east,southeast,south,southwest)

OPPOSING_CARDINALS = ((north,south),(east,west),(south,north),(west,east))

OPPOSING_PAIRS = ((northwest,southeast), (north,south), (northeast,southwest),
    (west,east), (east,west), (southwest,northeast), (south,north),
    (southeast, northwest))

