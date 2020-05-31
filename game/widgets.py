import pbge
import pygame

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
                , on_enter = None, on_leave = None, on_select = None
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
        self.on_select = on_select

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
        if self.on_select:
            self.on_select(self.current_item)

