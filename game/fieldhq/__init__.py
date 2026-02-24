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

WTAG_FIELDHQ = "WTAG_FIELDHQ"

class AssignMechaDescWidget(pbge.widgets.Widget):
    def __init__(self, camp, menu: pbge.widgetmenu.MenuWidget):
        super().__init__(0,0,0,0)
        self.camp = camp
        self.menu = menu
        self.infoz = dict()

    def _render(self, _delta):
        mymek = self.menu.current_data
        mydest = fhqinfo.UTIL_INFO.get_rect()
        if mymek:
            if mymek not in self.infoz:
                self.infoz[mymek] = AssignMechaIP(model=mymek, width=fhqinfo.UTIL_INFO.w,
                                                            camp=self.camp,
                                                            additional_info='\n Pilot: {} \n Damage: {}%'.format(
                                                                str(mymek.pilot),
                                                                mymek.get_total_damage_status()))
            self.infoz[mymek].render(mydest.x, mydest.y)
        super()._render(_delta)


class AssignPilotDescWidget(pbge.widgets.Widget):
    def __init__(self, camp, menu: pbge.widgetmenu.MenuWidget):
        super().__init__(0,0,0,0)
        self.camp = camp
        self.menu = menu
        self.infoz = dict()

    def _render(self, _delta):
        mymek = self.menu.current_data
        mydest = fhqinfo.UTIL_INFO.get_rect()
        if mymek:
            if mymek not in self.infoz:
                self.infoz[mymek] = AssignPilotIP(model=mymek, width=fhqinfo.UTIL_INFO.w,
                                                            camp=self.camp)
            self.infoz[mymek].render(mydest.x, mydest.y)


class NameChangeWidget(widgets.ColumnWidget):
    TAGS_TO_DEACTIVATE = {WTAG_FIELDHQ, }
    def __init__(self, mygear: gears.base.BaseGear):
        super().__init__(-100, -70, 200, 0, draw_border=True, center_interior=True, padding=16)
        self.mygear = mygear
        self.add_interior(pbge.widgets.LabelWidget(0, 0, 0, 0, "Change Name", font=pbge.BIGFONT))
        self.add_interior(pbge.widgets.TextEntryWidget(
            0, 0, 180, 24, text=str(mygear), on_change=self._set_name
        ))
        self.add_interior(pbge.widgets.LabelWidget(
            0, 0, 0, 0, "Done", justify=0, on_click=self._rename_done, draw_border=True
        ))

    def _set_name(self, wid, _ev):
        self.mygear.name = wid.text

    def _check_name(self):
        if not self.mygear.name:
            self.mygear.name = gears.selector.GENERIC_NAMES.gen_word()

    def _rename_done(self, _wid, _ev):
        self._check_name()
        self.pop()

    def _builtin_responder(self, ev):
        if ev.type == pygame.KEYDOWN:
            if pbge.my_state.is_key_for_action(ev, "exit"):
                self.register_response()
                self._check_name()
                self.pop()
            elif ev.unicode in "\n\r":
                self.register_response()
                self._check_name()
                self.pop()


