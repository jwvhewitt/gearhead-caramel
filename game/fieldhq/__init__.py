import pbge
from game.fieldhq.fhqinfo import CharaFHQIP, MechaFHQIP, AssignMechaIP, PetFHQIP, AssignPilotIP, create_item_fhq_ip
from pbge import widgets
import pygame
import gears
from game import cosplay
from . import backpack
from . import training
from . import fhqinfo
from . import pceditor


class AssignMechaDescObject(object):
    def __init__(self, camp):
        self.camp = camp
        self.infoz = dict()

    def __call__(self, menu_item):
        mydest = fhqinfo.UTIL_INFO.get_rect()
        if menu_item.value:
            if menu_item.value not in self.infoz:
                self.infoz[menu_item.value] = AssignMechaIP(model=menu_item.value, width=fhqinfo.UTIL_INFO.w,
                                                            camp=self.camp,
                                                            additional_info='\n Pilot: {} \n Damage: {}%'.format(
                                                                str(menu_item.value.pilot),
                                                                menu_item.value.get_total_damage_status()))
            self.infoz[menu_item.value].render(mydest.x, mydest.y)


class AssignPilotDescObject(object):
    def __init__(self, camp):
        self.camp = camp
        self.infoz = dict()

    def __call__(self, menu_item):
        mydest = fhqinfo.UTIL_INFO.get_rect()
        if menu_item.value:
            if menu_item.value not in self.infoz:
                self.infoz[menu_item.value] = AssignPilotIP(model=menu_item.value, width=fhqinfo.UTIL_INFO.w,
                                                            camp=self.camp)
            self.infoz[menu_item.value].render(mydest.x, mydest.y)


class InfoDisplayWidget(widgets.Widget):
    # Hand this widget an info panel, and it'll display it. That's all it does.
    def __init__(self, info_display: gears.info.InfoPanel):
        super().__init__(
            fhqinfo.CENTER_COLUMN.dx, fhqinfo.CENTER_COLUMN.dy, fhqinfo.CENTER_COLUMN.w, fhqinfo.CENTER_COLUMN.h
        )
        self.info_display = info_display

    def render(self, flash=False):
        myrect = self.get_rect()
        self.info_display.render(myrect.x, myrect.y)


class MeritBadgeDisplayWidget(widgets.ColumnWidget):
    def __init__(self, pc: gears.base.Character, **kwargs):
        super().__init__(
            fhqinfo.CENTER_COLUMN.dx, fhqinfo.CENTER_COLUMN.dy, fhqinfo.CENTER_COLUMN.w, fhqinfo.CENTER_COLUMN.h,
            border=pbge.default_border, draw_border=True, center_interior=True, **kwargs
        )
        self.up_button = widgets.ButtonWidget(0, 0, 128, 16,
                                              sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), off_frame=1)
        self.down_button = widgets.ButtonWidget(0, 0, 128, 16,
                                                sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), frame=2,
                                                on_frame=2, off_frame=3)

        self.display_area = widgets.ScrollColumnWidget(
            0, 0, fhqinfo.CENTER_COLUMN.w, fhqinfo.CENTER_COLUMN.h - 42,
            up_button=self.up_button, down_button=self.down_button
        )
        self.add_interior(self.up_button)
        self.add_interior(self.display_area)
        self.add_interior(self.down_button)

        for badge in pc.badges:
            self.display_area.add_interior(widgets.LabelWidget(
                0,0,fhqinfo.CENTER_COLUMN.w,0,str(badge), color=pbge.TEXT_COLOR, font=pbge.BIGFONT
            ))

            self.display_area.add_interior(widgets.LabelWidget(
                0,0,fhqinfo.CENTER_COLUMN.w,0,badge.desc, color=pbge.INFO_GREEN, font=pbge.MEDIUMFONT
            ))

            self.display_area.add_interior(widgets.LabelWidget(
                0,0,fhqinfo.CENTER_COLUMN.w,0,badge.get_effect_desc(), color=pbge.INFO_GREEN, font=pbge.ITALICFONT
            ))


