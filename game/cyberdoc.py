import pbge
import gears
#from . import widgets
from gears import base
#from gears.cyberinstaller import CyberwareSource, ListedSalesCyberwareSource, AllCyberwareSource, CyberwareInstaller
import pygame
from . import shopui
import copy

#ItemListWidget = widgets.ItemListWidget

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MARGIN = 32

CHOICE_WIDTH = int(SCREEN_WIDTH / 2.5)
CHOICE_HEIGHT = int(SCREEN_HEIGHT / 2.5)

UL_X = -SCREEN_WIDTH // 2
UL_Y = -SCREEN_HEIGHT // 2

COLUMN_WIDTH = (SCREEN_WIDTH - MARGIN * 4) // 3
HEADER_HEIGHT = 40
LABEL_HEIGHT = 20
FOOTER_HEIGHT = 20

MED_PANEL_FRECT = pbge.frects.Frect( UL_X + MARGIN + COLUMN_WIDTH + MARGIN, UL_Y + MARGIN
                                   , COLUMN_WIDTH * 2 - 40, HEADER_HEIGHT
                                   )

INFO_PANEL_FRECT = pbge.frects.Frect( UL_X + MARGIN, UL_Y + MARGIN
                                    , COLUMN_WIDTH, SCREEN_HEIGHT - MARGIN * 2
                                    )

MID_COLUMN_X = UL_X + MARGIN + COLUMN_WIDTH + MARGIN
LABEL_Y = UL_Y + MARGIN + HEADER_HEIGHT + MARGIN
LIST_Y = LABEL_Y + LABEL_HEIGHT + MARGIN
LIST_HEIGHT = SCREEN_HEIGHT - (MARGIN + HEADER_HEIGHT + MARGIN + LABEL_HEIGHT + MARGIN * 2)
RIGHT_COLUMN_X = UL_X + SCREEN_WIDTH - (MARGIN + COLUMN_WIDTH)
FOOTER_Y = LIST_Y + LIST_HEIGHT - FOOTER_HEIGHT + MARGIN//2

MONEY_PANEL_FRECT = pbge.frects.Frect( UL_X + MARGIN, FOOTER_Y
                                     , COLUMN_WIDTH, FOOTER_HEIGHT
                                     )

INSTALLED_LABEL_FRECT = pbge.frects.Frect( MID_COLUMN_X, LABEL_Y
                                         , COLUMN_WIDTH, LABEL_HEIGHT
                                         )
INSTALLED_LIST_FRECT = pbge.frects.Frect( MID_COLUMN_X, LIST_Y
                                        , COLUMN_WIDTH, LIST_HEIGHT
                                        )
AVAILABLE_LABEL_FRECT = pbge.frects.Frect( RIGHT_COLUMN_X, LABEL_Y
                                         , COLUMN_WIDTH, LABEL_HEIGHT
                                         )
AVAILABLE_LIST_FRECT = pbge.frects.Frect( RIGHT_COLUMN_X, LIST_Y
                                        , COLUMN_WIDTH, LIST_HEIGHT
                                        )

EXIT_BUTTON_FRECT = pbge.frects.Frect( UL_X + SCREEN_WIDTH - (MARGIN + 40), UL_Y + MARGIN
                                     , 40, 40
                                     )

###############################################################################

class _TraumaBlock(gears.info.AbstractModelTextBlock):
    '''Displays the current and max trauma of the given model character.'''
    def get_text(self):
        return "Trauma: {} / {}".format(self.model.current_trauma, self.model.max_trauma)

class _StaminaLostBlock(gears.info.AbstractModelTextBlock):
    ''' Display the stamina lost by the character due to
    cyberware
    '''
    def get_text(self):
        return "Stamina Lost: {}".format(self.model.get_uncybered_max_stamina() - self.model.get_max_stamina())

class _InstalledInBlock(gears.info.AbstractModelTextBlock):
    '''Displays the module the given model is installed in.'''
    def __init__(self, **keywords):
        keywords["color"] = keywords.get('color', pbge.TEXT_COLOR)
        super().__init__(**keywords)
    def get_text(self):
        return "Installed: {}".format(self.model.parent.name)

