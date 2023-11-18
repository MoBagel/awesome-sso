import json
from typing import BinaryIO, List

from fastapi.logger import logger
from pydantic import EmailStr, HttpUrl
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from awesome_sso.service.settings import Settings


def init_session() -> Session:
    session = Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class MailGun:
    def __init__(
        self,
        base_url: HttpUrl,
        api_key: str,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.session = init_session()

    def send_simple_message(
        self,
        from_name: str,
        from_email: EmailStr,
        to: List[EmailStr],
        subject: str,
        text: str,
        attachments: List[BinaryIO] = [],
        cc: List[EmailStr] = [],
        bcc: List[EmailStr] = [],
        tags: List[str] = [],
    ):
        return self.session.post(
            self.base_url + "/messages",
            auth=("api", self.api_key),
            files=[("attachment", attachment) for attachment in attachments],
            data={
                "from": "%s <%s>" % (from_name, from_email),
                "to": to,
                "cc": cc,
                "bcc": bcc,
                "subject": subject,
                "text": text,
                "o:tag": tags + [Settings.service_name],
            },
        )

    def send_template(
        self,
        from_name: str,
        from_email: EmailStr,
        to: List[EmailStr],
        subject: str,
        template: str,
        data: dict,
        attachments: List[BinaryIO] = [],
        cc: List[EmailStr] = [],
        bcc: List[EmailStr] = [],
        tags: List[str] = [],
    ):
        if self.base_url == "":
            logger.warning("not email because mailgun_base_url not configures")
            return
        return self.session.post(
            self.base_url + "/messages",
            auth=("api", self.api_key),
            files=[("attachment", attachment) for attachment in attachments],
            data={
                "from": "%s <%s>" % (from_name, from_email),
                "to": to,
                "cc": cc,
                "bcc": bcc,
                "subject": subject,
                "template": template,
                "h:X-Mailgun-Variables": json.dumps(data),
                "o:tag": tags + [Settings.service_name],
            },
        )
