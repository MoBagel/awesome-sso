import os
from multiprocessing import Process
from typing import Optional

import pytest
import requests
import uvicorn
from fastapi import FastAPI
from pydantic import AnyHttpUrl

from awesome_sso.service.service_registration import (
    register_service,
    unregister_service,
)
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import AwesomeUser, Service

settings: Settings = Settings()


class App:
    """Core application to test."""

    def __init__(self):
        self.api = FastAPI()
        # register endpoints
        self.api.post("/api/sso/register")(self.register_service)
        self.api.post("/api/sso/unregister")(self.unregister_service)
        self.api.get("/api/sso/service")(self.service)
        self.registered_service: Optional[Service] = None

    def register_service(self, service: Service):
        self.registered_service = service
        return {"message": "ok"}

    def unregister_service(self, service_name: str):
        if (
            self.registered_service is not None
            and self.registered_service.name == service_name
        ):
            self.registered_service = None
        return {"message": "ok"}

    def service(self):
        if self.registered_service is None:
            return []
        return [self.registered_service]

    @staticmethod
    def get_service():
        resp = requests.get("http://localhost:3500/api/sso/service", timeout=5)
        resp.close()
        return resp.json()


app = App()
proc = Process(
    target=uvicorn.run,
    args=(app.api,),
    kwargs={"host": "127.0.0.1", "port": 3500, "log_level": "info"},
    daemon=True,
)
proc.start()


@pytest.fixture(autouse=True)
def init(
    loop,
    symmetric_key: str,
    public_key: str,
    private_key: str,
    service_name: str,
    sso_domain: AnyHttpUrl,
):
    settings.init_app(
        public_key=public_key,
        private_key=private_key,
        symmetric_key=symmetric_key,
        user_model=AwesomeUser,
        service_name=service_name,
        sso_domain=sso_domain,
    )


def test_service_discovery(internal_service_name, config_options, hostname):
    os.environ.setdefault("SSO_REGISTER", "true")
    assert app.get_service() == []
    register_service(internal_service_name, hostname, config_options)
    assert len(app.get_service()) > 0
    unregister_service()
    assert app.get_service() == []
