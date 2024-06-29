import discord
from discord.ext import commands
import logging
import asyncio
import os
from dotenv import load_dotenv
import random

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
    print(f'We have logged in as {bot.user}')
    print(f'Discord.py version #{discord.__version__}')
    logger.info(f'We have logged in as {bot.user}')
    logger.info(f'Discord.py version #{discord.__version__}')

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')

    # Start the background task for changing status
    bot.loop.create_task(change_status())

async def change_status():
    status = ["your luscious locks"]
    while True:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(status)))
        await asyncio.sleep(300)

#####################
# Cogs              #
#####################
async def main():
    # Load the Kick cog
    await bot.load_extension('src.Commands.Moderation.Kick')

    # Commands
        # Moderation
    await bot.load_extension('src.Commands.Moderation.Say')
        # Public
    await bot.load_extension('src.Commands.Public.SupportTicket')

    # Events
    await bot.load_extension('src.Events.MessageEdited')
    await bot.load_extension('src.Events.MessageDeleted')
    await bot.load_extension('src.Events.YouTubeScraper')

    print('Extensions loaded. Bot is ready.')
    await bot.start(token)

# Start the bot
asyncio.run(main())