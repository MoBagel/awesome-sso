import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from awesome_sso.service import Service
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import AwesomeUser, RegisterModel
from awesome_sso.util.jwt import create_jwt_token, PUBLIC_KEY
from tests.conftest import init_mongo

cli: AsyncIOMotorClient


@pytest.fixture()
def app():
    app = FastAPI(on_startup=[init_mongo])
    service_settings: Settings = Settings()
    service: Service = Service()

    service_settings.init_app(PUBLIC_KEY, AwesomeUser)
    service.init_app(app)
    return app


@pytest.fixture()
def client(app):
    return TestClient(app)


def test_root(client):
    with client:
        response = client.get("/sso")
        assert response.status_code == 200, response.text
        assert response.json() == ["OK"]


def test_register(register_model: RegisterModel, client):
    with client:
        response = client.post("/sso/register")
        assert response.status_code == 403, response.text
        invalid_headers = {"Authorization": "Bearer CHLOEISBOSS"}
        response = client.post("/sso/register", headers=invalid_headers)
        assert response.status_code == 401, response.text
        token = "Bearer %s" % create_jwt_token(register_model.dict())
        valid_headers = {"Authorization": token}
        response = client.post("/sso/register", headers=valid_headers)
        assert response.status_code == 422, response.text
        response = client.post("/sso/register", data=register_model.json(), headers=valid_headers)
        assert response.status_code == 200, response.text
