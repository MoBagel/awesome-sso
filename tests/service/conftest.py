import string
import random
from typing import List

import pytest
from beanie import PydanticObjectId
from pydantic import EmailStr

from awesome_sso.service.depends import JWTPayload
from awesome_sso.service.user.schema import RegisterModel, ConfigOption, ConfigType, ConfigConstraint


@pytest.fixture
def register_model() -> RegisterModel:
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return RegisterModel(name="test_%s" % random_string, email="test%s@test.com" % random_string,
                         sso_user_id=PydanticObjectId())


@pytest.fixture
async def service_name() -> str:
    return 'awesome'


@pytest.fixture
def sso_domain() -> str:
    return "http://sso-be:3500/api/sso"


@pytest.fixture
def internal_service_name() -> str:
    return "awesome-be"


@pytest.fixture
def config_options() -> List[ConfigOption]:
    return [
        ConfigOption(
            name="max_campaign",
            description="maximum campaign allowed to create",
            type=ConfigType.INT,
            constraint=ConfigConstraint(max=1000000, min=1),
            default=2,
        ),
        ConfigOption(
            name="max_transaction_records",
            description="maximum accumulated customer data",
            type=ConfigType.INT,
            constraint=ConfigConstraint(max=1000000, min=500),
            default=500,
        ),
    ]


@pytest.fixture
def hostname() -> str:
    return 'test.com'


@pytest.fixture
def email() -> EmailStr:
    return EmailStr('test@test.com')


@pytest.fixture
def jwt_payload() -> JWTPayload:
    return JWTPayload(sso_user_id=PydanticObjectId())


@pytest.fixture
def object_id() -> PydanticObjectId:
    return PydanticObjectId()
