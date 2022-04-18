import glob

import game.plotcreator.conditionals
import pbge
import json
from . import pbclasses, statefinders, pbvars, varwidgets
from .pbclasses import ALL_BRICKS, BRICKS_BY_LABEL, BRICKS_BY_NAME, PlotBrick, BluePrint
import pygame
import os

from .varwidgets import StringVarEditorWidget, CampaignVarNameWidget, TextVarEditorWidget, FiniteStateEditorWidget, \
    BoolEditorWidget, DialogueContextWidget, DialogueOfferDataWidget, ConditionalEditorWidget, MusicEditorWidget, \
    PaletteEditorWidget, AddRemoveFSOptionsWidget


class PartsNodeWidget(pbge.widgets.Widget):
    def __init__(self,mypart,indent,editor,physical_view=None,**kwargs):
        self.font = pbge.MEDIUMFONT
        super().__init__(0,0,325
                         ,self.font.get_linesize()+1,data=mypart,**kwargs)
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

    def render(self, flash=False):
        myrect = self.get_rect()
        if myrect.collidepoint(*pbge.my_state.mouse_pos):
            pbge.my_state.screen.blit( self.mouseover_image , myrect )
            if self.editor:
                self.editor.mouseover_part = self.data
        elif flash or (self.data is self.editor.active_part):
            pbge.my_state.screen.blit(self.selected_image, myrect)
        else:
            pbge.my_state.screen.blit( self.regular_image , myrect )

    def _builtin_responder(self, ev):
        if self.get_rect().collidepoint(pbge.my_state.mouse_pos):
            if self.is_kb_selectable() and (ev.type == pygame.MOUSEBUTTONUP) and (ev.button == 3) and not pbge.my_state.widget_clicked:
                if not pbge.my_state.widget_clicked:
                    pbge.my_state.active_widget = self
                pbge.my_state.widget_clicked = True
                self._open_popup()

    def _open_popup(self):
        mymenu = pbge.rpgmenu.PopUpMenu()
        mymenu.add_item("Copy", self._copy_node)
        if self.editor.clipboard and self.editor.clipboard.brick.label in self.data.brick.child_types:
            mymenu.add_item("Paste", self._paste_node)
        q = mymenu.query()
        if q:
            q()

    def _copy_node(self):
        self.editor.clipboard = self.data.copy()

    def _paste_node(self):
        self.data.children.append(self.editor.clipboard.copy())
        self.editor.update_tree()


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


class PhysicalTreeWidget(pbge.widgets.ColumnWidget):
    # Instead of editing the plot nodes directly, show the physical contents of this adventure.
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
        for k, v in mybrick.vars.items():
            mylist = v.get_widgets(self.editor.active_part, k, refresh_fun=self.refresh_var_widgets)
            for mywidget in mylist:
                self.scroll_column.add_interior(
                    mywidget
                )


class PlotCreator(pbge.widgets.Widget):
    def __init__(self, mytree: BluePrint, **kwargs):
        super().__init__(-400,-300,800,600,**kwargs)

        self.mytree = mytree
        self.active_part = mytree
        self.clipboard = None

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
        mymenu.sort()
        nubrick = mymenu.query()
        if nubrick:
            newbp = BluePrint(nubrick)
            self.active_part.children.append(newbp)
            self.mytree.sort()
            self.set_active_part(newbp)

    def _remove_feature(self,widj,ev):
        if self.active_part != self.mytree and hasattr(self.active_part, "container"):
            myparent = self.active_part.container.owner
            myparent.children.remove(self.active_part)
            self.mytree.sort()
            self.set_active_part(myparent)

    def _exit_editor(self,widj,ev):
        self.finished = True

    def _save(self, widj, ev):
        fname = "PLOTCREATOR_{}.json".format(self.mytree.raw_vars["uname"])
        with open(pbge.util.user_dir("content",fname), 'wt') as fp:
            json.dump(self.mytree.get_save_dict(), fp, indent='\t')

    def _compile(self, widj, ev):
        myprog = self.mytree.compile()
        fname = "ADV_{}.py".format(self.mytree.raw_vars["uname"])
        with open(pbge.util.user_dir("content",fname), 'wt') as fp:
            for l in myprog["main"]:
                fp.write(l+'\n')
        pbge.BasicNotification("{} has been written. You can start the scenario from the main menu.".format(fname))
        game.content.ghplots.reload_plot_module(fname.rpartition('.')[0])
        for k,v in myprog.items():
            if k != "main":
                print("Leftover section: {}".format(k))

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

        if myui.mytree.raw_vars["uname"]:
            myui._save(None, None)

        pbge.my_state.widgets.remove(myui)


def start_plot_creator(redraw):
    mainmenu = pbge.rpgmenu.Menu(-150, 0, 300, 226, predraw=redraw, font=pbge.BIGFONT)
    mainmenu.add_item("+Create New Scenario", "CNS")
    myfiles = glob.glob(pbge.util.user_dir( "content", "PLOTCREATOR_*.json"))
    for f in myfiles:
        mainmenu.add_item(os.path.basename(f), f)

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


class PlotBrickCompiler(object):
    def __init__(self, *args):
        self.myfiles = glob.glob(pbge.util.game_dir("ploteditorsource", "*.pes"))

        self.source_block = None
        self.current_file = None

        for fname in self.myfiles:
            mylist = self.load(fname)

    def load(self, fname):
        self.current_file = os.path.basename(fname)
        with open(fname, 'rt') as f:
            mylist = self.load_list(f)
        self.current_file = None
        return mylist

    def flush_buffer(self, current_brick, line_buffer: list):
        if not line_buffer:
            return
        elif not current_brick:
            print('Error: Flushing buffer without a brick!')
        elif self.source_block:
            current_brick["scripts"][self.source_block] = "".join(line_buffer)
        else:
            try:
                mydict = json.loads("{" + "".join(line_buffer) + "}")
                current_brick.update(mydict)
            except json.decoder.JSONDecodeError as err:
                print("JSON decode error: {} in {}".format(err, self.current_file))
                print("{" + "".join(line_buffer) + "}")
        self.source_block = None
        line_buffer.clear()

    def load_list(self, p_file):
        """Given an open file, load the text and return the json-compatiple list of plot brick dicts"""
        mylist = list()
        current_brick = None
        self.source_block = None
        line_buffer = list()
        keep_going = True

        # Load everything at once.
        while keep_going:
            rawline = p_file.readline()

            if not rawline:
                keep_going = False
            elif (rawline.startswith("#") or rawline.isspace()) and not self.source_block:
                # This is either a comment or a blank line. pass please. Unless we're in a source block, in which
                # case save the comment or blank line.
                pass
            elif rawline.startswith("*"):
                # Special command! Deal with it
                a, rawb = rawline[1:].split(maxsplit=2)
                b = ''.join(c for c in rawb if not c.isspace())
                if a == "NEW":
                    self.flush_buffer(current_brick, line_buffer)
                    current_brick = dict()
                    mylist.append(current_brick)
                    current_brick["label"] = b
                    current_brick['scripts'] = dict()
                elif a == "SCRIPT":
                    self.flush_buffer(current_brick, line_buffer)
                    self.source_block = b
                else:
                    print("Unknown command {}:{}\n{}".format(a, b, self.current_file))
            else:
                line_buffer.append(rawline)

        # Flush the buffer one more time.
        self.flush_buffer(current_brick, line_buffer)
