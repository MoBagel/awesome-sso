from fastapi import APIRouter, Depends, Response
from fastapi.logger import logger

from awesome_sso.exceptions import BadRequest, HTTPException, InternalServerError
from awesome_sso.service.depends import (
    JWTPayload,
    jwt_token_decode,
    sso_registration,
    sso_token_decode,
    sso_user_email,
)
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import AwesomeUserType, RegisterModel

router = APIRouter(tags=["sso"])


@router.get("/health_check")
def health_check():
    return ["OK"]


@router.post("/register", summary="register user")
async def register(register_model: RegisterModel = Depends(sso_registration)):
    try:
        user = await Settings[AwesomeUserType]().user_model.find_one(  # type: ignore
            Settings[AwesomeUserType]().user_model.email == register_model.email  # type: ignore
        )
        if user is None:
            user = await Settings[AwesomeUserType]().user_model.register(register_model)  # type: ignore
        else:
            raise BadRequest(message="user email %s taken" % register_model.email)
    except HTTPException as e:
        logger.warning(str(e))
        raise e
    except Exception as e:
        logger.warning(str(e))
        raise InternalServerError(message=str(e))
    return user


@router.post("/login", summary="authenticate user")
async def login(payload: JWTPayload = Depends(sso_token_decode)):
    return "authenticated"


@router.post("/unregister")
async def unregister(email: str = Depends(sso_user_email)):
    user = await Settings[AwesomeUserType]().user_model.find_one(
        Settings[AwesomeUserType]().user_model.email == email
    )  # type: ignore
    if user is None:
        return Response(status_code=200, content="requested user not exist")
    else:
        await user.delete_data()
        await user.delete()
        return Response(status_code=200, content="user unregistered")
