import copy

import pbge
import gears
from pbge import my_state
from . import actions
import pygame
from game import fieldhq

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

LEFT_HEADER_HEIGHT = 155

COL_1 = UL_X + MARGIN
COL_2 = COL_1 + COLUMN_WIDTH + MARGIN
COL_3 = COL_2 + INFO_PANEL_WIDTH + MARGIN

TOP_Y = UL_Y + MARGIN
LABEL_Y = TOP_Y + HEADER_HEIGHT + MARGIN
LIST_Y = LABEL_Y + LABEL_HEIGHT + MARGIN

LEFT_LIST_HEIGHT = SCREEN_HEIGHT - MARGIN - LEFT_HEADER_HEIGHT - MARGIN * 4
LEFT_LIST_Y = TOP_Y + LEFT_HEADER_HEIGHT + MARGIN * 2

RIGHT_LIST_HEIGHT = SCREEN_HEIGHT - MARGIN - HEADER_HEIGHT - MARGIN - LABEL_HEIGHT - MARGIN * 3

CUSTOMER_PANEL_FRECT = pbge.frects.Frect(COL_1, TOP_Y
                                         , COLUMN_WIDTH, LEFT_HEADER_HEIGHT
                                         )
SHOP_PANEL_FRECT = pbge.frects.Frect(COL_3, TOP_Y
                                     , COLUMN_WIDTH, HEADER_HEIGHT
                                     )
