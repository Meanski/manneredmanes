import discord
from discord.ext import commands, tasks
from googleapiclient.discovery import build
import json

with open('config.json') as f:
    config = json.load(f)

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_CHANNEL_ID = 'UC6HEhd6eFIAmnwoi77hnNIw'
DISCORD_CHANNEL_ID = '1253092620998152273'

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

class YouTubeScraper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.latest_video_id = None
        self.check_new_video.start()

    def cog_unload(self):
        self.check_new_video.cancel()

    @tasks.loop(minutes=10)
    async def check_new_video(self):
        channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
        request = youtube.search().list(
            part="snippet",
            channelId=YOUTUBE_CHANNEL_ID,
            order="date",
            maxResults=1
        )
        response = request.execute()

        if response['items']:
            video = response['items'][0]
            video_id = video['id']['videoId']
            video_title = video['snippet']['title']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            if self.latest_video_id != video_id:
                self.latest_video_id = video_id
                embed = discord.Embed(
                    title=video_title,
                    url=video_url,
                    description=video['snippet']['description'],
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url=video['snippet']['thumbnails']['high']['url'])
                await channel.send(embed=embed)

    @check_new_video.before_loop
    async def before_check_new_video(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(YouTubeScraper(bot))
