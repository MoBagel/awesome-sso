import os
from typing import Optional

import jwt
from beanie import PydanticObjectId
from fastapi import Cookie, Depends, Security
from fastapi.logger import logger
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from awesome_sso.exceptions import BadRequest, NotFound, Unauthorized
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import AwesomeUserType, RegisterModel
from awesome_sso.util.constant import MOCK_USER_ID
from awesome_sso.util.jwt import ASYMMETRIC_ALGORITHM, SYMMETRIC_ALGORITHM

security = HTTPBearer()


class JWTPayload(BaseModel):
    sso_user_id: Optional[PydanticObjectId] = None


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


def sso_user_email(payload: dict = Depends(sso_token_decode)) -> EmailStr:
    if "email" not in payload:
        logger.warning(payload)
        raise BadRequest("email not found")
    return payload["email"]


async def sso_user(user_email: EmailStr = Depends(sso_user_email)) -> AwesomeUserType:
    user = await Settings[AwesomeUserType]().user_model.find_one(
        Settings[AwesomeUserType]().user_model.email == user_email, fetch_links=True
    )
    if user is None:
        raise NotFound("user not found")
    return user


async def jwt_token_decode(eightpoint: str = Cookie(None)) -> JWTPayload:
    try:
        payload = jwt.decode(
            eightpoint, Settings.symmetric_key, algorithms=[SYMMETRIC_ALGORITHM]
        )
    except Exception as e:
        environment = os.environ.get("ENV")
        if environment is None or environment == "":
            logger.warning("using mock user")
            payload = {"sso_user_id": MOCK_USER_ID}
        else:
            logger.warning(e)
            raise Unauthorized(str(e))

    try:
        jwt_payload = JWTPayload(sso_user_id=PydanticObjectId(payload["sso_user_id"]))
    except Exception as e:
        raise Unauthorized(str(e))
    return jwt_payload


def sso_user_id(
    payload: JWTPayload = Depends(jwt_token_decode),
) -> PydanticObjectId:
    if payload.sso_user_id is None:
        logger.warning(payload)
        raise BadRequest("sso user id not found")
    return payload.sso_user_id


async def get_current_user(
    sso_id: PydanticObjectId = Depends(sso_user_id),
) -> AwesomeUserType:
    user = await Settings[AwesomeUserType]().user_model.find_one(
        Settings[AwesomeUserType]().user_model.sso_user_id == sso_id, fetch_links=True
    )
    if user is None:
        raise NotFound("user not found")
    return user
