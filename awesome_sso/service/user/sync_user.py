import requests

from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import AwesomeUserType


async def sync_user(user: AwesomeUserType):
    resp = requests.get(
        "%s/user" % Settings.sso_domain,
        params={"user_id": str(user.sso_user_id)},
        timeout=5,
    )
    resp.close()
    if resp.status_code / 2 != 100:
        raise RuntimeError(
            "update vendor info failed: " + str(resp.content.decode("utf-8"))
        )
    sso_user = resp.json()
    user.email = sso_user["email"]
    user.name = sso_user["name"]
    services = sso_user["services"]
    services_info = []
    config_values = {}
    for service in services:
        if service["service_name"] == Settings.service_name:
            config_values = {
                config["name"]: config["value"] for config in service["config_values"]
            }
            if "status" in service and service["status"] == "trial_ended":
                config_values["status"] = "trial_ended"
        services_info.append(
            {
                "service_name": service["service_name"],
                "external_domain": service["external_domain"],
            }
        )
    config_values["services"] = services_info
    user.settings = config_values
    await user.save()
