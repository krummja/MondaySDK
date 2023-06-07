from __future__ import annotations
from beartype.typing import *
if TYPE_CHECKING:
    from fastapi import Request

import os
import jwt
import json
import pendulum as pdl

from starlette import status
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel


WebToken = TypedDict(
    'WebToken',
    {
        'accountId': int,
        'userId': int,
        'aud': str,
        'exp': int,
        'iat': int,
        'shortLivedToken': str,
    }
)


class AuthResponse(BaseModel):
    status: int
    data: str | None = None
    webtoken: WebToken | None = None


def decode(authorization: str, secret: str = '') -> WebToken:
    decoded = jwt.decode(
        authorization,
        os.environ.get('SIGNING_SECRET', secret),
        algorithms=['HS256'],
        options={
            'verify_aud': False,
        },
    )
    return cast(WebToken, decoded)


def authenticate(req: Request) -> AuthResponse:
    """
    Process an inbound request and authenticate against the monday.com API.

    If the request contains a valid token, the token will be decoded and
    returned in the response with HTTP status 200. If the token is invalid,
    the response will contain an error message with HTTP status 401.
    """
    try:

        authorization = req.headers.get(
            'Authorization',
            req.query_params.get('token', '') if req.query_params else '',
        )

        decoded = decode(cast(str, authorization))

        if pdl.now() >= pdl.from_timestamp(decoded['exp']):
            raise InvalidTokenError("Token has expired")

        return AuthResponse(
            status=status.HTTP_200_OK,
            webtoken={
                'accountId': decoded['accountId'],
                'userId': decoded['userId'],
                'aud': decoded['aud'],
                'exp': decoded['exp'],
                'iat': decoded['iat'],
                'shortLivedToken': decoded['shortLivedToken'],
            }
        )

    except InvalidTokenError as err:
        return AuthResponse(
            status=status.HTTP_401_UNAUTHORIZED,
            data=json.dumps(err.args),
        )
