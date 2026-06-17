from pbge import frects
import sdl2
from sdl2 import ext

ext.init()

window = ext.Window("Hello World!", size=(640, 480))
window.show()
mysurf = window.get_surface()

myrect = frects.PyRect(50,50,100,100)

running = True
while running:
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False
            break
    ext.fill(window.get_surface(), ext.color.Color(0, 0, 0))
    sdl2.SDL_FillRect(mysurf, myrect, sdl2.SDL_MapRGB(mysurf.format, 0,200,255))
    window.refresh()


window.close()
ext.quit()