class _CyberCharPanel(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.FullNameBlock, gears.info.ModuleStatusBlock, _TraumaBlock, _StaminaLostBlock, gears.info.CharacterStatusBlock, gears.info.PrimaryStatsBlock, gears.info.NonComSkillBlock)

class _CreditsPanel(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.CreditsBlock,)

class _MedicalCommentaryBlock( object ):
    def __init__(self, model, width = 220, year = 158, font = None, color = None, **kwargs):
        self.model = model
        self.year = year
        self.width = width
        self.font = font or pbge.SMALLFONT
        self.color = color or pbge.INFO_GREEN
        self._generate_commentary()
        self._image = pbge.render_text(self.font, self._text, self.width, self.color)
        self.height = self._image.get_height()

    def _generate_commentary(self):
        char = self.model
        text = ("Patient {} is {} {} years old, with "
               .format(char.name, char.gender.adjective.lower(), self.year - char.birth_year)
               )

        cw = list(char.cyberware())

        nwares = len(cw)
        if nwares == 0:
            text += "no installed cyberware"
        elif nwares == 1:
            text += ( "cyberware installed in {} of {}"
                    .format( cw[0].location.lower()
                           , cw[0].parent.name.lower()
                           )
                    )
        elif nwares == 2:
            text += ( "cyberware installed in {} of {} and {} of {}"
                    .format( cw[0].location.lower()
                           , cw[0].parent.name.lower()
                           , cw[1].location.lower()
                           , cw[1].parent.name.lower()
                           )
                    )
        else:
            text += "extensive cybermodifications"

        remaining_trauma = char.max_trauma - char.current_trauma
        if remaining_trauma > 10:
            text += " and good prognosis for major cyberware surgery"
        elif remaining_trauma > 6:
            text += " and good prognosis for cyberware surgery"
        elif remaining_trauma > 3:
            text += "; still safe for minor cyberware installation"
        elif remaining_trauma > 0:
            text += "; minimal scope for cyberware installation"
        else:
            text += "; cyberware installation contraindicated"

        text += "."

        self._text = text

    def render(self, x, y):
        pbge.my_state.screen.blit( self._image
                                 , pygame.Rect(x, y, self.width, self.height)
                                 )

