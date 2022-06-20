import copy

###############################################################################

# An Undo/Redo item.
class UndoRedoBase(object):
    # Return True if undoing succeeded, False if not.
    def on_do(self):
        raise NotImplementedError('UndoRedoBase.on_do must be overridden')

    # Return True if undoing succeeded, False if not.
    def on_undo(self):
        raise NotImplementedError('UndoRedoBase.on_undo must be overridden')

# The undo/redo list.
class UndoRedoSystem(object):
    def __init__(self):
        self.undos = list()
        self.redos = list()

    def do_action(self, undo_redo_base):
        if undo_redo_base.on_do():
            self.undos.append(undo_redo_base)
            self.redos.clear()

    def is_empty(self):
        return not (self.undos or self.redos)

    def undo(self):
        if not self.undos:
            return
        undo_redo_base = self.undos[-1]
        if undo_redo_base.on_undo():
            self.undos.pop()
            self.redos.append(undo_redo_base)

    def redo(self):
        if not self.redos:
            return
        undo_redo_base = self.redos[-1]
        if undo_redo_base.on_do():
            self.redos.pop()
            self.undos.append(undo_redo_base)

    # Undo a specific item.
    def undo_specific(self, undo_redo_base):
        if not (undo_redo_base in self.undos):
            return
        if undo_redo_base.on_undo():
            self.undos.remove(undo_redo_base)
            self.redos.append(undo_redo_base)

    # Undo everything.
    def undo_all(self):
        while self.undos:
            undo_redo_base = self.undos.pop()
            undo_redo_base.on_undo()
        self.redos.clear()

###############################################################################

class Action(object):
    '''
    An action triggered by clicking an entry on
    one of the two lists.
    '''
    def __call__(self):
        raise NotImplementedError('Action.__call__ must be overridden')

    @property
    def label(self):
        raise NotImplementedError('Action.label must be overridden')

    @property
    def cost(self):
        raise NotImplementedError('Action.cost must be overridden')

    @property
    def model(self):
        raise NotImplementedError('Action.model must be overridden')


class UndoAction(Action):
    '''
    An action to undo a buy or sell.
    '''
    def __init__(self, undo_redo_sys, undo_redo_base, label, cost, model):
        self.undo_redo_sys = undo_redo_sys
        self.undo_redo_base = undo_redo_base
        self._label = label
        self._cost = cost
        self._model = model

    @property
    def label(self):
        return self._label

    @property
    def cost(self):
        return self._cost

    @property
    def model(self):
        return self._model

    def __call__(self):
        self.undo_redo_sys.undo_specific(self.undo_redo_base)


class BuySellCounters(object):
    '''
    Abstract interface to an object that
    keeps track of items bought/sold
    '''
    @property
    def num_bought(self):
        # number of items bought.
        raise NotImplementedError('BuySellCounters.num_bought must be overridden')
    @num_bought.setter
    def num_bought(self, v):
        raise NotImplementedError('BuySellCounters.num_bought must be overridden')

    @property
    def num_sold(self):
        # number of items sold.
        raise NotImplementedError('BuySellCounters.num_sold must be overridden')
    @num_sold.setter
    def num_sold(self, v):
        raise NotImplementedError('BuySellCounters.num_sold must be overridden')

    @property
    def bought(self):
        # list of items bought.
        raise NotImplementedError('BuySellCounters.bought must be overridden')

class ListsManager(object):
    '''
    Abstract interface to an object that manages
    sell-lists and buy-lists.
    '''
    # Remove operations should silently fail
    # without raising an error if action is
    # not in the appropriate list.
    def add_sell_action(self, action):
        raise NotImplementedError("ListsManager.add_sell_action must be overridden")
    def remove_sell_action(self, action):
        raise NotImplementedError("ListsManager.remove_sell_action must be overridden")
    def add_buy_action(self, action):
        raise NotImplementedError("ListsManager.add_buy_action must be overridden")
    def remove_buy_action(self, action):
        raise NotImplementedError("ListsManager.remove_buy_action must be overridden")

    def cannot_afford(self):
        '''
        Called if the customer cannot afford item.
        '''
        raise NotImplementedError("ListsManager.cannot_afford must be overridden")


class CustomerManager(object):
    '''
    Abstract object to provide the active customer.
    '''
    def get_customer(self):
        raise NotImplementedError("CustomerManager.get_customer must be overridden")


class BuyActionUndoRedo(UndoRedoBase):
    '''
    An undoable buy.
    '''
    def __init__( self, camp, shop, ware
                # instance of UndoRedoSystem
                , undo_redo_sys
                # instance of BuySellCounters
                , buy_sell_counters
                # instance of ListsManager
                , lists_manager
                # instance of CustomerManager
                , customer_manager
                ):
        self.camp = camp
        self.shop = shop
        # Clone the ware here.
        self.ware = copy.deepcopy(ware)
        self.undo_redo_sys = undo_redo_sys
        self.buy_sell_counters = buy_sell_counters
        self.lists_manager = lists_manager
        self.customer_manager = customer_manager

        self.customer = self.customer_manager.get_customer()

        self.cost = self.shop.calc_purchase_price(self.camp, self.ware)

        self.action = UndoAction( self.undo_redo_sys
                                , self
                                , self.ware.get_full_name() + " [Bought]"
                                , self.cost
                                , self.ware
                                )

    def on_do(self):
        # Can they buy it?
        if self.camp.credits < self.cost:
            self.lists_manager.cannot_afford()
            return False

        # Hand it to the customer.
        customer = self.customer
        if customer.can_equip(self.ware):
            customer.inv_com.append(self.ware)
        else:
            self.camp.party.append(self.ware)
        # Charge the customer.
        self.camp.credits -= self.cost

        # Add the item to the sell list.
        self.lists_manager.add_sell_action(self.action)

        # Increment statistics.
        self.buy_sell_counters.num_bought += 1
        self.buy_sell_counters.bought.append(self.ware)

        return True

    def on_undo(self):
        # Take it back from the customer.
        customer = self.customer
        if customer.can_equip(self.ware):
            customer.inv_com.remove(self.ware)
        else:
            self.camp.party.remove(self.ware)
        # Refund the money.
        self.camp.credits += self.cost

        # Remove the item from the sell list.
        self.lists_manager.remove_sell_action(self.action)

        # Revert statistics.
        self.buy_sell_counters.num_bought -= 1
        self.buy_sell_counters.bought.remove(self.ware)

        return True


