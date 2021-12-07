from typing import Optional, Generic, ClassVar, Type

from awesome_sso.user.schema import AwesomeUserType


class Settings(Generic[AwesomeUserType]):
    public_key: Optional[str] = None
    user_model: ClassVar[AwesomeUserType]

    @staticmethod
    def init_app(public_key_path: str, user_model: Type[AwesomeUserType]):
        Settings.user_model = user_model
        Settings.public_key = open(public_key_path).read()