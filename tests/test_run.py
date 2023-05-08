from __future__ import annotations
from beartype.typing import *
if TYPE_CHECKING:
    pass

from monday_sdk.client import Monday
from monday_sdk.action import Action
from monday_sdk.controller import Controller

from uvicorn import run
from dev_server import with_localtunnel


class TestAction(Action):

    def __call__(self) -> dict[str, str]:
        return {'msg': 'Hello world!'}


if __name__ == '__main__':
    monday = Monday()

    test_path_controller = Controller()
    test_path_controller.add_action('test_action', TestAction)
    monday.connect('test_path', test_path_controller)

    app_run = with_localtunnel(monday.start(), run, subdomain='monday-sdk')
    app_run(host='localhost', port=8000)
