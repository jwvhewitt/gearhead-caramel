import pygame
from pbge import my_state

class MapCursor(object):
    def __init__(self, x, y, image, frame=0, visible=True):
        self.x = x
        self.y = y
        self.image = image
        self.frame = frame
        self.visible = visible

    def render(self, dest: pygame.Rect):
        if self.visible:
            self.image.render(dest, self.frame)

    def set_position(self, scene, x, y, must_be_visible=True):
        if scene.on_the_map(x, y) and (scene.get_visible(x, y) or not must_be_visible):
            self.x, self.y = x, y

    def update(self, view, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.set_position(view.scene, *view._mouse_tile)
        elif ev.type == pygame.KEYDOWN:
            if ev.key in my_state.get_keys_for("cursor_up"):
                self.set_position(view.scene, self.x-1, self.y-1)
                view.focus(self.x, self.y)
            elif ev.key in my_state.get_keys_for("cursor_upright"):
                self.set_position(view.scene, self.x, self.y-1)
                view.focus(self.x, self.y)
            elif ev.key in my_state.get_keys_for("cursor_right"):
                self.set_position(view.scene, self.x+1, self.y-1)
                view.focus(self.x, self.y)
            elif ev.key in my_state.get_keys_for("cursor_downright"):
                self.set_position(view.scene, self.x+1, self.y)
                view.focus(self.x, self.y)
            elif ev.key in my_state.get_keys_for("cursor_down"):
                self.set_position(view.scene, self.x+1, self.y+1)
                view.focus(self.x, self.y)
            elif ev.key in my_state.get_keys_for("cursor_downleft"):
                self.set_position(view.scene, self.x, self.y+1)
                view.focus(self.x, self.y)
            elif ev.key in my_state.get_keys_for("cursor_left"):
                self.set_position(view.scene, self.x-1, self.y+1)
                view.focus(self.x, self.y)
            elif ev.key in my_state.get_keys_for("cursor_upleft"):
                self.set_position(view.scene, self.x-1, self.y)
                view.focus(self.x, self.y)


