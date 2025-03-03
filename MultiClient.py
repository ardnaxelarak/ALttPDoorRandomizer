import aioconsole
import argparse
import asyncio
import colorama
import json
import logging
import shlex
import urllib.parse
import websockets
from websockets.extensions.permessage_deflate import ClientPerMessageDeflateFactory

from BaseClasses import PotItem, PotFlags
import Items
import Regions
import PotShuffle


class ReceivedItem:
    def __init__(self, item, location, player):
        self.item = item
        self.location = location
        self.player = player

class Context:
    def __init__(self, snes_address, server_address, password):
        self.snes_address = snes_address
        self.server_address = server_address

        self.exit_event = asyncio.Event()
        self.watcher_event = asyncio.Event()

        self.input_queue = asyncio.Queue()
        self.input_requests = 0

        self.snes_socket = None
        self.snes_state = SNES_DISCONNECTED
        self.snes_attached_device = None
        self.snes_reconnect_address = None
        self.snes_recv_queue = asyncio.Queue()
        self.snes_request_lock = asyncio.Lock()
        self.is_sd2snes = False
        self.snes_write_buffer = []

        self.server_task = None
        self.socket = None
        self.password = password

        self.team = None
        self.slot = None
        self.player_names = {}
        self.locations_checked = set()
        self.locations_scouted = set()
        self.items_received = []
        self.locations_info = {}
        self.awaiting_rom = False
        self.rom = None
        self.auth = None
        self.total_locations = None
        self.mode_flags = None
        self.key_drop_mode = False
        self.shop_mode = False
        self.retro_mode = False
        self.pottery_mode = False
        self.mystery_mode = False
        self.ignore_count = 0

        self.lookup_name_to_id = {}
        self.lookup_id_to_name = {}

        self.pottery_locations_enabled = None

def color_code(*args):
    codes = {'reset': 0, 'bold': 1, 'underline': 4, 'black': 30, 'red': 31, 'green': 32, 'yellow': 33, 'blue': 34,
             'magenta': 35, 'cyan': 36, 'white': 37 , 'black_bg': 40, 'red_bg': 41, 'green_bg': 42, 'yellow_bg': 43,
             'blue_bg': 44, 'purple_bg': 45, 'cyan_bg': 46, 'white_bg': 47}
    return '\033[' + ';'.join([str(codes[arg]) for arg in args]) + 'm'

def color(text, *args):
    return color_code(*args) + text + color_code('reset')

RECONNECT_DELAY = 30

ROM_START = 0x000000
WRAM_START = 0xF50000
WRAM_SIZE = 0x20000
SRAM_START = 0xE00000

ROMNAME_START = SRAM_START + 0x2000
ROMNAME_SIZE = 0x15

INGAME_MODES = {0x07, 0x09, 0x0b}

SAVEDATA_START = WRAM_START + 0xF000
SAVEDATA_SIZE = 0x500

POT_ITEMS_SRAM_START = WRAM_START + 0x016018        # 2 bytes per room
SPRITE_ITEMS_SRAM_START = WRAM_START + 0x016268     # 2 bytes per room
SHOP_SRAM_START = WRAM_START + 0x0164B8             # 2 bytes?
ITEM_SRAM_SIZE = 0x250
SHOP_SRAM_LEN = 0x29  # 41 tracked items

POT_LOCATION_TABLE = 0x142A60

RECV_PROGRESS_ADDR = SAVEDATA_START + 0x4D0         # 2 bytes
RECV_ITEM_ADDR = SAVEDATA_START + 0x4D2             # 1 byte
RECV_ITEM_PLAYER_ADDR = SAVEDATA_START + 0x4D3      # 1 byte
ROOMID_ADDR = SAVEDATA_START + 0x4D4                # 2 bytes
ROOMDATA_ADDR = SAVEDATA_START + 0x4D6              # 1 byte
SCOUT_LOCATION_ADDR = SAVEDATA_START + 0x4D7        # 1 byte
SCOUTREPLY_LOCATION_ADDR = SAVEDATA_START + 0x4D8   # 1 byte
SCOUTREPLY_ITEM_ADDR = SAVEDATA_START + 0x4D9       # 1 byte
SCOUTREPLY_PLAYER_ADDR = SAVEDATA_START + 0x4DA     # 1 byte
DYNAMIC_TOTAL_ADDR = SAVEDATA_START + 0x33E         # 2 bytes
MODE_FLAGS = SAVEDATA_START + 0x33D         # 1 byte

location_shop_order = [Regions.shop_to_location_table.keys()] + [Regions.retro_shops.keys()]
location_shop_ids = {0x0112, 0x0110, 0x010F, 0x00FF, 0x011F, 0x0109, 0x0115}

