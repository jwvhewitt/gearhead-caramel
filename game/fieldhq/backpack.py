import pbge
from pbge import widgets
import gears
import pygame

from pbge import widgetmenu

INFO_COLUMN = pbge.frects.Frect(-300, -200, 220, 300)
EQUIPMENT_COLUMN = pbge.frects.Frect(-50, -200, 350, 155)
INVENTORY_COLUMN = pbge.frects.Frect(-50, 0, 350, 200)
PC_SWITCH_AREA = pbge.frects.Frect(-300, 100, 220, 100)


class SwitchNameBlock(object):
    def __init__(self, switch, width=220, font=None, **kwargs):
        self.switch = switch
        self.width = width
        self.font = font or pbge.MEDIUM_DISPLAY_FONT

    @property
    def height(self):
        return len(pbge.wrapline(str(self.switch.pc), self.font, self.width)) * self.font.get_linesize()

    def render(self, x, y):
        mydest = pygame.Rect(x, y, self.width, self.height)
        pbge.draw_text(self.font, str(self.switch.pc), mydest, pbge.WHITE, justify=0)


class SwitchEncumberanceBlock(object):
    def __init__(self, switch, font=None, width=220, **kwargs):
        self.switch = switch
        self.width = width
        self.font = font or pbge.SMALLFONT

    @property
    def height(self):
        if hasattr(self.switch.pc, "carrying_capacity"):
            return self.font.get_linesize() * 2
        else:
            return self.font.get_linesize()

    def render(self, x, y):
        mydest = pygame.Rect(x, y, self.width, self.height)
        mymass = self.switch.pc.get_inv_mass()
        mycolor = pbge.INFO_GREEN
        if hasattr(self.switch.pc, "carrying_capacity"):
            mycapacity = self.switch.pc.carrying_capacity()
            if mymass > mycapacity * 1.25:
                mycolor = pbge.ENEMY_RED
            elif mymass > mycapacity:
                mycolor = pygame.Color("yellow")
        else:
            mycapacity = 0
        pbge.draw_text(
            self.font, self.switch.pc.scale.get_mass_string(mymass), mydest, mycolor, justify=0
        )
        if mycapacity > 0:
            mydest.y += self.font.get_linesize()
            pbge.draw_text(
                self.font, "/{}".format(self.switch.pc.scale.get_mass_string(mycapacity)), mydest, mycolor, justify=0
            )


