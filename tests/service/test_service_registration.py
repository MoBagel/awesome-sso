import pytest
from pydantic import AnyUrl, AnyHttpUrl

from awesome_sso.service.service_registration import register_service, unregister_service
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import AwesomeUser

settings: Settings = Settings()


@pytest.fixture(autouse=True)
def init(loop, symmetric_key: str, public_key: str, private_key: str, service_name: str, sso_domain: AnyHttpUrl):
    settings.init_app(public_key, private_key, symmetric_key, AwesomeUser, service_name, sso_domain)


def test_register_service(internal_service_name, config_options, hostname):
    register_service(internal_service_name, hostname, config_options)


def test_unregister_service(internal_service_name, config_options, hostname):
    unregister_service()
