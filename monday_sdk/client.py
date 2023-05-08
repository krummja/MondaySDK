from __future__ import annotations
from beartype.typing import *
if TYPE_CHECKING:
    from monday_sdk.controller import Controller
    from monday_sdk.action import Action

from enum import StrEnum
from dotenv import load_dotenv
from functools import wraps

from fastapi import FastAPI
from fastapi import APIRouter
from fastapi import Request
from fastapi import Response
from fastapi.routing import APIRoute
from pydantic import BaseModel

from monday_sdk.authentication import authenticate
from monday_sdk.authentication import AuthResponse


load_dotenv()


class Monday:

    def __init__(self) -> None:
        self._client = FastAPI()
        self._controllers: dict[str, Controller] = {}

    def connect(
        self,
        identifier: str,
        controller: Controller,
        root_path: str = '',
    ) -> None:
        """Attach a controller under a specific endpoint identifier."""
        self._controllers[identifier] = controller
        controller.bind(self)

        _path = root_path if root_path else ''

        for action in controller:
            _path += f'/{identifier}/{action}'
            self._client.add_api_route(_path, controller[action])

    def start(self):
        return self._client
