from typing import Generic, Optional, Type

from fastapi.logger import logger
from pydantic import AnyHttpUrl, parse_obj_as

from awesome_sso.service.user.schema import AwesomeUser, AwesomeUserType


class Settings(Generic[AwesomeUserType]):
    sso_domain: AnyHttpUrl
    service_name: Optional[str] = None
    public_key: str = ""
    private_key: Optional[str] = None
    symmetric_key: Optional[str] = None
    user_model: Type[AwesomeUserType] = AwesomeUser

    @staticmethod
    def init_app(
        symmetric_key: str,
        user_model: Type[AwesomeUserType],
        service_name: str,
        public_key: str,
        private_key: str = None,
        sso_domain: str = "http://sso-be:3500/api/sso",
    ):
        Settings.user_model = user_model
        Settings.public_key = public_key
        Settings.private_key = private_key
        Settings.symmetric_key = symmetric_key
        Settings.service_name = service_name
        Settings.sso_domain = parse_obj_as(AnyHttpUrl, sso_domain)
        logger.info("initialize setting")
