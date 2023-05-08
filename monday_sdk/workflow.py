from __future__ import annotations
from beartype.typing import *
if TYPE_CHECKING:
    pass

from pydantic import BaseModel

from fastapi import Request
from monday_sdk.utils import to_camel_case
from monday_sdk.authentication import authenticate


class Fields(BaseModel):

    class Config:
        alias_generator = to_camel_case


class NoOutput(Fields):
    pass


IN = TypeVar("IN", bound=Fields)
OUT = TypeVar("OUT", bound=Fields)


class WorkflowBlock(Generic[IN, OUT]):
    pass


class Trigger(WorkflowBlock[IN, OUT]):
    """
    A Trigger is a workflow block that responds to events outside of monday.com
    which can be used to execute one or more Action blocks.
    """
    pass


class Action(WorkflowBlock[IN, OUT]):
    """
    An Action is a workflow block that will perform some operation after a
    Trigger is invoked. An action can change monday.com data or initiate
    changes on outside platforms.
    """

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    async def execute(self, input_fields: IN) -> OUT:
        raise NotImplementedError(
            "This method must be implemented by subclasses."
        )

    async def _execute(self, request: Request, input_fields: IN) -> OUT:
        # TODO authenticate the request before doing anything
        # TODO grab the input fields from the request
        return await self.execute(input_fields)
