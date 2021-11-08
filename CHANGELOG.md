# Changelog

### 0.2.2.0
- Delivering Big Red Bomb is now in logic
- Smith/Purple Chest have proper dynamic pathing to fix logical issues
- Fixed issue with bomb walls in OW not requiring moon pearl in DW

### 0.2.1.3
- New fake flipper handling to allow S+Q rather than insta-kill
- Fixed whirlpools in Crossed OW
- Spoiler fixes, incl. missing Starting Inventory in Spoiler
- Fixed music track change to Sanc music when Standard mode is delivering Zelda
- Fixed SP flooding issue
- Fixed issue with Shuffle Ganon in CLI/GUI
- ~~Merged DR v0.5.1.5 - Mystery subweights~~

### 0.2.1.2
- Fixed issue with whirlpools not changing world when in Crossed OW

### 0.2.1.1
- Many fixes to ER: infinite loops, preventing cross-world scenarios in non-cross-world modes
- Spoiler log improvements, outputs in stages so a Spoiler is available if an error occurs
- Added no_race option for Mystery
- Fixed output_path in Mystery to use the saved setting if none is specified on CLI

### 0.2.1.0
- Implemented Whirlpool Shuffle

### 0.2.0.0
- Massive overhaul of ER algorithm
- Added 2 new ER modes (Lite and Lean)
- Added new mystery options (Logic/Shuffle Ganon)
- Smith deletion on S+Q only occurs if Blacksmith not reachable from starting locations
- Spoiler log improvements to prevent spoiling in the beginning 'meta' section
- Various minor fixes and improvements
- ~~Merged DR v0.5.1.4 - ROM bug fixes/keylogic improvements~~

### 0.1.9.4
- Hotfix for bad 0.1.9.3 version

### 0.1.9.3
- Moved flute spot from Northwest Lake Hylia to Southeast Lake Hylia
- Fixed Links House start in Inverted ER
- Minor accuracy improvements to ER, mostly preparations for future work

### 0.1.9.2
- Fixed spoiler log and mystery for new Crossed/Mixed structure
- Minor preparations and tweaks to ER framework (added global Entrance/Exit pool)
- ~~Merged DR v0.5.1.2 - Blind Prison shuffled outside TT/Keylogic Improvements~~

### 0.1.9.1
- Fixed logic issue with leaving IP entrance not requiring flippers
- ~~Merged DR v0.5.1.1 - Map Indicator Fix/Boss Shuffle Bias/Shop Hints~~

### 0.1.9.0
- Expanded Crossed OW to four separate options, see Readme for details
- Crossed OW will now play a short SFX when changing worlds
- Improved Link/Bunny state in Crossed OW
- Fixed issue with TR Pegs when fluting directly from an area with hammerpegs
- Updated OW GUI layout

### 0.1.8.2
- Fixed issue with game crashing on using Flute
- Fixed issues with Link/Bunny state in Crossed OW
- Fixed issue with Standard+Parallel not using vanilla connections for Escape
- Fixed issue with Mystery for OW boolean options
- ~~Merged DR v0.5.1.0 - Major Keylogic Update~~

### 0.1.8.1
- Fixed issue with activating flute in DW (OW Mixed)
- Fixed issue with Parallel+Crossed not generating
- Fixed issue with Standard not generating
- Fixed issue with Swordless not generating
- Fixed logic for Graveyard Ledge and Kings Tomb

### 0.1.8.0
- Moved Crossed to its own checkbox option
- Removed Legacy ER shuffles
- Added OW Shuffle support for Plando module (needs user testing)
- Fixed issue with Sanc start at TR as bunny when it is LW
- Fixed issue with Pyramid Hole not getting shuffled
- ~~Merged DR v0.5.0.3 - Minor DR fixes~~

### 0.1.7.4
- Fixed issue with Mixed OW failing to generate when HC/Pyramid is swapped
- Various fixes to improve generation rates for Mixed OW Shuffle
- ~~Merged DR v0.5.0.2 - Shuffle SFX~~

### 0.1.7.3
- Fixed minor issue with ambient SFX stopping and starting on OW screen load
- MSU-1 changed to play LW2 (track 60) when Aga1 is killed instead of ped pull
- Added dynamic flute exits for all LW OW regions
- Improved spoiler log playthru pathing accuracy by including flute routing
- Fixed issue with generating a filename for vanilla OW settings

### 0.1.7.2
- Fixed music algorithm to play correct track in OW Shuffle
- Removed convenient portal on WDM in OW Layout Shuffle
- Fixed Mystery to not spoil OW Shuffle in filename

### 0.1.7.1
- Improved bomb logic to consider tree pulls, bush crabs, and stun prize
- Fixed Mystery to use new updated OW mode terminology

### 0.1.7.0
- Expanded new DR bomb logic to all modes (bomb usage in logic only if there is an unlimited supply of bombs available)
- ~~Merged DR v0.5.0.1 - Bombbag mode / Enemizer fixes~~

### 0.1.6.9
- ~~Merged DR v0.4.0.12 - Secure random update / Credits fix~~