class BuyAction(Action):
    '''
    A buy action, to be listed on the shop "wares" list.
    '''
    def __init__( self, camp, shop, ware
                , undo_redo_sys
                , buy_sell_counters
                , lists_manager
                , customer_manager
                ):
        self.camp = camp
        self.shop = shop
        self.ware = ware
        self.undo_redo_sys = undo_redo_sys
        self.buy_sell_counters = buy_sell_counters
        self.lists_manager = lists_manager
        self.customer_manager = customer_manager

    def __call__(self):
        undo_redo_base = BuyActionUndoRedo( self.camp
                                          , self.shop
                                          , self.ware
                                          , self.undo_redo_sys
                                          , self.buy_sell_counters
                                          , self.lists_manager
                                          , self.customer_manager
                                          )
        self.undo_redo_sys.do_action(undo_redo_base)

    @property
    def label(self):
        return self.ware.get_full_name()

    @property
    def cost(self):
        return self.shop.calc_purchase_price(self.camp, self.ware)

    @property
    def model(self):
        return self.ware


class SellActionUndoRedo(UndoRedoBase):
    '''
    An undoable sell.
    '''

    def __init__( self, camp, shop, ware
                , undo_redo_sys, buy_sell_counters
                , lists_manager, customer_manager
                , sell_action
                ):
        self.camp = camp
        self.shop = shop
        self.ware = ware
        self.undo_redo_sys = undo_redo_sys
        self.buy_sell_counters = buy_sell_counters
        self.lists_manager = lists_manager
        self.customer_manager = customer_manager
        self.sell_action = sell_action

        self.customer = self.customer_manager.get_customer()
        if self.ware in self.customer.inv_com:
            self.provenance = 'inv_com'
        else:
            self.provenance = 'party'

        self.cost = self.shop.calc_sale_price(self.camp, self.ware)

        self.action = UndoAction( self.undo_redo_sys
                                , self
                                , self.ware.get_full_name() + " [Sold]"
                                , self.cost
                                , self.ware
                                )

    def on_do(self):
        # Will the shopkeeper buy it?
        if self.ware.stolen and not self.shop.buy_stolen_items:
            self.lists_manager.no_stolen_goods()
            return False

        # Get it from the customer.
        if self.provenance == 'inv_com':
            self.customer.inv_com.remove(self.ware)
        else:
            self.camp.party.remove(self.ware)
        # Pay the customer for it.
        self.camp.credits += self.cost

        # Add the item to the buy list.
        self.lists_manager.add_buy_action(self.action)

        # Remove the item from the sell list.
        self.lists_manager.remove_sell_action(self.sell_action)

        # Increment statistics.
        self.buy_sell_counters.num_sold += 1

        return True

    def on_undo(self):
        # Can the customer afford it?
        if self.camp.credits < self.cost:
            self.lists_manager.cannot_afford()
            return False

        # Return it to the customer.
        if self.provenance == 'inv_com':
            self.customer.inv_com.append(self.ware)
        else:
            self.camp.party.append(self.ware)

        # Take back the money from the customer.
        self.camp.credits -= self.cost

        # Remove the item from the buy list.
        self.lists_manager.remove_buy_action(self.action)

        # Return the item to the sell list.
        self.lists_manager.add_sell_action(self.sell_action)

        # Revert statistics.
        self.buy_sell_counters.num_sold -= 1

        return True


class SellAction(Action):
    '''
    A sell action, to be listed on the customer "inventory" list.
    '''
    def __init__( self, camp, shop, ware
                , undo_redo_sys
                , buy_sell_counters
                , lists_manager
                , customer_manager
                ):
       self.camp = camp
       self.shop = shop
       self.ware = ware
       self.undo_redo_sys = undo_redo_sys
       self.buy_sell_counters = buy_sell_counters
       self.lists_manager = lists_manager
       self.customer_manager = customer_manager

    def __call__(self):
        undo_redo_base = SellActionUndoRedo( self.camp
                                           , self.shop
                                           , self.ware
                                           , self.undo_redo_sys
                                           , self.buy_sell_counters
                                           , self.lists_manager
                                           , self.customer_manager
                                           , self
                                           )
        self.undo_redo_sys.do_action(undo_redo_base)

    @property
    def label(self):
        return self.ware.get_full_name()

    @property
    def cost(self):
        return self.shop.calc_sale_price(self.camp, self.ware)

    @property
    def model(self):
        return self.ware


