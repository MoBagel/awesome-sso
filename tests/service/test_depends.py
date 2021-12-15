import pytest
from beanie import PydanticObjectId
from pydantic import AnyHttpUrl

from awesome_sso.exceptions import NotFound, BadRequest
from awesome_sso.service.depends import sso_user_email, sso_user, JWTPayload, sso_user_id, get_current_user
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import RegisterModel, AwesomeUser
from tests.conftest import init_mongo

settings: Settings = Settings()


@pytest.fixture(autouse=True)
async def init(loop, symmetric_key: str, public_key: str, private_key: str, service_name: str, sso_domain: AnyHttpUrl):
    await init_mongo()
    settings.init_app(public_key=public_key, private_key=private_key, symmetric_key=symmetric_key,
                      user_model=AwesomeUser, service_name=service_name, sso_domain=sso_domain)


@pytest.fixture
async def registered_user(register_model: RegisterModel) -> AwesomeUser:
    user = await AwesomeUser.register(register_model)
    return user


def test_sso_user_email(register_model: RegisterModel):
    email = sso_user_email(register_model.dict())
    assert email == register_model.email
    with pytest.raises(BadRequest):
        sso_user_email({})


async def test_sso_user(registered_user: AwesomeUser, register_model: RegisterModel):
    test_user = await sso_user(register_model.email)
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
