import pbge
import gears
from . import actions
import pygame

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

class ShopPanel(pbge.widgets.RowWidget):
    '''
    Displays the panel at the upper right, where the shopkeeper
    and what the shopkeeper says is displayed.
    '''

    def __init__(self, shop, camp, undo_sys: actions.ShoppingUndoSystem):
        super().__init__(
            SHOP_PANEL_FRECT.dx, SHOP_PANEL_FRECT.dy, SHOP_PANEL_FRECT.w, SHOP_PANEL_FRECT.h,
            draw_border=True, border=pbge.default_border, padding=0, border_inflation=0
        )
        self.shop = shop
        self.camp = camp
        self.undo_sys = undo_sys

        if shop.npc:
            self.portrait = shop.npc.get_portrait()
        else:
            self.portrait = None

        self.add_left(pbge.widgets.ButtonWidget(
            0, 0, 100, 100, sprite=self.portrait, frame=1
        ))

        self.label = pbge.widgets.LabelWidget(
            0, 0, self.w - 100, self.h, font=pbge.MEDIUMFONT
        )
        self.add_right(self.label)

        self.reset_caption()

    @property
    def caption(self):
        return self.label.text

    @caption.setter
    def caption(self, text):
        self.label.text = text

    def reset_caption(self):
        num_bought, num_sold = self.undo_sys.get_bought_and_sold()
        if num_sold == 0 and num_bought == 0:
            self.caption = 'Enjoy your shopping.'
        elif num_sold == 0:
            self.caption = 'Buying {}.'.format(self._n_items(num_bought))
        elif num_bought == 0:
            self.caption = "Selling {}.".format(self._n_items(num_sold))
        else:
            self.caption = "Buying {} and selling {}.".format(self._n_items(num_bought)
                                                              , self._n_items(num_sold)
                                                              )

    def _n_items(self, n):
        if n == 1:
            return '1 item'
        else:
            return '{} items'.format(n)



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


###############################################################################

class WareMenuData:
    def __init__(self, ware, price, action):
        self.ware = ware
        self.price = price
        self.action = action


