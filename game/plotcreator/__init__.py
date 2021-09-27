import glob

import game.plotcreator.conditionals
import gears
import pbge
import json
from . import pbclasses, statefinders
from .pbclasses import ALL_BRICKS, BRICKS_BY_LABEL, BRICKS_BY_NAME, PlotBrick, BluePrint
import pygame
import os



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

class StringVarEditorWidget(pbge.widgets.ColumnWidget):
    def __init__(self, part, var_name, default_value, **kwargs):
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + pbge.MEDIUMFONT.get_linesize() + 8,**kwargs)
        self.part = part
        self.var_name = var_name
        self.add_interior(pbge.widgets.LabelWidget(0,0,self.w,pbge.SMALLFONT.get_linesize(),var_name,font=pbge.SMALLFONT))
        self.add_interior(pbge.widgets.TextEntryWidget(0,0,350,pbge.MEDIUMFONT.get_linesize() + 8,str(default_value),on_change=self._do_change,font=pbge.MEDIUMFONT))

    def _do_change(self, widj, ev):
        self.part.raw_vars[self.var_name] = widj.text


class CampaignVarNameWidget(pbge.widgets.ColumnWidget):
    def __init__(self, part, var_name, **kwargs):
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + pbge.MEDIUMFONT.get_linesize() + 8,**kwargs)
        self.part = part
        self.var_name = var_name
        self.add_interior(pbge.widgets.LabelWidget(0,0,self.w,pbge.SMALLFONT.get_linesize(),var_name,font=pbge.SMALLFONT))
        myrow = pbge.widgets.RowWidget(0,0,self.w, pbge.MEDIUMFONT.get_linesize() + 8)
        self.add_interior(myrow)
        self.text_widget = pbge.widgets.TextEntryWidget(0,0,300,pbge.MEDIUMFONT.get_linesize() + 8,str(part.raw_vars.get(var_name,"x")),on_change=self._do_change,font=pbge.MEDIUMFONT)
        myrow.add_left(self.text_widget)
        myrow.add_right(pbge.widgets.LabelWidget(0,0,40,pbge.MEDIUMFONT.get_linesize() + 4, "<--", font=pbge.MEDIUMFONT, justify=0, draw_border=True, on_click=self._click_arrow))

    def _do_change(self, widj, ev):
        self.part.raw_vars[self.var_name] = widj.text

    def _click_arrow(self, wid, ev):
        mymenu = pbge.rpgmenu.PopUpMenu(w=300)
        for cvn in self.part.get_campaign_variable_names():
            mymenu.add_item(cvn, cvn)
        mymenu.sort()
        choice = mymenu.query()
        if choice:
            self.text_widget.text = choice


class TextVarEditorWidget(pbge.widgets.ColumnWidget):
    def __init__(self, part, var_name, default_value, **kwargs):
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + pbge.MEDIUMFONT.get_linesize() * 5 + 8,**kwargs)
        self.part = part
        self.var_name = var_name
        self.add_interior(pbge.widgets.LabelWidget(0,0,self.w,pbge.SMALLFONT.get_linesize(),var_name,font=pbge.SMALLFONT))
        self.add_interior(pbge.widgets.TextEditorWidget(0,0,350,pbge.MEDIUMFONT.get_linesize() * 5 + 8,default_value,on_change=self._do_change,font=pbge.MEDIUMFONT))

    def _do_change(self, widj, ev):
        self.part.raw_vars[self.var_name] = widj.text


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
        self.legal_states = list()

        self.refresh_fun = refresh_fun

        if desc_fun:
            mymenu.menu.add_descbox(-325, 0, 300, mymenu.MENU_HEIGHT, anchor=pbge.frects.ANCHOR_UPPERLEFT, parent=mymenu.menu)
            for name,value in my_states:
                mymenu.add_item(name, value, desc_fun(value))
                self.legal_states.append(value)

        else:
            for name,value in my_states:
                mymenu.add_item(name, value)
                self.legal_states.append(value)

        mymenu.menu.sort()
        mymenu.menu.set_item_by_value(part.raw_vars.get(var_name, None))

    def _do_change(self, result):
        if result in self.legal_states:
            self.part.raw_vars[self.var_name] = result
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
        mymenu.menu.set_item_by_value(part.raw_vars.get(var_name, True))

    def _do_change(self, result):
        self.part.raw_vars[self.var_name] = result


