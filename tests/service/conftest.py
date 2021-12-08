import string
import random

import pytest
from beanie import PydanticObjectId

from awesome_sso.service.user.schema import RegisterModel


@pytest.fixture
def register_model() -> RegisterModel:
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return RegisterModel(name="test_%s" % random_string, email="test%s@test.com" % random_string,
                         sso_user_id=PydanticObjectId())