class InfoDisplayWidget(widgets.Widget):
    # Hand this widget an info panel, and it'll display it. That's all it does.
    def __init__(self, info_display: gears.info.InfoPanel):
        super().__init__(
            fhqinfo.CENTER_COLUMN.dx, fhqinfo.CENTER_COLUMN.dy, fhqinfo.CENTER_COLUMN.w, fhqinfo.CENTER_COLUMN.h
        )
        self.info_display = info_display

    def _render(self, delta):
        myrect = self.get_rect()
        self.info_display.render(myrect.x, myrect.y)

    def on_activate(self):
        self.info_display.update()


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
                pc.bio, font=pbge.MEDIUMFONT, draw_border=True, border=pbge.default_border, visible=False
            )
            self.children.append(self.bio_panel)
            self.panels.append(self.bio_panel)

            self.add_center(widgets.LabelWidget(
                0, 0, 50, 0, "Bio", draw_border=True, border=widgets.widget_border_off, data=self.bio_panel,
                on_click=self._switch_panel, justify=0
            ))

        if pc.badges:
            self.badges_panel = MeritBadgeDisplayWidget(pc, visible=False)
            self.children.append(self.badges_panel)
            self.panels.append(self.badges_panel)

            self.add_center(widgets.LabelWidget(
                0, 0, 50, 0, "Badges", draw_border=True, border=widgets.widget_border_off, data=self.badges_panel,
                on_click=self._switch_panel, justify=0
            ))

    def _switch_panel(self, wid, _ev):
        for ccc in self.panels:
            if ccc is wid.data:
                ccc.visible = True
            else:
                ccc.visible = False
        for butt in self._center_widgets:
            if butt is wid:
                butt.border = widgets.widget_border_on
            else:
                butt.border = widgets.widget_border_off


