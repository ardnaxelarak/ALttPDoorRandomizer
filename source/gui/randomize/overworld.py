from tkinter import ttk, Frame, Label, W, E, NW, LEFT, RIGHT, X, Y, TOP
import source.gui.widgets as widgets
import json
import os

def overworld_page(parent):
    # Overworld Shuffle
    self = ttk.Frame(parent)

    # Overworld Shuffle options
    self.widgets = {}

    # Overworld Shuffle option sections
    self.frames = {}

    # Load Overworld Shuffle option widgets as defined by JSON file
    # Defns include frame name, widget type, widget options, widget placement attributes
    # These get split left & right
    self.frames["leftOverworldFrame"] = Frame(self)
    self.frames["rightOverworldFrame"] = Frame(self)

    self.frames["leftOverworldFrame"].pack(side=LEFT, anchor=NW, fill=Y)
    self.frames["rightOverworldFrame"].pack(anchor=NW, fill=Y)
    
    with open(os.path.join("resources","app","gui","randomize","overworld","widgets.json")) as overworldWidgets:
        myDict = json.load(overworldWidgets)
        for framename,theseWidgets in myDict.items():
            dictWidgets = widgets.make_widgets_from_dict(self, theseWidgets, self.frames[framename])
            for key in dictWidgets:
                self.widgets[key] = dictWidgets[key]
                packAttrs = {"anchor":E}
                if key == "keepsimilar":
                    packAttrs = {"side":LEFT, "pady":(18,0)}
                elif key == "overworldflute":
                    packAttrs["pady"] = (20,0)
                elif key in ["whirlpool", "mixed"]:
                    packAttrs = {"anchor":W, "padx":(79,0)}
                
                self.widgets[key].pack(packAttrs)

    return self
