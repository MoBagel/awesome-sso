import jwt
from fastapi import Depends, Security
from fastapi.logger import logger
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import EmailStr
from awesome_sso.client.settings import Settings

from awesome_sso.exceptions import NotFound, Unauthorized
from awesome_sso.user.schema import RegisterModel, AwesomeUserType

ALGORITHM = "RS256"
security = HTTPBearer()


async def sso_token_decode(
        credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    try:
        jwt_token = credentials.credentials
        payload = jwt.decode(jwt_token, Settings.public_key, algorithms=[ALGORITHM])
        del payload["exp"]
    except Exception as e:
        logger.warn(e)
        raise Unauthorized(message=str(e))
    return payload


async def sso_registration(
        register_model: RegisterModel, payload: dict = Depends(sso_token_decode)
) -> RegisterModel:
    if payload != register_model.dict():
        logger.warn(payload)
        logger.warn(register_model.dict())
        raise Unauthorized(message="authentication invalid")
    return RegisterModel(**payload)


async def sso_user_email(payload: dict = Depends(sso_token_decode)) -> EmailStr:
    if "email" not in payload:
        logger.warn(payload)
        raise NotFound("email not found")
    return payload["email"]


async def sso_user(user_email: dict = Depends(sso_user_email)) -> AwesomeUserType:
    user = await AwesomeUserType.find_one(AwesomeUserType.email == user_email)
    if user is None:
        raise NotFound("user not found")
    return user