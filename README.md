# Palworld Appearance Editor

> ### :warning: This tool is experimental. Be careful of data loss and *always* make a backup.

This nifty tool allows you to change your appearance of your Palworld character *after* it has been created at the start. During testing on a **Singleplayer** world, I have not noticed any issues.

## Disclaimers
I have only tested this on Singleplayer, on offline mode.


## Usage

Dependencies:
- Python 3
- [uesave-rs](https://github.com/trumank/uesave-rs)

Command:    
`python main.py`

Steps:
- Ensure you have both **Python** and **UESave** installed.
- Have a character in Palworld you wish to change the appearance of. You can find your player saves in ```C:\Users\\computer_name\AppData\Local\Pal\Saved\SaveGames\\steam_id\\save_id\Players```
  - If you are changing your own character, it will most likely be `00000000000000000000000000000001.sav`
- Create a new temporary Palworld game, and note the save location.
- Run the program.
- Enter your UESave location
  - Usually `C:\Program Files\uesave\bin\uesave.exe`
- Enter the exact path to your **existing** character.
- Enter the exact path to your **new appearance** character.
- Press enter, and reload your game.

### Credit to [xNul](https://github.com/xNul/palworld-host-save-fix) for the bulk of the code. I would not have been able to do this without you!
> Credit to [cheahjs](https://gist.github.com/cheahjs/300239464dd84fe6902893b6b9250fd0) for his very useful script helping me to make this fix!

### Appreciate any help testing and resolving bugs.
