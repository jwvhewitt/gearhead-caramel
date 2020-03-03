import pbge
import gears
import pygame
import copy

MODE_CREATIVE = "CREATIVE"
MODE_RESTRICTED = "RESTRICTED"



class PartEditWidget(pbge.widgets.ColumnWidget):
    # Used for editing a miscellaneous gear.
    def __init__(self, mygear, editor, **kwargs):
        super().__init__(25,-200,350,450,draw_border=True,center_interior=True,**kwargs)
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




class PartsNodeWidget(pbge.widgets.Widget):
    def __init__(self,mypart,prefix,indent,editor,**kwargs):
        self.font = pbge.BIGFONT
        super().__init__(0,0,350,self.font.get_linesize()+1,data=mypart,**kwargs)
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

        myimage.blit(self.font.render(self.prefix + self.data.get_full_name(),True,text_color),(self.indent*12,0))
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
        self.scroll_column.add_interior(PartsNodeWidget(part,prefix,indent,self.editor,on_click=self.editor.click_part))
        for bit in part.sub_com:
            self.add_gear(bit,">",indent+1)
        for bit in part.inv_com:
            self.add_gear(bit,"+",indent+1)

class PartsListWidget(pbge.widgets.ColumnWidget):
    def __init__(self,dx,dy,w,h,part_list,editor,**kwargs):
        super().__init__(dx,dy,w,h,draw_border=True,center_interior=True,**kwargs)
        up_arrow = pbge.widgets.ButtonWidget(0,0,128,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),on_frame=0,off_frame=1)
        down_arrow = pbge.widgets.ButtonWidget(0,0,128,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),on_frame=2,off_frame=3)
        self.scroll_column = pbge.widgets.ScrollColumnWidget(0,0,w,h-50,up_arrow,down_arrow,padding=0)
        self.add_interior(up_arrow)
        self.add_interior(self.scroll_column)
        self.add_interior(down_arrow)
        self.part_list = part_list
        self.editor = editor

        self.refresh_gear_list()

    def set_new_list(self,new_part_list):
        self.part_list = new_part_list
        self.refresh_gear_list()

    def refresh_gear_list(self):
        self.scroll_column.clear()
        for part in self.part_list:
            self.scroll_column.add_interior(
                PartsNodeWidget(part, '', 0, self.editor, on_click=self.editor.click_part))


#   *******************************
#   ***  PART  SUPPLY  CLASSES  ***
#   *******************************
#
# When building a mecha, you may have access to several different sources for parts: your stash, the shop
# you're in, etc.

class LimitedPartsSource(object):
    # A supply object for the stash.
    def __init__(self, name, part_list):
        self.name = name
        self.part_list = part_list
    def get_part(self,part):
        self.part_list.remove(part)
        return part

class UnlimitedPartsSource(object):
    # A supply object for the STC templates.
    def __init__(self, name, part_list):
        self.name = name
        self.part_list = part_list
    def get_part(self,part):
        return copy.deepcopy(part)

class SourceSelectorTab(pbge.widgets.LabelWidget):
    def __init__(self,source,**kwargs):
        super().__init__(0,0,150,pbge.MEDIUMFONT.get_linesize(),text=source.name,font=pbge.MEDIUMFONT,draw_border=True,data=source,border=pbge.widgets.widget_border_off,**kwargs)
        self.on_frame = pbge.widgets.widget_border_on
        self.off_frame = pbge.widgets.widget_border_off

    def _get_frame(self):
        return self.border

    def _set_frame(self,nuval):
        self.border = nuval

    frame = property(_get_frame,_set_frame,None)