### 0.1.6.8
- Implemented a smarter Balanced Flute Shuffle algorithm
- Fixed Collection Rate in credits
- Removed sortedcontainers dependency

### 0.1.6.7
- Mountain Entry and West Death Mountain are now Swapped independently (Old Man rescue is always in your starting world)
- Fixed issue with AT/GT access logic
- Improved spoiler log playthru accuracy
- Fixed Boss Music when boss room is entered thru straight stairs
- Suppressed in-dungeon music changes when DR is enabled
- Fixed issue with Pyramid Exit exiting to wrong location in ER
- ~~Merged DR v0.4.0.11 - Various DR changes~~

### 0.1.6.6
- ~~Merged DR v0.4.0.9 - P/C Indicator / Credits fix / CLI Hints Fix~~

### 0.1.6.5
- Reduced chance of diagonal flute spot in Balanced
- ~~Merged DR v0.4.0.8 - Boss Indicator / Psuedo Boots / Quickswap Update / Credits Updates~~

### 0.1.6.4
- Fixed Frogsmith and Stumpy and restored progression in these locations
- Added Blacksmith/Hammer Pegs to OW Tile Swap pool

### 0.1.6.3
- Fixed borked credits (and missing Sprite Author) when collection rate isn't 216 or if GTBK count isn't /22
- Added OW Rando in credits
- Actually merged in DR v0.4.0.7 (with no thanks to GitHub)

### 0.1.6.2
- Added Balanced option for Flute Shuffle
- Fixed issue with Flute Spot to Mountain Entry softlocking
- Fixed logic bug with Inverted Kakariko Portal

### 0.1.6.1
- Fixed issue with Flute Spot to VoO softlocking
- Fixed Houlihan to exit where Link's House does
- Fixed issue with jsonout not correctly showing rom mods for some OW Shuffle data

### 0.1.6.0
- Added Flute Shuffle setting
- Minor GUI changes

### 0.1.5.3
- Fixed issue with Aga portal mirror bonking in Mixed Shuffle
- Fixed issue with Frog/Dig Game edges duplicating in edge pool, causing Insanity-like behavior

### 0.1.5.2
- Partial revert of horizontal VRAM fix from v0.1.5.0

### 0.1.5.1
- Fixed issue with Flute Spot 7 logically connecting to the wrong area in Mixed/Crossed OW Shuffle
- Fixed issue with TR portal not requiring mitts when tile is swapped

### 0.1.5.0
- Added OW Tile Swap setting
- Fixed horizontal VRAM visual loading glitch on megatiles
- ~~Merged DR v0.4.0.7 - Fast Credits / Reduced Flashing / Sprite Author in Credits~~

### 0.1.4.3
- Merged DR v0.4.0.6 - TT Maiden Attic Hint / DR Entrance Floor Mat Mods / Hard/Expert Item Pool Fix

### 0.1.4.2
- Modified various OW map terrain specific to OW Shuffle
- Changed World check to table-based vs OW ID-based (should have no effect with current modes)
- Merged DR v0.4.0.5 - Mystery Boss Shuffle Fix / Swordless+Hard Item Pool Fix / Insanity+Inverted ER Fixes

### 0.1.4.1
- Moved Inverted Pyramid Entrance to top of HC Ledge
- Fixed various issues with Inverted and Insanity

### 0.1.4.0
- Initial Inverted Implementation
- Fix for Kakariko Pond no longer requiring fake flipper

### 0.1.3.1
- Various logic fixes and region prep for Inverted
- Fixed muted MSU-1 music in door rando when descending GT Climb stairs
- Fixed Standard + Vanilla (thanks compiling)
- Merged DR v0.4.0.4 - Shuffle Link's House / Experimental Bunny Start / 10 Bomb Fix

### 0.1.3.0
- Added OWG Logic for OW Shuffle
- Merged DR v0.4.0.2 - OWG Framework / YAML

### 0.1.2.2
- Re-purposed OW Shuffle setting to Layout Shuffle
- Merged Parallel Worlds setting into Layout Shuffle
- Added guaranteed Flute hint for OW Shuffle modes

### 0.1.2.1
- Made possible fix for Standard
- Merged DR v0.3.1.10 - Fixed Standard generation

### 0.1.2.0
- Added 'Parallel Worlds' toggle option
- Updated shuffle algorithm
- Renamed some OW areas

### 0.1.1.2
- If Link's current position fits within the incoming gap, Link will not get re-centered to the incoming gap
- Added Rule for Pearl required to drop down back of SW
- Merged DR v0.3.1.8 - Improved Shopsanity pricing - Fixed Retro generation

### 0.1.1.1
- Fixed camera unlocking issue
- Changed default setting for DR to Vanilla

### 0.1.1.0
- Added 'Keep Similar Edges Together' toggle option
- Removed Duplicate Pyramid Ledge location, causing a Warning of unfilled location on generation

### 0.1.0.3
- Modified various logic rule for some OW locations

### 0.1.0.2
- Fixed error generating a bad Spoiler log

### 0.1.0.1
- Separated DR versioning from OR versioning
- Removed LW/DW flag toggle on transitions

### 0.1.0.0
- Initial release