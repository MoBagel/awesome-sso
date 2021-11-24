class HTTPException(Exception):
    detail: str
    status_code: int


class BadRequest(HTTPException):
    def __init__(self, message):
        self.detail = "Bad Request: %s" % message
        self.status_code = 400


class Unauthorized(HTTPException):
    def __init__(self, message):
        self.detail = "Unauthorized: %s" % message
        self.status_code = 401


class NotFound(HTTPException):
    def __init__(self, message):
        self.detail = "Not Found: %s" % message
        self.status_code = 403


class ResourceGone(HTTPException):
    def __init__(self, message):
        self.detail = "Resource Gone: %s" % message
        self.status_code = 410


class UnprocessableEntity(HTTPException):
    def __init__(self, message):
        self.detail = "Unprocessable Entity: %s" % message
        self.status_code = 422


class InternalServerError(HTTPException):
    def __init__(self, message):
        self.detail = "Internal Server Error: %s" % message
        self.status_code = 500
