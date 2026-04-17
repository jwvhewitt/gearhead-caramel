import game
import gears
import pbge
import sys
import os
import editor

#from pbge.widgets import On_Click


# Step one is to find our gamedir. The process is slightly different depending on whether we are running from
# source, running from a PyInstaller build, or running from a cx_Freeze build.
if getattr(sys, "_MEIPASS", False):
    # PyInstaller build.
    gamedir = sys._MEIPASS
    neargamedir = os.path.dirname(sys.argv[0])
elif getattr(sys, "frozen", False):
    # cx_Freeze build.
    gamedir = os.path.dirname(sys.executable)
    neargamedir = gamedir
else:
    # The application is not frozen
    gamedir = os.path.dirname(__file__)
    #neargamedir = gamedir
    neargamedir = os.path.dirname(sys.argv[0])

print(gamedir)
print(neargamedir)

pbge.init('GearHead Caramel', 'ghcaramel', gamedir, poster_pattern='eyecatch_*.png', start_gfx=False)
from main import VERSION

# PyGame Surface to WX bitmap:
# bmp = wx.BitmapFromBufferRGB( surface.get_width(), surface.get_height(), surface.get_buffer() )
# wx.BitmapFromBufferRGBA must be used if the surface contains per pixel alpha data.
# From PyGame wiki

if __name__ == "__main__":
    print("We got this far, didn't we?")
    # Been getting some problems with the program continuing to run sometimes after pygame.quit().
    # StackExchange suggested the following... I figure it couldn't hurt.
    sys.exit()

