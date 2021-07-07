
from BaseClasses import OWEdge, Direction, Terrain, WorldType, PolSlot
from enum import Enum, unique
from Utils import bidict

@unique
class OpenStd(Enum):
    Open = 0
    Standard = 1

@unique
class IsParallel(Enum):
    No = 0
    Yes = 1

# constants
We = Direction.West
Ea = Direction.East
So = Direction.South
No = Direction.North

Ld = Terrain.Land
Wr = Terrain.Water

LW = WorldType.Light
DW = WorldType.Dark

Vt = PolSlot.NorthSouth
Hz = PolSlot.EastWest

Op = OpenStd.Open
St = OpenStd.Standard

PL = IsParallel.Yes
NP = IsParallel.No


def create_owedges(world, player):
    edges = [
                             # name,                        owID,dir,type,edge_id,(owSlot)        vram
        create_owedge(player, 'Lost Woods NW',               0x00, No, Ld, 0x00)      .coordInfo(0x00a0, 0x0284),
        create_owedge(player, 'Lost Woods SW',               0x00, So, Ld, 0x01, 0x08).coordInfo(0x0058, 0x2000),
        create_owedge(player, 'Lost Woods SC',               0x00, So, Ld, 0x02, 0x08).coordInfo(0x0178, 0x2020),
        create_owedge(player, 'Lost Woods SE',               0x00, So, Ld, 0x03, 0x09).coordInfo(0x0388, 0x2060),
        create_owedge(player, 'Lost Woods EN',               0x00, Ea, Ld, 0x00, 0x01).coordInfo(0x0088, 0x0180),
        create_owedge(player, 'Lumberjack SW',               0x02, So, Ld, 0x00)      .coordInfo(0x04cc, 0x100a),
        create_owedge(player, 'Lumberjack WN',               0x02, We, Ld, 0x00)      .coordInfo(0x0088, 0x00e0),
        create_owedge(player, 'West Death Mountain EN',      0x03, Ea, Ld, 0x01, 0x04).coordInfo(0x0070, 0x0180),
        create_owedge(player, 'West Death Mountain ES',      0x03, Ea, Ld, 0x03, 0x0c).coordInfo(0x0340, 0x1780),
        create_owedge(player, 'East Death Mountain WN',      0x05, We, Ld, 0x01, 0x05).coordInfo(0x0070, 0x0060),
        create_owedge(player, 'East Death Mountain WS',      0x05, We, Ld, 0x03, 0x0d).coordInfo(0x0340, 0x1660),
        create_owedge(player, 'East Death Mountain EN',      0x05, Ea, Ld, 0x02, 0x06).coordInfo(0x0078, 0x0180),
        create_owedge(player, 'Death Mountain TR Pegs WN',   0x07, We, Ld, 0x02)      .coordInfo(0x0078, 0x00e0),
        create_owedge(player, 'Mountain Entry NW',           0x0a, No, Ld, 0x01)      .coordInfo(0x04cc, 0x180a),
        create_owedge(player, 'Mountain Entry SE',           0x0a, So, Ld, 0x04)      .coordInfo(0x0518, 0x1012),
        create_owedge(player, 'Zora Waterfall NE',           0x0f, No, Ld, 0x02)      .coordInfo(0x0f80, 0x009a),
        create_owedge(player, 'Zora Waterfall SE',           0x0f, So, Ld, 0x05)      .coordInfo(0x0f80, 0x1020),
        create_owedge(player, 'Lost Woods Pass NW',          0x10, No, Ld, 0x03)      .coordInfo(0x0058, 0x1800),
        create_owedge(player, 'Lost Woods Pass NE',          0x10, No, Ld, 0x04)      .coordInfo(0x0178, 0x181e),
        create_owedge(player, 'Lost Woods Pass SW',          0x10, So, Ld, 0x06)      .coordInfo(0x0088, 0x1002),
        create_owedge(player, 'Lost Woods Pass SE',          0x10, So, Ld, 0x07)      .coordInfo(0x0148, 0x101a),
        create_owedge(player, 'Kakariko Fortune NE',         0x11, No, Ld, 0x05)      .coordInfo(0x0388, 0x1820),
        create_owedge(player, 'Kakariko Fortune SC',         0x11, So, Ld, 0x08)      .coordInfo(0x0318, 0x1014),
        create_owedge(player, 'Kakariko Fortune EN',         0x11, Ea, Ld, 0x04)      .coordInfo(0x046c, 0x00c0),
        create_owedge(player, 'Kakariko Fortune ES',         0x11, Ea, Ld, 0x05)      .coordInfo(0x0580, 0x08c0),
        create_owedge(player, 'Kakariko Pond NE',            0x12, No, Ld, 0x06)      .coordInfo(0x0518, 0x1812),
        create_owedge(player, 'Kakariko Pond SW',            0x12, So, Ld, 0x09)      .coordInfo(0x04a4, 0x1006),
        create_owedge(player, 'Kakariko Pond SE',            0x12, So, Ld, 0x0a)      .coordInfo(0x0524, 0x1016),
        create_owedge(player, 'Kakariko Pond WN',            0x12, We, Ld, 0x04)      .coordInfo(0x046c, 0x00e0),
        create_owedge(player, 'Kakariko Pond WS',            0x12, We, Ld, 0x05)      .coordInfo(0x0580, 0x08e0),
        create_owedge(player, 'Kakariko Pond EN',            0x12, Ea, Ld, 0x06)      .coordInfo(0x04c4, 0x0340),
        create_owedge(player, 'Kakariko Pond ES',            0x12, Ea, Ld, 0x07)      .coordInfo(0x0570, 0x08c0),
        create_owedge(player, 'Sanctuary WN',                0x13, We, Ld, 0x06)      .coordInfo(0x04c4, 0x0360),
        create_owedge(player, 'Sanctuary WS',                0x13, We, Ld, 0x07)      .coordInfo(0x0570, 0x08e0),
        create_owedge(player, 'Sanctuary EC',                0x13, Ea, Ld, 0x08)      .coordInfo(0x050c, 0x04c0),
        create_owedge(player, 'Graveyard WC',                0x14, We, Ld, 0x08)      .coordInfo(0x050c, 0x04e0),
        create_owedge(player, 'Graveyard EC',                0x14, Ea, Ld, 0x09)      .coordInfo(0x0504, 0x04c0),
        create_owedge(player, 'River Bend SW',               0x15, So, Ld, 0x0b)      .coordInfo(0x0a9c, 0x1004),
        create_owedge(player, 'River Bend SC',               0x15, So, Wr, 0x0c)      .coordInfo(0x0b30, 0x1018),
        create_owedge(player, 'River Bend SE',               0x15, So, Ld, 0x0d)      .coordInfo(0x0b88, 0x1020),
        create_owedge(player, 'River Bend WC',               0x15, We, Ld, 0x09)      .coordInfo(0x0504, 0x04e0),
        create_owedge(player, 'River Bend EN',               0x15, Ea, Wr, 0x0a)      .coordInfo(0x0484, 0x01c0),
        create_owedge(player, 'River Bend EC',               0x15, Ea, Ld, 0x0b)      .coordInfo(0x04e0, 0x04c0),
        create_owedge(player, 'River Bend ES',               0x15, Ea, Ld, 0x0c)      .coordInfo(0x0574, 0x08c0),
        create_owedge(player, 'Potion Shop WN',              0x16, We, Wr, 0x0a)      .coordInfo(0x0484, 0x01e0),
        create_owedge(player, 'Potion Shop WC',              0x16, We, Ld, 0x0b)      .coordInfo(0x04e0, 0x04e0),
        create_owedge(player, 'Potion Shop WS',              0x16, We, Ld, 0x0c)      .coordInfo(0x0574, 0x08e0),
        create_owedge(player, 'Potion Shop EN',              0x16, Ea, Wr, 0x0d)      .coordInfo(0x0454, 0x00c0),
        create_owedge(player, 'Potion Shop EC',              0x16, Ea, Ld, 0x0e)      .coordInfo(0x0494, 0x01c0),
        create_owedge(player, 'Zora Approach NE',            0x17, No, Ld, 0x07)      .coordInfo(0x0f80, 0x1820),
        create_owedge(player, 'Zora Approach WN',            0x17, We, Wr, 0x0d)      .coordInfo(0x0454, 0x00e0),
        create_owedge(player, 'Zora Approach WC',            0x17, We, Ld, 0x0e)      .coordInfo(0x0494, 0x01e0),
        create_owedge(player, 'Kakariko NW',                 0x18, No, Ld, 0x08)      .coordInfo(0x0088, 0x1802),
        create_owedge(player, 'Kakariko NC',                 0x18, No, Ld, 0x09)      .coordInfo(0x0148, 0x181a),
        create_owedge(player, 'Kakariko NE',                 0x18, No, Ld, 0x0a, 0x19).coordInfo(0x0318, 0x1854),
        create_owedge(player, 'Kakariko SE',                 0x18, So, Ld, 0x0f, 0x21).coordInfo(0x0370, 0x2060),
        create_owedge(player, 'Kakariko ES',                 0x18, Ea, Ld, 0x10, 0x21).coordInfo(0x0928, 0x1680),
        create_owedge(player, 'Forgotten Forest NW',         0x1a, No, Ld, 0x0b)      .coordInfo(0x04a4, 0x1806),
        create_owedge(player, 'Forgotten Forest NE',         0x1a, No, Ld, 0x0c)      .coordInfo(0x0524, 0x1816),
        create_owedge(player, 'Forgotten Forest ES',         0x1a, Ea, Ld, 0x0f)      .coordInfo(0x0728, 0x06c0),
        create_owedge(player, 'Hyrule Castle SW',            0x1b, So, Ld, 0x10, 0x23).coordInfo(0x068c, 0x2002),
        create_owedge(player, 'Hyrule Castle SE',            0x1b, So, Ld, 0x11, 0x24).coordInfo(0x0924, 0x2054),
        create_owedge(player, 'Hyrule Castle WN',            0x1b, We, Ld, 0x0f)      .coordInfo(0x0728, 0x0660),
        create_owedge(player, 'Hyrule Castle ES',            0x1b, Ea, Ld, 0x11, 0x24).coordInfo(0x0890, 0x1280),
        create_owedge(player, 'Wooden Bridge NW',            0x1d, No, Ld, 0x0d)      .coordInfo(0x0a9c, 0x1804),
        create_owedge(player, 'Wooden Bridge NC',            0x1d, No, Wr, 0x0e)      .coordInfo(0x0b30, 0x1818),
        create_owedge(player, 'Wooden Bridge NE',            0x1d, No, Ld, 0x0f)      .coordInfo(0x0b88, 0x1820),
        create_owedge(player, 'Wooden Bridge SW',            0x1d, So, Ld, 0x0e)      .coordInfo(0x0aa8, 0x1006),
        create_owedge(player, 'Eastern Palace SW',           0x1e, So, Ld, 0x13, 0x26).coordInfo(0x0c80, 0x2002),
        create_owedge(player, 'Eastern Palace SE',           0x1e, So, Ld, 0x14, 0x27).coordInfo(0x0f78, 0x2060),
        create_owedge(player, 'Blacksmith WS',               0x22, We, Ld, 0x10)      .coordInfo(0x0928, 0x05e0),
        create_owedge(player, 'Sand Dunes NW',               0x25, No, Ld, 0x10)      .coordInfo(0x0aa8, 0x1806),
        create_owedge(player, 'Sand Dunes SC',               0x25, So, Ld, 0x12)      .coordInfo(0x0af0, 0x100e),
        create_owedge(player, 'Sand Dunes WN',               0x25, We, Ld, 0x11)      .coordInfo(0x0890, 0x01e0),
        create_owedge(player, 'Maze Race ES',                0x28, Ea, Ld, 0x12)      .coordInfo(0x0bc0, 0x0940),
        create_owedge(player, 'Kakariko Suburb NE',          0x29, No, Ld, 0x11)      .coordInfo(0x0370, 0x1820),
        create_owedge(player, 'Kakariko Suburb WS',          0x29, We, Ld, 0x12)      .coordInfo(0x0bc0, 0x0960),
        create_owedge(player, 'Kakariko Suburb ES',          0x29, Ea, Ld, 0x13)      .coordInfo(0x0b80, 0x0940),
        create_owedge(player, 'Flute Boy SW',                0x2a, So, Ld, 0x15)      .coordInfo(0x044c, 0x1000),
        create_owedge(player, 'Flute Boy SC',                0x2a, So, Ld, 0x16)      .coordInfo(0x04e8, 0x100c),
        create_owedge(player, 'Flute Boy WS',                0x2a, We, Ld, 0x13)      .coordInfo(0x0b80, 0x0960),
        create_owedge(player, 'Central Bonk Rocks NW',       0x2b, No, Ld, 0x12)      .coordInfo(0x068c, 0x1802),
        create_owedge(player, 'Central Bonk Rocks SW',       0x2b, So, Ld, 0x17)      .coordInfo(0x069c, 0x1004),
        create_owedge(player, 'Central Bonk Rocks EN',       0x2b, Ea, Ld, 0x14)      .coordInfo(0x0ac0, 0x0340),
        create_owedge(player, 'Central Bonk Rocks EC',       0x2b, Ea, Ld, 0x15)      .coordInfo(0x0b18, 0x05c0),
        create_owedge(player, 'Central Bonk Rocks ES',       0x2b, Ea, Ld, 0x16)      .coordInfo(0x0b8c, 0x08c0),
        create_owedge(player, 'Links House NE',              0x2c, No, Ld, 0x13)      .coordInfo(0x0924, 0x1814),
        create_owedge(player, 'Links House SC',              0x2c, So, Ld, 0x18)      .coordInfo(0x08e0, 0x100e),
        create_owedge(player, 'Links House WN',              0x2c, We, Ld, 0x14)      .coordInfo(0x0ac0, 0x0360),
        create_owedge(player, 'Links House WC',              0x2c, We, Ld, 0x15)      .coordInfo(0x0b18, 0x05e0),
        create_owedge(player, 'Links House WS',              0x2c, We, Ld, 0x16)      .coordInfo(0x0b8c, 0x08a0),
        create_owedge(player, 'Links House ES',              0x2c, Ea, Ld, 0x17)      .coordInfo(0x0b80, 0x08c0),
        create_owedge(player, 'Stone Bridge NC',             0x2d, No, Ld, 0x14)      .coordInfo(0x0af0, 0x180e),
        create_owedge(player, 'Stone Bridge SC',             0x2d, So, Ld, 0x19)      .coordInfo(0x0ae0, 0x100c),
        create_owedge(player, 'Stone Bridge WC',             0x2d, We, Wr, 0x17)      .coordInfo(0x0b1c, 0x061c),
        create_owedge(player, 'Stone Bridge WS',             0x2d, We, Ld, 0x18)      .coordInfo(0x0b80, 0x08e0),
        create_owedge(player, 'Stone Bridge EN',             0x2d, Ea, Ld, 0x18)      .coordInfo(0x0a90, 0x01c0),
        create_owedge(player, 'Stone Bridge EC',             0x2d, Ea, Wr, 0x19)      .coordInfo(0x0b3c, 0x0640),
        create_owedge(player, 'Tree Line NW',                0x2e, No, Ld, 0x15)      .coordInfo(0x0c80, 0x1802),
        create_owedge(player, 'Tree Line SC',                0x2e, So, Wr, 0x1a)      .coordInfo(0x0d48, 0x101a),
        create_owedge(player, 'Tree Line SE',                0x2e, So, Ld, 0x1b)      .coordInfo(0x0d98, 0x1020),
        create_owedge(player, 'Tree Line WN',                0x2e, We, Ld, 0x19)      .coordInfo(0x0a90, 0x01e0),
        create_owedge(player, 'Tree Line WC',                0x2e, We, Wr, 0x1a)      .coordInfo(0x0b3c, 0x0660),
        create_owedge(player, 'Eastern Nook NE',             0x2f, No, Ld, 0x16)      .coordInfo(0x0f78, 0x1820),
        create_owedge(player, 'Desert EC',                   0x30, Ea, Ld, 0x1e, 0x39).coordInfo(0x0ee4, 0x1480),
        create_owedge(player, 'Desert ES',                   0x30, Ea, Ld, 0x1f, 0x39).coordInfo(0x0f8c, 0x1980),
        create_owedge(player, 'Flute Boy Approach NW',       0x32, No, Ld, 0x17)      .coordInfo(0x044c, 0x1800),
        create_owedge(player, 'Flute Boy Approach NC',       0x32, No, Ld, 0x18)      .coordInfo(0x04e8, 0x180c),
        create_owedge(player, 'Flute Boy Approach EC',       0x32, Ea, Ld, 0x1a)      .coordInfo(0x0d04, 0x05c0),
        create_owedge(player, 'C Whirlpool NW',              0x33, No, Ld, 0x19)      .coordInfo(0x069c, 0x1804),
        create_owedge(player, 'C Whirlpool SC',              0x33, So, Ld, 0x1c)      .coordInfo(0x0728, 0x1016),
        create_owedge(player, 'C Whirlpool WC',              0x33, We, Ld, 0x1b)      .coordInfo(0x0d04, 0x05e0),
        create_owedge(player, 'C Whirlpool EN',              0x33, Ea, Ld, 0x1b)      .coordInfo(0x0cad, 0x02c0),
        create_owedge(player, 'C Whirlpool EC',              0x33, Ea, Wr, 0x1c)      .coordInfo(0x0d0b, 0x05c0),
        create_owedge(player, 'C Whirlpool ES',              0x33, Ea, Ld, 0x1d)      .coordInfo(0x0d76, 0x08c0),
        create_owedge(player, 'Statues NC',                  0x34, No, Ld, 0x1a)      .coordInfo(0x08e0, 0x180e),
        create_owedge(player, 'Statues SC',                  0x34, So, Ld, 0x1d)      .coordInfo(0x08f0, 0x1010),
        create_owedge(player, 'Statues WN',                  0x34, We, Ld, 0x1c)      .coordInfo(0x0cad, 0x02e0),
        create_owedge(player, 'Statues WC',                  0x34, We, Wr, 0x1d)      .coordInfo(0x0d0b, 0x05e0),
        create_owedge(player, 'Statues WS',                  0x34, We, Ld, 0x1e)      .coordInfo(0x0d76, 0x08e0),
        create_owedge(player, 'Lake Hylia NW',               0x35, No, Ld, 0x1b)      .coordInfo(0x0ae0, 0x180c),
        create_owedge(player, 'Lake Hylia NC',               0x35, No, Wr, 0x1c, 0x36).coordInfo(0x0d48, 0x185a),
        create_owedge(player, 'Lake Hylia NE',               0x35, No, Ld, 0x1d, 0x36).coordInfo(0x0d98, 0x1860),
        create_owedge(player, 'Lake Hylia WS',               0x35, We, Ld, 0x24, 0x3d).coordInfo(0x0f98, 0x1860),
        create_owedge(player, 'Lake Hylia EC',               0x35, Ea, Wr, 0x24, 0x3e).coordInfo(0x0f30, 0x1680),
        create_owedge(player, 'Lake Hylia ES',               0x35, Ea, Ld, 0x25, 0x3e).coordInfo(0x0f94, 0x1880),
        create_owedge(player, 'Ice Cave SW',                 0x37, So, Wr, 0x1e)      .coordInfo(0x0e80, 0x1002),
        create_owedge(player, 'Ice Cave SE',                 0x37, So, Ld, 0x1f)      .coordInfo(0x0f50, 0x101c),
        create_owedge(player, 'Desert Pass WC',              0x3a, We, Ld, 0x1f)      .coordInfo(0x0ee4, 0x03e0),
        create_owedge(player, 'Desert Pass WS',              0x3a, We, Ld, 0x20)      .coordInfo(0x0f8c, 0x0860),
        create_owedge(player, 'Desert Pass EC',              0x3a, Ea, Ld, 0x20)      .coordInfo(0x0f18, 0x0640),
        create_owedge(player, 'Desert Pass ES',              0x3a, Ea, Ld, 0x21)      .coordInfo(0x0fcb, 0x08c0),
        create_owedge(player, 'Dam NC',                      0x3b, No, Ld, 0x1e)      .coordInfo(0x0728, 0x1816),
        create_owedge(player, 'Dam WC',                      0x3b, We, Ld, 0x21)      .coordInfo(0x0f18, 0x0660),
        create_owedge(player, 'Dam WS',                      0x3b, We, Ld, 0x22)      .coordInfo(0x0fc8, 0x08e0),
        create_owedge(player, 'Dam EC',                      0x3b, Ea, Ld, 0x22)      .coordInfo(0x0ef0, 0x04c0),
        create_owedge(player, 'South Pass NC',               0x3c, No, Ld, 0x1f)      .coordInfo(0x08f0, 0x1810),
        create_owedge(player, 'South Pass WC',               0x3c, We, Ld, 0x23)      .coordInfo(0x0ef0, 0x04e0),
        create_owedge(player, 'South Pass ES',               0x3c, Ea, Ld, 0x23)      .coordInfo(0x0f98, 0x08c0),
        create_owedge(player, 'Octoballoon NW',              0x3f, No, Wr, 0x20)      .coordInfo(0x0e80, 0x1802),
        create_owedge(player, 'Octoballoon NE',              0x3f, No, Ld, 0x21)      .coordInfo(0x0f50, 0x181c),
        create_owedge(player, 'Octoballoon WC',              0x3f, We, Wr, 0x25)      .coordInfo(0x0f30, 0x05e0),
        create_owedge(player, 'Octoballoon WS',              0x3f, We, Ld, 0x26)      .coordInfo(0x0f94, 0x0860),
        create_owedge(player, 'Skull Woods SW',              0x40, So, Ld, 0x21, 0x48).coordInfo(0x0058, 0x2000),
        create_owedge(player, 'Skull Woods SC',              0x40, So, Ld, 0x22, 0x48).coordInfo(0x0178, 0x2020),
        create_owedge(player, 'Skull Woods SE',              0x40, So, Ld, 0x23, 0x49).coordInfo(0x0388, 0x2060),
        create_owedge(player, 'Skull Woods EN',              0x40, Ea, Ld, 0x26, 0x41).coordInfo(0x0088, 0x0180),
        create_owedge(player, 'Dark Lumberjack SW',          0x42, So, Ld, 0x20)      .coordInfo(0x04cc, 0x100a),
        create_owedge(player, 'Dark Lumberjack WN',          0x42, We, Ld, 0x27)      .coordInfo(0x0088, 0x00e0),
        create_owedge(player, 'West Dark Death Mountain EN', 0x43, Ea, Ld, 0x27, 0x44).coordInfo(0x0070, 0x0180),
        create_owedge(player, 'West Dark Death Mountain ES', 0x43, Ea, Ld, 0x29, 0x4c).coordInfo(0x0340, 0x1780),
        create_owedge(player, 'East Dark Death Mountain WN', 0x45, We, Ld, 0x28)      .coordInfo(0x0070, 0x0060),
        create_owedge(player, 'East Dark Death Mountain WS', 0x45, We, Ld, 0x2a, 0x4d).coordInfo(0x0340, 0x1660),
        create_owedge(player, 'East Dark Death Mountain EN', 0x45, Ea, Ld, 0x28, 0x46).coordInfo(0x0078, 0x0180),
        create_owedge(player, 'Turtle Rock WN',              0x47, We, Ld, 0x29)      .coordInfo(0x0078, 0x00e0),
        create_owedge(player, 'Bumper Cave NW',              0x4a, No, Ld, 0x22)      .coordInfo(0x04cc, 0x180a),
        create_owedge(player, 'Bumper Cave SE',              0x4a, So, Ld, 0x24)      .coordInfo(0x0518, 0x1012),
        create_owedge(player, 'Catfish SE',                  0x4f, So, Ld, 0x25)      .coordInfo(0x0f80, 0x1020),
        create_owedge(player, 'Skull Woods Pass NW',         0x50, No, Ld, 0x23)      .coordInfo(0x0058, 0x181e),
        create_owedge(player, 'Skull Woods Pass NE',         0x50, No, Ld, 0x24)      .coordInfo(0x0178, 0x1800),
        create_owedge(player, 'Skull Woods Pass SW',         0x50, So, Ld, 0x26)      .coordInfo(0x0088, 0x1002),
        create_owedge(player, 'Skull Woods Pass SE',         0x50, So, Ld, 0x27)      .coordInfo(0x0148, 0x101a),
        create_owedge(player, 'Dark Fortune NE',             0x51, No, Ld, 0x25)      .coordInfo(0x0388, 0x1820),
        create_owedge(player, 'Dark Fortune SC',             0x51, So, Ld, 0x28)      .coordInfo(0x0318, 0x1014),
        create_owedge(player, 'Dark Fortune EN',             0x51, Ea, Ld, 0x2a)      .coordInfo(0x046c, 0x00c0),
        create_owedge(player, 'Dark Fortune ES',             0x51, Ea, Ld, 0x2b)      .coordInfo(0x0580, 0x08c0),
        create_owedge(player, 'Outcast Pond NE',             0x52, No, Ld, 0x26)      .coordInfo(0x0518, 0x1812),
        create_owedge(player, 'Outcast Pond SW',             0x52, So, Ld, 0x29)      .coordInfo(0x04a4, 0x1006),
        create_owedge(player, 'Outcast Pond SE',             0x52, So, Ld, 0x2a)      .coordInfo(0x0524, 0x1016),
        create_owedge(player, 'Outcast Pond WN',             0x52, We, Ld, 0x2b)      .coordInfo(0x046c, 0x00e0),
        create_owedge(player, 'Outcast Pond WS',             0x52, We, Ld, 0x2c)      .coordInfo(0x0580, 0x08e0),
        create_owedge(player, 'Outcast Pond EN',             0x52, Ea, Ld, 0x2c)      .coordInfo(0x04c4, 0x0340),
        create_owedge(player, 'Outcast Pond ES',             0x52, Ea, Ld, 0x2d)      .coordInfo(0x0570, 0x08c0),
        create_owedge(player, 'Dark Chapel WN',              0x53, We, Ld, 0x2d)      .coordInfo(0x04c4, 0x0360),
        create_owedge(player, 'Dark Chapel WS',              0x53, We, Ld, 0x2e)      .coordInfo(0x0570, 0x08e0),
        create_owedge(player, 'Dark Chapel EC',              0x53, Ea, Ld, 0x2e)      .coordInfo(0x050c, 0x04c0),
        create_owedge(player, 'Dark Graveyard WC',           0x54, We, Ld, 0x2f)      .coordInfo(0x050c, 0x04e0),
        create_owedge(player, 'Dark Graveyard EC',           0x54, Ea, Ld, 0x2f)      .coordInfo(0x0504, 0x04c0),
        create_owedge(player, 'Qirn Jump SW',                0x55, So, Ld, 0x2b)      .coordInfo(0x0a9c, 0x1004),
        create_owedge(player, 'Qirn Jump SC',                0x55, So, Wr, 0x2c)      .coordInfo(0x0b30, 0x1018),
        create_owedge(player, 'Qirn Jump SE',                0x55, So, Ld, 0x2d)      .coordInfo(0x0b88, 0x1020),
        create_owedge(player, 'Qirn Jump WC',                0x55, We, Ld, 0x30)      .coordInfo(0x0504, 0x04e0),
        create_owedge(player, 'Qirn Jump EN',                0x55, Ea, Wr, 0x30)      .coordInfo(0x0484, 0x01c0),
        create_owedge(player, 'Qirn Jump EC',                0x55, Ea, Ld, 0x31)      .coordInfo(0x04e0, 0x04c0),
        create_owedge(player, 'Qirn Jump ES',                0x55, Ea, Ld, 0x32)      .coordInfo(0x0574, 0x08c0),
        create_owedge(player, 'Dark Witch WN',               0x56, We, Wr, 0x31)      .coordInfo(0x0484, 0x01e0),
        create_owedge(player, 'Dark Witch WC',               0x56, We, Ld, 0x32)      .coordInfo(0x04e0, 0x04e0),
        create_owedge(player, 'Dark Witch WS',               0x56, We, Ld, 0x33)      .coordInfo(0x0574, 0x08e0),
        create_owedge(player, 'Dark Witch EN',               0x56, Ea, Wr, 0x33)      .coordInfo(0x0454, 0x00c0),
        create_owedge(player, 'Dark Witch EC',               0x56, Ea, Ld, 0x34)      .coordInfo(0x0494, 0x01c0),
        create_owedge(player, 'Catfish Approach NE',         0x57, No, Ld, 0x27)      .coordInfo(0x0f80, 0x1820),
        create_owedge(player, 'Catfish Approach WN',         0x57, We, Wr, 0x34)      .coordInfo(0x0454, 0x00e0),
        create_owedge(player, 'Catfish Approach WC',         0x57, We, Ld, 0x35)      .coordInfo(0x0494, 0x01e0),
        create_owedge(player, 'Village of Outcasts NW',      0x58, No, Ld, 0x28)      .coordInfo(0x0088, 0x1802),
        create_owedge(player, 'Village of Outcasts NC',      0x58, No, Ld, 0x29)      .coordInfo(0x0148, 0x181a),
        create_owedge(player, 'Village of Outcasts NE',      0x58, No, Ld, 0x2a, 0x59).coordInfo(0x0318, 0x1854),
        create_owedge(player, 'Village of Outcasts SE',      0x58, So, Ld, 0x2f, 0x61).coordInfo(0x0370, 0x2060),
        create_owedge(player, 'Village of Outcasts ES',      0x58, Ea, Ld, 0x35, 0x61).coordInfo(0x0928, 0x1680),
        create_owedge(player, 'Shield Shop NW',              0x5a, No, Ld, 0x2b)      .coordInfo(0x04a4, 0x1806),
        create_owedge(player, 'Shield Shop NE',              0x5a, No, Ld, 0x2c)      .coordInfo(0x0524, 0x1816),
        create_owedge(player, 'Pyramid SW',                  0x5b, So, Ld, 0x30, 0x63).coordInfo(0x068c, 0x2002),
        create_owedge(player, 'Pyramid SE',                  0x5b, So, Ld, 0x31, 0x64).coordInfo(0x0924, 0x2054),
        create_owedge(player, 'Pyramid ES',                  0x5b, Ea, Ld, 0x36, 0x64).coordInfo(0x0890, 0x1280),
        create_owedge(player, 'Broken Bridge NW',            0x5d, No, Ld, 0x2d)      .coordInfo(0x0a9c, 0x1804),
        create_owedge(player, 'Broken Bridge NC',            0x5d, No, Wr, 0x2e)      .coordInfo(0x0b30, 0x1818),
        create_owedge(player, 'Broken Bridge NE',            0x5d, No, Ld, 0x2f)      .coordInfo(0x0b88, 0x1820),
        create_owedge(player, 'Broken Bridge SW',            0x5d, So, Ld, 0x2e)      .coordInfo(0x0aa8, 0x1006),
        create_owedge(player, 'Palace of Darkness SW',       0x5e, So, Ld, 0x33, 0x66).coordInfo(0x0c80, 0x2002),
        create_owedge(player, 'Palace of Darkness SE',       0x5e, So, Ld, 0x34, 0x67).coordInfo(0x0f78, 0x2060),
        create_owedge(player, 'Hammer Pegs WS',              0x62, We, Ld, 0x36)      .coordInfo(0x0928, 0x05e0),
        create_owedge(player, 'Dark Dunes NW',               0x65, No, Ld, 0x30)      .coordInfo(0x0aa8, 0x1806),
        create_owedge(player, 'Dark Dunes SC',               0x65, So, Ld, 0x32)      .coordInfo(0x0af0, 0x100e),
        create_owedge(player, 'Dark Dunes WN',               0x65, We, Ld, 0x37)      .coordInfo(0x0890, 0x01e0),
        create_owedge(player, 'Dig Game EC',                 0x68, Ea, Ld, 0x37)      .coordInfo(0x0b64, 0x08c0),
        create_owedge(player, 'Dig Game ES',                 0x68, Ea, Ld, 0x38)      .coordInfo(0x0bc0, 0x0940),
        create_owedge(player, 'Frog NE',                     0x69, No, Ld, 0x31)      .coordInfo(0x0370, 0x1820),
        create_owedge(player, 'Frog WC',                     0x69, We, Ld, 0x38)      .coordInfo(0x0b64, 0x08e0),
        create_owedge(player, 'Frog WS',                     0x69, We, Ld, 0x39)      .coordInfo(0x0bc0, 0x0960),
        create_owedge(player, 'Frog ES',                     0x69, Ea, Ld, 0x39)      .coordInfo(0x0b80, 0x0940),
        create_owedge(player, 'Stumpy SW',                   0x6a, So, Ld, 0x35)      .coordInfo(0x044c, 0x1000),
        create_owedge(player, 'Stumpy SC',                   0x6a, So, Ld, 0x36)      .coordInfo(0x04e8, 0x100c),
        create_owedge(player, 'Stumpy WS',                   0x6a, We, Ld, 0x3a)      .coordInfo(0x0b80, 0x0960),
        create_owedge(player, 'Dark Bonk Rocks NW',          0x6b, No, Ld, 0x32)      .coordInfo(0x068c, 0x1802),
        create_owedge(player, 'Dark Bonk Rocks SW',          0x6b, So, Ld, 0x37)      .coordInfo(0x069c, 0x1004),
        create_owedge(player, 'Dark Bonk Rocks EN',          0x6b, Ea, Ld, 0x3a)      .coordInfo(0x0ac0, 0x0340),
        create_owedge(player, 'Dark Bonk Rocks EC',          0x6b, Ea, Ld, 0x3b)      .coordInfo(0x0b18, 0x05c0),
        create_owedge(player, 'Dark Bonk Rocks ES',          0x6b, Ea, Ld, 0x3c)      .coordInfo(0x0b8c, 0x08c0),
        create_owedge(player, 'Big Bomb Shop NE',            0x6c, No, Ld, 0x33)      .coordInfo(0x0924, 0x1814),
        create_owedge(player, 'Big Bomb Shop SC',            0x6c, So, Ld, 0x38)      .coordInfo(0x08e0, 0x100e),
        create_owedge(player, 'Big Bomb Shop WN',            0x6c, We, Ld, 0x3b)      .coordInfo(0x0ac0, 0x0360),
        create_owedge(player, 'Big Bomb Shop WC',            0x6c, We, Ld, 0x3c)      .coordInfo(0x0b18, 0x05e0),
        create_owedge(player, 'Big Bomb Shop WS',            0x6c, We, Ld, 0x3d)      .coordInfo(0x0b8c, 0x08a0),
        create_owedge(player, 'Big Bomb Shop ES',            0x6c, Ea, Ld, 0x3d)      .coordInfo(0x0b80, 0x08c0),
        create_owedge(player, 'Hammer Bridge NC',            0x6d, No, Ld, 0x34)      .coordInfo(0x0af0, 0x180e),
        create_owedge(player, 'Hammer Bridge SC',            0x6d, So, Ld, 0x39)      .coordInfo(0x0ae0, 0x100c),
        create_owedge(player, 'Hammer Bridge WS',            0x6d, We, Ld, 0x3e)      .coordInfo(0x0b80, 0x08e0),
        create_owedge(player, 'Hammer Bridge EN',            0x6d, Ea, Ld, 0x3e)      .coordInfo(0x0a90, 0x01c0),
        create_owedge(player, 'Hammer Bridge EC',            0x6d, Ea, Wr, 0x3f)      .coordInfo(0x0b3c, 0x0640),
        create_owedge(player, 'Dark Tree Line NW',           0x6e, No, Ld, 0x35)      .coordInfo(0x0c80, 0x1802),
        create_owedge(player, 'Dark Tree Line SC',           0x6e, So, Wr, 0x3a)      .coordInfo(0x0d48, 0x101a),
        create_owedge(player, 'Dark Tree Line SE',           0x6e, So, Ld, 0x3b)      .coordInfo(0x0d98, 0x1020),
        create_owedge(player, 'Dark Tree Line WN',           0x6e, We, Ld, 0x3f)      .coordInfo(0x0a90, 0x01e0),
        create_owedge(player, 'Dark Tree Line WC',           0x6e, We, Wr, 0x40)      .coordInfo(0x0b3c, 0x0660),
        create_owedge(player, 'Palace of Darkness Nook NE',  0x6f, No, Ld, 0x36)      .coordInfo(0x0f78, 0x1820),
        create_owedge(player, 'Stumpy Approach NW',          0x72, No, Ld, 0x37)      .coordInfo(0x044c, 0x1800),
        create_owedge(player, 'Stumpy Approach NC',          0x72, No, Ld, 0x38)      .coordInfo(0x04e8, 0x180c),
        create_owedge(player, 'Stumpy Approach EC',          0x72, Ea, Ld, 0x40)      .coordInfo(0x0d04, 0x05c0),
        create_owedge(player, 'Dark C Whirlpool NW',         0x73, No, Ld, 0x39)      .coordInfo(0x069c, 0x1804),
        create_owedge(player, 'Dark C Whirlpool SC',         0x73, So, Ld, 0x3c)      .coordInfo(0x0728, 0x1016),
        create_owedge(player, 'Dark C Whirlpool WC',         0x73, We, Ld, 0x41)      .coordInfo(0x0d04, 0x05e0),
        create_owedge(player, 'Dark C Whirlpool EN',         0x73, Ea, Ld, 0x41)      .coordInfo(0x0cad, 0x02c0),
        create_owedge(player, 'Dark C Whirlpool EC',         0x73, Ea, Wr, 0x42)      .coordInfo(0x0d0b, 0x05c0),
        create_owedge(player, 'Dark C Whirlpool ES',         0x73, Ea, Ld, 0x43)      .coordInfo(0x0d76, 0x08c0),
        create_owedge(player, 'Hype Cave NC',                0x74, No, Ld, 0x3a)      .coordInfo(0x08e0, 0x180e),
        create_owedge(player, 'Hype Cave SC',                0x74, So, Ld, 0x3d)      .coordInfo(0x08f0, 0x1010),
        create_owedge(player, 'Hype Cave WN',                0x74, We, Ld, 0x42)      .coordInfo(0x0cad, 0x02e0),
        create_owedge(player, 'Hype Cave WC',                0x74, We, Wr, 0x43)      .coordInfo(0x0d0b, 0x05e0),
        create_owedge(player, 'Hype Cave WS',                0x74, We, Ld, 0x44)      .coordInfo(0x0d76, 0x08e0),
        create_owedge(player, 'Ice Lake NW',                 0x75, No, Ld, 0x3b)      .coordInfo(0x0ae0, 0x180c),
        create_owedge(player, 'Ice Lake NC',                 0x75, No, Wr, 0x3c, 0x76).coordInfo(0x0d48, 0x185a),
        create_owedge(player, 'Ice Lake NE',                 0x75, No, Ld, 0x3d, 0x76).coordInfo(0x0d98, 0x1860),
        create_owedge(player, 'Ice Lake WS',                 0x75, We, Ld, 0x48, 0x7d).coordInfo(0x0f98, 0x1860),
        create_owedge(player, 'Ice Lake EC',                 0x75, Ea, Wr, 0x48, 0x7e).coordInfo(0x0f30, 0x1680),
        create_owedge(player, 'Ice Lake ES',                 0x75, Ea, Ld, 0x49, 0x7e).coordInfo(0x0f94, 0x1880),
        create_owedge(player, 'Shopping Mall SW',            0x77, So, Wr, 0x3e)      .coordInfo(0x0e80, 0x1002),
        create_owedge(player, 'Shopping Mall SE',            0x77, So, Ld, 0x3f)      .coordInfo(0x0f50, 0x101c),
        create_owedge(player, 'Swamp Nook EC',               0x7a, Ea, Ld, 0x44)      .coordInfo(0x0f18, 0x0640),
        create_owedge(player, 'Swamp Nook ES',               0x7a, Ea, Ld, 0x45)      .coordInfo(0x0fc8, 0x08c0),
        create_owedge(player, 'Swamp NC',                    0x7b, No, Ld, 0x3e)      .coordInfo(0x0728, 0x1816),
        create_owedge(player, 'Swamp WC',                    0x7b, We, Ld, 0x45)      .coordInfo(0x0f18, 0x0660),
        create_owedge(player, 'Swamp WS',                    0x7b, We, Ld, 0x46)      .coordInfo(0x0fc8, 0x08e0),
        create_owedge(player, 'Swamp EC',                    0x7b, Ea, Ld, 0x46)      .coordInfo(0x0ef0, 0x04c0),
        create_owedge(player, 'Dark South Pass NC',          0x7c, No, Ld, 0x3f)      .coordInfo(0x08f0, 0x1810),
        create_owedge(player, 'Dark South Pass WC',          0x7c, We, Ld, 0x47)      .coordInfo(0x0ef0, 0x04e0),
        create_owedge(player, 'Dark South Pass ES',          0x7c, Ea, Ld, 0x47)      .coordInfo(0x0f98, 0x08c0),
        create_owedge(player, 'Bomber Corner NW',            0x7f, No, Wr, 0x40)      .coordInfo(0x0e80, 0x1802),
        create_owedge(player, 'Bomber Corner NE',            0x7f, No, Ld, 0x41)      .coordInfo(0x0f50, 0x181c),
        create_owedge(player, 'Bomber Corner WC',            0x7f, We, Wr, 0x49)      .coordInfo(0x0f30, 0x05e0),
        create_owedge(player, 'Bomber Corner WS',            0x7f, We, Ld, 0x4a)      .coordInfo(0x0f94, 0x0860),
        create_owedge(player, 'Master Sword Meadow SC',      0x80, So, Ld, 0x40)      .coordInfo(0x0080, 0x0000),
        create_owedge(player, 'Hobo EC',                     0x80, Ea, Wr, 0x4a)      .coordInfo(0x008c, 0x0020),
        create_owedge(player, 'Zoras Domain SW',             0x81, So, Ld, 0x41, 0x89).coordInfo(0x02a4, 0x1782)
    ]
        
    world.owedges += edges
    world.initialize_owedges(edges)

