import pbge
import sdl2
from sdl2 import ext
import os

gamedir = os.path.dirname(__file__)

pbge.init('GearHead Caramel', 'ghcaramel', gamedir, poster_pattern='eyecatch_*.png')
pbge.please_stand_by()

myrect = pbge.frects.PyRect(50,50,100,100)

mybutton = pbge.widgets.LabelWidget(-100,-50,200,100,"Testing the label widget", draw_border=True)
mybutton.activate()

pbge.my_state.widgets.append(mybutton)
mybutton.activate()

class SpeedTest(pbge.widgets.Widget):
    ITERATIONS = 10000
    TAGS_TO_HIDE = {pbge.widgets.WTAG_TITLEMENU,}
    ACTIVATE_IMMEDIATELY = True

    def __init__(self):
        super().__init__(0, 0, 1280, 720)
        self.sprite = pbge.image.Image("terrain_decor_bed.png")

    def draw_individual(self):
        mydest = pbge.frects.PyRect(0,360 + pbge.my_state.anim_phase%200,64,64)
        for t in range(self.ITERATIONS):
            self.sprite.render(mydest)
            mydest.x += 5
            if mydest.x > 1260:
                mydest.x = 0
                mydest.y += 5

    def _render(self, _delta):
        self.draw_individual()

    def _builtin_responder(self, ev):
        if ev.type == sdl2.SDL_MOUSEBUTTONUP:
            if ev.button == 1:
                self.register_response()
                self.pop()

        elif ev.type == sdl2.SDL_KEYDOWN:
            self.register_response()
            self.pop()

pbge.my_state.widgets.append(SpeedTest())


pbge.my_state.play()


# running = True
# while running:
#     events = sdl2.ext.get_events()
#     for event in events:
#         if event.type == sdl2.SDL_QUIT:
#             running = False
#             break
#     ext.fill(window.get_surface(), ext.color.Color(0, 0, 0))
#     sdl2.SDL_FillRect(mysurf, myrect, sdl2.SDL_MapRGB(mysurf.format, 0,200,255))
#     window.refresh()



pbge.quit()

