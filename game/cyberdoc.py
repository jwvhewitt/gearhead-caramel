import pbge
import gears
from . import widgets
from gears import base
from gears.cyberinstaller import CyberwareSource, ListedSalesCyberwareSource, AllCyberwareSource, CyberwareInstaller
import pygame

ItemListWidget = widgets.ItemListWidget

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
LIST_HEIGHT = SCREEN_HEIGHT - (MARGIN + HEADER_HEIGHT + MARGIN + LABEL_HEIGHT + MARGIN * 2 + FOOTER_HEIGHT + MARGIN)
RIGHT_COLUMN_X = UL_X + SCREEN_WIDTH - (MARGIN + COLUMN_WIDTH)
FOOTER_Y = LIST_Y + LIST_HEIGHT + MARGIN

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

REMOVE_BUTTON_FRECT = pbge.frects.Frect( MID_COLUMN_X, FOOTER_Y
                                       , COLUMN_WIDTH, FOOTER_HEIGHT
                                       )
INSTALL_BUTTON_FRECT = pbge.frects.Frect( RIGHT_COLUMN_X, FOOTER_Y
                                        , COLUMN_WIDTH, FOOTER_HEIGHT
                                        )

EXIT_BUTTON_FRECT = pbge.frects.Frect( UL_X + SCREEN_WIDTH - (MARGIN + 40), UL_Y + MARGIN
                                     , 40, 40
                                     )

###############################################################################



class _AggregateCyberwareSource(CyberwareSource):
    def __init__(self, sources):
        self._sources = sources
        self._cw_to_source = dict()

    def get_cyberware_list(self):
        self._cw_to_source.clear()

        cws = list()
        for source in self._sources:
            source_cws = source.get_cyberware_list()

            for cw in source_cws:
                self._cw_to_source[cw] = source

            cws.extend(source_cws)

        return cws

    # Get the delegatee.
    def _get_source(self, cyberware):
        return self._cw_to_source[cyberware]

    def get_list_annotation(self, cyberware):
        return self._get_source(cyberware).get_list_annotation(cyberware)
    def get_panel_annotation(self, cyberware):
        return self._get_source(cyberware).get_panel_annotation(cyberware)
    def can_purchase(self, cyberware, camp):
        return self._get_source(cyberware).can_purchase(cyberware, camp)
    def acquire_cyberware(self, cyberware, camp):
        return self._get_source(cyberware).acquire_cyberware(cyberware, camp)


###############################################################################

