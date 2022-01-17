import pytest

from awesome_sso.service.user.schema import AwesomeUser
from tests.conftest import init_mongo
from tests.service.model import FantasticUser, UserWithExtraParameter


@pytest.fixture(autouse=True)
async def init(loop):
    await init_mongo()


async def test_user_registration(register_model):
    user = await AwesomeUser.register(register_model)
    assert user.name == register_model.name
    assert user.email == register_model.email
    assert user.sso_user_id == register_model.sso_user_id
    assert "fantastic" not in user.dict()


async def test_child_user(register_model):
    user: FantasticUser = await FantasticUser.register(register_model)
    assert user.name == register_model.name
    assert user.email == register_model.email
    assert user.sso_user_id == register_model.sso_user_id
    assert user.dict()["fantastic"]


async def test_child_user_with_extra_param(register_model):
    user: UserWithExtraParameter = await UserWithExtraParameter.register(register_model)
    assert user.name == register_model.name
    assert user.email == register_model.email
    assert user.sso_user_id == register_model.sso_user_id
    assert user.extra.nickname == register_model.name
