# Changelog

### 0.1.7.2
- Fixed music algorithm to play correct track in OW Shuffle
- Removed convenient portal on WDM in OW Layout Shuffle
- Fixed Mystery to not spoil OW Shuffle in filename

### 0.1.7.1
- Improved bomb logic to consider tree pulls, bush crabs, and stun prize
- Fixed Mystery to use new updated OW mode terminology

### 0.1.7.0
- Expanded new DR bomb logic to all modes (bomb usage in logic only if there is an unlimited supply of bombs available)
- ~~Merged DR v0.5.0.1 - Bomblogic mode / Enemizer fixes~~

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