location_table_uw = {"Blind's Hideout - Top": (0x11d, 0x10),
                     "Blind's Hideout - Left": (0x11d, 0x20),
                     "Blind's Hideout - Right": (0x11d, 0x40),
                     "Blind's Hideout - Far Left": (0x11d, 0x80),
                     "Blind's Hideout - Far Right": (0x11d, 0x100),
                     'Secret Passage': (0x55, 0x10),
                     'Waterfall Fairy - Left': (0x114, 0x10),
                     'Waterfall Fairy - Right': (0x114, 0x20),
                     "King's Tomb": (0x113, 0x10),
                     'Floodgate Chest': (0x10b, 0x10),
                     "Link's House": (0x104, 0x10),
                     'Kakariko Tavern': (0x103, 0x10),
                     'Chicken House': (0x108, 0x10),
                     "Aginah's Cave": (0x10a, 0x10),
                     "Sahasrahla's Hut - Left": (0x105, 0x10),
                     "Sahasrahla's Hut - Middle": (0x105, 0x20),
                     "Sahasrahla's Hut - Right": (0x105, 0x40),
                     'Kakariko Well - Top': (0x2f, 0x10),
                     'Kakariko Well - Left': (0x2f, 0x20),
                     'Kakariko Well - Middle': (0x2f, 0x40),
                     'Kakariko Well - Right': (0x2f, 0x80),
                     'Kakariko Well - Bottom': (0x2f, 0x100),
                     'Lost Woods Hideout': (0xe1, 0x200),
                     'Lumberjack Tree': (0xe2, 0x200),
                     'Cave 45': (0x11b, 0x400),
                     'Graveyard Cave': (0x11b, 0x200),
                     'Checkerboard Cave': (0x126, 0x200),
                     'Mini Moldorm Cave - Far Left': (0x123, 0x10),
                     'Mini Moldorm Cave - Left': (0x123, 0x20),
                     'Mini Moldorm Cave - Right': (0x123, 0x40),
                     'Mini Moldorm Cave - Far Right': (0x123, 0x80),
                     'Mini Moldorm Cave - Generous Guy': (0x123, 0x400),
                     'Ice Rod Cave': (0x120, 0x10),
                     'Cold Fairy Statue': (0x120, 0x200),
                     'Bonk Rock Cave': (0x124, 0x10),
                     'Desert Palace - Big Chest': (0x73, 0x10),
                     'Desert Palace - Torch': (0x73, 0x400),
                     'Desert Palace - Map Chest': (0x74, 0x10),
                     'Desert Palace - Compass Chest': (0x85, 0x10),
                     'Desert Palace - Big Key Chest': (0x75, 0x10),
                     'Desert Palace - Desert Tiles 1 Pot Key': (0x63, 0x400),
                     'Desert Palace - Beamos Hall Pot Key': (0x53, 0x400),
                     'Desert Palace - Desert Tiles 2 Pot Key': (0x43, 0x400),
                     'Desert Palace - Boss': (0x33, 0x800),
                     'Eastern Palace - Compass Chest': (0xa8, 0x10),
                     'Eastern Palace - Big Chest': (0xa9, 0x10),
                     'Eastern Palace - Dark Square Pot Key': (0xba, 0x400),
                     'Eastern Palace - Dark Eyegore Key Drop': (0x99, 0x400),
                     'Eastern Palace - Cannonball Chest': (0xb9, 0x10),
                     'Eastern Palace - Big Key Chest': (0xb8, 0x10),
                     'Eastern Palace - Map Chest': (0xaa, 0x10),
                     'Eastern Palace - Boss': (0xc8, 0x800),
                     'Hyrule Castle - Boomerang Chest': (0x71, 0x10),
                     'Hyrule Castle - Boomerang Guard Key Drop': (0x71, 0x400),
                     'Hyrule Castle - Map Chest': (0x72, 0x10),
                     'Hyrule Castle - Map Guard Key Drop': (0x72, 0x400),
                     "Hyrule Castle - Zelda's Chest": (0x80, 0x10),
                     'Hyrule Castle - Big Key Drop': (0x80, 0x400),
                     'Sewers - Dark Cross': (0x32, 0x10),
                     'Hyrule Castle - Key Rat Key Drop': (0x21, 0x400),
                     'Sewers - Secret Room - Left': (0x11, 0x10),
                     'Sewers - Secret Room - Middle': (0x11, 0x20),
                     'Sewers - Secret Room - Right': (0x11, 0x40),
                     'Sanctuary': (0x12, 0x10),
                     'Castle Tower - Room 03': (0xe0, 0x10),
                     'Castle Tower - Dark Maze': (0xd0, 0x10),
                     'Castle Tower - Dark Archer Key Drop': (0xc0, 0x400),
                     'Castle Tower - Circle of Pots Key Drop': (0xb0, 0x400),
                     'Spectacle Rock Cave': (0xea, 0x400),
                     'Paradox Cave Lower - Far Left': (0xef, 0x10),
                     'Paradox Cave Lower - Left': (0xef, 0x20),
                     'Paradox Cave Lower - Right': (0xef, 0x40),
                     'Paradox Cave Lower - Far Right': (0xef, 0x80),
                     'Paradox Cave Lower - Middle': (0xef, 0x100),
                     'Paradox Cave Upper - Left': (0xff, 0x10),
                     'Paradox Cave Upper - Right': (0xff, 0x20),
                     'Spiral Cave': (0xfe, 0x10),
                     'Tower of Hera - Basement Cage': (0x87, 0x400),
                     'Tower of Hera - Map Chest': (0x77, 0x10),
                     'Tower of Hera - Big Key Chest': (0x87, 0x10),
                     'Tower of Hera - Compass Chest': (0x27, 0x20),
                     'Tower of Hera - Big Chest': (0x27, 0x10),
                     'Tower of Hera - Boss': (0x7, 0x800),
                     'Hype Cave - Top': (0x11e, 0x10),
                     'Hype Cave - Middle Right': (0x11e, 0x20),
                     'Hype Cave - Middle Left': (0x11e, 0x40),
                     'Hype Cave - Bottom': (0x11e, 0x80),
                     'Hype Cave - Generous Guy': (0x11e, 0x400),
                     'Peg Cave': (0x127, 0x400),
                     'Pyramid Fairy - Left': (0x116, 0x10),
                     'Pyramid Fairy - Right': (0x116, 0x20),
                     'Brewery': (0x106, 0x10),
                     'C-Shaped House': (0x11c, 0x10),
                     'Chest Game': (0x106, 0x400),
                     'Mire Shed - Left': (0x10d, 0x10),
                     'Mire Shed - Right': (0x10d, 0x20),
                     'Superbunny Cave - Top': (0xf8, 0x10),
                     'Superbunny Cave - Bottom': (0xf8, 0x20),
                     'Spike Cave': (0x117, 0x10),
                     'Hookshot Cave - Top Right': (0x3c, 0x10),
                     'Hookshot Cave - Top Left': (0x3c, 0x20),
                     'Hookshot Cave - Bottom Right': (0x3c, 0x80),
                     'Hookshot Cave - Bottom Left': (0x3c, 0x40),
                     'Mimic Cave': (0x10c, 0x10),
                     'Swamp Palace - Entrance': (0x28, 0x10),
                     'Swamp Palace - Map Chest': (0x37, 0x10),
                     'Swamp Palace - Pot Row Pot Key': (0x38, 0x400),
                     'Swamp Palace - Trench 1 Pot Key': (0x37, 0x400),
                     'Swamp Palace - Hookshot Pot Key': (0x36, 0x400),
                     'Swamp Palace - Big Chest': (0x36, 0x10),
                     'Swamp Palace - Compass Chest': (0x46, 0x10),
                     'Swamp Palace - Trench 2 Pot Key': (0x35, 0x400),
                     'Swamp Palace - Big Key Chest': (0x35, 0x10),
                     'Swamp Palace - West Chest': (0x34, 0x10),
                     'Swamp Palace - Flooded Room - Left': (0x76, 0x10),
                     'Swamp Palace - Flooded Room - Right': (0x76, 0x20),
                     'Swamp Palace - Waterfall Room': (0x66, 0x10),
                     'Swamp Palace - Waterway Pot Key': (0x16, 0x400),
                     'Swamp Palace - Boss': (0x6, 0x800),
                     "Thieves' Town - Big Key Chest": (0xdb, 0x20),
                     "Thieves' Town - Map Chest": (0xdb, 0x10),
                     "Thieves' Town - Compass Chest": (0xdc, 0x10),
                     "Thieves' Town - Ambush Chest": (0xcb, 0x10),
                     "Thieves' Town - Hallway Pot Key": (0xbc, 0x400),
                     "Thieves' Town - Spike Switch Pot Key": (0xab, 0x400),
                     "Thieves' Town - Attic": (0x65, 0x10),
                     "Thieves' Town - Big Chest": (0x44, 0x10),
                     "Thieves' Town - Blind's Cell": (0x45, 0x10),
                     "Thieves' Town - Boss": (0xac, 0x800),
                     'Skull Woods - Compass Chest': (0x67, 0x10),
                     'Skull Woods - Map Chest': (0x58, 0x20),
                     'Skull Woods - Big Chest': (0x58, 0x10),
                     'Skull Woods - Pot Prison': (0x57, 0x20),
                     'Skull Woods - Pinball Room': (0x68, 0x10),
                     'Skull Woods - Big Key Chest': (0x57, 0x10),
                     'Skull Woods - West Lobby Pot Key': (0x56, 0x400),
                     'Skull Woods - Bridge Room': (0x59, 0x10),
                     'Skull Woods - Spike Corner Key Drop': (0x39, 0x400),
                     'Skull Woods - Boss': (0x29, 0x800),
                     'Ice Palace - Jelly Key Drop': (0x0e, 0x400),
                     'Ice Palace - Compass Chest': (0x2e, 0x10),
                     'Ice Palace - Conveyor Key Drop': (0x3e, 0x400),
                     'Ice Palace - Freezor Chest': (0x7e, 0x10),
                     'Ice Palace - Big Chest': (0x9e, 0x10),
                     'Ice Palace - Iced T Room': (0xae, 0x10),
                     'Ice Palace - Many Pots Pot Key': (0x9f, 0x400),
                     'Ice Palace - Spike Room': (0x5f, 0x10),
                     'Ice Palace - Big Key Chest': (0x1f, 0x10),
                     'Ice Palace - Hammer Block Key Drop': (0x3f, 0x400),
                     'Ice Palace - Map Chest': (0x3f, 0x10),
                     'Ice Palace - Boss': (0xde, 0x800),
                     'Misery Mire - Big Chest': (0xc3, 0x10),
                     'Misery Mire - Map Chest': (0xc3, 0x20),
                     'Misery Mire - Main Lobby': (0xc2, 0x10),
                     'Misery Mire - Bridge Chest': (0xa2, 0x10),
                     'Misery Mire - Spikes Pot Key': (0xb3, 0x400),
                     'Misery Mire - Spike Chest': (0xb3, 0x10),
                     'Misery Mire - Fishbone Pot Key': (0xa1, 0x400),
                     'Misery Mire - Conveyor Crystal Key Drop': (0xc1, 0x400),
                     'Misery Mire - Compass Chest': (0xc1, 0x10),
                     'Misery Mire - Big Key Chest': (0xd1, 0x10),
                     'Misery Mire - Boss': (0x90, 0x800),
                     'Turtle Rock - Compass Chest': (0xd6, 0x10),
                     'Turtle Rock - Roller Room - Left': (0xb7, 0x10),
                     'Turtle Rock - Roller Room - Right': (0xb7, 0x20),
                     'Turtle Rock - Pokey 1 Key Drop': (0xb6, 0x400),
                     'Turtle Rock - Chain Chomps': (0xb6, 0x10),
                     'Turtle Rock - Pokey 2 Key Drop': (0x13, 0x400),
                     'Turtle Rock - Big Key Chest': (0x14, 0x10),
                     'Turtle Rock - Big Chest': (0x24, 0x10),
                     'Turtle Rock - Crystaroller Room': (0x4, 0x10),
                     'Turtle Rock - Eye Bridge - Bottom Left': (0xd5, 0x80),
                     'Turtle Rock - Eye Bridge - Bottom Right': (0xd5, 0x40),
                     'Turtle Rock - Eye Bridge - Top Left': (0xd5, 0x20),
                     'Turtle Rock - Eye Bridge - Top Right': (0xd5, 0x10),
                     'Turtle Rock - Boss': (0xa4, 0x800),
                     'Palace of Darkness - Shooter Room': (0x9, 0x10),
                     'Palace of Darkness - The Arena - Bridge': (0x2a, 0x20),
                     'Palace of Darkness - Stalfos Basement': (0xa, 0x10),
                     'Palace of Darkness - Big Key Chest': (0x3a, 0x10),
                     'Palace of Darkness - The Arena - Ledge': (0x2a, 0x10),
                     'Palace of Darkness - Map Chest': (0x2b, 0x10),
                     'Palace of Darkness - Compass Chest': (0x1a, 0x20),
                     'Palace of Darkness - Dark Basement - Left': (0x6a, 0x10),
                     'Palace of Darkness - Dark Basement - Right': (0x6a, 0x20),
                     'Palace of Darkness - Dark Maze - Top': (0x19, 0x10),
                     'Palace of Darkness - Dark Maze - Bottom': (0x19, 0x20),
                     'Palace of Darkness - Big Chest': (0x1a, 0x10),
                     'Palace of Darkness - Harmless Hellway': (0x1a, 0x40),
                     'Palace of Darkness - Boss': (0x5a, 0x800),
                     'Ganons Tower - Conveyor Cross Pot Key': (0x8b, 0x400),
                     "Ganons Tower - Bob's Torch": (0x8c, 0x400),
                     'Ganons Tower - Hope Room - Left': (0x8c, 0x20),
                     'Ganons Tower - Hope Room - Right': (0x8c, 0x40),
                     'Ganons Tower - Tile Room': (0x8d, 0x10),
                     'Ganons Tower - Compass Room - Top Left': (0x9d, 0x10),
                     'Ganons Tower - Compass Room - Top Right': (0x9d, 0x20),
                     'Ganons Tower - Compass Room - Bottom Left': (0x9d, 0x40),
                     'Ganons Tower - Compass Room - Bottom Right': (0x9d, 0x80),
                     'Ganons Tower - Conveyor Star Pits Pot Key': (0x7b, 0x400),
                     'Ganons Tower - DMs Room - Top Left': (0x7b, 0x10),
                     'Ganons Tower - DMs Room - Top Right': (0x7b, 0x20),
                     'Ganons Tower - DMs Room - Bottom Left': (0x7b, 0x40),
                     'Ganons Tower - DMs Room - Bottom Right': (0x7b, 0x80),
                     'Ganons Tower - Map Chest': (0x8b, 0x10),
                     'Ganons Tower - Double Switch Pot Key': (0x9b, 0x400),
                     'Ganons Tower - Firesnake Room': (0x7d, 0x10),
                     'Ganons Tower - Randomizer Room - Top Left': (0x7c, 0x10),
                     'Ganons Tower - Randomizer Room - Top Right': (0x7c, 0x20),
                     'Ganons Tower - Randomizer Room - Bottom Left': (0x7c, 0x40),
                     'Ganons Tower - Randomizer Room - Bottom Right': (0x7c, 0x80),
                     "Ganons Tower - Bob's Chest": (0x8c, 0x80),
                     'Ganons Tower - Big Chest': (0x8c, 0x10),
                     'Ganons Tower - Big Key Room - Left': (0x1c, 0x20),
                     'Ganons Tower - Big Key Room - Right': (0x1c, 0x40),
                     'Ganons Tower - Big Key Chest': (0x1c, 0x10),
                     'Ganons Tower - Mini Helmasaur Room - Left': (0x3d, 0x10),
                     'Ganons Tower - Mini Helmasaur Room - Right': (0x3d, 0x20),
                     'Ganons Tower - Mini Helmasaur Key Drop': (0x3d, 0x400),
                     'Ganons Tower - Pre-Moldorm Chest': (0x3d, 0x40),
                     'Ganons Tower - Validation Chest': (0x4d, 0x10)}
