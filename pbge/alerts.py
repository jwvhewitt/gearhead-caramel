import pygame
from . import widgets, my_state, render_text, default_border, frects


WTAG_ALERT = "WTAG_ALERT"

# Alerts are meant to display narration and other info for the player.
# Often we want to display several alerts in a row, as in when NPCs are speaking
# or there's ongoing narration.
# So alerts, when created, get added to an alert queue.
# If the queue has any alerts, and no alerts are active, the first alerts deployed.
# Alerts disable other widgets while they're active.
# When the alert pops, the other widgets get re-enabled, and maybe a new alert from
# the queue will be deployed.

class AbstractAlert(widgets.Widget):
    def __init__(self, dx=0, dy=0, w=0, h=0, on_close: widgets.On_Click=None):
        super().__init__(dx,dy,w,h, tags={WTAG_ALERT}, )
        self.on_close = on_close
        my_state.alert_queue.append(self)

    # When an alert arrives, everything else gets deactivated. Bwa ha ha!
    TAGS_TO_DEACTIVATE = {widgets.WTAG_WIDGET,}

    def _builtin_responder(self, ev):
        if (ev.type == pygame.MOUSEBUTTONUP):
            if self.on_close:
                self.on_close(self, ev)
            self.register_response()
            self.pop()
            my_state.update_alerts()
        elif (ev.type == pygame.KEYDOWN):
            if my_state.is_key_for_action(ev, "exit") or my_state.is_key_for_action(ev, "select"):
                if self.on_close:
                    self.on_close(self, ev)
                self.register_response()
                self.pop()
                my_state.update_alerts()

    def _render(self, _delta):
        raise NotImplementedError("AbstractAlert cannot be displayed; that's what makes it art.")


class TextAlert(AbstractAlert):
    def __init__(self, text, font=None, justify=-1, **kwargs):
        super().__init__(**kwargs)
        if not font:
            font = my_state.medium_font
        self.text_surf = render_text(font, text, 400, justify=justify)
        w,h = self.text_surf.get_size()
        self.dest = frects.Frect(-w/2, -h/2, w, h)

    def _render(self, _delta):
        mydest = self.dest.get_rect()
        default_border.render(mydest)
        _=my_state.screen.blit(self.text_surf, mydest)


class FunAlert(AbstractAlert):
    def __init__(self, display_fun, **kwargs):
        # display_fun is a callable with no parameters. It is the display.
        super().__init__(**kwargs)
        self.display_fun = display_fun

    def _render(self, _delta):
        # Just call the display fun. That's what makes this alert so fun.
        self.display_fun()

