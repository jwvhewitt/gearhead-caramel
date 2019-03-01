import lifepath
import pbge
import gears
import pygame
import collections
import random
from .. import cosplay


class LifepathChooser(object):
    def __init__(self,cgen):
        self.cgen = cgen

        # Record the character generator zones.
        self.title_zone = pbge.frects.Frect(-100,30,450,20)
        self.charsheet_zone = pbge.frects.Frect(-125,-200,500,200)
        self.info_zone = pbge.frects.Frect(-125,80,170,120)
        self.menu_zone = pbge.frects.Frect(75, 80, 300, 120)

        self.cancelled = False

        self.title = ''
        self.info = None

    def render(self):
        pbge.my_state.view()
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

        self.info = None

class PortraitEditorW(pbge.widgets.Widget):
    def __init__(self,cgen,**kwargs):
        super(PortraitEditorW, self).__init__(-400, -300, 800, 600, **kwargs)
        self.cgen = cgen
        self.pc = cgen.pc
        self.por = cgen.pc.portrait_gen
        self.portrait = cgen.portrait

        self.portrait_zone = pbge.frects.Frect(-400,-300,400,600)
        self.minus_plus_image = pbge.image.Image("sys_minus_plus.png",16,16)

        self.option_column = pbge.widgets.ColumnWidget(-50,-200,300,400,draw_border=False)
        self.children.append(self.option_column)
        self.rebuild_menu()

        self.finished = False

    def rebuild_menu(self):
        if self.option_column.children:
            self.option_column.clear()
        form_tags = gears.portraits.Portrait.get_form_tags(self.pc)
        for bname in self.por.bits:
            myrow = pbge.widgets.RowWidget(0,0,300,32)
            myrow.add_center(pbge.widgets.LabelWidget(0,0,250,pbge.MEDIUMFONT.get_linesize()+4,bname,font=pbge.MEDIUMFONT,draw_border=True))
            mylist = gears.portraits.Portrait.get_list_of_type(gears.portraits.PORTRAIT_BITS[bname].btype,form_tags,False)
            if len(mylist) > 1:
                myrow.add_left(pbge.widgets.ButtonWidget(0,0,16,16,self.minus_plus_image,frame=0,data=(bname,mylist),on_click=self.prev_bit))
                myrow.add_right(pbge.widgets.ButtonWidget(0,0,16,16,self.minus_plus_image,frame=1,data=(bname,mylist),on_click=self.next_bit))
            form_tags += gears.portraits.PORTRAIT_BITS[bname].form_tags
            self.option_column.add_interior(myrow)

    def prev_bit(self,wid,ev):
        # Change this bit.
        # bname is the name of the current bit, mylist is the list of potential replacements.
        bname,mylist = wid.data
        new_i = mylist.index(gears.portraits.PORTRAIT_BITS[bname]) - 1
        bit_pos = self.por.bits.index(bname)
        self.por.bits[bit_pos] = mylist[new_i].name
        self.por.verify(self.pc)
        self.portrait = self.por.build_portrait(self.pc,force_rebuild=True)
        self.rebuild_menu()

    def next_bit(self,wid,ev):
        # Change this bit.
        # bname is the name of the current bit, mylist is the list of potential replacements.
        bname,mylist = wid.data
        new_i = mylist.index(gears.portraits.PORTRAIT_BITS[bname]) + 1
        if new_i >= len(mylist):
            new_i = 0
        bit_pos = self.por.bits.index(bname)
        self.por.bits[bit_pos] = mylist[new_i].name
        self.por.verify(self.pc)
        self.portrait = self.por.build_portrait(self.pc,force_rebuild=True)
        self.rebuild_menu()

    def render(self):
        self.portrait.render(self.portrait_zone.get_rect(),0)

    def done_button(self,wid,ev):
        self.finished = True

    @classmethod
    def create_and_invoke(cls, cgen):
        # Run the UI. Return a DoInvocation action if an invocation
        # was chosen, or None if the invocation was cancelled.
        myui = cls(cgen)
        pbge.my_state.widgets.append(myui)
        myui.children.append(pbge.widgets.LabelWidget(150,220,80,16,text="Done",justify=0,on_click=myui.done_button,draw_border=True))

        keepgoing = True
        while keepgoing and not myui.finished and not pbge.my_state.got_quit:
            ev = pbge.wait_event()
            if ev.type == pbge.TIMEREVENT:
                pbge.my_state.view()
                pbge.my_state.do_flip()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    keepgoing = False
                elif ev.key == pygame.K_F1:
                    pygame.image.save(myui.portrait.bitmap, pbge.util.user_dir("out.png"))

        cgen.portrait = myui.portrait
        pbge.my_state.widgets.remove(myui)


