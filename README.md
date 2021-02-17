# glearn-scraper
This glearn-scraper fetches the timetable from g-learn website (our student portal) and sends online class links
to the discord server according to the timetable.

### Dependencies :package:

- Make sure that python is pre-installed in your system if not [Click Here](https://www.python.org/downloads/) to download and install the latest python version.
- Install all the requirements using `pip install -r requirements.txt` command in cmd.
- Compatible Browsers : *Chrome*
*Chrome runs in *headless mode* so no distractions.

### Setup & Run :rocket:
- Enter your G-learn credentials and Discord webhook url in **keys.env** file.
```
 USER_ID=
 PASSWORD=
 DISCORD_WEBHOOK_URL=
```
- Navigate to the *glearn-scraper* folder and Run the bot `python link_bot.py`
