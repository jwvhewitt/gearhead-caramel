import inspect

import dd_combatmission
import dd_homebase
import dd_main
import dd_tarot
import dd_tarotsupport
import dd_intro
import mocha
import utility
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

harvest(mocha)
harvest(dd_homebase)
harvest(dd_main)
harvest(dd_combatmission)
harvest(dd_tarot)
harvest(dd_tarotsupport)
harvest(dd_intro)
harvest(utility)
