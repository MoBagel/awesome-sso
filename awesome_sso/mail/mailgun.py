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
        from_name: str,
        from_email: EmailStr,
        to: List[EmailStr],
        subject: str,
        text: str,
        cc: List[EmailStr] = [],
        bcc: List[EmailStr] = [],
    ):
        return requests.post(
            self.base_url + "/messages",
            auth=("api", self.api_key),
            data={
                "from": "%s <%s>" % (from_name, from_email),
                "to": to,
                "cc": cc,
                "bcc": bcc,
                "subject": subject,
                "text": text,
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
        cc: List[EmailStr] = [],
        bcc: List[EmailStr] = [],
    ):
        return requests.post(
            self.base_url + "/messages",
            auth=("api", self.api_key),
            data={
                "from": "%s <%s>" % (from_name, from_email),
                "to": to,
                "cc": cc,
                "bcc": bcc,
                "subject": subject,
                "template": template,
                "h:X-Mailgun-Variables": json.dumps(data),
            },
        )
