if __name__ == '__main__':
    from source.meta.check_requirements import check_requirements
    check_requirements()

import json
import os
import sys
from tkinter import Tk, Button, BOTTOM, TOP, StringVar, BooleanVar, X, BOTH, RIGHT, ttk, messagebox

from CLI import get_args_priority
from DungeonRandomizer import parse_cli
from source.gui.adjust.overview import adjust_page
from source.gui.startinventory.overview import startinventory_page
from source.gui.custom.overview import custom_page
from source.gui.loadcliargs import loadcliargs, loadadjustargs
from source.gui.randomize.item import item_page
from source.gui.randomize.overworld import overworld_page
from source.gui.randomize.entrando import entrando_page
from source.gui.randomize.enemizer import enemizer_page
from source.gui.randomize.dungeon import dungeon_page
#from source.gui.randomize.multiworld import multiworld_page
from source.gui.randomize.gameoptions import gameoptions_page
from source.gui.randomize.generation import generation_page
from source.gui.bottom import bottom_frame, create_guiargs
from GuiUtils import set_icon
from Main import __version__ as ESVersion
from OverworldShuffle import __version__ as ORVersion

from source.classes.BabelFish import BabelFish
from source.classes.Empty import Empty


def check_python_version(fish):
    import sys
    version = sys.version_info
    if version.major < 3 or version.minor < 7:
        messagebox.showinfo("Overworld Shuffle %s (DR %s)" % (ORVersion, ESVersion), fish.translate("cli","cli","old.python.version") % sys.version)


# Save settings to file
def save_settings(gui, args, filename):
    user_resources_path = os.path.join(".", "resources", "user")
    settings_path = os.path.join(user_resources_path)
    if not os.path.exists(settings_path):
        os.makedirs(settings_path)
    output_args = {}
    settings = ["create_rom", "suppress_rom", "bps", "create_spoiler", "suppress_spoiler",
                "calc_playthrough", "skip_playthrough", "print_custom_yaml",
                "settingsonload", "rom", "enemizercli", "outputpath"]
    if filename == "settings.json":
        for s in settings:
            output_args[s] = args[s]
        for widget in gui.pages["adjust"].content.widgets:
            output_args["adjust." + widget] = gui.pages["adjust"].content.widgets[widget].storageVar.get()
    else:
        for k, v in args.items():
            if k not in settings and not k.startswith("adjust."):
                output_args[k] = v
    with open(os.path.join(settings_path, filename), "w+") as f:
        f.write(json.dumps(output_args, indent=2))
    os.chmod(os.path.join(settings_path, filename),0o755)

    
