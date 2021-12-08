from datetime import timedelta
from typing import Type

from fastapi import APIRouter, Depends, Response
from fastapi.logger import logger

from awesome_sso.exceptions import BadRequest, HTTPException, InternalServerError
from awesome_sso.service.depends import (
    JWTPayload,
    sso_registration,
    sso_user,
    sso_user_email,
)
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import (
    AccessToken,
    AwesomeUser,
    AwesomeUserType,
    RegisterModel,
)
from awesome_sso.util.jwt import SYMMETRIC_ALGORITHM, create_token

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


@router.post("/login", summary="get login access token", response_model=AccessToken)
async def login(user: Type[AwesomeUserType] = Depends(sso_user)):
    jwt_payload = JWTPayload(user_id=user.id).dict()
    jwt_payload["user_id"] = str(jwt_payload["user_id"])
    token = create_token(
        jwt_payload,
        Settings.symmetric_key,
        SYMMETRIC_ALGORITHM,
        expires_delta=timedelta(days=7),
    )
    return AccessToken(access_token=token)


@router.post("/unregister")
async def unregister(email: str = Depends(sso_user_email)):
    user = await Settings.user_model.find_one(Settings.user_model.email == email)
    if user is None:
        return Response(status_code=200, content="requested user not exist")
    else:
        await user.delete_data()
        await user.delete()
        return Response(status_code=200, content="user unregistered")