class DialogueContextWidget(FiniteStateEditorWidget):
    def __init__(self, part: BluePrint, var_name, desc_fun=None, refresh_fun=None, **kwargs):
        super().__init__(part, var_name, desc_fun, refresh_fun, **kwargs)
        myinfo = statefinders.CONTEXT_INFO.get(part.raw_vars.get(var_name, None), None)
        if myinfo:
            self.add_interior(pbge.widgets.LabelWidget(
                0,0,self.w,0, myinfo.desc,
                font=pbge.SMALLFONT, justify=0, color=pbge.INFO_GREEN
            ))
        self.add_interior(pbge.widgets.LabelWidget(
            0,0,self.w,0, self.get_comes_from_and_goes_to(part.raw_vars.get(var_name, None)),
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
        mycontext = part.raw_vars.get("context", None)
        if mycontext:
            myinfo = statefinders.CONTEXT_INFO.get(mycontext, None)
            if myinfo:
                for d in myinfo.needed_data:
                    self.add_interior(DataDictItemEditorWidget(part, part.raw_vars[var_name], d))

        if len(self.children) < 2:
            self.add_interior(
                pbge.widgets.LabelWidget(0, 0, self.w, pbge.SMALLFONT.get_linesize(), "No Data", justify=0, color=pbge.INFO_GREEN, font=pbge.SMALLFONT))


class ConditionalValueEditor(pbge.widgets.RowWidget):
    def __init__(self, part, val_list, refresh_fun, **kwargs):
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + 8,**kwargs)
        var_type = pbge.widgets.DropdownWidget(0, 0, 150, self.h, font=pbge.SMALLFONT, on_select=self.set_type)
        for vt in game.plotcreator.conditionals.CONDITIONAL_VALUE_TYPES:
            var_type.add_item(vt.capitalize(), vt)
        var_type.menu.set_item_by_value(val_list[0])
        val_list[0] = var_type.value
        self.add_left(var_type)

        self.val_list = val_list
        self.refresh_fun = refresh_fun

        if val_list[0] == game.plotcreator.conditionals.CONDITIONAL_VALUE_TYPES[0]:
            # This is an integer.
            value_entry = pbge.widgets.TextEntryWidget(0,0,150,self.h, str(val_list[1]),font=pbge.SMALLFONT,justify=0, on_change=self.set_text)
            self.add_left(value_entry)
        elif val_list[0] == game.plotcreator.conditionals.CONDITIONAL_VALUE_TYPES[1]:
            # This is a campaign variable.
            name_entry = pbge.widgets.DropdownWidget(0, 0, 150, self.h, font=pbge.SMALLFONT, on_select=self.set_value)
            for cvn in part.get_campaign_variable_names():
                name_entry.add_item(cvn, cvn)
            name_entry.menu.sort()
            name_entry.add_item('None', None)
            name_entry.menu.set_item_by_value(val_list[1])
            self.add_left(name_entry)

    def set_type(self, result):
        if self.val_list[0] != result:
            self.val_list[0] = result
            if result == game.plotcreator.conditionals.CONDITIONAL_VALUE_TYPES[0]:
                self.val_list[1] = 0
            elif result == game.plotcreator.conditionals.CONDITIONAL_VALUE_TYPES[1]:
                self.val_list[1] = None
            self.refresh_fun()

    def set_value(self, result):
        self.val_list[1] = result

    def set_text(self, wid, ev):
        self.val_list[1] = wid.text

class ConditionalOperatorEditor(pbge.widgets.RowWidget):
    def __init__(self, part, var_name, var_index, refresh_fun, **kwargs):
        super().__init__(0, 0, 350, pbge.SMALLFONT.get_linesize() + 8, **kwargs)
        self.part = part
        self.var_name = var_name
        self.var_index = var_index
        self.dropper = pbge.widgets.DropdownWidget(0, 0, 320, pbge.SMALLFONT.get_linesize() + 8, font=pbge.SMALLFONT, justify=0, on_select=self.set_value)
        self.add_left(self.dropper)
        for op in game.plotcreator.conditionals.CONDITIONAL_EXPRESSION_OPS:
            self.dropper.add_item(op.capitalize(), op)
        for op,desc in conditionals.CONDITIONAL_FUNCTIONS.items():
            self.dropper.add_item(op.capitalize(), op)
        self.dropper.menu.set_item_by_value(part.raw_vars[var_name][var_index][0])
        self.refresh_fun = refresh_fun

        self.add_right(pbge.widgets.LabelWidget(0,0,20,pbge.SMALLFONT.get_linesize() + 4, "X", font=pbge.SMALLFONT, justify=0, draw_border=True, on_click=self._delete_expression))

    def _delete_expression(self, wid, ev):
        mylist = self.part.raw_vars[self.var_name]
        if self.var_index > 0:
            del mylist[self.var_index-1:self.var_index+1]
        elif len(mylist) > 1:
            del mylist[0:2]
        else:
            del mylist[self.var_index]
        self.refresh_fun()

    def set_value(self, result):
        old_var = self.part.raw_vars[self.var_name][self.var_index][0]
        if old_var in game.plotcreator.conditionals.CONDITIONAL_EXPRESSION_OPS and result in game.plotcreator.conditionals.CONDITIONAL_EXPRESSION_OPS:
            self.part.raw_vars[self.var_name][self.var_index][0] = result
        elif result:
            # Gonna need a brand new expression.
            self.part.raw_vars[self.var_name][self.var_index] = game.plotcreator.conditionals.generate_new_conditional_expression(result)
            self.refresh_fun()


class ConditionalFunParamEditor(pbge.widgets.RowWidget):
    def __init__(self, part, val_list, param_type, param_index, refresh_fun, **kwargs):
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + 8,**kwargs)
        var_type = pbge.widgets.LabelWidget(0, 0, 150, self.h, param_type, justify=1, font=pbge.SMALLFONT)
        self.add_left(var_type)

        self.val_list = val_list
        self.param_index = param_index
        self.refresh_fun = refresh_fun

        if param_type == game.plotcreator.conditionals.CONDITIONAL_VALUE_TYPES[0]:
            # This is an integer.
            value_entry = pbge.widgets.TextEntryWidget(0,0,150,self.h, str(val_list[1]),font=pbge.SMALLFONT,justify=0, on_change=self.set_text)
            self.add_left(value_entry)
        elif param_type == game.plotcreator.conditionals.CONDITIONAL_VALUE_TYPES[1]:
            # This is a campaign variable.
            name_entry = pbge.widgets.DropdownWidget(0, 0, 150, self.h, font=pbge.SMALLFONT, on_select=self.set_value)
            for cvn in part.get_campaign_variable_names():
                name_entry.add_item(cvn, "camp.campdata.get(\"{}\", 0)".format(cvn))
            name_entry.menu.sort()
            name_entry.add_item('None', None)
            name_entry.menu.set_item_by_value(val_list[1])
            self.add_left(name_entry)
        else:
            # Dunno what this is. Assume it's a finite state thingamabob.
            name_entry = pbge.widgets.DropdownWidget(0, 0, 150, self.h, font=pbge.SMALLFONT, on_select=self.set_value)
            for fsname,fscode in statefinders.get_possible_states(part, param_type):
                name_entry.add_item(fsname,fscode)
            name_entry.add_item('None', None)
            name_entry.menu.set_item_by_value(val_list[param_index])
            self.add_left(name_entry)

    def set_value(self, result):
        self.val_list[self.param_index] = result

    def set_text(self, wid, ev):
        self.val_list[self.param_index] = wid.text


