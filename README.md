# AniRecomBot

The bot generates a list of recommendations based on the MyAnimeList account.
Recommendations are obtained through scraping from the site https://anime.ameo.dev/

The bot can also show a random quote, picture or gif using various APIs.

![demo](demo.gif)

## Getting started

1. Clone this repository to your local machine.

2. Install requirements:
`pip install -r requirements.txt`

3. Create an .env file in the root of your project directory and add your Telegram bot API token:
`BOT_TOKEN=bot-token-here`

4. Run `bot.py` from project directory.

## Usage
The bot executes all commands using the corresponding buttons in the menu.

- `Quote` - Random quote.
- `PicRandom` - Random picture.
- `B..baka!` - Random "baka" gif.
- `Anime Recommendations` - Recommendations. When clicked, it will ask for a nickname for "MyAnimeList". Has its own submenu:
  - `Next` - Show next recommendation.
  - `Update recs` - Update list of recommendations.
  - `Main Menu` - Return to the main menu.