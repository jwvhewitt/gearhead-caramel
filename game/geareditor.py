import pbge
import gears
import pygame
import copy

MODE_CREATIVE = "CREATIVE"
MODE_RESTRICTED = "RESTRICTED"

#   **************************
#   ***  UTILITY  WIDGETS  ***
#   **************************

class PlusMinusWidget(pbge.widgets.RowWidget):
    def __init__(self,mygear,att_name,att_min,att_max,on_change,step=1,x=0,y=0,w=350,**kwargs):
        super().__init__(x,y,w,max(pbge.BIGFONT.get_linesize(),16),**kwargs)
        minus_plus_image = pbge.image.Image("sys_minus_plus.png",16,16)

        self.mygear = mygear
        self.att_name = att_name
        self.att_min = att_min
        self.att_max = att_max
        self.on_change = on_change
        self.step = step

        self.add_left(pbge.widgets.LabelWidget(0, 0, 200, pbge.BIGFONT.get_linesize(), text=att_name, font=pbge.BIGFONT))
        self.add_right(pbge.widgets.ButtonWidget(0, 0, 16, 16, sprite=minus_plus_image, frame=0, on_click=self.stat_minus))
        self.add_right(pbge.widgets.LabelWidget(0, 0, 64, pbge.BIGFONT.get_linesize(), text_fun=self.stat_display, font=pbge.BIGFONT, justify=0))
        self.add_right(pbge.widgets.ButtonWidget(0, 0, 16, 16, sprite=minus_plus_image, frame=1, on_click=self.stat_plus))

    def stat_display(self,widg):
        return str(getattr(self.mygear,self.att_name))

    def stat_minus(self,widg,ev):
        ov = getattr(self.mygear,self.att_name)
        if ov > self.att_min:
            setattr(self.mygear,self.att_name,ov-self.step)
            if not self.change_is_okay():
                setattr(self.mygear, self.att_name, ov)
        if self.on_change:
            self.on_change()

    def stat_plus(self,widg,ev):
        ov = getattr(self.mygear,self.att_name)
        if ov < self.att_max:
            setattr(self.mygear,self.att_name,ov+self.step)
            if not self.change_is_okay():
                setattr(self.mygear, self.att_name, ov)
        if self.on_change:
            self.on_change()

    def change_is_okay(self):
        # Return True if the recent change doesn't break anything, False otherwise.
        ok = self.mygear.free_volume >= 0
        if ok:
            parent = self.mygear.parent
            if parent:
                if self.mygear in parent.sub_com:
                    ok = parent.can_install(self.mygear,False) and parent.free_volume >= 0
                else:
                    ok = parent.can_equip(self.mygear,False)
        return ok

#   ***********************
#   ***  PART  EDITORS  ***
#   ***********************

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


class ArmorEditWidget(PartEditWidget):
    def __init__(self, mygear, editor, **kwargs):
        super().__init__(mygear, editor, **kwargs)
        self.add_interior(PlusMinusWidget(mygear,"size",mygear.MIN_SIZE,mygear.MAX_SIZE,None))

class ShieldEditWidget(ArmorEditWidget):
    def __init__(self, mygear, editor, **kwargs):
        super().__init__(mygear, editor, **kwargs)
        self.add_interior(PlusMinusWidget(mygear,"bonus",mygear.MIN_BONUS,mygear.MAX_BONUS,None))

class EngineEditWidget(PartEditWidget):
    def __init__(self, mygear, editor, **kwargs):
        super().__init__(mygear, editor, **kwargs)
        self.add_interior(PlusMinusWidget(mygear,"size",mygear.MIN_SIZE,mygear.MAX_SIZE,None,step=5))

class SensorEditWidget(PartEditWidget):
    def __init__(self, mygear, editor, **kwargs):
        super().__init__(mygear, editor, **kwargs)
        self.add_interior(PlusMinusWidget(mygear,"size",mygear.MIN_SIZE,mygear.MAX_SIZE,None))

class MoveSysEditWidget(PartEditWidget):
    def __init__(self, mygear, editor, **kwargs):
        super().__init__(mygear, editor, **kwargs)
        self.add_interior(PlusMinusWidget(mygear,"size",1,25,None))

class PowerSourceEditWidget(PartEditWidget):
    def __init__(self, mygear, editor, **kwargs):
        super().__init__(mygear, editor, **kwargs)
        self.add_interior(PlusMinusWidget(mygear,"size",1,25,None))


