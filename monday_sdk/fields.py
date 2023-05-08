from __future__ import annotations
from beartype.typing import *
if TYPE_CHECKING:
    pass

from pydantic import BaseModel

from monday_sdk.utils import to_camel_case


class Field(BaseModel):
    name: str
    key: str


class TextField(Field):
    """
    Field type representing simple text.
    Can be restricted to numbers only.
    """
    value: str
    only_numbers: bool = False


class ListField(Field):
    """Field type that generates an array of options for selection."""
    options: dict[str, Any] | None = None
    options_url: str | None = None
    dependencies: list[Field] | None = None


class DynamicMapping(Field):
    """Field type used for mapping fields to or from another platform."""
    field_definitions_url: str
    dependencies: list[Field] | None = None
