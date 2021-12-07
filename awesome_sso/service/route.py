from typing import Type

from fastapi import APIRouter, Depends
from fastapi.logger import logger

from awesome_sso.exceptions import BadRequest, HTTPException, InternalServerError
from awesome_sso.service.depends import sso_registration
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import AwesomeUser, RegisterModel

router = APIRouter(tags=["sso"])


@router.get("/health_check")
def health_check():
    return ["OK"]


@router.post("/register", summary="register user", response_model=AwesomeUser)
async def register(register_model: RegisterModel = Depends(sso_registration)):
    try:
        user: Type[Settings.user_model] = await Settings.user_model.find_one(
            Settings.user_model.email == register_model.email
        )
        if user is None:
            user = await Settings.user_model.register(register_model)
        else:
            raise BadRequest(message="user email %s taken" % register_model.email)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.warning(str(e))
        raise InternalServerError(message=str(e))
    return user
