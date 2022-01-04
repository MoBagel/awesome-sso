from pydantic import BaseModel

from awesome_sso.service.user.schema import AwesomeUser


class FantasticUser(AwesomeUser):
    fantastic: bool = True


class ExtraParameter(BaseModel):
    nickname: str


class UserWithExtraParameter(AwesomeUser):
    extra: ExtraParameter

    @classmethod
    def extra_constructor_params(cls, args) -> dict:
        return {"extra": ExtraParameter(nickname=args.name)}
