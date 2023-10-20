from __future__ import annotations
from typing import *
if TYPE_CHECKING:
    pass

# Standard
import os
import json
from enum import IntEnum
from pathlib import Path
import pendulum as pdl

# Dependencies
from devtools import debug
from dotenv import load_dotenv
from dotenv import set_key
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from pydantic import BaseModel
from starlette import status
from uvicorn import run

# Local
from dev_server import with_localtunnel
from monday_sdk.monday import MondayClient
from monday_sdk.graphql_loader import load_query
from monday_sdk.graphql_loader import load_mutation
from monday_sdk.authentication import authenticate


def init_env() -> None:
    """
    Initialize the local environment.

    Override the default values for the graphql source file paths and load the
    environment variables.
    """
    query_path = str(Path(__file__).parent.parent / "graphql" / "queries")
    mutation_path = str(Path(__file__).parent.parent / "graphql" / "mutations")

    set_key(".env", "QUERY_PATH", query_path)
    set_key(".env", "MUTATION_PATH", mutation_path)

    load_dotenv()


monday = MondayClient(client_id=os.environ['CLIENT_ID'])


app = FastAPI()


T = TypeVar("T", bound=TypedDict)


FromDateValue = TypedDict(
    "FromDateValue",
    {
        "date": str,
        "icon": NotRequired[str],
        "time": NotRequired[str],
        "changed_at": NotRequired[str],
    }
)


InputFields = TypedDict(
    "InputFields",
    {
        "boardId": str,
        "itemId": str,
        "columnId": str,
        "toDateId": str,
        "fromDateValue": FromDateValue,
    }
)


START_DATE = "date4"
END_DATE = "date1"


async def get_input_fields(request: Request, field_model: type[T]) -> T | None:
    if data := await request.json():
        if payload := data.get('payload'):
            return cast(field_model, payload['inputFields'])


@app.post("/api/execute/custom-action", status_code=200)
async def on_status_changed(request: Request) -> int:

    if input_fields := await get_input_fields(request, InputFields):
        debug(input_fields)
        monday.set_token(authenticate(request))

    return status.HTTP_200_OK


@app.post("/api/execute/copy-and-push", status_code=200)
async def on_start_date_changed(request: Request) -> int:
    if input_fields := await get_input_fields(request, InputFields):
        monday.set_token(authenticate(request))

        date = input_fields["fromDateValue"]["date"]
        dt = pdl.from_format(date, "YYYY-MM-DD")
        dt = dt.add(days=30)
        to_date = dt.to_date_string()

        mutation = load_mutation("change_column_value")
        mutation_fields: dict[str, Any] = {
            "board_id": input_fields["boardId"],
            "item_id": input_fields["itemId"],
            "column_id": input_fields["toDateId"],
            "value": json.dumps({"date": to_date}),
        }

        response = monday.api(mutation, None, **mutation_fields)
        if response:
            debug(response.status_code)
            debug(response.json())

    return status.HTTP_200_OK


if __name__ == "__main__":
    init_env()
    app_run = with_localtunnel(app, run, subdomain="solution-demos")
    app_run(host="localhost", port=8000)
