import glob

import gears
import pbge
import json
from . import pbclasses, statefinders
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
        self.add_interior(pbge.widgets.TextEntryWidget(0,0,350,pbge.MEDIUMFONT.get_linesize() + 8,str(default_value),on_change=self._do_change,font=pbge.MEDIUMFONT))

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


class FiniteStateEditorWidget(pbge.widgets.ColumnWidget):
    def __init__(self, part: BluePrint, var_name, desc_fun=None, refresh_fun=None, **kwargs):
        # desc_fun, if it exists, is a function that takes value and returns a description
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + pbge.MEDIUMFONT.get_linesize() + 8,**kwargs)
        self.part = part
        self.var_name = var_name
        self.add_interior(pbge.widgets.LabelWidget(0,0,self.w,pbge.SMALLFONT.get_linesize(),var_name,font=pbge.SMALLFONT))

        my_states = statefinders.get_possible_states(part, part.brick.vars[var_name].var_type)
        mymenu = pbge.widgets.DropdownWidget(0,0,350,pbge.MEDIUMFONT.get_linesize() + 8,justify=0,font=pbge.MEDIUMFONT, on_select=self._do_change)
        self.add_interior(mymenu)

        self.refresh_fun = refresh_fun

        if desc_fun:
            mymenu.menu.add_descbox(-325, 0, 300, mymenu.MENU_HEIGHT, anchor=pbge.frects.ANCHOR_UPPERLEFT, parent=mymenu.menu)
            for name,value in my_states:
                mymenu.add_item(name, value, desc_fun(value))

        else:
            for name,value in my_states:
                mymenu.add_item(name, value)

        mymenu.menu.sort()
        mymenu.menu.set_item_by_value(part.vars.get(var_name,None))

    def _do_change(self, result):
        self.part.vars[self.var_name] = result
        if self.refresh_fun:
            self.refresh_fun()


class BoolEditorWidget(pbge.widgets.ColumnWidget):
    def __init__(self, part, var_name, default_value, **kwargs):
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + pbge.MEDIUMFONT.get_linesize() + 8,**kwargs)
        self.part = part
        self.var_name = var_name
        self.add_interior(pbge.widgets.LabelWidget(0,0,self.w,pbge.SMALLFONT.get_linesize(),var_name,font=pbge.SMALLFONT))
        mymenu = pbge.widgets.DropdownWidget(0,0,350,pbge.MEDIUMFONT.get_linesize() + 8,justify=0,font=pbge.MEDIUMFONT, on_select=self._do_change)
        self.add_interior(mymenu)
        mymenu.add_item("True", True)
        mymenu.add_item("False", False)
        mymenu.menu.set_item_by_value(part.vars.get(var_name,True))

    def _do_change(self, result):
        self.part.vars[self.var_name] = result


class DialogueContextWidget(FiniteStateEditorWidget):
    def __init__(self, part: BluePrint, var_name, desc_fun=None, refresh_fun=None, **kwargs):
        super().__init__(part, var_name, desc_fun, refresh_fun, **kwargs)
        myinfo = statefinders.CONTEXT_INFO.get(part.vars.get(var_name, None), None)
        if myinfo:
            self.add_interior(pbge.widgets.LabelWidget(
                0,0,self.w,0, myinfo.desc,
                font=pbge.SMALLFONT, justify=0, color=pbge.INFO_GREEN
            ))
        self.add_interior(pbge.widgets.LabelWidget(
            0,0,self.w,0, self.get_comes_from_and_goes_to(part.vars.get(var_name, None)),
            font=pbge.SMALLFONT, justify=0, color=pbge.INFO_GREEN
        ))

    def get_comes_from_and_goes_to(self, mycontext):
        cf = set()
        gt = set()
        if mycontext:
            for rep in pbge.dialogue.STANDARD_REPLIES:
                if rep.context[0] == mycontext:
                    gt.add(rep.destination.context[0])
                if rep.destination.context[0] == mycontext:
                    cf.add(rep.context[0])
        if cf:
            cfs = ', '.join(cf)
        else:
            cfs = "None"
        if gt:
            gts = ', '.join(gt)
        else:
            gts = "None"
        return "Comes From: {}\nGoes To: {}".format(cfs,gts)


