## New Features

## Pottery Lottery and Key Drop Shuffle Changes

### Pottery

New pottery option that control which pots (and large blocks) are in the locations pool:

* None: No pots are in the pool, like normal randomizer
* Key Pots: The pots that have keys are in the pool. This is about half of the old keydropshuffle option
* Cave Pots: The pots that are not found in dungeons are in the pool. (Includes the large block in Spike Cave). Does
not include key pots. 
* CaveKeys: Both non-dungeon pots and pots that used to have keys are in the pool.
* Reduced: Same as CaveKeys but also roughly a quarter of dungeon pots are added to the location pool picked at random. This is a dynamic mode so pots in the pool will be colored. Pots out of the pool will have vanilla contents.
* Clustered: LIke reduced but pot are grouped by logical sets and roughly 50% of pots are chosen from those group. This is a dynamic mode like the above.
* Nonempty: All pots that had some sort of objects under them are chosen to be in the location pool. This excludes most large blocks and some pots out of dungeons. 
* Dungeon Pots: The pots that are in dungeons are in the pool. (Includes serveral large blocks) 
* Lottery: All pots and large blocks are in the pool

By default, switches remain in their vanilla location (unless you turn on the legacy option below)

CLI `--pottery <option>` from `none, keys, cave, cavekeys, reduced, clustered, nonempty, dungeon, lottery`

Note for multiworld: due to the design of the pottery lottery, only 256 items for other players can be under pots in your world.

### Colorize Pots

If the pottery mode is dynamic, this option is forced to be on (clustered and reduced). It is allowed to be on in all other pottery modes. Exceptions include "none" where no pots would be colored, and "lottery" where all pots would be. This option colors the pots differently that have been chosen to be part of the location pool. If not specified, you are expected to remember the pottery setting you chose. Note that Mystery will colorize all pots if lottery is chosen randomly.

CLI `--colorizepots`

### Shuffle key drops

Enemies that drop keys can have their drop shuffled into the pool. This is the other half of the keydropshuffle option.

CLI `--dropshuffle`

#### Legacy options

"Drop and Pot Keys" or `--keydropshuffle` is still availabe for use. This simply sets the pottery to keys and turns dropshuffle on as well to have the same behavior as the old setting.

The old "Pot Shuffle" option is still available under "Pot Shuffle (Legacy)" or `--shufflepots` and works the same by shuffling all pots on a supertile. It works with the lottery option as well to move the switches to any valid pot on the supertile regardless of the pots chosen in the pottery mode. This may increase the number of pot locations slightly depending on the mode.

#### Tracking Notes

The sram locations for pots and sprite drops are now final, please reach out for assistance or investigate the rom changes if needed.

## New Options

### Collection Rate

You can set the collection rate counter on using the "Display Collection Rate" on the Game Options tab are using the CLI option `--collection_rate`. Mystery seeds will not display the total.

### Goal: Trinity

Triforces are placed behind Ganon, on the pedestal, and on Murahdahla with 8/10 triforce pieces required. Recommend to run with 4-5 Crystal requirement for Ganon. Automatically pre-opens the pyramid.

### Boss Shuffle: Unique

At least one boss each of the prize bosses will be present guarding the prizes. GT bosses can be anything.

### MSU Resume

Turns on msu resume support. Found on "Game Options" tab, the "Adjust/Patch" tab, or use the `--msu_resume` CLI option. 

### BPS Patch

Creates a bps patch for the seed. Found on the "Generation Setup" tab called "Create BPS Patches" or `--bps`. Can turn off generating a rom using the existing "Create Patched ROM" option or `--suppress_rom`. There is an option on the Adjust/Patch tab to select a bps file to apply to the Base Rom selected on the Generation Setup tab using the Patch Rom button. Selected adjustments will be applied during patching.

## New Font

Font updated to support lowercase English. Lowercase vs. uppercase typos may exist. Note, you can use lowercase English letters on the file name.

## Restricted Item Placement Algorithm

