# Patch Notes

* 1.5.0
  * Logic: Fixed vanilla key logic for GT basement
  * Logic (Playthrough): Fixed an issue where enemy kill rules were not applied during playthrough calculation. (Thanks Catobat for the catch)
  * Enemy Drop: Added "spies" and shadows for hidden enemies when enemy drop shuffled is enabled
  * Keysanity/Keydrop Menu for DR:
    * Map key information is now controlled by the Dungeon Chest Counts setting. If set to always on, this information will be available right away in the menu. And will be on the HUD even when the map is not obtained.
    * The key counter on the HUD for the current dungeon now accounts for keys from enemies or pots that are from vanilla key locations.
    * The first number on the HUD represents all keys collected either in that dungeon or elsewhere.
    * The second number on the HUD is the total keys that can be collected either in that dungeon or elsewhere.
    * The key counter on inside the Menu is unchanged. (At the bottom near A button items)
    * The first number in the Menu is the current number of keys in your inventory
    * The second number is how many keys left to find in chests (not those from pots/enemies unless those item pools are enabled)
  * Customizer: free_lamp_cone option added. The logic will account for this, and place the lamp without regard to dark rooms. 
  * Customizer: force_enemy option added that makes all enemies the specified type if possible. There are known gfx glitches in the overworld.
  * Optimization: Improved generation performance (Thanks Catobat!)
