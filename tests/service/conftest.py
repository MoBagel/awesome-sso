import pytest
from beanie import PydanticObjectId

from awesome_sso.service.user.schema import RegisterModel


@pytest.fixture
def register_model() -> RegisterModel:
    return RegisterModel(name="test", email="test@test.com", sso_user_id=PydanticObjectId())
