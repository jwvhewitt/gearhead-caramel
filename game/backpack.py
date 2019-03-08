import pbge
from pbge import widgets
import gears
import pygame

EQUIPMENT_COLUMN = pbge.frects.Frect(0,-200,250,170)
INVENTORY_COLUMN = pbge.frects.Frect(0,0,250,200)

class InvItemWidget(widgets.Widget):
    def __init__(self, item, bp, **kwargs):
        """

        :type bp: BackpackWidget
        :type item: gears.base.BaseGear
        """
        self.item = item
        self.bp = bp
        super(InvItemWidget,self).__init__(0,0,INVENTORY_COLUMN.w,pbge.MEDIUMFONT.get_linesize(),**kwargs)

    def render(self):
        mydest = self.get_rect()
        if self is self.bp.active_item:
            color = pbge.INFO_HILIGHT
        else:
            color = pbge.INFO_GREEN
        pbge.draw_text(pbge.MEDIUMFONT,self.item.get_full_name(),mydest,color=color)
        pbge.draw_text(pbge.ITALICFONT, '{:.1f}kg'.format(self.item.mass), mydest, justify=1, color=color)

    def _builtin_responder(self,ev):
        if (ev.type == pygame.MOUSEMOTION) and self.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.bp.active_item = self

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

        self.ec_up_button = widgets.ButtonWidget(0, 0, EQUIPMENT_COLUMN.w, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), off_frame=1)
        self.ec_down_button = widgets.ButtonWidget(0, 0, EQUIPMENT_COLUMN.w, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), frame=2, on_frame=2, off_frame=3)
        self.equipment_selector = widgets.ScrollColumnWidget(0, 0, EQUIPMENT_COLUMN.w, EQUIPMENT_COLUMN.h - 42, up_button = self.ec_up_button, down_button=self.ec_down_button, padding=2)

        self.equipment_column = widgets.ColumnWidget(EQUIPMENT_COLUMN.dx,EQUIPMENT_COLUMN.dy,EQUIPMENT_COLUMN.w,EQUIPMENT_COLUMN.h,draw_border=True)

        self.equipment_column.add_interior(self.ec_up_button)
        self.equipment_column.add_interior(self.equipment_selector)
        self.equipment_column.add_interior(self.ec_down_button)

        self.children.append(self.equipment_column)

        self.build_equipment_menu(self.equipment_selector)

    def add_equipped_items(self, part_list, menu_widget, is_inv):
        """

        :type menu_widget: widgets.ScrollColumnWidget
        :type part_list: list
        """
        for part in part_list:
            if is_inv:
                menu_widget.add_interior(InvItemWidget(part,self))
            self.add_equipped_items(part.sub_com, menu_widget, False)
            self.add_equipped_items(part.inv_com, menu_widget, True)


    def build_equipment_menu(self,menu_widget):
        self.add_equipped_items(self.pc.sub_com, menu_widget, False)
        self.add_equipped_items(self.pc.inv_com, menu_widget, False)
