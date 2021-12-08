from datetime import datetime, timedelta
from typing import Optional

import jwt

from awesome_sso.service.settings import Settings
from awesome_sso.util.encode import JSONEncoder

# to get a string like this run:
# openssl rand -hex 32
ASYMMETRIC_ALGORITHM = "RS256"
SYMMETRIC_ALGORITHM = "HS256"
PUBLIC_KEY = open("tests/key_pairs/test.key.pub").read()
PRIVATE_KEY = open("tests/key_pairs/test.key").read()


# 生成token
def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=15)
    to_encode.update({"exp": datetime.timestamp(expire)})
    encoded_jwt = jwt.encode(
        to_encode, Settings.private_key, algorithm=ASYMMETRIC_ALGORITHM, json_encoder=JSONEncoder
    )
    return encoded_jwt


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=15)
    to_encode.update({"exp": datetime.timestamp(expire)})
    encoded_jwt = jwt.encode(to_encode, Settings.symmetric_key, algorithm=SYMMETRIC_ALGORITHM)
    return encoded_jwt
