import pbge
from game import widgets
import gears
from . import actions
import pygame

ItemListWidget = widgets.ItemListWidget
UndoRedoSystem = actions.UndoRedoSystem
BuySellCounters = actions.BuySellCounters
ListsManager = actions.ListsManager
BuyAction = actions.BuyAction
SellAction = actions.SellAction

###############################################################################

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MARGIN = 24

UL_X = -SCREEN_WIDTH // 2
UL_Y = -SCREEN_HEIGHT // 2

INFO_PANEL_WIDTH = 280

COLUMN_WIDTH = (SCREEN_WIDTH - MARGIN * 4 - INFO_PANEL_WIDTH) // 2

HEADER_HEIGHT = 100
LABEL_HEIGHT = 22
BUTTON_HEIGHT = 24

COL_1 = UL_X + MARGIN
COL_2 = COL_1 + COLUMN_WIDTH + MARGIN
COL_3 = COL_2 + INFO_PANEL_WIDTH + MARGIN

TOP_Y = UL_Y + MARGIN
LABEL_Y = TOP_Y + HEADER_HEIGHT + MARGIN
LIST_Y = LABEL_Y + LABEL_HEIGHT + MARGIN

LIST_HEIGHT = SCREEN_HEIGHT - MARGIN - HEADER_HEIGHT - MARGIN - LABEL_HEIGHT - MARGIN * 3

CUSTOMER_PANEL_FRECT = pbge.frects.Frect(COL_1, TOP_Y
                                         , COLUMN_WIDTH, HEADER_HEIGHT
                                         )
SHOP_PANEL_FRECT = pbge.frects.Frect(COL_3, TOP_Y
                                     , COLUMN_WIDTH, HEADER_HEIGHT
                                     )
INVENTORY_LABEL_FRECT = pbge.frects.Frect(COL_1, LABEL_Y
                                          , COLUMN_WIDTH, LABEL_HEIGHT
                                          )
INVENTORY_LIST_FRECT = pbge.frects.Frect(COL_1, LIST_Y
                                         , COLUMN_WIDTH, LIST_HEIGHT
                                         )
INFO_PANEL_FRECT = pbge.frects.Frect(COL_2, TOP_Y
                                     , INFO_PANEL_WIDTH, SCREEN_HEIGHT
                                     )
CHECKOUT_BUTTON_FRECT = pbge.frects.Frect(COL_2, UL_Y + SCREEN_HEIGHT - MARGIN - BUTTON_HEIGHT
                                          , INFO_PANEL_WIDTH, BUTTON_HEIGHT
                                          )
WARES_LABEL_FRECT = pbge.frects.Frect(COL_3, LABEL_Y
                                      , COLUMN_WIDTH, LABEL_HEIGHT
                                      )
WARES_LIST_FRECT = pbge.frects.Frect(COL_3, LIST_Y
                                     , COLUMN_WIDTH, LIST_HEIGHT
                                     )

EXITMENU_WIDTH = int(SCREEN_WIDTH / 2)
EXITMENU_HEIGHT = int(SCREEN_HEIGHT / 2.5)


###############################################################################