def create_owedge(player, name, owIndex, direction, terrain, edge_id, owSlotIndex=0xff):
    return OWEdge(player, name, owIndex, direction, terrain, edge_id, owSlotIndex)


OWEdgeGroups = {
    #(IsStandard, World, EdgeAxis, Terrain, HasParallel, NumberInGroup)
    (St, LW, Vt, Ld, PL, 1): (
        [
            ['Hyrule Castle SW'],
            ['Hyrule Castle SE']
        ],
        [
            ['Central Bonk Rocks NW'],
            ['Links House NE']
        ]
    ),
    (St, LW, Hz, Ld, PL, 3): (
        [
            ['Central Bonk Rocks EN', 'Central Bonk Rocks EC', 'Central Bonk Rocks ES']
        ],
        [
            ['Links House WN', 'Links House WC', 'Links House WS']
        ]
    ),
    (Op, LW, Hz, Ld, PL, 1): (
        [
            ['Lost Woods EN'],
            ['East Death Mountain EN'],
            ['Sanctuary EC'],
            ['Graveyard EC'],
            ['Kakariko ES'],
            ['Hyrule Castle ES'],
            ['Maze Race ES'],
            ['Kakariko Suburb ES'],
            ['Links House ES'],
            ['Flute Boy Approach EC'],
            ['Dam EC'],
            ['South Pass ES'],
            ['Potion Shop EC'],
            ['Lake Hylia ES'],
            ['Stone Bridge EN'],
            ['West Death Mountain EN'],
            ['West Death Mountain ES']
        ],
        [
            ['Lumberjack WN'],
            ['Death Mountain TR Pegs WN'],
            ['Graveyard WC'],
            ['River Bend WC'],
            ['Blacksmith WS'],
            ['Sand Dunes WN'],
            ['Kakariko Suburb WS'],
            ['Flute Boy WS'],
            ['Stone Bridge WS'],
            ['C Whirlpool WC'],
            ['South Pass WC'],
            ['Lake Hylia WS'],
            ['Zora Approach WC'],
            ['Octoballoon WS'],
            ['Tree Line WN'],
            ['East Death Mountain WN'],
            ['East Death Mountain WS']
        ]
    ),
    (Op, LW, Hz, Ld, NP, 1): (
        [
            ['Forgotten Forest ES']
        ],
        [
            ['Hyrule Castle WN']
        ]
    ),
    (Op, LW, Vt, Ld, PL, 1): (
        [
            ['Lumberjack SW'],
            ['Mountain Entry SE'],
            ['Lost Woods SE'],
            ['Zora Waterfall SE'],
            ['Kakariko Fortune SC'],
            ['Wooden Bridge SW'],
            ['Kakariko SE'],
            ['Sand Dunes SC'],
            ['Eastern Palace SW'],
            ['Eastern Palace SE'],
            ['Central Bonk Rocks SW'],
            ['Links House SC'],
            ['Stone Bridge SC'],
            ['C Whirlpool SC'],
            ['Statues SC'],
            ['Tree Line SE'],
            ['Ice Cave SE']
        ],
        [
            ['Mountain Entry NW'],
            ['Kakariko Pond NE'],
            ['Kakariko Fortune NE'],
            ['Zora Approach NE'],
            ['Kakariko NE'],
            ['Sand Dunes NW'],
            ['Kakariko Suburb NE'],
            ['Stone Bridge NC'],
            ['Tree Line NW'],
            ['Eastern Nook NE'],
            ['C Whirlpool NW'],
            ['Statues NC'],
            ['Lake Hylia NW'],
            ['Dam NC'],
            ['South Pass NC'],
            ['Lake Hylia NE'],
            ['Octoballoon NE']
        ]
    ),
    (Op, LW, Hz, Ld, PL, 2): (
        [
            ['Kakariko Fortune EN', 'Kakariko Fortune ES'],
            ['Kakariko Pond EN', 'Kakariko Pond ES'],
            ['Desert Pass EC', 'Desert Pass ES'],
            ['River Bend EC', 'River Bend ES'],
            ['C Whirlpool EN', 'C Whirlpool ES']
        ],
        [
            ['Kakariko Pond WN', 'Kakariko Pond WS'],
            ['Sanctuary WN', 'Sanctuary WS'],
            ['Dam WC', 'Dam WS'],
            ['Potion Shop WC', 'Potion Shop WS'],
            ['Statues WN', 'Statues WS']
        ]
    ),
    (Op, LW, Hz, Ld, NP, 2): (
        [
            ['Desert EC', 'Desert ES']
        ],
        [
            ['Desert Pass WC', 'Desert Pass WS']
        ]
    ),
    (Op, LW, Vt, Ld, PL, 2): (
        [
            ['Lost Woods SW', 'Lost Woods SC'],
            ['Lost Woods Pass SW', 'Lost Woods Pass SE'],
            ['Kakariko Pond SW', 'Kakariko Pond SE'],
            ['Flute Boy SW', 'Flute Boy SC'],
            ['River Bend SW', 'River Bend SE']
        ],
        [
            ['Lost Woods Pass NW', 'Lost Woods Pass NE'],
            ['Kakariko NW', 'Kakariko NC'],
            ['Forgotten Forest NW', 'Forgotten Forest NE'],
            ['Flute Boy Approach NW', 'Flute Boy Approach NC'],
            ['Wooden Bridge NW', 'Wooden Bridge NE']
        ]
    ),
    (Op, LW, Hz, Wr, PL, 1): (
        [
            ['Potion Shop EN'],
            ['Lake Hylia EC'],
            ['Stone Bridge EC'],
            ['River Bend EN'],
            ['C Whirlpool EC']
        ],
        [
            ['Zora Approach WN'],
            ['Octoballoon WC'],
            ['Tree Line WC'],
            ['Potion Shop WN'],
            ['Statues WC']
        ]
    ),
    (Op, LW, Vt, Wr, PL, 1): (
        [
            ['Tree Line SC'],
            ['Ice Cave SW'],
            ['River Bend SC']
        ],
        [
            ['Lake Hylia NC'],
            ['Octoballoon NW'],
            ['Wooden Bridge NC']
        ]
    ),
    (Op, DW, Hz, Ld, PL, 1): (
        [
            ['Skull Woods EN'],
            ['East Dark Death Mountain EN'],
            ['Dark Chapel EC'],
            ['Dark Graveyard EC'],
            ['Village of Outcasts ES'],
            ['Pyramid ES'],
            ['Frog ES'],
            ['Big Bomb Shop ES'],
            ['Stumpy Approach EC'],
            ['Swamp EC'],
            ['Dark South Pass ES'],
            ['Dark Witch EC'],
            ['Ice Lake ES'],
            ['Hammer Bridge EN'],
            ['West Dark Death Mountain EN'],
            ['West Dark Death Mountain ES']
        ],
        [
            ['Dark Lumberjack WN'],
            ['Turtle Rock WN'],
            ['Dark Graveyard WC'],
            ['Qirn Jump WC'],
            ['Hammer Pegs WS'],
            ['Dark Dunes WN'],
            ['Stumpy WS'],
            ['Hammer Bridge WS'],
            ['Dark C Whirlpool WC'],
            ['Dark South Pass WC'],
            ['Ice Lake WS'],
            ['Catfish Approach WC'],
            ['Bomber Corner WS'],
            ['Dark Tree Line WN'],
            ['East Dark Death Mountain WN'],
            ['East Dark Death Mountain WS']
        ]
    ),
    (Op, DW, Vt, Ld, PL, 1): (
        [
            ['Dark Lumberjack SW'],
            ['Bumper Cave SE'],
            ['Skull Woods SE'],
            ['Catfish SE'],
            ['Dark Fortune SC'],
            ['Broken Bridge SW'],
            ['Village of Outcasts SE'],
            ['Pyramid SW'],
            ['Pyramid SE'],
            ['Dark Dunes SC'],
            ['Palace of Darkness SW'],
            ['Palace of Darkness SE'],
            ['Dark Bonk Rocks SW'],
            ['Big Bomb Shop SC'],
            ['Hammer Bridge SC'],
            ['Dark C Whirlpool SC'],
            ['Hype Cave SC'],
            ['Dark Tree Line SE'],
            ['Shopping Mall SE']
        ],
        [
            ['Bumper Cave NW'],
            ['Outcast Pond NE'],
            ['Dark Fortune NE'],
            ['Catfish Approach NE'],
            ['Village of Outcasts NE'],
            ['Dark Dunes NW'],
            ['Frog NE'],
            ['Dark Bonk Rocks NW'],
            ['Big Bomb Shop NE'],
            ['Hammer Bridge NC'],
            ['Dark Tree Line NW'],
            ['Palace of Darkness Nook NE'],
            ['Dark C Whirlpool NW'],
            ['Hype Cave NC'],
            ['Ice Lake NW'],
            ['Swamp NC'],
            ['Dark South Pass NC'],
            ['Ice Lake NE'],
            ['Bomber Corner NE']
        ]
    ),
    (Op, DW, Hz, Ld, NP, 1): (
        [ ],
        [ ]
    ),
    (Op, DW, Hz, Ld, PL, 2): (
        [
            ['Dark Fortune EN', 'Dark Fortune ES'],
            ['Outcast Pond EN', 'Outcast Pond ES'],
            ['Swamp Nook EC', 'Swamp Nook ES'],
            ['Qirn Jump EC', 'Qirn Jump ES'],
            ['Dark C Whirlpool EN', 'Dark C Whirlpool ES']
        ],
        [
            ['Outcast Pond WN', 'Outcast Pond WS'],
            ['Dark Chapel WN', 'Dark Chapel WS'],
            ['Swamp WC', 'Swamp WS'],
            ['Dark Witch WC', 'Dark Witch WS'],
            ['Hype Cave WN', 'Hype Cave WS']
        ]
    ),
    (Op, DW, Hz, Ld, NP, 2): (
        [
            ['Dig Game EC', 'Dig Game ES']
        ],
        [
            ['Frog WC', 'Frog WS']
        ]
    ),
    (Op, DW, Vt, Ld, PL, 2): (
        [
            ['Skull Woods SW', 'Skull Woods SC'],
            ['Skull Woods Pass SW', 'Skull Woods Pass SE'],
            ['Outcast Pond SW', 'Outcast Pond SE'],
            ['Stumpy SW', 'Stumpy SC'],
            ['Qirn Jump SW', 'Qirn Jump SE']
        ],
        [
            ['Skull Woods Pass NW', 'Skull Woods Pass NE'],
            ['Village of Outcasts NW', 'Village of Outcasts NC'],
            ['Shield Shop NW', 'Shield Shop NE'],
            ['Stumpy Approach NW', 'Stumpy Approach NC'],
            ['Broken Bridge NW', 'Broken Bridge NE']
        ]
    ),
    (Op, DW, Hz, Ld, PL, 3): (
        [
            ['Dark Bonk Rocks EN', 'Dark Bonk Rocks EC', 'Dark Bonk Rocks ES']
        ],
        [
            ['Big Bomb Shop WN', 'Big Bomb Shop WC', 'Big Bomb Shop WS']
        ]
    ),
    (Op, DW, Hz, Wr, PL, 1): (
        [
            ['Dark Witch EN'],
            ['Ice Lake EC'],
            ['Hammer Bridge EC'],
            ['Qirn Jump EN'],
            ['Dark C Whirlpool EC']
        ],
        [
            ['Catfish Approach WN'],
            ['Bomber Corner WC'],
            ['Dark Tree Line WC'],
            ['Dark Witch WN'],
            ['Hype Cave WC']
        ]
    ),
    (Op, DW, Vt, Wr, PL, 1): (
        [
            ['Dark Tree Line SC'],
            ['Shopping Mall SW'],
            ['Qirn Jump SC']
        ],
        [
            ['Ice Lake NC'],
            ['Bomber Corner NW'],
            ['Broken Bridge NC']
        ]
    )
}

