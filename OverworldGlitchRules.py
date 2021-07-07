"""
Helper functions to deliver entrance/exit/region sets to OWG rules.
"""

from BaseClasses import Entrance


def get_sword_required_superbunny_mirror_regions():
    """
    Cave regions that superbunny can get through - but only with a sword.
    """
    yield 'Spiral Cave (Top)'

def get_boots_required_superbunny_mirror_regions():
    """
    Cave regions that superbunny can get through - but only with boots.
    """
    yield 'Two Brothers House'

def get_boots_required_superbunny_mirror_locations():
    """
    Cave locations that superbunny can access - but only with boots.
    """
    yield 'Sahasrahla\'s Hut - Left'
    yield 'Sahasrahla\'s Hut - Middle'
    yield 'Sahasrahla\'s Hut - Right'


def get_invalid_mirror_bunny_entrances():
    """
    Entrances that can't be superbunny-mirrored into.
    """
    yield 'Skull Woods Final Section'
    yield 'Hype Cave'
    yield 'Bonk Fairy (Dark)'
    yield 'Thieves Town'
    yield 'Dark World Hammer Peg Cave'
    yield 'Brewery'
    yield 'Hookshot Cave'
    yield 'Dark Lake Hylia Ledge Fairy'
    yield 'Dark Lake Hylia Ledge Spike Cave'
    yield 'Palace of Darkness'
    yield 'Misery Mire'
    yield 'Turtle Rock'
    yield 'Bonk Rock Cave'
    yield 'Bonk Fairy (Light)'
    yield '50 Rupee Cave'
    yield '20 Rupee Cave'
    yield 'Checkerboard Cave'
    yield 'Light Hype Fairy'
    yield 'Waterfall of Wishing'
    yield 'Light World Bomb Hut'
    yield 'Mini Moldorm Cave'
    yield 'Ice Rod Cave'
    yield 'Sanctuary Grave'
    yield 'Kings Grave'
    yield 'Sanctuary Grave'
    yield 'Hyrule Castle Secret Entrance Drop'
    yield 'Skull Woods Second Section Hole'
    yield 'Skull Woods First Section Hole (North)'


def get_superbunny_accessible_locations():
    """
    Interior locations that can be accessed with superbunny state.
    """

    yield 'Waterfall of Wishing - Left'
    yield 'Waterfall of Wishing - Right'
    yield 'King\'s Tomb'
    yield 'Floodgate'
    yield 'Floodgate Chest'
    yield 'Cave 45'
    yield 'Bonk Rock Cave'
    yield 'Brewery'
    yield 'C-Shaped House'
    yield 'Chest Game'
    yield 'Mire Shed - Left'
    yield 'Mire Shed - Right'
    yield 'Secret Passage'
    yield 'Ice Rod Cave'
    yield 'Pyramid Fairy - Left'
    yield 'Pyramid Fairy - Right'
    yield 'Superbunny Cave - Top'
    yield 'Superbunny Cave - Bottom'
    yield 'Blind\'s Hideout - Left'
    yield 'Blind\'s Hideout - Right'
    yield 'Blind\'s Hideout - Far Left'
    yield 'Blind\'s Hideout - Far Right'
    yield 'Kakariko Well - Left'
    yield 'Kakariko Well - Middle'
    yield 'Kakariko Well - Right'
    yield 'Kakariko Well - Bottom'
    yield 'Kakariko Tavern'
    yield 'Library'
    yield 'Spiral Cave'
    for location in get_boots_required_superbunny_mirror_locations():
        yield location


def get_non_mandatory_exits(inverted):
    """
    Entrances that can be reached with full equipment using overworld glitches and don't need to be an exit.
    The following are still be mandatory exits:

    Open:
    Turtle Rock Isolated Ledge Entrance
    Skull Woods Second Section Door (West) (or Skull Woods Final Section)

    Inverted:
    Two Brothers House (West)
    Desert Palace Entrance (East)
    """

    yield 'Bumper Cave (Top)'
    yield 'Death Mountain Return Cave (West)'
    yield 'Hookshot Cave Back Entrance'

    if inverted:
        yield 'Desert Palace Entrance (North)'
        yield 'Desert Palace Entrance (West)'
        yield 'Agahnims Tower'
        yield 'Hyrule Castle Entrance (West)'
        yield 'Hyrule Castle Entrance (East)'
    else:
        yield 'Dark Death Mountain Ledge (West)'
        yield 'Dark Death Mountain Ledge (East)'
        yield 'Mimic Cave'
        yield 'Desert Palace Entrance (East)'


