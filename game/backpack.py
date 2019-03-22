import pbge
from pbge import widgets
import gears
import pygame

INFO_COLUMN = pbge.frects.Frect(-300,-200,220,300)
EQUIPMENT_COLUMN = pbge.frects.Frect(-50,-200,350,170)
INVENTORY_COLUMN = pbge.frects.Frect(-50,0,350,200)
PC_SWITCH_AREA = pbge.frects.Frect(-300,100,220,100)

class InvItemWidget(widgets.Widget):
    def __init__(self, item, bp, show_parent=False, **kwargs):
        """

        :type bp: BackpackWidget
        :type item: gears.base.BaseGear
        """
        self.item = item
        self.bp = bp
        if show_parent:
            self.text = '{} [{}]'.format(str(item),str(item.parent))
        else:
            self.text = item.get_full_name()
        super(InvItemWidget,self).__init__(0,0,INVENTORY_COLUMN.w,pbge.MEDIUMFONT.get_linesize(),**kwargs)

    def render(self):
        mydest = self.get_rect()
        if self is self.bp.active_item:
            color = pbge.INFO_HILIGHT
        else:
            color = pbge.INFO_GREEN
        pbge.draw_text(pbge.MEDIUMFONT,self.text,mydest,color=color)
        pbge.draw_text(pbge.ITALICFONT, self.item.scale.get_mass_string(self.item.mass), mydest, justify=1, color=color)

    def _builtin_responder(self,ev):
        if (ev.type == pygame.MOUSEMOTION) and self.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.bp.active_item = self

    def get_menu(self):
        # Return a popup menu for this widget.
        mydest = self.get_rect()
        mydest.h = 150
        mydest.clamp_ip(pbge.my_state.screen.get_rect())
        return pbge.rpgmenu.Menu(mydest.x,mydest.y,self.w,150,font=pbge.MEDIUMFONT,border=widgets.popup_menu_border,anchor=pbge.frects.ANCHOR_UPPERLEFT)

    def __str__(self):
        return self.text

    def __lt__(self,other):
        """ Comparison of menu items done by msg string """
        return( self.text < str(other) )

class PlayerCharacterSwitch(widgets.RowWidget):
    def __init__(self, camp, pc, set_pc_fun, **kwargs):
        super(PlayerCharacterSwitch, self).__init__(PC_SWITCH_AREA.dx,PC_SWITCH_AREA.dy,PC_SWITCH_AREA.w,PC_SWITCH_AREA.h,**kwargs)
        self.camp = camp
        self.pc = pc
        self.portraits = dict()
        self.set_pc_fun = set_pc_fun

        arrow_sprite = pbge.image.Image("sys_leftrightarrows.png",16,100)
        self.add_left(widgets.ButtonWidget(0,0,16,100,sprite=arrow_sprite,on_click=self.click_left))
        self.portrait_button = widgets.ButtonWidget(0,0,100,100,sprite=None,frame=1)
        self.add_left(self.portrait_button)
        self.add_left(widgets.ButtonWidget(0,0,16,100,sprite=arrow_sprite,on_click=self.click_right,frame=1))

        self.add_right(widgets.LabelWidget(0,0,70,100,text_fun=self.get_label_text, justify=0, color=pbge.INFO_GREEN))

        self.update()

    def click_left(self,wid,ev):
        party = self.camp.get_active_party()
        if self.pc in party:
            new_i = party.index(self.pc) - 1
            self.pc = party[new_i]
            self.update()

    def click_right(self,wid,ev):
        party = self.camp.get_active_party()
        if self.pc in party:
            new_i = party.index(self.pc) + 1
            if new_i >= len(party):
                new_i = 0
            self.pc = party[new_i]
            self.update()

    def get_label_text(self,wid):
        return "{}\n \n ${}\n {}".format(str(self.pc),self.camp.credits,self.pc.scale.get_mass_string(self.pc.get_inv_mass()))

    def update(self):
        if self.pc not in self.portraits:
            self.portraits[self.pc] = self.pc.get_portrait()
        self.portrait_button.sprite = self.portraits[self.pc]
        self.set_pc_fun(self.pc)

