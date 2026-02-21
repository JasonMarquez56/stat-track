import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Voice(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.join_times: dict[int, datetime] = {} # user_id -> join time
		self.total_seconds: dict[int, float] = {} # user_id -> total seconds

	# Helpers
	def get_total_seconds(self, user_id: int) -> float:
		# Returns total voice seconds for a user, includes current session if active
		total = self.total_seconds.get(user_id, 0)
		if user_id in self.join_times:
			total += (datetime.utcnow() - self.join_times[user_id]).total_seconds()
		return total
	
	def format_duration(self, seconds: float) -> str:
		# Converts seconds into readable strings
		seconds = int(seconds)
		hours = seconds // 3600
		minutes = (seconds % 3600) // 60
		secs = seconds % 60
		if hours > 0:
			return f"{hours}h {minutes}m {secs}s"
		elif minutes > 0:
			return f"{minutes}m {secs}s"
		else:
			return f"{secs}s"
		
	# Listeners
	@commands.Cog.listener()
	async def on_voice_state_update(
		self,
		member: discord.Member,
		before: discord.VoiceState,
		after: discord.VoiceState,
	):
		user_id = member.id

		# Joined a voice channel
		if before.channel is None and after.channel is not None:
			self.join_times[user_id] = datetime.utcnow()

		# Left a voice channel
		elif before.channel is not None and after.channel is None:
			if user_id in self.join_times:
				duration = (datetime.utcnow() - self.join_times[user_id]).total_seconds()
				self.total_seconds[user_id] = self.total_seconds.get(user_id, 0) + duration
				del self.join_times[user_id]

	# Commands
	@app_commands.command(name="voicetime", description="Check how long a user has spent in voice channels.")
	@app_commands.describe(member="The user to check (defaults to you)")
	async def voicetimer(self, interaction: discord.Interaction, member: discord.Member | None = None):
		target = member or interaction.user
		seconds = self.get_total_seconds(target.id)

		if seconds == 0:
			await interaction.response.send_message(
				f"**{target.display_name}** has no tracked voice time yet.",
				ephemeral=True
			)
			return

		duration = self.format_duration(seconds)
		currently_in_voice = target.id in self.join_times

		embed = discord.Embed(
			title="Voice Time",
			color=discord.Color.blurple()
		)
		embed.set_thumbnail(url=target.display_avatar.url)
		embed.add_field(name="User", value=target.mention, inline=True)
		embed.add_field(name="Total Time", value=duration, inline=True)
		if currently_in_voice:
			embed.set_footer(text="Currently in a voice channel, time is still counting!")
		
		await interaction.response.send_message(embed=embed)
	
	@app_commands.command(name="voiceleaderboard", description="See who has spend the most time in voice channels.")
	async def voiceleaderboard(self, interaction: discord.Interaction):
		if interaction.guild is None:
			await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
			return

		if not self.total_seconds and not self.join_times:
			await interaction.response.send_message("No voice time data yet!", ephemeral=True)
			return
		
		# Combine all tracked users
		all_users = set(self.total_seconds.keys()) | set(self.join_times.keys())
		leaderboard = []

		for user_id in all_users:
			seconds = self.get_total_seconds(user_id)
			member = interaction.guild.get_member(user_id)
			name = member.display_name if member else f"User {user_id}"
			leaderboard.append((name, seconds))
		
		leaderboard.sort(key=lambda x: x[1], reverse=True)

		embed = discord.Embed(
			title="Voice Time Leaderboard",
			color = discord.Color.gold()
		)

		medals = ["🥇", "🥈", "🥉"]
		lines = []
		for i, (name, seconds) in enumerate(leaderboard[:10]):
			prefix = medals[i] if i < 3 else f"`{i+1}.`"
			lines.append(f"{prefix} **{name}** - {self.format_duration(seconds)}")
		
		embed.description = "\n".join(lines)
		await interaction.response.send_message(embed=embed)
	
async def setup(bot: commands.Bot):
	await bot.add_cog(Voice(bot))