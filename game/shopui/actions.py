import copy
import gears

###############################################################################

class ShoppingUndoRecord:
    def __init__(self, camp: gears.GearHeadCampaign, item, price, is_purchase=True):
        # Price needs to be recorded since it's going to depend on the player's relationship with the shopkeeper
        # among other things.
        self.camp = camp
        self.item = item
        self._item_initial_mass = item.mass
        self._item_initial_cost = item.cost
        self._item_initial_owner = item.get_root()
        if self._item_initial_owner == self.item:
            self._item_initial_owner = None
        self.price = price
        self.is_purchase = is_purchase

    def on_undo(self):
        # Return True if the undo completed successfully, or False if it didn't.
        if self.item.mass != self._item_initial_mass or self.item.cost != self._item_initial_cost:
            # Goods that have been tampered with cannot be returned.
            return False

        if self.is_purchase:
            # Return this item for a refund.
            if hasattr(self.item, "container") and self.item.container:
                self.item.container.remove(self.item)
            elif self.item in self.camp.party:
                self.camp.party.remove(self.item)
            else:
                # Items cannot be returned if I have no idea where they are.
                return False

            self.camp.credits += self.price

        else:
            # Return this item to the party, and take back the cash you paid for it.
            if self._item_initial_owner and self._item_initial_owner.can_equip(self.item):
                self._item_initial_owner.inv_com.append(self.item)
            else:
                self.camp.party.append(self.item)

            self.camp.credits -= self.price

        return True


class ShoppingUndoSystem:
    def __init__(self):
        self.items_to_undo = dict()

    def record_undo(self, camp, item, price, *args, **kwargs):
        self.items_to_undo[item] = ShoppingUndoRecord(camp, item, price, *args, **kwargs)

    def undo_specific(self, item):
        if item in self.items_to_undo:
            if self.items_to_undo[item].on_undo():
                del self.items_to_undo[item]
                return True

    def undo_all(self):
        for k,my_undo in self.items_to_undo.items():
            my_undo.on_undo()
        self.items_to_undo.clear()

    def get_bought_and_sold(self):
        # Return two numbers: the number of items bought, and the number of items sold.
        b, s = 0, 0
        for undo_rec in self.items_to_undo.values():
            if undo_rec.is_purchase:
                b += 1
            else:
                s += 1
        return b, s

    def get_sold_items(self):
        # Return a list of the items sold.
        return [rec.item for rec in self.items_to_undo.values() if not rec.is_purchase]

    def get_bought_items(self):
        # Return a list of the items bought.
        return [rec.item for rec in self.items_to_undo.values() if rec.is_purchase]

    def actions_have_happened(self):
        return bool(self.items_to_undo)

    def get_undo_action(self, item):
        def undo_action():
            if not self.undo_specific(item):
                return "No take backs."
        return undo_action


###############################################################################



class BuyAction:
    #An undoable buy.
    def __init__( self, camp, shop, ware
                # instance of UndoRedoSystem
                , undo_sys: ShoppingUndoSystem
                , customer_manager
                ):
        self.camp = camp
        self.shop = shop
        # Clone the ware here.
        self.ware = ware
        self.undo_sys = undo_sys
        self.customer_manager =customer_manager

        self.price = self.shop.calc_purchase_price(self.camp, self.ware)

    def __call__(self):
        # Can they buy it?
        if self.camp.credits < self.price:
            return "You can't afford it."

        # Hand it to the customer.
        customer = self.customer_manager.get_customer()
        my_item = copy.deepcopy(self.ware)
        if customer.can_equip(my_item):
            customer.inv_com.append(my_item)
        else:
            self.camp.party.append(my_item)
        # Charge the customer.
        self.camp.credits -= self.price

        # Add the item to the undo manager.
        self.undo_sys.record_undo(self.camp, my_item, self.price)


class SellAction:
    # An undoable sell.
    def __init__( self, camp, shop, ware
                , undo_sys, customer_manager
                ):
        self.camp = camp
        self.shop = shop
        self.ware = ware
        self.undo_sys = undo_sys
        self.customer_manager = customer_manager

        self.customer_manager = customer_manager

        self.price = self.shop.calc_sale_price(self.camp, self.ware)

    def __call__(self):
        # Will the shopkeeper buy it?
        if self.ware.stolen and not self.shop.buy_stolen_items:
            return "I don't buy stolen merchandise."

        # Get it from the customer.
        if hasattr(self.ware, "container") and self.ware.container:
            self.ware.container.remove(self.ware)
        elif self.ware in self.camp.party:
            self.camp.party.remove(self.ware)
        else:
            # Items cannot be returned if I have no idea where they are.
            return "I'm confused... just what are you selling?!"

        self.camp.credits += self.price

        # Add the item to the undo manager.
        self.undo_sys.record_undo(self.camp, self.ware, self.price, is_purchase=False)



