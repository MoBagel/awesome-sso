from awesome_sso.user.schema import AwesomeUser, RegisterModel
from beanie import PydanticObjectId
import pytest

from tests.user.model import FantasticUser


@pytest.fixture
def register_model() -> RegisterModel:
    return RegisterModel(name="test", email="test@test.com", sso_user_id=PydanticObjectId())


async def test_user_registration(register_model):
    user = await AwesomeUser.register(register_model)
    assert user.name == register_model.name
    assert user.email == register_model.email
    assert user.sso_user_id == register_model.sso_user_id
    assert 'fantastic' not in user.dict()


async def test_child_user(register_model):
    user: FantasticUser = await FantasticUser.register(register_model)
    assert user.name == register_model.name
    assert user.email == register_model.email
    assert user.sso_user_id == register_model.sso_user_id
    assert user.dict()['fantastic']