class ConditionalExpressionEditor(pbge.widgets.ColumnWidget):
    def __init__(self, part, var_name, var_index, refresh_fun, **kwargs):
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + 8, **kwargs)
        self.part = part
        self.var_name = var_name
        self.var_index = var_index
        elist = self.part.raw_vars[var_name][var_index]
        if elist[0] in game.plotcreator.conditionals.CONDITIONAL_EXPRESSION_OPS:
            self.add_interior(ConditionalValueEditor(part, elist[1], refresh_fun))
            self.add_interior(ConditionalOperatorEditor(part, var_name, var_index, refresh_fun))
            self.add_interior(ConditionalValueEditor(part, elist[2], refresh_fun))
        elif elist[0] in conditionals.CONDITIONAL_FUNCTIONS:
            self.add_interior(ConditionalOperatorEditor(part, var_name, var_index, refresh_fun))
            for pt, t in enumerate(conditionals.CONDITIONAL_FUNCTIONS[elist[0]].param_types, 1):
                self.add_interior(ConditionalFunParamEditor(part, elist, pt, t, refresh_fun))


class BooleanOperatorEditor(pbge.widgets.DropdownWidget):
    def __init__(self, part, var_name, var_index, refresh_fun, **kwargs):
        super().__init__(0, 0, 350, pbge.SMALLFONT.get_linesize() + 8, font=pbge.SMALLFONT, justify=0, on_select=self._select_operator, **kwargs)
        self.part = part
        self.var_name = var_name
        self.var_index = var_index
        self.refresh_fun = refresh_fun
        for op in game.plotcreator.conditionals.CONDITIONAL_BOOL_OPS:
            self.add_item(op.capitalize(), op)
        self.menu.set_item_by_value(part.raw_vars[var_name][var_index])

    def _select_operator(self, result):
        if result:
            self.part.raw_vars[self.var_name][self.var_index] = result
            #self.refresh_fun()