The "Item Sorting" option or ```--algorithm``` has been updated with new placement algorithms. Older algorithms have been removed.
 
 When referenced below, Major Items include all Y items, all A items, all equipment (swords, shields, & armor) and Heart Containers. Dungeon items are considered major if shuffled outside of dungeons. Bomb and arrows upgrades are Major if shopsanity is turned on. The arrow quiver and universal small keys are Major if retro is turned on. Triforce Pieces are Major if that is the goal, and the Bomb Bag is Major if that is enabled.
 
 Here are the current fill options:

### Balanced 

This one stays the same as before and is recommended for the most random distribution of items.

### Vanilla Fill 

This fill attempts to place all items in their vanilla locations when possible. Obviously shuffling entrances or the dungeon interiors will often prevent items from being placed in their vanilla location. If the vanilla fill is not possible, then other locations are tried in sequence preferring "major" locations (see below), then heart piece locations, then the rest except for GT locations which are preferred last. Note the PoD small key that is normally found in the dark maze in vanilla is move to Harmless Hellway due to the placement algorithm limitation.

### Major Location Restriction

This fill attempts to place major items in major locations. Major locations are where the major items are found in the vanilla game. This includes the spot next to Uncle in the Sewers, and the Boomerang chest in Hyrule Castle.

This location pool is expanded to where dungeon items are locations if those dungeon items are shuffled. The Capacity Fairy locations are included if Shopsanity is on. If retro is enabled in addition to shopsanity, then the Old Man Sword Cave and one location in each retro cave is included. Key drop locations can be included if small or big key shuffle is on. This gives a very good balance between overworld and underworld locations though the dungeons ones will be on bosses and in big chests generally. Seeds do become more linear but usually easier to figure out.

### Dungeon Restriction

The fill attempts to place all major items in dungeons. It will overflow to the overworld if there are more items than locations (e.g. Triforce hunt.) This fill does attempt to run the GT trash fill when possible. Seeds are typically very linear but tend to be more difficult.

### District Restriction
 
The world is divided up into different regions or districts. Each dungeon is its own district. The overworld consists of the following districts:

Light world:

