from fastapi import APIRouter, Depends

from awesome_sso.exceptions import BadRequest
from awesome_sso.user.depends import sso_registration
from awesome_sso.user.schema import RegisterModel, AwesomeUserType
from awesome_sso.client.settings import Settings

router = APIRouter(tags=["sso"])


@router.post("/register")
async def register(register_model: RegisterModel = Depends(sso_registration)):
    user: AwesomeUserType = await Settings.user_model.find_one(Settings.user_model.email == register_model.email)
    if user is None:
        user = Settings.user_model.register(register_model)
    else:
        raise BadRequest(message="user email %s taken" % register_model.email)
    return user