class ShopUI(pbge.widgets.Widget):
    def __init__(self, camp, shop, **kwargs):
        super().__init__(UL_X, UL_Y, SCREEN_WIDTH, SCREEN_HEIGHT, **kwargs)

        self.camp = camp
        self.shop = shop

        self.running = False

        self.undo_sys = actions.ShoppingUndoSystem()
        self.shop_panel = ShopPanel(self.shop, self.camp, self.undo_sys)
        self.children.append(self.shop_panel)
        self.customer_manager = ShopCustomerManager(self.shop)
        self.customer_panel = CustomerPanel(self.camp, self.customer_manager)

        self._item_panel = None
        self._hover_action = None

        # Build UI.
        inventory_label = pbge.widgets.LabelWidget(INVENTORY_LABEL_FRECT.dx, INVENTORY_LABEL_FRECT.dy
                                                   , INVENTORY_LABEL_FRECT.w, INVENTORY_LABEL_FRECT.h
                                                   , text="Inventory"
                                                   , justify=0, color=pbge.WHITE
                                                   , font=pbge.BIGFONT
                                                   )
        self.children.append(inventory_label)
        self._sell_list_widget = pbge.widgetmenu.MenuWidget(
            INVENTORY_LIST_FRECT.dx, INVENTORY_LIST_FRECT.dy, INVENTORY_LIST_FRECT.w, INVENTORY_LIST_FRECT.h,
            activate_child_on_enter=True, on_activate_item=self._set_item_panel
        )
        self.children.append(self._sell_list_widget)
        wares_label = pbge.widgets.LabelWidget(WARES_LABEL_FRECT.dx, WARES_LABEL_FRECT.dy
                                               , WARES_LABEL_FRECT.w, WARES_LABEL_FRECT.h
                                               , text="For Sale"
                                               , justify=0, color=pbge.WHITE
                                               , font=pbge.BIGFONT
                                               )
        self.children.append(wares_label)
        self._buy_list_widget = pbge.widgetmenu.MenuWidget(
            WARES_LIST_FRECT.dx, WARES_LIST_FRECT.dy, WARES_LIST_FRECT.w, WARES_LIST_FRECT.h,
            activate_child_on_enter=True, on_activate_item=self._set_item_panel
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

        # Build initial menus.
        self._refresh_ware_lists()
        self._item_panel = None

    REACTIVATE_SELL = 1
    REACTIVATE_BUY = 2

    def _refresh_ware_lists(self):
        # Figure out which of the buy menu or the sell menu is being used right now, because probably one of those has
        # just been used and if the player clicked on an item with their mouse that means that the buy or sell menu
        # is no longer the active menu- the menu item that we're about to delete and replace is.
        # So, we need to remember which menu is being used and re-activate it after rebuilding it.
        # I am writing this out as a long story because it's a cautionary tale for both you and future Joe.
        # It took me far too long to figure out why clicking on a menu item was deselecting the menu and I was
        # looking for the solution in all the wrong places.
        if self._sell_list_widget.is_in_menu(pbge.my_state.active_widget):
            reactivate = self.REACTIVATE_SELL
        elif self._buy_list_widget.is_in_menu(pbge.my_state.active_widget):
            reactivate = self.REACTIVATE_BUY
        else:
            reactivate = 0
        self._build_sell_list()
        self._build_buy_list()
        if reactivate == self.REACTIVATE_SELL:
            pbge.my_state.active_widget = self._sell_list_widget.scroll_column
        elif reactivate == self.REACTIVATE_BUY:
            pbge.my_state.active_widget = self._buy_list_widget.scroll_column

    def _build_sell_list(self):
        active_index = self._sell_list_widget.active_index
        self._sell_list_widget.clear()
        pc = self.customer_manager.get_customer()
        pc_root = pc.get_root()
        source = list(pc.inv_com) + self.camp.party
        bought_items = self.undo_sys.get_bought_items()
        for ware in source:
            if not self.shop.can_be_sold(ware):
                continue
            if ware in bought_items:
                continue
            self._sell_list_widget.add_interior(
                pbge.widgetmenu.MenuItemWidget(
                    0,0,INVENTORY_LIST_FRECT.w, 0,
                    text = ware.get_full_name(),
                    data=WareMenuData(
                        ware=ware, price=self.shop.calc_sale_price(self.camp, ware),
                        action=actions.SellAction(self.camp, self.shop, ware, self.undo_sys, self.customer_manager),
                    ), on_click=self._click_ware, font=pbge.BIGFONT
                )
            )

        # Add returnable items.
        for ware in bought_items:
            if ware in self.camp.party or ware.get_root() is pc_root:
                self._sell_list_widget.add_interior(
                    pbge.widgetmenu.MenuItemWidget(
                        0, 0, INVENTORY_LIST_FRECT.w, 0,
                        text="{} [Bought]".format(ware.get_full_name()),
                        data=WareMenuData(
                            ware=ware, price=self.undo_sys.items_to_undo[ware].price,
                            action=self.undo_sys.get_undo_action(ware),
                        ), on_click=self._click_ware, font=pbge.BIGFONT
                    )
                )
        self._sell_list_widget.sort(key=lambda a: str(a))
        self._sell_list_widget.active_index = active_index

    def _build_buy_list(self):
        active_index = self._buy_list_widget.active_index
        self._buy_list_widget.clear()
        for ware in self.shop.wares:
            self._buy_list_widget.add_interior(
                pbge.widgetmenu.MenuItemWidget(
                    0, 0, INVENTORY_LIST_FRECT.w, 0,
                    text=ware.get_full_name(),
                    data=WareMenuData(
                        ware=ware, price=self.shop.calc_purchase_price(self.camp, ware),
                        action=actions.BuyAction(self.camp, self.shop, ware, self.undo_sys, self.customer_manager),
                    ), on_click=self._click_ware, font=pbge.BIGFONT
                )
            )

        # Add cancelable sales.
        for ware in self.undo_sys.get_sold_items():
            self._buy_list_widget.add_interior(
                pbge.widgetmenu.MenuItemWidget(
                    0, 0, INVENTORY_LIST_FRECT.w, 0,
                    text="{} [Sold]".format(ware.get_full_name()),
                    data=WareMenuData(
                        ware=ware, price=self.undo_sys.items_to_undo[ware].price,
                        action=self.undo_sys.get_undo_action(ware),
                    ), on_click=self._click_ware, font=pbge.BIGFONT
                )
            )

        self._buy_list_widget.sort(key=lambda a: str(a))
        self._buy_list_widget.active_index = active_index

    def _set_item_panel(self, colwidget, warewidget):
        if warewidget and isinstance(warewidget.data, WareMenuData):
            ip = gears.info.get_longform_display(model=warewidget.data.ware
                                                 , width=INFO_PANEL_FRECT.w
                                                 )
            ip.info_blocks.insert(1, _CostBlock(cost=warewidget.data.price
                                                , width=INFO_PANEL_FRECT.w
                                                ))
            self._item_panel = ip
        #else:
        #    self._item_panel = None

    def _click_ware(self, ware_widget, *etc):
        text = ware_widget.data.action()
        if text:
            self.shop_panel.caption = text
        else:
            self.shop_panel.reset_caption()
        self._refresh_ware_lists()

    def _checkout(self, *etc):
        self.running = False

    def _on_escape_key(self):
        '''
        Done when escape key is pressed while displaying the shop.
        '''
        if self.undo_sys.actions_have_happened():
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
                self.undo_sys.undo_all()
        self.running = False

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
        if self.undo_sys.actions_have_happened():
            pbge.my_state.start_sound_effect("purchase2.ogg")
        for item in self.undo_sys.get_bought_items():
            self.shop.improve_friendliness(self.camp, item)

    def render(self, flash=False):
        super().render()
        self.customer_panel.render()
        if self._item_panel:
            rect = INFO_PANEL_FRECT.get_rect()
            self._item_panel.render(rect.x, rect.y)