def get_boots_clip_exits_lw(inverted = False):
    """
    Special Light World region exits that require boots clips.
    """

    yield ('Lumberjack DMA Clip', 'Lumberjack Area', 'West Death Mountain (Bottom)')
    yield ('Lumberjack DMD Clip', 'West Death Mountain (Top)', 'Lumberjack Area')
    yield ('DM Glitched Bridge Clip', 'West Death Mountain (Bottom)', 'East Death Mountain (Top East)')
    yield ('WDM to EDM Top Clip', 'West Death Mountain (Top)', 'East Death Mountain (Top West)')
    yield ('Hera Ascent Clip', 'West Death Mountain (Bottom)', 'West Death Mountain (Top)') #cannot guarantee camera correction, but a bomb clip exists
    yield ('Sanctuary DMD Clip', 'West Death Mountain (Bottom)', 'Sanctuary Area')
    yield ('Graveyard Ledge DMD Clip', 'West Death Mountain (Bottom)', 'Graveyard Ledge')
    yield ('Kings Grave DMD Clip', 'West Death Mountain (Bottom)', 'Kings Grave Area')
    yield ('EDM to WDM Top Clip', 'East Death Mountain (Top West)', 'West Death Mountain (Top)')
    yield ('EDM East Dropdown Clip', 'East Death Mountain (Top East)', 'East Death Mountain (Bottom Left)')
    yield ('EDM To TR Pegs Clip', 'East Death Mountain (Top East)', 'Death Mountain TR Pegs')
    yield ('EDM DMD FAWT Clip', 'East Death Mountain (Bottom)', 'Potion Shop Area')
    yield ('WDM To EDM Bottom Clip', 'East Death Mountain (Bottom Left)', 'East Death Mountain (Bottom)')
    yield ('WDM DMD To River Bend Clip', 'East Death Mountain (Bottom Left)', 'River Bend Area')
    yield ('EDM DMD To River Bend Clip', 'East Death Mountain (Bottom)', 'River Bend Area')
    yield ('TR Pegs Ledge Clip', 'Death Mountain TR Pegs', 'Death Mountain TR Pegs Ledge')
    yield ('TR Pegs To EDM Clip', 'Death Mountain TR Pegs', 'East Death Mountain (Top East)')
    yield ('Zora DMD Clip', 'Death Mountain TR Pegs', 'Zora Waterfall Area')
    yield ('Mountain Entry To Ledge Clip', 'Mountain Entry Area', 'Death Mountain Return Ledge')
    yield ('Mountain Ledge Drop Clip', 'Death Mountain Return Ledge', 'Death Mountain Entrance')
    yield ('Mountain Entry To Pond Clip', 'Mountain Entry Area', 'Kakariko Pond Area')
    yield ('Zora Waterfall Ledge Clip', 'Zora Waterfall Area', 'Zora Approach Area')
    
    #yield ('Pond DMA Clip', 'Kakariko Pond Area', 'West Death Mountain (Bottom)') #cannot guarantee camera correction
    yield ('Pond To Mountain Entry Clip', 'Kakariko Pond Area', 'Mountain Entry Area')
    yield ('Pond To Bonk Rocks Clip', 'Kakariko Pond Area', 'Bonk Rock Ledge')
    yield ('River Bend To Potion Shop Clip', 'River Bend East Bank', 'Potion Shop Area')
    yield ('River Bend To Wooden Bridge Clip', 'River Bend East Bank', 'Wooden Bridge Area')
    yield ('Potion Shop To EP Clip', 'Potion Shop Area', 'Eastern Palace Area')
    yield ('Potion Shop To River Bend Clip', 'Potion Shop Area', 'River Bend East Bank')
    yield ('Potion Shop To Zora Approach Clip', 'Potion Shop Northeast', 'Zora Approach Area')
    yield ('Zora Approach To Potion Shop Clip', 'Zora Approach Area', 'Potion Shop Area')
    
    yield ('Kakariko Bomb Hut Clip', 'Kakariko Area', 'Maze Race Area')
    yield ('Forgotten Forest To Blacksmith Clip', 'Forgotten Forest Area', 'Blacksmith Area') #fake flipper
    yield ('Hyrule Castle To Blacksmith Clip', 'Hyrule Castle Area', 'Blacksmith Area') #fake flipper
    yield ('Wooden Bridge To Dunes Clip', 'Wooden Bridge Area', 'Sand Dunes Area')
    yield ('Eastern Palace To Zora Approach Clip', 'Eastern Palace Area', 'Zora Approach Area')
    yield ('Eastern Palace To Nook Clip', 'Eastern Palace Area', 'Eastern Nook Area')
    yield ('Eastern Palace To Cliff Clip', 'Eastern Palace Area', 'Eastern Cliff')
    #yield ('Bat Cave River Clip Spot', 'Blacksmith Area', 'Bat Cave Ledge') #cannot guarantee camera correction
    yield ('Sand Dunes To Cliff Clip', 'Sand Dunes Area', 'Eastern Cliff')
    
    yield ('Maze Race Item Get Ledge Clip', 'Maze Race Area', 'Maze Race Prize')
    yield ('Maze Race To Desert Ledge Clip', 'Maze Race Area', 'Desert Ledge')
    yield ('Maze Race To Desert Boss Clip', 'Maze Race Area', 'Desert Palace Entrance (North) Spot')
    yield ('Suburb To Cliff Clip', 'Kakariko Suburb Area', 'Desert Northeast Cliffs')
    yield ('Central Bonk Rocks To Cliff Clip', 'Central Bonk Rocks Area', 'Central Cliffs')
    yield ('Links House To Cliff Clip', 'Links House Area', 'Central Cliffs')
    yield ('Stone Bridge To Cliff Clip', 'Stone Bridge Area', 'Central Cliffs')
    yield ('Tree Line Water Clip', 'Tree Line Area', 'Tree Line Water') #requires flippers
    yield ('Eastern Nook To Eastern Clip', 'Eastern Nook Area', 'Eastern Palace Area')
    yield ('Eastern Nook To Ice Cave FAWT Clip', 'Eastern Nook Area', 'Ice Cave Area')
    
    yield ('Desert To Maze Race Clip', 'Desert Ledge', 'Maze Race Area')
    yield ('Desert Ledge To Cliff Clip', 'Desert Ledge', 'Desert Northeast Cliffs') #requires gloves
    yield ('Checkerboard To Cliff Clip', 'Desert Checkerboard Ledge', 'Desert Northeast Cliffs')
    yield ('Desert To Cliff Clip', 'Desert Area', 'Desert Northeast Cliffs')
    yield ('Desert To Teleporter Clip', 'Desert Area', 'Desert Palace Teleporter Ledge')
    yield ('Desert To Bombos Tablet Clip', 'Desert Area', 'Bombos Tablet Ledge')
    
    yield ('Flute Boy To Cliff Clip', 'Flute Boy Approach Area', 'Desert Northeast Cliffs')
    yield ('Cave 45 To Cliff Clip', 'Cave 45 Ledge', 'Desert Northeast Cliffs')
    yield ('C Whirlpool To Cliff Clip', 'C Whirlpool Area', 'Central Cliffs')
    yield ('C Whirlpool Outer To Cliff Clip', 'C Whirlpool Outer Area', 'Central Cliffs')
    yield ('Statues To Cliff Clip', 'Statues Area', 'Central Cliffs')
    yield ('Lake Hylia To Statues Clip', 'Lake Hylia Area', 'Statues Area')
    yield ('Lake Hylia To South Pass Clip', 'Lake Hylia Area', 'South Pass Area')
    yield ('Lake Hylia To Shore Clip', 'Lake Hylia Area', 'Lake Hylia South Shore')
    yield ('Desert Pass To Cliff Clip', 'Desert Pass Area', 'Desert Northeast Cliffs')
    yield ('Desert Pass Southeast To Cliff Clip', 'Desert Pass Southeast', 'Desert Northeast Cliffs')
    #yield ('Desert Pass To Zora Clip', 'Desert Pass Area', 'Zoras Domain') #revisit when Zora is shuffled
    yield ('Dam To Cliff Clip', 'Dam Area', 'Desert Northeast Cliffs')
    yield ('South Pass To Lake Hylia Clip', 'South Pass Area', 'Lake Hylia Area')
    yield ('South Pass To Shore Clip', 'South Pass Area', 'Lake Hylia South Shore')
    #yield ('Octoballoon To Shore Clip', 'Octoballoon Area', 'Lake Hylia South Shore') #map wrap hardlock risk
    
    if not inverted:
        yield ('Spectacle Rock Ledge Clip', 'West Death Mountain (Top)', 'Spectacle Rock Ledge')
        yield ('Floating Island Clip', 'East Death Mountain (Top East)', 'Death Mountain Floating Island')
        yield ('Floating Island Return Clip', 'Death Mountain Floating Island', 'East Death Mountain (Top East)')

