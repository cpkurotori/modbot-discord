import json

from logger import LOGGER as logger
from authz import check_authorized_guilds
from http_response import HTTPResponse
from message_violation import message_violation

_report_details_modal_id = "report_details"


def _modal_handler_not_found(modal_id):
    def handler_not_found(*args, **kwargs):
        return HTTPResponse(
            200,
            json.dumps(
                {
                    "type": 4,
                    "data": {
                        "content": f"Unknown type of modal: {modal_id}",
                        "flags": 1 << 6,
                    },
                }
            ),
        )

    return handler_not_found


def modal_submit_handler(body):
    data = body["data"]
    check_authorized_guilds(body["guild_id"])

    calling_user_name = body["member"]["user"]["username"]
    calling_user_discriminator = body["member"]["user"]["discriminator"]
    logger.debug({"calling_user": f"{calling_user_name}#{calling_user_discriminator}", "interaction": "modal_submit"})

    modal_id = str(data["custom_id"]).split(":")
    handlers = {_report_details_modal_id: report_details}

    handler = handlers.get(modal_id[0], _modal_handler_not_found(modal_id[0]))
    return handler(data, modal_id[1:])


def report_details(data, report_details_id):
    channel_id, message_id = report_details_id
    explanation = data["components"][0]["components"][0]["value"]
    message_violation(channel_id, message_id, explanation)
    return HTTPResponse(
        200,
        json.dumps(
            {
                "type": 4,
                "data": {
                    "content": "Message removed and user has been contacted.",
                    "flags": 1 << 6,
                },
            }
        ),
    )
