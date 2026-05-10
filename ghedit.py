import game
import gears
import pbge
import sys
import os
import editor
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
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

class GearHeadEditor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GearHead Caramel Scenario Editor")
        self.geometry("1280x720")
        self.option_add('*tearOff', False)
        _=self.columnconfigure(0, weight=1)
        _=self.rowconfigure(0, weight=1)


if __name__ == "__main__":
    root = GearHeadEditor()

    # content = ttk.Frame(root)
    # content.grid(sticky="nswe")
    # _=content.columnconfigure(0, pad=10)

    widget = editor.PhysicalEditor(root)
    widget.grid(sticky="nswe")

    # def on_text_change(event):
    #     """Function to handle text changes."""
    #     text_content = text_widget.get("1.0", "end-1c")  # Get the current text
    #     print("Current text:", text_content)
        
    #     text_widget.edit_modified(False)  # Reset the modified flag

    # svew = editor.tkvarwidgets.StringVarEditorWidget(content, dict(), "Color")
    # svew.grid(column=0, sticky="we", padx=10, pady=10,)

    # # Create a Text widget
    # text_widget = ScrolledText(content, width=72, wrap="word", height=5)
    # text_widget.grid(column=0, padx=10, pady=10)

    # # Bind the <<Modified>> event to the text widget
    # _=text_widget.bind("<<Modified>>", on_text_change)

    # Run the Tkinter event loop
    root.mainloop()

    # Been getting some problems with the program continuing to run sometimes after pygame.quit().
    # StackExchange suggested the following... I figure it couldn't hurt.
    sys.exit()