class _MedicalCommentaryPanel(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (_MedicalCommentaryBlock,)


###############################################################################

class CyberMenu(pbge.rpgmenu.AlertMenu):
    WIDTH = 350
    HEIGHT = 250
    MENU_HEIGHT = 150

    FULL_RECT = pbge.frects.Frect(-WIDTH//2,-HEIGHT//2,WIDTH,HEIGHT)
    TEXT_RECT = pbge.frects.Frect(-WIDTH//2,-HEIGHT//2,WIDTH,HEIGHT - MENU_HEIGHT - 10)


class SurgeryUI(pbge.widgets.Widget):
    def __init__(self, camp: gears.GearHeadCampaign, shop, pc: gears.base.Being, **kwargs):
        super().__init__(UL_X, UL_Y, SCREEN_WIDTH, SCREEN_HEIGHT, show_when_inactive=True, **kwargs)

        self.pc = pc
        self.shop = shop
        self.camp = camp

        self.running = True

        # Info panels at the left.
        self._active_info_panel = None

        installed_label = pbge.widgets.LabelWidget( INSTALLED_LABEL_FRECT.dx, INSTALLED_LABEL_FRECT.dy
                                                  , INSTALLED_LABEL_FRECT.w, INSTALLED_LABEL_FRECT.h
                                                  , text = "INSTALLED", justify = 0
                                                  , font = pbge.BIGFONT
                                                  )
        self.children.append(installed_label)
        self._installed_listwidget = pbge.widgetmenu.MenuWidget(
            INSTALLED_LIST_FRECT.dx, INSTALLED_LIST_FRECT.dy, INSTALLED_LIST_FRECT.w, INSTALLED_LIST_FRECT.h,
            activate_child_on_enter=True, on_activate_item=self._try_set_info_panel
        )
        self.children.append(self._installed_listwidget)
        available_label = pbge.widgets.LabelWidget( AVAILABLE_LABEL_FRECT.dx, AVAILABLE_LABEL_FRECT.dy
                                                  , AVAILABLE_LABEL_FRECT.w, AVAILABLE_LABEL_FRECT.h
                                                  , text = "AVAILABLE", justify = 0
                                                  , font = pbge.BIGFONT
                                                  )
        self.children.append(available_label)
        self._available_listwidget = pbge.widgetmenu.MenuWidget(
            AVAILABLE_LIST_FRECT.dx, AVAILABLE_LIST_FRECT.dy, AVAILABLE_LIST_FRECT.w, AVAILABLE_LIST_FRECT.h,
            activate_child_on_enter=True, on_activate_item=self._try_set_info_panel
        )
        self.children.append(self._available_listwidget)

        exitimage = pbge.image.Image('sys_geareditor_buttons.png', 40, 40)
        exit_button = pbge.widgets.ButtonWidget( EXIT_BUTTON_FRECT.dx, EXIT_BUTTON_FRECT.dy
                                               , EXIT_BUTTON_FRECT.w, EXIT_BUTTON_FRECT.h
                                               , exitimage
                                               , frame = 6, on_frame = 6, off_frame = 7
                                               , on_click = self._on_exit
                                               , tooltip = "Leave Cyberdoc"
                                               )
        self.children.append(exit_button)

        self._med_panel = _MedicalCommentaryPanel( model = self.pc, year = self.camp.year, width = MED_PANEL_FRECT.w)
        self._med_panel_widget = gears.info.InfoWidget(
            MED_PANEL_FRECT.dx, MED_PANEL_FRECT.dy, MED_PANEL_FRECT.w, MED_PANEL_FRECT.h,
            info_panel= self._med_panel,
        )
        self.children.append(self._med_panel_widget)

        self._credits_panel = _CreditsPanel(
            model = self.pc, camp = self.camp, width = MONEY_PANEL_FRECT.w, font=pbge.BIGFONT
        )
        self._credits_panel_widget = gears.info.InfoWidget(
            MONEY_PANEL_FRECT.dx, MONEY_PANEL_FRECT.dy, MONEY_PANEL_FRECT.w, MONEY_PANEL_FRECT.h,
            info_panel = self._credits_panel
        )
        self.children.append(self._credits_panel_widget)

        self._style = dict(font=pbge.MEDIUM_DISPLAY_FONT)

        # Preparations
        self._build_all()

    def _try_set_info_panel(self, wmenu, menuitem):
        if not self.active:
            return
        if menuitem and menuitem.data:
            self._set_infopanel(menuitem.data)

    def _set_infopanel(self, gear):
        if isinstance(gear, base.Character):
            self._active_info_panel = _CyberCharPanel(model = gear, width = COLUMN_WIDTH, camp = self.camp)
        else:
            ip = gears.info.get_longform_display(model = gear, width = COLUMN_WIDTH)
            if gear.parent and isinstance(gear.parent, base.Module):
                ip.info_blocks.insert(1, _InstalledInBlock(model = gear, width = COLUMN_WIDTH))
            else:
                ip.info_blocks.insert(1, shopui.CostBlock(cost=self.shop.calc_purchase_price(self.camp, gear), width = COLUMN_WIDTH))
            self._active_info_panel = ip

    def _build_all(self):
        self._refresh_installed_list()
        self._refresh_available_list()
        self._set_infopanel(self.pc)

    def _refresh_all(self):
        self._refresh_installed_list()
        self._refresh_available_list()
        self._med_panel.update()
        self._credits_panel.update()
        if self._active_info_panel:
            self._active_info_panel.update()

    def _refresh_installed_list(self):
        self._installed_listwidget.clear()
        for gear in self.pc.sub_sub_coms():
            if isinstance(gear, gears.base.BaseCyberware):
                self._installed_listwidget.add_interior(pbge.widgetmenu.MenuItemWidget(
                    0, 0, COLUMN_WIDTH, 0, text="{} [{}]".format(gear, gear.parent), data=gear, on_click=self._remove, **self._style
                ))

        self._installed_listwidget.sort(key=lambda a: str(a))

    def _refresh_available_list(self):
        self._available_listwidget.clear()
        for gear in self.shop.wares:
            if isinstance(gear, gears.base.BaseCyberware):
                self._available_listwidget.add_interior(pbge.widgetmenu.MenuItemWidget(
                    0, 0, COLUMN_WIDTH, 0, text=gear.get_full_name(), data=gear, on_click=self._install, **self._style
                ))

        for gear in self.pc.inv_com:
            if isinstance(gear, gears.base.BaseCyberware) and (gear.dna_sequence == self.pc.dna_sequence or not gear.dna_sequence):
                self._available_listwidget.add_interior(pbge.widgetmenu.MenuItemWidget(
                    0, 0, COLUMN_WIDTH, 0, text="{} [inv]".format(gear.get_full_name()), data=gear, on_click=self._install, **self._style
                ))

        self._available_listwidget.sort(key=lambda a: str(a))

    def _install(self, widj, ev):
        cyber = widj.data
        mymenu = CyberMenu("Select Installation Location", alert_font=pbge.BIGFONT, font=pbge.MEDIUM_DISPLAY_FONT)
        if self.camp.credits >= self.shop.calc_purchase_price(self.camp, cyber):
            for limb in self.pc.sub_com:
                if limb.can_install(cyber, False):
                    other_cyber = cyber.get_current_cyber(limb)
                    if limb.can_install(cyber):
                        mymenu.add_item("Install {} in {}".format(cyber, limb), limb)
                    elif other_cyber and cyber.can_replace(limb, other_cyber):
                        mymenu.add_item("Replace {} with {} in {}".format(other_cyber, cyber, limb), limb)
            if mymenu.items:
                mymenu.add_item("Cancel installation", False)
            else:
                mymenu.add_item("Cannot install {} due to current trauma".format(cyber), False)
        else:
            mymenu.desc = "You cannot afford {}".format(cyber)
            mymenu.add_item("[Continue]", False)

        limb = mymenu.query()
        if limb:
            other_cyber = cyber.get_current_cyber(limb)
            if other_cyber:
                other_cyber.container.remove(other_cyber)
                other_cyber.record_dna(self.pc)
                self.pc.inv_com.append(other_cyber)

            self.camp.credits -= self.shop.calc_purchase_price(self.camp, cyber)

            if cyber in self.pc.inv_com:
                self.pc.inv_com.remove(cyber)
            else:
                cyber = copy.deepcopy(cyber)
            cyber.record_dna(self.pc)
            limb.sub_com.append(cyber)
            self._refresh_all()

    def _remove(self, widj, ev):
        cyber = widj.data
        mymenu = CyberMenu(
            "Remove {} from {}?".format(cyber, cyber.parent), alert_font=pbge.BIGFONT, font=pbge.MEDIUM_DISPLAY_FONT
        )
        mymenu.add_item("Accept", True)
        mymenu.add_item("Cancel", False)

        if mymenu.query():
            cyber.container.remove(cyber)
            cyber.record_dna(self.pc)
            self.pc.inv_com.append(cyber)
            self._refresh_all()

    def _on_exit(self, *args, **kwargs):
        self.running = False

    def render(self, flash=False):
        super().render(flash)
        if self._active_info_panel:
            myrect = INFO_PANEL_FRECT.get_rect()
            self._active_info_panel.render(myrect.x, myrect.y)

    def _builtin_responder(self, ev):
        super()._builtin_responder(ev)
        a_rect = self._installed_listwidget.get_rect()
        b_rect = self._available_listwidget.get_rect()
        if not (a_rect.collidepoint(pbge.my_state.mouse_pos) or b_rect.collidepoint(pbge.my_state.mouse_pos)):
            self._set_infopanel(self.pc)

    ### Primary entry point.
    def activate_and_run(self):
        pbge.my_state.widgets.append(self)
        self.running = True
        while self.running and not pbge.my_state.got_quit:
            ev = pbge.wait_event()
            if ev.type == pbge.TIMEREVENT:
                pbge.my_state.view()
                pbge.my_state.do_flip()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.running = False
        pbge.my_state.widgets.remove(self)



