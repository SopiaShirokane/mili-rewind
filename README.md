# mili-rewind
Another discord bot, yeah. This time using your watch-history.json file from Google Takeout (yes I took it from HoloRewind, the only difference being Youtube's API key and your own discord bot)

# Usage

 - Clone this repo 
 - Run these commands:
   ```python -m venv .venv```
   ```pip install --disable-pip-version-check -U --prefix .venv/ -r requirements.txt```
   ```source [the path you installed this repo]/.venv/bin/[*]```
   [*]: activate.fish for fish shell
        Activate.ps1 for Windows Powershell
        activate.csh for anything else
   ```python3 mili-rewind.py```
 - Make sure you already created environment variables for Youtube's API and Discord's token before using python3
 - Invite the bot to your server (find out how yourself)
 - Go to Google Takeout and request your Youtube's watch history in json, put it in the same folder as the bot
 - Enjoy!
