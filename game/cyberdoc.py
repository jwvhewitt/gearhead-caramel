import pbge
import gears
from gears import base
import pygame

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

# Users of the cyberdoc should provide an object providing this
# interface.
class CyberwareSource(object):
    def get_cyberware_list(self):
        ''' Return a list of cyberware this source
        provides.
        Cyberware are gears from BaseCyberware.
        This implies to the caller that any of the
        returned cyberware gears may, in the future,
        be used in the other functions below.
        '''
        raise NotImplementedError()
    def get_list_annotation(self, cyberware):
        ''' Return either None, or a string.
        If a string is returned, that string
        will be appended with a space to
        cyberware.name in the list of available
        gears.
        '''
        return None
    def get_panel_annotation(self, cyberware):
        ''' Return either None, or a string.
        If a string is returned, that string
        will be added to the infopanel when
        the cyberware is hovered.
        '''
        return None
    def can_purchase(self, cyberware, camp):
        ''' Determine if the given camp can
        pay for the cyberware, or whatever.
        Return true if the camp can buy.
        '''
        return True
    def acquire_cyberware(self, cyberware, camp):
        ''' Acquire a stock copy of the cyberware
        and deduct money from the camp, or remove
        this cyberware from this source.
        Return the copy, or the same cyberware.
        '''
        raise NotImplementedError()


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

        self._cyberware_installer = _CyberwareInstaller( self.char
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
            return _CyberCharPanel(model = gear, width = COLUMN_WIDTH)
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

    def render(self):
        super().render()
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
# ItemListWidget - we can factor this out trivially.

class SingleListItemWidget(pbge.widgets.Widget):
    def __init__(self, text, width, data = None, on_enter = None, on_leave = None, font = None, color = None, **kwargs):
        self.font = font or pbge.BIGFONT
        super().__init__(0, 0, width, self.font.get_linesize(), **kwargs)

        self.text = text
        self.data = data
        self.on_enter = on_enter
        self.on_leave = on_leave
        self.color = color or pbge.INFO_GREEN
        self.h = self._image.get_height() + self.font.get_linesize() // 3

        self._mouse_is_over = False

    @property
    def color(self):
        return self._color
    @color.setter
    def color(self, value):
        self._color = value
        self._image = pbge.render_text(self.font, self.text, self.w, self.color)

    def render(self):
        myrect = self.get_rect()
        pbge.my_state.screen.blit(self._image, myrect)
        if self.on_enter or self.on_leave:
            if myrect.collidepoint(*pygame.mouse.get_pos()):
               if not self._mouse_is_over:
                   self._mouse_is_over = True
                   if self.on_enter:
                       self.on_enter(self)
            else:
               if self._mouse_is_over:
                   self._mouse_is_over = False;
                   if self.on_leave:
                       self.on_leave(self)

# TODO: We should have a common base list selection widget.
# Heck, we have an RPG menu that does most of what we want,
# but is modal.
# We just need to create a modeless widget and then make it
# modal for RPG menu.
class ItemListWidget(pbge.widgets.ColumnWidget):
    def __init__( self, item_list, frect, text_fn = None, can_select = True
                , on_enter = None, on_leave = None
                , **keywords
                ):
        super().__init__( frect.dx, frect.dy, frect.w, frect.h
                        , draw_border = True
                        , center_interior = True
                        , **keywords
                        )
        self.item_list = item_list
        self.current_item = None
        self.text_fn = text_fn or (lambda a: a)
        self._item_width = frect.w - 12
        self.can_select = can_select

        self.on_enter = on_enter
        self.on_leave = on_leave

        # TODO: These up/down button widgets really oughta
        # be factored out.
        # These are duplicated a good nmber of places in the code!
        updown = pbge.image.Image("sys_updownbuttons.png", 128, 16)
        up_arrow = pbge.widgets.ButtonWidget( 0, 0, 128, 16
                                            , sprite = updown
                                            , on_frame = 0, off_frame = 1
                                            )
        down_arrow = pbge.widgets.ButtonWidget( 0, 0, 128, 16
                                              , sprite = updown
                                              , on_frame = 2, off_frame = 3
                                              )
        self.scroll_column = pbge.widgets.ScrollColumnWidget( 0, 0
                                                            , frect.w, frect.h - 32
                                                            , up_arrow, down_arrow
                                                            , padding = 0
                                                            )
        self.add_interior(up_arrow)
        self.add_interior(self.scroll_column)
        self.add_interior(down_arrow)

        # Highlighting and selecting.
        self._current_highlight_widj = None
        self._current_selected_widj = None

        self.refresh_item_list()

    def refresh_item_list(self):
        # Remove all items.
        self.scroll_column.clear()
        for item in self.item_list:
            self.scroll_column.add_interior(
                SingleListItemWidget( self.text_fn(item), self._item_width
                                    , data = item
                                    , on_enter = self._handle_item_enter
                                    , on_leave = self._handle_item_leave
                                    , on_click = self._handle_item_click
                                    )
            )
        self._current_selected_widj = None
        self._current_highlight_widj = None
        self.current_item = None

    def _handle_item_enter(self, widj):
        if self._current_highlight_widj and not self._current_highlight_widj is self._current_selected_widj:
           self._current_highlight_widj.color = pbge.INFO_GREEN
           if self.on_leave:
               self.on_leave(self._current_highlight_widj.data)

        if widj is self._current_selected_widj:
            pass
        else:
            widj.color = pbge.INFO_HILIGHT
        self._current_highlight_widj = widj

        if self.on_enter:
            self.on_enter(widj.data)

    def _handle_item_leave(self, widj):
        if widj is self._current_highlight_widj:
            self._current_highlight_widj = None
            if not widj is self._current_selected_widj:
                widj.color = pbge.INFO_GREEN

            if self.on_leave:
                self.on_leave(widj.data)
    def _handle_item_click(self, widj, ev):
        if not self.can_select:
            return
        if widj is self._current_selected_widj:
            return
        if self._current_selected_widj:
            self._current_selected_widj.color = pbge.INFO_GREEN
        self._current_selected_widj = widj
        widj.color = pbge.rpgmenu.MENU_SELECT_COLOR
        self.current_item = widj.data

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

class _CyberwareInstaller(object):
    ''' Business logic for installing cyberware.
    '''
    def __init__(self, char, source, camp, alert, choose):
        # alert is a function that accepts a single string and shows it to
        # the user.
        # choose is a function given a list of strings, prompts the user
        # to choose one, then returns the 0-based index of the selection.
        self.char = char
        self.source = source
        self.camp = camp
        self.alert = alert
        self.choose = choose

    def install(self, cyberware):
        if not self.source.can_purchase(cyberware, self.camp):
            self.alert("You cannot afford it!")
            return

        candidate_modules = self._get_candidate_modules(cyberware)
        if not candidate_modules:
            self.alert('Cannot install {}: cannot be installed in any body part.'.format(cyberware.name))
            return

        no_choice_failure = ( "Cannot install {}:\nCurrent trauma is {} / {};\nit would bring your trauma to {}."
                              .format( cyberware.name
                                     , self.char.current_trauma
                                     , self.char.max_trauma
                                     , self.char.current_trauma + cyberware.trauma
                                     )
                            )

        choices = list()
        for mod in candidate_modules:
            if mod.can_install(cyberware):
                choices.append(( "Install in {}".format(mod.name)
                               , self._make_install_fun(mod, cyberware)
                               ))
            # Seach for replacements.
            for other_cyberware in list(mod.sub_com):
                if not isinstance(other_cyberware, base.BaseCyberware):
                    continue
                # You can only replace with the same location.
                if not cyberware.location is other_cyberware.location:
                    continue
                if self._can_replace(mod, other_cyberware, cyberware):
                    choices.append(( "Replace {} in {}".format(other_cyberware.name, mod.name)
                                   , self._make_replace_fun(mod, other_cyberware, cyberware)
                                   ))
                else:
                    no_choice_failure = ( "Cannot install {}:\nCurrent trauma is {} / {};\neven replacing {} would bring your trauma to {}."
                                          .format( cyberware.name
                                                 , self.char.current_trauma
                                                 , self.char.max_trauma
                                                 , other_cyberware.name
                                                 , self.char.current_trauma + cyberware.trauma - other_cyberware.trauma
                                                 )
                                        )

        if not choices:
            self.alert(no_choice_failure)
            return

        # If only once choice, don't bother asking the
        # player.
        if len(choices) == 1:
            choice = choices[0]
            choice[1]()
            return

        text_choices = [choice[0] for choice in choices]
        text_choices.append("[Cancel]")

        choice_index = self.choose(text_choices)
        if choice_index is False or choice_index >= len(choices):
            # Cancelled.
            return

        # Execute the choice.
        choice = choices[choice_index]
        choice[1]()

    def remove(self, cyberware):
        ''' Remove cyberware from its owner.
        Note: we do not do any checks below, we presume the
        caller has already determined that the cyberware is
        installed in the given self.char!
        '''
        cyberware.parent.sub_com.remove(cyberware)
        self._return_old_cyberware(cyberware)

    def _get_candidate_modules(self, cyberware):
        ''' Return all modules the cyberware can be installed in.
        Do not filter based on trauma or having an existing
        cyberware yet.
        '''
        return [ mod for mod in self.char.sub_sub_coms()
              if isinstance(mod, base.Module)
             and mod.can_install(cyberware, check_volume = False)
               ]

    def _can_replace(self, mod, old, new):
        ''' Determine if we can install the new cyberware
        if the old cyberware is removed first.
        '''
        # We actually perform the remove, *then* check,
        # then restore the old gear.
        # This lets us leave the cyberware check to
        # gears.base, so only one place needs to be
        # updated if we want to change the limits on
        # cyberware.
        mod.sub_com.remove(old)
        ret = mod.can_install(new)
        mod.sub_com.append(old)
        return ret

    def _make_install_fun(self, mod, cyberware):
        ''' Create a function which will actually install
        the cyberware into the specified module.
        '''
        def install():
            to_install = self._acquire_new_cyberware(cyberware)
            mod.sub_com.append(to_install)
        return install

    def _make_replace_fun(self, mod, old, new):
        ''' Create a function which will actually remove
        the old cyberware and put the new cyberware into
        the specified module.
        '''
        def replace():
            mod.sub_com.remove(old)
            self._return_old_cyberware(old)
            to_install = self._acquire_new_cyberware(new)
            mod.sub_com.append(to_install)
        return replace

    def _acquire_new_cyberware(self, cyberware):
        ''' Removes the cyberware from wherever it currently
        is so we can install it into the character.
        '''
        return self.source.acquire_cyberware(cyberware, self.camp)

    def _return_old_cyberware(self, cyberware):
        self.char.inv_com.append(cyberware)


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
        return '[Inv]'
    def get_panel_annotation(self, cyberware):
        return 'With {}'.format(self.char.name)
    def acquire_cyberware(self, cyberware, camp):
        self.char.inv_com.remove(cyberware)
        return cyberware
class StashSource(CyberwareSource):
    def __init__(self, stash):
        self.stash = stash
    def get_cyberware_list(self):
        rv = list()
        for cw in self.stash:
            if isinstance(cw, base.BaseCyberware):
                rv.append(cw)
        return rv
    def get_list_annotation(self, cyberware):
        return "[Stash]"
    def get_panel_annottion(self, cyberware):
        return "Stashed"
    def acquire_cyberware(self, cyberware, camp):
        self.stash.remove(cyberware)
        return cyberware

# Adaptor class, for existing interface.
class UI(CoreUI):
    def __init__(self, char, camp, stash = None, year = 158, **kwargs):
        if stash is None:
            stash = pbge.container.ContainerList(owner=self)
        sources = [ InventorySource(char)
                  , StashSource(stash)
                  ]
        super().__init__(char, _AggregateCyberwareSource(sources), camp, year)

