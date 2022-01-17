import pytest

from awesome_sso.store.minio import MinioStore
from tests.datastore import generate_fake_dataframe


@pytest.fixture()
def test_string():
    return b"to grasp how wide and long and high and deep is the love of Christ"


@pytest.fixture()
def test_dataframe():
    return generate_fake_dataframe(size=100, cols="cicid")


@pytest.fixture()
def test_dict(test_string):
    return {"test_string": test_string.decode("utf-8")}


@pytest.fixture
def minio_store(settings):
    return MinioStore(
        host=settings.minio_host,
        bucket=settings.minio_bucket,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
    )
