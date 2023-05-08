from __future__ import annotations
from beartype.typing import *
if TYPE_CHECKING:
    pass

import pytest
from devtools import debug
from httpx import AsyncClient

from pydantic import BaseModel
from pydantic import Field
from fastapi import FastAPI
from fastapi import Request

from monday_sdk.client import Monday
from monday_sdk.controller import Controller
from monday_sdk.service import QueryService
from monday_sdk.service import MutationService
from monday_sdk.utils import to_camel_case

from monday_sdk.workflow import Action
from monday_sdk.workflow import Fields
from monday_sdk.workflow import NoOutput

from uvicorn import run
from dev_server import with_localtunnel


class InputFields(Fields):
    board_id: int
    item_id: str
    column_id: str


class UnassignUser(Action[InputFields, InputFields]):

    async def execute(self, input_fields: InputFields) -> str:
        return "Test"


class UserController(Controller):
    pass


def test_client_setup():
    monday = Monday()
    assert monday.client is not None
    assert isinstance(monday.client, FastAPI)


def test_controller_setup():
    monday = Monday()

    user_controller = UserController()
    user_controller.add_action('unassign', UnassignUser)
    monday.connect('users', user_controller)

    assert 'unassign' in user_controller
    assert isinstance(user_controller['unassign'], UnassignUser)
    assert user_controller['unassign'].endpoint == 'unassign'
    assert user_controller._client is not None
    assert user_controller._client == monday


if __name__ == '__main__':
    monday = Monday()
    user_controller = UserController()
    user_controller.add_action('unassign', UnassignUser)
    monday.connect('users', user_controller)

    app_run = with_localtunnel(monday.start(), run, subdomain='monday-sdk')
    app_run(host='localhost', port=8000)