location_table_npc = {'Mushroom': 0x1000,
                      'King Zora': 0x2,
                      'Sahasrahla': 0x10,
                      'Blacksmith': 0x400,
                      'Magic Bat': 0x8000,
                      'Sick Kid': 0x4,
                      'Library': 0x80,
                      'Potion Shop': 0x2000,
                      'Old Man': 0x1,
                      'Ether Tablet': 0x100,
                      'Catfish': 0x20,
                      'Stumpy': 0x8,
                      'Bombos Tablet': 0x200}
location_table_ow = {'Flute Spot': 0x2a,
                     'Sunken Treasure': 0x3b,
                     "Zora's Ledge": 0x81,
                     'Lake Hylia Island': 0x35,
                     'Maze Race': 0x28,
                     'Desert Ledge': 0x30,
                     'Master Sword Pedestal': 0x80,
                     'Spectacle Rock': 0x3,
                     'Pyramid': 0x5b,
                     'Digging Game': 0x68,
                     'Bumper Cave Ledge': 0x4a,
                     'Floating Island': 0x5}
location_table_misc = {'Bottle Merchant': (0x3c9, 0x2),
                       'Purple Chest': (0x3c9, 0x10),
                       "Link's Uncle": (0x3c6, 0x1),
                       'Hobo': (0x3c9, 0x1)}
