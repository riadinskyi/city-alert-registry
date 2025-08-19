import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from core.config import correct_token

TEST_API_TOKEN = correct_token


@pytest.mark.asyncio
async def test_get_cached_alerts():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/api/v1/air-alert/cached-alerts", headers={"X-API-Token": TEST_API_TOKEN}
        )
        data = response.json()
        assert response.status_code == 200
        assert data["data"]


@pytest.mark.asyncio
async def test_get_active_alerts():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/api/v1/air-alert/codifier/", headers={"X-API-Token": TEST_API_TOKEN}
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_location_search_by_name():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/api/v1/codifier"
    ) as ac:
        response = await ac.get(
            "/search/by-name",
            headers={"X-API-TOKEN": TEST_API_TOKEN},
            params={"q": "Татарбунари"},
        )
        correct_ua_code = "UA51040250010015619"
        data = response.json()
        assert response.status_code == 200
        assert data[0]["code"] == correct_ua_code


@pytest.mark.asyncio
async def test_location_by_search_ua_code():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testapi/api/v1/codifier"
    ) as ac:
        dict_of_locations = {
            "Київ": {"code": "UA80000000000093317", "category": "K"},
            "Запорізька": {"code": "UA23000000000064947", "category": "O"},
            "Ізмаїльський": {"code": "UA51080000000061776", "category": "P"},
            "Моршинська": {"code": "UA46100130000048262", "category": "H"},
            "Кривий Ріг": {"code": "UA12060170010065850", "category": "M"},
            "Новоіванівка": {"code": "UA12060170020084226", "category": "C"},
            "Гірницьке": {"code": "UA12060170050068450", "category": "X"},
        }
        for city_name, city_data in dict_of_locations.items():
            print("\n", city_name)
            print(city_data["code"])
            response = await ac.get(
                f"/search/by-code/{city_data['code']}",
                headers={"X-API-TOKEN": TEST_API_TOKEN},
            )
            data = response.json()
            print("data:", data)
            print("last_chain:", data["chain"][-1])
            assert response.status_code == 200
            assert data["chain"][-1] == city_name
            assert data["category"] == city_data["category"]


@pytest.mark.asyncio
async def test_location_hierarchy_search():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testapi/api/v1/codifier"
    ) as ac:

        region = await ac.get("/location", headers={"X-API-TOKEN": TEST_API_TOKEN})
        assert region.status_code == 200
        assert len(region.json()) == 27

        district = await ac.get(
            "/location",
            headers={"X-API-TOKEN": TEST_API_TOKEN},
            params={"region": "Одеська"},
        )
        assert district.status_code == 200
        assert len(district.json()) == 7

        community = await ac.get(
            "/location",
            headers={"X-API-TOKEN": TEST_API_TOKEN},
            params={"region": "Одеська", "district": "Одеський"},
        )
        assert community.status_code == 200
        assert len(community.json()) == 21

        city = await ac.get(
            "/location",
            headers={"X-API-TOKEN": TEST_API_TOKEN},
            params={
                "region": "Одеська",
                "district": "Одеський",
                "community": "Одеська",
            },
        )
        assert city.status_code == 200
        assert len(city.json()) == 1
