import pytest
from pydantic import BaseSettings, Field, HttpUrl

from awesome_sso.mail.mailgun import MailGun


class MailSettings(BaseSettings):
    BASE_URL: HttpUrl = Field(
        default="https://api.mailgun.net/v3/somedomain.mailgun.org"
    )
    API_KEY: str = Field(default="9d8h7324q65rcx7q34jr76txcq9243nd-awx4o9j8-wc9fye8h")

    class Config:
        env_prefix = "MAIL"


@pytest.fixture()
def mail_setting() -> MailSettings:
    return MailSettings()


@pytest.fixture()
def mailgun(mail_setting: MailSettings) -> MailGun:
    return MailGun(mail_setting.BASE_URL, mail_setting.API_KEY)