location_table_pot_items = {}
location_table_sprite_items = {}

SNES_DISCONNECTED = 0
SNES_CONNECTING = 1
SNES_CONNECTED = 2
SNES_ATTACHED = 3

async def snes_connect(ctx : Context, address):
    if ctx.snes_socket is not None:
        logging.error('Already connected to snes')
        return

    ctx.snes_state = SNES_CONNECTING
    recv_task = None

    address = f"ws://{address}" if "://" not in address else address

    logging.info("Connecting to QUsb2snes at %s ..." % address)

    ext = [ClientPerMessageDeflateFactory()]
    try:
        ctx.snes_socket = await websockets.connect(address, ping_timeout=None, ping_interval=None, extensions=ext)
        ctx.snes_state = SNES_CONNECTED

        DeviceList_Request = {
            "Opcode" : "DeviceList",
            "Space" : "SNES"
        }
        await ctx.snes_socket.send(json.dumps(DeviceList_Request))

        reply = json.loads(await ctx.snes_socket.recv())
        devices = reply['Results'] if 'Results' in reply and len(reply['Results']) > 0 else None

        if not devices:
            raise Exception('No device found')

        logging.info("Available devices:")
        for id, device in enumerate(devices):
            logging.info("[%d] %s" % (id + 1, device))

        device = None
        if len(devices) == 1:
            device = devices[0]
        elif ctx.snes_reconnect_address:
            if ctx.snes_attached_device[1] in devices:
                device = ctx.snes_attached_device[1]
            else:
                device = devices[ctx.snes_attached_device[0]]
        else:
            while True:
                logging.info("Select a device:")
                choice = await console_input(ctx)
                if choice is None:
                    raise Exception('Abort input')
                if not choice.isdigit() or int(choice) < 1 or int(choice) > len(devices):
                    logging.warning("Invalid choice (%s)" % choice)
                    continue

                device = devices[int(choice) - 1]
                break

        logging.info("Attaching to " + device)

        Attach_Request = {
            "Opcode" : "Attach",
            "Space" : "SNES",
            "Operands" : [device]
        }
        await ctx.snes_socket.send(json.dumps(Attach_Request))
        ctx.snes_state = SNES_ATTACHED
        ctx.snes_attached_device = (devices.index(device), device)

        if 'SD2SNES'.lower() in device.lower() or (len(device) == 4 and device[:3] == 'COM'):
            logging.info("SD2SNES Detected")
            ctx.is_sd2snes = True
            await ctx.snes_socket.send(json.dumps({"Opcode" : "Info", "Space" : "SNES"}))
            reply = json.loads(await ctx.snes_socket.recv())
            if reply and 'Results' in reply:
                logging.info(reply['Results'])
        else:
            ctx.is_sd2snes = False

        ctx.snes_reconnect_address = address
        recv_task = asyncio.create_task(snes_recv_loop(ctx))

    except Exception as e:
        if recv_task is not None:
            if not ctx.snes_socket.closed:
                await ctx.snes_socket.close()
        else:
            if ctx.snes_socket is not None:
                if not ctx.snes_socket.closed:
                    await ctx.snes_socket.close()
                ctx.snes_socket = None
            ctx.snes_state = SNES_DISCONNECTED
        if not ctx.snes_reconnect_address:
            logging.error("Error connecting to snes (%s)" % e)
        else:
            logging.error(f"Error connecting to snes, attempt again in {RECONNECT_DELAY}s")
            asyncio.create_task(snes_autoreconnect(ctx))

async def snes_autoreconnect(ctx: Context):
    await asyncio.sleep(RECONNECT_DELAY)
    if ctx.snes_reconnect_address and ctx.snes_socket is None:
        await snes_connect(ctx, ctx.snes_reconnect_address)