def get_boots_clip_exits_dw(inverted):
    """
    Special Dark World region exits that require boots clips.
    """

    yield ('Dark Lumberjack DMA Clip', 'Dark Lumberjack Area', 'West Dark Death Mountain (Bottom)')
    yield ('DDM Glitched Bridge Clip', 'West Dark Death Mountain (Bottom)', 'East Dark Death Mountain (Top)')
    yield ('Chapel DMD Clip', 'West Dark Death Mountain (Bottom)', 'Dark Chapel Area')
    yield ('Dark Graveyard DMD Clip', 'West Dark Death Mountain (Bottom)', 'Dark Graveyard Area')
    yield ('EDDM West Dropdown Clip', 'East Dark Death Mountain (Top)', 'East Dark Death Mountain (West Lip)')
    yield ('EDDM To WDDM Clip', 'East Dark Death Mountain (Top)', 'West Dark Death Mountain (Top)')
    yield ('TR Bridge Clip', 'East Dark Death Mountain (Top)', 'Dark Death Mountain Ledge')
    yield ('Dark Witch DMD FAWT Clip', 'East Dark Death Mountain (Bottom)', 'Dark Witch Area')
    yield ('Qirn Jump DMD Clip', 'East Dark Death Mountain (West Lip)', 'Qirn Jump Area')
    yield ('WDDM To EDDM Clip', 'East Dark Death Mountain (West Lip)', 'East Dark Death Mountain (Bottom)')
    #yield ('DW Floating Island Clip', 'East Dark Death Mountain (Bottom)', 'Dark Death Mountain Floating Island') #cannot guarantee camera correction
    yield ('TR To EDDM Clip', 'Turtle Rock Area', 'East Dark Death Mountain (Top)')
    yield ('Catfish DMD Clip', 'Turtle Rock Area', 'Catfish Area')
    yield ('Bumper Cave Ledge Clip', 'Bumper Cave Area', 'Bumper Cave Ledge')
    yield ('Bumper Cave Ledge Drop Clip', 'Bumper Cave Ledge', 'Bumper Cave Entrance')
    yield ('Bumper Cave To Pond Clip', 'Bumper Cave Area', 'Outcast Pond Area')
    yield ('Catfish Ledge Clip', 'Catfish Area', 'Catfish Approach Area')
    
    #yield ('Dark Pond DMA Clip', 'Outcast Pond Area', 'West Dark Death Mountain (Bottom)') #cannot guarantee camera correction
    yield ('Pond To Bumper Cave Clip', 'Outcast Pond Area', 'Bumper Cave Area')
    yield ('Pond To Chapel Clip', 'Outcast Pond Area', 'Dark Chapel Area')
    yield ('Qirn Jump To Dark Witch Clip', 'Qirn Jump East Bank', 'Dark Witch Area')
    yield ('Qirn Jump To Broken Bridge North Clip', 'Qirn Jump East Bank', 'Broken Bridge Northeast')
    yield ('Qirn Jump To Broken Bridge Clip', 'Qirn Jump East Bank', 'Broken Bridge Area')
    yield ('Dark Witch To PoD Clip', 'Dark Witch Area', 'Palace of Darkness Area')
    yield ('Dark Witch To Qirn Jump Clip', 'Dark Witch Area', 'Qirn Jump East Bank')
    yield ('Dark Witch To Catfish Approach Clip', 'Dark Witch Northeast', 'Catfish Approach Area')
    yield ('Catfish Approach To Dark Witch Clip', 'Catfish Approach Area', 'Dark Witch Area')
    yield ('Catfish Approach To PoD Clip', 'Catfish Approach Area', 'Palace of Darkness Area')
    
    yield ('VoO To Dig Game Clip', 'Village of Outcasts Area', 'Dig Game Area')
    yield ('VoO To Dig Game Hook Clip', 'Village of Outcasts Area', 'Dig Game Ledge') #requires hookshot
    yield ('Broken Bridge To Dunes Clip', 'Broken Bridge West', 'Dark Dunes Area')
    yield ('Broken Bridge To Hammer Pegs Clip', 'Broken Bridge West', 'Hammer Pegs Area') #fake flipper
    yield ('Broken Bridge To Bomb Shop Clip', 'Broken Bridge West', 'Big Bomb Shop Area') #fake flipper
    yield ('PoD To Cliff Clip', 'Palace of Darkness Area', 'Darkness Cliff')
    yield ('Dark Dunes To Cliff Clip', 'Dark Dunes Area', 'Darkness Cliff')
    yield ('Dark Dunes To Hammer Pegs Clip', 'Dark Dunes Area', 'Hammer Pegs Area')
    yield ('Dark Dunes To Bomb Shop Clip', 'Dark Dunes Area', 'Big Bomb Shop Area')
    
    yield ('Dig Game To Mire Clip', 'Dig Game Area', 'Misery Mire Area')
    yield ('Archery Game To Cliff Clip', 'Archery Game Area', 'Mire Northeast Cliffs')
    yield ('Dark Bonk Rocks To Cliff Clip', 'Dark Bonk Rocks Area', 'Dark Central Cliffs')
    yield ('Bomb Shop To Cliff Clip', 'Big Bomb Shop Area', 'Dark Central Cliffs')
    yield ('Bomb Shop To Hammer Bridge FAWT Clip', 'Big Bomb Shop Area', 'Hammer Bridge North Area')
    yield ('Hammer Bridge To Bomb Shop Clip', 'Hammer Bridge North Area', 'Big Bomb Shop Area')
    yield ('Hammer Bridge To Hammer Pegs Clip', 'Hammer Bridge North Area', 'Hammer Pegs Area')
    yield ('Hammer Bridge To Cliff Clip', 'Hammer Bridge South Area', 'Dark Central Cliffs')
    yield ('Dark Tree Line Water Clip', 'Dark Tree Line Area', 'Dark Tree Line Water') #requires flippers
    yield ('PoD Nook To Shopping Mall FAWT Clip', 'Palace of Darkness Nook Area', 'Shopping Mall Area')
    
    yield ('Mire To Cliff Clip', 'Misery Mire Area', 'Mire Northeast Cliffs')
    yield ('Mire To Teleporter Clip', 'Misery Mire Area', 'Misery Mire Teleporter Ledge')
    yield ('Stumpy To Cliff Clip', 'Stumpy Approach Area', 'Mire Northeast Cliffs')
    yield ('Dark C Whirlpool To Cliff Clip', 'Dark C Whirlpool Area', 'Dark Central Cliffs')
    yield ('Dark C Whirlpool Outer To Cliff Clip', 'Dark C Whirlpool Outer Area', 'Dark Central Cliffs')
    yield ('Hype To Cliff Clip', 'Hype Cave Area', 'Dark Central Cliffs')
    yield ('Ice Lake To Hype Clip', 'Ice Lake Area', 'Hype Cave Area')
    yield ('Ice Lake To South Pass Clip', 'Ice Lake Area', 'Dark South Pass Area')
    yield ('Ice Lake To Shore Clip', 'Ice Lake Area', 'Ice Lake Ledge (West)')
    
    yield ('Swamp Nook To Cliff Clip', 'Swamp Nook Area', 'Mire Northeast Cliffs')
    yield ('Swamp To Cliff Clip', 'Swamp Area', 'Mire Northeast Cliffs')
    yield ('South Pass To Ice Lake Clip', 'Dark South Pass Area', 'Ice Lake Area')
    yield ('South Pass To Dark Shore Clip', 'Dark South Pass Area', 'Ice Lake Ledge (West)')
    #yield ('Bomber Corner To Shore Clip', 'Bomber Corner Area', 'Ice Lake Ledge (East)') #map wrap hardlock risk
    
    if not inverted:
        yield ('Ganons Tower Screen Wrap Clip', 'West Dark Death Mountain (Bottom)', 'GT Approach')  # This only gets you to the GT entrance
        yield ('WDDM Bomb Clip', 'West Dark Death Mountain (Bottom)', 'West Dark Death Mountain (Top)') #cannot guarantee camera correction, but a bomb clip exists
        yield ('Turtle Rock Ledge Clip', 'Turtle Rock Area', 'Turtle Rock Ledge')
    else:
        yield ('Misery Mire Teleporter Clip', 'Misery Mire Area', 'Misery Mire Teleporter Ledge')


