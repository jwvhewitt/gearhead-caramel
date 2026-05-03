from . import tkvarwidgets
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

class ScrolledFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=5, )
        _=self.columnconfigure(0, weight=1)
        _=self.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(self, background="#CCFFFF")
        self.content = ttk.Frame(self.canvas, padding=5)
        _=self.content.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        _=self.canvas.create_window(0,0,anchor=tk.NW, window=self.content)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview,)
        _=self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nswe")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
    #     _=self.bind("<<gh_scroll>>", self._on_scroll)

    # def _on_scroll(self, ev: tk.Event):
    #     g = self.winfo_geometry()
    #     x, y = ev.x, ev.y
    #     print(g)
    #     print("Virtual!")



class PhysicalEditor(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, borderwidth=2, relief="raised")
        _=self.columnconfigure(0, weight=1)
        _=self.columnconfigure(2, weight=2, minsize=700)
        _=self.rowconfigure(0, weight=1)

        sf1 = ScrolledFrame(self)
        self.tree_canvas = sf1.canvas
        self.tree_frame = sf1.content

        my_separator = ttk.Separator(self, orient="vertical")
        self.edit_canvas = tk.Canvas(self, width=640)
    
        sf1.grid(row=0, column=0, sticky="nswe")
        my_separator.grid(row=0, column=1, sticky="ns")
        self.edit_canvas.grid(row=0, column=2, sticky="ns")

        for t in range(100):
            label = ttk.Button(self.tree_frame, text="Line {}".format(t+1))
            label.grid()


