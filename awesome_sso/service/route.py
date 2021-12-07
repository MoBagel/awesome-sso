from typing import Type

from fastapi import APIRouter, Depends

from awesome_sso.exceptions import BadRequest, InternalServerError
from awesome_sso.service.depends import sso_registration
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import RegisterModel

router = APIRouter(tags=["sso"])


@router.get("")
def get_empty():
    return ["OK"]


@router.post("/register", summary="register user")
async def register(register_model: RegisterModel = Depends(sso_registration)):
    try:
        user: Type[Settings.user_model] = await Settings.user_model.find_one(Settings.user_model.email == register_model.email)
        if user is None:
            user = await Settings.user_model.register(register_model)
        else:
            raise BadRequest(message="user email %s taken" % register_model.email)

    except Exception as e:
        raise InternalServerError(message=str(e))
    return user
