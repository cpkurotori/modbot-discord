import json
import traceback

from logger import LOGGER as logger
from http_response import SOMETHING_WENT_WRONG_ERROR, HTTPError
from http_response import HTTPResponse
from http_response import INTERNAL_SERVER_ERROR
from authz import validate_signature
from application_command import application_command_handler
from modal_submit import modal_submit_handler


def lambda_handler(event, context):
    try:
        validate_signature(event)
        body = json.loads(event["body"])

        handlers = {
            1: _ping_handler,
            2: application_command_handler,
            5: modal_submit_handler,
        }
        handler = handlers.get(
            body["type"], _unimplemented_interaction_submit(body["type"])
        )
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


def _unimplemented_interaction_submit(interaction_type):
    def handler(body):
        logger.error(f"interaction type {interaction_type} not implemented")
        return SOMETHING_WENT_WRONG_ERROR

    return handler


# Ping


def _ping_handler(body):
    return HTTPResponse(200, {"type": 1})