OWTileGroups = {
    ("Woods", "Regular"): (
        [
            0x00, 0x2d, 0x40, 0x6d, 0x80
        ],
        [
            'Master Sword Meadow',
            'Lost Woods West Area',
            'Lost Woods East Area',
            'Stone Bridge Area',
            'Stone Bridge Water',
            'Hobo Bridge'
        ],
        [
            'Skull Woods Forest',
            'Skull Woods Portal Entry',
            'Skull Woods Forest (West)',
            'Skull Woods Forgotten Path (Southwest)',
            'Skull Woods Forgotten Path (Northeast)',
            'Hammer Bridge North Area',
            'Hammer Bridge South Area',
            'Hammer Bridge Water'
        ]
    ),
    ("Lumberjack", "Regular"): (
        [
            0x02, 0x42
        ],
        [
            'Lumberjack Area'
        ],
        [
            'Dark Lumberjack Area'
        ]
    ),
    ("West Mountain", "Regular"): (
        [
            0x03, 0x43
        ],
        [
            'West Death Mountain (Top)',
            'Spectacle Rock Ledge',
            'West Death Mountain (Bottom)'
        ],
        [
            'West Dark Death Mountain (Top)',
            'GT Approach',
            'West Dark Death Mountain (Bottom)'
        ]
    ),
    ("East Mountain", "Regular"): (
        [
            0x05, 0x45
        ],
        [
            'Death Mountain Floating Island',
            'East Death Mountain (Top West)',
            'East Death Mountain (Top East)',
            'Spiral Cave Ledge',
            'Mimic Cave Ledge',
            'Fairy Ascension Ledge',
            'Fairy Ascension Plateau',
            'East Death Mountain (Bottom Left)',
            'East Death Mountain (Bottom)'
        ],
        [
            'East Dark Death Mountain (Top)',
            'East Dark Death Mountain (Bottom Left)',
            'East Dark Death Mountain (Bottom)'
        ]
    ),
    ("East Mountain", "Entrance"): (
        [
            0x07, 0x47
        ],
        [
            'Death Mountain TR Pegs',
            'Death Mountain TR Pegs Ledge'
        ],
        [
            'Turtle Rock Area',
            'Turtle Rock Ledge'
        ]
    ),
    ("Lake", "Regular"): (
        [
            0x0f, 0x35, 0x4f, 0x75, 0x81
        ],
        [
            'Zora Waterfall Area',
            'Zora Waterfall Water',
            'Waterfall of Wishing Cave',
            'Zoras Domain',
            'Lake Hylia Area',
            'Lake Hylia South Shore',
            'Lake Hylia Northeast Bank',
            'Lake Hylia Central Island',
            'Lake Hylia Island',
            'Lake Hylia Water'
        ],
        [
            'Catfish Area',
            'Ice Lake Area',
            'Ice Lake Northeast Bank',
            'Ice Lake Ledge (West)',
            'Ice Lake Ledge (East)',
            'Ice Lake Water',
            'Ice Lake Moat',
            'Ice Palace Area'
        ]
    ),
    ("West Mountain", "Entrance"): (
        [
            0x0a, 0x4a
        ],
        [
            'Mountain Entry Area',
            'Mountain Entry Entrance',
            'Mountain Entry Ledge'
        ],
        [
            'Bumper Cave Area',
            'Bumper Cave Entrance',
            'Bumper Cave Ledge'
        ]
    ),
    ("Woods Pass", "Regular"): (
        [
            0x10, 0x50
        ],
        [
            'Lost Woods Pass West Area',
            'Lost Woods Pass East Top Area',
            'Lost Woods Pass East Bottom Area'
        ],
        [
            'Skull Woods Pass West Area',
            'Skull Woods Pass East Top Area',
            'Skull Woods Pass East Bottom Area'
        ]
    ),
    ("Fortune", "Regular"): (
        [
            0x11, 0x51
        ],
        [
            'Kakariko Fortune Area'
        ],
        [
            'Dark Fortune Area'
        ]
    ),
    ("Whirlpools", "Regular"): (
        [
            0x12, 0x15, 0x33, 0x3f, 0x52, 0x55, 0x73, 0x7f
        ],
        [
            'Kakariko Pond Area',
            'River Bend Area',
            'River Bend East Bank',
            'River Bend Water',
            'C Whirlpool Area',
            'C Whirlpool Water',
            'C Whirlpool Outer Area',
            'Octoballoon Area',
            'Octoballoon Water',
            'Octoballoon Water Ledge'
        ],
        [
            'Outcast Pond Area',
            'Qirn Jump Area',
            'Qirn Jump East Bank',
            'Qirn Jump Water',
            'Dark C Whirlpool Area',
            'Dark C Whirlpool Water',
            'Dark C Whirlpool Outer Area',
            'Bomber Corner Area',
            'Bomber Corner Water',
            'Bomber Corner Water Ledge'
        ]
    ),
    ("Castle", "Entrance"): (
        [
            0x13, 0x14, 0x53, 0x54
        ],
        [
            'Sanctuary Area',
            'Bonk Rock Ledge',
            'Graveyard Area',
            'Graveyard Ledge',
            'Kings Grave Area'
        ],
        [
            'Dark Chapel Area',
            'Dark Graveyard Area'
        ]
    ),
    ("Castle", "Regular"): (
        [
            0x1a, 0x1b, 0x5a, 0x5b
        ],
        [
            'Forgotten Forest Area',
            'Hyrule Castle Area',
            'Hyrule Castle Southwest',
            'Hyrule Castle Courtyard',
            'Hyrule Castle Courtyard Northeast',
            'Hyrule Castle Ledge',
            'Hyrule Castle East Entry'
        ],
        [
            'Shield Shop Area',
            'Shield Shop Fence',
            'Pyramid Area',
            'Pyramid Exit Ledge',
            'Pyramid Pass'
        ]
    ),
    ("Witch", "Regular"): (
        [
            0x16, 0x56
        ],
        [
            'Potion Shop Area',
            'Potion Shop Northeast',
            'Potion Shop Water'
        ],
        [
            'Dark Witch Area',
            'Dark Witch Northeast',
            'Dark Witch Water'
        ]
    ),
    ("Water Approach", "Regular"): (
        [
            0x17, 0x57
        ],
        [
            'Zora Approach Area',
            'Zora Approach Ledge',
            'Zora Approach Water'
        ],
        [
            'Catfish Approach Area',
            'Catfish Approach Ledge',
            'Catfish Approach Water'
        ]
    ),
    ("Village", "Regular"): (
        [
            0x18, 0x58
        ],
        [
            'Kakariko Area',
            'Kakariko Southwest',
            'Kakariko Grass Yard'
        ],
        [
            'Village of Outcasts Area',
            'Dark Grassy Lawn'
        ]
    ),
    ("Wooden Bridge", "Regular"): (
        [
            0x1d, 0x5d
        ],
        [
            'Wooden Bridge Area',
            'Wooden Bridge Northeast',
            'Wooden Bridge Water'
        ],
        [
            'Broken Bridge Area',
            'Broken Bridge Northeast',
            'Broken Bridge West',
            'Broken Bridge Water'
        ]
    ),
    ("Eastern", "Regular"): (
        [
            0x1e, 0x5e
        ],
        [
            'Eastern Palace Area'
        ],
        [
            'Palace of Darkness Area'
        ]
    ),
    ("Blacksmith", "Regular"): (
        [
            0x22, 0x62
        ],
        [
            'Blacksmith Area',
            'Bat Cave Ledge'
        ],
        [
            'Hammer Pegs Area',
            'Hammer Pegs Entry'
        ]
    ),
    ("Dunes", "Regular"): (
        [
            0x25, 0x65
        ],
        [
            'Sand Dunes Area'
        ],
        [
            'Dark Dunes Area'
        ]
    ),
    ("Game", "Regular"): (
        [
            0x28, 0x29, 0x68, 0x69
        ],
        [
            'Maze Race Area',
            'Maze Race Ledge',
            'Maze Race Prize',
            'Kakariko Suburb Area'
        ],
        [
            'Dig Game Area',
            'Dig Game Ledge',
            'Frog Area',
            'Frog Prison',
            'Archery Game Area'
        ]
    ),
    ("Grove", "Regular"): (
        [
            0x2a, 0x6a
        ],
        [
            'Flute Boy Area',
            'Flute Boy Pass'
        ],
        [
            'Stumpy Area',
            'Stumpy Pass'
        ]
    ),
    ("Central Bonk Rocks", "Regular"): (
        [
            0x2b, 0x6b
        ],
        [
            'Central Bonk Rocks Area'
        ],
        [
            'Dark Bonk Rocks Area'
        ]
    ),
    # ("Links", "Regular"): (
    #     [
    #         0x2c, 0x6c
    #     ],
    #     [
    #         'Links House Area'
    #     ],
    #     [
    #         'Big Bomb Shop Area'
    #     ]
    # ),
    ("Tree Line", "Regular"): (
        [
            0x2e, 0x6e
        ],
        [
            'Tree Line Area',
            'Tree Line Water'
        ],
        [
            'Dark Tree Line Area',
            'Dark Tree Line Water'
        ]
    ),
    ("Nook", "Regular"): (
        [
            0x2f, 0x6f
        ],
        [
            'Eastern Nook Area'
        ],
        [
            'Palace of Darkness Nook Area'
        ]
    ),
    ("Desert", "Regular"): (
        [
            0x30, 0x3a, 0x70, 0x7a
        ],
        [
            'Desert Area',
            'Desert Ledge',
            'Desert Palace Entrance (North) Spot',
            'Desert Checkerboard Ledge',
            'Desert Palace Stairs',
            'Desert Palace Mouth',
            'Desert Palace Teleporter Ledge',
            'Bombos Tablet Ledge',
            'Desert Pass Area',
            'Desert Pass Southeast',
            'Desert Pass Ledge'
        ],
        [
            'Misery Mire Area',
            'Misery Mire Teleporter Ledge',
            'Swamp Nook Area'
        ]
    ),
    ("Grove Approach", "Regular"): (
        [
            0x32, 0x72
        ],
        [
            'Flute Boy Approach Area',
            'Flute Boy Bush Entry',
            'Cave 45 Ledge'
        ],
        [
            'Stumpy Approach Area',
            'Stumpy Approach Bush Entry'
        ]
    ),
    ("Hype", "Regular"): (
        [
            0x34, 0x74
        ],
        [
            'Statues Area',
            'Statues Water'
        ],
        [
            'Hype Cave Area',
            'Hype Cave Water'
        ]
    ),
    ("Shopping Mall", "Regular"): (
        [
            0x37, 0x77
        ],
        [
            'Ice Cave Area'
        ],
        [
            'Shopping Mall Area'
        ]
    ),
    ("Swamp", "Regular"): (
        [
            0x3b, 0x7b
        ],
        [
            'Dam Area'
        ],
        [
            'Swamp Area'
        ]
    ),
    ("South Pass", "Regular"): (
        [
            0x3c, 0x7c
        ],
        [
            'South Pass Area'
        ],
        [
            'Dark South Pass Area'
        ]
    )
}