class CharacterCenterColumnWidget(widgets.RowWidget):
    def __init__(self, camp, pc: gears.base.Character, **kwargs):
        super().__init__(fhqinfo.CENTER_COLUMN.dx, fhqinfo.CENTER_COLUMN.dy - 35, fhqinfo.CENTER_COLUMN.w,
                         20, padding=10, **kwargs)

        self.panels = list()

        self.stats_panel = InfoDisplayWidget(CharaFHQIP(
            model=pc, width=fhqinfo.CENTER_COLUMN.w, font=pbge.SMALLFONT, camp=camp
        ))
        self.children.append(self.stats_panel)
        self.panels.append(self.stats_panel)

        if pc.bio or pc.badges:
            self.add_center(widgets.LabelWidget(
                0, 0, 50, 0, "Stats", draw_border=True, border=widgets.widget_border_on, data=self.stats_panel,
                on_click=self._switch_panel, justify=0
            ))

        if pc.bio:
            self.bio_panel = widgets.LabelWidget(
                fhqinfo.CENTER_COLUMN.dx, fhqinfo.CENTER_COLUMN.dy, fhqinfo.CENTER_COLUMN.w, 0,
                pc.bio, font=pbge.MEDIUMFONT, draw_border=True, border=pbge.default_border, active=False
            )
            self.children.append(self.bio_panel)
            self.panels.append(self.bio_panel)

            self.add_center(widgets.LabelWidget(
                0, 0, 50, 0, "Bio", draw_border=True, border=widgets.widget_border_off, data=self.bio_panel,
                on_click=self._switch_panel, justify=0
            ))

        if pc.badges:
            self.badges_panel = MeritBadgeDisplayWidget(pc, active=False)
            self.children.append(self.badges_panel)
            self.panels.append(self.badges_panel)

            self.add_center(widgets.LabelWidget(
                0, 0, 50, 0, "Badges", draw_border=True, border=widgets.widget_border_off, data=self.badges_panel,
                on_click=self._switch_panel, justify=0
            ))

    def _switch_panel(self, wid, ev):
        for ccc in self.panels:
            if ccc is wid.data:
                ccc.active = True
            else:
                ccc.active = False
        for butt in self._center_widgets:
            if butt is wid:
                butt.border = widgets.widget_border_on
            else:
                butt.border = widgets.widget_border_off


class CharacterInfoWidget(widgets.Widget):
    def __init__(self, camp, pc, fhq, **kwargs):
        super().__init__(0, 0, 0, 0, **kwargs)
        self.camp = camp
        self.pc = pc
        self.portrait_view = gears.portraits.PortraitView(pc.get_portrait())
        self.column = widgets.ColumnWidget(fhqinfo.LEFT_COLUMN.dx, fhqinfo.LEFT_COLUMN.dy, fhqinfo.LEFT_COLUMN.w,
                                           fhqinfo.LEFT_COLUMN.h, padding=10)
        self.children.append(self.column)
        self.column.add_interior(
            widgets.LabelWidget(0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Inventory", justify=0, draw_border=True,
                                on_click=self.open_backpack))
        self.column.add_interior(
            widgets.LabelWidget(0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Do Training", justify=0, draw_border=True,
                                on_click=self.open_training))
        self.column.add_interior(
            widgets.LabelWidget(0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Assign Mecha", justify=0, draw_border=True,
                                on_click=self.assign_mecha))
        self.column.add_interior(
            widgets.LabelWidget(0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Change Colors", justify=0, draw_border=True,
                                on_click=self.change_colors))
        if pc.relationship and pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
            self.column.add_interior(
                widgets.LabelWidget(0, 0, fhqinfo.LEFT_COLUMN.w, 16, text="Jump to Next Dev", justify=0,
                                    draw_border=True, on_click=self.jump_plot))
        if pc is camp.pc:
            self.column.add_interior(
                widgets.LabelWidget(0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Edit Character", justify=0, draw_border=True,
                                    on_click=self.edit_pc))
        self.fhq = fhq
        self.children.append(CharacterCenterColumnWidget(camp, pc))

        self.sl = pbge.StretchyLayer()

    def edit_pc(self, wid, ev):
        self.fhq.active = False
        pceditor.PCEditorWidget.create_and_invoke(self.camp, self.pc)
        self.fhq.active = True

    def jump_plot(self, wid, ev):
        while not self.pc.relationship.can_do_development():
            self.pc.relationship.missions_together += 10

    def open_training(self, wid, ev):
        self.fhq.active = False
        my_trainer = training.TrainingMenu(self.camp, self.pc)
        my_trainer()
        self.fhq.update_party()
        self.fhq.active = True

    def open_backpack(self, wid, ev):
        self.fhq.active = False
        myui = backpack.BackpackWidget(self.camp, self.pc)
        pbge.my_state.widgets.append(myui)
        myui.finished = False
        myui.children.append(
            pbge.widgets.LabelWidget(150, 220, 80, 0, text="Done", justify=0, on_click=self.bp_done,
                                     draw_border=True, data=myui))

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
        pygame.event.clear()
        self.fhq.update_party()
        self.fhq.active = True

    def bp_done(self, wid, ev):
        wid.data.finished = True

    def assign_mecha(self, wid, ev):
        self.fhq.active = False

        mymenu = pbge.rpgmenu.Menu(fhqinfo.UTIL_MENU.dx, fhqinfo.UTIL_MENU.dy, fhqinfo.UTIL_MENU.w, fhqinfo.UTIL_MENU.h,
                                   font=pbge.MEDIUMFONT, predraw=self.draw_portrait)
        for mek in self.camp.party:
            if isinstance(mek, gears.base.Mecha) and mek.is_not_destroyed() and (
                    not hasattr(mek, "owner") or mek.owner is self.pc):
                mymenu.add_item(mek.get_full_name(), mek)
        mymenu.descobj = AssignMechaDescObject(self.camp)
        mek = mymenu.query()

        self.camp.assign_pilot_to_mecha(self.pc, mek)

        if mek:
            self.fhq.update_party()
            pbge.my_state.view.regenerate_avatars([mek, ])

        self.fhq.active = True

    def change_colors(self, wid, ev):
        self.fhq.active = False
        if self.pc.portrait_gen:
            cchan = self.pc.portrait_gen.color_channels
        else:
            cchan = gears.color.CHARACTER_COLOR_CHANNELS
        myui = cosplay.ColorEditor(self.pc.get_portrait(add_color=False), 0,
                                   channel_filters=cchan, colors=self.pc.colors)
        pbge.my_state.widgets.append(myui)
        myui.finished = False
        myui.children.append(
            pbge.widgets.LabelWidget(150, 220, 80, 0, text="Done", justify=0, on_click=self.color_done,
                                     draw_border=True, data=myui))

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
        self.portrait_view.portrait = self.pc.get_portrait(self.pc, force_rebuild=True)

        pbge.my_state.widgets.remove(myui)
        pygame.event.clear()
        self.fhq.update_party()
        self.fhq.active = True
        pbge.my_state.view.regenerate_avatars([self.pc, ])

    def color_done(self, wid, ev):
        wid.data.finished = True

    def draw_portrait(self, include_background=True):
        if include_background:
            pbge.my_state.view()
        self.portrait_view.render()

    def render(self, flash=False):
        self.draw_portrait(False)


