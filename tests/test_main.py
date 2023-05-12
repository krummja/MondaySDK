from __future__ import annotations
from beartype.typing import *
if TYPE_CHECKING:
    from fastapi import Request
    from fastapi import Response

from pydantic import BaseModel
from fastapi import FastAPI
from starlette import status

from uvicorn import run
from dev_server import with_localtunnel


class RootResponse(BaseModel):
    status: int
    message: str


app = FastAPI()


@app.get("/main")
async def read_main() -> RootResponse:
    return RootResponse(
        status=status.HTTP_200_OK,
        message="Main API OK",
    )


test_api = FastAPI()


@test_api.get("/test")
async def read_test_api() -> str:
    return "Test API OK"


app.mount("/api", test_api)


# if __name__ == '__main__':
#     app_run = with_localtunnel(app, run, subdomain="monday-sdk")
#     app_run(host="localhost", port=8000)
