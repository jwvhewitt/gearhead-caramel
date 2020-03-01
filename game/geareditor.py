import pbge
import gears
import pygame


class PartEditWidget(pbge.widgets.ColumnWidget):
    # Used for editing a miscellaneous gear.
    def __init__(self, mygear, editor, **kwargs):
        super().__init__(25,-250,350,200,draw_border=True,center_interior=True,**kwargs)
        self.mygear = mygear
        self.editor = editor

        desig_row = pbge.widgets.RowWidget(0,0,350,pbge.BIGFONT.get_linesize()+8)
        desig_label = pbge.widgets.LabelWidget(0,0,65,desig_row.h,text="Desig:",font=pbge.BIGFONT)
        desig_row.add_center(desig_label)
        desig_field = pbge.widgets.TextEntryWidget(0, 0, 280, desig_row.h, text=mygear.desig, font=pbge.BIGFONT, on_change=self._set_desig)
        desig_row.add_center(desig_field)
        self.add_interior(desig_row)

        name_row = pbge.widgets.RowWidget(0,0,350,pbge.BIGFONT.get_linesize()+8)
        name_label = pbge.widgets.LabelWidget(0,0,65,name_row.h,text="Name:",font=pbge.BIGFONT)
        name_row.add_center(name_label)
        name_field = pbge.widgets.TextEntryWidget(0, 0, 280, name_row.h, text=str(mygear), font=pbge.BIGFONT, on_change=self._set_name)
        name_row.add_center(name_field)
        self.add_interior(name_row)


    def _set_desig(self,widg,ev):
        self.mygear.desig = widg.text
        self.editor.update()

    def _set_name(self,widg,ev):
        self.mygear.desig = widg.text
        self.editor.update()

class MechaEditWidget(pbge.widgets.ColumnWidget):
    # Used for editing a mecha gear.
    def __init__(self, mygear, **kwargs):
        super().__init__(25,-250,350,200,draw_border=True,center_interior=True,**kwargs)
        self.mygear = mygear

        self.desig_field = pbge.widgets.TextEntryWidget(0, 0, 300, 30, justify=1, text=mygear.desig, font=pbge.BIGFONT)
        self.add_interior(self.desig_field)
        self.name_field = pbge.widgets.TextEntryWidget(0, 0, 300, 30, justify=-1, text=str(mygear), font=pbge.BIGFONT)
        self.add_interior(self.name_field)


        self.form_field = pbge.widgets.DropdownWidget(-50,36,250,30,parent=self,anchor=pbge.frects.ANCHOR_TOP,on_select=self._set_form)
        for mf in gears.base.MECHA_FORMS:
            self.form_field.add_item(mf.name,mf)
        self.form_field.menu.set_item_by_value(self.mygear.form)
        self.add_interior(self.form_field)

    def _set_form(self,result):
        if result:
            self.mygear.form = result


class PartsNodeWidget(pbge.widgets.Widget):
    def __init__(self,mypart,prefix,indent,editor,**kwargs):
        super().__init__(0,0,350,pbge.MEDIUMFONT.get_linesize()+1,data=mypart,on_click=editor.click_part,**kwargs)
        self.prefix = prefix
        self.indent = indent
        self.editor = editor
        self.selected_image = self._draw_image(pbge.INFO_HILIGHT)
        self.regular_image = self._draw_image(pbge.INFO_GREEN)
        self.mouseover_image = self._draw_image(pbge.rpgmenu.MENU_SELECT_COLOR)

    def _draw_image(self,text_color):
        myimage = pygame.Surface((self.w,self.h))
        myimage.fill((0, 0, 0))
        myimage.set_colorkey((0, 0, 0), pygame.RLEACCEL)

        myimage.blit(pbge.MEDIUMFONT.render(self.prefix + self.data.get_full_name(),True,text_color),(self.indent*12,0))
        return myimage

    def render( self ):
        myrect = self.get_rect()
        if myrect.collidepoint(*pygame.mouse.get_pos()):
            pbge.my_state.screen.blit( self.mouseover_image , myrect )
        elif self.data is self.editor.active_part:
            pbge.my_state.screen.blit(self.selected_image, myrect)
        else:
            pbge.my_state.screen.blit( self.regular_image , myrect )

class PartsTreeWidget(pbge.widgets.ColumnWidget):
    def __init__(self,mygear,editor,**kwargs):
        super().__init__(-350,-250,350,500,draw_border=True,center_interior=True,**kwargs)
        up_arrow = pbge.widgets.ButtonWidget(0,0,128,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),on_frame=0,off_frame=1)
        down_arrow = pbge.widgets.ButtonWidget(0,0,128,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),on_frame=2,off_frame=3)
        self.scroll_column = pbge.widgets.ScrollColumnWidget(0,0,350,450,up_arrow,down_arrow,padding=0)
        self.add_interior(up_arrow)
        self.add_interior(self.scroll_column)
        self.add_interior(down_arrow)
        self.mygear = mygear
        self.editor = editor

        self.refresh_gear_list()

    def refresh_gear_list(self):
        self.scroll_column.clear()
        self.add_gear(self.mygear)

    def add_gear(self,part,prefix='',indent=0):
        self.scroll_column.add_interior(PartsNodeWidget(part,prefix,indent,self.editor))
        for bit in part.sub_com:
            self.add_gear(bit,">",indent+1)
        for bit in part.inv_com:
            self.add_gear(bit,"+",indent+1)


class GearEditor(pbge.widgets.Widget):
    def __init__(self, mygear=None, **kwargs):
        super().__init__(-400,-300,800,600,**kwargs)

        self.mygear = mygear
        self.active_part = mygear
        self.active_part_editor = None
        self.update_part_editor()

        self.parts_widget = PartsTreeWidget(mygear,self)
        self.children.append(self.parts_widget)

        self.finished = False

    def click_part(self,widj,ev):
        if widj.data:
            self.active_part = widj.data
            self.update_part_editor()

    def update_part_editor(self):
        if self.active_part_editor:
            self.children.remove(self.active_part_editor)
        self.active_part_editor = PartEditWidget(self.active_part,self)
        self.children.append(self.active_part_editor)

    def update(self):
        self.parts_widget.refresh_gear_list()

    @classmethod
    def create_and_invoke(cls, redraw):
        # Create the UI. Run the UI. Clean up after you leave.
        mymek = gears.selector.get_design_by_full_name("SAN-X9 Buru Buru")
        myui = cls(mymek)
        pbge.my_state.widgets.append(myui)
        pbge.my_state.view = redraw
        keepgoing = True
        while keepgoing and not myui.finished and not pbge.my_state.got_quit:
            ev = pbge.wait_event()
            if ev.type == pbge.TIMEREVENT:
                redraw()
                pbge.my_state.do_flip()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    keepgoing = False

        pbge.my_state.widgets.remove(myui)


