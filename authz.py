import os

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from logger import LOGGER as logger
from http_response import HTTPError


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
    logger.warning(f"unauthorized guild: {guild_id}")
    raise HTTPError(401, "Unauthorized")
