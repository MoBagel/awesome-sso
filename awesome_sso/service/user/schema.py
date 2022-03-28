from datetime import datetime
from distutils.util import strtobool
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar

import requests
from beanie import Document, PydanticObjectId
from fastapi.logger import logger
from pydantic import AnyHttpUrl, BaseModel, EmailStr

import awesome_sso.service.settings as awesome_settings


class ConfigType(str, Enum):
    STRING = "str"
    INT = "int"
    BOOLEAN = "bool"


class ConfigConstraint(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None
    options: Optional[List[str]] = None


class ConfigValue(BaseModel):
    name: str
    description: str
    type: ConfigType
    value: Any

    def set_value(self, value):
        if self.type == ConfigType.INT:
            if type(value) == list:
                self.value = [int(x) for x in value]
            else:
                self.value = int(value)
        elif self.type == ConfigType.BOOLEAN:
            if type(value) == str:
                self.value = bool(strtobool(value))
            else:
                self.value = bool(value)
        else:
            self.value = value


class ConfigOption(BaseModel):
    name: str
    description: str
    type: ConfigType
    constraint: ConfigConstraint
    default: Any

    def to_config_value(self, value: Optional[Any] = None) -> ConfigValue:
        field_value = value if value is not None else self.default
        config = ConfigValue(
            name=self.name,
            description=self.description,
            type=self.type,
            value=field_value,
        )
        config.set_value(field_value)
        return config


class UpdateConfigValue(BaseModel):
    name: str
    value: Any


class UpdateUserService(BaseModel):
    service_name: str
    config_values: List[UpdateConfigValue] = []
    trial_end_at: Optional[datetime] = None

    class Config:
        anystr_strip_whitespace: True
        schema_extra = {
            "example": {
                "service_name": "restock",
                "config_values": [
                    {"name": "available_restock_unit", "value": ["month"]},
                    {"name": "max_store", "value": 2},
                    {"name": "max_sku", "value": 10},
                    {"name": "max_additional_store_columns", "value": 2},
                    {"name": "max_additional_commodity_columns", "value": 2},
                    {"name": "max_additional_POS_columns", "value": 2},
                ],
                "trial_end_at": "2022-04-01 00:00:00",
            }
        }


class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    DOWN = "down"
    END_OF_LIFE = "eof"


class Service(BaseModel):
    name: str
    internal_domain: AnyHttpUrl
    external_domain: AnyHttpUrl
    user_register_endpoint: str
    user_unregister_endpoint: str
    user_login_endpoint: str
    status: ServiceStatus = ServiceStatus.DOWN
    mem_percent: float
    cpu_percent: float
    config_options: List[ConfigOption] = []


class AccessToken(BaseModel):
    access_token: str


class RegisterModel(BaseModel):
    name: str
    email: EmailStr
    sso_user_id: PydanticObjectId


AwesomeUserType = TypeVar("AwesomeUserType", bound="AwesomeUser")


class AwesomeUser(Document):
    name: str
    email: EmailStr
    sso_user_id: PydanticObjectId
    settings: Dict[str, Any] = {}
    line_linked: bool = False

    class Collection:
        name = "user"

    @classmethod
    async def register(
        cls: Type[AwesomeUserType], args: RegisterModel
    ) -> AwesomeUserType:
        extra_params = await cls.extra_constructor_params(args)
        return await cls(**args.dict(), **extra_params).create()

    @classmethod
    async def extra_constructor_params(
        cls: Type[AwesomeUserType], args: RegisterModel
    ) -> dict:
        return {}

    async def delete_data(self):
        pass

    def update_settings(self, data: UpdateUserService):
        try:
            resp = requests.post(
                awesome_settings.Settings.sso_domain + "/user/service",
                params={"user_id": str(self.sso_user_id)},
                data=data.json(),
                timeout=3,
            )
            resp.close()

        except Exception as e:
            raise InterruptedError(str(e))

        if resp.status_code / 2 == 100:
            logger.info("sync user pricing plan with sso")
        else:
            logger.warning(f"sync user pricing plan with sso failed")
