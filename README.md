# Stat Track

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![discord.py](https://img.shields.io/badge/discord.py-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discordpy.readthedocs.io)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org)

A Discord bot for tracking server stats. Built with `discord.py`, slash commands, and a SQLite database — with a modular cog-based architecture for easy extension.

## Features

- **Slash command support** — Clean, modern `/commands` registered with Discord
- **Persistent storage** — Stats saved to a local SQLite database
- **Modular cogs** — Each feature lives in its own cog file for easy maintenance
- **[Add your specific tracked stats here — e.g. message counts, voice time, game scores]**

## Prerequisites

- Python 3.10+
- A Discord bot token ([create one here](https://discord.com/developers/applications))

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/JasonMarquez56/stat-track.git
cd stat-track
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your bot token

Create a `.env` file in the project root:

```env
DISCORD_TOKEN=your_bot_token_here
```

> **Never commit your `.env` file.** It's already in `.gitignore`.

### 4. Run the bot

```bash
python bot.py
```

On startup, the bot will initialize the database, load all cogs, and sync slash commands with Discord.

## Project Structure

```
stat-track/
├── bot.py           # Entry point — sets up intents, loads cogs, syncs commands
├── database.py      # Database initialization and helper functions
├── bot.db           # SQLite database (auto-created on first run)
├── cogs/            # Feature modules (each file is a separate cog)
├── requirements.txt # Python dependencies
└── .env             # Bot token (not committed)
```

## Adding a New Cog

1. Create a new `.py` file inside the `cogs/` folder
2. Define a `Cog` class and a `setup(bot)` function
3. Restart the bot — it will be loaded automatically

Example:

```python
from discord.ext import commands

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def hello(self, ctx):
        await ctx.send("Hello!")

async def setup(bot):
    await bot.add_cog(MyCog(bot))
```

## Inviting the Bot

When creating your bot on the [Discord Developer Portal](https://discord.com/developers/applications), make sure to enable:

- **Privileged Gateway Intents:** Server Members, Message Content, Voice States

Use the OAuth2 URL Generator to create an invite link with the `bot` and `applications.commands` scopes.

## License

This project is open source. See [LICENSE](LICENSE) for details.
