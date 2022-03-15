import asyncio
import discord

import discord_client
from logger import LOGGER as logger
from authz import check_authorized_guilds
from http_response import (
    SOMETHING_WENT_WRONG_ERROR,
    HTTPResponse,
    new_ephemeral_message,
)
from modal_submit import new_report_details_modal


# Application Commands


def application_command_handler(body):
    data = body["data"]
    check_authorized_guilds(body["guild_id"])

    calling_user_name = body["member"]["user"]["username"]
    calling_user_discriminator = body["member"]["user"]["discriminator"]
    logger.info(
        {
            "calling_user": f"{calling_user_name}#{calling_user_discriminator}",
            "interaction": "application_command",
        }
    )

    app_command_type = data["type"]

    handlers = {1: _slash_command_handler, 3: _message_command_handler}
    handler = handlers.get(
        app_command_type, _unimplemented_application_command(app_command_type)
    )

    return handler(body)


def _unimplemented_application_command(app_command_type):
    def handler(data):
        logger.error(f"unimplemented application command command: {app_command_type}")
        return SOMETHING_WENT_WRONG_ERROR

    return handler


# Message Commands


def _message_command_handler(body):
    message_commands = {"Mark as Violation": _mark_as_violation_message}
    name = body["data"]["name"]
    message_command = message_commands.get(name, _unimplemented_message_command(name))
    return message_command(body)


def _unimplemented_message_command(name):
    def handler(body):
        logger.error(f"unimplemented message command command: {name}")
        return SOMETHING_WENT_WRONG_ERROR

    return handler


def _mark_as_violation_message(body):
    data = body["data"]
    message_id = data["target_id"]
    channel_id = data["resolved"]["messages"][message_id]["channel_id"]
    guild_id = body["guild_id"]
    message = asyncio.run(_get_message(channel_id, message_id))
    return HTTPResponse(200, new_report_details_modal(guild_id, channel_id, message))


# Slash Commands


def _slash_command_handler(body):
    slash_commands = {"violation": _mark_as_violation_slash}
    name = body["data"]["name"]
    slash_command = slash_commands.get(name, _unimplemented_slash_command(name))
    return slash_command(body)


def _unimplemented_slash_command(name):
    def handler(body):
        logger.error(f"unrecognized slash command: {name}")
        return SOMETHING_WENT_WRONG_ERROR

    return handler


def _mark_as_violation_slash(body):
    data = body["data"]
    if len(data["options"]) != 1 or data["options"][0]["name"] != "message_id":
        logger.error({"msg": "not enough options or options with invalid name", "options": data["options"]})
        raise SOMETHING_WENT_WRONG_ERROR

    channel_id = body["channel_id"]
    guild_id = body["guild_id"]

    message_id = data["options"][0]["value"]
    message = asyncio.run(_get_message(channel_id, message_id))
    if not message:
        return new_ephemeral_message(f"Message `{message_id}` does not exist!")
    return HTTPResponse(
        200,
        new_report_details_modal(guild_id, channel_id, message),
    )


async def _get_message(channel_id, message_id):
    try:
        client = await discord_client.get_client()
        channel = await client.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
        await client.logout()
        return message
    except discord.errors.HTTPException as e:
        if e.status == 400 and f'Value "{message_id}" is not snowflake' in str(e):
            return None
        raise
    except:
        raise
