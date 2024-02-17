[![Stable Version](https://badge.fury.io/py/awesome-sso.svg)](https://pypi.org/project/awesome-sso/)
[![tests](https://github.com/MoBagel/awesome-sso/workflows/develop/badge.svg)](https://github.com/MoBagel/awesome-sso)
[![Coverage Status](https://coveralls.io/repos/github/MoBagel/awesome-sso/badge.svg?branch=develop)](https://coveralls.io/github/MoBagel/awesome-sso)

# Awesome SSO

A library designed to host common components for a cluster of microservices sharing a single sign on.

## Feature

- [x] A common exception class, supporting both status code and custom error code to map to more detailed error message
  or serve as i18n key.
- [x] A common FastAPI app for interaction with service, like login ,registration and unregistration.
- [x] a connector for minio object store.
- [x] a connector for beanie, a mongo odm compatible with pydantic.

## Usage

### Installation

1. `pip install awesome-sso`

### Service

#### configure service settings

```python
from awesome_sso.service.settings import Settings

settings = Settings()
settings.init_app(
    symmetric_key='YOUR_SYMMETRIC_KEY',  # to encode and decode service token
    public_key='YOUR_PUBLIC_KEY',  # to decode the token signed by sso
    user_model=USER_MODEL,  # user orm needs to inherit AwesomeUser from `awesome_sso.user.schema`
    service_name='YOUR_SERVICE_NAME',  # for service discovery, to recognize service
    sso_domain='YOUR_SSO_DOMAIN',  # for service registration and sync user
)

```

#### initial service and mount to your application

```python
from awesome_sso.service import Service
from fastapi import FastAPI

app = FastAPI()
service = Service()
service.init_app(YOUR_FASTAPI_APP)
app.mount('/YOUR/PATH', YOUR_FASTAPI_APP)
```

then open the api doc, you will see the apis in `awesome_sso.service.user.route`

## Development

### Installing Poetry

1. create your own environment for poetry, and simply run: `pip install poetry`
2. alternatively, you can refer to [poetry's official page](https://github.com/python-poetry/poetry)
3. to be able to use `poe` directly, `pip install poethepoet`

### Contributing

1. project setup: `poetry install`
2. create your own branch to start developing new feature.
3. before creating pr, make sure you pass `poe lint` and `./run_test.sh`.
    - what happened inside `./run_test.sh` is that a minio server is setup for you temporarily, and teardown and unit
      test is finished.
    - notice that `poe test` would also work if you already have a minio up and running. You need the following env
      variable: `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_ADDRESS` upon running `poe test`.
4. for a list of available poe command, `poe`
5. after you submit a pr, you should check if pipeline is successful.

### Releasing

1. `poetry version [new_version]`
2. `git commit -m"Bump version"`
3. `git push origin develop`
4. [create new release](https://github.com/MoBagel/awesome-sso/releases/new) on github.
5. Create release off develop branch, auto generate notes, and review release note. 
6. Publish release