class MechaInfoWidget(widgets.Widget):
    def __init__(self, camp, pc, fhq, **kwargs):
        super(MechaInfoWidget, self).__init__(0, 0, 0, 0, **kwargs)
        self.camp = camp
        self.pc = pc
        self.portrait_view = gears.portraits.PortraitView(pc.get_portrait())
        self.info = MechaFHQIP(model=pc, width=fhqinfo.CENTER_COLUMN.w, camp=camp, font=pbge.SMALLFONT)
        self.column = widgets.ColumnWidget(fhqinfo.LEFT_COLUMN.dx, fhqinfo.LEFT_COLUMN.dy, fhqinfo.LEFT_COLUMN.w,
                                           fhqinfo.LEFT_COLUMN.h, padding=10)
        self.children.append(self.column)
        if not hasattr(pc, "owner") or not pc.owner:
            self.column.add_interior(
                widgets.LabelWidget(0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Inventory", justify=0, draw_border=True,
                                    on_click=self.open_backpack))
        self.column.add_interior(
            widgets.LabelWidget(0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Assign Pilot", justify=0, draw_border=True,
                                on_click=self.assign_pilot))
        self.column.add_interior(
            widgets.LabelWidget(0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Change Colors", justify=0, draw_border=True,
                                on_click=self.change_colors))
        self.fhq = fhq

    def draw_portrait(self, include_background=True):
        if include_background:
            pbge.my_state.view()
        self.portrait_view.render()

    def render(self, flash=False):
        self.draw_portrait(False)
        mydest = fhqinfo.CENTER_COLUMN.get_rect()
        self.info.render(mydest.x, mydest.y)

    def assign_pilot(self, wid, ev):
        self.fhq.active = False

        mymenu = pbge.rpgmenu.Menu(fhqinfo.UTIL_MENU.dx, fhqinfo.UTIL_MENU.dy, fhqinfo.UTIL_MENU.w, fhqinfo.UTIL_MENU.h,
                                   font=pbge.MEDIUMFONT, predraw=self.draw_portrait)
        for plr in self.camp.party:
            if isinstance(plr, gears.base.Character) and plr.is_not_destroyed() and (
                    not hasattr(self.pc, "owner") or self.pc.owner is plr):
                mymenu.add_item(plr.get_full_name(), plr)
        mymenu.descobj = AssignPilotDescObject(self.camp)
        pilot = mymenu.query()

        self.camp.assign_pilot_to_mecha(pilot, self.pc)
        self.info.update()

        self.fhq.update_party()
        pbge.my_state.view.regenerate_avatars([self.pc, ])

        self.fhq.active = True

    def open_backpack(self, wid, ev):
        self.fhq.active = False
        myui = backpack.BackpackWidget(self.camp, self.pc)
        pbge.my_state.widgets.append(myui)
        myui.finished = False
        myui.children.append(
            pbge.widgets.LabelWidget(150, 220, 80, 0, text="Done", justify=0, on_click=self.bp_done,
                                     draw_border=True, data=myui))

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
        pygame.event.clear()
        self.info.update()
        self.fhq.update_party()
        self.fhq.active = True

    def bp_done(self, wid, ev):
        wid.data.finished = True

    def change_colors(self, wid, ev):
        self.fhq.active = False
        myui = cosplay.ColorEditor(self.pc.get_portrait(add_color=False), 0,
                                   channel_filters=gears.color.MECHA_COLOR_CHANNELS, colors=self.pc.colors)
        pbge.my_state.widgets.append(myui)
        myui.finished = False
        myui.children.append(
            pbge.widgets.LabelWidget(150, 220, 80, 0, text="Done", justify=0, on_click=self.color_done,
                                     draw_border=True, data=myui))

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
        self.portrait_view.portrait = self.pc.get_portrait(self.pc, force_rebuild=True)

        pbge.my_state.widgets.remove(myui)
        pygame.event.clear()
        self.fhq.update_party()
        self.fhq.active = True
        pbge.my_state.view.regenerate_avatars([self.pc, ])

        if isinstance(self.pc, gears.base.Mecha) and self.pc.pilot:
            self.pc.pilot.mecha_colors = self.pc.colors

    def color_done(self, wid, ev):
        wid.data.finished = True