class DataDictItemEditorWidget(pbge.widgets.RowWidget):
    def __init__(self, part, mydict, mykey, **kwargs):
        super().__init__(0,0,350,pbge.MEDIUMFONT.get_linesize() * 3 + 8,**kwargs)
        self.part = part
        self.mydict = mydict
        self.mykey = mykey
        self.add_left(pbge.widgets.LabelWidget(0,0,90,self.h,mykey,font=pbge.SMALLFONT, justify=1, color=pbge.INFO_GREEN))
        self.add_right(pbge.widgets.TextEditorWidget(0,0,250,pbge.MEDIUMFONT.get_linesize() * 3 + 8, str(mydict.get(mykey,"")),on_change=self._do_change,font=pbge.MEDIUMFONT))

    def _do_change(self, widj, ev):
        self.mydict[self.mykey] = widj.text


class DialogueOfferDataWidget(pbge.widgets.ColumnWidget):
    def __init__(self, part, var_name, **kwargs):
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + pbge.MEDIUMFONT.get_linesize() + 8,**kwargs)

        self.var_name = var_name
        self.add_interior(pbge.widgets.LabelWidget(0,0,self.w,pbge.SMALLFONT.get_linesize(),var_name,font=pbge.SMALLFONT))
        mycontext = part.vars.get("context", None)
        if mycontext:
            myinfo = statefinders.CONTEXT_INFO.get(mycontext, None)
            if myinfo:
                for d in myinfo.needed_data:
                    self.add_interior(DataDictItemEditorWidget(part, part.vars[var_name], d))

        if len(self.children) < 2:
            self.add_interior(
                pbge.widgets.LabelWidget(0, 0, self.w, pbge.SMALLFONT.get_linesize(), "No Data", justify=0, color=pbge.INFO_GREEN, font=pbge.SMALLFONT))


class VarEditorPanel(pbge.widgets.ColumnWidget):
    def __init__(self,mypart,editor,dx=10,dy=-200,w=350,h=450,**kwargs):
        super().__init__(dx,dy,w,h,draw_border=True,center_interior=True,**kwargs)
        up_arrow = pbge.widgets.ButtonWidget(0,0,128,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),on_frame=0,off_frame=1)
        down_arrow = pbge.widgets.ButtonWidget(0,0,128,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),on_frame=2,off_frame=3)
        self.scroll_column = pbge.widgets.ScrollColumnWidget(0,0,w,h-50,up_arrow,down_arrow,padding=10)
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
            elif mybrick.vars[k].var_type == "faction":
                mywidget = FiniteStateEditorWidget(self.editor.active_part, k)
            elif mybrick.vars[k].var_type == "boolean":
                mywidget = BoolEditorWidget(self.editor.active_part, k, self.editor.active_part.vars.get(k))
            elif mybrick.vars[k].var_type == "dialogue_context":
                mywidget = DialogueContextWidget(self.editor.active_part, k, lambda v: statefinders.CONTEXT_INFO[v].desc, refresh_fun=self.refresh_var_widgets)
            elif mybrick.vars[k].var_type == "dialogue_data":
                mywidget = DialogueOfferDataWidget(self.editor.active_part, k)
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
        mybuttonrow.add_right(pbge.widgets.ButtonWidget(0,0,40,40,mybuttons,frame=8,on_frame=8,off_frame=9,on_click=self._save,tooltip="Save Scenario"))
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

    def _save(self, widj, ev):
        fname = "PLOTCREATOR_{}.json".format(self.mytree.vars["uname"])
        with open(pbge.util.user_dir("content",fname), 'wt') as fp:
            json.dump(self.mytree.get_save_dict(), fp, indent='\t')

    def _compile(self, widj, ev):
        myprog = self.mytree.compile()
        fname = "ADV_{}.py".format(self.mytree.vars["uname"])
        with open(pbge.util.user_dir("content",fname), 'wt') as fp:
            for l in myprog["main"]:
                fp.write(l+'\n')
        pbge.BasicNotification("{} has been written. Restart GearHead to load the scenario.".format(fname))

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
    def create_and_invoke(cls, redraw, mytree):
        # Create the UI. Run the UI. Clean up after you leave.
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


def start_plot_creator(redraw):
    mainmenu = pbge.rpgmenu.Menu(-150, 0, 300, 226, predraw=redraw, font=pbge.BIGFONT)
    mainmenu.add_item("+Create New Scenario", "CNS")
    myfiles = glob.glob(pbge.util.user_dir( "content", "PLOTCREATOR_*.json"))
    for f in myfiles:
        mainmenu.add_item(f, f)

    fname = mainmenu.query()
    if fname == "CNS":
        mytree = BluePrint(BRICKS_BY_NAME["Scenario"])
        PlotCreator.create_and_invoke(redraw, mytree)
    elif fname:
        with open(fname, 'rt') as fp:
            mydict = json.load(fp)
            if mydict:
                mytree = BluePrint.load_save_dict(mydict)
                PlotCreator.create_and_invoke(redraw, mytree)


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

