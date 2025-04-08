from . import fhqinfo
import pbge
import gears


class TrainingMenu(object):
    def __init__(self,camp,pc):
        self.camp = camp
        self.active_pc = pc
        # The "z" instead of "s" below implies two things.
        # First, it differentiates the portraitz dict from the portraits unit.
        # Second, it shows I remember the 1990z. Totally radical with attitude.
        self.infoz = dict()
        self.portraitz = dict()
        self.portrait_view = gears.portraits.PortraitView(None)

    def _predraw(self):
        pbge.my_state.view()
        if self.active_pc not in self.infoz:
            self.infoz[self.active_pc] = fhqinfo.CharaFHQIP(model=self.active_pc, width=fhqinfo.CENTER_COLUMN.w, font=pbge.SMALLFONT, camp=self.camp)
        mydest = fhqinfo.CENTER_COLUMN.get_rect()
        self.infoz[self.active_pc].render(mydest.x,mydest.y)

        if self.active_pc not in self.portraitz:
            self.portraitz[self.active_pc] = self.active_pc.get_portrait()
        self.portrait_view.portrait = self.portraitz[self.active_pc]
        self.portrait_view.render()

    def _get_standard_desc_box(self,mymenu):
        return pbge.rpgmenu.DescBox(mymenu,fhqinfo.RIGHT_INFO.dx,fhqinfo.RIGHT_INFO.dy,fhqinfo.RIGHT_INFO.w,fhqinfo.RIGHT_INFO.h,font=pbge.BIGFONT)

    def _get_menu(self):
        mymenu = pbge.rpgmenu.Menu(fhqinfo.RIGHT_MENU.dx,fhqinfo.RIGHT_MENU.dy,fhqinfo.RIGHT_MENU.w,fhqinfo.RIGHT_MENU.h,predraw=self._predraw)
        return mymenu

    def _get_free_xp(self):
        return self.active_pc.experience[self.active_pc.TOTAL_XP] - self.active_pc.experience[self.active_pc.SPENT_XP]

    def _spend_xp(self,amount):
        self.active_pc.experience[self.active_pc.SPENT_XP] += amount

    def __call__(self):
        choice = True
        while choice:
            mymenu = self._get_menu()
            mymenu.descobj = self._get_standard_desc_box(mymenu)
            for skill,value in self.active_pc.statline.items():
                if issubclass(skill,gears.stats.Skill):
                    mymenu.add_item('{} {:+} ({}XP)'.format(skill.name,value,skill.improvement_cost(self.active_pc,value)),skill,skill.desc)
            mymenu.sort()
            mymenu.add_item('[exit]',False,"")
            mymenu.set_item_by_value(choice)

            choice = mymenu.query()
            if choice:
                if choice.improvement_cost(self.active_pc,self.active_pc.statline[choice]) <= self._get_free_xp():
                    self._spend_xp(choice.improvement_cost(self.active_pc,self.active_pc.statline[choice]))
                    self.active_pc.statline[choice] += 1
                    self.infoz[self.active_pc].update()