def get_glitched_speed_drops_lw(inverted = False):
    """
    Light World drop-down ledges that require glitched speed.
    """


def get_glitched_speed_drops_dw(inverted = False):
    """
    Dark World drop-down ledges that require glitched speed.
    """


def get_mirror_clip_spots_dw():
    """
    Out of bounds transitions using the mirror
    """
    yield ('Qirn Jump Bunny DMD Clip', 'East Dark Death Mountain (West Lip)', 'Qirn Jump Area')
    yield ('EDDM Mirror Clip', 'East Dark Death Mountain (West Lip)', 'East Dark Death Mountain (Bottom)')
    yield ('Desert East Mirror Clip', 'Misery Mire Area', 'Desert Palace Mouth')


def get_mirror_offset_spots_dw():
    """
    Mirror shenanigans placing a mirror portal with a broken camera
    """
    yield ('Dark Death Mountain Offset Mirror', 'West Dark Death Mountain (Bottom)', 'Pyramid Area')


def get_mirror_offset_spots_lw(player):
    """
    Mirror shenanigans placing a mirror portal with a broken camera
    """
    #yield ('Death Mountain Offset Mirror', 'West Death Mountain (Bottom)', 'Hyrule Castle Courtyard') #revisit when we can guarantee walk access to Pyramid Area
    #yield ('Death Mountain Offset Mirror (Houlihan Exit)', 'West Death Mountain (Bottom)', 'Hyrule Castle Ledge', lambda state: state.has_Mirror(player) and state.can_boots_clip_dw(player) and state.has_Pearl(player))


