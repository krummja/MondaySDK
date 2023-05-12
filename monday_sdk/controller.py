from __future__ import annotations
from beartype.typing import *
if TYPE_CHECKING:
    from fastapi import Request
    from monday_sdk.authentication import AuthResponse

from functools import wraps


ServiceResult = TypedDict(
    "ServiceResult",
    {
        "success": bool,
        "data": NotRequired[dict[str, Any]],
    }
)


QueryVariables = TypedDict(
    "QueryVariables",
    {
        "userId": NotRequired[str],
        "boardId": NotRequired[str],
        "itemId": NotRequired[str],
        "columnId": NotRequired[str],
    }
)


ServiceParams = TypedDict(
    "ServiceParams",
    {
        "request": Request,
        "token": str,
    }
)


class Service(Protocol):

    async def __call__(self, params: ServiceParams) -> ServiceResult:
        ...


class ServiceRepository:

    def __init__(self, controller: Controller) -> None:
        self._controller = controller
        self._services: dict[str, Service] = {}

    def __getitem__(self, identifier: str) -> Service:
        return self._services[identifier]

    def __setitem__(self, identifier: str, service: Service) -> None:
        self._services[identifier] = service


class Controller:

    def __init__(self) -> None:
        self._cached_token: str | None = None
        self._services = ServiceRepository(self)
        self._last_result: ServiceResult = {
            "success": False,
            "data": {},
        }

    @property
    def last_result(self) -> ServiceResult:
        return self._last_result

    async def execute(
        self,
        req: Request,
        auth: AuthResponse,
        action: str,
    ) -> None:
        self._set_authentication(auth)

        if self._cached_token is None:
            return

        if func := getattr(self, f"execute_{action}"):
            params: ServiceParams = {
                'request': req,
                'token': self._cached_token,
            }

            service: Service = func
            self._last_result = await service(params)

        self._expire()

    def _expire(self) -> None:
        self._cached_token = None

    def _set_authentication(self, authorization: AuthResponse) -> None:
        if webtoken := authorization.webtoken:
            self._cached_token = webtoken.get("shortLivedToken")
