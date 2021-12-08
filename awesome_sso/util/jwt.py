from datetime import datetime, timedelta
from typing import Optional

import jwt

from awesome_sso.util.encode import JSONEncoder

# to get a string like this run:
# openssl rand -hex 32
ASYMMETRIC_ALGORITHM = "RS256"
SYMMETRIC_ALGORITHM = "HS256"


# 生成token
def create_token(
    data: dict, encode_key, algorithm, expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=15)
    to_encode.update({"exp": datetime.timestamp(expire)})
    encoded_jwt = jwt.encode(
        to_encode,
        encode_key,
        algorithm=algorithm,
        json_encoder=JSONEncoder,
    )
    return encoded_jwt
