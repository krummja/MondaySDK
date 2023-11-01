from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict, Any, Literal, Optional
from types import TracebackType

if TYPE_CHECKING:
    from requests import Request
    from requests import Response
    from requests import Session

import os

from devtools import debug
from dotenv import load_dotenv
from requests.auth import AuthBase
from requests.adapters import HTTPAdapter
from requests_toolbelt import sessions

from monday_sdk.authentication import AuthResponse


load_dotenv()


HTTP_PROTOCOL = os.environ.get("HTTP_PROTOCOL", "https")
MONDAY_DOMAIN = os.environ.get("MONDAY_DOMAIN", "monday.com")
MONDAY_API_VERSION = os.environ.get("MONDAY_API_VERSION", "2023-10")
MONDAY_API_URL = f"{HTTP_PROTOCOL}://api.{MONDAY_DOMAIN}/v2"


class MondayAuth(AuthBase):

    def __init__(self, *, token: str) -> None:
        self.token = token

    def __call__(self, request: Request) -> Request:
        request.headers["Content-Type"] = "application/json"
        request.headers["Authorization"] = self.token
        request.headers["API-Version"] = MONDAY_API_VERSION
        return request


class MondayContext:

    def __init__(self, token: str, suppress: bool = False) -> None:
        self._suppress = suppress
        self._base = MONDAY_API_URL
        self._base_ctx = sessions.BaseUrlSession(base_url=self._base)
        self._base_ctx.auth = MondayAuth(token=token)
        self._base_ctx.mount(prefix=self._base, adapter=HTTPAdapter())

    def __enter__(self) -> Session:
        return self._base_ctx

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType,
    ) -> bool:
        self._base_ctx.close()

        if exc_type is not None:
            info = (exc_type, exc_value, exc_tb)
            debug(info)

            return self._suppress
        return False


class APIParams(TypedDict):
    query: str
    variables: dict[str, Any]


class APIOptions(TypedDict):
    method: Literal["GET", "POST", "PUT", "DELETE"]
    path: str
    url: str


API_DEFAULTS: APIOptions = {
    "method": "POST",
    "path": "",
    "url": MONDAY_API_URL,
}


class MondayClient:
    """Client for making requests against the monday.com API."""

    @property
    def client_id(self) -> str:
        return self._client_id

    def __init__(self, *, client_id: str = "", token: str = "") -> None:
        self._client_id = client_id
        self._token = token

    def set_token(self, auth: AuthResponse) -> None:
        """Set the cached API token from an authenticated AuthResponse."""
        if credential := auth.webtoken:
            self._token = credential["shortLivedToken"]

    def api(
        self,
        query: str,
        options: Optional[APIOptions] = None,
        **variables: dict[str, Any],
    ) -> Optional[Response]:
        """
        Execute a query or mutation against the monday.com API.

        Pass a query (or mutation) as a string and any variables as keyword
        arguments. The query and variables will be passed to the API as a JSON
        object.

        A dictionary of options can be passed to override the default API
        settings, specifying the HTTP method, path, and URL.
        """
        params: APIParams = {
            "query"       : query,
            "variables"   : variables,
        }

        if self._token:
            result = self._execute(
                params,
                self._token,
                options or API_DEFAULTS,
            )

            return result

    def _execute(
        self,
        data: APIParams,
        token: str,
        options: APIOptions,
    ) -> Optional[Response]:
        url = options.get("url", MONDAY_API_URL)
        path = options.get("path", "")
        method = options.get("method", "POST")
        full_url = url + path

        with MondayContext(token) as ctx:
            response: Response = ctx.request(
                url=full_url,
                method=method,
                json=data,
            )

            return response