def guiMain(args=None):
    # Save settings from GUI
    def save_settings_from_gui(confirm):
        gui_args = vars(create_guiargs(self))
        if self.randomSprite.get():
            gui_args['sprite'] = 'random'
        elif gui_args['sprite']:
            gui_args['sprite'] = gui_args['sprite'].name
        save_settings(self, gui_args, "saved.json")
        save_settings(self, gui_args, "settings.json")
        if confirm:
            messagebox.showinfo("Overworld Shuffle " + ORVersion, "Settings saved from GUI.")

    # routine for exiting the app
    def guiExit():
        sys.exit(0)

    # make main window
    # add program title & version number
    mainWindow = Tk()
    self = mainWindow

    mainWindow.wm_title("Overworld Shuffle %s (DR %s)" % (ORVersion, ESVersion))
    mainWindow.protocol("WM_DELETE_WINDOW", guiExit)  # intercept when user clicks the X

    # set program icon
    set_icon(mainWindow)

    # get args
    # getting Settings & CLI (no GUI built yet)
    self.args = get_args_priority(None, None, None)
    lang = "en"
    if "load" in self.args and "lang" in self.args["load"]:
        lang = self.args["load"].lang
    self.fish = BabelFish(lang=lang)

    # get saved settings
    self.settings = vars(self.args["settings"])

    # make array for pages
    self.pages = {}

    # make array for frames
    self.frames = {}

    # make pages for each section
    self.notebook = ttk.Notebook(self)
    self.pages["randomizer"] = ttk.Frame(self.notebook)
    self.pages["adjust"] = ttk.Frame(self.notebook)
    self.pages["startinventory"] = ttk.Frame(self.notebook)
    self.pages["custom"] = ttk.Frame(self.notebook)
    self.notebook.add(self.pages["randomizer"], text='Randomize')
    self.notebook.add(self.pages["adjust"], text='Adjust/Patch')
    self.notebook.add(self.pages["startinventory"], text='Starting Inventory')
    self.notebook.add(self.pages["custom"], text='Custom Item Pool')
    self.notebook.pack()

    # randomizer controls

    # Randomize notebook page:
    #  make notebook pages: Item, Entrances, Enemizer, Dungeon Shuffle, Multiworld, Game Options, Generation Setup
    #   Item:             Item Randomizer settings
    #   Overworld:        Overworld Randomizer settings
    #   Entrances:        Entrance Randomizer settings
    #   Enemizer:         Enemy Randomizer settings
    #   Dungeon Shuffle:  Dungeon Door Randomizer settings
    #   Multiworld:       Multiworld settings
    #   Game Options:     Cosmetic settings that don't affect logic/placement
    #   Generation Setup: Primarily one&done settings
    self.pages["randomizer"].notebook = ttk.Notebook(self.pages["randomizer"])

    # make array for pages
    self.pages["randomizer"].pages = {}

    # Item Randomizer
    self.pages["randomizer"].pages["item"] = item_page(self.pages["randomizer"].notebook)
    self.pages["randomizer"].notebook.add(self.pages["randomizer"].pages["item"], text="Items")

    # Overworld Randomizer
    self.pages["randomizer"].pages["overworld"] = overworld_page(self.pages["randomizer"].notebook)
    self.pages["randomizer"].notebook.add(self.pages["randomizer"].pages["overworld"], text="Overworld")

    # Entrance Randomizer
    self.pages["randomizer"].pages["entrance"] = entrando_page(self.pages["randomizer"].notebook)
    self.pages["randomizer"].notebook.add(self.pages["randomizer"].pages["entrance"], text="Entrances")

    # Dungeons
    self.pages["randomizer"].pages["dungeon"] = dungeon_page(self.pages["randomizer"].notebook)
    self.pages["randomizer"].notebook.add(self.pages["randomizer"].pages["dungeon"], text="Dungeons")

    # Enemizer
    self.pages["randomizer"].pages["enemizer"],self.settings = enemizer_page(self.pages["randomizer"].notebook,self.settings)
    self.pages["randomizer"].notebook.add(self.pages["randomizer"].pages["enemizer"], text="Enemizer")

    # Multiworld
#    self.pages["randomizer"].pages["multiworld"],self.settings = multiworld_page(self.pages["randomizer"].notebook,self.settings)
#    self.pages["randomizer"].notebook.add(self.pages["randomizer"].pages["multiworld"], text="Multiworld")

    # Game Options
    self.pages["randomizer"].pages["gameoptions"] = gameoptions_page(self, self.pages["randomizer"].notebook)
    self.pages["randomizer"].notebook.add(self.pages["randomizer"].pages["gameoptions"], text="Game Options")

    # Generation Setup
    self.pages["randomizer"].pages["generation"],self.settings = generation_page(self.pages["randomizer"].notebook,self.settings)
    self.pages["randomizer"].notebook.add(self.pages["randomizer"].pages["generation"], text="Generation Setup")

    # add randomizer notebook to main window
    self.pages["randomizer"].notebook.pack()

    # bottom of window: Open Output Directory, Open Documentation (if exists)
    self.pages["bottom"] = Empty()
    self.pages["bottom"].pages = {}
    self.pages["bottom"].pages["content"] = bottom_frame(self, self, None)
    ## Save Settings Button
    savesettingsButton = self.pages["bottom"].pages["content"].widgets["savesettings"].pieces["button"]
    savesettingsButton.configure(command=lambda: save_settings_from_gui(True))

    # set bottom frame to main window
    self.pages["bottom"].pages["content"].pack(side=BOTTOM, fill=X, padx=5, pady=5)

    self.outputPath = StringVar()
    self.randomSprite = BooleanVar()

    # Adjuster Controls
    self.pages["adjust"].content,self.settings = adjust_page(self, self.pages["adjust"], self.settings)
    self.pages["adjust"].content.pack(side=TOP, fill=BOTH, expand=True)

    # Starting Inventory Controls
    self.pages["startinventory"].content = startinventory_page(self, self.pages["startinventory"])
    self.pages["startinventory"].content.pack(side=TOP, fill=BOTH, expand=True)

    # Custom Controls
    self.pages["custom"].content = custom_page(self, self.pages["custom"])
    self.pages["custom"].content.pack(side=TOP, fill=BOTH, expand=True)

    def validation(P):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False
    vcmd=(self.pages["custom"].content.register(validation), '%P')

    # load args
    loadcliargs(self, self.args["load"])

    # load adjust settings into options
    loadadjustargs(self, self.settings)

    check_python_version(self.fish)

    # run main window
    mainWindow.mainloop()


if __name__ == '__main__':
    args = parse_cli(None)
    guiMain(args)
