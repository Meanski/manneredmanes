import discord
from discord.ext import commands
import datetime

class MessageEdited(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        # Ignore edits that don't actually change the message content (e.g., embeds added by Discord or links)
        if before.content == after.content:
            return

        # Ignore messages edited in DMs
        if not before.guild:
            return

        channel_id = 1253143585872937000

        try:
            channel = self.bot.get_channel(channel_id)
            if channel and before.author:  # Check if channel and author exist
                permissions = channel.permissions_for(before.guild.me)
                if permissions.send_messages and permissions.embed_links:  # Check bot permissions
                    embedlog = discord.Embed(color=0x7289DA)
                    embedlog.set_author(name=before.author, icon_url=before.author.display_avatar.url)
                    embedlog.add_field(name="Original Message", value=before.content[:1021] + '...' if len(before.content) > 1024 else before.content, inline=False)
                    embedlog.add_field(name="Edited Message", value=after.content[:1021] + '...' if len(after.content) > 1024 else after.content, inline=False)
                    embedlog.timestamp = datetime.datetime.utcnow()
                    await channel.send(embed=embedlog)
                else:
                    print(f"Missing permissions to send messages or embed links in {channel.name}")
            else:
                print(f"Channel or author not found. Channel ID: {channel_id}")
        except Exception as e:
            print(f"Error sending message edit log: {e}")

async def setup(bot):
    await bot.add_cog(MessageEdited(bot))
