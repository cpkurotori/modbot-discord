import json
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import traceback
import logging
import os
import discord
import asyncio

default_log_factory = logging.getLogRecordFactory()


def _log_factory(
    name, level, fn, lno, msg, args, exc_info, func=None, sinfo=None, **kwargs
):
    msg = json.dumps(msg)
    return default_log_factory(
        name, level, fn, lno, msg, args, exc_info, func=func, sinfo=sinfo, **kwargs
    )


logging.setLogRecordFactory(_log_factory)

log_level = os.getenv("LOGLEVEL", "INFO")
logger = logging.getLogger("modbot")
logger.setLevel(log_level)

ch = logging.StreamHandler()
ch.setLevel(log_level)

formatter = logging.Formatter(
    """{"ts": "%(asctime)s", "level": "%(levelname)s", "caller": "%(name)s.%(funcName)s:%(lineno)d", "log": %(message)s}"""
)
formatter.converter
ch.setFormatter(formatter)

logger.handlers.clear()
logger.addHandler(ch)
logger.propagate = False


class HTTPResponse:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body

    def response(self):
        return {"statusCode": self.status_code, "body": self.body}


class HTTPError(Exception):
    def __init__(self, status_code, body):
        self.resp = HTTPResponse(status_code, body)

    def response(self):
        return self.resp.response()


INTERNAL_SERVER_ERROR = HTTPError(500, "Internal Server Error")


def validate_signature(event):
    try:
        public_key = os.getenv("DISCORD_BOT_PUBLIC_KEY")
        if public_key:
            body = event["body"]
            signature = event["headers"]["x-signature-ed25519"]
            timestamp = event["headers"]["x-signature-timestamp"]

            logger.debug({"signature": signature, "timestamp": timestamp, "body": body})

            verify_key = VerifyKey(bytes.fromhex(public_key))
            verify_key.verify(
                f"{timestamp}{body}".encode(), signature=bytes.fromhex(signature)
            )
    except BadSignatureError as e:
        logger.debug({"msg": "verification failed", "exception": str(e)})
        raise HTTPError(401, "Unauthorized")
    except Exception as e:
        logger.info({"exception": e, "msg": "validate signature failed"})
        raise HTTPError(401, "Unauthorized")


def check_authorized_guilds(guild_id):
    guilds = os.getenv("AUTHORIZED_GUILDS").split(",")
    for guild in guilds:
        if guild_id.strip() == guild.strip():
            return
    raise HTTPError(401, "Unauthorized")   


def ping_handler(body):
    return HTTPResponse(200, json.dumps({"type": 1}))


def application_command_handler(body):
    data = body["data"]
    check_authorized_guilds(body["guild_id"])

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


async def async_modal_submit_handler(body):
    data = body["data"]
    check_authorized_guilds(body["guild_id"])

    modal_id = str(data["custom_id"])
    if not modal_id.startswith("report_details:"):
        logger.debug({"modal_id", modal_id})
        return HTTPResponse(
            200,
            json.dumps(
                {
                    "type": 4,
                    "data": {
                        "content": "Unknown type of modal!",
                        "flags": 1 << 6,
                    },
                }
            ),
        )
    channel_id, message_id = modal_id[len("report_details:") :].split(":")
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

    explanation = data["components"][0]["components"][0]["value"]
    notification_msg = (
        f"Your message in channel <#{channel_id}> has been removed for violating one more more server rules ({guild.name})."
        f"\n\nViolation explanation:\n`{explanation}`"
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


def modal_submit_handler(body):
    return asyncio.run(async_modal_submit_handler(body))


def default_not_implemented(type):
    return lambda body: HTTPResponse(
        200,
        json.dumps(
            {
                "type": 4,
                "data": {
                    "content": f"Interaction type {type} not implemented!",
                    "flags": 1 << 6,
                },
            }
        ),
    )


def lambda_handler(event, context):
    try:
        validate_signature(event)
        body = json.loads(event["body"])
        handlers = {
            1: ping_handler,
            2: application_command_handler,
            5: modal_submit_handler,
        }
        handler = handlers.get(body["type"], default_not_implemented(body["type"]))
        response = handler(body)
        logger.info(
            {
                "msg": "response complete",
                "response_statuscode": response.status_code,
            }
        )
        logger.debug(
            {
                "msg": "debug body",
                "response_body": response.body,
            }
        )

        return response.response()
    except HTTPError as e:
        logger.info(
            {"response_statuscode": e.resp.status_code, "response_message": e.resp.body}
        )
        return e.response()
    except Exception as e:
        print(traceback.format_exc())
        logger.error(
            {
                "exception": str(e),
                "response_statuscode": INTERNAL_SERVER_ERROR.resp.status_code,
                "response_message": INTERNAL_SERVER_ERROR.resp.body,
            }
        )
        return INTERNAL_SERVER_ERROR.response()