class ConditionalEditorWidget(pbge.widgets.ColumnWidget):
    def __init__(self, part, var_name, refresh_fun, **kwargs):
        my_conditions = part.raw_vars.get(var_name, list())
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + pbge.MEDIUMFONT.get_linesize() + 8,**kwargs)
        self.add_interior(pbge.widgets.LabelWidget(0,0,self.w,pbge.SMALLFONT.get_linesize(),var_name,font=pbge.SMALLFONT))
        self.part = part
        self.var_name = var_name
        self.refresh_fun = refresh_fun

        for t, item in enumerate(my_conditions):
            if isinstance(item, list):
                # This is an expression.
                self.add_interior(ConditionalExpressionEditor(part, var_name, t, refresh_fun))
            else:
                # This must be a boolean operator.
                self.add_interior(BooleanOperatorEditor(part, var_name, t, refresh_fun))

        self.add_interior(pbge.widgets.LabelWidget(0,0,100,0,"Add Expression", draw_border=True, on_click=self.add_expression))

    def add_expression(self, wid, ev):
        my_conditions = self.part.raw_vars.get(self.var_name, list())
        if not isinstance(my_conditions, list):
            my_conditions = list()
            self.part.raw_vars[self.var_name] = my_conditions
        if my_conditions:
            my_conditions.append(game.plotcreator.conditionals.CONDITIONAL_BOOL_OPS[0])
        my_conditions.append(game.plotcreator.conditionals.generate_new_conditional_expression(
            game.plotcreator.conditionals.CONDITIONAL_EXPRESSION_OPS[2]))
        self.refresh_fun()


