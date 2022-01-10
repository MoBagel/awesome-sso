import json
from typing import List

import requests
from pydantic import EmailStr, HttpUrl


class MailGun:
    def __init__(
        self,
        base_url: HttpUrl,
        api_key: str,
    ):
        self.base_url = base_url
        self.api_key = api_key

    def send_simple_message(
        self,
        source_name: str,
        source_email: EmailStr,
        target_emails: List[EmailStr],
        subject: str,
        text: str,
    ):
        return requests.post(
            self.base_url + "/messages",
            auth=("api", self.api_key),
            data={
                "from": "%s <%s>" % (source_name, source_email),
                "to": target_emails,
                "subject": subject,
                "text": text,
            },
        )

    def send_template(
        self,
        source_name: str,
        source_email: EmailStr,
        target_emails: List[EmailStr],
        subject: str,
        template: str,
        data: dict,
    ):
        return requests.post(
            self.base_url + "/messages",
            auth=("api", self.api_key),
            data={
                "from": "%s <%s>" % (source_name, source_email),
                "to": target_emails,
                "subject": subject,
                "template": template,
                "h:X-Mailgun-Variables": json.dumps(data),
            },
        )
