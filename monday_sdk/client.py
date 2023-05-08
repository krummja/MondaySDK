from __future__ import annotations
from beartype.typing import *
if TYPE_CHECKING:
    from monday_sdk.controller import Controller

from dotenv import load_dotenv
from fastapi import FastAPI
from functools import wraps

from monday_sdk.authentication import authenticate
from monday_sdk.authentication import AuthResponse
from starlette.routing import Route


load_dotenv()


Method = Literal['POST'] | Literal['GET'] | Literal['PUT'] | Literal['DELETE']


class Monday:

    def __init__(self) -> None:
        self.client = FastAPI()
        self._controllers: dict[str, Controller] = {}

    def call_deferred(self, endpoint: str):
        path = endpoint.split('/')
        controller = self._controllers[path[2]]
        return controller.call_deferred(path[3])

    def connect(
        self,
        identifier: str,
        controller: Controller,
        methods: list[Method] | None = None,
    ) -> None:
        if not methods:
            methods = ['POST']

        self._controllers[identifier] = controller
        controller.bind_client(self)

        for endpoint in controller:
            _endpoint = f'/api/{identifier}/{endpoint}'
            self.client.add_api_route(
                path=_endpoint,
                endpoint=self.call_deferred(_endpoint),
                methods=methods,
            )

    def start(self) -> FastAPI:
        return self.client


if __name__ == '__main__':
    monday = Monday()
