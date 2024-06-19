import discord
from discord.ext import commands
import logging
import asyncio
import os
from dotenv import load_dotenv

#####################
# Setup             #
#####################
intents = discord.Intents.default()
intents.typing = True
intents.presences = True
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

load_dotenv()
token = os.getenv('DISCORD_API_KEY')

#####################
# Logging           #
#####################
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


#####################
# On load           #
#####################
@bot.event
async def on_ready():
    #Print version on start
    print('We have logged in as {0.user}'.format(bot))
    print('Discord.py version #' + discord.__version__ )
    logger.info('We have logged in as {0.user}'.format(bot))
    logger.info('Discord.py version #' + discord.__version__ )

    #Discord status
    status = ["luscious locks"]
    while True:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(status)))
        await asyncio.sleep(300)


#####################
# Cogs          #
#####################

#Load up cogs and run the bot
async def main():

    #We'll add stuff here
    #await bot.load_extension('src.X')

    print('Extensions loaded. Bot is ready.')
    await bot.start(token)

# Start the bot
asyncio.run(main())

