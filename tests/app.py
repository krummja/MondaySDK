from __future__ import annotations
from beartype.typing import *
if TYPE_CHECKING:
    pass

from fastapi import FastAPI


app = FastAPI()


@app.get('/')
def main() -> str:
    return "OK"
