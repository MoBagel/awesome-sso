from typing import Optional

import jwt
from beanie import PydanticObjectId
from fastapi import Depends, Security
from fastapi.logger import logger
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from awesome_sso.exceptions import NotFound, Unauthorized
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import AwesomeUserType, RegisterModel
from awesome_sso.util.jwt import ASYMMETRIC_ALGORITHM

security = HTTPBearer()


class JWTPayload(BaseModel):
    user_id: Optional[PydanticObjectId] = None


async def sso_token_decode(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    try:
        jwt_token = credentials.credentials
        payload = jwt.decode(
            jwt_token, Settings.public_key, algorithms=[ASYMMETRIC_ALGORITHM]
        )
        del payload["exp"]
    except Exception as e:
        logger.warning(e)
        raise Unauthorized(message=str(e))
    return payload


async def sso_registration(
    register_model: RegisterModel, payload: dict = Depends(sso_token_decode)
) -> RegisterModel:
    payload["sso_user_id"] = PydanticObjectId(payload["sso_user_id"])
    if payload != register_model.dict():
        logger.warning(payload)
        logger.warning(register_model.dict())
        raise Unauthorized(message="authentication invalid")
    return RegisterModel(**payload)


async def sso_user_email(payload: dict = Depends(sso_token_decode)) -> EmailStr:
    if "email" not in payload:
        logger.warn(payload)
        raise NotFound("email not found")
    return payload["email"]


async def sso_user(user_email: dict = Depends(sso_user_email)) -> AwesomeUserType:
    user = await Settings[AwesomeUserType]().user_model.find_one(
        Settings[AwesomeUserType]().user_model.email == user_email
    )
    if user is None:
        raise NotFound("user not found")
    return user
