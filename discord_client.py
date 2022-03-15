import os
import discord
from logger import LOGGER as logger

async def get_client():
    discord_client = discord.Client()
    logger.debug("logging in")
    await discord_client.login(os.getenv("DISCORD_BOT_TOKEN"), bot=True)
    return discord_client