class PetInfoWidget(widgets.Widget):
    def __init__(self, camp, pc: gears.base.Monster, fhq, **kwargs):
        super().__init__(0, 0, 0, 0, **kwargs)
        self.camp = camp
        self.pc = pc
        self.info = PetFHQIP(model=pc, width=fhqinfo.CENTER_COLUMN.w, camp=camp, font=pbge.SMALLFONT)
        self.column = widgets.ColumnWidget(fhqinfo.LEFT_COLUMN.dx, fhqinfo.LEFT_COLUMN.dy, fhqinfo.LEFT_COLUMN.w,
                                           fhqinfo.LEFT_COLUMN.h, padding=10)
        self.children.append(self.column)

        self.column.add_interior(widgets.LabelWidget(
            0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Change Name", justify=0, draw_border=True,
            on_click=self._change_name
        ))

        if self.pc.pet_data.active:
            self.column.add_interior(widgets.LabelWidget(
                0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Send Home", justify=0, draw_border=True,
                on_click=self.leave_behind
            ))
        elif gears.tags.SCENE_PUBLIC in self.camp.scene.attributes:
            self.column.add_interior(widgets.LabelWidget(
                0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Bring Along", justify=0, draw_border=True,
                on_click=self.bring_along
            ))

        self.column.add_interior(widgets.LabelWidget(
            0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Dismiss {}".format(self.pc), justify=0, draw_border=True,
            on_click=self._dismiss
        ))

        self.fhq = fhq

    def render(self, flash=False):
        mydest = fhqinfo.CENTER_COLUMN.get_rect()
        self.info.render(mydest.x, mydest.y)

    def _dismiss(self, wid, ev):
        self.fhq.active = False

        mymenu = pbge.rpgmenu.AlertMenu("Are you sure you want to dismiss {} permanently?".format(self.pc))
        mymenu.add_item("Yes, dismiss {}.".format(self.pc), True)
        mymenu.add_item("No, I don't.".format(self.pc), False)

        if mymenu.query():
            self.camp.deactivate_pet(self.pc)
            self.camp.party.remove(self.pc)
            self.fhq.update_party()

        self.fhq.active = True

    def leave_behind(self, wid, ev):
        self.camp.deactivate_pet(self.pc)
        self.fhq.update_party()

    def bring_along(self, wid, ev):
        self.camp.activate_pet(self.pc)
        self.fhq.update_party()

    def _change_name(self, wid, ev):
        self.fhq.active = False
        myui = widgets.ColumnWidget(-100, -70, 200, 0, draw_border=True, center_interior=True, padding=16)
        myui.add_interior(pbge.widgets.LabelWidget(0, 0, 0, 0, "Change Name", font=pbge.BIGFONT))
        myui.add_interior(pbge.widgets.TextEntryWidget(
            0, 0, 180, 24, text=self.pc.name, on_change=self._set_name
        ))
        myui.add_interior(pbge.widgets.LabelWidget(
            0, 0, 0, 0, "Done", justify=0, on_click=self._rename_done, draw_border=True
        ))

        pbge.my_state.widgets.append(myui)
        self.rename_finished = False

        while not self.rename_finished and not pbge.my_state.got_quit:
            ev = pbge.wait_event()
            if ev.type == pbge.TIMEREVENT:
                pbge.my_state.view()
                pbge.my_state.do_flip()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.rename_finished = True
                elif ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
                    self.rename_finished = True

        pbge.my_state.widgets.remove(myui)
        pygame.event.clear()
        self.info.update()
        self.fhq.update_party()
        self.fhq.active = True

    def _set_name(self, wid, ev):
        self.pc.name = wid.text

    def _rename_done(self, wid, ev):
        self.rename_finished = True


