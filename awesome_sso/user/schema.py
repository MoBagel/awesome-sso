from enum import Enum
from typing import Any, List, Optional, Dict, TypeVar, Type

from beanie import Document, PydanticObjectId
from pydantic import AnyHttpUrl, BaseModel, EmailStr


class ConfigType(str, Enum):
    STRING = "str"
    INT = "int"


class ConfigConstraint(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None
    options: Optional[List[str]] = None


class ConfigOption(BaseModel):
    name: str
    description: str
    type: ConfigType
    constraint: ConfigConstraint
    default: Any


class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    DOWN = "down"
    END_OF_LIFE = "eof"


class Service(BaseModel):
    name: str
    internal_domain: AnyHttpUrl
    external_domain: AnyHttpUrl
    user_register_endpoint: str = "/api/sso/register"
    user_unregister_endpoint: str = "/api/sso/unregister"
    user_login_endpoint: str = "/api/sso/login"
    status: ServiceStatus = ServiceStatus.DOWN
    mem_percent: float
    cpu_percent: float
    config_options: List[ConfigOption] = []


class AccessToken(BaseModel):
    access_token: str


class RegisterModel(BaseModel):
    name: str
    email: EmailStr
    sso_user_id: str


AwesomeUserType = TypeVar("AwesomeUserType", bound='AwesomeUser')


class AwesomeUser(Document):
    name: str
    email: EmailStr
    sso_user_id: PydanticObjectId
    setting: Dict[str, Any] = {}
    status: Dict[str, Any] = {}

    @classmethod
    async def register(cls: Type[AwesomeUserType], args: RegisterModel) -> AwesomeUserType:
        return await cls(name=args.name, email=args.email, sso_user_id=args.sso_user_id).create()


