import discord
from discord.ext import commands
import datetime

class MessageDeleted(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Ignore messages deleted from DMs
        if not message.guild:
            return

        channel_id = 1253143585872937000

        try:
            channel = self.bot.get_channel(channel_id)
            if channel and message.author:  # Check if channel and author exist
                permissions = channel.permissions_for(message.guild.me)
                if permissions.send_messages and permissions.embed_links:  # Check bot permissions
                    embedlog = discord.Embed(color=0x752421)
                    embedlog.set_author(name=message.author, icon_url=message.author.display_avatar.url)
                    embedlog.add_field(name=f"Message deleted by {message.author.display_name}", value=message.content, inline=False)
                    embedlog.timestamp = datetime.datetime.utcnow()
                    await channel.send(embed=embedlog)
                else:
                    print(f"Missing permissions to send messages or embed links in {channel.name}")
            else:
                print(f"Channel or author not found. Channel ID: {channel_id}")
        except Exception as e:
            print(f"Error sending message deletion log: {e}")

async def setup(bot):
    await bot.add_cog(MessageDeleted(bot))