import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from pygame import color

VAR_BORDER = dict(padding=5, borderwidth=2, relief="raised")

class StringVarEditorWidget(ttk.Frame):
    def __init__(self, master, part, key):
        super().__init__(master, **VAR_BORDER)  # pyright: ignore[reportArgumentType]
        self.part = part
        self.key = key

        self.my_string = tk.StringVar(value="")
        _=self.my_string.trace_add("write", self._do_change)

        my_label = ttk.Label(self, text=key)
        # my_spacer = ttk.Frame(self, width=5, height=5)
        my_entry = ttk.Entry(self, textvariable=self.my_string, width=64, justify="center")

        # my_label.grid(column=0, row=0)
        # my_spacer.grid(column=1, row=0)
        # my_entry.grid(column=2, row=0)
        my_label.pack(side=tk.LEFT)
        my_entry.pack(side=tk.RIGHT)

    def _do_change(self, *_args):
        #self.part.raw_vars[self.key] = self.my_string.get()
        print("{}: {}".format(self.key, self.my_string.get()))


class CampaignVarNameWidget(ttk.Frame):
    def __init__(self, master, part, var_name, **kwargs):
        super().__init__(master, **VAR_BORDER)  # pyright: ignore[reportArgumentType]
        self.part = part
        self.var_name = var_name

        self.my_string = tk.StringVar(value=str(part.raw_vars.get(var_name, "x")))
        _=self.my_string.trace_add("write", self._do_change)

        my_label = ttk.Label(self, text=var_name)
        my_entry = ttk.Combobox(
            self, textvariable=self.my_string, width=64, justify="center", 
            values=[cvn for cvn in self.part.get_campaign_variable_names()]
        )

        my_label.pack(side=tk.LEFT)
        my_entry.pack(side=tk.RIGHT)

    def _do_change(self, *_args):
        self.part.raw_vars[self.var_name] = self.my_string.get()


class TextVarEditorWidget(ttk.Frame):
    def __init__(self, master, part, var_name, default_value):
        super().__init__(master, **VAR_BORDER)  # pyright: ignore[reportArgumentType]
        self.part = part
        self.var_name = var_name

        my_label = ttk.Label(self, text=var_name)
        self.my_text = ScrolledText(self, width=72, wrap="word", height=5)
        # Bind the <<Modified>> event to the text widget
        _=self.my_text.bind("<<Modified>>", self._do_change)

        my_label.pack()
        self.my_text.pack()

    def _do_change(self, *_args):
        self.part.raw_vars[self.var_name] = self.my_text.get("1.0", "end-1c")
        self.my_text.edit_modified(False)  # Reset the modified flag