async def snes_recv_loop(ctx : Context):
    try:
        async for msg in ctx.snes_socket:
            ctx.snes_recv_queue.put_nowait(msg)
        logging.warning("Snes disconnected")
    except Exception as e:
        if not isinstance(e, websockets.WebSocketException):
            logging.exception(e)
        logging.error("Lost connection to the snes, type /snes to reconnect")
    finally:
        socket, ctx.snes_socket = ctx.snes_socket, None
        if socket is not None and not socket.closed:
            await socket.close()

        ctx.snes_state = SNES_DISCONNECTED
        ctx.snes_recv_queue = asyncio.Queue()
        ctx.hud_message_queue = []

        ctx.rom = None

        if ctx.snes_reconnect_address:
            logging.info(f"...reconnecting in {RECONNECT_DELAY}s")
            asyncio.create_task(snes_autoreconnect(ctx))

async def snes_read(ctx : Context, address, size):
    try:
        await ctx.snes_request_lock.acquire()

        if ctx.snes_state != SNES_ATTACHED or ctx.snes_socket is None or not ctx.snes_socket.open or ctx.snes_socket.closed:
            return None

        GetAddress_Request = {
            "Opcode" : "GetAddress",
            "Space" : "SNES",
            "Operands" : [hex(address)[2:], hex(size)[2:]]
        }
        try:
            await ctx.snes_socket.send(json.dumps(GetAddress_Request))
        except websockets.ConnectionClosed:
            return None

        data = bytes()
        while len(data) < size:
            try:
                data += await asyncio.wait_for(ctx.snes_recv_queue.get(), 5)
            except asyncio.TimeoutError:
                break

        if len(data) != size:
            logging.error('Error reading %s, requested %d bytes, received %d' % (hex(address), size, len(data)))
            if len(data):
                logging.error(str(data))
            if ctx.snes_socket is not None and not ctx.snes_socket.closed:
                await ctx.snes_socket.close()
            return None

        return data
    finally:
        ctx.snes_request_lock.release()

async def snes_write(ctx : Context, write_list):
    try:
        await ctx.snes_request_lock.acquire()

        if ctx.snes_state != SNES_ATTACHED or ctx.snes_socket is None or not ctx.snes_socket.open or ctx.snes_socket.closed:
            return False

        PutAddress_Request = {
            "Opcode" : "PutAddress",
            "Operands" : []
        }

        if ctx.is_sd2snes:
            cmd = b'\x00\xE2\x20\x48\xEB\x48'

            for address, data in write_list:
                if (address < WRAM_START) or ((address + len(data)) > (WRAM_START + WRAM_SIZE)):
                    logging.error("SD2SNES: Write out of range %s (%d)" % (hex(address), len(data)))
                    return False
                for ptr, byte in enumerate(data, address + 0x7E0000 - WRAM_START):
                    cmd += b'\xA9' # LDA
                    cmd += bytes([byte])
                    cmd += b'\x8F' # STA.l
                    cmd += bytes([ptr & 0xFF, (ptr >> 8) & 0xFF, (ptr >> 16) & 0xFF])

            cmd += b'\xA9\x00\x8F\x00\x2C\x00\x68\xEB\x68\x28\x6C\xEA\xFF\x08'

            PutAddress_Request['Space'] = 'CMD'
            PutAddress_Request['Operands'] = ["2C00", hex(len(cmd)-1)[2:], "2C00", "1"]
            try:
                if ctx.snes_socket is not None:
                    await ctx.snes_socket.send(json.dumps(PutAddress_Request))
                if ctx.snes_socket is not None:
                    await ctx.snes_socket.send(cmd)
            except websockets.ConnectionClosed:
                return False
        else:
            PutAddress_Request['Space'] = 'SNES'
            try:
                #will pack those requests as soon as qusb2snes actually supports that for real
                for address, data in write_list:
                    PutAddress_Request['Operands'] = [hex(address)[2:], hex(len(data))[2:]]
                    if ctx.snes_socket is not None:
                        await ctx.snes_socket.send(json.dumps(PutAddress_Request))
                    if ctx.snes_socket is not None:
                        await ctx.snes_socket.send(data)
            except websockets.ConnectionClosed:
                return False

        return True
    finally:
        ctx.snes_request_lock.release()

def snes_buffered_write(ctx : Context, address, data):
    if len(ctx.snes_write_buffer) > 0 and (ctx.snes_write_buffer[-1][0] + len(ctx.snes_write_buffer[-1][1])) == address:
        ctx.snes_write_buffer[-1] = (ctx.snes_write_buffer[-1][0], ctx.snes_write_buffer[-1][1] + data)
    else:
        ctx.snes_write_buffer.append((address, data))

async def snes_flush_writes(ctx : Context):
    if not ctx.snes_write_buffer:
        return

    await snes_write(ctx, ctx.snes_write_buffer)
    ctx.snes_write_buffer = []

async def send_msgs(websocket, msgs):
    if not websocket or not websocket.open or websocket.closed:
        return
    try:
        await websocket.send(json.dumps(msgs))
    except websockets.ConnectionClosed:
        pass

async def server_loop(ctx : Context, address = None):
    if ctx.socket is not None:
        logging.error('Already connected')
        return

    if address is None:
        address = ctx.server_address

    while not address:
        logging.info('Enter multiworld server address')
        address = await console_input(ctx)

    address = f"ws://{address}" if "://" not in address else address
    port = urllib.parse.urlparse(address).port or 38281

    logging.info('Connecting to multiworld server at %s' % address)
    try:
        ctx.socket = await websockets.connect(address, port=port, ping_timeout=None, ping_interval=None)
        logging.info('Connected')
        ctx.server_address = address

        async for data in ctx.socket:
            for msg in json.loads(data):
                cmd, args = (msg[0], msg[1]) if len(msg) > 1 else (msg, None)
                await process_server_cmd(ctx, cmd, args)
        logging.warning('Disconnected from multiworld server, type /connect to reconnect')
    except ConnectionRefusedError:
        logging.error('Connection refused by the multiworld server')
    except (OSError, websockets.InvalidURI):
        logging.error('Failed to connect to the multiworld server')
    except Exception as e:
        logging.error('Lost connection to the multiworld server, type /connect to reconnect')
        if not isinstance(e, websockets.WebSocketException):
            logging.exception(e)
    finally:
        ctx.awaiting_rom = False
        ctx.auth = None
        ctx.items_received = []
        ctx.locations_info = {}
        socket, ctx.socket = ctx.socket, None
        if socket is not None and not socket.closed:
            await socket.close()
        ctx.server_task = None
        if ctx.server_address:
            logging.info(f"... reconnecting in {RECONNECT_DELAY}s")
            asyncio.create_task(server_autoreconnect(ctx))