CLASS_EDITORS = {
    gears.base.Armor: ArmorEditWidget,
    gears.base.Shield: ShieldEditWidget,
    gears.base.Engine: EngineEditWidget,
    gears.base.Sensor: SensorEditWidget,
    gears.base.MovementSystem: MoveSysEditWidget,
    gears.base.PowerSource: PowerSourceEditWidget,
}

#   *********************
#   ***  PART  MENUS  ***
#   *********************

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
            if self.editor:
                self.editor.mouseover_part = self.data
        elif self.data is self.editor.active_part:
            pbge.my_state.screen.blit(self.selected_image, myrect)
        else:
            pbge.my_state.screen.blit( self.regular_image , myrect )


class PartsTreeWidget(pbge.widgets.ColumnWidget):
    def __init__(self,mygear,editor,dx=-350,dy=-250,w=350,h=500,**kwargs):
        super().__init__(dx,dy,w,h,draw_border=True,center_interior=True,**kwargs)
        up_arrow = pbge.widgets.ButtonWidget(0,0,128,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),on_frame=0,off_frame=1)
        down_arrow = pbge.widgets.ButtonWidget(0,0,128,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),on_frame=2,off_frame=3)
        self.scroll_column = pbge.widgets.ScrollColumnWidget(0,0,w,h-50,up_arrow,down_arrow,padding=0)
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
    INFO_FRECT = pbge.frects.Frect(-300,-160,220,320)
    def __init__(self,sources,filter_fun,**kwargs):
        super().__init__(-50, -200, 350, 400, padding=20, **kwargs)

        self.filter_fun = filter_fun
        self.active_part = None
        self.active_part_info = None
        self.active_source = None
        self.mouseover_part = None

        # Create the tabs
        self.source_tabs = pbge.widgets.RowWidget(0,0,self.w,pbge.MEDIUMFONT.get_linesize(),padding=15)
        self.source_widgets = dict()
        for s in sources:
            mytab = SourceSelectorTab(s,on_click=self.click_tab)
            self.source_tabs.add_center(mytab)
            self.source_widgets[s] = mytab
        self.add_interior(self.source_tabs)

        # Create the list
        self.part_list_widget = PartsListWidget(0,0,self.w,325,sources[0].part_list, self)
        self.add_interior(self.part_list_widget)

        self.set_source(sources[0])

    def filter_part_list(self,part_list):
        if self.filter_fun:
            return [part for part in part_list if self.filter_fun(part)]
        else:
            return part_list

    def click_tab(self,widj,ev):
        self.set_source(widj.data)

    def set_source(self,source):
        if self.active_source:
            self.source_widgets[self.active_source].frame = self.source_widgets[self.active_source].off_frame
        self.active_source = source
        self.active_part = None
        self.source_widgets[self.active_source].frame = self.source_widgets[self.active_source].on_frame
        self.part_list_widget.set_new_list(self.filter_part_list(source.part_list))

    def click_part(self, widj, ev):
        self.active_part = widj.data
        self.active_part_info = gears.info.get_longform_display(self.active_part)

    def super_render( self ):
        self.mouseover_part = None
        super().super_render()
        if self.mouseover_part:
            mydest = self.INFO_FRECT.get_rect()
            gears.info.get_longform_display(self.mouseover_part).render(mydest.x, mydest.y)
        elif self.active_part:
            mydest = self.INFO_FRECT.get_rect()
            self.active_part_info.render(mydest.x, mydest.y)


class PartAcceptCancelWidget(PartSelectorWidget):
    # As above, but with Accept and Cancel buttons on the bottom.
    def __init__(self,sources,filter_fun,on_selection,**kwargs):
        super().__init__(sources, filter_fun, **kwargs)
        self.on_selection = on_selection

        # Create the Okay and Cancel buttons
        myrow = pbge.widgets.RowWidget(0,0,self.w,30,padding=15)
        myrow.add_center(pbge.widgets.LabelWidget(0,0,50,pbge.MEDIUMFONT.get_linesize(),"Accept",draw_border=True,on_click=self.accept,font=pbge.MEDIUMFONT))
        myrow.add_center(pbge.widgets.LabelWidget(0,0,50,pbge.MEDIUMFONT.get_linesize(),"Cancel",draw_border=True,on_click=self.cancel,font=pbge.MEDIUMFONT))
        self.add_interior(myrow)

    def accept(self,widj,ev):
        if self.active_part:
            self.on_selection(self.active_source.get_part(self.active_part))

    def cancel(self,widj,ev):
        self.active_part = False
        self.on_selection(None)


#   ******************************
#   ***  MECHA  STATS  HEADER  ***
#   ******************************