INVENTORY_LIST_FRECT = pbge.frects.Frect(COL_1, LEFT_LIST_Y
                                         , COLUMN_WIDTH, LEFT_LIST_HEIGHT
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
                                     , COLUMN_WIDTH, RIGHT_LIST_HEIGHT
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

class _CostBlock(object):
    def __init__(self, cost, width):
        self._cost = cost
        self.width = width
        msg = '${:,}'.format(cost)
        self.image = pbge.render_text(pbge.MEDIUM_DISPLAY_FONT, msg, self.width
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


class CustomerPanelWidget(pbge.widgets.ColumnWidget):
    '''
    Displays the panel at the upper left, where the customer
    and customer info is displayed.
    '''

    def __init__(self, camp: gears.GearHeadCampaign, refresh_lists_fun, open_backpack_fun):
        super().__init__(
            CUSTOMER_PANEL_FRECT.dx, CUSTOMER_PANEL_FRECT.dy, CUSTOMER_PANEL_FRECT.w, CUSTOMER_PANEL_FRECT.h,
            draw_border=True, border=pbge.default_border, center_interior=True
        )

        self.camp = camp
        self.refresh_lists_fun = refresh_lists_fun
        self._pc = camp.first_active_pc()

        myrow = pbge.widgets.RowWidget(
            0, 0, self.w, CUSTOMER_PANEL_FRECT.h - 100, draw_border=False,
        )

        self.info_widget_width = self.w - 50    # Magic number is the width of the Backpack button.
        self.info_widget = gears.info.InfoWidget(
            0, 0, self.info_widget_width, CUSTOMER_PANEL_FRECT.h - 100, info_panel=None
        )
        self.player_switcher = fieldhq.backpack.PlayerCharacterSwitch(camp, self._pc, set_pc_fun=self._set_pc)
        self.backpack_button = pbge.widgets.ButtonWidget(
            0, 0, 49, 55, sprite=pbge.image.Image("sys_backpack2.png"), tooltip="Open Backpack",
            on_click=open_backpack_fun
        )
        self.add_interior(self.player_switcher)
        self.add_interior(myrow)
        myrow.add_right(self.backpack_button)
        myrow.add_left(self.info_widget)

        self._set_pc(self._pc)
        print(COLUMN_WIDTH)

    def _set_pc(self, pc):
        self._pc = pc
        self.info_widget.info_panel = CustomerPanelIP(
            draw_border=False, width=self.info_widget_width, model=self._pc, camp=self.camp
        )
        self.refresh_lists_fun()

    def get_customer(self):
        return self._pc


###############################################################################

class WareMenuData:
    def __init__(self, ware, price, action, sort_order=0):
        self.ware = ware
        self.price = price
        self.action = action
        self.sort_order = sort_order


class ShopUI(pbge.widgets.Widget):
    def __init__(self, camp, shop, **kwargs):
        # Note that the order in which the sub-widgets are initialized is a finely tuned machine. It's that
        # PlayerSelectorWidget that causes all the problems because it expects everything to be set up and ready by
        # the time it's initialized.
        super().__init__(UL_X, UL_Y, SCREEN_WIDTH, SCREEN_HEIGHT, **kwargs)

        self.camp = camp
        self.shop = shop

        self.running = False

        self.undo_sys = actions.ShoppingUndoSystem()
        self.shop_panel = ShopPanel(self.shop, self.camp, self.undo_sys)
        self.children.append(self.shop_panel)

        self._item_panel = None

        # Build UI.
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

        self._style = dict(font=pbge.MEDIUM_DISPLAY_FONT)
        self._special_wares = list()

        self.customer_manager = CustomerPanelWidget(self.camp, self._refresh_ware_lists, self._open_backpack)
        self.children.append(self.customer_manager)

        # Build initial menus.
        self._refresh_ware_lists()
        self._item_panel = None

    REACTIVATE_SELL = 1
    REACTIVATE_BUY = 2

    def _open_backpack(self, *args, **kwargs):
        pc = self.customer_manager.get_customer()
        if pc:
            my_state.widgets.remove(self)
            fieldhq.backpack.BackpackWidget.create_and_invoke(self.camp, pc)
            my_state.widgets.append(self)
            self._refresh_ware_lists()

    def _refresh_ware_lists(self):
        # Figure out which of the buy menu or the sell menu is being used right now, because probably one of those has
        # just been used and if the player clicked on an item with their mouse that means that the buy or sell menu
        # is no longer the active menu- the menu item that we're about to delete and replace is.
        # So, we need to remember which menu is being used and re-activate it after rebuilding it.
        # I am writing this out as a long story because it's a cautionary tale for both you and future Joe.
        # It took me far too long to figure out why clicking on a menu item was deselecting the menu and I was
        # looking for the solution in all the wrong places.
        if not hasattr(self, "customer_manager"):
            return
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
                    ), on_click=self._click_ware, **self._style
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
                        ), on_click=self._click_ware, **self._style
                    )
                )
        self._sell_list_widget.sort(key=lambda a: str(a))
        self._sell_list_widget.active_index = active_index

    def _build_buy_list(self):
        if self._special_wares:
            self._build_special_buy_list()
        else:
            self._build_regular_buy_list()

    def _build_special_buy_list(self):
        active_index = self._buy_list_widget.active_index
        self._buy_list_widget.clear()
        for ware in self._special_wares:
            self._buy_list_widget.add_interior(
                pbge.widgetmenu.MenuItemWidget(
                    0, 0, INVENTORY_LIST_FRECT.w, 0,
                    text=ware.get_full_name(),
                    data=WareMenuData(
                        ware=ware, price=self.shop.calc_purchase_price(self.camp, ware),
                        action=actions.BuyAction(self.camp, self.shop, ware, self.undo_sys, self.customer_manager),
                    ), on_click=self._click_ware, **self._style
                )
            )
        self._buy_list_widget.sort(key=lambda a: str(a))

        self._buy_list_widget.add_interior(
            pbge.widgetmenu.MenuItemWidget(
                0, 0, INVENTORY_LIST_FRECT.w, 0,
                text="[Done]", on_click=self._return_to_regular_menu, **self._style
            )
        )
        self._buy_list_widget.active_index = active_index

    def _build_regular_buy_list(self):
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
                    ), on_click=self._click_ware, **self._style
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
                    ), on_click=self._click_ware, **self._style
                )
            )

        self._buy_list_widget.sort(key=lambda a: str(a))

        # Part three- add ammo packs for guns.
        for n, wid in enumerate(self._buy_list_widget.items(), start=1):
            wid.data.sort_order = n*100

        for wid in self._buy_list_widget.items():
            if wid.data.ware:
                if self.shop.can_sell_ammo(wid.data.ware):
                    self._buy_list_widget.add_interior(
                        pbge.widgetmenu.MenuItemWidget(
                            0, 0, INVENTORY_LIST_FRECT.w, 0,
                            text="+ {} ammo".format(wid.data.ware.get_full_name()),
                            data=WareMenuData(
                                ware=wid.data.ware, price=self.shop.calc_purchase_price(self.camp, wid.data.ware),
                                action=None, sort_order=wid.data.sort_order + 1
                            ), on_click=self._switch_ammo_menu, **self._style
                        )
                    )
                elif isinstance(wid.data.ware, gears.base.ChemThrower):
                    myammo = wid.data.ware.get_ammo()
                    if myammo:
                        myammo = copy.deepcopy(myammo)
                        self._buy_list_widget.add_interior(
                            pbge.widgetmenu.MenuItemWidget(
                                0, 0, INVENTORY_LIST_FRECT.w, 0,
                                text="+ {}".format(myammo.get_full_name()),
                                data=WareMenuData(
                                    ware=myammo, price=self.shop.calc_purchase_price(self.camp, myammo),
                                    action=actions.BuyAction(self.camp, self.shop, myammo, self.undo_sys,
                                                             self.customer_manager),
                                    sort_order=wid.data.sort_order + 1
                                ), on_click=self._click_ware, **self._style
                            )
                        )

        self._buy_list_widget.sort(key=lambda a: a.data.sort_order)
        self._buy_list_widget.active_index = active_index

    def _return_to_regular_menu(self, *etc):
        self._special_wares.clear()
        self._refresh_ware_lists()

    def _switch_ammo_menu(self, ware_widget, *etc):
        self._special_wares = self.shop.get_ammo_list(ware_widget.data.ware)
        self._buy_list_widget.active_index = 0
        self._refresh_ware_lists()

    def _set_item_panel(self, colwidget, warewidget):
        if warewidget and isinstance(warewidget.data, WareMenuData):
            if warewidget.data.ware:
                ip = gears.info.get_longform_display(model=warewidget.data.ware
                                                     , width=INFO_PANEL_FRECT.w
                                                     )
                ip.info_blocks.insert(1, _CostBlock(cost=warewidget.data.price
                                                    , width=INFO_PANEL_FRECT.w
                                                    ))
                self._item_panel = ip
            else:
                self._item_panel = None
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
        if self._special_wares:
            self._return_to_regular_menu()
            return

        if self.undo_sys.actions_have_happened():
            # Ask if we should abort or not.
            mymenu = pbge.rpgmenu.Menu(-EXITMENU_WIDTH // 2, -EXITMENU_HEIGHT // 2
                                       , EXITMENU_WIDTH, EXITMENU_HEIGHT
                                       , font=pbge.MEDIUM_DISPLAY_FONT
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
                elif ev.unicode == "R" and pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
                    self.shop.wares = list()
                    self.shop.update_wares(self.camp)
                    self._refresh_ware_lists()

        pbge.my_state.widgets.remove(self)
        # Improve friendliness for all items bought.
        if self.undo_sys.actions_have_happened():
            pbge.my_state.start_sound_effect("purchase2.ogg")
        for item in self.undo_sys.get_bought_items():
            self.shop.improve_friendliness(self.camp, item)

    def render(self, flash=False):
        super().render()
        if self._item_panel:
            rect = INFO_PANEL_FRECT.get_rect()
            self._item_panel.render(rect.x, rect.y)
