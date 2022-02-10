import pytest
from beanie import PydanticObjectId
from pydantic import AnyHttpUrl

from awesome_sso.exceptions import BadRequest, NotFound
from awesome_sso.service.depends import (
    JWTPayload,
    get_current_user,
    jwt_token_decode,
    sso_user,
    get_sso_user_id,
    sso_user_id,
)
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import AwesomeUser, RegisterModel
from awesome_sso.util.constant import MOCK_USER_ID
from tests.conftest import init_mongo

settings: Settings = Settings()


@pytest.fixture(autouse=True)
async def init(
    loop,
    symmetric_key: str,
    public_key: str,
    private_key: str,
    service_name: str,
    sso_domain: AnyHttpUrl,
):
    await init_mongo()
    settings.init_app(
        public_key=public_key,
        private_key=private_key,
        symmetric_key=symmetric_key,
        user_model=AwesomeUser,
        service_name=service_name,
        sso_domain=sso_domain,
    )


@pytest.fixture
async def registered_user(register_model: RegisterModel) -> AwesomeUser:
    user = await AwesomeUser.register(register_model)
    return user


def test_get_sso_user_id(register_model: RegisterModel):
    sso_id = get_sso_user_id(register_model.dict())
    assert sso_id == register_model.sso_user_id
    with pytest.raises(BadRequest):
        get_sso_user_id({})


async def test_sso_user(registered_user: AwesomeUser, register_model: RegisterModel):
    test_user = await sso_user(register_model.sso_user_id)
    assert registered_user.id == test_user.id


def test_sso_user_id(jwt_payload: JWTPayload):
    test_user_id = sso_user_id(jwt_payload)
    assert test_user_id == jwt_payload.sso_user_id
    with pytest.raises(BadRequest):
        sso_user_id(JWTPayload())


async def test_get_current_user(registered_user: AwesomeUser):
    user = await get_current_user(registered_user.sso_user_id)
    assert user.id == registered_user.id
    with pytest.raises(NotFound):
        await get_current_user(PydanticObjectId())


async def test_token_decode(registered_user: AwesomeUser):
    jwt_payload = await jwt_token_decode("")
    assert str(jwt_payload.sso_user_id) == MOCK_USER_ID
