from __future__ import annotations
from typing import *
if TYPE_CHECKING:
    pass

import os
import time
import requests
from enum import IntEnum

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from starlette import status
from pydantic import BaseModel
from devtools import debug

from monday_sdk.monday import MondayClient
from monday_sdk.graphql_loader import load_query
from monday_sdk.graphql_loader import load_mutation
from monday_sdk.authentication import authenticate

from dev_server import with_localtunnel
from uvicorn import run


monday = MondayClient(client_id=os.environ['CLIENT_ID'])


app = FastAPI()


WEBHOOK_ID = 228975808


InputFields = TypedDict(
    "InputFields",
    {
        "boardId": NotRequired[str],
        "itemId": NotRequired[str],
        "columnId": NotRequired[str],
        "columnValue": NotRequired[Any],
        "previousColumnValue": NotRequired[str],
        "columnType": NotRequired[Any],
        "itemMapping": NotRequired[Any],
    }
)

RequestPayload = TypedDict(
    "Payload",
    {
        "blockKind": str,
        "inputFieldValues": InputFields,
        "inputFields": InputFields,
        "recipeId": int,
        "integrationId": int,
    }
)


class OverviewStatus(IntEnum):
    CREWING = 0
    ACTIVE = 1
    COMPLETE = 2
    NOT_STARTED = 5


async def get_input_fields(request: Request) -> InputFields | None:
    if data := await request.json():
        if payload := data.get('payload'):
            return cast(InputFields, payload['inputFields'])


async def get_column_values(token: str, board_id: str, item_id: str):
    pass


async def parse_column_value(column_value: str) -> dict[str, Any]:
    return {}


@app.post("/monday/execute/on-button-pressed")
async def on_button_pressed(request: Request) -> int:
    # pull input fields from incoming request body
    if input_fields := await get_input_fields(request):
        variables = {
            'boardId': input_fields['boardId'],
            'itemId': input_fields['itemId'],
        }

        # authenticate and set token for the request
        monday.set_token(authenticate(request))

        # load the relevant GraphQL query
        query = load_query('get_column_value')

        # execute against the API and process the response
        response = monday.api(query, **variables)

        if response:
            debug(response.json())

    # Monday requires all recipes to return a 200 status code
    return status.HTTP_200_OK


@app.post("/monday/execute/on-status-changed")
async def on_status_changed(request: Request) -> int:
    if input_fields := await get_input_fields(request):
        column_value = input_fields["columnValue"]
        label_data = column_value["label"]
        index = label_data["index"]
        value = OverviewStatus(index)

        debug(value)

        if (value == OverviewStatus.CREWING):
            role_ids = [
                "DR",
                "PR",
                "PD",
                "DP",
                "1D",
                "2D",
                "SS",
                "1C",
                "2C",
                "KY",
                "GF",
                "BE",
                "SM",
                "BO",
            ]

            mutation = load_mutation("create_production_role")
            monday.set_token(authenticate(request))

            for role in role_ids:
                mutation_fields = {
                    "parent_item_id": 4456826335,
                    "item_name": role,
                }

                response = monday.api(mutation, **mutation_fields)

                if response:
                    debug(response.json())

    return status.HTTP_200_OK


class WebhookResponse(BaseModel):
    webhookId: int


@app.post("/monday/subscribe/test", status_code=status.HTTP_200_OK)
async def test_trigger_subscribe(request: Request) -> WebhookResponse:
    debug(request.headers)

    payload = {}

    if data := await request.json():
        payload = data['payload']
        debug(payload)

        # Now I'd want to put the webhook_id into Supabase for later execution.

    return WebhookResponse(webhookId=payload['subscriptionId'])


@app.post("/monday/unsubscribe/test", status_code=status.HTTP_200_OK)
async def test_trigger_unsubscribe(request: Request) -> int:
    debug(request.headers)
    debug(await request.json())
    return status.HTTP_200_OK


@app.post("/monday/execute/test", status_code=status.HTTP_200_OK)
async def test_trigger_execute(request: Request) -> int:
    response = requests.post(
        url="https://api-gw.monday.com/automations/apps-events/229005218",
        headers={
            "Authorization": os.environ['SIGNING_SECRET'],
        }
    )
    debug(response.status_code)
    debug(response.reason)

    return status.HTTP_200_OK


if __name__ == '__main__':
    load_dotenv()
    app_run = with_localtunnel(app, run, subdomain="monday-sdk")
    app_run(host="localhost", port=8000)
