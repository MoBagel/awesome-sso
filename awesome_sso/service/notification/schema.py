from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel


class NotificationType(str, Enum):
    BROADCAST = "broadcast"
    MULTICAST = "multicast"


class Action(str, Enum):
    WEB = "web"
    EMAIL = "email"
    LINE = "line"


class UserNotification(BaseModel):
    id: PydanticObjectId
    message: str
    type: NotificationType
    action: Action = Action.WEB
    service: Optional[str]
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    option: Dict[str, Any] = {}
    read: bool
    created_at: datetime


class UserNotificationListResponse(BaseModel):
    list: List[UserNotification]
    total: int
    page: Optional[int]
    page_size: Optional[int]