class ShopPanel(BuySellCounters):
    '''
    Displays the panel at the upper right, where the shopkeeper
    and what the shopkeeper says is displayed.
    '''

    def __init__(self, shop, camp):
        self.shop = shop
        self.camp = camp
        self._num_sold = 0
        self._num_bought = 0
        self._bought = list()
        self.caption = ''

        if shop.npc:
            self.portrait = shop.npc.get_portrait()
        else:
            self.portrait = None

        self._set_caption()

    def _set_caption(self):
        if self._num_sold == 0 and self._num_bought == 0:
            self.caption = 'Enjoy your shopping.'
        elif self._num_sold == 0:
            self.caption = 'Buying {}.'.format(self._n_items(self._num_bought))
        elif self._num_bought == 0:
            self.caption = "Selling {}.".format(self._n_items(self._num_sold))
        else:
            self.caption = "Buying {} and selling {}.".format(self._n_items(self._num_bought)
                                                              , self._n_items(self._num_sold)
                                                              )

    def _n_items(self, n):
        if n == 1:
            return '1 item'
        else:
            return '{} items'.format(n)

    def set_cannot_afford(self):
        self.caption = "You can't afford it!"

    def set_no_stolen_goods(self):
        self.caption = "I don't buy stolen merchandise."

    @property
    def num_bought(self):
        return self._num_bought

    @num_bought.setter
    def num_bought(self, v):
        self._num_bought = v
        self._set_caption()

    @property
    def num_sold(self):
        return self._num_sold

    @num_sold.setter
    def num_sold(self, v):
        self._num_sold = v
        self._set_caption()

    @property
    def bought(self):
        return self._bought

    def render(self, flash):
        myrect = SHOP_PANEL_FRECT.get_rect()
        pbge.default_border.render(myrect)
        if self.portrait:
            self.portrait.render(myrect, 1)
            myrect.x += 100
            myrect.w -= 100
        pbge.draw_text(pbge.MEDIUMFONT, self.caption, myrect)


###############################################################################

class ShopCustomerManager:
    def __init__(self, shop):
        self.customer = shop.customer

    def get_customer(self):
        return self.customer


###############################################################################

class _CostBlock(object):
    def __init__(self, cost, width):
        self._cost = cost
        self.width = width
        msg = '${:,}'.format(cost)
        self.image = pbge.render_text(pbge.BIGFONT, msg, self.width
                                      , justify=0, color=pbge.TEXT_COLOR
                                      )
        self.height = self.image.get_height()

    def render(self, x, y):
        pbge.my_state.screen.blit(self.image
                                  , pygame.Rect(x, y, self.width, self.height)
                                  )


###############################################################################

class CustomerPanelIP(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.NameBlock, gears.info.CreditsBlock, gears.info.EncumberanceBlock)


class NoCustomerPanelIP(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.CreditsBlock,)


class CustomerPanel(object):
    '''
    Displays the customer and the money money money.
    '''

    def __init__(self, camp, customer_manager):
        self.camp = camp
        self.customer_manager = customer_manager
        self._portraits = dict()
        self._infopanels = dict()
        self._no_customer_ip = NoCustomerPanelIP(draw_border=False, width=CUSTOMER_PANEL_FRECT.w - 100, camp=self.camp)

    def render(self):
        myrect = CUSTOMER_PANEL_FRECT.get_rect()
        pbge.default_border.render(myrect)
        customer = self.customer_manager.get_customer()
        if customer:
            if customer not in self._portraits:
                self._portraits[customer] = customer.get_portrait()
            if customer not in self._infopanels:
                self._infopanels[customer] = CustomerPanelIP(draw_border=False, width=myrect.w - 100, model=customer,
                                                             camp=self.camp)
            self._portraits[customer].render(myrect, 1)
            myrect.x += 100
            myrect.w -= 100
            ip = self._infopanels[customer]
            customertext = customer.name + '\n'
        else:
            customertext = ''
            ip = self._no_customer_ip

        ip.render(myrect.x, myrect.y)
        # pbge.draw_text( pbge.MEDIUMFONT
        #              , '{} ${:,}'.format(customertext, self.camp.credits)
        #              , myrect
        #              )


###############################################################################

