from . import lifepath
import pbge
import gears
import pygame
import collections
import random
from .. import cosplay
import copy


class LifepathChooser(object):
    def __init__(self,cgen):
        self.cgen = cgen

        # Record the character generator zones.
        self.title_zone = pbge.frects.Frect(-100,10,450,40)
        self.charsheet_zone = pbge.frects.Frect(-125,-200,500,180)
        self.info_zone = pbge.frects.Frect(-125,80,170,120)
        self.menu_zone = pbge.frects.Frect(75, 80, 300, 120)

        self.cancelled = False

        self.title = ''
        self.info = None

    def render(self):
        pbge.my_state.view()
        self.cgen.render()
        pbge.default_border.render(self.title_zone.get_rect())
        pbge.default_border.render(self.charsheet_zone.get_rect())
        pbge.default_border.render(self.info_zone.get_rect())
        pbge.default_border.render(self.menu_zone.get_rect())
        if self.title:
            pbge.draw_text(pbge.BIGFONT,self.title,self.title_zone.get_rect(),pbge.WHITE,justify=0)
        if self.info:
            myrect = self.charsheet_zone.get_rect()
            self.info.render(myrect.x,myrect.y)

    def create_menu(self):
        mymenu= pbge.rpgmenu.Menu(self.menu_zone.dx, self.menu_zone.dy, self.menu_zone.w, self.menu_zone.h, border=None,
                          predraw=self.render, font=pbge.BIGFONT)
        mymenu.add_descbox(self.info_zone.dx,self.info_zone.dy,self.info_zone.w,self.info_zone.h,font=pbge.MEDIUMFONT)
        return mymenu

    def choose_lifepath(self):
        self.info = lifepath.LifePathStatusPanel(model=self.cgen.pc,cgen=self.cgen,width=self.charsheet_zone.w,draw_border=False,padding=5)
        self.cgen.active = False

        self.title = "Where is your character from?"
        choices = lifepath.STARTING_CHOICES
        while choices and not self.cancelled:
            mymenu =self.create_menu()
            for c in choices:
                mymenu.add_item(c.name,c,c.desc)

            mychoice = mymenu.query()
            if mychoice:
                if mychoice.auto_fx:
                    mychoice.auto_fx.apply(self.cgen)
                    self.info.update()
                for c in mychoice.choices:
                    self.title = c.prompt
                    mymenu = self.create_menu()
                    for c2 in c.options:
                        mymenu.add_item(c2.name,c2,c2.desc)
                    myop = mymenu.query()
                    if myop:
                        myop.apply(self.cgen)
                        self.info.update()
                    else:
                        self.cancelled = True
                self.title = mychoice.next_prompt
                choices = mychoice.next
            else:
                self.cancelled = True

        self.cgen.active = True
        self.info = None


class PortraitBitSelector(pbge.widgets.RowWidget):
    def __init__(self, width, height, bname, form_tags, button_image, use_style, on_prev_bit: pbge.widgets.On_Click, on_next_bit: pbge.widgets.On_Click, **kwargs):
        super().__init__(0, 0, width, height, on_click=on_next_bit, **kwargs)
        self.add_center(pbge.widgets.LabelWidget(0,0,250,0,bname,font=pbge.MEDIUMFONT,draw_border=True, should_hilight=self._should_hilight_label))
        mylist = sorted(gears.portraits.Portrait.get_list_of_type(gears.portraits.PORTRAIT_BITS[bname].btype,form_tags,False,use_style=use_style),key=lambda b: b.name)
        if len(mylist) > 1:
            self.add_left(pbge.widgets.ButtonWidget(0,0,16,16,button_image,frame=0,data=(bname,mylist),on_click=on_prev_bit))
            self.add_right(pbge.widgets.ButtonWidget(0,0,16,16,button_image,frame=1,data=(bname,mylist),on_click=on_next_bit))
        self.on_prev_bit = on_prev_bit
        self.on_next_bit = on_next_bit
        self.data = (bname,mylist)

    def _should_hilight_label(self, _widg):
        return self.should_hilight(self)

    def _builtin_responder(self, ev):
        if self.should_hilight(self) and (ev.type == pygame.KEYDOWN):
            if pbge.my_state.is_key_for_action(ev, "left"):
                self.on_prev_bit(self, ev)
                self.register_response()
            elif pbge.my_state.is_key_for_action(ev, "right"):
                self.on_next_bit(self, ev)
                self.register_response()

    def _render(self, delta):
        pass


