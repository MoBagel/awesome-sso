from typing import Type

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from awesome_sso.service import Service
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import AwesomeUser, RegisterModel, AwesomeUserType
from awesome_sso.util.jwt import create_jwt_token
from tests.conftest import init_mongo

cli: AsyncIOMotorClient

app = FastAPI(on_startup=[init_mongo])
service_settings: Settings = Settings()
service: Service = Service()
service.init_app(app)
client = TestClient(app)


@pytest.fixture(autouse=True)
def init(loop, symmetric_key: str, public_key: str, private_key: str):
    service_settings.init_app(public_key, private_key, symmetric_key, AwesomeUser)


def test_root():
    with client:
        response = client.get("/health_check")
        assert response.status_code == 200, response.text
        assert response.json() == ["OK"]


def test_register(register_model: RegisterModel):
    with client:
        response = client.post("/register")
        assert response.status_code == 403, response.text
        invalid_headers = {"Authorization": "Bearer CHLOEISBOSS"}
        response = client.post("/register", headers=invalid_headers)
        assert response.status_code == 401, response.text
        token = "Bearer %s" % create_jwt_token(register_model.dict())
        valid_headers = {"Authorization": token}
        response = client.post("/register", headers=valid_headers)
        assert response.status_code == 422, response.text
        response = client.post("/register", data=register_model.json(), headers=valid_headers)
        assert response.status_code == 200, response.text


def test_login(register_model: RegisterModel):
    with client:
        response = client.post("/login")
        assert response.status_code == 403, response.text
        invalid_headers = {"Authorization": "Bearer CHLOEISBOSS"}
        response = client.post("/login", headers=invalid_headers)
        assert response.status_code == 401, response.text
        token = "Bearer %s" % create_jwt_token(register_model.dict())
        valid_headers = {"Authorization": token}
        response = client.post("/register", data=register_model.json(), headers=valid_headers)
        assert response.status_code == 200, response.text
        response = client.post("/login", headers=valid_headers)
        assert response.status_code == 200, response.text


def test_unregister(register_model: RegisterModel):
    with client:
        response = client.post("/unregister")
        assert response.status_code == 403, response.text
        invalid_headers = {"Authorization": "Bearer CHLOEISBOSS"}
        response = client.post("/login", headers=invalid_headers)
        assert response.status_code == 401, response.text
        token = "Bearer %s" % create_jwt_token(register_model.dict())
        valid_headers = {"Authorization": token}
        response = client.post("/register", data=register_model.json(), headers=valid_headers)
        assert response.status_code == 200, response.text
        response = client.post("/unregister", headers=valid_headers)
        assert response.status_code == 200, response.text


