import glob
import pbge
import json
from . import pbclasses
from .pbclasses import ALL_BRICKS, BRICKS_BY_LABEL, BRICKS_BY_NAME, PlotBrick, BluePrint
import pygame


class PartsNodeWidget(pbge.widgets.Widget):
    def __init__(self,mypart,indent,editor,**kwargs):
        self.font = pbge.BIGFONT
        super().__init__(0,0,350,self.font.get_linesize()+1,data=mypart,**kwargs)
        self.indent = indent
        self.editor = editor
        self.selected_image = self._draw_image(pbge.INFO_HILIGHT)
        self.regular_image = self._draw_image(pbge.INFO_GREEN)
        self.mouseover_image = self._draw_image(pbge.rpgmenu.MENU_SELECT_COLOR)

    def _part_text(self):
        return self.data.name

    def _draw_image(self,text_color):
        myimage = pygame.Surface((self.w,self.h))
        myimage.fill((0, 0, 0))
        myimage.set_colorkey((0, 0, 0), pygame.RLEACCEL)

        myimage.blit(self.font.render(self._part_text(),True,text_color),(self.indent*12,0))
        return myimage

    def render( self ):
        myrect = self.get_rect()
        if myrect.collidepoint(*pbge.my_state.mouse_pos):
            pbge.my_state.screen.blit( self.mouseover_image , myrect )
            if self.editor:
                self.editor.mouseover_part = self.data
        elif self.data is self.editor.active_part:
            pbge.my_state.screen.blit(self.selected_image, myrect)
        else:
            pbge.my_state.screen.blit( self.regular_image , myrect )


class PlotTreeWidget(pbge.widgets.ColumnWidget):
    def __init__(self,mypart,editor,dx=-350,dy=-250,w=325,h=500,**kwargs):
        super().__init__(dx,dy,w,h,draw_border=True,center_interior=True,**kwargs)
        up_arrow = pbge.widgets.ButtonWidget(0,0,128,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),on_frame=0,off_frame=1)
        down_arrow = pbge.widgets.ButtonWidget(0,0,128,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),on_frame=2,off_frame=3)
        self.scroll_column = pbge.widgets.ScrollColumnWidget(0,0,w,h-50,up_arrow,down_arrow,padding=0)
        self.add_interior(up_arrow)
        self.add_interior(self.scroll_column)
        self.add_interior(down_arrow)
        self.mypart = mypart
        self.editor = editor

        self.refresh_part_list()

    def refresh_part_list(self):
        self.scroll_column.clear()
        self.add_parts(self.mypart)


    def add_parts(self,part,indent=0):
        self.scroll_column.add_interior(PartsNodeWidget(part,indent,self.editor,on_click=self.editor.click_part))
        for bit in part.children:
            self.add_parts(bit,indent+1)


class StringVarEditorWidget(pbge.widgets.ColumnWidget):
    def __init__(self, part, var_name, default_value, **kwargs):
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + pbge.MEDIUMFONT.get_linesize() + 8,**kwargs)
        self.part = part
        self.var_name = var_name
        self.add_interior(pbge.widgets.LabelWidget(0,0,self.w,pbge.SMALLFONT.get_linesize(),var_name,font=pbge.SMALLFONT))
        self.add_interior(pbge.widgets.TextEntryWidget(0,0,350,pbge.MEDIUMFONT.get_linesize() + 8,default_value,on_change=self._do_change,font=pbge.MEDIUMFONT))

    def _do_change(self, widj, ev):
        self.part.vars[self.var_name] = widj.text

class TextVarEditorWidget(pbge.widgets.ColumnWidget):
    def __init__(self, part, var_name, default_value, **kwargs):
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + pbge.MEDIUMFONT.get_linesize() * 5 + 8,**kwargs)
        self.part = part
        self.var_name = var_name
        self.add_interior(pbge.widgets.LabelWidget(0,0,self.w,pbge.SMALLFONT.get_linesize(),var_name,font=pbge.SMALLFONT))
        self.add_interior(pbge.widgets.TextEditorWidget(0,0,350,pbge.MEDIUMFONT.get_linesize() * 5 + 8,default_value,on_change=self._do_change,font=pbge.MEDIUMFONT))

    def _do_change(self, widj, ev):
        self.part.vars[self.var_name] = widj.text


