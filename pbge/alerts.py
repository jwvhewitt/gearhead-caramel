import sdl2

from pbge import fontstyles
from . import widgets, my_state, image, default_border, frects


WTAG_ALERT = "WTAG_ALERT"
ALERT_EVENT = sdl2.SDL_RegisterEvents(1)

# Alerts are meant to display narration and other info for the player.
# Often we want to display several alerts in a row, as in when NPCs are speaking
# or there's ongoing narration.
# So alerts, when created, get added to an alert queue.
# If the queue has any alerts, and no alerts are active, the first alerts deployed.
# Alerts disable other widgets while they're active.
# When the alert pops, the other widgets get re-enabled, and maybe a new alert from
# the queue will be deployed.

class AbstractAlert(widgets.Widget):
    def __init__(self, dx=0, dy=0, w=0, h=0, on_close: widgets.On_Click=None, data=None):
        super().__init__(dx,dy,w,h, tags={WTAG_ALERT}, data=data)
        self.on_close = on_close
        my_state.alert_queue.append(self)

    # When an alert arrives, everything else gets deactivated. Bwa ha ha!
    TAGS_TO_DEACTIVATE = {widgets.WTAG_WIDGET,}

    def _builtin_responder(self, ev):
        if (ev.type == sdl2.SDL_MOUSEBUTTONUP):
            self.register_response()
            self.pop()
            if self.on_close:
                self.on_close(self, ev)
            my_state.update_alerts()
        elif (ev.type == sdl2.SDL_KEYDOWN):
            if my_state.is_key_for_action(ev, "exit") or my_state.is_key_for_action(ev, "select"):
                self.register_response()
                self.pop()
                if self.on_close:
                    self.on_close(self, ev)
                my_state.update_alerts()

    def _render(self, _delta):
        raise NotImplementedError("AbstractAlert cannot be displayed; that's what makes it art.")


class TextAlert(AbstractAlert):
    def __init__(self, text, font=None,  align=fontstyles.ALIGN_CENTER, **kwargs):
        super().__init__(**kwargs)
        if not font:
            font = fontstyles.MEDIUMFONT
        self.text_image = image.TextImage(text, frame_width=400, style=font, align=align)
        w,h = self.text_image.size
        self.dest = frects.Frect(-w/2, -h/2, w, h)

    def _render(self, _delta):
        mydest = self.dest.get_rect()
        default_border.render(mydest)
        self.text_image.render(mydest)


class FunAlert(AbstractAlert):
    def __init__(self, display_fun, **kwargs):
        # display_fun is a callable with no parameters. It is the display.
        super().__init__(**kwargs)
        self.display_fun = display_fun

    def _render(self, _delta):
        # Just call the display fun. That's what makes this alert so fun.
        self.display_fun()


class AnimAlert(AbstractAlert):
    # An alert that deploys animations and waits for them to finish.
    # Waits an extra half a second for emphasis.
    def __init__(self, *anim_list, **kwargs):
        # display_fun is a callable with no parameters. It is the display.
        super().__init__(**kwargs)
        self.anim_list = anim_list
        self.timer = 500

    def _render(self, delta):
        # Just call the display fun. That's what makes this alert so fun.
        if self.anim_list:
            my_state.view.play_anims(*self.anim_list)
            self.anim_list = None
        elif not my_state.view.has_animations():
            self.timer -= delta
            if self.timer <= 0:
                self.register_response()
                self.pop()
                if self.on_close:
                    self.on_close(self, sdl2.SDL_Event(ALERT_EVENT, {}))
                my_state.update_alerts()

    def _builtin_responder(self, ev):
        if not my_state.view.has_animations() and not self.anim_list:
            super()._builtin_responder(ev)


class InvocationAlert(AnimAlert):
    def __init__(self, invo, camp, originator, target_points, invo_data=None, **kwargs):
        anim_list = list()
        invo.invoke(camp, originator, target_points, anim_list, data=invo_data)
        super().__init__(*anim_list, **kwargs)