parallel_links = bidict({'Lost Woods SW': 'Skull Woods SW',
                        'Lost Woods SC': 'Skull Woods SC',
                        'Lost Woods SE': 'Skull Woods SE',
                        'Lost Woods EN': 'Skull Woods EN',
                        'Lumberjack SW': 'Dark Lumberjack SW',
                        'Lumberjack WN': 'Dark Lumberjack WN',
                        'West Death Mountain EN': 'West Dark Death Mountain EN',
                        'West Death Mountain ES': 'West Dark Death Mountain ES',
                        'East Death Mountain WN': 'East Dark Death Mountain WN',
                        'East Death Mountain WS': 'East Dark Death Mountain WS',
                        'East Death Mountain EN': 'East Dark Death Mountain EN',
                        'Death Mountain TR Pegs WN': 'Turtle Rock WN',
                        'Mountain Entry NW': 'Bumper Cave NW',
                        'Mountain Entry SE': 'Bumper Cave SE',
                        'Zora Waterfall SE': 'Catfish SE',
                        'Lost Woods Pass NW': 'Skull Woods Pass NW',
                        'Lost Woods Pass NE': 'Skull Woods Pass NE',
                        'Lost Woods Pass SW': 'Skull Woods Pass SW',
                        'Lost Woods Pass SE': 'Skull Woods Pass SE',
                        'Kakariko Fortune NE': 'Dark Fortune NE',
                        'Kakariko Fortune SC': 'Dark Fortune SC',
                        'Kakariko Fortune EN': 'Dark Fortune EN',
                        'Kakariko Fortune ES': 'Dark Fortune ES',
                        'Kakariko Pond NE': 'Outcast Pond NE',
                        'Kakariko Pond SW': 'Outcast Pond SW',
                        'Kakariko Pond SE': 'Outcast Pond SE',
                        'Kakariko Pond WN': 'Outcast Pond WN',
                        'Kakariko Pond WS': 'Outcast Pond WS',
                        'Kakariko Pond EN': 'Outcast Pond EN',
                        'Kakariko Pond ES': 'Outcast Pond ES',
                        'Sanctuary WN': 'Dark Chapel WN',
                        'Sanctuary WS': 'Dark Chapel WS',
                        'Sanctuary EC': 'Dark Chapel EC',
                        'Graveyard WC': 'Dark Graveyard WC',
                        'Graveyard EC': 'Dark Graveyard EC',
                        'River Bend SW': 'Qirn Jump SW',
                        'River Bend SC': 'Qirn Jump SC',
                        'River Bend SE': 'Qirn Jump SE',
                        'River Bend WC': 'Qirn Jump WC',
                        'River Bend EN': 'Qirn Jump EN',
                        'River Bend EC': 'Qirn Jump EC',
                        'River Bend ES': 'Qirn Jump ES',
                        'Potion Shop WN': 'Dark Witch WN',
                        'Potion Shop WC': 'Dark Witch WC',
                        'Potion Shop WS': 'Dark Witch WS',
                        'Potion Shop EN': 'Dark Witch EN',
                        'Potion Shop EC': 'Dark Witch EC',
                        'Zora Approach NE': 'Catfish Approach NE',
                        'Zora Approach WN': 'Catfish Approach WN',
                        'Zora Approach WC': 'Catfish Approach WC',
                        'Kakariko NW': 'Village of Outcasts NW',
                        'Kakariko NC': 'Village of Outcasts NC',
                        'Kakariko NE': 'Village of Outcasts NE',
                        'Kakariko SE': 'Village of Outcasts SE',
                        'Kakariko ES': 'Village of Outcasts ES',
                        'Forgotten Forest NW': 'Shield Shop NW',
                        'Forgotten Forest NE': 'Shield Shop NE',
                        'Hyrule Castle SW': 'Pyramid SW',
                        'Hyrule Castle SE': 'Pyramid SE',
                        'Hyrule Castle ES': 'Pyramid ES',
                        'Wooden Bridge NW': 'Broken Bridge NW',
                        'Wooden Bridge NC': 'Broken Bridge NC',
                        'Wooden Bridge NE': 'Broken Bridge NE',
                        'Wooden Bridge SW': 'Broken Bridge SW',
                        'Eastern Palace SW': 'Palace of Darkness SW',
                        'Eastern Palace SE': 'Palace of Darkness SE',
                        'Blacksmith WS': 'Hammer Pegs WS',
                        'Sand Dunes NW': 'Dark Dunes NW',
                        'Sand Dunes SC': 'Dark Dunes SC',
                        'Sand Dunes WN': 'Dark Dunes WN',
                        'Maze Race ES': 'Dig Game ES',
                        'Kakariko Suburb NE': 'Frog NE',
                        'Kakariko Suburb WS': 'Frog WS',
                        'Kakariko Suburb ES': 'Frog ES',
                        'Flute Boy SW': 'Stumpy SW',
                        'Flute Boy SC': 'Stumpy SC',
                        'Flute Boy WS': 'Stumpy WS',
                        'Central Bonk Rocks NW': 'Dark Bonk Rocks NW',
                        'Central Bonk Rocks SW': 'Dark Bonk Rocks SW',
                        'Central Bonk Rocks EN': 'Dark Bonk Rocks EN',
                        'Central Bonk Rocks EC': 'Dark Bonk Rocks EC',
                        'Central Bonk Rocks ES': 'Dark Bonk Rocks ES',
                        'Links House NE': 'Big Bomb Shop NE',
                        'Links House SC': 'Big Bomb Shop SC',
                        'Links House WN': 'Big Bomb Shop WN',
                        'Links House WC': 'Big Bomb Shop WC',
                        'Links House WS': 'Big Bomb Shop WS',
                        'Links House ES': 'Big Bomb Shop ES',
                        'Stone Bridge NC': 'Hammer Bridge NC',
                        'Stone Bridge SC': 'Hammer Bridge SC',
                        'Stone Bridge WS': 'Hammer Bridge WS',
                        'Stone Bridge EN': 'Hammer Bridge EN',
                        'Stone Bridge EC': 'Hammer Bridge EC',
                        'Tree Line NW': 'Dark Tree Line NW',
                        'Tree Line SC': 'Dark Tree Line SC',
                        'Tree Line SE': 'Dark Tree Line SE',
                        'Tree Line WN': 'Dark Tree Line WN',
                        'Tree Line WC': 'Dark Tree Line WC',
                        'Eastern Nook NE': 'Palace of Darkness Nook NE',
                        'Flute Boy Approach NW': 'Stumpy Approach NW',
                        'Flute Boy Approach NC': 'Stumpy Approach NC',
                        'Flute Boy Approach EC': 'Stumpy Approach EC',
                        'C Whirlpool NW': 'Dark C Whirlpool NW',
                        'C Whirlpool SC': 'Dark C Whirlpool SC',
                        'C Whirlpool WC': 'Dark C Whirlpool WC',
                        'C Whirlpool EN': 'Dark C Whirlpool EN',
                        'C Whirlpool EC': 'Dark C Whirlpool EC',
                        'C Whirlpool ES': 'Dark C Whirlpool ES',
                        'Statues NC': 'Hype Cave NC',
                        'Statues SC': 'Hype Cave SC',
                        'Statues WN': 'Hype Cave WN',
                        'Statues WC': 'Hype Cave WC',
                        'Statues WS': 'Hype Cave WS',
                        'Lake Hylia NW': 'Ice Lake NW',
                        'Lake Hylia NC': 'Ice Lake NC',
                        'Lake Hylia NE': 'Ice Lake NE',
                        'Lake Hylia WS': 'Ice Lake WS',
                        'Lake Hylia EC': 'Ice Lake EC',
                        'Lake Hylia ES': 'Ice Lake ES',
                        'Ice Cave SW': 'Shopping Mall SW',
                        'Ice Cave SE': 'Shopping Mall SE',
                        'Desert Pass EC': 'Swamp Nook EC',
                        'Desert Pass ES': 'Swamp Nook ES',
                        'Dam NC': 'Swamp NC',
                        'Dam WC': 'Swamp WC',
                        'Dam WS': 'Swamp WS',
                        'Dam EC': 'Swamp EC',
                        'South Pass WC': 'Dark South Pass WC',
                        'South Pass NC': 'Dark South Pass NC',
                        'South Pass ES': 'Dark South Pass ES',
                        'Octoballoon NW': 'Bomber Corner NW',
                        'Octoballoon NE': 'Bomber Corner NE',
                        'Octoballoon WC': 'Bomber Corner WC',
                        'Octoballoon WS': 'Bomber Corner WS'
                        })