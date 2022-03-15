import asyncio

import discord_client
from logger import LOGGER as logger
from http_response import HTTPError, new_ephemeral_message


def message_violation(*args, **kwargs):
    return asyncio.run(_async_message_violation(*args, **kwargs))


async def _async_message_violation(channel_id, message_id, explanation):

    logger.debug({"channel_id": channel_id, "message_id": message_id})

    client = await discord_client.get_client()
    channel = await client.fetch_channel(channel_id)
    if not channel:
        raise HTTPError(http_response=new_ephemeral_message(f"channel {channel_id} not found (make sure bot is added to the channel)"))

    msg = await channel.fetch_message(message_id)
    if not msg:
        raise HTTPError(http_response=new_ephemeral_message(f"message {message_id} not found"))

    guild = await client.fetch_guild(channel.guild.id)
    notification_msg = (
        ":warning: Violation Notice :warning:\n\n"
        f"Your message in channel <#{channel_id}> has been removed for violating one more more server rules (**{guild.name}**)."
        f"\n\nViolation explanation:```{explanation}```"
        f"\nOriginal message:\n> {msg.content}"
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
    await client.close()
