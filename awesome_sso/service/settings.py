from typing import ClassVar, Generic, Optional, Type

from pydantic import AnyHttpUrl, AnyUrl

from awesome_sso.service.user.schema import AwesomeUserType


class Settings(Generic[AwesomeUserType]):
    sso_domain: Optional[AnyHttpUrl] = None
    service_name: Optional[str] = None
    public_key: Optional[str] = None
    private_key: Optional[str] = None
    symmetric_key: Optional[str] = None
    user_model: ClassVar[AwesomeUserType]

    @staticmethod
    def init_app(
        public_key: str,
        private_key: str,
        symmetric_key: str,
        user_model: Type[AwesomeUserType],
        service_name: str,
        sso_domain: AnyHttpUrl,
    ):
        Settings.user_model = user_model
        Settings.public_key = public_key
        Settings.private_key = private_key
        Settings.symmetric_key = symmetric_key
        Settings.service_name = service_name
        Settings.sso_domain = sso_domain
