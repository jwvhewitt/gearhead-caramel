
import collections
from pbge.plots import PlotError
import pbge
import gears
from .. import exploration

import ghterrain
import ghwaypoints
import ghcutscene
import uuid


# The list of plots will be stored as a dictionary based on label.
PLOT_LIST = collections.defaultdict( list )
UNSORTED_PLOT_LIST = list()
CARDS_BY_NAME = dict()


class GHNarrativeRequest(pbge.plots.NarrativeRequest):
    def init_tarot_card(self,myplot,card_class,pstate,ident=None):
        cp = card_class(self,pstate)
        if cp:
            if not ident:
                ident = "_autoident_{0}".format(len(myplot.subplots))
            myplot.subplots[ident] = cp
        return cp
    def generate_tarot_card( self, pstate, tags ):
        """Locate a plot which matches the request, init it, and return it."""
        # Create a list of potential plots.
        candidates = list()
        tagset = set(tags)
        for sp in self.plot_list['TAROT']:
            if tagset.issubset(sp.TAGS) and sp.matches( pstate ):
                candidates.append( sp )
        if candidates:
            cp = None
            while candidates and not cp:
                cpc = self.random_choice_by_weight( candidates )
                candidates.remove( cpc )
                try:
                    cp = cpc(self,pstate)
                except PlotError:
                    cp = None
            if not cp:
                self.errors.append( "No plot accepted for {0}".format( tags ) )
            return cp
        else:
            self.errors.append( "No plot found for {0}".format( tags ) )

    def add_tarot_card( self, myplot, tarot_tags, spstate=None, ident=None, necessary=True, tarot_position=None ):
        if not spstate:
            spstate = pbge.plots.PlotState().based_on(myplot)
        if not ident:
            ident = "_autoident_{0}".format( len( myplot.subplots ) )
        if tarot_position or mechtarot.ME_TAROTPOSITION not in spstate.elements:
            if not tarot_position:
                tarot_position = uuid.uuid4()
            spstate.elements[mechtarot.ME_TAROTPOSITION] = tarot_position
        sp = self.generate_tarot_card( spstate, tarot_tags )
        if necessary and not sp:
            #print "Fail: {}".format(splabel)
            myplot.fail( self )
        elif sp:
            #print "Success: {}".format(splabel)
            myplot.subplots[ident] = sp
        return sp
    def request_tarot_card_by_name(self,tarot_name,pstate):
        cpc = CARDS_BY_NAME.get(tarot_name)
        if cpc:
            self.story = cpc(self,pstate)
            return self.story

import mechtarot

from game.content.ghplots import dd_combatmission, dd_homebase, dd_main, dd_tarot, dd_tarotsupport, mocha, harvest
import plotutility

import adventureseed




def narrative_convenience_function( pc_egg, adv_type="SCENARIO_DEADZONEDRIFTER" ):
#def narrative_convenience_function(adv_type="SCENARIO_MOCHA"):
    # Start an adventure.
    init = pbge.plots.PlotState(rank=1)
    camp = gears.GearHeadCampaign(name=str(pc_egg.pc),explo_class=exploration.Explorer,egg=pc_egg)
    nart = GHNarrativeRequest(camp,init,adv_type,PLOT_LIST)
    if nart.story:
        nart.build()
        return nart.camp
    else:
        for e in nart.errors:
            print e


def test_mocha_encounters():
    frontier = list()
    possible_states = list()
    move_cost = collections.defaultdict(int)
    for p in PLOT_LIST['MOCHA_MINTRO']:
        frontier.append(p.CHANGES)

    while frontier:
        current = frontier.pop()
        possible_states.append(current)
        # Find the neighbors
        for p in PLOT_LIST['MOCHA_MENCOUNTER']:
            if all( p.REQUIRES[k] == current.get(k,0) for k in p.REQUIRES.iterkeys() ):
                dest = current.copy()
                dest.update(p.CHANGES)
                new_cost = move_cost[repr(current)] + 1
                if new_cost <= 2 and ( repr(dest) not in move_cost or new_cost < move_cost[repr(dest)] ):
                    move_cost[repr(dest)] = new_cost
                    frontier.append(dest)
    # Finally, print an analysis.
    print "Possible States: {}".format(possible_states)
    done_stuff = set()
    for s in possible_states:
        if move_cost[repr(s)] < 2:
            ec = (mocha.ENEMY, s.get(mocha.ENEMY, 0), mocha.COMPLICATION, s.get(mocha.COMPLICATION, 0))
            EnemyComp = [p for p in PLOT_LIST['MOCHA_MENCOUNTER']
                         if s.get(mocha.ENEMY, 0) == p.REQUIRES.get(mocha.ENEMY, 0)
                         and mocha.ENEMY in p.REQUIRES
                         and mocha.COMPLICATION in p.REQUIRES
                         and s.get(mocha.COMPLICATION, 0) == p.REQUIRES.get(mocha.COMPLICATION, 0)]
            if ec not in done_stuff and not EnemyComp:
                print "No encounter found for Enemy:{} Complication:{}".format(ec[1],ec[3])
            done_stuff.add(ec)

            es = (mocha.ENEMY, s.get(mocha.ENEMY, 0), mocha.STAKES, s.get(mocha.STAKES, 0))
            EnemyStakes = [p for p in PLOT_LIST['MOCHA_MENCOUNTER']
                           if s.get(mocha.ENEMY, 0) == p.REQUIRES.get(mocha.ENEMY, 0)
                           and mocha.ENEMY in p.REQUIRES
                           and mocha.STAKES in p.REQUIRES
                           and s.get(mocha.STAKES, 0) == p.REQUIRES.get(mocha.STAKES, 0)]
            if es not in done_stuff and not EnemyStakes:
                print "No encounter found for Enemy:{} Stakes:{}".format(es[1],es[3])
            done_stuff.add(es)

            cs = (mocha.COMPLICATION, s.get(mocha.COMPLICATION, 0), mocha.STAKES, s.get(mocha.STAKES, 0))
            CompStakes = [p for p in PLOT_LIST['MOCHA_MENCOUNTER']
                          if s.get(mocha.COMPLICATION, 0) == p.REQUIRES.get(mocha.COMPLICATION, 0)
                          and mocha.COMPLICATION in p.REQUIRES
                          and mocha.STAKES in p.REQUIRES
                          and s.get(mocha.STAKES, 0) == p.REQUIRES.get(mocha.STAKES, 0)]
            if cs not in done_stuff and not CompStakes:
                print "No encounter found for Complication:{} Stakes:{}".format(cs[1],cs[3])
            done_stuff.add(cs)

    for s in possible_states:
        if move_cost[repr(s)] >= 2:
            choices = [ p for p in PLOT_LIST['MOCHA_MHOICE'] if all( p.REQUIRES[k] == s.get(k,0) for k in p.REQUIRES.iterkeys() )]
            if len(choices) < 4:
                print "Only {} choices for {}".format(len(choices),s)




#test_mocha_encounters()
