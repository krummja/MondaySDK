from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict, TypeAlias, Any, Literal
from types import TracebackType

if TYPE_CHECKING:
    from requests import Request
    from requests import Response
    from requests import Session

import os

from dotenv import load_dotenv
from requests.auth import AuthBase
from requests.adapters import HTTPAdapter
from requests_toolbelt import sessions

from monday_sdk.authentication import AuthResponse


load_dotenv()


HTTP_PROTOCOL = os.environ.get("HTTP_PROTOCOL", "https")
MONDAY_DOMAIN = os.environ.get("MONDAY_DOMAIN", "monday.com")
MONDAY_API_VERSION = os.environ.get("MONDAY_API_VERSION", "2")
MONDAY_API_URL = f"{HTTP_PROTOCOL}://api.{MONDAY_DOMAIN}/v{MONDAY_API_VERSION}"


class MondayAuth(AuthBase):

    def __init__(self, access_token: str) -> None:
        self.token = access_token

    def __call__(self, request: Request) -> Request:
        request.headers["Content-Type"] = "application/json"
        request.headers["Authorization"] = self.token
        return request


class MondayContext:

    def __init__(self, token: str) -> None:
        self._base = MONDAY_API_URL
        self._base_ctx = sessions.BaseUrlSession(base_url=self._base)
        self._base_ctx.auth = MondayAuth(token)
        self._base_ctx.mount(prefix=self._base, adapter=HTTPAdapter())

    def __enter__(self) -> Session:
        return self._base_ctx

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        self._base_ctx.close()


class APIParams(TypedDict):
    query: str
    variables: dict[str, Any]


QueryVars: TypeAlias = dict[str, Any]


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

    def __init__(self, *, client_id: str) -> None:
        self.client_id = client_id
        self._token: str = ""

    def set_token(self, auth: AuthResponse) -> None:
        """Set the cached API token from an authenticated AuthResponse."""
        if credential := auth.webtoken:
            self._token = credential["shortLivedToken"]

    def api(
        self,
        query: str,
        options: APIOptions | None = None,
        **variables: QueryVars,
    ) -> Response | None:
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
    ) -> Response | None:
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