* Kakariko (The main screen, blacksmith screen, and library/maze race screens)
* Northwest Hyrule (The lost woods and fortune teller screens all the way to the river west of the potion shop)
* Central Hyrule (Hyrule castle, Link's House, the marsh, and the haunted grove)
* Desert (From the thief to the main desert screen)
* Lake Hylia (Around the lake)
* Eastern Hyrule (The eastern wild, the potion shop, and Zora's Domain)
* Death Mountain

Dark world:

* East Dark World (The pyramid, Palace of darkness, and Catfish)
* South Dark World (The dark lake, swamp area, to the dig game)
* Northwest Dark World (Village of Outcasts, to the Dark Sanctuary and screens in between)
* The Mire
* Dark Death Mountain

These districts are chosen at random and then filled with major items. If a location is part of a chosen district, but there are no more major items to place, a single green rupee is placed in the extra to indicate that as a placeholder. All other single green rupees are changed to be a blue rupee in order to not give false positives.

In entrance shuffle, what is shuffled to the entrances is considered instead of where the interior was originally. For example, if Blind's Hut is shuffled to the Dam, then the 5 chests in Blind's Hut are part of Central Hyrule instead of Kakariko.

Note: Bombos Tablet, Lake Hylia Island, Bumper Cave Ledge, the Floating Island, Cave 45, the Graveyard Cave, Checkerboard Cave and Mimic Cave are considered part of the light world region rather than the dark world region you mirror from.

In multiworld, the districts chosen apply to all players.  

### CLI values:

```balanced, vanilla_fill, major_only, dungeon_only, district```

## New Hints

Based on the district algorithm above (whether it is enabled or not,) new hints can appear about that district or dungeon. For each district and dungeon, it is evaluated whether it contains vital items and how many. If it has not any vital item, items then it moves onto useful items. Useful items are generally safeties or convenience items: shields, mails, half magic, bottles, medallions that aren't required, etc. If it contains none of those and is an overworld district, then it checks for a couple more things. First, if dungeons are shuffled, it looks to see if any are in the district, if so, one of those dungeons is picked for the hint. Then, if connectors are shuffled, it checks to see if you can get to unique region through a connector in that district. If none of the above apply, the district or dungeon is considered completely foolish.

## Overworld Map shows Dungeon Entrances

Option to move indicators on overworld map to reference dungeon location. The non-default options include indicators for Hyrule Castle, Agahnim's Tower, and Ganon's Tower.

CLI ```--overworld_map```

#### Options

##### default

Status quo. Showing only the prize markers on the vanilla dungeon locations.

##### compass

The compass item controls whether the marker is moved to the dungeons locations. If you possess the compass but not the map, only a glowing X will be present regardless of dungeon prize type, if you only possess the map, the prizes will be shown in predicable locations at the bottom of the overworld map instead of the vanilla location. Light world dungeons on the light world map and dark world dungeons on the dark world map. If you posses both map and compass, then the prize of the dungeon and the location will be on the map.

If you do not shuffle the compass or map outside of the dungeon, the non-shuffled items are not needed to display the information. If a dungeon does not have a map or compass, it is not needed for the information. Talking to the bomb shop or Sahasrahla furnishes you with complete information as well as map information.

##### map

The map item plays double duty in this mode and only possession of the map will show both prize and location of the dungeon. If you do not shuffle maps or the dungeon does not have a map, the information will be displayed without needing to find any items.

## Restricted Dungeon Items on Bosses

You may now restrict the items that can appear on the boss, like the popular ambrosia preset does.

CLI: ```--restrict_boss_items <option>```

#### Options

##### none

As before, the boss may have any item including any dungeon item that could occur there.

##### mapcompass

~~The map and compass are logically required to defeat a boss. This prevents both of those from appearing on the dungeon boss. Note that this does affect item placement logic and the placement algorithm as maps and compasses are considered as required items to beat a boss.~~

Currently bugged, not recommended for use.

##### dungeon

Same as above but both small keys and bigs keys of the dungeon are not allowed on a boss. (Note: this does not affect universal keys as they are not dungeon-specific)

## Notes and Bug Fixes

#### Unstable

* 1.0.1.3
  * Fix for rain prevented doors fouling up key doors
  * Couple minor issues
* 1.0.1.2
  * Removed "good bee" as an in-logic way of killing Mothula
  * Fixed an issue with Mystery generation and Windows path
  * Fixed an issue with small key bias rework
  * Fixed an issue where trinity goal would open pyramid unexpectedly. (No longer does so if ER mdoe is shuffling holes). Crystals goal updated to match that behavior.
  * Fixed a playthrough issue that was not respecting pot rules
  * Fixed an issue that was conflicting with downstream OWR project
  * Fixed an issue with inverted and certain pottery settings
  * Fixed an issue with small keys being shuffled and big keys not (key distribution)
* 1.0.1.1
  * Fixed the pots in Mire Storyteller/ Dark Desert Hint to be colorized when they should be
  * Certain pot items no longer reload when reloading the supertile (matches original pot behavior better)
  * Changed the key distribution that made small keys placement more random when keys are in their own dungeon
  * Unique boss shuffle no longer allows repeat bosses in GT (e.g. only one Trinexx in GT, so exactly 3 bosses are repeated in the seed. This is a difference process than full which does affect the probability distribution.)
  * Removed text color in hints due to vanilla bug
* 1.0.1.0
  * Large features
    * New pottery modes - see notes above
      * Pot substitutions added for red rupees, 10 bomb packs, 3 bomb packs, and 10 arrows have been added. They use objects that can result from a tree pull or other drop. The 3 bomb pack becomes a 4 bomb pack and the 10 bomb pack becomes an 8 pack. These substitutions are repeatable like all other normal pot contents.
      * Updated TFH to support up to 850 pieces
    * New font support
    * Trinity goal added
    * Separated Collection Rate counter from experimental
    * Added MSU Resume option
    * Support for BPS patch creation and applying patches during adjustment
    * New option for Boss Shuffle: Unique (Prize bosses will be one of each, but GT bosses can be anything)
  * Logic Notes
    * Skull X Room requires Boots or access to Skull Back Drop
    * GT Falling Torches requires Boots to get over the falling tile gap (this is a stop-gap measure until more sophisticated crystal switch traversal is possible) 
    * Waterfall of Wishing logic in open. You must have flippers to exit the Waterfall (flippers also required in glitched modes as well)
    * Fix for GT Crystal Conveyor not requiring Somaria/Bombs to get through
    * Pedestal goal + vanilla swords places a random sword in the pool
    * Added a few more places Links House shouldn't go when shuffled
  * Small features
    * Added a check for python package requirements before running code. GUI and console both for better error messages. Thanks to mtrethewey for the idea.
    * Refactored spoiler to generate in stages for better error collection. A meta file will be generated additionally for mystery seeds. Some random settings moved later in the spoiler to have the meta section at the top not spoil certain things. (GT/Ganon requirements.) Thanks to codemann and OWR for most of this work.
    * Updated tourney winners (included Doors Async League winners)
    * Some textual changes for hints (capitalization standardization)
    * Reworked GT Trash Fill. Base rate is 0-75% of locations fill with 7 crystals entrance requirements. Triforce hunt is 75%-100% of locations. The 75% number will decrease based on the crystal entrance requirement. Dungeon_only algorithm caps it based on how many items need to be placed in dungeons. Cross dungeon shuffle will now work with the trash fill.
    * Expanded Mystery logic options (e.g. owglitches)
    * Updated indicators on keysanity menu for overworld map option
  * Bug fixes:
    * Fix for Zelda (or any follower) going to the maiden cell supertile and the boss is not Blind. The follower will not despawn unless the boss is Blind, then the maiden will spawn as normal.
    * Bug with 0 GT crystals not opening GT
    * Fixed a couple issues with dungeon counters and the DungeonCompletion field for autotracking
    * Settings code fix
    * Fix for forbidding certain dashable doors (it actually does something this time)
    * Fix for major item algorithm and pottery
    * Updated map display on keysanity menu to work better with overworld_map option
    * Minor bug in crossed doors
    * Fix for Multiworld forfeits, shops and pot items now included
    * MultiServer fix for ssl certs and python
    * forbid certain doors from being dashable when you either can't dash them open (but bombs would work) or you'd fall into a pit from the bonk recoil in OHKO
    * Fixed a couple rain state issues
    * Add major_only algorithm to settings code
    * Fixes for Links House being at certain entrances (did not generate)
    * Fix for vanilla_fill, it now prioritizes heart container placements
    * Fix for dungeon counter showing up in AT/HC in crossed dungeon mode
    * Fixed usestartinventory with mystery
    * Added double click fix for install.py
    * Fix for SFX shuffle
    * Fix for districting + shopsanity
    * Fix for multiworld progression balancing would place Nothing or Arrow items
    * Fixed a bug with shopsanity + district algorithm where pre-placed potions messed up the placeholder count
    * Fixed usestartinventory flag (can be use on a per player basis)
    * Sprite selector fix for systems with SSL issues
    * Fix for Standard ER where locations in rain state could be in logic
* 1.0.0.3
    * overworld_map=map mode fixed. Location of dungeons with maps are not shown until map is retrieved. (Dungeon that do not have map like Castle Tower are simply never shown)
    * Aga2 completion on overworld_map now tied to boss defeat flag instead of pyramid hole being opened (fast ganon fix)
    * Minor issue in dungeon_only algorithm fixed (minorly affected major_only keyshuffle and vanilla fallbacks)
* 1.0.0.2
    * Include 1.0.1 fixes
    * District hint rework
* 1.0.0.1
    * Add Light Hype Fairy to bombbag mode as needing bombs
	
### From stable DoorDev

* 1.0.1
	* Fixed a bug with key doors not detecting one side of an interior door
	* Sprite selector fix for systems with SSL issues