def create_owg_connections(world, player):
    """
    Add OWG transitions to player's world without logic
    """
    create_no_logic_connections(player, world, get_boots_clip_exits_lw(world.mode[player] == 'inverted'))
    create_no_logic_connections(player, world, get_boots_clip_exits_dw(world.mode[player] == 'inverted'))

    # Glitched speed drops.
    #create_no_logic_connections(player, world, get_glitched_speed_drops_lw(world.mode[player] == 'inverted'))
    #create_no_logic_connections(player, world, get_glitched_speed_drops_dw(world.mode[player] == 'inverted'))

    # Mirror clip spots.
    if world.mode[player] != 'inverted':
        create_no_logic_connections(player, world, get_mirror_clip_spots_dw())
        create_no_logic_connections(player, world, get_mirror_offset_spots_dw())
    #else:
        #create_no_logic_connections(player, world, get_mirror_offset_spots_lw(player))


def overworld_glitches_rules(world, player):
    # Boots-accessible locations.
    set_owg_rules(player, world, get_boots_clip_exits_lw(world.mode[player] == 'inverted'), lambda state: state.can_boots_clip_lw(player))
    set_owg_rules(player, world, get_boots_clip_exits_dw(world.mode[player] == 'inverted'), lambda state: state.can_boots_clip_dw(player))

    # Glitched speed drops.
    #set_owg_rules(player, world, get_glitched_speed_drops_lw(world.mode[player] == 'inverted'), lambda state: state.can_get_glitched_speed_lw(player))
    #set_owg_rules(player, world, get_glitched_speed_drops_dw(world.mode[player] == 'inverted'), lambda state: state.can_get_glitched_speed_dw(player))

    # Mirror clip spots.
    if world.mode[player] != 'inverted':
        set_owg_rules(player, world, get_mirror_clip_spots_dw(), lambda state: state.has_Mirror(player))
        set_owg_rules(player, world, get_mirror_offset_spots_dw(), lambda state: state.has_Mirror(player) and state.can_boots_clip_lw(player))
    #else:
        #set_owg_rules(player, world, get_mirror_offset_spots_lw(player), lambda state: state.has_Mirror(player) and state.can_boots_clip_dw(player))

    # Regions that require the boots and some other stuff.
    # TODO: Revisit below when we can guarantee water walk
    # if world.mode[player] != 'inverted':
    #     add_alternate_rule(world.get_entrance('Waterfall of Wishing Cave Entry', player), lambda state: state.has_Pearl(player) or state.has_Boots(player))
    # else:
    #     add_alternate_rule(world.get_entrance('Waterfall of Wishing Cave Entry', player), lambda state: state.has_Pearl(player))

    # Zora's Ledge via waterwalk setup.
    #add_alternate_rule(world.get_location('Zora\'s Ledge', player), lambda state: state.has_Boots(player)) #revisit when we can guarantee water walk

    # Regions that can bypass item requirements
    add_alternate_rule(world.get_entrance('DM Hammer Bridge (West)', player), lambda state: state.can_boots_clip_lw(player))
    add_alternate_rule(world.get_entrance('DM Broken Bridge (West)', player), lambda state: state.can_boots_clip_lw(player))
    add_alternate_rule(world.get_entrance('Potion Shop Rock (North)', player), lambda state: state.can_boots_clip_lw(player))
    add_alternate_rule(world.get_entrance('Potion Shop Rock (South)', player), lambda state: state.can_boots_clip_lw(player))
    add_alternate_rule(world.get_entrance('Dark Witch Rock (North)', player), lambda state: state.can_boots_clip_dw(player))
    add_alternate_rule(world.get_entrance('Dark Witch Rock (South)', player), lambda state: state.can_boots_clip_dw(player))

    # Adding additional item requirements to OWG Clips
    add_additional_rule(world.get_entrance('Tree Line Water Clip', player), lambda state: state.has('Flippers', player))
    add_additional_rule(world.get_entrance('Desert Ledge To Cliff Clip', player), lambda state: state.can_lift_rocks(player))
    add_additional_rule(world.get_entrance('VoO To Dig Game Hook Clip', player), lambda state: state.has('Hookshot', player))
    add_additional_rule(world.get_entrance('Dark Tree Line Water Clip', player), lambda state: state.has('Flippers', player))
    

def add_alternate_rule(entrance, rule):
    old_rule = entrance.access_rule
    entrance.access_rule = lambda state: old_rule(state) or rule(state)


def add_additional_rule(entrance, rule):
    old_rule = entrance.access_rule
    entrance.access_rule = lambda state: old_rule(state) and rule(state)


def create_no_logic_connections(player, world, connections):
    for entrance, parent_region, target_region, *rule_override in connections:
        parent = world.get_region(parent_region, player)
        target = world.get_region(target_region, player)
        connection = Entrance(player, entrance, parent)
        parent.exits.append(connection)
        connection.connect(target)


def set_owg_rules(player, world, connections, default_rule):
    for entrance, parent_region, target_region, *rule_override in connections:
        connection = world.get_entrance(entrance, player)
        rule = rule_override[0] if len(rule_override) > 0 else default_rule
        connection.access_rule = rule