class CoreUI(pbge.widgets.Widget):
    def __init__(self, char, source, camp, year = 158, **kwargs):
        super().__init__( UL_X, UL_Y
                        , SCREEN_WIDTH, SCREEN_HEIGHT
                        , **kwargs
                        )

        self.char = char
        self.source = source
        self.camp = camp
        self.year = year

        self._cyberware_installer = CyberwareInstaller( self.char
                                                      , self.source
                                                      , self.camp
                                                      , self._alert
                                                      , self._choose
                                                      )

        self.running = False
        self._active = True

        self.installed = list()
        self.uninstalled = list()

        # Info panels at the left.
        self._activeinfopanel = None

        self._mouseover_gear = None
        self._mouseover_prevgear = None
        self._mouseover_infopanel = None

        # Info panel at top.
        self._medicalpanel = None
        # Info panel at bottom.
        self._moneypanel = None

        # Build UI components.
        installed_label = pbge.widgets.LabelWidget( INSTALLED_LABEL_FRECT.dx, INSTALLED_LABEL_FRECT.dy
                                                  , INSTALLED_LABEL_FRECT.w, INSTALLED_LABEL_FRECT.h
                                                  , text = "INSTALLED", justify = 0
                                                  , font = pbge.BIGFONT
                                                  )
        self.children.append(installed_label)
        self._installed_listwidget = ItemListWidget( self.installed
                                                   , INSTALLED_LIST_FRECT
                                                   , text_fn = self._get_gear_name
                                                   , on_enter = self._try_set_mouseoverinfopanel
                                                   , on_leave = self._try_clear_mouseoverinfopanel
                                                   )
        self.children.append(self._installed_listwidget)
        available_label = pbge.widgets.LabelWidget( AVAILABLE_LABEL_FRECT.dx, AVAILABLE_LABEL_FRECT.dy
                                                  , AVAILABLE_LABEL_FRECT.w, AVAILABLE_LABEL_FRECT.h
                                                  , text = "AVAILABLE", justify = 0
                                                  , font = pbge.BIGFONT
                                                  )
        self.children.append(available_label)
        self._available_listwidget = ItemListWidget( self.uninstalled
                                                   , AVAILABLE_LIST_FRECT
                                                   , text_fn = self._get_list_annotated_gear_name
                                                   , on_enter = self._try_set_mouseoverinfopanel
                                                   , on_leave = self._try_clear_mouseoverinfopanel
                                                   )
        self.children.append(self._available_listwidget)
        remove_button = pbge.widgets.LabelWidget( REMOVE_BUTTON_FRECT.dx, REMOVE_BUTTON_FRECT.dy
                                                , REMOVE_BUTTON_FRECT.w, REMOVE_BUTTON_FRECT.h
                                                 , text = "Remove", justify = 0
                                                 , draw_border = True
                                                 , font = pbge.MEDIUMFONT
                                                 , on_click = self._remove
                                                )
        self.children.append(remove_button)
        install_button = pbge.widgets.LabelWidget( INSTALL_BUTTON_FRECT.dx, INSTALL_BUTTON_FRECT.dy
                                                 , INSTALL_BUTTON_FRECT.w, INSTALL_BUTTON_FRECT.h
                                                 , text = "Install", justify = 0
                                                 , draw_border = True
                                                 , font = pbge.MEDIUMFONT
                                                 , on_click = self._install
                                                 )
        self.children.append(install_button)
        exitimage = pbge.image.Image('sys_geareditor_buttons.png', 40, 40)
        exit_button = pbge.widgets.ButtonWidget( EXIT_BUTTON_FRECT.dx, EXIT_BUTTON_FRECT.dy
                                               , EXIT_BUTTON_FRECT.w, EXIT_BUTTON_FRECT.h
                                               , exitimage
                                               , frame = 6, on_frame = 6, off_frame = 7
                                               , on_click = self._on_exit
                                               , tooltip = "Leave Cyberdoc"
                                               )
        self.children.append(exit_button)

        # Preparations
        self._refresh_all()

    def _alert(self, text):
        # pbge.alert does not quite do what we want.
        self._choose([text])
    def _choose(self, items):
        '''Wrapper function to query the user among multiple choices.'''
        mymenu = pbge.rpgmenu.Menu( -CHOICE_WIDTH // 2, -CHOICE_HEIGHT // 2
                                  , CHOICE_WIDTH, CHOICE_HEIGHT
                                  , font = pbge.BIGFONT
                                  )
        for i, item in enumerate(items):
            mymenu.add_item(item, i)
        return mymenu.query()

    def _on_exit(self, *whatevs):
        self.running = False

    def set_activeinfopanel(self, gear):
        self._activeinfopanel = self._make_infopanel(gear)
    def set_mouseoverinfopanel(self, gear):
        self._mouseover_gear = gear
    def _try_set_mouseoverinfopanel(self, gear):
        if not self._active:
            return
        self.set_mouseoverinfopanel(gear)
    def _try_clear_mouseoverinfopanel(self, gear):
        if not self._active:
            return
        # Only clear if it is currently selected;
        # this handles out-of-order cases.
        if self._mouseover_gear is gear:
            self._mouseover_gear = None

    def _get_gear_name(self, gear):
        return gear.name
    def _get_list_annotated_gear_name(self, gear):
        name = self._get_gear_name(gear)
        ann = self.source.get_list_annotation(gear)
        if ann:
           name += " " + ann
        return name

    def _make_infopanel(self, gear):
        if isinstance(gear, base.Character):
            return _CyberCharPanel(model = gear, width = COLUMN_WIDTH, camp = self.camp)
        else:
            ip = gears.info.get_longform_display(model = gear, width = COLUMN_WIDTH)
            if gear.parent and isinstance(gear.parent, base.Module):
                ip.info_blocks.insert(1, _InstalledInBlock(model = gear, width = COLUMN_WIDTH))
            if gear in self.uninstalled:
                ip.info_blocks.insert(1, _SourceAnnotationBlock(model = gear, width = COLUMN_WIDTH, source = self.source))
            return ip

    def _refresh_all(self):
        self._gather_cyberware()
        self.set_activeinfopanel(self.char)
        self._medicalpanel = _MedicalCommentaryPanel( model = self.char
                                                    , year = self.year
                                                    , width = MED_PANEL_FRECT.w
                                                    )
        self._moneypanel = _CreditsPanel( model = self.char
                                        , camp = self.camp
                                        , width = MONEY_PANEL_FRECT.w
                                        )

    def _gather_cyberware(self):
        del self.installed[:]
        del self.uninstalled[:]

        for part in self.char.sub_sub_coms():
             if isinstance(part, base.BaseCyberware):
                 self.installed.append(part)
        self.uninstalled.extend(self.source.get_cyberware_list())

        self.installed.sort(key = lambda c: c.name)
        self.uninstalled.sort(key = lambda c: c.name)

        self._installed_listwidget.refresh_item_list()
        self._available_listwidget.refresh_item_list()

    def render(self, flash=False):
        super().render(flash)
        rect = INFO_PANEL_FRECT.get_rect()
        if self._mouseover_gear:
            if not (self._mouseover_gear is self._mouseover_prevgear):
                self._mouseover_infopanel = self._make_infopanel(self._mouseover_gear)
                self._mouseover_prevgear = self._mouseover_gear
            self._mouseover_infopanel.render(rect.x, rect.y)
        else:
            self._mouseover_prevgear = None
            self._mouseover_infopanel = None
            self._activeinfopanel.render(rect.x, rect.y)

        rect = MED_PANEL_FRECT.get_rect()
        self._medicalpanel.render(rect.x, rect.y)

        rect = MONEY_PANEL_FRECT.get_rect()
        self._moneypanel.render(rect.x, rect.y)

    def _install(self, widj, ev):
        if self._available_listwidget.current_item:
            cw = self._available_listwidget.current_item

            self._active = False
            self._cyberware_installer.install(cw)
            self._active = True

            self._refresh_all()
    def _remove(self, widj, ev):
        if self._installed_listwidget.current_item:
            cw = self._installed_listwidget.current_item

            self._active = False
            self._cyberware_installer.remove(cw)
            self._active = True

            self._refresh_all()

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