class VarEditorPanel(pbge.widgets.ColumnWidget):
    def __init__(self,mypart,editor,dx=10,dy=-200,w=350,h=450,**kwargs):
        super().__init__(dx,dy,w,h,draw_border=True,center_interior=True,**kwargs)
        up_arrow = pbge.widgets.ButtonWidget(0,0,128,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),on_frame=0,off_frame=1)
        down_arrow = pbge.widgets.ButtonWidget(0,0,128,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),on_frame=2,off_frame=3)
        self.scroll_column = pbge.widgets.ScrollColumnWidget(0,0,w,h-50,up_arrow,down_arrow,padding=0)
        self.add_interior(up_arrow)
        self.add_interior(self.scroll_column)
        self.add_interior(down_arrow)
        self.mypart = mypart
        self.editor = editor

        self.refresh_var_widgets()

    def refresh_var_widgets(self):
        self.scroll_column.clear()
        mybrick = self.editor.active_part.brick
        for k in mybrick.vars.keys():
            if mybrick.vars[k].var_type == "text":
                mywidget = TextVarEditorWidget(self.editor.active_part, k, self.editor.active_part.vars.get(k))
            else:
                mywidget = StringVarEditorWidget(self.editor.active_part, k, self.editor.active_part.vars.get(k))
            self.scroll_column.add_interior(
                mywidget
            )


class PlotCreator(pbge.widgets.Widget):
    def __init__(self, mytree: BluePrint, **kwargs):
        super().__init__(-400,-300,800,600,**kwargs)

        self.mytree = mytree
        self.active_part = mytree

        self.parts_widget = PlotTreeWidget(mytree,self)
        self.children.append(self.parts_widget)

        mybuttons = pbge.image.Image("sys_geareditor_buttons.png",40,40)
        mybuttonrow = pbge.widgets.RowWidget(25,-255,350,40)
        self.children.append(mybuttonrow)
        mybuttonrow.add_left(pbge.widgets.ButtonWidget(0,0,40,40,mybuttons,frame=2,on_frame=2,off_frame=3,on_click=self._add_feature,tooltip="Add Feature"))
        self.remove_gear_button = pbge.widgets.ButtonWidget(0,0,40,40,mybuttons,frame=4,on_frame=4,off_frame=5,on_click=self._remove_feature,tooltip="Remove Feature", show_when_inactive=True)
        mybuttonrow.add_left(self.remove_gear_button)
        mybuttonrow.add_right(pbge.widgets.ButtonWidget(0,0,40,40,mybuttons,frame=10,on_frame=10,off_frame=11,on_click=self._compile,tooltip="Compile Scenario"))
        mybuttonrow.add_right(pbge.widgets.ButtonWidget(0,0,40,40,mybuttons,frame=6,on_frame=6,off_frame=7,on_click=self._exit_editor,tooltip="Exit Editor"))

        self.vars_widget = VarEditorPanel(mytree, self)
        self.children.append(self.vars_widget)

        self.finished = False

        self.update_tree()

    def _add_feature(self,widj,ev):
        mymenu = pbge.rpgmenu.Menu(-100,-200,250,400)
        mymenu.add_descbox(175,-200,175,400)
        mybrick = self.active_part.brick
        for tlabel in mybrick.child_types:
            for tbrick in BRICKS_BY_LABEL.get(tlabel, ()):
                mymenu.add_item(tbrick.name, tbrick, tbrick.desc)
        nubrick = mymenu.query()
        if nubrick:
            newbp = BluePrint(nubrick)
            self.active_part.children.append(newbp)
            self.set_active_part(newbp)

    def _remove_feature(self,widj,ev):
        if self.active_part != self.mytree and hasattr(self.active_part, "container"):
            myparent = self.active_part.container.owner
            myparent.children.remove(self.active_part)
            self.set_active_part(myparent)

    def _exit_editor(self,widj,ev):
        self.finished = True

    def _compile(self, widj, ev):
        myprog = self.mytree.compile()
        fname = "ADV_{}.py".format(self.mytree.vars["uname"])
        with open(pbge.util.user_dir("content",fname), 'wt') as fp:
            for l in myprog["main"]:
                fp.write(l+'\n')
        pbge.alert("{} has been written to your content folder. You will need to restart GearHead to load the scenario.".format(fname))

    def click_part(self,widj,ev):
        if widj.data:
            self.set_active_part(widj.data)

    def set_active_part(self,new_part):
        self.active_part = new_part
        self.update_tree()

    def update_tree(self):
        self.parts_widget.refresh_part_list()
        self.vars_widget.refresh_var_widgets()

    @classmethod
    def create_and_invoke(cls, redraw):
        # Create the UI. Run the UI. Clean up after you leave.
        mytree = BluePrint(BRICKS_BY_NAME["Scenario"])
        myui = cls(mytree)
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


def init_plotcreator():
    protobits = list()
    myfiles = glob.glob(pbge.util.data_dir( "pb_*.json"))
    for f in myfiles:
        with open(f, 'rt') as fp:
            mylist = json.load(fp)
            if mylist:
                protobits += mylist
    for j in protobits:
        mybrick = PlotBrick(**j)
        ALL_BRICKS.append(mybrick)
        BRICKS_BY_LABEL[j["label"]].append(mybrick)
        if j["name"] in BRICKS_BY_NAME:
            print("Plot Brick Error: Multiple bricks named {}".format(j["name"]))
        BRICKS_BY_NAME[j["name"]] = mybrick