async def server_autoreconnect(ctx: Context):
    await asyncio.sleep(RECONNECT_DELAY)
    if ctx.server_address and ctx.server_task is None:
        ctx.server_task = asyncio.create_task(server_loop(ctx))

async def process_server_cmd(ctx : Context, cmd, args):
    if cmd == 'RoomInfo':
        logging.info('--------------------------------')
        logging.info('Room Information:')
        logging.info('--------------------------------')
        if args['password']:
            logging.info('Password required')
        if len(args['players']) < 1:
            logging.info('No player connected')
        else:
            args['players'].sort()
            current_team = 0
            logging.info('Connected players:')
            logging.info('  Team #1')
            for team, slot, name in args['players']:
                if team != current_team:
                    logging.info(f'  Team #{team + 1}')
                    current_team = team
                logging.info('    %s (Player %d)' % (name, slot))
        await server_auth(ctx, args['password'])

    if cmd == 'ConnectionRefused':
        if 'InvalidPassword' in args:
            logging.error('Invalid password')
            ctx.password = None
            await server_auth(ctx, True)
        if 'InvalidRom' in args:
            raise Exception('Invalid ROM detected, please verify that you have loaded the correct rom and reconnect your snes')
        if 'SlotAlreadyTaken' in args:
            raise Exception('Player slot already in use for that team')
        raise Exception('Connection refused by the multiworld host')

    if cmd == 'Connected':
        ctx.team, ctx.slot = args[0]
        ctx.player_names = {p: n for p, n in args[1]}
        msgs = []
        if ctx.locations_checked:
            msgs.append(['LocationChecks', [ctx.lookup_name_to_id[loc] for loc in ctx.locations_checked]])
        if ctx.locations_scouted:
            msgs.append(['LocationScouts', list(ctx.locations_scouted)])
        if msgs:
            await send_msgs(ctx.socket, msgs)

    if cmd == 'ReceivedItems':
        start_index, items = args
        if start_index == 0:
            ctx.items_received = []
        elif start_index != len(ctx.items_received):
            sync_msg = [['Sync']]
            if ctx.locations_checked:
                sync_msg.append(['LocationChecks', [ctx.lookup_name_to_id[loc] for loc in ctx.locations_checked]])
            await send_msgs(ctx.socket, sync_msg)
        if start_index == len(ctx.items_received):
            for item in items:
                ctx.items_received.append(ReceivedItem(*item))
        ctx.watcher_event.set()

    if cmd == 'LocationInfo':
        for location, item, player in args:
            if location not in ctx.locations_info:
                replacements = {0xA2: 'Small Key', 0x9D: 'Big Key', 0x8D: 'Compass', 0x7D: 'Map'}
                item_name = replacements.get(item, get_item_name_from_id(item))
                logging.info(f"Saw {color(item_name, 'red', 'bold')} at {list(ctx.lookup_id_to_name.keys())[location - 1]}")
                ctx.locations_info[location] = (item, player)
        ctx.watcher_event.set()

    if cmd == 'ItemSent':
        player_sent, location, player_recvd, item = args
        item = color(get_item_name_from_id(item), 'cyan' if player_sent != ctx.slot else 'green')
        player_sent = color(ctx.player_names[player_sent], 'yellow' if player_sent != ctx.slot else 'magenta')
        player_recvd = color(ctx.player_names[player_recvd], 'yellow' if player_recvd != ctx.slot else 'magenta')
        location_name = get_location_name_from_address(ctx, location)
        logging.info('%s sent %s to %s (%s)' % (player_sent, item, player_recvd, location_name))

    if cmd == 'Print':
        logging.info(args)

async def server_auth(ctx : Context, password_requested):
    if password_requested and not ctx.password:
        logging.info('Enter the password required to join this game:')
        ctx.password = await console_input(ctx)
    if ctx.rom is None:
        ctx.awaiting_rom = True
        logging.info('No ROM detected, awaiting snes connection to authenticate to the multiworld server')
        return
    ctx.awaiting_rom = False
    ctx.auth = ctx.rom.copy()
    await send_msgs(ctx.socket, [['Connect', {'password': ctx.password, 'rom': ctx.auth}]])

async def console_input(ctx : Context):
    ctx.input_requests += 1
    return await ctx.input_queue.get()

async def disconnect(ctx: Context):
    if ctx.socket is not None and not ctx.socket.closed:
        await ctx.socket.close()
    if ctx.server_task is not None:
        await ctx.server_task

async def connect(ctx: Context, address=None):
    await disconnect(ctx)
    ctx.server_task = asyncio.create_task(server_loop(ctx, address))

async def console_loop(ctx : Context):
    while not ctx.exit_event.is_set():
        input = await aioconsole.ainput()

        if ctx.input_requests > 0:
            ctx.input_requests -= 1
            ctx.input_queue.put_nowait(input)
            continue

        command = shlex.split(input)
        if not command:
            continue

        if command[0] == '/exit':
            ctx.exit_event.set()

        if command[0] == '/snes':
            ctx.snes_reconnect_address = None
            asyncio.create_task(snes_connect(ctx, command[1] if len(command) > 1 else ctx.snes_address))
        if command[0] in ['/snes_close', '/snes_quit']:
            ctx.snes_reconnect_address = None
            if ctx.snes_socket is not None and not ctx.snes_socket.closed:
                await ctx.snes_socket.close()

        if command[0] in ['/connect', '/reconnect']:
            ctx.server_address = None
            asyncio.create_task(connect(ctx, command[1] if len(command) > 1 else None))
        if command[0] == '/disconnect':
            ctx.server_address = None
            asyncio.create_task(disconnect(ctx))
        if command[0][:1] != '/':
            asyncio.create_task(send_msgs(ctx.socket, [['Say', input]]))

        if command[0] == '/received':
            logging.info('Received items:')
            for index, item in enumerate(ctx.items_received, 1):
                logging.info('%s from %s (%s) (%d/%d in list)' % (
                    color(get_item_name_from_id(item.item), 'red', 'bold'), color(ctx.player_names[item.player], 'yellow'),
                    get_location_name_from_address(ctx, item.location), index, len(ctx.items_received)))

        if command[0] == '/missing':
            for location in [k for k, v in ctx.lookup_name_to_id.items()
                             if type(v) is int and not filter_location(ctx, k)]:
                if location not in ctx.locations_checked:
                    logging.info('Missing: ' + location)
        if command[0] == '/getitem' and len(command) > 1:
            item = input[9:]
            item_id = Items.item_table[item][3] if item in Items.item_table else None
            if type(item_id) is int and item_id in range(0x100):
                logging.info('Sending item: ' + item)
                snes_buffered_write(ctx, RECV_ITEM_ADDR, bytes([item_id]))
                snes_buffered_write(ctx, RECV_ITEM_PLAYER_ADDR, bytes([0]))
            else:
                logging.info('Invalid item: ' + item)

        await snes_flush_writes(ctx)


