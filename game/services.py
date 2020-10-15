import pygame
import gears
from gears import tags
from gears import champions
import random
import pbge
import copy
from . import shopui

MECHA_STORE = (tags.ST_MECHA,)
MEXTRA_STORE = (tags.ST_MECHA,tags.ST_MECHA_WEAPON)
ARMOR_STORE = (tags.ST_CLOTHING,)
WEAPON_STORE = (tags.ST_WEAPON,)
GENERAL_STORE = (tags.ST_WEAPON,tags.ST_CLOTHING,tags.ST_ESSENTIAL)
MECHA_PARTS_STORE = (tags.ST_MECHA_EQUIPMENT,)
MECHA_WEAPON_STORE = (tags.ST_MECHA_WEAPON,)
TIRE_STORE = (tags.ST_MECHA_MOBILITY,)
CYBERWARE_STORE = (tags.ST_CYBERWARE,)
GENERAL_STORE_PLUS_MECHA = (tags.ST_WEAPON,tags.ST_CLOTHING,tags.ST_ESSENTIAL,tags.ST_MECHA,tags.ST_MECHA_EQUIPMENT)
BARE_ESSENTIALS_STORE = (tags.ST_ESSENTIAL,)

class Shop(object):
    MENU_AREA = pbge.frects.Frect(50, -200, 300, 300)

    def __init__(self, ware_types=MECHA_STORE, allow_misc=True, caption="Shop", rank=25, shop_faction=None,
                 num_items=10, turnover=1, npc=None, mecha_colors=None, sell_champion_equipment=False):
        self.wares = list()
        self.ware_types = ware_types
        self.allow_misc = allow_misc
        self.caption = caption
        self.rank = rank
        self.num_items = num_items
        self.turnover = turnover
        self.last_updated = -1
        self.npc = npc
        self.shopper = None
        self.shop_faction = shop_faction
        self.mecha_colors = mecha_colors or gears.color.random_mecha_colors()
        self.customer = None
        self.sell_champion_equipment = sell_champion_equipment

    def item_matches_shop(self, item):
        if item.get_full_name() in [a.get_full_name() for a in self.wares]:
            return False
        elif self.shop_faction and hasattr(item, "faction_list"):
            if (self.shop_faction in item.faction_list) or (None in item.faction_list):
                return True
        else:
            return True

    def _pick_an_item(self, itype, rank):
        candidates = [item for item in gears.selector.DESIGN_LIST if
                      itype in item.shop_tags and self.item_matches_shop(item)]
        if candidates:
            # Step one: Sort the candidates by cost.
            random.shuffle(candidates)
            candidates.sort(key=lambda i: i.cost)
            # Step two: Determine this store's ideal index position.
            ideal_index = len(candidates) * min(max(rank,0),100) / 100.0
            # Step three: Create a new list sorted by distance from ideal_index.
            sorted_candidates = candidates.copy()
            sorted_candidates.sort(key=lambda i: abs(candidates.index(i) - ideal_index))
            # Step four: Choose an item, the lower the better.
            max_i = min(len(candidates)-1,max(5,len(candidates)//3))
            i = min(random.randint(0,max_i),random.randint(0,max_i),random.randint(0,max_i))
            it = copy.deepcopy(sorted_candidates[i])
            if isinstance(it, gears.base.Mecha):
                it.colors = self.mecha_colors
            if self.sell_champion_equipment and random.randint(1,3) == 1:
                if isinstance(it, gears.base.Mecha):
                    champions.upgrade_to_champion(it)
                elif it.scale == gears.scale.MechaScale and isinstance(it, (gears.base.Component, gears.base.Shield, gears.base.Launcher)):
                    champions.upgrade_item_to_champion(it)

            return it


    def generate_item(self, itype, rank):
        tries = 0
        while tries < 10:
            it = self._pick_an_item(itype, rank)
            # Avoid duplicates.
            if it.get_full_name() not in [a.get_full_name() for a in self.wares]:
                return it
            tries = tries + 1
        return it


    def update_wares(self, camp):
        # Once a day the wares get updated. Delete some items, make sure that
        # there's at least one item of every ware_type, and then fill up the
        # store to full capacity.

        # A lot of stuff about the wares is going to depend on the shopkeeper's
        # friendliness.
        if self.npc:
            friendliness = self.npc.get_reaction_score(camp.pc, camp)
        else:
            friendliness = 0

        # Find prosperity of the town, if possible.
        metro = camp.scene.get_metro_scene()
        if metro:
            prosperity = metro.metrodat.get_quality_of_life().prosperity
        else:
            prosperity = 0

        # The number of items is highly dependent on friendliness, or more
        # specifically a lack thereof.
        if friendliness < 0:
            num_items = max(5, (self.num_items * (100 + 2 * friendliness)) // 100)
        else:
            num_items = self.num_items + friendliness // 10

        if prosperity < 0:
            num_items = max(num_items+prosperity, 1)

        # Get rid of some of the old stock, to make room for new stock.
        while len(self.wares) > num_items:
            it = random.choice(self.wares)
            self.wares.remove(it)
        days = camp.day - self.last_updated
        for n in range(max(3, (random.randint(1, 6) + days) * self.turnover)):
            if self.wares:
                it = random.choice(self.wares)
                self.wares.remove(it)
            else:
                break

        rank = self.rank + prosperity * 10

        tries = 0
        while len(self.wares) < num_items:
            tries += 1
            itype = random.choice(self.ware_types)
            it = self.generate_item(itype, rank)
            if it:
                self.wares.append(it)
            elif tries > 100:
                break

    def improve_friendliness(self, camp, item, modifier=0):
        """Dealing with a shopkeeper will generally increase friendliness."""
        if self.npc:
            target = abs( self.npc.get_reaction_score( self.customer, camp ) ) + 50
            roll = random.randint( 1, 100 ) + camp.get_party_skill(gears.stats.Charm,gears.stats.Negotiation) + modifier
            if roll > target:
                self.npc.relationship.reaction_mod += random.randint(1,6)

    def calc_purchase_price(self, camp, item):
        """The sale price of an item depends on friendliness. Min price = 70%"""
        it = item.cost
        if self.npc:
            f = self.npc.get_reaction_score(camp.pc, camp)
            if f < 0:
                it = (it * (120 - 2 * f)) // 100
            else:
                it = (it * (240 - f)) // 200
        return it

    def can_be_sold(self,item):
        if isinstance(item,gears.base.Being):
            return False
        elif hasattr(item,"pilot") and item.pilot:
            return False
        elif hasattr(item,"owner") and item.owner:
            return False
        else:
            return True

    def calc_sale_price(self, camp, it):
        # Max price = 60%
        percent = 46
        if self.npc:
            f = self.npc.get_reaction_score(camp.pc, camp)
            percent += f//7
        return max((it.cost * percent)//100 , 1)

    def enter_shop(self, camp):
        self.customer = camp.pc
        ui = shopui.ShopUI(camp, self)
        ui.activate_and_run()

    def update_shop(self, camp):
        if camp.day > self.last_updated:
            self.update_wares(camp)
            self.last_updated = camp.day

    def __call__(self, camp):
        self.update_shop(camp)
        self.enter_shop(camp)


