import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="test", description="Test command.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def test(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        await interaction.response.defer(ephemeral=True)

        # Define the mod-log channel
        channellog = discord.utils.get(interaction.guild.channels, name="mod-log")

        # Construct the base embed
        embed = discord.Embed(title="", description="", color=0x752421)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()

        # Define the reason message
        if not reason:
            reason_msg = f"{user} tested by {interaction.user}. No reason set."
        else:
            reason_msg = f"{user} tested by {interaction.user}. {reason}."

        # Add the message to the embed
        embed.add_field(name=reason_msg, value="Test command used.", inline=True)

        # Send the embed to the mod-log
        if channellog:
            await channellog.send(embed=embed)

        # Feedback to the invoking user
        await interaction.followup.send(f"**{user}** has been tested for **{reason}**." if reason else f"**{user}** has been tested.", ephemeral=True)

    @test.error
    async def test_handler(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.AppCommandError):
            embed = discord.Embed(title="ERROR - Test", description=str(error), color=0x752421)
            embed.set_footer(text=f"/test attempted by: {interaction.user}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Kick(bot))
