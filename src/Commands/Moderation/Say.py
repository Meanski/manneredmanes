import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import checks

class SayCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command for /say
    @app_commands.command(name="say", description="Repeats what you say and deletes the original message")
    @checks.has_permissions(kick_members=True)
    async def say(self, interaction: discord.Interaction, message: str):
        # Delete the original message (interaction)
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.delete_original_response()

        # Send the message that was said
        await interaction.channel.send(message)

async def setup(bot):
    await bot.add_cog(SayCommandCog(bot))