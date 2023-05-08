from __future__ import annotations
from beartype.typing import *
from typing_extensions import NotRequired
if TYPE_CHECKING:
    from monday_sdk.client import Monday
    from monday_sdk.authentication import AuthResponse
    from monday_sdk.workflow import Action
    from monday_sdk.workflow import Fields

from devtools import debug
from pydantic import BaseModel

from fastapi import Request
from monday_sdk.authentication import authenticate


class Controller:

    def __init__(self) -> None:
        self._client: Monday | None = None
        self._cached_token: str | None = None
        self._actions: dict[str, Action] = {}

    def bind_client(self, client: Monday) -> None:
        self._client = client

    def call_deferred(self, action_name: str) -> Callable[[Request, Fields], Any]:
        action = self._actions[action_name]
        return action._execute

    def add_action(self, action_name: str, action: type[Action]) -> None:
        self._actions[action_name] = action(action_name)

    def __getitem__(self, action_name: str) -> Action:
        return self._actions[action_name]

    def __iter__(self) -> Iterator[str]:
        return iter(self._actions)


# class Controller:

#     def __init__(self, client: Monday) -> None:
#         self._client = client
#         self._cached_token: str | None = None

#     async def execute(
#         self,
#         request: Request,
#         authorization: AuthResponse,
#         method: str,
#     ) -> ExecResponse:
#         self._check_webtoken(authorization)

#         if self._cached_token is None:
#             return ExecResponse(
#                 action_identifier='',
#                 succeeded=False,
#             )

#         # Check if we have a properly named method with the given identifier.
#         # If so, get a new ServiceParams instance with the passed monday.com
#         # request as well as the current cached token and execute it.
#         if func := getattr(self, f'execute_{method}'):
#             params = ServiceParams(
#                 request=request,
#                 token=self._cached_token,
#             )

#             # The result of the monday action will return an `ExecResponse`
#             # instance, simply informing us of what was done and whether the
#             # operation executed successfully.
#             result = await self._execute(func, params)
#             return ExecResponse(
#                 action_identifier=method,
#                 succeeded=result['succeeded'],
#             )

#         self._expire()
#         return ExecResponse(
#             action_identifier=method,
#             succeeded=True,
#         )

#     def _expire(self) -> None:
#         self._cached_token = None

#     def _check_webtoken(self, authorization: AuthResponse) -> None:
#         if webtoken := authorization.webtoken:
#             self._cached_token = webtoken.get('shortLivedToken')

#     async def _execute(
#         self,
#         func: Service,
#         params: ServiceParams,
#         **kwargs,
#     ) -> ServiceResult:
#         auth_response: AuthResponse = authenticate(params.request)
#         if result := func(params.token, **kwargs):
#             return result
#         return {
#             'succeeded': False,
#         }
