import pygame
import gears
from gears import tags
import random
import pbge
import copy

MECHA_STORE = (tags.ST_MECHA,tags.ST_WEAPON,tags.ST_CLOTHING)
WEAPON_STORE = (tags.ST_WEAPON,)
GENERAL_STORE = (tags.ST_WEAPON,tags.ST_ESSENTIAL)


class CostBlock(object):
    def __init__(self, model, shop, camp, width=360, **kwargs):
        self.model = model
        self.shop = shop
        self.width = width
        self.image = pbge.render_text(pbge.BIGFONT, "${:,}".format(shop.calc_purchase_price(camp, model)), width,
                                      justify=0, color=pbge.TEXT_COLOR)
        self.height = self.image.get_height()

    def render(self, x, y):
        pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))


class MechaBuyIP(gears.info.InfoPanel):
    # A floating status display, drawn wherever the mouse is pointing.
    DEFAULT_BLOCKS = (gears.info.FullNameBlock, CostBlock, gears.info.MechaFeaturesAndSpriteBlock, gears.info.DescBlock)

class ItemBuyIP(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.FullNameBlock, CostBlock, gears.info.MassVolumeBlock, gears.info.DescBlock)

class WeaponBuyIP(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.FullNameBlock, CostBlock, gears.info.MassVolumeBlock, gears.info.WeaponStatsBlock, gears.info.ItemStatsBlock, gears.info.WeaponSkillBlock, gears.info.WeaponAttributesBlock, gears.info.DescBlock)

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
        elif isinstance(item, gears.base.Mecha):
            it = MechaBuyIP(model=item, shop=self.shop, camp=self.camp, width=self.ITEM_INFO_AREA.w)
        elif isinstance(item, gears.base.Weapon):
            it = WeaponBuyIP(model=item, shop=self.shop, camp=self.camp, width=self.ITEM_INFO_AREA.w)
        else:
            it = ItemBuyIP(model=item, shop=self.shop, camp=self.camp, width=self.ITEM_INFO_AREA.w)
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
                 num_items=25, turnover=1, npc=None, mecha_colors=None):
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
        # TODO: Make rank work properly.
        candidates = [item for item in gears.selector.DESIGN_LIST if
                      itype in item.shop_tags and self.item_matches_shop(item)]
        if candidates:
            it = copy.deepcopy(random.choice(candidates))
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

        mymenu.quick_keys[pygame.K_LEFT] = -1
        mymenu.quick_keys[pygame.K_RIGHT] = 1
        return mymenu

    def improve_friendliness(self, camp, item, modifier=0):
        """Dealing with a shopkeeper will generally increase friendliness."""
        """if self.npc:
            target = abs( self.npc.get_friendliness( camp ) ) + 50 - 5 * item.min_rank()
            roll = random.randint( 1, 100 ) + camp.party_spokesperson().get_stat_bonus( stats.CHARISMA ) + modifier
            if roll > target:
                self.npc.friendliness += ( roll - target + 9 ) // 10
        """
        pass

    def calc_purchase_price(self, camp, item):
        """The sale price of an item depends on friendliness."""
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

    def sale_price(self, it):
        return max(it.cost // 2, 1)

    def sell_items(self, camp, shopdesc):
        """
        keep_going = True
        myredraw = charsheet.CharacterViewRedrawer( csheet=self.charsheets[self.pc], screen=explo.screen, predraw=explo.view, caption="Sell Items" )
        last_item = 1;

        while keep_going:
            mymenu = charsheet.RightMenu( explo.screen, predraw = myredraw )

            self.pc.contents.tidy()
            for s in self.pc.contents:
                if s.equipped:
                    mymenu.add_item( "*{0} ({1}gp)".format( s, self.sale_price( s )), s )
                elif s.slot != items.NOSLOT and not self.pc.can_equip(s):
                    mymenu.add_item( "#{0} ({1}gp)".format( s, self.sale_price( s ) ), s )
                else:
                    mymenu.add_item( "{0} ({1}gp)".format( s, self.sale_price( s ) ), s )
            mymenu.sort()
            mymenu.add_alpha_keys()
            mymenu.add_item( "Exit", False )
            mymenu.set_item_by_position( last_item )
            myredraw.menu = mymenu
            mymenu.quick_keys[ pygame.K_LEFT ] = -1
            mymenu.quick_keys[ pygame.K_RIGHT ] = 1

            it = mymenu.query()
            last_item = mymenu.selected_item
            if it is -1:
                n = ( explo.camp.party.index(self.pc) + len( explo.camp.party ) - 1 ) % len( explo.camp.party )
                self.pc = explo.camp.party[n]
                myredraw.csheet = self.charsheets[self.pc]
            elif it is 1:
                n = ( explo.camp.party.index(self.pc) + 1 ) % len( explo.camp.party )
                self.pc = explo.camp.party[n]
                myredraw.csheet = self.charsheets[self.pc]
            elif it:
                # An item was selected. Deal with it.
                self.pc.contents.remove( it )
                explo.camp.gold += self.sale_price( it )
                self.improve_friendliness( explo, it, modifier=-20 )
                if it.enhancement:
                    it.identified = True
                    self.wares.append( it )
                myredraw.caption = "You have sold {0}.".format(it)
                if it.equipped:
                    myredraw.csheet.regenerate_avatar()
                    explo.view.regenerate_avatars( explo.camp.party )

            else:
                keep_going = False
        """


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

    def __call__(self, camp):
        if camp.day > self.last_updated:
            self.update_wares(camp)
            self.last_updated = camp.day

        self.enter_shop(camp)