class BackpackSwitchIP(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (SwitchNameBlock, gears.info.CreditsBlock, SwitchEncumberanceBlock)


class InvItemWidget(widgets.Widget):
    def __init__(self, dx, dy, w, h, text, on_click: widgets.On_Click=None,data=None, desc=None, **kwargs):
        """

        :type bp: BackpackWidget
        :type item: gears.base.BaseGear
        """
        self.text = text
        if h == 0:
            h = pbge.MEDIUMFONT.get_linesize()
        super().__init__(dx, dy, w, h, on_click=on_click, data=data, desc=desc, **kwargs)

    def _render(self, delta):
        mydest = self.get_rect()
        if self._should_flash():
            color = pbge.widgetmenu.MENU_SELECT_COLOR
        elif self.data and self.data.is_destroyed():
            color = pbge.ENEMY_RED
        else:
            color = pbge.widgetmenu.MENU_ITEM_COLOR
        pbge.draw_text(pbge.MEDIUMFONT, self.text, mydest, color=color)
        if self.data:
            pbge.draw_text(pbge.ITALICFONT, self.data.scale.get_mass_string(self.data.mass), mydest, justify=1, color=color)

    def __str__(self):
        return self.text

    def __lt__(self, other):
        """ Comparison of menu items done by msg string """
        return (self.text < str(other))


class PlayerCharacterSwitch(widgets.RowWidget):
    WIDTH = 136
    HEIGHT = 100

    def __init__(self, camp, pc, set_pc_fun, upleft=(0, 0), **kwargs):
        super().__init__(upleft[0], upleft[1], self.WIDTH, self.HEIGHT, padding=2, **kwargs)
        self.camp = camp
        self.pc = pc
        self.portraits = dict()
        self.set_pc_fun = set_pc_fun

        arrow_sprite = pbge.image.Image("sys_leftrightarrows.png", 16, 100)
        self.add_center(widgets.ButtonWidget(0, 0, 16, 100, sprite=arrow_sprite, on_click=self.click_left))
        self.portrait_button = widgets.ButtonWidget(0, 0, 100, 100, sprite=None, frame=1)
        self.add_center(self.portrait_button)
        self.add_center(widgets.ButtonWidget(0, 0, 16, 100, sprite=arrow_sprite, on_click=self.click_right, frame=1))

        self.update_pc()

    def click_left(self, _wid, _ev):
        party = [pc for pc in self.camp.get_active_party() if isinstance(pc, (gears.base.Character, gears.base.Mecha))]
        if self.pc in party:
            new_i = party.index(self.pc) - 1
            self.pc = party[new_i]
            self.update_pc()

    def click_right(self, _wid, _ev):
        party = [pc for pc in self.camp.get_active_party() if isinstance(pc, (gears.base.Character, gears.base.Mecha))]
        if self.pc in party:
            new_i = party.index(self.pc) + 1
            if new_i >= len(party):
                new_i = 0
            self.pc = party[new_i]
            self.update_pc()

    def _builtin_responder(self, ev):
        if (ev.type == pygame.KEYDOWN):
            if pbge.my_state.is_key_for_action(ev, "left"):
                self.click_left(self, ev)
            elif pbge.my_state.is_key_for_action(ev, "right"):
                self.click_right(self, ev)

    def update_pc(self):
        if self.pc not in self.portraits:
            self.portraits[self.pc] = self.pc.get_portrait()
        self.portrait_button.sprite = self.portraits[self.pc]
        self.set_pc_fun(self.pc)


class PlayerCharacterSwitchPlusBPInfo(widgets.RowWidget):
    def __init__(self, camp, pc, set_pc_fun, upleft=None, **kwargs):
        super().__init__(PC_SWITCH_AREA.dx, PC_SWITCH_AREA.dy, PC_SWITCH_AREA.w, PC_SWITCH_AREA.h, **kwargs)
        if upleft:
            self.dx, self.dy = upleft

        self.my_switch = PlayerCharacterSwitch(camp, pc, set_pc_fun)
        self.add_left(self.my_switch)
        self.add_right(
            gears.info.InfoWidget(0, 0, 80, 100, info_panel=BackpackSwitchIP(
                draw_border=False, switch=self.my_switch, camp=camp, width=80, abbreviate=False
            ))
        )
        # self.add_right(widgets.LabelWidget(0,0,70,100,text_fun=self.get_label_text, justify=0, color=pbge.INFO_GREEN))

    # def get_label_text(self,wid):
    #    return "{}\n \n ${}\n {}".format(str(self.my_switch.pc),self.my_switch.camp.credits,self.my_switch.pc.scale.get_mass_string(self.my_switch.pc.get_inv_mass()))


class BackpackWidget(widgets.Widget):
    TAGS_TO_DEACTIVATE = {widgets.WTAG_WIDGET,}

    def __init__(self, camp, pc, **kwargs):
        """

        :type pc: gears.base.Character
        :type camp: gears.GearHeadCampaign
        """
        super(BackpackWidget, self).__init__(0, 0, 0, 0, **kwargs)

        self.camp = camp
        self.pc = pc
        self.info_cache = dict()
        self.active_item: pbge.widgets.Widget|None = None
        self._latest_item_to_open_menu = None

        self.equipment_selector = widgetmenu.MenuWidget(
            EQUIPMENT_COLUMN.dx, EQUIPMENT_COLUMN.dy, EQUIPMENT_COLUMN.w, EQUIPMENT_COLUMN.h,
            on_activate_item=self._activate_item, item_class=InvItemWidget
        )

        self.children.append(self.equipment_selector)

        self.inventory_selector = widgetmenu.MenuWidget(
            INVENTORY_COLUMN.dx, INVENTORY_COLUMN.dy, INVENTORY_COLUMN.w, INVENTORY_COLUMN.h,
            on_activate_item=self._activate_item, item_class=InvItemWidget
        )

        self.children.append(self.inventory_selector)

        self.children.append(PlayerCharacterSwitchPlusBPInfo(camp, pc, self.set_pc, draw_border=True))
        self.finished = False

        self.update_selectors()

        self.children.append( pbge.widgets.LabelWidget(
            150, 240, 80, 0, text="Done", justify=0, on_click=self.finish,
            draw_border=True
        ))

    def _activate_item(self, _col, colitem):
        self.active_item = colitem.data

    def set_pc(self, pc):
        self.pc = pc
        self.update_selectors()

    def _add_equipped_items(self, part_list, menu_widget, is_inv):
        """

        :type menu_widget: widgets.ScrollColumnWidget
        :type part_list: list
        """
        for part in part_list:
            if is_inv:
                menu_widget.add_item(
                    '{} [{}]'.format(str(part), str(part.parent)), self.this_item_was_selected,
                    data=part
                )
            self._add_equipped_items(part.sub_com, menu_widget, False)
            self._add_equipped_items(part.inv_com, menu_widget, True)

    def build_equipment_menu(self, menu_widget):
        self._add_equipped_items(self.pc.sub_com, menu_widget, False)
        self._add_equipped_items(self.pc.inv_com, menu_widget, False)

    def build_inventory_menu(self, container, menu_widget):
        for item in container.inv_com:
            menu_widget.add_item(item.get_full_name(), on_click=self.this_item_was_selected, data=item)
        menu_widget.sort(key=lambda w: w.text)

    def update_selectors(self):
        self.inventory_selector.clear()
        self.build_inventory_menu(self.pc, self.inventory_selector)
        self.equipment_selector.clear()
        self.build_equipment_menu(self.equipment_selector)
        self.active_item = None

    def _unequip_item(self, wid, _ev):
        item = wid.data
        item.parent.inv_com.remove(item)
        self.pc.inv_com.append(item)
        self.update_selectors()

    def _equip_item(self, wid, _ev):
        item = wid.data
        mymenu: pbge.widgetmenu.PopupMenuWidget = self.get_tiws_menu()
        for part in self.pc.descendants():
            if part.can_equip(item, check_slots=False):
                _=mymenu.add_item(part.get_full_name(), self._select_destination, (item, part))
        _=mymenu.add_item("[CANCEL]", None)

    def _select_destination(self, wid, _ev):
        part, dest = wid.data
        if dest:
            for item in dest.inv_com:
                if item.slot == part.slot:
                    item.parent.inv_com.remove(item)
                    self.pc.inv_com.append(item)
            part.parent.inv_com.remove(part)
            dest.inv_com.append(part)
            self.update_selectors()

    def _load_ammo(self, wid, _ev):
        item = wid.data
        mymenu = self.get_tiws_menu()
        for part in self.pc.descendants():
            if isinstance(part, (gears.base.BallisticWeapon, gears.base.ChemThrower)) and part.is_good_ammo(item):
                msg = part.get_full_name()
                if part.parent is not self.pc:
                    msg = "{} ({})".format(msg, part.parent)
                _=mymenu.add_item(msg, self._do_the_loading, data=(item, part))
        mymenu.sort()
        _=mymenu.add_item("[CANCEL]", None)

    def _do_the_loading(self, wid, _ev):
        ammo, dest = wid.data
        dest.reload(ammo)
        _=pbge.my_state.start_sound_effect("reload.ogg")
        self.update_selectors()

    def _reload_gun(self, wid, _ev):
        item = wid.data
        mymenu = self.get_tiws_menu()
        for part in self.pc.inv_com:
            if isinstance(part, (gears.base.Ammo, gears.base.Chem)) and item.is_good_ammo(part):
                _=mymenu.add_item("{} [{}/{}]".format(part.get_full_name(), part.quantity - part.spent, part.quantity), self._do_the_reload, data=(item, part))
        mymenu.sort()
        _=mymenu.add_item("[CANCEL]", None)

    def _do_the_reload(self, wid, _ev):
        gun, dest = wid.data
        gun.reload(dest)
        _=pbge.my_state.start_sound_effect("reload.ogg")
        self.update_selectors()

    def _drop_item(self, wid, _ev):
        item = wid.data
        item.parent.inv_com.remove(item)
        self.camp.scene.contents.append(item)
        item.pos = self.pc.get_root().pos
        self.update_selectors()

    def _trade_item(self, wid, _ev):
        item = wid.data
        mymenu: widgetmenu.PopupMenuWidget = self.get_tiws_menu()
        mypc = self.pc.get_root()
        for pc in self.camp.get_active_party():
            if (pc is not mypc and pc.can_equip(item) 
                and isinstance(pc, (gears.base.Mecha, gears.base.Character)) 
                and not (hasattr(pc, "owner") and pc.owner)  # pyright: ignore[reportAttributeAccessIssue]
            ):
                _=mymenu.add_item(str(pc), self._do_the_trade, data=(pc, item))
        _=mymenu.add_item("[Cancel]", None)

    def _do_the_trade(self, wid, _ev):
        nupc, item = wid.data
        item.parent.inv_com.remove(item)
        nupc.inv_com.append(item)
        self.update_selectors()

    def _stash_item(self, wid, _ev):
        item = wid.data
        item.parent.inv_com.remove(item)
        self.camp.party.append(item)
        self.update_selectors()

    def get_tiws_menu(self, current_menu_item: pbge.widgets.Widget|None=None) -> pbge.widgetmenu.MenuWidget:
        # Return a popup menu for this widget.
        if current_menu_item:
            mydest = current_menu_item.get_rect()
            self._latest_item_to_open_menu = current_menu_item
        elif self._latest_item_to_open_menu:
            mydest = self._latest_item_to_open_menu.get_rect()
        else:
            mydest = INVENTORY_COLUMN.get_rect()
        mydest.h = 150
        mydest.clamp_ip(pbge.my_state.screen.get_rect())
        mymenu = pbge.widgetmenu.PopupMenuWidget(
            w=mydest.w, h=mydest.h, topleft=mydest.topleft, font=pbge.MEDIUMFONT,
            border=widgets.popup_menu_border, auto_escape=True
        )
        mymenu.push_and_deploy()
        return mymenu

    def this_item_was_selected(self, wid: InvItemWidget, _ev):
        """

        :type wid: InvItemWidget
        """
        mymenu = self.get_tiws_menu(wid)
        item = wid.data
        # Basic options: Equip, Unequip, Transfer, Drop, Apply Skill
        # Let's let items set their own special menu options, like eat, use, engage safety, etc.
        if item.parent is self.pc:
            _=mymenu.add_item("Equip {}".format(item), self._equip_item, data=item)
        else:
            _=mymenu.add_item("Unequip {}".format(item), self._unequip_item, data=item)

        if isinstance(item, (gears.base.Ammo, gears.base.Chem)):
            _=mymenu.add_item("Load {}".format(item), self._load_ammo, data=item)
        elif isinstance(item, (gears.base.BallisticWeapon, gears.base.ChemThrower)) and any([item.is_good_ammo(a) for a in self.pc.inv_com]):
            _=mymenu.add_item("Reload {}".format(item), self._reload_gun, data=item)

        if self.pc.get_root() in self.camp.scene.contents:
            _=mymenu.add_item("Drop {}".format(item), self._drop_item, data=item)
            if isinstance(self.pc.get_root(), gears.base.Character):
                _=mymenu.add_item("Trade {}".format(item), self._trade_item, data=item)
        else:
            _=mymenu.add_item("Stash {}".format(item), self._stash_item, data=item)

    def _render(self, delta):
        if self.active_item:
            if self.active_item not in self.info_cache:
                self.info_cache[self.active_item] = gears.info.get_longform_display(
                    self.active_item, width=INFO_COLUMN.w
                )
            mydest = INFO_COLUMN.get_rect()
            self.info_cache[self.active_item].render(mydest.x, mydest.y)

    def finish(self, _wid, _ev):
        self.pop()

    def _builtin_responder(self, ev):
        if ev.type == pygame.KEYDOWN:
            if pbge.my_state.is_key_for_action(ev, "exit"):
                self.pop()
                self.register_response()


class ItemExchangeWidget(widgets.Widget):
    TAGS_TO_DEACTIVATE = {widgets.WTAG_WIDGET,}

    def __init__(self, camp, pc: gears.base.Character, conlist: pbge.container.ContainerList, **kwargs):
        """

        :type camp: gears.GearHeadCampaign
        """
        super().__init__(0, 0, 0, 0, **kwargs)

        self.camp = camp
        self.pc = pc
        self.conlist = conlist
        self.info_cache = dict()
        self.active_item = None

        self.crate_selector = widgetmenu.MenuWidget(
            EQUIPMENT_COLUMN.dx, EQUIPMENT_COLUMN.dy, EQUIPMENT_COLUMN.w, EQUIPMENT_COLUMN.h,
            on_activate_item=self._activate_item, item_class=InvItemWidget
        )

        self.children.append(self.crate_selector)

        self.inventory_selector = widgetmenu.MenuWidget(
            INVENTORY_COLUMN.dx, INVENTORY_COLUMN.dy, INVENTORY_COLUMN.w, INVENTORY_COLUMN.h,
            on_activate_item=self._activate_item, item_class=InvItemWidget
        )

        self.children.append(self.inventory_selector)

        self.children.append(PlayerCharacterSwitchPlusBPInfo(camp, pc, self.set_pc, draw_border=True))

        self.update_selectors()

        self.children.append( pbge.widgets.LabelWidget(
            150, 240, 80, 0, text="Done", justify=0, on_click=self.done_button,
            draw_border=True
        ))

    def _activate_item(self, _col, colitem):
        self.active_item = colitem.data

    def set_pc(self, pc):
        self.pc = pc
        self.update_selectors()

    def build_inventory_menu(self, mylist, menu_widget, click_fun):
        for item in mylist:
            menu_widget.add_item(item.get_full_name(), on_click=click_fun, data=item)
        menu_widget.sort(key=lambda w: str(w))

    def update_selectors(self):
        self.inventory_selector.clear()
        self.build_inventory_menu(self.pc.inv_com, self.inventory_selector, self.trade_to_crate)
        self.crate_selector.clear()
        self.build_inventory_menu(self.conlist, self.crate_selector, self.trade_to_pc)
        self.active_item = None

    def trade_to_crate(self, wid, _ev):
        item = wid.data
        item.parent.inv_com.remove(item)
        self.conlist.append(item)
        self.update_selectors()

    def trade_to_pc(self, wid, _ev):
        item = wid.data
        if self.pc.can_equip(item):
            self.conlist.remove(item)
            _=self.pc.inv_com.append(item)
            self.update_selectors()
            self.camp.check_trigger("GET", item)

    def done_button(self, _wid, _ev):
        self.pop()

    def _render(self, delta):
        if self.active_item:
            if self.active_item not in self.info_cache:
                self.info_cache[self.active_item] = gears.info.get_longform_display(self.active_item,
                                                                                         width=INFO_COLUMN.w)
            mydest = INFO_COLUMN.get_rect()
            self.info_cache[self.active_item].render(mydest.x, mydest.y)

    def _builtin_responder(self, ev):
        if ev.type == pygame.KEYDOWN:
            if pbge.my_state.is_key_for_action(ev, "exit"):
                self.pop()
                self.register_response()