class MechaStatsHeader(pbge.widgets.Widget):
    def __init__(self,mecha):
        super().__init__(0,0,350,136)
        self.mecha = mecha

        self.bg = pbge.image.Image("sys_mechascalegrid.png", 136, 136)
        self.update_mecha_sprite()

        self.mecha_avatars = pbge.image.glob_images('mav_*.png')

        button_image = pbge.image.Image("sys_leftrightarrows.png",16,100)
        self.children.append(pbge.widgets.ButtonWidget(0,18,16,100,button_image,0,parent=self,anchor=pbge.frects.ANCHOR_UPPERLEFT,on_click=self.prev_avatar))
        self.children.append(pbge.widgets.ButtonWidget(152,18,16,100,button_image,1,parent=self,anchor=pbge.frects.ANCHOR_UPPERLEFT,on_click=self.next_avatar))

    def prev_avatar(self,widg,ev):
        if self.mecha.imagename in self.mecha_avatars:
            self.mecha.imagename = self.mecha_avatars[self.mecha_avatars.index(self.mecha.imagename)-1]
        else:
            self.mecha.imagename = self.mecha_avatars[0]
        self.update_mecha_sprite()

    def next_avatar(self,widg,ev):
        if self.mecha.imagename in self.mecha_avatars:
            i = self.mecha_avatars.index(self.mecha.imagename)+1
            if i >= len(self.mecha_avatars):
                i = 0
            self.mecha.imagename = self.mecha_avatars[i]
        else:
            self.mecha.imagename = self.mecha_avatars[0]
        self.update_mecha_sprite()

    def update_mecha_sprite(self):
        mybmp = pygame.Surface((64, 64))
        mybmp.fill((0, 0, 255))
        mybmp.set_colorkey((0, 0, 255), pygame.RLEACCEL)
        myimg = self.mecha.get_sprite()
        myimg.render(dest_surface=mybmp, dest=pygame.Rect(0, 0, 64, 64), frame=self.mecha.frame)
        self.image = pygame.transform.scale2x(mybmp)

    def get_text_rect(self):
        myrect = self.get_rect()
        myrect.x += 172
        myrect.w -= 172
        return myrect

    def render(self):
        mydest = self.get_rect()
        pbge.default_border.render(mydest)

        self.bg.render(pygame.Rect(mydest.x+16, mydest.y, 136, 136), 0)
        pbge.my_state.screen.blit(self.image, pygame.Rect(mydest.x + 20, mydest.y + 4, 128, 128))

        pbge.draw_text(
            pbge.MEDIUMFONT,
             "Cost: ${}\n Mass: {:.1f} tons\n Armor: {}\n Mobility: {}\n Speed: {}\n Sensor Range: {}\n E-War Progs: {}".format(
                self.mecha.cost,
                 self.mecha.mass / 10000.0,
                 self.mecha.calc_average_armor(),
                 self.mecha.calc_mobility(),
                 self.mecha.get_max_speed(),
                 self.mecha.get_sensor_range(self.mecha.scale),
                 self.mecha.get_ewar_rating()),
             self.get_text_rect(), justify=-1, color=pbge.INFO_GREEN
        )

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

        left_column = pbge.widgets.ColumnWidget(-350,-250,350,500,padding=25)
        self.children.append(left_column)

        left_column.add_interior(MechaStatsHeader(mygear))

        self.parts_widget = PartsTreeWidget(mygear,self,h=300)
        left_column.add_interior(self.parts_widget)

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
        self.part_selector = PartAcceptCancelWidget(self.sources,self.active_part.can_install,self._return_add_subcom)
        pbge.my_state.widgets.append(self.part_selector)
        self.active = False

    def _add_invcom(self,widj,ev):
        self.part_selector = PartAcceptCancelWidget(self.sources,self.active_part.can_equip,self._return_add_invcom)
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
        # Determine what sort of editor to use.
        myeditor = PartEditWidget
        for k,v in CLASS_EDITORS.items():
            if isinstance(self.active_part,k):
                myeditor = v
        self.active_part_editor = myeditor(self.active_part,self)
        self.children.append(self.active_part_editor)

    def update(self):
        self.parts_widget.refresh_gear_list()

    @classmethod
    def create_and_invoke(cls, redraw):
        # Create the UI. Run the UI. Clean up after you leave.
        mymek = gears.selector.get_design_by_full_name("SAN-X9c Urban Buru Buru")
        mymek.colors = (gears.color.ShiningWhite,gears.color.FreedomBlue,gears.color.ElectricYellow,gears.color.WarmGrey,gears.color.GunRed)
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


