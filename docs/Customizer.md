## Customizer Files

A customizer file is [yaml file](https://yaml.org/) with different settings. This documentation is intended to be read with an [example customizer file](customizer_example.yaml).

This can also be used to roll a mystery or mutli-mystery seed via the GUI. [Example](multi_mystery_example.yaml)

The cli includes a couple arguments to help:

`--print_custom_yaml` will create a yaml file based on the seed rolled. Treat it like a spoiler.

`--customizer` takes a file as an argument. 

Present on the GUI as `Print Customizer File` and `Customizer File` on the Generation Setup tab.

### meta

Supported values:

* `players`: number of players
* `seed`: you can set the seed number for a set experience on things that are randomized instead of specified
* `algorithm`: fill algorithm
* `names`: for naming mutliworld players

###### Not Yet Implemented

* `mystery`: indicates the seed should be treated as a mystery (hides total collection_rate) (This may end up player specific)

### settings

This must be defined by player. Each player number should be listed with the appropriate settings.

in each player section you can set up default settings for that player or you can specify a mystery yaml file.

```
1: player1.yaml 
2:
  shuffle: crossed
  door_shuffle: basic   
```

Player 1's settings will be determined by rolling the mystery weights and player 2's setting will be default except for those two specified in his section. Each setting should be consistent with the CLI arguments. Simple weighted settings are supported here. If you need sub-weights though, use a separate yaml file.

Start inventory is not supported here. It has a separate section.

###### Not Yet Implemented

Rom/Adjust flags like sprite, quickswap are not outputing with the print_custom_yaml settings 

### item_pool

This must be defined by player. Each player number should be listed with the appropriate pool.

Then each player can have the entire item pool defined. The name of item should be followed by the number of that item in the pool. Many key items will be added to the pool if not detected.

`Bottle (Random)` is supported to randomize bottle contents according to those allowed by difficulty. Pendants and crystals are supported here.


##### Caveat 
 
Dungeon items amount can be increased (but not decreased as the minimum of each dungeon item is either pre-determined or calculated by door rando) if the type of dungeon item is not shuffled then it is attempted to be placed in the dungeon. Extra item beyond dungeon capacity not be confined to the dungeon.

### placements

This must be defined by player. Each player number should be listed with the appropriate placement list.

You may list each location for a player and the item you wish to place there. A location name requires to be enclosed by single quotes if the location name contains a `#` (Most pot locations have the `#`). (Currently no location names have both a `'` and a `#` so you don't need to worry about escaping the `'`)
 
 For multiworld you can specify which player the item is for using this syntax:

`<item name>#<player number>`
 
 Example:
 `Pegasus Boots#3` means the boots for player 3.


### advanced_placements

This must be defined by player. Each player number should be listed with the appropriate section. Each section is a list of placement rules. Each placement rule has a specific type.

Supported Types: PlacementGroup, NotPlacmentGroup

#### PlacementGroup

You may define an item, and a list of locations. The locations may be weighted if desired. The item will be placed at one of the listed locations - this currently ignores logic. The item will be placed there. The special location 'Random' indicates that the item should be placed randomly, without any other consideration. This may be repeated for placement of multiple items like multiple bows or swords.

#### NotPlacementGroup

You may define an item and a list of locations that an item should not be placed at. This will apply to all items of that type. The logic is considered for this. If it is otherwise impossible, the item will be considered for the listed locations. This is important for small key layouts mostly, but it will try other locations first. 
 
### entrances

This must be defined by player. Each player number should be listed with the appropriate sections. This section has three primary subsections: `entrances`, `exits`, and `two-way`.

#### two-way

`two-way` should be used for connectors, dungeons that you wish to couple. (as opposite to decoupled in the insanity shuffle). Links house should be placed using this method as is can be decoupled logically. (Haven't tested to see if it works in game). The overworld entrance is listed first, followed by the interior exit that it leads to. (The exit will then be linked to exit at that entrance).

`50 Rupee Cave: Desert Palace Exit (North)` The 50 Rupee entrance leads to Desert North entrance, and leaving there will spit you out at the same place.

#### exits

`exits` is used for the Chris Houlihan Room Exit and connectors and dungeons that you wish to be decoupled from their entrances. Perhaps counter-intuitively, the exit is listed after the entrance from which it emerges.

`Light Hype Fairy: Chris Houlihan Room Exit` leaving Chris Houlihan Room will spit you out at the Light Hype Fairy.

(I can easily switch this syntax around if people would like me too) 

#### entrances

`entrances` is used for single entrances caves, houses, shops, etc. and drops. Single entrance caves always exit to where you enter, they cannot be decoupled. Dungeons and connectors which are decoupled can also be listed here.

`Chicken House: Kakariko Shop` if you walk into Chicken House door, you will in the Kakariko Shop.

##### Known Issues

Chris Houlihan and Links House should be specified together or not at all. 

### doors

This must be defined by player. Each player number should be listed with the appropriate sections. This section has three primary subsections: `lobbies` and `doors`.

`lobbies` lists the doors by which each dungeon is entered

`<lobby name>: <door name>` Ex. `Turtle Rock Chest: TR Lava Escape SE`

`doors` lists pairs of doors. The first door name is listed is the key. The value of this object may be the paired door name or optionally it can have two properties: `dest` and `type`. If you want a type, you must use the second option. 

The destination door is listed under `dest`
Supported `type`s are `Key Door`, `Bomb Door`, and `Dash Door`

Here are the two examples of the syntax:

```Hyrule Dungeon Guardroom Abyss Edge: Hyrule Castle Lobby W```
```
Sewers Rat Path WS:
        dest: Sewers Secret Room ES
        two-way: true
        type: Key Door
```

You'll note that sub-tile door do not need to be listed, but if you want them to be key doors you will have to list them.
 
 ###### Not Yet Implemented
 
 `one-way` to indicate decoupled doors
 
 ##### Known Issue
 
 If you specify a door type and those doors cannot be a stateful door due to the nature of the supertile (or you've placed too many on the supertile) an exception is thrown. 

### medallions

This must be defined by player. Each player number should be listed with the appropriate info.

Example:
```
Misery Mire: Ether
Turtle Rock: Quake
```

Leave blank or omit if you wish it to be random. Alternatively, a weighted dictionary is supported and a 'Random' option

### bosses

This must be defined by player. Each player number should be listed with the appropriate boss list.

This is done as `<dungeon>: <boss>`

E.g. `Skull Woods: Helmasaur King` for helmacopter. Be sure to turn on at least one enemizer setting for the bosses to actually be randomized.

### start_inventory

This must be defined by player. Each player number should be listed with a list of items to start with.

This is a yaml list (note the hyphens):

```
start_inventory:
    1:
      - Pegasus Boots
      - Progressive Sword
```

To start with multiple copies of progressive items, list them more than once.

##### Known Issue

This conflicts with the mystery yaml, if specified. These start inventory items will be added after those are added.

### drops

This must be defined by player. You may have prize packs, tree pulls, crab drops, stun prizes, and the fish prize defined using the following keys:
```
drops:
   1: 
     Pack 1
     - Small Heart
     - Bombs (4)
     - Random
     - etc
    Pack 2: (list)
    ...
    Pack 7: (list)
    Tree Pull Tier 1: Single Bomb
    Tree Pull Tier 2: Arrows (10)
    Tree Pull Tier 3: Fairy
    Crab Normal: Rupees (20)
    Crab Special: Small Magic
    Stun Prize: Bombs (8)
    Fish: Big Magic
```

Prize packs expect a list of eight items each (anything not specified will be whatever randomization would have normally occurred). The special drops expect a single item. Packs 1 through 7 are supported. Prize pack 0 is not customizable.