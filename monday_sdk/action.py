from __future__ import annotations
from beartype.typing import *
if TYPE_CHECKING:
    from monday_sdk.controller import Controller


class Action:

    def __init__(self, controller: Controller) -> None:
        """Initialize an action with an endpoint controller."""
        self._controller = controller

    def __call__(self) -> Any:
        """Override this method to implement your own action."""
        raise NotImplementedError("Actions require a Callable implementation.")