class MusicEditorWidget(pbge.widgets.ColumnWidget):
    def __init__(self, part: BluePrint, var_name, **kwargs):
        # desc_fun, if it exists, is a function that takes value and returns a description
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + pbge.MEDIUMFONT.get_linesize() + 8,**kwargs)
        self.part = part
        self.var_name = var_name
        self.add_interior(pbge.widgets.LabelWidget(0,0,self.w,pbge.SMALLFONT.get_linesize(),var_name,font=pbge.SMALLFONT))

        myrow = pbge.widgets.RowWidget(0,0,self.w, pbge.MEDIUMFONT.get_linesize() + 8)
        self.add_interior(myrow)

        mymenu = pbge.widgets.DropdownWidget(0,0,300,pbge.MEDIUMFONT.get_linesize() + 8,justify=0,font=pbge.MEDIUMFONT, on_select=self._do_change)
        myrow.add_left(mymenu)
        mymenu.menu.w += 200
        self.legal_states = list(pbge.my_state.get_music_list())
        for name in self.legal_states:
            mymenu.add_item(name, name)
        mymenu.add_item("==None==", None)
        self.legal_states.append(None)
        mymenu.menu.sort()
        mymenu.menu.set_item_by_value(part.raw_vars.get(var_name, None))

        mybutton = pbge.widgets.LabelWidget(0,0,40,pbge.MEDIUMFONT.get_linesize()+2, "play", font=pbge.MEDIUMFONT, on_click=self._click_play, draw_border=True, justify=0)
        myrow.add_right(mybutton)

    def _do_change(self, result):
        if result in self.legal_states:
            self.part.raw_vars[self.var_name] = result

    def _click_play(self, wid, ev):
        mysong = self.part.raw_vars.get(self.var_name, None)
        if mysong:
            pbge.my_state.start_music(mysong, True)

class ColorSwatchEditorWidget(pbge.widgets.DropdownWidget):
    def __init__(self, mypalette, color_index, **kwargs):
        super().__init__(0, 0, 24, 36, on_select=self.update_swatch, **kwargs)
        self.palette = mypalette
        self.color_index = color_index
        self.sprite = None
        self.update_swatch(self.palette[self.color_index])
        self.menu.w = 300
        for c in gears.color.ALL_COLORS:
            self.add_item(c.name, gears.SINGLETON_REVERSE[c])
        self.menu.sort()

    def update_swatch(self, color_name):
        if color_name:
            self.palette[self.color_index] = color_name
            color = gears.SINGLETON_TYPES[color_name]
            self.sprite = pbge.image.Image("sys_color_menu_swatch.png", 24, 36, color=[color, color, color, color, color])

    def render( self ):
        self.sprite.render(self.get_rect(), 0)


class PaletteEditorWidget(pbge.widgets.ColumnWidget):
    def __init__(self, part: BluePrint, var_name, **kwargs):
        super().__init__(0,0,350,pbge.SMALLFONT.get_linesize() + 36,**kwargs)
        self.part = part
        self.var_name = var_name
        self.add_interior(pbge.widgets.LabelWidget(0,0,self.w,pbge.SMALLFONT.get_linesize(),var_name,font=pbge.SMALLFONT))

        myrow = pbge.widgets.RowWidget(0,0,self.w, 36)
        self.add_interior(myrow)

        mypalette = part.raw_vars.get(var_name)
        for t in range(5):
            myrow.add_center(ColorSwatchEditorWidget(mypalette, t))


