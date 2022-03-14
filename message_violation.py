import asyncio
import os

import discord

from logger import LOGGER as logger
from http_response import HTTPError


def message_violation(*args, **kwargs):
    return asyncio.run(_async_message_violation(*args, **kwargs))


async def _async_message_violation(channel_id, message_id, explanation):

    logger.debug({"channel_id": channel_id, "message_id": message_id})

    discord_client = discord.Client()
    logger.debug("logging in")
    await discord_client.login(os.getenv("DISCORD_BOT_TOKEN"), bot=True)

    channel = await discord_client.fetch_channel(channel_id)
    if not channel:
        raise HTTPError(
            500, {"reason": "channel not found (make sure bot is added to channel)"}
        )

    guild = await discord_client.fetch_guild(channel.guild.id)
    msg = await channel.fetch_message(message_id)
    if not msg:
        raise HTTPError(500, {"reason": "msg not found"})

    notification_msg = (
        f"Your message in channel <#{channel_id}> has been removed for violating one more more server rules ({guild.name})."
        f"\n\nViolation explanation:\n```{explanation}```"
        f"\n\nOriginal message:\n> {msg.content}"
    )
    try:
        await msg.author.send(content=notification_msg)
    except Exception as e:
        logger.warn(
            {
                "msg": "unable to send notification message to user",
                "user": msg.author.name,
                "notification_msg": notification_msg,
                "exception": str(e),
            }
        )
    await msg.delete()
    await discord_client.logout()
