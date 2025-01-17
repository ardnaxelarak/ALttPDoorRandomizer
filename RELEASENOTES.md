# Patch Notes

* 1.4.8.1
  - Fixed broken doors generation
* 1.4.8
  - New option: Mirror Scroll - to add the item to the starting inventory in non-doors modes (Thanks Telethar!)
  - Customizer: Ability to customize shop prices and control money balancing. `money_balance` is a percentage betwen 0 and 100 that attempts to ensure you have that much percentage of money available for purchases. (100 is default, 0 essentially ignores money considerations) 
  - Fixed a key logic bug with decoupled doors when a big key door leads to a small key door (the small key door was missing appropriate logic)
  - Fixed an ER bug where Bonk Fairy could be used for a mandatory connector in standard mode (boots could allow escape to be skipped)
  - Fixed an issue with flute activation in rain mode. (thanks Codemann!)
  - Fixed an issue with enemies in TR Dark Ride room not requiring Somaria. (Refactored the room for decoupled logic better)
  - More HMG fixes by Muffins
  - Fixed an issue with multi-player HMG
  - Fixed an issue limiting number of items specified in the item pool on the GUI
  - Minor documentation fixes (thanks Codemann!)