def get_item_name_from_id(code):
    items = [k for k, i in Items.item_table.items() if type(i[3]) is int and i[3] == code]
    return items[0] if items else f'Unknown item (ID:{code})'


def get_location_name_from_address(ctx, address):
    if type(address) is str:
        return address

    return ctx.lookup_id_to_name.get(address, f'Unknown location (ID:{address})')


def filter_location(ctx, location):
    if location in location_table_pot_items:
        tile_idx, mask = location_table_pot_items[location]
        tracking_data = ctx.pottery_locations_enabled
        tile_pots = tracking_data[tile_idx] | (tracking_data[tile_idx+1] << 8)
        return (mask & tile_pots) == 0
    if (not ctx.key_drop_mode and location in PotShuffle.key_drop_data
         and PotShuffle.key_drop_data[location][0] == 'Drop'):
        return True
    if not ctx.shop_mode and location in Regions.flat_normal_shops:
        return True
    if not ctx.retro_mode and location in Regions.flat_retro_shops:
        return True
    return False


def init_lookups(ctx):
    ctx.lookup_id_to_name = {x: y for x, y in Regions.lookup_id_to_name.items()}
    ctx.lookup_name_to_id = {x: y for x, y in Regions.lookup_name_to_id.items()}
    for location, datum in PotShuffle.key_drop_data.items():
        type = datum[0]
        if type == 'Drop':
            location_id, super_tile, sprite_index = datum[1]
            location_table_sprite_items[location] = (2 * super_tile, 0x8000 >> sprite_index)
            ctx.lookup_name_to_id[location] = location_id
            ctx.lookup_id_to_name[location_id] = location
    for super_tile, pot_list in PotShuffle.vanilla_pots.items():
        for pot_index, pot in enumerate(pot_list):
            if pot.item != PotItem.Hole:
                if pot.item == PotItem.Key:
                    loc_name = next(loc for loc, datum in PotShuffle.key_drop_data.items()
                                    if datum[1] == super_tile)
                else:
                    descriptor = 'Large Block' if pot.flags & PotFlags.Block else f'Pot #{pot_index+1}'
                    loc_name = f'{pot.room} {descriptor}'
                location_table_pot_items[loc_name] = (2 * super_tile, 0x8000 >> pot_index)
                location_id = Regions.pot_address(pot_index, super_tile)
                ctx.lookup_name_to_id[loc_name] = location_id
                ctx.lookup_id_to_name[location_id] = loc_name


async def track_locations(ctx : Context, roomid, roomdata):
    new_locations = []

    if ctx.total_locations is None:
        total_data = await snes_read(ctx, DYNAMIC_TOTAL_ADDR, 2)
        ttl = total_data[0] | (total_data[1] << 8)
        if ttl > 0:
            ctx.total_locations = ttl

    if ctx.mode_flags is None:
        flags = await snes_read(ctx, MODE_FLAGS, 1)
        ctx.mode_flags = flags
        ctx.key_drop_mode = flags[0] & 0x1
        ctx.shop_mode = flags[0] & 0x2
        ctx.retro_mode = flags[0] & 0x4
        ctx.pottery_mode = flags[0] & 0x8
        ctx.mystery_mode = flags[0] & 0x10

    def new_check(location):
        ctx.locations_checked.add(location)
        ignored = filter_location(ctx, location)
        if ignored:
            ctx.ignore_count += 1
        else:
            total = '???' if ctx.mystery_mode else ctx.total_locations
            logging.info(f"New check: {location} ({len(ctx.locations_checked)-ctx.ignore_count}/{total})")
            new_locations.append(ctx.lookup_name_to_id[location])

    try:
        if ctx.shop_mode or ctx.retro_mode:
            misc_data = await snes_read(ctx, SHOP_SRAM_START, SHOP_SRAM_LEN)
            for cnt, b in enumerate(misc_data):
                my_check = Regions.shop_table_by_location_id[0x400000 + cnt]
                if int(b) > 0 and my_check not in ctx.locations_checked:
                    new_check(my_check)
    except Exception as e:
        print(e)
        logging.warning(e)

    for location, (loc_roomid, loc_mask) in location_table_uw.items():
        if location not in ctx.locations_checked and loc_roomid == roomid and (roomdata << 4) & loc_mask != 0:
            new_check(location)

    uw_begin = 0x129
    uw_end = 0
    uw_unchecked = {}
    for location, (roomid, mask) in location_table_uw.items():
        if location not in ctx.locations_checked:
            uw_unchecked[location] = (roomid, mask)
            uw_begin = min(uw_begin, roomid)
            uw_end = max(uw_end, roomid + 1)
    if uw_begin < uw_end:
        uw_data = await snes_read(ctx, SAVEDATA_START + (uw_begin * 2), (uw_end - uw_begin) * 2)
        if uw_data is not None:
            for location, (roomid, mask) in uw_unchecked.items():
                offset = (roomid - uw_begin) * 2
                roomdata = uw_data[offset] | (uw_data[offset + 1] << 8)
                if roomdata & mask != 0:
                    new_check(location)

    ow_begin = 0x82
    ow_end = 0
    ow_unchecked = {}
    for location, screenid in location_table_ow.items():
        if location not in ctx.locations_checked:
            ow_unchecked[location] = (screenid, 0x40)
            ow_begin = min(ow_begin, screenid)
            ow_end = max(ow_end, screenid + 1)
    from Regions import bonk_prize_table
    from OWEdges import OWTileRegions
    for location, (_, flag, _, _, region_name, _) in bonk_prize_table.items():
        if location not in ctx.locations_checked:
            if region_name in OWTileRegions:
                screenid = OWTileRegions[region_name]
                ow_unchecked[location] = (screenid, flag)
                ow_begin = min(ow_begin, screenid)
                ow_end = max(ow_end, screenid + 1)
    if ow_begin < ow_end:
        ow_data = await snes_read(ctx, SAVEDATA_START + 0x280 + ow_begin, ow_end - ow_begin)
        if ow_data is not None:
            for location, (screenid, flag) in ow_unchecked.items():
                if ow_data[screenid - ow_begin] & flag != 0:
                    new_check(location)

    if not all([location in ctx.locations_checked for location in location_table_npc.keys()]):
        npc_data = await snes_read(ctx, SAVEDATA_START + 0x410, 2)
        if npc_data is not None:
            npc_value = npc_data[0] | (npc_data[1] << 8)
            for location, mask in location_table_npc.items():
                if npc_value & mask != 0 and location not in ctx.locations_checked:
                    new_check(location)

    if not all([location in ctx.locations_checked for location in location_table_misc.keys()]):
        misc_data = await snes_read(ctx, SAVEDATA_START + 0x3c6, 4)
        if misc_data is not None:
            for location, (offset, mask) in location_table_misc.items():
                assert(0x3c6 <= offset <= 0x3c9)
                if misc_data[offset - 0x3c6] & mask != 0 and location not in ctx.locations_checked:
                    new_check(location)

    if not all([location in ctx.locations_checked for location in location_table_pot_items.keys()]):
        pot_items_data = await snes_read(ctx, POT_ITEMS_SRAM_START, ITEM_SRAM_SIZE)
        if pot_items_data is not None:
            for location, (offset, mask) in location_table_pot_items.items():
                pot_value = pot_items_data[offset] | (pot_items_data[offset + 1] << 8)
                if pot_value & mask != 0 and location not in ctx.locations_checked:
                    new_check(location)

    if not all([location in ctx.locations_checked for location in location_table_sprite_items.keys()]):
        sprite_items_data = await snes_read(ctx, SPRITE_ITEMS_SRAM_START, ITEM_SRAM_SIZE)
        if sprite_items_data is not None:
            for location, (offset, mask) in location_table_sprite_items.items():
                sprite_value = sprite_items_data[offset] | (sprite_items_data[offset + 1] << 8)
                if sprite_value & mask != 0 and location not in ctx.locations_checked:
                    new_check(location)

    await send_msgs(ctx.socket, [['LocationChecks', new_locations]])