class FHQPortraitMenu(pbge.widgetmenu.MenuWidget):
    def __init__(self, portrait_view: gears.portraits.PortraitView):
        super().__init__(
            fhqinfo.UTIL_MENU.dx, fhqinfo.UTIL_MENU.dy, fhqinfo.UTIL_MENU.w, fhqinfo.UTIL_MENU.h,
            font=pbge.MEDIUMFONT, pop_when_clicked=True
        )
        self.portrait_view = portrait_view

    def _render(self, delta):
        self.portrait_view.render()
        super()._render(delta)


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

        # self.column.add_interior(widgets.LabelWidget(
        #    0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Change Name", justify=0, draw_border=True,
        #    on_click=self._change_name
        # ))

        if pc is camp.pc:
            self.column.add_interior(
                widgets.LabelWidget(0, 0, fhqinfo.LEFT_COLUMN.w, 0, text="Edit Character", justify=0, draw_border=True,
                                    on_click=self.edit_pc))
        self.fhq = fhq
        self.children.append(CharacterCenterColumnWidget(camp, pc))

        self.sl = pbge.StretchyLayer()

    def _change_name(self, _wid, _ev):
        NameChangeWidget.push_state_and_instantiate(mygear=self.pc)

    def edit_pc(self, _wid, _ev):
        pceditor.PCEditorWidget.push_state_and_instantiate(self.fhq, camp=self.camp, pc=self.pc)

    def jump_plot(self, _wid, _ev):
        while not self.pc.relationship.can_do_development():
            self.pc.relationship.missions_together += 10

    def open_training(self, _wid, _ev):
        training.TrainingMenu.push_state_and_instantiate(self.fhq, camp=self.camp, pc=self.pc)
 
    def open_backpack(self, _wid, _ev):
        backpack.BackpackWidget.push_state_and_instantiate(self.fhq, camp=self.camp, pc=self.pc)

    def assign_mecha(self, _wid, _ev):
        mymenu = FHQPortraitMenu(self.portrait_view)
        for mek in self.camp.party:
            if isinstance(mek, gears.base.Mecha) and mek.is_not_destroyed() and (
                    not hasattr(mek, "owner") or mek.owner is self.pc):
                _=mymenu.add_item(mek.get_full_name(), self._actually_assign_the_mecha, data=mek)
        mymenu.children.append(AssignMechaDescWidget(self.camp, mymenu))
        mymenu.push_and_deploy(self.fhq)

    def _actually_assign_the_mecha(self, wid, _ev):
        # Callback for the assign mecha menu widget
        mek = wid.data
        self.camp.assign_pilot_to_mecha(self.pc, mek)

        if mek:
            self.fhq.update_party()
            pbge.my_state.view.regenerate_avatars([mek, ])

    def change_colors(self, _wid, _ev):
        if self.pc.portrait_gen:
            cchan = self.pc.portrait_gen.color_channels
        else:
            cchan = gears.color.CHARACTER_COLOR_CHANNELS
        cosplay.ColorEditor.push_state_and_instantiate(
            self.fhq,
            proto_sprite=self.pc.get_portrait(add_color=False), sprite_frame=0,
            channel_filters=cchan, colors=self.pc.colors, on_done=self._color_done
        )

    def on_activate(self):
        self.fhq.update_party()

    def _color_done(self, new_colors):
        self.pc.colors = new_colors
        self.portrait_view.portrait = self.pc.get_portrait(self.pc, force_rebuild=True)
        pbge.my_state.view.regenerate_avatars([self.pc, ])
        self.fhq.update_party()

    def _render(self, delta):
        self.portrait_view.render()


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

    def _render(self, delta):
        self.draw_portrait(False)
        mydest = fhqinfo.CENTER_COLUMN.get_rect()
        self.info.render(mydest.x, mydest.y)

    def assign_pilot(self, _wid, _ev):
        mymenu = FHQPortraitMenu(self.portrait_view)
        for plr in self.camp.party:
            if isinstance(plr, gears.base.Character) and plr.is_not_destroyed() and (
                    not hasattr(self.pc, "owner") or self.pc.owner is plr):
                _=mymenu.add_item(plr.get_full_name(), self._actually_assign_pilot, data=plr)
        mymenu.children.append(AssignPilotDescWidget(self.camp, mymenu))
        mymenu.push_and_deploy(self.fhq)

    def _actually_assign_pilot(self, wid, _ev):
        pilot = wid.data
        self.camp.assign_pilot_to_mecha(pilot, self.pc)
        self.info.update()

        self.fhq.update_party()
        pbge.my_state.view.regenerate_avatars([self.pc, ])

        self.fhq.active = True

    def open_backpack(self, _wid, _ev):
        backpack.BackpackWidget.push_state_and_instantiate(self.fhq, camp=self.camp, pc=self.pc)

    def change_colors(self, _wid, _ev):
        if self.pc.portrait_gen:
            cchan = self.pc.portrait_gen.color_channels
        else:
            cchan = gears.color.CHARACTER_COLOR_CHANNELS
        cosplay.ColorEditor.push_state_and_instantiate(
            self.fhq,
            proto_sprite=self.pc.get_portrait(add_color=False), sprite_frame=0,
            channel_filters=cchan, colors=self.pc.colors, on_done=self._color_done
        )

    def on_activate(self):
        self.fhq.update_party()

    def _color_done(self, new_colors):
        self.pc.colors = new_colors
        self.portrait_view.portrait = self.pc.get_portrait(self.pc, force_rebuild=True)
        pbge.my_state.view.regenerate_avatars([self.pc, ])
        self.fhq.update_party()


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

    def _render(self, delta):
        mydest = fhqinfo.CENTER_COLUMN.get_rect()
        self.info.render(mydest.x, mydest.y)

    def _dismiss(self, _wid, _ev):
        mymenu = pbge.widgetmenu.AlertMenuWidget(
            "Are you sure you want to dismiss {} permanently?".format(self.pc),
            pop_when_clicked=True, auto_escape=True
        )
        _=mymenu.add_item("Yes, dismiss {}.".format(self.pc), self._actually_dismiss)
        _=mymenu.add_item("No, I don't.".format(self.pc), None)
        mymenu.push_and_deploy(self.fhq)

    def _actually_dismiss(self, _wid, _ev):
        self.camp.deactivate_pet(self.pc)
        self.camp.party.remove(self.pc)
        self.fhq.update_party()

    def leave_behind(self, _wid, _ev):
        self.camp.deactivate_pet(self.pc)
        self.fhq.update_party()

    def bring_along(self, _wid, _ev):
        self.camp.activate_pet(self.pc)
        self.fhq.update_party()

    def _change_name(self, _wid, _ev):
        NameChangeWidget.push_state_and_instantiate(mygear=self.pc)

    def on_activate(self):
        self.info.update()
        self.fhq.update_party()


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

    def _render(self, delta):
        mydest = fhqinfo.CENTER_COLUMN.get_rect()
        self.info.render(mydest.x, mydest.y)

    def give_item(self, _wid, _ev):
        mymenu = pbge.widgetmenu.MenuWidget(
            fhqinfo.UTIL_MENU.dx, fhqinfo.UTIL_MENU.dy, fhqinfo.UTIL_MENU.w, fhqinfo.UTIL_MENU.h,
            font=pbge.MEDIUMFONT, pop_when_clicked=True, auto_escape=True
        )
        for plr in self.camp.party:
            if plr.can_equip(self.pc) and not (hasattr(plr, "owner") and plr.owner):
                _=mymenu.add_item(plr.get_full_name(), self._actually_give_item, data=plr)
        mymenu.push_and_deploy(self.fhq)

    def _actually_give_item(self, wid, _ev):
        pilot = wid.data
        if pilot:
            self.camp.party.remove(self.pc)
            pilot.inv_com.append(self.pc)

        self.info.update()
        self.fhq.update_party()


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
            draw_border=False, font=pbge.MEDIUMFONT, alt_smaller_fonts=(pbge.SMALLFONT, pbge.TINYFONT), 
            anchor=pbge.frects.ANCHOR_UPPERLEFT,
            on_click=self._click_name
        )
        self.children.append(label)

    def _render(self, delta):
        mydest = self.get_rect().inflate(-8, -8)
        if self.fhq.active_pc is self.pc:
            widgets.widget_border_on.render(mydest)
        else:
            widgets.widget_border_off.render(mydest)
        self.avatar_pic.render(mydest, self.avatar_frame)

    def _name_fun(self, *_args):
        return self.pc.get_full_name()

    def _click_name(self, _wid, ev):
        if self.on_click:
            self.on_click(self, ev)



