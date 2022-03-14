import json

from http_response import HTTPResponse


def ping_handler(body):
    return HTTPResponse(200, json.dumps({"type": 1}))