class BackpackWidget(widgets.Widget):
    active_item = None  # type: InvItemWidget

    def __init__(self, camp, pc, **kwargs):
        """

        :type pc: gears.base.Character
        :type camp: gears.GearHeadCampaign
        """
        super(BackpackWidget, self).__init__(0,0,0,0,**kwargs)

        self.camp = camp
        self.pc = pc
        self.info_cache = dict()

        self.ec_up_button = widgets.ButtonWidget(0, 0, EQUIPMENT_COLUMN.w, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), off_frame=1)
        self.ec_down_button = widgets.ButtonWidget(0, 0, EQUIPMENT_COLUMN.w, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), frame=2, on_frame=2, off_frame=3)
        self.equipment_selector = widgets.ScrollColumnWidget(0, 0, EQUIPMENT_COLUMN.w, EQUIPMENT_COLUMN.h - 42, up_button = self.ec_up_button, down_button=self.ec_down_button, padding=2)

        self.equipment_column = widgets.ColumnWidget(EQUIPMENT_COLUMN.dx,EQUIPMENT_COLUMN.dy,EQUIPMENT_COLUMN.w,EQUIPMENT_COLUMN.h,draw_border=True)

        self.equipment_column.add_interior(self.ec_up_button)
        self.equipment_column.add_interior(self.equipment_selector)
        self.equipment_column.add_interior(self.ec_down_button)

        self.children.append(self.equipment_column)

        self.ic_up_button = widgets.ButtonWidget(0, 0, INVENTORY_COLUMN.w, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), off_frame=1)
        self.ic_down_button = widgets.ButtonWidget(0, 0, INVENTORY_COLUMN.w, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), frame=2, on_frame=2, off_frame=3)
        self.inventory_selector = widgets.ScrollColumnWidget(0, 0, INVENTORY_COLUMN.w, INVENTORY_COLUMN.h - 42, up_button = self.ic_up_button, down_button=self.ic_down_button, padding=2)

        self.inventory_column = widgets.ColumnWidget(INVENTORY_COLUMN.dx,INVENTORY_COLUMN.dy,INVENTORY_COLUMN.w,INVENTORY_COLUMN.h,draw_border=True)

        self.inventory_column.add_interior(self.ic_up_button)
        self.inventory_column.add_interior(self.inventory_selector)
        self.inventory_column.add_interior(self.ic_down_button)

        self.children.append(self.inventory_column)
        self.children.append(PlayerCharacterSwitch(camp,pc,self.set_pc,draw_border=True))

        self.update_selectors()

    def set_pc(self,pc):
        self.pc = pc
        self.update_selectors()

    def _add_equipped_items(self, part_list, menu_widget, is_inv):
        """

        :type menu_widget: widgets.ScrollColumnWidget
        :type part_list: list
        """
        for part in part_list:
            if is_inv:
                menu_widget.add_interior(InvItemWidget(part,self,show_parent=True,on_click=self.this_item_was_selected))
            self._add_equipped_items(part.sub_com, menu_widget, False)
            self._add_equipped_items(part.inv_com, menu_widget, True)


    def build_equipment_menu(self,menu_widget):
        self._add_equipped_items(self.pc.sub_com, menu_widget, False)
        self._add_equipped_items(self.pc.inv_com, menu_widget, False)

    def build_inventory_menu(self,container,menu_widget):
        for item in container.inv_com:
            menu_widget.add_interior(InvItemWidget(item, self, show_parent=False,on_click=self.this_item_was_selected))
        menu_widget.sort(key=lambda w: w.text)

    def update_selectors(self):
        self.inventory_selector.clear()
        self.build_inventory_menu(self.pc,self.inventory_selector)
        self.equipment_selector.clear()
        self.build_equipment_menu(self.equipment_selector)
        self.active_item = None

    def _unequip_item(self,wid):
        wid.item.parent.inv_com.remove(wid.item)
        self.pc.inv_com.append(wid.item)
        self.update_selectors()

    def _equip_item(self,wid):
        mymenu = wid.get_menu()
        for part in self.pc.descendants():
            if part.can_equip(wid.item,check_slots=False):
                mymenu.add_item(part.get_full_name(),part)
        mymenu.add_item("[CANCEL]",None)
        dest = mymenu.query()
        if dest:
            for item in dest.inv_com:
                if item.slot == wid.item.slot:
                    item.parent.inv_com.remove(item)
                    self.pc.inv_com.append(item)
            wid.item.parent.inv_com.remove(wid.item)
            dest.inv_com.append(wid.item)
            self.update_selectors()

    def _drop_item(self,wid):
        wid.item.parent.inv_com.remove(wid.item)
        self.camp.contents.append(wid.item)
        wid.item.pos = self.pc.get_root().pos
        self.update_selectors()

    def this_item_was_selected(self,wid,ev):
        """

        :type wid: InvItemWidget
        """
        # I know I'm breaking the Python naming convention, but this is what this function has been called
        # since the 20th century, and I'm not changing it now just because I'm using a modern high-falutin'
        # language.
        mymenu = wid.get_menu()
        # Basic options: Equip, Unequip, Transfer, Drop, Apply Skill
        # Let's let items set their own special menu options, like eat, use, engage safety, etc.
        if wid.item.parent is self.pc:
            mymenu.add_item("Equip {}".format(wid.item),self._equip_item)
        else:
            mymenu.add_item("Unequip {}".format(wid.item), self._unequip_item)

        if self.pc.get_root() in self.camp.scene.contents:
            mymenu.add_item("Drop {}".format(wid.item),self._drop_item)

        cmd = mymenu.query()
        if cmd:
            cmd(wid)

    def render(self):
        if self.active_item:
            if self.active_item.item not in self.info_cache:
                self.info_cache[self.active_item.item] = gears.info.get_longform_display(self.active_item.item,width=INFO_COLUMN.w)
            mydest = INFO_COLUMN.get_rect()
            self.info_cache[self.active_item.item].render(mydest.x,mydest.y)
