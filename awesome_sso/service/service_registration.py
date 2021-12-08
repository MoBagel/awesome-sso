import logging
import os
from datetime import datetime

import psutil
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi.logger import logger

from awesome_sso.util.response_error_check import response_error_check

from awesome_sso.service.user.schema import ConfigConstraint, ConfigOption, ConfigType, Service, ServiceStatus
from awesome_sso.service.settings import Settings
sso_domain = "http://sso-be:3500/api/sso"
service_name = Settings.service_name


def register_service():
    internal_domain = os.environ.get("SERVICE_NAME")
    hostname = os.environ.get("HOSTNAME")
    config_options = [
        ConfigOption(
            name="max_campaign",
            description="maximum campaign allowed to create",
            type=ConfigType.INT,
            constraint=ConfigConstraint(max=1000000, min=1),
            default=2,
        ),
        ConfigOption(
            name="max_transaction_records",
            description="maximum accumulated customer data",
            type=ConfigType.INT,
            constraint=ConfigConstraint(max=1000000, min=500),
            default=500,
        ),
    ]
    service = Service(
        name=service_name,
        internal_domain="http://%s:3500" % internal_domain,
        external_domain="https://%s" % hostname,
        status=ServiceStatus.HEALTHY,
        mem_percent=psutil.virtual_memory().percent,
        cpu_percent=psutil.cpu_percent(),
        config_options=config_options,
    )
    registration_url = sso_domain + "/register"
    try:
        resp = requests.post(registration_url, json=service.dict())
        resp.close()
        response_error_check(resp)
    except Exception as e:
        logger.warn("unable to register with sso: %s", str(e))


def unregister_service():
    if os.environ.get("SSO_REGISTER") == "true":
        unregister_url = sso_domain + "/unregister?service_name=%s" % service_name
        try:
            resp = requests.post(unregister_url)
            resp.close()
            response_error_check(resp)
        except Exception as e:
            logger.warn("unable to unregister with sso: %s", str(e))


if os.environ.get("SSO_REGISTER") == "true":
    scheduler = AsyncIOScheduler()
    scheduler.start()
    logging.getLogger("apscheduler.executors.default").propagate = False
    scheduler.add_job(
        register_service, "interval", seconds=30, next_run_time=datetime.now()
    )
