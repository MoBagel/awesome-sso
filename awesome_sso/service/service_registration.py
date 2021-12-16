import os
from typing import List

import psutil
import requests
from fastapi.logger import logger

from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import ConfigOption, Service, ServiceStatus
from awesome_sso.util.response_error_check import response_error_check


def register_service(
    internal_domain: str, hostname: str, config_options: List[ConfigOption]
):
    internal_domain = internal_domain
    hostname = hostname
    config_options = config_options
    service = Service(
        name=Settings.service_name,
        internal_domain="http://%s:3500" % internal_domain,
        external_domain="https://%s" % hostname,
        status=ServiceStatus.HEALTHY,
        mem_percent=psutil.virtual_memory().percent,
        cpu_percent=psutil.cpu_percent(),
        config_options=config_options,
    )
    registration_url = Settings.sso_domain + "/register"
    try:
        resp = requests.post(registration_url, json=service.dict(), timeout=5)
        resp.close()
        response_error_check(resp)
    except Exception as e:
        logger.warning("unable to register with sso: %s", str(e))


def unregister_service():
    if os.environ.get("SSO_REGISTER") == "true":
        unregister_url = (
            Settings.sso_domain + "/unregister?service_name=%s" % Settings.service_name
        )
        try:
            resp = requests.post(unregister_url, timeout=5)
            resp.close()
            response_error_check(resp)
        except Exception as e:
            logger.warning("unable to unregister with sso: %s", str(e))
