from datetime import timedelta

from beanie import DeleteRules
from fastapi import APIRouter, Depends, Response
from fastapi.logger import logger

from awesome_sso.exceptions import BadRequest, HTTPException, InternalServerError
from awesome_sso.service.depends import sso_registration, sso_user, sso_user_email
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import AccessToken, AwesomeUserType, RegisterModel
from awesome_sso.util.jwt import SYMMETRIC_ALGORITHM, create_token

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


@router.post("/login", summary="get login access token", response_model=AccessToken)
async def login(user: AwesomeUserType = Depends(sso_user)):
    jwt_payload = {"sso_user_id": str(user.sso_user_id)}
    token = create_token(
        jwt_payload,
        Settings.symmetric_key,
        SYMMETRIC_ALGORITHM,
        expires_delta=timedelta(days=7),
    )
    return AccessToken(access_token=token)


@router.post("/unregister")
async def unregister(email: str = Depends(sso_user_email)):
    user = await Settings[AwesomeUserType]().user_model.find_one(  # type: ignore
        Settings[AwesomeUserType]().user_model.email == email  # type: ignore
    )
    if user is None:
        return Response(status_code=200, content="requested user not exist")
    else:
        await user.delete_data()
        await user.delete(link_rule=DeleteRules.DELETE_LINKS)
        return Response(status_code=200, content="user unregistered")
