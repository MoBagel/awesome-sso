from typing import Optional


class HTTPException(Exception):
    detail: dict
    status_code: int
    error_code: str

    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        args: dict = {},
    ):
        self.status_code = status_code
        self.detail = {"message": message, **args}
        self.error_code = error_code if error_code is not None else str(status_code)


class BadRequest(HTTPException):
    def __init__(self, message, error_code: Optional[str] = None, args: dict = {}):
        super().__init__(
            status_code=400,
            message="Bad Request: %s" % message,
            error_code=error_code,
            args=args,
        )


class Unauthorized(HTTPException):
    def __init__(self, message, error_code: Optional[str] = None, args: dict = {}):
        super().__init__(
            status_code=401,
            message="Unauthorized: %s" % message,
            error_code=error_code,
            args=args,
        )


class NotFound(HTTPException):
    def __init__(self, message, error_code: Optional[str] = None, args: dict = {}):
        super().__init__(
            status_code=404,
            message="Not Found: %s" % message,
            error_code=error_code,
            args=args,
        )


class ResourceGone(HTTPException):
    def __init__(self, message, error_code: Optional[str] = None, args: dict = {}):
        super().__init__(
            status_code=410,
            message="Resource Gone: %s" % message,
            error_code=error_code,
            args=args,
        )


class UnprocessableEntity(HTTPException):
    def __init__(self, message, error_code: Optional[str] = None, args: dict = {}):
        super().__init__(
            status_code=422,
            message="Unprocessable Entity: %s" % message,
            error_code=error_code,
            args=args,
        )


class InternalServerError(HTTPException):
    def __init__(self, message, error_code: Optional[str] = None, args: dict = {}):
        super().__init__(
            status_code=500,
            message="Internal Server Error: %s" % message,
            error_code=error_code,
            args=args,
        )
