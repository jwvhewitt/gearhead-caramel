import lifepath
import pbge
import pygame
import gears


class CharacterGenerator(object):
    def __init__(self,redraw):
        self.redraw = redraw

        self.pc = gears.base.Character(name="New Character")
        self.biogram = dict()

        # Record the character generator zones.
        self.title_zone = pbge.frects.Frect(-200,-280,400,20)
        self.charsheet_zone = pbge.frects.Frect(-360,-230,350,460)
        self.info_zone = pbge.frects.Frect(20,-230,340,180)
        self.menu_zone = pbge.frects.Frect(20, -20, 340, 200)
        self.points_zone = pbge.frects.Frect(20,210,340,20)
        self.instructions_zone = pbge.frects.Frect(-200,260,400,20)

        self.cancelled = False

        self.title = ''
        self.info = None

    def render(self):
        self.redraw()
        pbge.default_border.render(self.title_zone.get_rect())
        pbge.default_border.render(self.charsheet_zone.get_rect())
        pbge.default_border.render(self.info_zone.get_rect())
        pbge.default_border.render(self.menu_zone.get_rect())
        pbge.default_border.render(self.points_zone.get_rect())
        pbge.default_border.render(self.instructions_zone.get_rect())
        if self.title:
            pbge.draw_text(pbge.BIGFONT,self.title,self.title_zone.get_rect(),pbge.WHITE,justify=0)
        if self.info:
            myrect = self.charsheet_zone.get_rect()
            self.info.render(myrect.x,myrect.y)

    def create_menu(self):
        mymenu= pbge.rpgmenu.Menu(self.menu_zone.dx, self.menu_zone.dy, self.menu_zone.w, self.menu_zone.h, border=None,
                          predraw=self.render, font=pbge.BIGFONT)
        mymenu.add_descbox(self.info_zone.dx,self.info_zone.dy,self.info_zone.w,self.info_zone.h)
        return mymenu

    def choose_lifepath(self):
        self.info = lifepath.LifePathStatusPanel(model=self.pc,width=self.charsheet_zone.w,draw_border=False)

        self.title = "Where is your character from?"
        choices = lifepath.STARTING_CHOICES
        while choices and not self.cancelled:
            mymenu =self.create_menu()
            for c in choices:
                mymenu.add_item(c.name,c,c.desc)

            mychoice = mymenu.query()
            if mychoice:
                for c in mychoice.choices:
                    self.title = c.prompt
                    mymenu = self.create_menu()
                    for c2 in c.options:
                        mymenu.add_item(c2.name,c2,c2.desc)
                    myop = mymenu.query()
                self.title = mychoice.next_prompt
                choices = mychoice.next
            else:
                self.cancelled = True

        self.info = None

    @classmethod
    def create_and_invoke(cls, redraw):
        # Run the UI. Return a DoInvocation action if an invocation
        # was chosen, or None if the invocation was cancelled.
        myui = cls(redraw)
        myui.choose_lifepath()

        keepgoing = True
        while keepgoing:
            ev = pbge.wait_event()
            if ev.type == pbge.TIMEREVENT:
                myui.render()
                pbge.my_state.do_flip()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    keepgoing = False