class ItemInfoWidget(widgets.Widget):
    def __init__(self, camp, pc, fhq, **kwargs):
        super().__init__(0, 0, 0, 0, **kwargs)
        self.camp = camp
        self.pc = pc
        self.info = create_item_fhq_ip(model=pc, width=fhqinfo.CENTER_COLUMN.w, camp=camp, font=pbge.SMALLFONT)
        self.column = widgets.ColumnWidget(fhqinfo.LEFT_COLUMN.dx, fhqinfo.LEFT_COLUMN.dy, fhqinfo.LEFT_COLUMN.w,
                                           fhqinfo.LEFT_COLUMN.h, padding=10)
        self.children.append(self.column)
        self.column.add_interior(
            widgets.LabelWidget(0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Give Item", justify=0, draw_border=True,
                                on_click=self.give_item))
        self.fhq = fhq

    def render(self, flash=False):
        mydest = fhqinfo.CENTER_COLUMN.get_rect()
        self.info.render(mydest.x, mydest.y)

    def give_item(self, wid, ev):
        self.fhq.active = False

        mymenu = pbge.rpgmenu.Menu(fhqinfo.UTIL_MENU.dx, fhqinfo.UTIL_MENU.dy, fhqinfo.UTIL_MENU.w, fhqinfo.UTIL_MENU.h,
                                   font=pbge.MEDIUMFONT)
        for plr in self.camp.party:
            if plr.can_equip(self.pc) and not (hasattr(plr, "owner") and plr.owner):
                mymenu.add_item(plr.get_full_name(), plr)
        pilot = mymenu.query()

        if pilot:
            self.camp.party.remove(self.pc)
            pilot.inv_com.append(self.pc)

        self.info.update()
        self.fhq.update_party()
        self.fhq.active = True


class PartyMemberButton(widgets.Widget):
    def __init__(self, camp, pc, fhq, **kwargs):
        super().__init__(0, 0, fhqinfo.RIGHT_COLUMN.w, 72, **kwargs)
        self.camp = camp
        self.pc = pc
        self.fhq = fhq
        self.avatar_pic = pc.get_sprite()
        self.avatar_frame = pc.frame
        label = widgets.LabelWidget(
            64, 4, fhqinfo.RIGHT_COLUMN.w-72, 64, text_fun=self._name_fun, color=pbge.WHITE, parent=self,
            border=None, font=pbge.MEDIUMFONT, alt_smaller_fonts=(pbge.SMALLFONT, pbge.TINYFONT), anchor=pbge.frects.ANCHOR_UPPERLEFT,
            on_click=self._click_name
        )
        self.children.append(label)

    def render(self, flash=False):
        mydest = self.get_rect().inflate(-8, -8)
        if self.fhq.active_pc is self.pc:
            widgets.widget_border_on.render(mydest)
        else:
            widgets.widget_border_off.render(mydest)
        self.avatar_pic.render(mydest, self.avatar_frame)

    def _name_fun(self, *args):
        return self.pc.get_full_name()

    def _click_name(self, wid, ev):
        if self.on_click:
            self.on_click(self, ev)



