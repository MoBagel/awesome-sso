from typing import Generic, Optional

from fastapi.logger import logger
from pydantic import AnyHttpUrl, parse_obj_as

from awesome_sso.service.user.schema import AwesomeUser, AwesomeUserType


class Settings(Generic[AwesomeUserType]):
    sso_domain: AnyHttpUrl
    service_name: Optional[str] = None
    public_key: str = ""
    private_key: Optional[str] = None
    symmetric_key: Optional[str] = None
    user_model: AwesomeUserType

    @classmethod
    def init_app(
        cls,
        symmetric_key: str,
        user_model: AwesomeUserType,
        service_name: str,
        public_key: str,
        private_key: str = None,
        sso_domain: str = "http://sso-be:3500/api/sso",
    ):
        cls.user_model = user_model
        cls.public_key = public_key
        cls.private_key = private_key
        cls.symmetric_key = symmetric_key
        cls.service_name = service_name
        cls.sso_domain = parse_obj_as(AnyHttpUrl, sso_domain)