class PartSelectorWidget(pbge.widgets.ColumnWidget):
    def __init__(self,sources,filter_fun,on_selection,**kwargs):
        super().__init__(-125, -200, 350, 400, padding=20, **kwargs)

        self.filter_fun = filter_fun
        self.on_selection = on_selection

        # Create the tabs
        self.source_tabs = pbge.widgets.RowWidget(0,0,self.w,pbge.MEDIUMFONT.get_linesize(),padding=15)
        for s in sources:
            self.source_tabs.add_center(SourceSelectorTab(s,on_click=self.click_tab))
        self.add_interior(self.source_tabs)

        # Create the list
        self.active_part = None
        self.part_list_widget = PartsListWidget(0,0,350,325,sources[0].part_list, self)
        self.add_interior(self.part_list_widget)

        self.set_source(sources[0])

        # Create the Okay and Cancel buttons
        myrow = pbge.widgets.RowWidget(0,0,350,30)
        myrow.add_center(pbge.widgets.LabelWidget(0,0,50,30,"Accept",draw_border=True,on_click=self.accept))
        myrow.add_center(pbge.widgets.LabelWidget(0,0,50,30,"Cancel",draw_border=True,on_click=self.cancel))
        self.add_interior(myrow)

    def filter_part_list(self,part_list):
        if self.filter_fun:
            return [part for part in part_list if self.filter_fun(part)]
        else:
            return part_list

    def click_tab(self,widj,ev):
        self.set_source(widj.data)

    def set_source(self,source):
        self.active_source = source
        self.active_part = None
        self.part_list_widget.set_new_list(self.filter_part_list(source.part_list))

    def click_part(self, widj, ev):
        self.active_part = widj.data

    def accept(self,widj,ev):
        if self.active_part:
            self.on_selection(self.active_source.get_part(self.active_part))

    def cancel(self,widj,ev):
        self.active_part = False
        self.on_selection(None)

#   *****************************
#   ***  THE  EDITOR  ITSELF  ***
#   *****************************

class GearEditor(pbge.widgets.Widget):
    def __init__(self, mygear=None, stash=None, mode=MODE_CREATIVE, **kwargs):
        super().__init__(-400,-300,800,600,**kwargs)

        self.mygear = mygear
        self.active_part = mygear
        self.active_part_editor = None
        if stash is None:
            self.stash = pbge.container.ContainerList(owner=self)
        else:
            self.stash = stash
        self.mode = mode
        self.update_part_editor()

        self.sources = list()
        if mode is MODE_CREATIVE:
            self.sources.append(UnlimitedPartsSource("Standard Parts",gears.selector.STC_LIST))
        self.sources.append(LimitedPartsSource("Stash",self.stash))

        self.parts_widget = PartsTreeWidget(mygear,self)
        self.children.append(self.parts_widget)

        mybuttons = pbge.image.Image("sys_geareditor_buttons.png",40,40)
        mybuttonrow = pbge.widgets.RowWidget(25,-255,325,40)
        self.children.append(mybuttonrow)
        mybuttonrow.add_left(pbge.widgets.ButtonWidget(0,0,40,40,mybuttons,frame=0,on_frame=0,off_frame=1,on_click=self._add_subcom,tooltip="Add Component"))
        mybuttonrow.add_left(pbge.widgets.ButtonWidget(0,0,40,40,mybuttons,frame=2,on_frame=2,off_frame=3,on_click=self._add_invcom,tooltip="Add Inventory"))
        mybuttonrow.add_left(pbge.widgets.ButtonWidget(0,0,40,40,mybuttons,frame=4,on_frame=4,off_frame=5,on_click=self._remove_gear,tooltip="Remove Gear"))
        mybuttonrow.add_right(pbge.widgets.ButtonWidget(0,0,40,40,mybuttons,frame=6,on_frame=6,off_frame=7,on_click=self._exit_editor,tooltip="Exit Editor"))

        self.part_selector = None

        self.finished = False

    def _add_subcom(self,widj,ev):
        self.part_selector = PartSelectorWidget(self.sources,self.active_part.can_install,self._return_add_subcom)
        pbge.my_state.widgets.append(self.part_selector)
        self.active = False

    def _add_invcom(self,widj,ev):
        self.part_selector = PartSelectorWidget(self.sources,self.active_part.can_equip,self._return_add_invcom)
        pbge.my_state.widgets.append(self.part_selector)
        self.active = False

    def _return_add_subcom(self,new_subcom):
        pbge.my_state.widgets.remove(self.part_selector)
        self.active = True
        self.part_selector = None
        if new_subcom:
            self.active_part.sub_com.append(new_subcom)
            self.update()

    def _return_add_invcom(self, new_invcom):
        pbge.my_state.widgets.remove(self.part_selector)
        self.active = True
        self.part_selector = None
        if new_invcom:
            self.active_part.inv_com.append(new_invcom)
            self.update()

    def _remove_gear(self,widj,ev):
        parent = self.active_part.parent
        if parent:
            if self.active_part in parent.sub_com:
                parent.sub_com.remove(self.active_part)
            else:
                parent.inv_com.remove(self.active_part)
            self.stash.append(self.active_part)
            self.set_active_part(parent)
            self.update()

    def _exit_editor(self,widj,ev):
        self.finished = True

    def click_part(self,widj,ev):
        if widj.data:
            self.set_active_part(widj.data)

    def set_active_part(self,new_part):
        self.active_part = new_part
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