async def game_watcher(ctx : Context):
    while not ctx.exit_event.is_set():
        try:
            await asyncio.wait_for(ctx.watcher_event.wait(), 2)
        except asyncio.TimeoutError:
            pass
        ctx.watcher_event.clear()

        if not ctx.rom:
            rom = await snes_read(ctx, ROMNAME_START, ROMNAME_SIZE)
            if rom is None or rom == bytes([0] * ROMNAME_SIZE):
                continue

            ctx.rom = list(rom)
            ctx.locations_checked = set()
            ctx.locations_scouted = set()
            if ctx.awaiting_rom:
                await server_auth(ctx, False)

        if ctx.auth and ctx.auth != ctx.rom:
            logging.warning("ROM change detected, please reconnect to the multiworld server")
            await disconnect(ctx)

        if ctx.pottery_locations_enabled is None:
            ctx.pottery_locations_enabled = await snes_read(ctx, POT_LOCATION_TABLE, 0x250)

        gamemode = await snes_read(ctx, WRAM_START + 0x10, 1)
        if gamemode is None or gamemode[0] not in INGAME_MODES:
            continue

        data = await snes_read(ctx, RECV_PROGRESS_ADDR, 8)
        if data is None:
            continue

        recv_index = data[0] | (data[1] << 8)
        assert RECV_ITEM_ADDR == RECV_PROGRESS_ADDR + 2
        recv_item = data[2]
        assert ROOMID_ADDR == RECV_PROGRESS_ADDR + 4
        roomid = data[4] | (data[5] << 8)
        assert ROOMDATA_ADDR == RECV_PROGRESS_ADDR + 6
        roomdata = data[6]
        assert SCOUT_LOCATION_ADDR == RECV_PROGRESS_ADDR + 7
        scout_location = data[7]

        if recv_index < len(ctx.items_received) and recv_item == 0:
            item = ctx.items_received[recv_index]
            logging.info('Received %s from %s (%s) (%d/%d in list)' % (
                color(get_item_name_from_id(item.item), 'red', 'bold'), color(ctx.player_names[item.player], 'yellow'),
                get_location_name_from_address(ctx, item.location), recv_index + 1, len(ctx.items_received)))
            recv_index += 1
            snes_buffered_write(ctx, RECV_PROGRESS_ADDR, bytes([recv_index & 0xFF, (recv_index >> 8) & 0xFF]))
            snes_buffered_write(ctx, RECV_ITEM_ADDR, bytes([item.item]))
            snes_buffered_write(ctx, RECV_ITEM_PLAYER_ADDR, bytes([item.player if item.player != ctx.slot else 0]))
        if scout_location > 0 and scout_location in ctx.locations_info:
            snes_buffered_write(ctx, SCOUTREPLY_LOCATION_ADDR, bytes([scout_location]))
            snes_buffered_write(ctx, SCOUTREPLY_ITEM_ADDR, bytes([ctx.locations_info[scout_location][0]]))
            snes_buffered_write(ctx, SCOUTREPLY_PLAYER_ADDR, bytes([ctx.locations_info[scout_location][1]]))

        await snes_flush_writes(ctx)

        if scout_location > 0 and scout_location not in ctx.locations_scouted:
            ctx.locations_scouted.add(scout_location)
            logging.info(f'Scouting item at {list(ctx.lookup_id_to_name.keys())[scout_location - 1]}')
            await send_msgs(ctx.socket, [['LocationScouts', [scout_location]]])
        await track_locations(ctx, roomid, roomdata)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snes', default='localhost:8080', help='Address of the QUsb2snes server.')
    parser.add_argument('--connect', default=None, help='Address of the multiworld host.')
    parser.add_argument('--password', default=None, help='Password of the multiworld host.')
    parser.add_argument('--loglevel', default='info', choices=['debug', 'info', 'warning', 'error', 'critical'])
    args = parser.parse_args()

    logging.basicConfig(format='%(message)s', level=getattr(logging, args.loglevel.upper(), logging.INFO))

    ctx = Context(args.snes, args.connect, args.password)
    init_lookups(ctx)

    input_task = asyncio.create_task(console_loop(ctx))

    await snes_connect(ctx, ctx.snes_address)

    if ctx.server_task is None:
        ctx.server_task = asyncio.create_task(server_loop(ctx))

    watcher_task = asyncio.create_task(game_watcher(ctx))


    await ctx.exit_event.wait()
    ctx.server_address = None
    ctx.snes_reconnect_address = None

    await watcher_task

    if ctx.socket is not None and not ctx.socket.closed:
        await ctx.socket.close()
    if ctx.server_task is not None:
        await ctx.server_task

    if ctx.snes_socket is not None and not ctx.snes_socket.closed:
        await ctx.snes_socket.close()

    while ctx.input_requests > 0:
        ctx.input_queue.put_nowait(None)
        ctx.input_requests -= 1

    await input_task

if __name__ == '__main__':
    colorama.init()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
    loop.close()
    colorama.deinit()