class ShopListsManager(ListsManager):
    '''
    Manages the raw list objects for the sell and buy actions
    on behalf of the shop.
    '''

    def __init__(self
                 , sell_list, buy_list
                 # These are called with a single argument, the
                 # list index that should get displayed.
                 # It may also be given a None argument, in
                 # which case there is no particular index.
                 , on_sell_list_update, on_buy_list_update
                 # Instance of ShopPanel
                 , shop_panel
                 ):
        self.sell_list = sell_list
        self.buy_list = buy_list
        self.on_sell_list_update = on_sell_list_update
        self.on_buy_list_update = on_buy_list_update
        self.shop_panel = shop_panel

    def _find_insert_index(self, l, action):
        # Find the index to insert into.
        # We *could* use binary search followed by scanning
        # for actions with the same label, but premature
        # optimization...
        for i, a in enumerate(l):
            if action.label <= a.label:
                return i
        return len(l)

    def _add_to_list(self, l, action, on_update):
        i = self._find_insert_index(l, action)
        l.insert(i, action)
        on_update(i)

    def _remove_from_list(self, l, action, on_update):
        if action in l:
            l.remove(action)
            on_update(None)

    def add_sell_action(self, action):
        self._add_to_list(self.sell_list, action, self.on_sell_list_update)

    def remove_sell_action(self, action):
        self._remove_from_list(self.sell_list, action, self.on_sell_list_update)

    def add_buy_action(self, action):
        self._add_to_list(self.buy_list, action, self.on_buy_list_update)

    def remove_buy_action(self, action):
        self._remove_from_list(self.buy_list, action, self.on_buy_list_update)

    def cannot_afford(self):
        self.shop_panel.set_cannot_afford()

    def no_stolen_goods(self):
        self.shop_panel.set_no_stolen_goods()


###############################################################################