class AddRemoveFSOptionsWidget(pbge.widgets.ColumnWidget):
    def __init__(self, part, var_name,**kwargs):
        super().__init__(0,0,350,100,**kwargs)
        self.part = part
        self.var_name = var_name

        self.ops_taken = part.raw_vars[var_name]

        self.op_candidates = tuple(a[0] for a in statefinders.get_possible_states(part, part.brick.vars[var_name].var_type[5:]))

        mytitle = pbge.widgets.RowWidget(0,0,self.w,max(pbge.SMALLFONT.get_linesize(),16))
        minus_plus_image = pbge.image.Image("sys_minus_plus.png",16,16)
        mytitle.add_left(pbge.widgets.LabelWidget(0,0,250,mytitle.h,font=pbge.SMALLFONT,text=var_name))

        mytitle.add_right(pbge.widgets.ButtonWidget(0,0,16,16,minus_plus_image,on_click=self._delete_op,active=kwargs.get("active",True)))
        mytitle.add_right(pbge.widgets.ButtonWidget(0,0,16,16,minus_plus_image,frame=1,on_click=self._add_op,active=kwargs.get("active",True)))
        self.add_interior(mytitle)
        self.add_interior(pbge.widgets.LabelWidget(0,0,300,50,font=pbge.MEDIUMFONT,draw_border=True,text_fun=self._get_op_string))

    def _get_op_string(self, widg):
        if not self.ops_taken:
            return "None"
        elif len(self.ops_taken) == 1:
            return str(self.ops_taken[0])
        else:
            return ', '.join([str(p) for p in self.ops_taken])

    def _delete_op(self,widg,ev):
        if self.ops_taken:
            mymenu = pbge.rpgmenu.PopUpMenu()
            for p in self.ops_taken:
                mymenu.add_item(p, p)
            delete_this_one = mymenu.query()
            if delete_this_one in self.ops_taken:
                self.ops_taken.remove(delete_this_one)

    def _add_op(self,widg,ev):
        mymenu = pbge.rpgmenu.PopUpMenu()
        for p in self.op_candidates:
            if p not in self.ops_taken:
                mymenu.add_item(p,p)
        add_this_one = mymenu.query()
        if add_this_one:
            self.ops_taken.append(add_this_one)


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
                mywidget = TextVarEditorWidget(self.editor.active_part, k, self.editor.active_part.raw_vars.get(k))
            elif mybrick.vars[k].var_type == "campaign_variable":
                mywidget = CampaignVarNameWidget(self.editor.active_part, k)
            elif mybrick.vars[k].var_type in ("faction", "scene", "npc"):
                mywidget = FiniteStateEditorWidget(self.editor.active_part, k)
            elif mybrick.vars[k].var_type in statefinders.LIST_TYPES:
                mywidget = FiniteStateEditorWidget(self.editor.active_part, k)
            elif mybrick.vars[k].var_type.endswith(".png"):
                mywidget = FiniteStateEditorWidget(self.editor.active_part, k)
            elif mybrick.vars[k].var_type == "boolean":
                mywidget = BoolEditorWidget(self.editor.active_part, k, self.editor.active_part.raw_vars.get(k))
            elif mybrick.vars[k].var_type == "dialogue_context":
                mywidget = DialogueContextWidget(self.editor.active_part, k, lambda v: statefinders.CONTEXT_INFO[v].desc, refresh_fun=self.refresh_var_widgets)
            elif mybrick.vars[k].var_type == "dialogue_data":
                mywidget = DialogueOfferDataWidget(self.editor.active_part, k)
            elif mybrick.vars[k].var_type == "conditional":
                mywidget = ConditionalEditorWidget(self.editor.active_part, k, refresh_fun=self.refresh_var_widgets)
            elif mybrick.vars[k].var_type == "music":
                mywidget = MusicEditorWidget(self.editor.active_part, k)
            elif mybrick.vars[k].var_type == "palette":
                mywidget = PaletteEditorWidget(self.editor.active_part, k)
            elif mybrick.vars[k].var_type.startswith("list:"):
                mywidget = AddRemoveFSOptionsWidget(self.editor.active_part, k)
            else:
                mywidget = StringVarEditorWidget(self.editor.active_part, k, self.editor.active_part.raw_vars.get(k))
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
            self.set_active_part(newbp)

    def _remove_feature(self,widj,ev):
        if self.active_part != self.mytree and hasattr(self.active_part, "container"):
            myparent = self.active_part.container.owner
            myparent.children.remove(self.active_part)
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

