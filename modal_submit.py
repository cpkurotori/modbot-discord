import asyncio
import discord_client
from logger import LOGGER as logger
from authz import check_authorized_guilds
from http_response import (
    SOMETHING_WENT_WRONG_ERROR,
    new_ephemeral_message,
)
from message_violation import message_violation

REPORT_DETAILS_MODAL_ID = "report_details"


# Modal Submit


def modal_submit_handler(body):
    data = body["data"]
    check_authorized_guilds(body["guild_id"])

    calling_user_name = body["member"]["user"]["username"]
    calling_user_discriminator = body["member"]["user"]["discriminator"]
    logger.info(
        {
            "calling_user": f"{calling_user_name}#{calling_user_discriminator}",
            "interaction": "modal_submit",
        }
    )

    modal_id = str(data["custom_id"]).split(":")
    handlers = {REPORT_DETAILS_MODAL_ID: _report_details}

    handler = handlers.get(modal_id[0], _unimplemented_modal_submit(modal_id[0]))
    return handler(data, modal_id[1:])


def _unimplemented_modal_submit(modal_id):
    def handler(data, modal_values):
        logger.error(f"unknown type of modal: {modal_id}")
        return SOMETHING_WENT_WRONG_ERROR

    return handler


def _report_details(data, modal_values):
    channel_id, message_id = modal_values
    explanation = data["components"][0]["components"][0]["value"]
    message_violation(channel_id, message_id, explanation)
    return new_ephemeral_message("Message regmoved and user has been contacted.")


def new_report_details_modal(guild_id, channel_id, message):
    author = asyncio.run(_get_author(guild_id, message.author.id))
    username = author.nick or f"{author.name}#{author.discriminator}"

    message_id = message.id
    modal_id = f"{REPORT_DETAILS_MODAL_ID}:{channel_id}:{message_id}"
    placeholder = (
        f"Explanation for violation of message:\n@{username}: {message.content}"
    )

    max_placeholder_length = 97
    placeholder = placeholder[: min(max_placeholder_length, len(placeholder))] + (
        "..." if len(placeholder) > max_placeholder_length else ""
    )

    return {
        "type": 9,
        "data": {
            "custom_id": modal_id,
            "title": "Message Violation Report Details",
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 4,
                            "custom_id": "explanation",
                            "style": 2,
                            "label": "Explanation of Violation",
                            "min_length": 10,
                            "max_length": 4000,
                            "required": True,
                            "placeholder": placeholder,
                        }
                    ],
                },
            ],
        },
    }


async def _get_author(guild_id, user_id):
    client = await discord_client.get_client()
    guild = await client.fetch_guild(guild_id)
    member = await guild.fetch_member(user_id)
    return member
