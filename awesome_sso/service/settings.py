from typing import ClassVar, Generic, Optional, Type

from awesome_sso.service.user.schema import AwesomeUserType


class Settings(Generic[AwesomeUserType]):
    service_name: str
    public_key: Optional[str] = None
    private_key: Optional[str] = None
    symmetric_key: Optional[str] = None
    user_model: ClassVar[AwesomeUserType]

    @staticmethod
    def init_app(public_key: str, private_key: str, symmetric_key: str, user_model: Type[AwesomeUserType],
                 service_name: str):
        Settings.user_model = user_model
        Settings.public_key = public_key
        Settings.private_key = private_key
        Settings.symmetric_key = symmetric_key
        Settings.service_name = service_name