####
# Cyberdoc-specific info blocks.

class _TextLabelBlock(object):
    '''Display a constant string centered in the info panel.'''
    def __init__(self, model, width = 220, font = None, color = None, **keywords):
        self.model = model
        self.width = width
        self.font = font or pbge.BIGFONT
        self.color = color or pbge.WHITE

        msg = self.get_text()
        if msg:
            self.image = pbge.render_text(self.font, msg, self.width, justify = 0, color = self.color)
            self.height = self.image.get_height()
        else:
            self.image = None
            self.height = 0

    def render(self, x, y):
        if self.image:
            pbge.my_state.screen.blit(self.image, pygame.Rect(x, y, self.width, self.height))

    def get_text(self):
        raise RuntimeError("_TextLabelBlock.get_text called")

class _SourceAnnotationBlock(_TextLabelBlock):
    '''Displays the source-based annotation.
    '''
    def __init__(self, source, **keywords):
        keywords.pop('color', None)
        self.source = source
        super().__init__(color = pbge.TEXT_COLOR, **keywords)
    def get_text(self):
        return self.source.get_panel_annotation(self.model)

class _CreditsBlock(_TextLabelBlock):
    def __init__(self, camp, **keywords):
        keywords.pop('color', None)
        self.camp = camp
        super().__init__(color = pbge.TEXT_COLOR, **keywords)
    def get_text(self):
        return '${:,}'.format(self.camp.credits)

