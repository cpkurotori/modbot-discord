import json

class HTTPResponse:
    def __init__(self, status_code, body, json_dump=True):
        self.status_code = status_code
        if json_dump:
            body = json.dumps(body)    
        self.body = body

    def response(self):
        return {"statusCode": self.status_code, "body": self.body}


class HTTPError(Exception):
    def __init__(self, *args, http_response=None, **kwargs):
        if http_response:
            self.resp = http_response
        else:
            self.resp = HTTPResponse(*args, **kwargs)

    def response(self):
        return self.resp.response()


INTERNAL_SERVER_ERROR = HTTPError(500, "Internal Server Error")

def new_ephemeral_message(content):
    return HTTPResponse(
            200,
            {
                "type": 4,
                "data": {
                    "content": content,
                    "flags": 1 << 6,
                },
            },
        )

SOMETHING_WENT_WRONG_ERROR = new_ephemeral_message("Something went wrong while processing your request. Please reach out to a bot maintainer if the problem persists.")