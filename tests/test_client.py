import pytest
from httpx import AsyncClient

from monday_sdk.client import Monday


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(app=Monday().start(), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
