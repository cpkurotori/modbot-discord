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