class _TraumaBlock(_TextLabelBlock):
    '''Displays the current and max trauma of the given model character.'''
    def get_text(self):
        return "Trauma: {} / {}".format(self.model.current_trauma, self.model.max_trauma)

class _StaminaLostBlock(_TextLabelBlock):
    ''' Display the stamina lost by the character due to
    cyberware
    '''
    def get_text(self):
        return "Stamina Lost: {}".format(self.model.get_uncybered_max_stamina() - self.model.get_max_stamina())

class _InstalledInBlock(_TextLabelBlock):
    '''Displays the module the given model is installed in.'''
    def __init__(self, **keywords):
        keywords["color"] = keywords.get('color', pbge.TEXT_COLOR)
        super().__init__(**keywords)
    def get_text(self):
        return "Installed: {}".format(self.model.parent.name)

class _CyberCharPanel(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (gears.info.FullNameBlock, gears.info.ModuleStatusBlock, _TraumaBlock, _StaminaLostBlock, gears.info.CharacterStatusBlock, gears.info.PrimaryStatsBlock, gears.info.NonComSkillBlock)

class _CreditsPanel(gears.info.InfoPanel):
    DEFAULT_BLOCKS = (_CreditsBlock,)

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

class InventorySource(CyberwareSource):
    def __init__(self, char):
        self.char = char
    def get_cyberware_list(self):
        rv = list()
        for cw in self.char.inv_com:
            if isinstance(cw, base.BaseCyberware):
                rv.append(cw)
        return rv
    def get_list_annotation(self, cyberware):
        if cyberware.dna_sequence and cyberware.dna_sequence != self.char.dna_sequence:
            return "[Incompatible]"
        return '[Inv]'
    def get_panel_annotation(self, cyberware):
        if cyberware.dna_sequence and cyberware.dna_sequence != self.char.dna_sequence:
            return "Genetically Incompatible With {}".format(self.char.name)
        return 'With {}'.format(self.char.name)
    def acquire_cyberware(self, cyberware, camp):
        self.char.inv_com.remove(cyberware)
        return cyberware
class StashSource(CyberwareSource):
    def __init__(self, char, stash):
        self.char = char
        self.stash = stash
    def get_cyberware_list(self):
        rv = list()
        for cw in self.stash:
            if isinstance(cw, base.BaseCyberware):
                rv.append(cw)
        return rv
    def get_list_annotation(self, cyberware):
        if cyberware.dna_sequence and cyberware.dna_sequence != self.char.dna_sequence:
            return "[Incompatible]"
        return "[Stash]"
    def get_panel_annotation(self, cyberware):
        if cyberware.dna_sequence and cyberware.dna_sequence != self.char.dna_sequence:
            return "Genetically Incompatible With {}".format(self.char.name)
        return "Stashed"
    def acquire_cyberware(self, cyberware, camp):
        self.stash.remove(cyberware)
        return cyberware


class ShopCyberwareSource(ListedSalesCyberwareSource):
    def __init__(self, shop, camp):
        # shop must be instance of game.services.Shop
        shop.update_shop(camp)
        self.shop = shop
        self.camp = camp
        super().__init__(shop.wares)
    def get_cyberware_cost(self, cyberware):
        return self.shop.calc_purchase_price(self.camp, cyberware)
    def acquire_cyberware(self, cyberware, camp):
        ret = super().acquire_cyberware(cyberware, camp)
        self.shop.improve_friendliness(camp, ret)
        return ret


# Adaptor class, for external use.
class UI(CoreUI):
    def __init__(self, char, camp, shop = None, stash = None, year = 158, **kwargs):
        if stash is None:
            stash = pbge.container.ContainerList(owner=self)
        if shop:
            shop_source = ShopCyberwareSource(shop, camp)
        else:
            shop_source = AllCyberwareSource()
        sources = [ InventorySource(char)
                  , StashSource(char, stash)
                  , shop_source
                  ]
        super().__init__(char, _AggregateCyberwareSource(sources), camp, year)

