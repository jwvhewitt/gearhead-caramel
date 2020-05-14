import copy
import gears
from gears import base

# Users of the cyberinstaller and the cyberdoc should
# provide an object providing this
# interface.
class CyberwareSource(object):
    def get_cyberware_list(self):
        ''' Return a list of cyberware this source
        provides.
        Cyberware are gears from BaseCyberware.
        This implies to the caller that any of the
        returned cyberware gears may, in the future,
        be used in the other functions below.
        '''
        raise NotImplementedError()
    def get_list_annotation(self, cyberware):
        ''' Return either None, or a string.
        If a string is returned, that string
        will be appended with a space to
        cyberware.name in the list of available
        gears.
        '''
        return None
    def get_panel_annotation(self, cyberware):
        ''' Return either None, or a string.
        If a string is returned, that string
        will be added to the infopanel when
        the cyberware is hovered.
        '''
        return None
    def can_purchase(self, cyberware, camp):
        ''' Determine if the given camp can
        pay for the cyberware, or whatever.
        Return true if the camp can buy.
        '''
        return True
    def acquire_cyberware(self, cyberware, camp):
        ''' Acquire a stock copy of the cyberware
        and deduct money from the camp, or remove
        this cyberware from this source.
        Return the copy, or the same cyberware.
        '''
        raise NotImplementedError()

class ListedSalesCyberwareSource(CyberwareSource):
    def __init__(self, cyberware_list):
        self._cyberware_list = cyberware_list
    def get_cyberware_list(self):
        return self._cyberware_list.copy()
    def get_panel_annotation(self, cyberware):
        return '${:,}'.format(cyberware.cost)
    def get_cyberware_cost(self, cyberware):
        return cyberware.cost
    def can_purchase(self, cyberware, camp):
        return self.get_cyberware_cost(cyberware) <= camp.credits
    def acquire_cyberware(self, cyberware, camp):
        camp.credits -= self.get_cyberware_cost(cyberware)
        return copy.deepcopy(cyberware)

class AllCyberwareSource(ListedSalesCyberwareSource):
    def __init__(self):
        super().__init__([ cw for cw in gears.selector.DESIGN_LIST
                        if isinstance(cw, base.BaseCyberware)
                         ])

###############################################################################

class CyberwareInstaller(object):
    ''' Business logic for installing cyberware.
    '''
    def __init__(self, char, source, camp, alert, choose):
        # alert is a function that accepts a single string and shows it to
        # the user.
        # choose is a function given a list of strings, prompts the user
        # to choose one, then returns the 0-based index of the selection.
        self.char = char
        self.source = source
        self.camp = camp
        self.alert = alert
        self.choose = choose

    def install(self, cyberware):
        if not self.source.can_purchase(cyberware, self.camp):
            self.alert("You cannot afford it!")
            return

        if cyberware.dna_sequence and cyberware.dna_sequence != self.char.dna_sequence:
            self.alert("Cannot install {};\ndoes not match your genetics.".format(cyberware.name))
            return

        candidate_modules = self._get_candidate_modules(cyberware)
        if not candidate_modules:
            self.alert('Cannot install {}: cannot be installed in any body part.'.format(cyberware.name))
            return

        no_choice_failure = ( "Cannot install {}:\nCurrent trauma is {} / {};\nit would bring your trauma to {}."
                              .format( cyberware.name
                                     , self.char.current_trauma
                                     , self.char.max_trauma
                                     , self.char.current_trauma + cyberware.trauma
                                     )
                            )

        choices = list()
        for mod in candidate_modules:
            if mod.can_install(cyberware):
                choices.append(( "Install in {}".format(mod.name)
                               , self._make_install_fun(mod, cyberware)
                               ))
            # Seach for replacements.
            for other_cyberware in list(mod.sub_com):
                if not isinstance(other_cyberware, base.BaseCyberware):
                    continue
                # You can only replace with the same location.
                if not cyberware.location is other_cyberware.location:
                    continue
                if self._can_replace(mod, other_cyberware, cyberware):
                    choices.append(( "Replace {} in {}".format(other_cyberware.name, mod.name)
                                   , self._make_replace_fun(mod, other_cyberware, cyberware)
                                   ))
                else:
                    no_choice_failure = ( "Cannot install {}:\nCurrent trauma is {} / {};\neven replacing {} would bring your trauma to {}."
                                          .format( cyberware.name
                                                 , self.char.current_trauma
                                                 , self.char.max_trauma
                                                 , other_cyberware.name
                                                 , self.char.current_trauma + cyberware.trauma - other_cyberware.trauma
                                                 )
                                        )

        if not choices:
            self.alert(no_choice_failure)
            return

        # If only once choice, don't bother asking the
        # player.
        if len(choices) == 1:
            choice = choices[0]
            choice[1]()
            return

        text_choices = [choice[0] for choice in choices]
        text_choices.append("[Cancel]")

        choice_index = self.choose(text_choices)
        if choice_index is False or choice_index >= len(choices):
            # Cancelled.
            return

        # Execute the choice.
        choice = choices[choice_index]
        choice[1]()

    def remove(self, cyberware):
        ''' Remove cyberware from its owner.
        Note: we do not do any checks below, we presume the
        caller has already determined that the cyberware is
        installed in the given self.char!
        '''
        cyberware.parent.sub_com.remove(cyberware)
        # The cyberware is now full of the previous user's cells.
        cyberware.dna_sequence = self.char.dna_sequence
        self._return_old_cyberware(cyberware)

    def _put_in(self, mod, cyberware):
        actual = self._acquire_new_cyberware(cyberware)
        # The host's cells permeate into the cyberware.
        actual.dna_sequence = self.char.dna_sequence
        mod.sub_com.append(actual)

    def _get_candidate_modules(self, cyberware):
        ''' Return all modules the cyberware can be installed in.
        Do not filter based on trauma or having an existing
        cyberware yet.
        '''
        return [ mod for mod in self.char.sub_sub_coms()
              if isinstance(mod, base.Module)
             and mod.can_install(cyberware, check_volume = False)
               ]

    def _can_replace(self, mod, old, new):
        ''' Determine if we can install the new cyberware
        if the old cyberware is removed first.
        '''
        # We actually perform the remove, *then* check,
        # then restore the old gear.
        # This lets us leave the cyberware check to
        # gears.base, so only one place needs to be
        # updated if we want to change the limits on
        # cyberware.
        mod.sub_com.remove(old)
        ret = mod.can_install(new)
        mod.sub_com.append(old)
        return ret

    def _make_install_fun(self, mod, cyberware):
        ''' Create a function which will actually install
        the cyberware into the specified module.
        '''
        def install():
            self._put_in(mod, cyberware)
        return install

    def _make_replace_fun(self, mod, old, new):
        ''' Create a function which will actually remove
        the old cyberware and put the new cyberware into
        the specified module.
        '''
        def replace():
            self.remove(old)
            self._put_in(mod, new)
        return replace

    def _acquire_new_cyberware(self, cyberware):
        ''' Removes the cyberware from wherever it currently
        is so we can install it into the character.
        '''
        return self.source.acquire_cyberware(cyberware, self.camp)

    def _return_old_cyberware(self, cyberware):
        self.char.inv_com.append(cyberware)
