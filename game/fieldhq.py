import pbge
from pbge import widgets
import pygame
import gears

CENTER_COLUMN = pbge.frects.Frect(-50,-200,200,400)
RIGHT_COLUMN = pbge.frects.Frect(175,-200,200,400)
PORTRAIT_AREA = pbge.frects.Frect(-450, -300, 400, 600)

class CharaFHQIP(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.FullNameBlock, gears.info.ModuleStatusBlock, gears.info.PrimaryStatsBlock,gears.info.NonComSkillBlock)

class MechaFHQIP(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.FullNameBlock, gears.info.ModuleStatusBlock, gears.info.DescBlock)


class CharacterInfoWidget(widgets.Widget):
    def __init__(self,camp,pc,**kwargs):
        super(CharacterInfoWidget, self).__init__(0,0,0,0,**kwargs)
        self.camp = camp
        self.pc = pc
        self.portrait_image = pc.get_portrait()
        self.info = CharaFHQIP(model=pc,width=CENTER_COLUMN.w)

    def render(self):
        mydest = self.portrait_image.get_rect(0)
        mydest.midbottom = PORTRAIT_AREA.get_rect().midbottom
        self.portrait_image.render(mydest,0)
        mydest = CENTER_COLUMN.get_rect()
        self.info.render(mydest.x,mydest.y)

class MechaInfoWidget(widgets.Widget):
    def __init__(self,camp,pc,**kwargs):
        super(MechaInfoWidget, self).__init__(0,0,0,0,**kwargs)
        self.camp = camp
        self.pc = pc
        self.portrait_image = pc.get_portrait()
        self.info = MechaFHQIP(model=pc,width=CENTER_COLUMN.w)

    def render(self):
        mydest = self.portrait_image.get_rect(0)
        mydest.midbottom = PORTRAIT_AREA.get_rect().midbottom
        self.portrait_image.render(mydest,0)
        mydest = CENTER_COLUMN.get_rect()
        self.info.render(mydest.x,mydest.y)

class PartyMemberButton(widgets.Widget):
    def __init__(self,camp,pc,fhq,**kwargs):
        super(PartyMemberButton, self).__init__(0,0,RIGHT_COLUMN.w,72,**kwargs)
        self.camp = camp
        self.pc = pc
        self.fhq = fhq
        self.avatar_pic = pc.get_sprite()
        self.avatar_frame = pc.frame
    def render(self):
        mydest = self.get_rect().inflate(-8,-8)
        if self.pc is self.fhq.active_pc:
            widgets.widget_border_on.render(mydest)
        else:
            widgets.widget_border_off.render(mydest)
        self.avatar_pic.render(mydest,self.avatar_frame)
        mydest.x += 64
        mydest.w -= 64
        pbge.draw_text(pbge.MEDIUMFONT,self.pc.get_full_name(),mydest,color=pbge.WHITE)

class FieldHQ(widgets.Widget):
    # Three columns
    # To the left: the character portrait (if available)
    # In the center: the character info/action widgets
    # To the right: The list of characters/mecha in the party
    def __init__(self,camp):
        super(FieldHQ, self).__init__(0,0,0,0)

        self.up_button = widgets.ButtonWidget(0,0,RIGHT_COLUMN.w,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),off_frame=1)
        self.down_button = widgets.ButtonWidget(0,0,RIGHT_COLUMN.w,16,sprite=pbge.image.Image("sys_updownbuttons.png",128,16),frame=2,on_frame=2,off_frame=3)

        self.member_selector = widgets.ScrollColumnWidget(0,0,RIGHT_COLUMN.w,RIGHT_COLUMN.h-42,up_button = self.up_button,down_button=self.down_button)

        self.r_column = widgets.ColumnWidget(RIGHT_COLUMN.dx,RIGHT_COLUMN.dy,RIGHT_COLUMN.w,RIGHT_COLUMN.h)
        self.r_column.add_interior(self.up_button)
        self.r_column.add_interior(self.member_selector)
        self.r_column.add_interior(self.down_button)

        self.children.append(self.r_column)

        self.member_widgets = dict()

        for pc in camp.party:
            self.member_selector.add_interior(PartyMemberButton(camp,pc,fhq=self,on_click=self.click_member))
            if isinstance(pc,gears.base.Character):
                self.member_widgets[pc] = CharacterInfoWidget(camp,pc,active=False)
                self.children.append(self.member_widgets[pc])
            elif isinstance(pc,gears.base.Mecha):
                self.member_widgets[pc] = MechaInfoWidget(camp,pc,active=False)
                self.children.append(self.member_widgets[pc])

        self.camp = camp
        self.finished = False
        self.active_pc = camp.pc
        self.active_widget = self.member_widgets.get(camp.pc,None)
        if self.active_widget:
            self.active_widget.active = True

    def click_member(self,wid,ev):
        if self.active_widget:
            self.active_widget.active = False
        self.active_widget = self.member_widgets.get(wid.pc,None)
        self.active_pc = wid.pc
        if self.active_widget:
            self.active_widget.active = True

    def done_button(self,wid,ev):
        self.finished = True

    @classmethod
    def create_and_invoke(cls, camp):
        # Run the UI. Return a DoInvocation action if an invocation
        # was chosen, or None if the invocation was cancelled.
        myui = cls(camp)
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

        pbge.my_state.widgets.remove(myui)