class PortraitEditorW(pbge.widgets.Widget):
    def __init__(self, pc, por_gen, portrait, form_tags, cgen=None, **kwargs):
        super(PortraitEditorW, self).__init__(-400, -300, 800, 600, **kwargs)
        self.pc = pc
        self.por = por_gen
        self.portrait = portrait
        self.form_tags = form_tags
        self.sl = pbge.StretchyLayer()
        self.cgen = cgen

        self.minus_plus_image = pbge.image.Image("sys_minus_plus.png",16,16)

        self.outer_column = pbge.widgets.ColumnWidget(-50,-250,300,500,draw_border=False,center_interior=True)
        self.children.append(self.outer_column)

        self.style_on = True
        self.style_button = pbge.widgets.LabelWidget(0,0,200,0,text="Style Rules: On",justify=0,on_click=self.toggle_style,draw_border=True, can_take_focus=True)
        self.outer_column.add_interior(self.style_button)

        self.up_button = pbge.widgets.ButtonWidget(0, 0, 128, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), off_frame=1)
        self.down_button = pbge.widgets.ButtonWidget(0, 0, 128, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), frame=2, on_frame=2, off_frame=3)

        self.option_column = pbge.widgets.ScrollColumnWidget(-50,-200,300,400,up_button=self.up_button, down_button=self.down_button, draw_border=False)
        self.outer_column.add_interior(self.up_button)
        self.outer_column.add_interior(self.option_column)
        self.outer_column.add_interior(self.down_button)
        self.rebuild_menu()

        self.children.append(pbge.widgets.LabelWidget(150,220,80,0,text="Done",justify=0,on_click=self.done_button,draw_border=True, can_take_focus=True))

        self.finished = False

    def toggle_style(self, *_args):
        self.style_on = not self.style_on
        if self.style_on:
            self.style_button.text = "Style Rules: On"
        else:
            self.style_button.text = "Style Rules: Off"
        self.rebuild_menu()

    def rebuild_menu(self):
        current_active = self.option_column.selected_widget_id
        if self.option_column.children:
            self.option_column.clear()
        form_tags = list(self.form_tags)
        for bname in self.por.bits:
            myrow = PortraitBitSelector(300, 32, bname, form_tags, self.minus_plus_image, self.style_on, self.prev_bit, self.next_bit)
            form_tags += gears.portraits.PORTRAIT_BITS[bname].form_tags
            self.option_column.add_interior(myrow)
        self.option_column.set_item_by_position(current_active)

    def prev_bit(self, wid,_ev):
        # Change this bit.
        # bname is the name of the current bit, mylist is the list of potential replacements.
        bname,mylist = wid.data
        if gears.portraits.PORTRAIT_BITS[bname] in mylist:
            old_i = mylist.index(gears.portraits.PORTRAIT_BITS[bname])
        else:
            old_i = 0
        new_i = old_i - 1
        bit_pos = self.por.bits.index(bname)
        self.por.bits[bit_pos] = mylist[new_i].name
        self.por.verify(self.pc,self.form_tags)
        self.portrait = self.por.build_portrait(self.pc,force_rebuild=True,form_tags=self.form_tags)
        self.rebuild_menu()

    def next_bit(self,wid,_ev):
        # Change this bit.
        # bname is the name of the current bit, mylist is the list of potential replacements.
        bname,mylist = wid.data
        if gears.portraits.PORTRAIT_BITS[bname] in mylist:
            new_i = mylist.index(gears.portraits.PORTRAIT_BITS[bname]) + 1
        else:
            new_i = 0
        if new_i >= len(mylist):
            new_i = 0
        bit_pos = self.por.bits.index(bname)
        self.por.bits[bit_pos] = mylist[new_i].name
        self.por.verify(self.pc,self.form_tags)
        self.portrait = self.por.build_portrait(self.pc,force_rebuild=True)
        self.rebuild_menu()

    def _render(self, delta):
        self.sl.clear()
        mydest = pygame.Rect(self.sl.get_width()//2-400, 0, 600, 600)
        self.portrait.render(mydest, 0, dest_surface=self.sl.surf)
        self.portrait.render(mydest, 2, dest_surface=self.sl.surf)
        self.sl.render()

    def done_button(self,_wid,_ev):
        if self.cgen:
            self.cgen.portrait_view.portrait = self.portrait
        self.pop()

    def _builtin_responder(self, ev):
        if self.active and self.visible and not pbge.my_state.widget_responded:
            if ev.type == pygame.KEYDOWN and pbge.my_state.is_key_for_action(ev, "exit"):
                self.done_button(self, ev)
                self.register_response()

    @classmethod
    def push_state_and_instantiate_with_cgen(cls, *widgets_to_push, cgen=None, formtags=()):
        myui = cls(cgen.pc, cgen.pc.portrait_gen, cgen.portrait_view.portrait, formtags, cgen=cgen)
        myui.push_and_deploy(*widgets_to_push)

    @classmethod
    def push_state_and_instantiate_with_pc(cls, *widgets_to_push, pc=None):
        myui = cls(pc, pc.portrait_gen, pc.get_portrait(), gears.portraits.Portrait.get_form_tags(pc))
        myui.push_and_deploy(*widgets_to_push)


class GenderCustomizationWidget(pbge.widgets.ColumnWidget):
    PROPERTIES = ("noun", "adjective", "subject_pronoun", "object_pronoun", "possessive_determiner",
                  "absolute_pronoun", "reflexive_pronoun")
    def __init__(self, pc: gears.base.Character, **kwargs):
        super().__init__(-200, -225, 400, 450, center_interior=True, padding=16, draw_border=True, **kwargs)
        self.set_header(pbge.widgets.LabelWidget(0,0,200,0,"Custom Gender",color=pbge.WHITE, font=pbge.BIGFONT, justify=0, draw_border=True))

        self.pc = pc
        self.gender = copy.deepcopy(pc.gender)
        self.property_widgets = dict()

        for prop in self.PROPERTIES:
            mywidget = pbge.widgets.ColTextEntryWidget(
                self.w, prop, getattr(self.gender, prop),
                on_change=self._set_property, data=prop
            )
            self.add_interior(mywidget)
            self.property_widgets[prop] = mywidget

        self.style_menu = pbge.widgetmenu.ColDropdownWidget(
            self.w, "Style Options", on_select=self._set_style
        )
        self.add_interior(self.style_menu)
        self.style_menu.add_item("All Options", None, {gears.genderobj.TAG_MASC, gears.genderobj.TAG_FEMME})
        self.style_menu.add_item("Feminine", None, {gears.genderobj.TAG_FEMME,})
        self.style_menu.add_item("Masculine", None, {gears.genderobj.TAG_MASC,})
        self.style_menu.set_item_by_data(self.gender.tags)

        self.add_interior(pbge.widgets.LabelWidget(
            0,0,200,0,"Set Default Female", justify=0, draw_border=True, on_click=self._set_defaults,
            data=self.gender.DEF_FEMALE_PARAMS
        ))
        self.add_interior(pbge.widgets.LabelWidget(
            0,0,200,0,"Set Default Male", justify=0, draw_border=True, on_click=self._set_defaults,
            data=self.gender.DEF_MALE_PARAMS
        ))
        self.add_interior(pbge.widgets.LabelWidget(
            0,0,200,0,"Set Default Nonbinary", justify=0, draw_border=True, on_click=self._set_defaults,
            data=self.gender.DEF_NONBINARY_PARAMS
        ))

        myrow = pbge.widgets.RowWidget(0, 0, self.w, 16)
        myrow.add_left(pbge.widgets.LabelWidget(0,0,100,0,"Done",font=pbge.BIGFONT, on_click=self._done, justify=0,
                                                draw_border=True))
        myrow.add_right(pbge.widgets.LabelWidget(0,0,100,0,"Cancel",font=pbge.BIGFONT, on_click=self._cancel,
                                                 justify=0, draw_border=True))
        self.add_interior(myrow)

    def _done(self, _wid, _ev):
        self.pc.gender = self.gender
        self.pop()

    def _cancel(self, _wid, _ev):
        self.pop()

    def _set_defaults(self, wid, _ev):
        for k,v in wid.data.items():
            setattr(self.gender, k, v)
            if k in self.PROPERTIES:
                self.property_widgets[k].quietly_set_text(v)

        self.style_menu.set_item_by_data(self.gender.tags)

    def _set_property(self, wid, _ev):
        setattr(self.gender, wid.data, wid.text)

    def _set_style(self, result):
        self.gender.tags = result

    # The create_and_invoke(cls, pc) method has been depreciated. In the blocking style game interface, this
    # method used to instantiate the widget and run it in a private game loop. Now that GHC uses an unblocking
    # interface with a central loop its functionality has been replace by push_state_and_instantiate. I leave
    # the following massive comment as a demonstration of why this UI overhaul was necessary, and also as a
    # warning to future generations.
    #
    #    Run the UI. You know, usually I'm a big fan of commenting code but I just noticed that I've copied and
    #    pasted this "create_and_invoke" method a bazillion times (often with very minor changes that make it
    #    difficult to genderalize) and most of them have kept the comment from the Invoker widget. This method
    #    will not return an Invocation object. Most of the cases where the comment says create_and_invoke will
    #    return an Invocation object are lying to you, unless you're dealing with an Invoker widget or one of its
    #    descendants. I leave this extra long comment here as a warning to other programmers who may be reading
    #    this code. When you copy and paste something a lot, consider making it a method of the parent class.
    #    And if you can't do that, then for Eris' sake check the comments and make sure they stll apply to your
    #    modified version.



class CharacterGeneratorW(pbge.widgets.Widget):
    STAT_POINTS = 105
    C1_WIDTH = 260
    C2_WIDTH = 230
    C3_WIDTH = 120
    MECHA_PRICE_LIMIT = 300000
    def __init__(self,year=158,**kwargs):
        super().__init__(-400, -300, 800, 600, **kwargs)
        self.pc = gears.base.Character(name="New Character",portrait_gen=gears.portraits.Portrait(),job=gears.jobs.Job("Cavalier"))
        self.year = year

        self.pc.roll_stats(self.STAT_POINTS)
        self.bio_bonuses = collections.defaultdict(int)

        self.biogram = dict()
        self.bio_personality = list()
        self.bio_badges = list()
        lifepath.generate_random_lifepath(self)

        self.unspent_stat_points = 0

        self.finished = False

        self.title = ''

        self.column_one = pbge.widgets.ColumnWidget(-125,-200,self.C1_WIDTH,400,draw_border=True)
        self.name_field = pbge.widgets.TextEntryWidget(0,0,200,30,justify=0,text=gears.selector.random_name(self.pc))
        self.column_one.set_header(self.name_field)
        age_gender_row = pbge.widgets.RowWidget(0,0,self.C1_WIDTH,30)
        age_menu = pbge.widgetmenu.DropdownWidget(0,0,140,30,font=pbge.BIGFONT,on_select=self.set_age)
        for age in range(18,36):
            age_menu.add_item("{} year old".format(age), None, age)
        age_menu.menu.set_item_by_position(min(random.randint(0,17),random.randint(0,17)))
        age_gender_row.add_center(age_menu)
        gender_menu = pbge.widgetmenu.DropdownWidget(0,0,110,30,font=pbge.BIGFONT,on_select=self.set_gender)
        gender_menu.add_item("Male", None, gears.genderobj.Gender.get_default_male())
        gender_menu.add_item("Female", None, gears.genderobj.Gender.get_default_female())
        gender_menu.add_item("Nonbinary", None, gears.genderobj.Gender.get_default_nonbinary())
        gender_menu.add_item("Custom", None, 1234567)
        gender_menu.menu.set_item_by_position(random.choice((0,0,0,1,1,1,2)))
        self.pc.gender = gender_menu.menu.current_data

        age_gender_row.add_center(gender_menu)
        self.column_one.add_interior(age_gender_row)

        self.mecha_menu = pbge.widgetmenu.DropdownWidget(0,0,self.C1_WIDTH,25,font=pbge.MEDIUMFONT)
        self.reset_mecha_menu()
        self.column_one.add_interior(self.mecha_menu)

        minus_plus_image = pbge.image.Image("sys_minus_plus.png",16,16)
        for s in gears.stats.PRIMARY_STATS:
            nu_row = pbge.widgets.RowWidget(0,0,self.C1_WIDTH,30)
            nu_row.add_left(pbge.widgets.LabelWidget(0,0,150,pbge.BIGFONT.get_linesize(),text=s.name,font=pbge.BIGFONT))
            nu_row.add_right(pbge.widgets.ButtonWidget(0,0,16,16,sprite=minus_plus_image,frame=0,data=s,on_click=self.stat_minus))
            nu_row.add_right(pbge.widgets.LabelWidget(0,0,32,pbge.BIGFONT.get_linesize(),text_fun=self.stat_display,data=s,font=pbge.BIGFONT,justify=0))
            nu_row.add_right(pbge.widgets.ButtonWidget(0,0,16,16,sprite=minus_plus_image,frame=1,data=s,on_click=self.stat_plus))
            self.column_one.add_interior(nu_row)
        self.column_one.add_interior(pbge.widgets.LabelWidget(0,0,self.C1_WIDTH,0,text_fun=self.stat_point_display,justify=0))
        random_reset_row = pbge.widgets.RowWidget(0,0,self.C1_WIDTH,30)
        random_reset_row.add_left(pbge.widgets.LabelWidget(0,0,100,pbge.SMALLFONT.get_linesize(),text="Random",font=pbge.SMALLFONT,on_click=self.stat_randomize,draw_border=True,justify=0,can_take_focus=True))
        random_reset_row.add_right(pbge.widgets.LabelWidget(0,0,100,pbge.SMALLFONT.get_linesize(),text="Reset",font=pbge.SMALLFONT,on_click=self.stat_reset,draw_border=True,justify=0, can_take_focus=True))
        self.column_one.add_interior(random_reset_row)

        self.column_one.add_interior(pbge.widgets.LabelWidget(0,0,self.C1_WIDTH,100,text_fun=self.skill_display))

        self.children.append(self.column_one)

        self.column_two = pbge.widgets.ColumnWidget(160,-200,self.C2_WIDTH,400,draw_border=True)
        self.column_two.add_interior(pbge.widgets.LabelWidget(0,0,self.C2_WIDTH,360,text_fun=self.biography_display,justify=-1,font=pbge.SMALLFONT))
        random_reset_row = pbge.widgets.RowWidget(0,0,self.C2_WIDTH,30)
        random_reset_row.add_left(pbge.widgets.LabelWidget(0,0,100,pbge.SMALLFONT.get_linesize(),text="Random",font=pbge.SMALLFONT,on_click=self.biography_randomize,draw_border=True,justify=0, can_take_focus=True))
        random_reset_row.add_right(pbge.widgets.LabelWidget(0,0,100,pbge.SMALLFONT.get_linesize(),text="Choose",font=pbge.SMALLFONT,on_click=self.biography_choose,draw_border=True,justify=0, can_take_focus=True))
        self.column_two.add_interior(random_reset_row)

        self.children.append(self.column_two)

        self.column_three = pbge.widgets.ColumnWidget(-375,100,self.C3_WIDTH,120,draw_border=False,padding=10)
        self.column_three.add_interior(pbge.widgets.LabelWidget(0,0,self.C3_WIDTH,0,text="Random Portait",justify=0,on_click=self.portrait_random,draw_border=True, can_take_focus=True))
        self.column_three.add_interior(pbge.widgets.LabelWidget(0,0,self.C3_WIDTH,0,text="Edit Portait",justify=0,on_click=self.portrait_edit,draw_border=True, can_take_focus=True))
        self.column_three.add_interior(pbge.widgets.LabelWidget(0,0,self.C3_WIDTH,0,text="Random Colors",justify=0,on_click=self.color_random,draw_border=True, can_take_focus=True))
        self.column_three.add_interior(pbge.widgets.LabelWidget(0,0,self.C3_WIDTH,0,text="Edit Colors",justify=0,on_click=self.color_edit,draw_border=True, can_take_focus=True))

        self.children.append(self.column_three)

        self.children.append(pbge.widgets.LabelWidget(160,210,self.C2_WIDTH,0,text="Save Character",justify=0,on_click=self.save_egg,draw_border=True,font=pbge.BIGFONT, can_take_focus=True))
        self.children.append(pbge.widgets.LabelWidget(160,240,self.C2_WIDTH,0,text="Cancel",justify=0,on_click=self.cancel,draw_border=True,font=pbge.BIGFONT, can_take_focus=True))

        self.portrait_view = gears.portraits.PortraitView(self.pc.portrait_gen.build_portrait(self.pc,form_tags=self.get_portrait_tags()))

    def set_age(self,new_age):
        self.pc.birth_year = self.year - new_age

    def set_gender(self,new_gender):
        if new_gender == 1234567:
            GenderCustomizationWidget.push_state_and_instantiate(self, pc=self.pc)
        else:
            self.pc.gender = new_gender

    def stat_display(self,wid):
        return str(self.pc.get_stat(wid.data) + self.bio_bonuses.get(wid.data,0))

    def stat_minus(self,wid,_ev):
        if self.pc.statline[wid.data] > 5:
            self.pc.statline[wid.data] -= 1
            self.unspent_stat_points += 1

    def stat_plus(self,wid,_ev):
        if self.pc.statline[wid.data] < 18 and self.unspent_stat_points > 0:
            self.pc.statline[wid.data] += 1
            self.unspent_stat_points -= 1

    def stat_point_display(self,_wid):
        return "{} Stat Points".format(self.unspent_stat_points)

    def stat_randomize(self,_wid,_ev):
        if self.unspent_stat_points > 0:
            self.pc.roll_stats(self.unspent_stat_points,False)
            self.unspent_stat_points = 0
        else:
            self.pc.roll_stats(self.STAT_POINTS)

    def stat_reset(self,_wid,_ev):
        self.unspent_stat_points = self.STAT_POINTS
        for s in gears.stats.PRIMARY_STATS:
            self.pc.statline[s] = 5
            self.unspent_stat_points -= 5

    def skill_display(self,_wid):
        skillz = [sk.name for sk in list(self.bio_bonuses.keys()) if sk in gears.stats.NONCOMBAT_SKILLS]
        skillz.sort()
        sk_block = ', '.join(skillz or ["None"])
        skillz = [b.name for b in self.bio_badges]
        skillz.sort()
        bad_block = ', '.join(skillz or ["None"])
        skillz =  [b.name for b in self.bio_personality]
        skillz.sort()
        tag_block = ', '.join(skillz or ["None"])
        return 'Skills: {}\n Badges: {}\n Tags: {}'.format(sk_block,bad_block,tag_block)

    def biography_display(self,_wid):
        return self.pc.bio

    def _reset_biography(self):
        self.bio_bonuses.clear()
        self.bio_personality = list()
        self.bio_badges = list()
        self.biogram.clear()
        self.pc.bio = ""
        self.pc.portrait_gen.color_channels = list(gears.color.CHARACTER_COLOR_CHANNELS)

    def reset_mecha_menu(self):
        mymek = self.mecha_menu.menu.current_data
        self.mecha_menu.clear()
        if gears.personality.GreenZone in self.bio_personality:
            fac = gears.factions.TerranFederation
        elif gears.personality.DeadZone in self.bio_personality:
            fac = gears.factions.DeadzoneFederation
        else:
            fac = None
        mecha_shopping_list = gears.selector.MechaShoppingList(self.MECHA_PRICE_LIMIT,fac)
        for mek in mecha_shopping_list.best_choices:
            self.mecha_menu.add_item(mek.get_full_name(), None, mek)
        for mek in mecha_shopping_list.backup_choices:
            self.mecha_menu.add_item(mek.get_full_name(), None, mek)
        self.mecha_menu.menu.sort()
        if mymek and self.mecha_menu.menu.has_value(mymek):
            self.mecha_menu.menu.set_item_by_data(mymek)
        else:
            self.mecha_menu.menu.set_item_by_data(random.choice(mecha_shopping_list.best_choices))

    def biography_randomize(self,_wid,_ev):
        self._reset_biography()
        lifepath.generate_random_lifepath(self)
        self.reset_mecha_menu()

    def biography_choose(self,_wid,_ev):
        self._reset_biography()
        self.column_one.active = False
        self.column_two.active = False
        self.column_three.active = False
        my_chooser = LifepathChooser(self)
        my_chooser.choose_lifepath()
        if my_chooser.cancelled:
            self.biography_randomize(None,None)
        self.column_one.active = True
        self.column_two.active = True
        self.column_three.active = True
        self.reset_mecha_menu()

    def get_portrait_tags(self):
        mytags = gears.portraits.Portrait.get_form_tags(self.pc)
        for pt in self.bio_personality:
            _=mytags.append(pt.name)
        return mytags

    def portrait_edit(self,_wid,_ev):
        PortraitEditorW.push_state_and_instantiate_with_cgen(self, cgen=self, formtags=self.get_portrait_tags())

    def portrait_random(self,_wid,_ev):
        self.pc.portrait_gen.random_portrait(self.pc,form_tags=self.get_portrait_tags())
        self.portrait_view.portrait = self.pc.portrait_gen.build_portrait(self.pc,force_rebuild=True)

    def color_edit(self,_wid,ev):
        self.active = False
        myui = cosplay.ColorEditor(self.pc.portrait_gen.build_portrait(self.pc,add_color=False),0,channel_filters=self.pc.portrait_gen.color_channels,colors=self.pc.colors)
        pbge.my_state.widgets.append(myui)
        myui.finished = False
        myui.children.append(pbge.widgets.LabelWidget(150,220,80,0,text="Done",justify=0,on_click=self.color_done,draw_border=True,data=myui))

        keepgoing = True
        while keepgoing and not myui.finished and not pbge.my_state.got_quit:
            ev = pbge.wait_event()
            if ev.type == pbge.TIMEREVENT:
                pbge.my_state.view()
                pbge.my_state.do_flip()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    keepgoing = False

        self.pc.colors = myui.colors
        self.portrait_view.portrait = self.pc.portrait_gen.build_portrait(self.pc,force_rebuild=True)

        pbge.my_state.widgets.remove(myui)
        pygame.event.clear()
        self.active = True

    def color_done(self,wid,_ev):
        wid.data.finished = True

    def color_random(self,_wid,_ev):
        self.pc.colors = self.pc.portrait_gen.generate_random_colors(self.pc)
        self.portrait_view.portrait = self.pc.portrait_gen.build_portrait(self.pc,force_rebuild=True)

    def save_egg(self,_wid,_ev):
        if not pbge.my_state.widget_responded:
            my_egg = gears.eggs.Egg(self.pc)
            self.pc.name = self.name_field.text
            if self.unspent_stat_points > 0:
                self.pc.roll_stats(self.unspent_stat_points,clear_first=False)
            for sk in gears.stats.FUNDAMENTAL_COMBATANT_SKILLS:
                self.pc.statline[sk] = 4
            for sk in gears.stats.EXTRA_COMBAT_SKILLS:
                self.pc.statline[sk] = 1
            num_fives = 4
            for k,v in list(self.bio_bonuses.items()):
                self.pc.statline[k] += v
                if k in gears.stats.NONCOMBAT_SKILLS:
                    self.pc.statline[k] += 3
                    num_fives -= 1
            if num_fives > 0:
                for sk in random.sample(gears.stats.COMBATANT_SKILLS,num_fives):
                    self.pc.statline[sk] += 1
            self.pc.personality.update( self.bio_personality)
            self.pc.badges += self.bio_badges
            my_egg.mecha = copy.deepcopy(self.mecha_menu.value)
            my_egg.mecha.colors = gears.color.random_mecha_colors()
            my_egg.credits = 200000 - my_egg.mecha.cost // 2
            my_egg.save()
            self.pop()

    def cancel(self,_wid,_ev):
        self.pop()

    def _render(self, delta):
        self.portrait_view.render()

    def _builtin_responder(self, ev):
        if self.active and self.visible and not pbge.my_state.widget_responded:
            if ev.type == pygame.KEYDOWN and pbge.my_state.is_key_for_action(ev, "exit"):
                self.pop()
                self.register_response()

    TAGS_TO_HIDE = {"WTAG_TITLEMENU",}

