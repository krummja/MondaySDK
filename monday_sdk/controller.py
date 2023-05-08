from __future__ import annotations
from beartype.typing import *
if TYPE_CHECKING:
    from monday_sdk.action import Action

from monday_sdk.client import Monday


class Controller:

    def __init__(self) -> None:
        self._client: Monday | None = None
        self._actions: dict[str, Callable[..., Any]] = {}

    def bind(self, client: Monday) -> None:
        self._client = client

    def add_action(self, action_name: str, action: type[Action]) -> None:
        """Register an Action subclass with this Controller."""
        self._actions[action_name] = action(self)

    def __getitem__(self, action_name: str) -> Callable[..., Any]:
        return self._actions[action_name]

    def __iter__(self) -> Iterator[str]:
        return iter(self._actions)
