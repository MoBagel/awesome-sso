from fastapi.logger import logger
from requests import Response


def response_error_check(response: Response):
    if response.status_code / 2 != 100:
        if "json" in str(response.headers.get("content-type")):
            logger.error(response.json())
        else:
            logger.error(response.content.decode("utf-8"))