class CharacterGeneratorW(pbge.widgets.Widget):
    STAT_POINTS = 105
    C1_WIDTH = 260
    C2_WIDTH = 220
    C3_WIDTH = 120
    def __init__(self,year=158,**kwargs):
        super(CharacterGeneratorW, self).__init__(-400, -300, 800, 600, **kwargs)
        self.pc = gears.base.Character(name="New Character",portrait_gen=gears.portraits.Portrait(),job=gears.jobs.Job("Cavalier"))
        self.year = year

        self.pc.roll_stats(self.STAT_POINTS)
        self.bio_bonuses = collections.defaultdict(int)

        self.biogram = dict()
        lifepath.generate_random_lifepath(self)

        self.unspent_stat_points = 0

        self.finished = False

        self.title = ''

        self.portrait_zone = pbge.frects.Frect(-450,-300,400,600)

        self.column_one = pbge.widgets.ColumnWidget(-125,-200,self.C1_WIDTH,400,draw_border=True)
        self.name_field = pbge.widgets.TextEntryWidget(0,0,200,30,justify=0,text=gears.selector.random_name(self.pc))
        self.column_one.set_header(self.name_field)
        age_gender_row = pbge.widgets.RowWidget(0,0,self.C1_WIDTH,30)
        age_menu = pbge.widgets.DropdownWidget(0,0,140,30,font=pbge.BIGFONT,on_select=self.set_age)
        for age in range(18,36):
            age_menu.add_item("{} year old".format(age),age)
        age_menu.menu.set_item_by_position(min(random.randint(0,17),random.randint(0,17)))
        age_gender_row.add_center(age_menu)
        gender_menu = pbge.widgets.DropdownWidget(0,0,110,30,font=pbge.BIGFONT,on_select=self.set_gender)
        gender_menu.add_item("Male",gears.genderobj.Gender.get_default_male())
        gender_menu.add_item("Female",gears.genderobj.Gender.get_default_female())
        gender_menu.add_item("Nonbinary",gears.genderobj.Gender.get_default_nonbinary())
        gender_menu.menu.set_item_by_position(random.choice((0,0,0,1,1,1,2)))
        self.pc.gender = gender_menu.menu.get_current_item().value

        age_gender_row.add_center(gender_menu)
        self.column_one.add_interior(age_gender_row)
        self.column_one.add_interior(pbge.widgets.LabelWidget(0,0,self.C1_WIDTH,16,"===========",justify=0))
        minus_plus_image = pbge.image.Image("sys_minus_plus.png",16,16)
        for s in gears.stats.PRIMARY_STATS:
            nu_row = pbge.widgets.RowWidget(0,0,self.C1_WIDTH,30)
            nu_row.add_left(pbge.widgets.LabelWidget(0,0,150,pbge.BIGFONT.get_linesize(),text=s.name,font=pbge.BIGFONT))
            nu_row.add_right(pbge.widgets.ButtonWidget(0,0,16,16,sprite=minus_plus_image,frame=0,data=s,on_click=self.stat_minus))
            nu_row.add_right(pbge.widgets.LabelWidget(0,0,32,pbge.BIGFONT.get_linesize(),text_fun=self.stat_display,data=s,font=pbge.BIGFONT,justify=0))
            nu_row.add_right(pbge.widgets.ButtonWidget(0,0,16,16,sprite=minus_plus_image,frame=1,data=s,on_click=self.stat_plus))
            self.column_one.add_interior(nu_row)
        self.column_one.add_interior(pbge.widgets.LabelWidget(0,0,self.C1_WIDTH,16,text_fun=self.stat_point_display,justify=0))
        random_reset_row = pbge.widgets.RowWidget(0,0,self.C1_WIDTH,30)
        random_reset_row.add_left(pbge.widgets.LabelWidget(0,0,100,pbge.SMALLFONT.get_linesize(),text="Random",font=pbge.SMALLFONT,on_click=self.stat_randomize,draw_border=True,justify=0))
        random_reset_row.add_right(pbge.widgets.LabelWidget(0,0,100,pbge.SMALLFONT.get_linesize(),text="Reset",font=pbge.SMALLFONT,on_click=self.stat_reset,draw_border=True,justify=0))
        self.column_one.add_interior(random_reset_row)

        self.column_one.add_interior(pbge.widgets.LabelWidget(0,0,self.C1_WIDTH,16,"===========",justify=0))
        self.column_one.add_interior(pbge.widgets.LabelWidget(0,0,self.C1_WIDTH,50,text_fun=self.skill_display))

        self.children.append(self.column_one)

        self.column_two = pbge.widgets.ColumnWidget(160,-200,self.C2_WIDTH,400,draw_border=True)
        self.column_two.add_interior(pbge.widgets.LabelWidget(0,0,self.C2_WIDTH,360,text_fun=self.biography_display,justify=-1,font=pbge.SMALLFONT))
        random_reset_row = pbge.widgets.RowWidget(0,0,self.C2_WIDTH,30)
        random_reset_row.add_left(pbge.widgets.LabelWidget(0,0,100,pbge.SMALLFONT.get_linesize(),text="Random",font=pbge.SMALLFONT,on_click=self.biography_randomize,draw_border=True,justify=0))
        random_reset_row.add_right(pbge.widgets.LabelWidget(0,0,100,pbge.SMALLFONT.get_linesize(),text="Choose",font=pbge.SMALLFONT,on_click=self.biography_choose,draw_border=True,justify=0))
        self.column_two.add_interior(random_reset_row)

        self.children.append(self.column_two)

        self.column_three = pbge.widgets.ColumnWidget(-375,100,self.C3_WIDTH,120,draw_border=False,padding=10)
        self.column_three.add_interior(pbge.widgets.LabelWidget(0,0,self.C3_WIDTH,16,text="Random Portait",justify=0,on_click=self.portrait_random,draw_border=True))
        self.column_three.add_interior(pbge.widgets.LabelWidget(0,0,self.C3_WIDTH,16,text="Edit Portait",justify=0,on_click=self.portrait_edit,draw_border=True))
        self.column_three.add_interior(pbge.widgets.LabelWidget(0,0,self.C3_WIDTH,16,text="Random Colors",justify=0,on_click=self.color_random,draw_border=True))
        self.column_three.add_interior(pbge.widgets.LabelWidget(0,0,self.C3_WIDTH,16,text="Edit Colors",justify=0,on_click=self.color_edit,draw_border=True))

        self.children.append(self.column_three)

        self.children.append(pbge.widgets.LabelWidget(160,210,self.C2_WIDTH,20,text="Save Character",justify=0,on_click=self.save_egg,draw_border=True,font=pbge.BIGFONT))
        self.children.append(pbge.widgets.LabelWidget(160,240,self.C2_WIDTH,20,text="Cancel",justify=0,on_click=self.cancel,draw_border=True,font=pbge.BIGFONT))

        self.portrait = self.pc.portrait_gen.build_portrait(self.pc)

    def set_age(self,new_age):
        self.pc.birth_year = self.year - new_age
    def set_gender(self,new_gender):
        self.pc.gender = new_gender
    def stat_display(self,wid):
        return str(self.pc.get_stat(wid.data) + self.bio_bonuses.get(wid.data,0))
    def stat_minus(self,wid,ev):
        if self.pc.statline[wid.data] > 5:
            self.pc.statline[wid.data] -= 1
            self.unspent_stat_points += 1
    def stat_plus(self,wid,ev):
        if self.pc.statline[wid.data] < 18 and self.unspent_stat_points > 0:
            self.pc.statline[wid.data] += 1
            self.unspent_stat_points -= 1
    def stat_point_display(self,wid):
        return "{} Stat Points".format(self.unspent_stat_points)
    def stat_randomize(self,wid,ev):
        if self.unspent_stat_points > 0:
            self.pc.roll_stats(self.unspent_stat_points,False)
            self.unspent_stat_points = 0
        else:
            self.pc.roll_stats(self.STAT_POINTS)
    def stat_reset(self,wid,ev):
        self.unspent_stat_points = self.STAT_POINTS
        for s in gears.stats.PRIMARY_STATS:
            self.pc.statline[s] = 5
            self.unspent_stat_points -= 5
    def skill_display(self,wid):
        skillz = [sk.name for sk in self.bio_bonuses.keys() if sk in gears.stats.NONCOMBAT_SKILLS]
        return 'Skills: {}'.format(', '.join(skillz or ["None"]))

    def biography_display(self,wid):
        return self.pc.bio
    def _reset_biography(self):
        self.bio_bonuses.clear()
        self.biogram.clear()
        self.pc.bio = ""
        self.pc.portrait_gen.color_channels = list(gears.color.CHARACTER_COLOR_CHANNELS)
    def biography_randomize(self,wid,ev):
        self._reset_biography()
        lifepath.generate_random_lifepath(self)

    def biography_choose(self,wid,ev):
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

    def portrait_edit(self,wid,ev):
        self.active = False
        PortraitEditorW.create_and_invoke(self)
        self.active = True

    def portrait_random(self,wid,ev):
        self.pc.portrait_gen.random_portrait(self.pc)
        self.portrait = self.pc.portrait_gen.build_portrait(self.pc,force_rebuild=True)

    def color_edit(self,wid,ev):
        self.active = False
        myui = cosplay.ColorEditor(self.pc.portrait_gen.build_portrait(self.pc,add_color=False),0,channel_filters=self.pc.portrait_gen.color_channels,colors=self.pc.colors)
        pbge.my_state.widgets.append(myui)
        myui.finished = False
        myui.children.append(pbge.widgets.LabelWidget(150,220,80,16,text="Done",justify=0,on_click=self.color_done,draw_border=True,data=myui))

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
        self.portrait = self.pc.portrait_gen.build_portrait(self.pc,force_rebuild=True)

        pbge.my_state.widgets.remove(myui)
        pygame.event.clear()
        self.active = True

    def color_done(self,wid,ev):
        wid.data.finished = True

    def color_random(self,wid,ev):
        self.pc.colors = [random.choice(gears.color.COLOR_LISTS[chan]) for chan in self.pc.portrait_gen.color_channels]
        self.portrait = self.pc.portrait_gen.build_portrait(self.pc,force_rebuild=True)

    def save_egg(self,wid,ev):
        if not pbge.my_state.widget_clicked:
            my_egg = gears.eggs.Egg(self.pc,credits=500000)
            self.pc.name = self.name_field.text
            if self.unspent_stat_points > 0:
                self.pc.roll_stats(self.unspent_stat_points,clear_first=False)
            for sk in gears.stats.COMBATANT_SKILLS:
                self.pc.statline[sk] = 4
            num_fives = 4
            for k,v in self.bio_bonuses.items():
                self.pc.statline[k] += v
                if k in gears.stats.NONCOMBAT_SKILLS:
                    self.pc.statline[k] += 3
                    num_fives -= 1
            if num_fives > 0:
                for sk in random.sample(gears.stats.COMBATANT_SKILLS,num_fives):
                    self.pc.statline[sk] += 1
            self.finished = True
            my_egg.save()

    def cancel(self,wid,ev):
        self.finished = True

    def render(self):
        self.portrait.render(self.portrait_zone.get_rect(),0)

    @classmethod
    def create_and_invoke(cls, redraw):
        # Run the UI. Return a DoInvocation action if an invocation
        # was chosen, or None if the invocation was cancelled.
        myui = cls()
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

