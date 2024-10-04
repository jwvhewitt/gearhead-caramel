from .. import my_state, wait_event, TIMEREVENT
import pygame
import random


COLORS = (
    pygame.Color(150, 150, 105),
    pygame.Color(250, 0, 0),
    pygame.Color(0, 250, 0),
    pygame.Color(0, 0, 250),
    pygame.Color(250, 250, 0),
    pygame.Color(0, 250, 250),
    pygame.Color(250, 0, 250)
)

class DebugViewer:
    def __init__(self, myscene, myscenegen):
        self.myscene = myscene
        self.myscenegen = myscenegen
        self.room_color = dict()
        self._map = None
        for n, r in enumerate(myscenegen.all_rooms()):
            self.room_color[r] = n % (len(COLORS) - 1) + 1
        self.prep_map()

    def prep_map(self):
        self._map = [[list(('.', 0))
                      for _y in range(self.myscene.height)]
                     for _x in range(self.myscene.width)]
        for x in range(self.myscene.width):
            for y in range(self.myscene.height):
                if self.myscene.get_wall(x, y):
                    self._map[x][y][0] = "#"
                myroom = self.myscene.get_visible(x,y)
                if myroom:
                    self._map[x][y][1] = self.room_color.setdefault(myroom, random.randint(1,6))

    def __call__(self):
        my_state.screen.fill((0, 0, 0))

        for x in range(self.myscene.width):
            for y in range(self.myscene.height):
                mydest = pygame.Rect(x*12, y*12, 12, 12)
                my_surf = my_state.tiny_font.render(self._map[x][y][0], True, COLORS[self._map[x][y][1]])
                my_state.screen.blit(my_surf, mydest)

    @classmethod
    def test_map_generation(cls, myscene, myscenegen):
        myscene.DEBUG = True
        my_view = cls(myscene, myscenegen)

        gb = True
        for gb in myscenegen.make():
            my_view.prep_map()
            keep_going = bool(gb)
            while keep_going:
                gdi = wait_event()
                if gdi.type == TIMEREVENT:
                    my_view()
                    my_state.do_flip()
                elif gdi.type == pygame.KEYDOWN and gdi.key == pygame.K_SPACE:
                    keep_going = False

