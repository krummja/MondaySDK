from __future__ import annotations
from typing import TYPE_CHECKING, cast, Optional
if TYPE_CHECKING:
    from fastapi import Request

import os
import jwt
import json
import pendulum as pdl

from typing_extensions import TypedDict

from starlette import status
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel


WebToken = TypedDict(
    "WebToken",
    {
        "accountId": int,
        "userId": int,
        "aud": str,
        "exp": int,
        "iat": int,
        "shortLivedToken": str,
    }
)


class AuthResponse(BaseModel):
    """
    Response model for the authentication endpoint.

    Returns a status code and a JSON web token if the request is valid.
    If the request is invalid, returns a status code and an error message
    accessible via the `data` attribute.
    """
    status: int
    data: Optional[str] = None
    webtoken: Optional[WebToken] = None


def _decode(authorization: str, secret: str = "") -> WebToken:
    decoded = jwt.decode(
        authorization,
        os.environ.get("SIGNING_SECRET", secret),
        algorithms=["HS256"],
        options={
            "verify_aud": False,
        },
    )

    return cast(WebToken, decoded)


def authenticate(req: Request) -> AuthResponse:
    """
    Process an inbound request and authenticate against the monday.com API.

    Currently, the `req` parameter must be a `starlette.requests.Request`
    instance. Support for request types from other libraries---or a more
    generalized request type---will be added in the future.

    If the request contains a valid token, the token will be decoded and
    returned in the response with HTTP status 200. If the token is invalid,
    the response will contain an error message with HTTP status 401.
    """
    try:
        authorization = req.headers.get(
            "Authorization",
            req.query_params.get("token", "") if req.query_params else "",
        )

        decoded = _decode(cast(str, authorization))

        if pdl.now() >= pdl.from_timestamp(decoded["exp"]):
            raise InvalidTokenError("Token has expired")

        return AuthResponse(
            status=status.HTTP_200_OK,
            webtoken={
                "accountId": decoded["accountId"],
                "userId": decoded["userId"],
                "aud": decoded["aud"],
                "exp": decoded["exp"],
                "iat": decoded["iat"],
                "shortLivedToken": decoded["shortLivedToken"],
            }
        )

    except InvalidTokenError as err:
        return AuthResponse(
            status=status.HTTP_401_UNAUTHORIZED,
            data=json.dumps(err.args),
        )
