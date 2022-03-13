import pygame

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


