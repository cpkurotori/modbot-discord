import json

from logger import LOGGER as logger
from authz import check_authorized_guilds
from http_response import HTTPResponse


def application_command_handler(body):
    data = body["data"]
    check_authorized_guilds(body["guild_id"])

    calling_user_name = body["member"]["user"]["username"]
    calling_user_discriminator = body["member"]["user"]["discriminator"]
    logger.debug({"calling_user": f"{calling_user_name}#{calling_user_discriminator}", "interaction": "application_command"})

    app_command_type = data["type"]

    if app_command_type != 3:
        return HTTPResponse(
            200,
            json.dumps(
                {
                    "type": 4,
                    "data": {
                        "content": f"Application command {app_command_type} not implemented!",
                        "flags": 1 << 6,
                    },
                }
            ),
        )

    name = data["name"]
    if name != "Mark as Violation":
        return HTTPResponse(
            200,
            json.dumps(
                {
                    "type": 4,
                    "data": {
                        "content": f"Unknown message command {name}!",
                        "flags": 1 << 6,
                    },
                }
            ),
        )

    message_id = data["target_id"]
    channel_id = data["resolved"]["messages"][message_id]["channel_id"]

    modal_id = f"report_details:{channel_id}:{message_id}"
    return HTTPResponse(
        200,
        json.dumps(
            {
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
                                }
                            ],
                        },
                    ],
                },
            }
        ),
    )
