import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import AnyHttpUrl

from awesome_sso.service import Service
from awesome_sso.service.depends import sso_token_decode
from awesome_sso.service.settings import Settings
from awesome_sso.service.user.schema import AwesomeUser, RegisterModel
from awesome_sso.util.jwt import create_token
from tests.conftest import init_mongo

cli: AsyncIOMotorClient

app = FastAPI(on_startup=[init_mongo])
service_settings: Settings = Settings()
service: Service = Service()
service.init_app(app)
client = TestClient(app)


@pytest.fixture(autouse=True)
def init(
    loop,
    symmetric_key: str,
    public_key: str,
    private_key: str,
    service_name: str,
    sso_domain: AnyHttpUrl,
):
    service_settings.init_app(
        symmetric_key=symmetric_key,
        user_model=AwesomeUser,
        service_name=service_name,
        public_key=public_key,
        private_key=private_key,
        sso_domain=sso_domain,
    )


def test_root():
    with client:
        response = client.get("/health_check")
        assert response.status_code == 200, response.text
        assert response.json() == ["OK"]


def test_register(register_model: RegisterModel, asymmetric_algorithm):
    with client:
        response = client.post("/register")
        assert response.status_code == 403, response.text
        invalid_headers = {"Authorization": "Bearer CHLOEISBOSS"}
        response = client.post("/register", headers=invalid_headers)
        assert response.status_code == 401, response.text
        token = "Bearer %s" % create_token(
            register_model.dict(), Settings.private_key, asymmetric_algorithm
        )
        valid_headers = {"Authorization": token}
        response = client.post("/register", headers=valid_headers)
        assert response.status_code == 422, response.text
        response = client.post(
            "/register", data=register_model.json(), headers=valid_headers
        )
        assert response.status_code == 200, response.text
        # test register existed user
        response = client.post(
            "/register", data=register_model.json(), headers=valid_headers
        )
        assert response.status_code == 400, response.text


def test_login(
    register_model: RegisterModel,
    symmetric_key: str,
    symmetric_algorithm: str,
    asymmetric_algorithm,
):
    with client:
        response = client.post("/login")
        assert response.status_code == 403, response.text
        invalid_headers = {"Authorization": "Bearer CHLOEISBOSS"}
        response = client.post("/login", headers=invalid_headers)
        assert response.status_code == 401, response.text
        token = "Bearer %s" % create_token(
            register_model.dict(), Settings.private_key, asymmetric_algorithm
        )
        valid_headers = {"Authorization": token}
        user_response = client.post(
            "/register", data=register_model.json(), headers=valid_headers
        )
        assert user_response.status_code == 200, user_response.text
        response = client.post("/login", headers=valid_headers)
        assert response.status_code == 200, response.text


def test_unregister(register_model: RegisterModel, asymmetric_algorithm):
    with client:
        token = "Bearer %s" % create_token(
            register_model.dict(), Settings.private_key, asymmetric_algorithm
        )
        valid_headers = {"Authorization": token}
        response = client.post(
            "/register", data=register_model.json(), headers=valid_headers
        )
        assert response.status_code == 200, response.text
        response = client.post("/unregister")
        assert response.status_code == 403, response.text
        invalid_headers = {"Authorization": "Bearer CHLOEISBOSS"}
        response = client.post("/login", headers=invalid_headers)
        assert response.status_code == 401, response.text
        response = client.post("/unregister", headers=valid_headers)
        assert response.status_code == 200, response.text


def test_sso_registration(register_model, asymmetric_algorithm):
    async def override_dependency():
        return {
            "sso_user_id": "619b5ecad44afe99430824d3",
            "email": "mock@mock.com",
            "name": "test",
        }

    app.dependency_overrides[sso_token_decode] = override_dependency
    with client:
        token = "Bearer %s" % create_token(
            register_model.dict(), Settings.private_key, asymmetric_algorithm
        )
        valid_headers = {"Authorization": token}
        response = client.post(
            "/register", data=register_model.json(), headers=valid_headers
        )
        assert response.status_code == 401, response.text
