from awesome_exception.exceptions import HTTPException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from awesome_sso.service.route import router


class Service:
    @staticmethod
    def init_app(app: FastAPI):
        app.include_router(router)

        @app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, "error_code": exc.error_code},
            )
