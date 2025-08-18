import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from core.config import correct_token

TEST_API_TOKEN = correct_token

@pytest.mark.asyncio
async def test_get_cached_alerts():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/air-alert/cashed-alerts",
                                headers={"X-API-Token": TEST_API_TOKEN})
        data = response.json()
        assert response.status_code == 200
        assert data["data"]


@pytest.mark.asyncio
async def test_get_active_alerts():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/air-alert/codifier/",
                                headers={"X-API-Token": TEST_API_TOKEN})
        assert response.status_code == 200