class ShopUI(pbge.widgets.Widget):
    def __init__(self, camp, shop, **kwargs):
        super().__init__(UL_X, UL_Y, SCREEN_WIDTH, SCREEN_HEIGHT, **kwargs)

        self.camp = camp
        self.shop = shop

        self.running = False

        self.undo_redo_sys = UndoRedoSystem()
        self.shop_panel = ShopPanel(self.shop, self.camp)
        self.customer_manager = ShopCustomerManager(self.shop)
        self.customer_panel = CustomerPanel(self.camp, self.customer_manager)

        self.sell_list = list()
        self.buy_list = list()

        self.shop_lists_manager = ShopListsManager(self.sell_list
                                                   , self.buy_list
                                                   , self._on_sell_list_update
                                                   , self._on_buy_list_update
                                                   , self.shop_panel
                                                   )

        # Build initial sell list.
        self._build_sell_list(self.customer_manager.get_customer().inv_com)
        self._build_sell_list(self.camp.party)
        self.sell_list.sort(key=lambda a: a.label)
        # Build initial buy list.
        for ware in self.shop.wares:
            self.buy_list.append(BuyAction(self.camp, self.shop, ware
                                           , self.undo_redo_sys
                                           , self.shop_panel
                                           , self.shop_lists_manager
                                           , self.customer_manager
                                           ))
        self.buy_list.sort(key=lambda a: a.label)

        self._item_panel = None
        self._hover_action = None

        # Build UI.
        inventory_label = pbge.widgets.LabelWidget(INVENTORY_LABEL_FRECT.dx, INVENTORY_LABEL_FRECT.dy
                                                   , INVENTORY_LABEL_FRECT.w, INVENTORY_LABEL_FRECT.h
                                                   , text="Inventory"
                                                   , justify=0
                                                   , font=pbge.BIGFONT
                                                   )
        self.children.append(inventory_label)
        self._sell_list_widget = ItemListWidget(self.sell_list
                                                , INVENTORY_LIST_FRECT
                                                , text_fn=lambda a: a.label
                                                , on_enter=self._set_item_panel
                                                , on_leave=self._clear_item_panel
                                                , on_select=self._select_item
                                                )
        self.children.append(self._sell_list_widget)
        wares_label = pbge.widgets.LabelWidget(WARES_LABEL_FRECT.dx, WARES_LABEL_FRECT.dy
                                               , WARES_LABEL_FRECT.w, WARES_LABEL_FRECT.h
                                               , text="For Sale"
                                               , justify=0
                                               , font=pbge.BIGFONT
                                               )
        self.children.append(wares_label)
        self._buy_list_widget = ItemListWidget(self.buy_list
                                               , WARES_LIST_FRECT
                                               , text_fn=lambda a: a.label
                                               , on_enter=self._set_item_panel
                                               , on_leave=self._clear_item_panel
                                               , on_select=self._select_item
                                               )
        self.children.append(self._buy_list_widget)
        checkout_button = pbge.widgets.LabelWidget(CHECKOUT_BUTTON_FRECT.dx, CHECKOUT_BUTTON_FRECT.dy
                                                   , CHECKOUT_BUTTON_FRECT.w, CHECKOUT_BUTTON_FRECT.h
                                                   , text="Checkout"
                                                   , justify=0
                                                   , draw_border=True
                                                   , font=pbge.MEDIUMFONT
                                                   , on_click=self._checkout
                                                   )
        self.children.append(checkout_button)

    def _build_sell_list(self, source):
        for ware in source:
            if not self.shop.can_be_sold(ware):
                continue
            self.sell_list.append(SellAction(self.camp, self.shop, ware
                                             , self.undo_redo_sys
                                             , self.shop_panel
                                             , self.shop_lists_manager
                                             , self.customer_manager
                                             ))

    def _set_item_panel(self, action, *etc):
        ip = gears.info.get_longform_display(model=action.model
                                             , width=INFO_PANEL_FRECT.w
                                             )
        ip.info_blocks.insert(1, _CostBlock(cost=action.cost
                                            , width=INFO_PANEL_FRECT.w
                                            ))
        self._item_panel = ip
        self._hover_action = action

    def _clear_item_panel(self, action, *etc):
        if self._hover_action is action:
            self._item_panel = None
            self._hover_action = None

    def _select_item(self, action, *etc):
        action()
        self._sell_list_widget.deselect()
        self._buy_list_widget.deselect()

    def _checkout(self, *etc):
        self.running = False

    def _on_escape_key(self):
        '''
        Done when escape key is pressed while displaying the shop.
        '''
        if self.shop_panel.num_bought != 0 or self.shop_panel.num_sold != 0:
            # Ask if we should abort or not.
            mymenu = pbge.rpgmenu.Menu(-EXITMENU_WIDTH // 2, -EXITMENU_HEIGHT // 2
                                       , EXITMENU_WIDTH, EXITMENU_HEIGHT
                                       , font=pbge.BIGFONT
                                       )
            mymenu.add_item('Continue Shopping', 0)
            mymenu.add_item('Finalize Transactions', 1)
            mymenu.add_item('Cancel All Transactions', 2)
            res = mymenu.query()
            if not res:
                # Keep on going on.
                self.running = True
                return
            if res == 2:
                self.undo_redo_sys.undo_all()
        self.running = False

    def _on_sell_list_update(self, index):
        self._sell_list_widget.refresh_item_list()
        if index is not None:
            self._sell_list_widget.scroll_to_index(index)

    def _on_buy_list_update(self, index):
        self._buy_list_widget.refresh_item_list()
        if index is not None:
            self._buy_list_widget.scroll_to_index(index)

    def activate_and_run(self):
        pbge.my_state.widgets.append(self)
        self.running = True
        while self.running and not pbge.my_state.got_quit:
            ev = pbge.wait_event()
            if ev.type == pbge.TIMEREVENT:
                pbge.my_state.view()
                pbge.my_state.do_flip()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self._on_escape_key()
        pbge.my_state.widgets.remove(self)
        # Improve friendliness for all items bought.
        if self.shop_panel.num_bought > 0 or self.shop_panel.num_sold > 0:
            pbge.my_state.start_sound_effect("purchase2.ogg")
        for item in self.shop_panel.bought:
            self.shop.improve_friendliness(self.camp, item)

    def render(self, flash=False):
        super().render()
        self.shop_panel.render(flash)
        self.customer_panel.render()
        if self._item_panel:
            rect = INFO_PANEL_FRECT.get_rect()
            self._item_panel.render(rect.x, rect.y)