class FieldHQ(widgets.Widget):
    # Three columns
    # To the left: the character portrait (if available)
    # In the center: the character info/action widgets
    # To the right: The list of characters/mecha in the party
    TAGS_TO_DEACTIVATE = {widgets.WTAG_WIDGET,}

    def __init__(self, camp):
        self._active_info = None
        super(FieldHQ, self).__init__(0, 0, 0, 0, tags={WTAG_FIELDHQ})

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

        self.children.append(pbge.widgets.LabelWidget(
            fhqinfo.RIGHT_COLUMN.dx + 64, fhqinfo.RIGHT_COLUMN.dy + fhqinfo.RIGHT_COLUMN.h + 20, 80, 0,
            text="Done", justify=0, on_click=self.done_button, draw_border=True
        ))

    def _set_active_info(self, pc):
        if self._active_info:
            self._active_info.visible = False
        self.active_pc = pc
        self._active_info = self.member_widgets.get(pc, None)
        if self._active_info:
            self._active_info.visible = True
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
                self.member_widgets[pc] = CharacterInfoWidget(self.camp, pc, self, visible=False)
                self.children.append(self.member_widgets[pc])
            elif isinstance(pc, gears.base.Mecha):
                self.member_widgets[pc] = MechaInfoWidget(self.camp, pc, self, visible=False)
                self.children.append(self.member_widgets[pc])
            elif isinstance(pc, gears.base.Monster):
                self.member_widgets[pc] = PetInfoWidget(self.camp, pc, self, visible=False)
                self.children.append(self.member_widgets[pc])
            else:
                self.member_widgets[pc] = ItemInfoWidget(self.camp, pc, self, visible=False)
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

    def click_member(self, wid, _ev):
        # self.active_pc = wid.pc
        self.active_info = wid.pc

    def done_button(self, _wid, _ev):
        self.pop()

    def _builtin_responder(self, ev):
        if ev.type == pygame.KEYDOWN:
            if pbge.my_state.is_key_for_action(ev, "exit"):
                self.register_response()
                self.pop()
                #print(self, ev, id(ev))

    def on_activate(self):
        self.update_party()

