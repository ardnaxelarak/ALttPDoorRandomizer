# Overworld Randomizer

This is a overworld randomizer for _The Legend of Zelda: A Link to the Past_ for the SNES
based on the Door Randomizer found at [Aerinon's Github Project.](https://github.com/Aerinon/ALttPDoorRandomizer)
See https://alttpr.com/ for more details on the normal randomizer.

### Trackers & Guides

This is a very new mode of LTTPR so the tools and info is very limited.
- There is an [OW Rando Cheat Sheet](https://zelda.codemann8.com/images/shared/ow-rando-reference-sheet.png) that shows all the transitions that exist and are candidates for shuffle.
- There is OW tracking capability within the following trackers:
  - [Community Tracker](https://alttptracker.dunka.net/)
  - CodeTracker, an [EmoTracker](https://emotracker.net) package for LTTPR
- There is an [OW OWG Reference Sheet](https://zelda.codemann8.com/images/shared/ow-owg-reference-sheet.png) that shows all the in-logic places where boots/mirror clips and fake flippers are expected from the player.

# Known Issues
(Updated 2021-08-26)

### If you want to playtest this, know these things:
- Big Red Bomb may require bomb duping as ledge drops may be in the way of your path to the Pyramid Fairy crack
- If you fake flipper, beware of transitioning south. You could end up at the top of the waterfall in the southeast of either world. If you mistakenly drop down, it is important to NOT make any other movements and S+Q immediately when the game allows you to (might take several seconds, the game has to scroll back to the original point of water entry) or there will be a hardlock. Falling from the waterfall is avoidable but it is super easy to do as it is super close to the transition.
- In Crossed OW, there are some interesting bunny swimming situations that can occur, these are meant to be out-of-logic but beware of logic bugs around this area. But also, hardlocks can occur; if you take damage, be sure to S+Q immediately before moving in any direction, or you may get an infinite screen wrap glitch.

### Known bugs:
- Screens that loop on itself and also have free-standing items, the sprites are duplicated and can cause item duplication
- When OWG are performed to enter mega-tile screens (large OW screens), there is a small chance that an incorrect VRAM reference value causes the map graphics to offset in increments of 16 pixels

# Feedback and Bug Reports

All feedback and dev conversation happens in the #ow-rando channel on the [ALTTP Randomizer discord](https://discordapp.com/invite/alttprandomizer).

# Installation from Source

Download the source code from the repository directly and put it in a folder of your choosing.

You must have Python installed (version 3.6 - 3.9 supported)

This program requires all python dependencies that are necessary to run Aerinon's Door Randomizer. Try running ```pip install missingdependency``` or ```python -m pip install missingdependency``` on the command line (replace ```missingdependency``` with the specific package that is missing) to install the dependency.

Alternatively, run ```resources/ci/common/local_install.py``` to install all the missing dependencies as well.

See the following link if you have additional trouble: https://github.com/codemann8/ALttPDoorRandomizer/blob/OverworldShuffle/docs/BUILDING.md

# Running the Program

To use the CLI, run ```DungeonRandomizer.py```.

Alternatively, run ```Gui.py``` for a simple graphical user interface.

# Settings

Only extra settings are found here. All door and entrance randomizer settings are supported. See their [readme](https://github.com/Aerinon/ALttPDoorRandomizer/blob/master/README.md)

## Overworld Layout Shuffle (--ow_shuffle)

### Vanilla

OW is not shuffled.

### Parallel

OW Transitions are shuffled, but both worlds will have a matching layout.

### Full

OW Transitions are shuffled within each world separately.

## Crossed Options (--ow_crossed)

This allows OW connections to be shuffled cross-world.

Polar and Grouped both are guaranteed to result in two separated planes of tiles. To navigate to the other plane, you have the following methods: 1) Normal portals 2) Mirroring on DW tiles 3) Fluting to a LW tile that was previously unreachable

Limited and Chaos are not bound to follow a two-plane framework. This means that it could be possible to travel on foot to every tile without entering a normal portal.

See each option to get more details on the differences.

### None

Transitions will remain same-world.

### Polar

Only effective if Mixed/Tile Swap is enabled. Enabling Polar preserves the original/vanilla connections even when tiles are swapped/mixed. This results in a completely vanilla overworld, except that some tiles will transform Link to a Bunny (as per Mixed swapping some tiles to the other world). This offers an interesting twist on Mixed where you have a pre-conditioned knowledge of the terrain you will encounter, but not necessarily be able to do what you need to do there. (see Tile Swap/Mixed section for more details)

### Grouped

This option shuffles connections cross-world in the same manner as Tile Swap/Mixed, the connections leading in and coming out of a group of tiles are crossed. Unlike Polar, this uses a different set of tile groups as a basis of crossing connections, albeit the same rule govern which groups of tiles must cross together (see Tile Swap/Mixed for more details)

### Limited

Every transition independently is a candidate to be chosen as a cross-world connection, however only 9 transitions become crossed (in each world). This option abides by the Keep Similar Edges Together option and will guarantee same effect on all edges in a Similar Edge group if enabled. If a Similar Edge group is chosen from the pool of candidates, it only counts as one portal, not multiple.

Note: Only parallel connections (a connection that also exists in the opposite world) are considered for cross-world connections, which means that the same connection in the opposite world will also connect cross-world.

Motive: Why 9 connections? To imitate the effect of the 9 standard portals that exist.

### Chaos

Same as Limited, except that there is no limit to the number of cross-world connections that are made. Each transition has an equal 50/50 chance of being a crossed connection.

## Keep Similar Edges Together (--ow_keepsimilar)

This keeps similar edge transitions together. ie. The 2 west edges of Potion Shop will be paired to another set of two similar edges

Note: This affects OW Layout Shuffle mostly, but also affects Limited and Chaos modes in Crossed OW.

## Tile Swap / Mixed Overworld (--ow_mixed)

OW tiles are randomly chosen to become a part of the opposite world. When on the Overworld, there will be an L or D in the upper left corner, indicating which world you are currently in. Mirroring still works the same, you must be in the DW to mirror to the LW.

Note: Tiles are put into groups that must be shuffled together when certain settings are enabled. For instance, if ER is disabled, then any tiles that have a connector cave that leads to another tile, those tiles must swap together; (an exception to this is the Old Man Rescue cave which has been modified similar to how Inverted modifies it, Old Man Rescue is ALWAYS accessible from the Light World)

## Flute Shuffle (--ow_fluteshuffle)

When enabled, new flute spots are generated and gives the player the option to cancel out of the flute menu by pressing X.

Note: Desert Teleporter Ledge is always guaranteed to be chosen. One of the three Mountain tiles are guaranteed if OW Layout Shuffle is set to Vanilla.

### Vanilla

Flute spots remain unchanged.

### Balanced

New flute spots are chosen at random, with restrictions that limit the promixity between other chosen flute spots.

### Random

New flute spots are chosen at random with minimum bias.


## Ganon Vulnerability Item (--ganon_item)

### Default

Ganon will remain vulnerable to the default item (silver arrows except in bomb-only mode) in his final phase.

### Random

Ganon will be vulnerable to a random item in his final phase instead of being vulnerable to silver. Ganon will tell you what his weakness is as he enters his final phase, and in swordless mode a medallion will never be picked.

### *<item>*

Ganon will be vulnerable to the specified item in his final phase instead of being vulnerable to silver.


# Command Line Options

```
-h, --help
```

Show the help message and exit.

```
--ow_shuffle <mode>
```

For specifying the overworld layout shuffle you want as above. (default: vanilla)

```
--ow_crossed <mode>
```

For specifying the type of cross-world connections  you want on the overworld

```
--ow_keepsimilar
```

This keeps similar edge transitions paired together with other pairs of transitions

```
--ow_mixed
```

This gives each OW tile a random chance to be swapped to the opposite world

```
--ow_fluteshuffle <mode>
```

For randomizing the flute spots around the overworld

```
--ganon_item <item>
```

For specifying what item ganon will be vulnerable to while stunned in his final phase. (default: default)