class FieldHQ(widgets.Widget):
    # Three columns
    # To the left: the character portrait (if available)
    # In the center: the character info/action widgets
    # To the right: The list of characters/mecha in the party
    def __init__(self, camp):
        self._active_info = None
        super(FieldHQ, self).__init__(0, 0, 0, 0)

        self.up_button = widgets.ButtonWidget(0, 0, fhqinfo.RIGHT_COLUMN.w, 16,
                                              sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), off_frame=1)
        self.down_button = widgets.ButtonWidget(0, 0, fhqinfo.RIGHT_COLUMN.w, 16,
                                                sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), frame=2,
                                                on_frame=2, off_frame=3)

        self.member_selector = widgets.ScrollColumnWidget(0, 0, fhqinfo.RIGHT_COLUMN.w, fhqinfo.RIGHT_COLUMN.h - 42,
                                                          up_button=self.up_button, down_button=self.down_button,
                                                          autoclick=True, focus_locked=True)

        self.r_column = widgets.ColumnWidget(fhqinfo.RIGHT_COLUMN.dx, fhqinfo.RIGHT_COLUMN.dy, fhqinfo.RIGHT_COLUMN.w,
                                             fhqinfo.RIGHT_COLUMN.h)
        self.r_column.add_interior(self.up_button)
        self.r_column.add_interior(self.member_selector)
        self.r_column.add_interior(self.down_button)
        self.children.append(self.r_column)
        self.member_widgets = dict()
        self.camp = camp
        self.active_pc = camp.pc
        self.update_party()
        self.finished = False

        self.active_info = camp.pc

    def _set_active_info(self, pc):
        if self._active_info:
            self._active_info.active = False
        self.active_pc = pc
        self._active_info = self.member_widgets.get(pc, None)
        if self._active_info:
            self._active_info.active = True
        else:
            self._active_info = self.member_widgets.get(self.camp.pc, None)
            self.active_pc = self.camp.pc

    def _get_active_info(self):
        return self._active_info

    active_info = property(_get_active_info, _set_active_info)

    def update_party(self):
        return_to = self.active_pc
        self.member_selector.clear()
        for v in self.member_widgets.values():
            self.children.remove(v)
        self.member_widgets.clear()
        for pc in self.camp.party:
            self.member_selector.add_interior(PartyMemberButton(self.camp, pc, fhq=self, on_click=self.click_member))
            if isinstance(pc, gears.base.Character):
                self.member_widgets[pc] = CharacterInfoWidget(self.camp, pc, self, active=False)
                self.children.append(self.member_widgets[pc])
            elif isinstance(pc, gears.base.Mecha):
                self.member_widgets[pc] = MechaInfoWidget(self.camp, pc, self, active=False)
                self.children.append(self.member_widgets[pc])
            elif isinstance(pc, gears.base.Monster):
                self.member_widgets[pc] = PetInfoWidget(self.camp, pc, self, active=False)
                self.children.append(self.member_widgets[pc])
            else:
                self.member_widgets[pc] = ItemInfoWidget(self.camp, pc, self, active=False)
                self.children.append(self.member_widgets[pc])
        self.member_selector.sort(key=self._get_sort_order)
        self.active_info = return_to
        
    def _get_sort_order(self,  wid):
        pc = wid.pc
        if pc is self.camp.pc:
            return (0,  str(pc))
        elif isinstance(pc,  gears.base.Character):
            return (100,  str(pc))
        elif isinstance(pc,  gears.base.Being):
            return (200,  str(pc))
        elif isinstance(pc,  gears.base.Mecha) and pc.pilot:
            if pc.pilot is self.camp.pc:
                return (300,  str(pc.pilot))
            else:
                return (400,  str(pc.pilot))
        else:
            return (500,  str(pc))

    def click_member(self, wid, ev):
        # self.active_pc = wid.pc
        self.active_info = wid.pc

    def done_button(self, wid, ev):
        if not pbge.my_state.widget_clicked:
            self.finished = True

    @classmethod
    def create_and_invoke(cls, camp):
        # Run the UI. Return a DoInvocation action if an invocation
        # was chosen, or None if the invocation was cancelled.
        myui = cls(camp)
        pbge.my_state.widgets.append(myui)
        myui.children.append(pbge.widgets.LabelWidget(fhqinfo.RIGHT_COLUMN.dx + 64,
                                                      fhqinfo.RIGHT_COLUMN.dy + fhqinfo.RIGHT_COLUMN.h + 20, 80, 0,
                                                      text="Done", justify=0, on_click=myui.done_button,
                                                      draw_border=True))

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
