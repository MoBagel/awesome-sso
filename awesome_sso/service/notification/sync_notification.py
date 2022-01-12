import requests
from beanie import PydanticObjectId

from awesome_sso.service.notification.schema import UserNotificationListResponse
from awesome_sso.service.settings import Settings


async def sync_notification(
    sso_user_id: PydanticObjectId,
) -> UserNotificationListResponse:
    resp = requests.get(
        "%s/notification" % Settings.sso_domain,
        params={"user_id": str(sso_user_id)},
        timeout=5,
    )
    resp.close()
    if resp.status_code / 2 != 100:
        raise RuntimeError(
            "sync notification with sso failed. %s: "
            + str(resp.content.decode("utf-8"))
        )
    return UserNotificationListResponse.parse_obj(resp.json())
