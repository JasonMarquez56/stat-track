import calendar
import os
from datetime import datetime, timezone

import discord
from discord.ext import commands, tasks


class Scheduler(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.posted_this_month = False
		self.monthly_post.start()

	def cog_unload(self):
		self.monthly_post.cancel()

	@tasks.loop(hours=1)
	async def monthly_post(self):
		now = datetime.now(timezone.utc)
		last_day = calendar.monthrange(now.year, now.month)[1]

		# Post once on the last day of the month at 8 PM UTC
		if now.day == last_day and now.hour == 20:
			if self.posted_this_month:
				return
			self.posted_this_month = True
			await self._post_monthly_leaderboard(now.year, now.month)
		else:
			self.posted_this_month = False

	@monthly_post.before_loop
	async def before_monthly_post(self):
		await self.bot.wait_until_ready()

	async def _post_monthly_leaderboard(self, year: int, month: int):
		channel_id = int(os.getenv("MONTHLY_CHANNEL_ID", "0"))
		channel = self.bot.get_channel(channel_id)
		if channel is None or not isinstance(channel, discord.TextChannel):
			print(f"[Scheduler] Could not find MONTHLY_CHANNEL_ID={channel_id}")
			return

		voice_cog = self.bot.cogs.get("Voice")
		if voice_cog is None:
			print("[Scheduler] Voice cog not loaded, cannot build monthly leaderboard")
			return

		# Gather monthly seconds for all tracked users, including active sessions
		all_users = set(voice_cog.monthly_seconds.keys()) | set(voice_cog.join_times.keys())
		if not all_users:
			await channel.send("No voice time data for this month!")
			return

		leaderboard = []
		for guild in self.bot.guilds:
			for user_id in all_users:
				seconds = voice_cog.get_monthly_seconds(user_id)
				member = guild.get_member(user_id)
				name = member.display_name if member else f"User {user_id}"
				leaderboard.append((name, seconds))
			break  # only use the first guild

		leaderboard.sort(key=lambda x: x[1], reverse=True)

		month_name = datetime(year, month, 1).strftime("%B %Y")
		embed = discord.Embed(
			title=f"Monthly Voice Leaderboard — {month_name}",
			color=discord.Color.gold()
		)

		medals = ["🥇", "🥈", "🥉"]
		lines = []
		for i, (name, seconds) in enumerate(leaderboard[:10]):
			prefix = medals[i] if i < 3 else f"`{i+1}.`"
			lines.append(f"{prefix} **{name}** — {voice_cog.format_duration(seconds)}")

		embed.description = "\n".join(lines)
		await channel.send(embed=embed)
		print(f"[Scheduler] Posted monthly leaderboard for {month_name}")


async def setup(bot: commands.Bot):
	await bot.add_cog(Scheduler(bot))
