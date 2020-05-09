import pygame
import gears
from gears import tags
import random
import pbge
import copy

MECHA_STORE = (tags.ST_MECHA,)
ARMOR_STORE = (tags.ST_CLOTHING,)
WEAPON_STORE = (tags.ST_WEAPON,)
GENERAL_STORE = (tags.ST_WEAPON,tags.ST_CLOTHING,tags.ST_ESSENTIAL)
MECHA_PARTS_STORE = (tags.ST_MECHA_EQUIPMENT,)
TIRE_STORE = (tags.ST_MECHA_MOBILITY,)
CYBERWARE_STORE = (tags.ST_CYBERWARE,)
GENERAL_STORE_PLUS_MECHA = (tags.ST_WEAPON,tags.ST_CLOTHING,tags.ST_ESSENTIAL,tags.ST_MECHA,tags.ST_MECHA_EQUIPMENT)
BARE_ESSENTIALS_STORE = (tags.ST_ESSENTIAL,)


class CostBlock(object):
    def __init__(self, model, shop, camp, width=360, purchase_price=True, **kwargs):
        self.model = model
        self.shop = shop
        self.width = width
        if purchase_price:
            self.image = pbge.render_text(pbge.BIGFONT, "${:,}".format(shop.calc_purchase_price(camp, model)), width,
                                      justify=0, color=pbge.TEXT_COLOR)
        else:
            self.image = pbge.render_text(pbge.BIGFONT, "${:,}".format(shop.calc_sale_price(camp, model)), width,
                                          justify=0, color=pbge.TEXT_COLOR)
        self.height = self.image.get_height()

    def render(self, x, y):
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class CustomerPanel(object):
    INFO_AREA = pbge.frects.Frect(50, 130, 300, 100)
    def __init__(self,shop,camp):
        self.shop = shop
        self.camp = camp
        self.portraits = dict()
        #self.portraits[shop.customer] = shop.customer.get_portrait()
    def render(self):
        mydest = self.INFO_AREA.get_rect()
        pbge.default_border.render(mydest)
        if self.shop.customer not in self.portraits:
            self.portraits[self.shop.customer] = self.shop.customer.get_portrait()
        self.portraits[self.shop.customer].render(mydest,1)
        mydest.x += 100
        mydest.w -= 100
        pbge.draw_text(pbge.MEDIUMFONT,"{} \n ${:,}".format(str(self.shop.customer),self.camp.credits),mydest,justify=0)

class ShopDesc(object):
    # This is a DescObj for the shop menu.
    SHOP_INFO_AREA = pbge.frects.Frect(-300, -200, 300, 100)
    ITEM_INFO_AREA = pbge.frects.Frect(-300, -80, 300, 300)

    def __init__(self, shop, camp):
        self.shop = shop
        self.camp = camp
        self.buy_info_cache = dict()
        self.customer = CustomerPanel(shop,camp)
        if shop.npc:
            self.portrait = shop.npc.get_portrait()
        else:
            self.portrait = None
        self.caption = ""

    def get_buy_info(self, item):
        if item in self.buy_info_cache:
            return self.buy_info_cache[item]
        else:
            costblock = CostBlock(model = item, width = self.ITEM_INFO_AREA.w, shop = self.shop, camp = self.camp, purchase_price = item in self.shop.wares)
            it = gears.info.get_longform_display(model = item, width = self.ITEM_INFO_AREA.w)
            it.info_blocks.insert(1, costblock)
            self.buy_info_cache[item] = it
            return it

    def __call__(self, menuitem):
        mydest = self.SHOP_INFO_AREA.get_rect()
        pbge.default_border.render(mydest)
        if self.portrait:
            self.portrait.render(mydest,1)
            mydest.x += 100
            mydest.w -= 100
        pbge.draw_text(pbge.MEDIUMFONT,self.caption,mydest)

        mydest = self.ITEM_INFO_AREA.get_rect()
        item = menuitem.value
        if item:
            myinfo = self.get_buy_info(item)
            if myinfo:
                myinfo.render(mydest.x, mydest.y)
        self.customer.render()


