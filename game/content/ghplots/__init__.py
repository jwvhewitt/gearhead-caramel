import inspect

from . import actionscenes
from . import dd_combatmission
from . import dd_customobjectives
from . import dd_distanttown
from . import dd_homebase
from . import dd_intro
from . import dd_lancedev
from . import dd_main
from . import dd_roadedge
from . import dd_roadedge_propp
from . import dd_roadstops
from . import dd_tarot
from . import dd_tarotsupport
from . import encounters
from . import lancemates
from . import missionbuilder
from . import mocha
from . import recovery
from . import utility
from game.content import mechtarot, PLOT_LIST, UNSORTED_PLOT_LIST, CARDS_BY_NAME
from pbge.plots import Plot


def harvest( mod ):
    for name in dir( mod ):
        o = getattr( mod, name )
        if inspect.isclass( o ) and issubclass( o , Plot ) and o is not Plot and o is not mechtarot.TarotCard:
            PLOT_LIST[ o.LABEL ].append( o )
            UNSORTED_PLOT_LIST.append( o )
            # print o.__name__
            if issubclass(o,mechtarot.TarotCard):
                CARDS_BY_NAME[o.__name__] = o

harvest(actionscenes)
harvest(dd_combatmission)
harvest(dd_customobjectives)
harvest(dd_distanttown)
harvest(dd_homebase)
harvest(dd_intro)
harvest(dd_lancedev)
harvest(dd_main)
harvest(dd_roadedge)
harvest(dd_roadedge_propp)
harvest(dd_roadstops)
harvest(dd_tarot)
harvest(dd_tarotsupport)
harvest(encounters)
harvest(lancemates)
harvest(missionbuilder)
harvest(mocha)
harvest(recovery)
harvest(utility)
