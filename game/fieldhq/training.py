from . import fhqinfo
import pbge
import gears


class TrainingMenu(pbge.widgetmenu.MenuWidget):
    ACTIVATE_IMMEDIATELY = True
    def __init__(self,camp,pc):
        super().__init__(
            fhqinfo.RIGHT_MENU.dx,fhqinfo.RIGHT_MENU.dy,fhqinfo.RIGHT_MENU.w,fhqinfo.RIGHT_MENU.h,
            on_escape=self._close_menu
        )
        self.camp = camp
        self.active_pc = pc
        # The "z" instead of "s" below implies two things.
        # First, it differentiates the portraitz dict from the portraits unit.
        # Second, it shows I remember the 1990z. Totally radical with attitude.
        self.infoz = dict()
        self.portraitz = dict()
        self.portrait_view = gears.portraits.PortraitView(None)

        self.children.append(pbge.widgetmenu.DescBoxWidget(
            fhqinfo.RIGHT_INFO.dx,fhqinfo.RIGHT_INFO.dy,fhqinfo.RIGHT_INFO.w,fhqinfo.RIGHT_INFO.h,
            font=pbge.BIGFONT, menu=self
        ))

        self._refresh_menu()

    def _refresh_menu(self):
        for skill in self.active_pc.statline.keys():
            if issubclass(skill,gears.stats.Skill) and self.active_pc.statline[skill] > 0:
                _=self.add_item(
                    self._menu_text_fun(skill), self._improve_skill, 
                    data=skill, desc=skill.desc
                )
        self.sort()
        _=self.add_item('[exit]', self._close_menu)

    def _close_menu(self, _wid, _ev):
        self.pop()

    def _menu_text_fun(self, skill):
        value = self.active_pc.statline.get(skill)
        return '{} {:+} ({}XP)'.format(skill.name,value,skill.improvement_cost(self.active_pc,value))

    def _improve_skill(self, wid, _ev):
        choice = wid.data
        if choice.improvement_cost(self.active_pc,self.active_pc.statline[choice]) <= self._get_free_xp():
            self._spend_xp(choice.improvement_cost(self.active_pc,self.active_pc.statline[choice]))
            self.active_pc.statline[choice] += 1
            self.infoz[self.active_pc].update()
            wid.text = self._menu_text_fun(choice)

    def _render(self, delta):
        if self.active_pc not in self.portraitz:
            self.portraitz[self.active_pc] = self.active_pc.get_portrait()
        self.portrait_view.portrait = self.portraitz[self.active_pc]
        self.portrait_view.render()

        if self.active_pc not in self.infoz:
            self.infoz[self.active_pc] = fhqinfo.CharaFHQIP(model=self.active_pc, width=fhqinfo.CENTER_COLUMN.w, font=pbge.SMALLFONT, camp=self.camp)
        mydest = fhqinfo.CENTER_COLUMN.get_rect()
        self.infoz[self.active_pc].render(mydest.x,mydest.y)

        super()._render(delta)

    def _get_free_xp(self):
        return self.active_pc.experience[self.active_pc.TOTAL_XP] - self.active_pc.experience[self.active_pc.SPENT_XP]

    def _spend_xp(self,amount):
        self.active_pc.experience[self.active_pc.SPENT_XP] += amount