class Shop(object):
    MENU_AREA = pbge.frects.Frect(50, -200, 300, 300)

    def __init__(self, ware_types=MECHA_STORE, allow_misc=True, caption="Shop", rank=25, shop_faction=None,
                 num_items=10, turnover=1, npc=None, mecha_colors=None):
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

    def item_matches_shop(self, item):
        if item.get_full_name() in [a.get_full_name() for a in self.wares]:
            return False
        elif self.shop_faction and hasattr(item, "faction_list"):
            if (self.shop_faction in item.faction_list) or (None in item.faction_list):
                return True
        else:
            return True

    def generate_item(self, itype, rank):
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

        # The number of items is highly dependent on friendliness, or more
        # specifically a lack thereof.
        if friendliness < 0:
            num_items = max(5, (self.num_items * (100 + 2 * friendliness)) // 100)
        else:
            num_items = self.num_items + friendliness // 10

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

        # The store rank tracks the party rank, but doesn't quite keep up.
        rank = self.rank
        """if friendliness > 50:
            rank = max( rank, camp.party_rank() )
        elif friendliness > -20:
            rank = max( rank, ( rank + camp.party_rank() ) // 2 )"""

        # Generate one of each type of item this shop stocks first.
        """needed_wares = list( self.ware_types )
        for i in self.wares:
            if i.itemtype in needed_wares:
                needed_wares.remove( i.itemtype )
        for w in needed_wares:
            it = self.generate_item( w, rank )
            if it:
                self.wares.append( it )"""

        # Fill the rest of the store later.
        tries = 0
        while len(self.wares) < num_items:
            tries += 1
            itype = random.choice(self.ware_types)
            it = self.generate_item(itype, rank)
            if it:
                self.wares.append(it)
            elif tries > 100:
                break

    def make_wares_menu(self, camp, shopdesc):
        mymenu = self.get_menu(shopdesc)

        for s in self.wares:
            sname = s.get_full_name()
            scost = str(self.calc_purchase_price(camp, s))
            mymenu.add_item(sname, s)
        mymenu.sort()
        mymenu.add_alpha_keys()
        mymenu.add_item("Exit", False)

        #mymenu.quick_keys[pygame.K_LEFT] = -1
        #mymenu.quick_keys[pygame.K_RIGHT] = 1
        return mymenu

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

    def buy_items(self, camp, shopdesc):
        keep_going = True
        last_selected = None

        while keep_going:
            mymenu = self.make_wares_menu(camp, shopdesc)
            if last_selected:
                mymenu.set_item_by_position(last_selected)
            it = mymenu.query()
            last_selected = mymenu.selected_item
            if it:
                cost = self.calc_purchase_price( camp, it )
                if cost > camp.credits:
                    shopdesc.caption = "You can't afford it!"
                else:
                    it2 = copy.deepcopy( it )

                    if self.customer.can_equip(it2):
                        self.customer.inv_com.append( it2 )
                    else:
                        camp.party.append(it2)
                    self.improve_friendliness( camp, it2 )
                    camp.credits -= cost
                    shopdesc.caption = "You have bought {0}.".format(it2)
            else:
                keep_going = False

    def can_be_sold(self,item):
        if isinstance(item,gears.base.Being):
            return False
        elif hasattr(item,"pilot") and item.pilot:
            return False
        elif hasattr(item,"owner") and item.owner:
            return False
        else:
            return True

    def make_sellitems_menu(self, camp, shopdesc, item_source):
        mymenu = self.get_menu(shopdesc)

        for s in item_source:
            if self.can_be_sold(s):
                sname = s.get_full_name()
                scost = self.calc_sale_price(camp, s)
                mymenu.add_item("{}: ${:,}".format(sname,scost), s)
        mymenu.sort()
        mymenu.add_alpha_keys()
        mymenu.add_item("Exit", False)

        #mymenu.quick_keys[pygame.K_LEFT] = -1
        #mymenu.quick_keys[pygame.K_RIGHT] = 1
        return mymenu

    def calc_sale_price(self, camp, it):
        # Max price = 60%
        percent = 46
        if self.npc:
            f = self.npc.get_reaction_score(camp.pc, camp)
            percent += f//7
        return max((it.cost * percent)//100 , 1)

    def call_sales_backend(self, camp, shopdesc, item_source):
        keep_going = True
        last_selected = None

        while keep_going:
            mymenu = self.make_sellitems_menu(camp, shopdesc, item_source)
            if last_selected:
                mymenu.set_item_by_position(last_selected)
            it = mymenu.query()
            last_selected = mymenu.selected_item
            if it:
                cost = self.calc_sale_price( camp, it )
                camp.credits += cost
                item_source.remove(it)
                shopdesc.caption = "You have sold {} for ${:,}.".format(it,cost)
            else:
                keep_going = False

    def sell_items(self, camp, shopdesc):
        self.call_sales_backend(camp,shopdesc,self.customer.inv_com)

    def sell_mecha(self, camp, shopdesc):
        self.call_sales_backend(camp,shopdesc,camp.party)

    def get_menu(self, menu_desc_fun=None):
        mymenu = pbge.rpgmenu.Menu(self.MENU_AREA.dx, self.MENU_AREA.dy, self.MENU_AREA.w, self.MENU_AREA.h,
                                   font=pbge.BIGFONT)
        mymenu.descobj = menu_desc_fun
        return mymenu

    def enter_shop(self, camp):
        """Find out what the PC wants to do."""
        keep_going = True
        self.customer = camp.pc

        mydesc = ShopDesc(self, camp)

        mymenu = self.get_menu()
        mymenu.add_item("Buy Items", self.buy_items)
        mymenu.add_item("Sell Items", self.sell_items)
        mymenu.add_item("Sell Mecha", self.sell_mecha)
        mymenu.add_item("Exit", False)
        mymenu.add_alpha_keys()

        # mymenu.quick_keys[ pygame.K_LEFT ] = -1
        # mymenu.quick_keys[ pygame.K_RIGHT ] = 1

        while keep_going:
            it = mymenu.query()
            if it is -1:
                pass
            elif it is 1:
                pass
            elif it:
                # A method was selected. Deal with it.
                it(camp, mydesc)
                # myredraw.csheet = self.charsheets[self.pc]
            else:
                keep_going = False

    def update_shop(self, camp):
        if camp.day > self.last_updated:
            self.update_wares(camp)
            self.last_updated = camp.day

    def __call__(self, camp):
        self.update_shop(camp)
        self.enter_shop(camp)
