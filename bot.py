import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Load Cogs
async def load_cogs():
	for filename in os.listdir("./cogs"):
		if filename.endswith(".py"):
			cog_name = filename[:-3]
			try:
				await bot.load_extension(f"cogs.{cog_name}")
				print(f"Loaded cog: {cog_name}")
			except Exception as e:
				print(f"Failed to load cog {cog_name}: {e}")

# Events
@bot.event
async def on_ready():
	assert bot.user is not None
	print(f"\nLogged in as {bot.user} (ID: {bot.user.id})")
	print("-" * 40)
	print("Loading cogs...")
	await load_cogs()

	# sync the slash commands with Discord
	try:
		synced = await bot.tree.sync()
		print(f"\nSynced {len(synced)} slash command(s)")
	except Exception as e:
		print(f"Failed to sync commands: {e}")

	print("\nBot is ready!")

# Run
bot.run(os.getenv("DISCORD_TOKEN", ""))