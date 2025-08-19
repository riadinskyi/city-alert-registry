import pytest
import asyncio
from api_v1.air_alert.crud import get_active_alerts


@pytest.mark.asyncio
async def test_cached_air_alert_limit():
    print("\n\nFIRST ATTEMPT:")
    first_attempt = await get_active_alerts()
    await asyncio.sleep(1)
    print("SECOND ATTEMPT:")
    second_attempt = await get_active_alerts()
    assert first_attempt == second_attempt  # it must be the same because it's cached'
    await asyncio.sleep(20)
    print("THIRD ATTEMPT:")
    third_attempt = await get_active_alerts()
    assert first_attempt != third_attempt
    print(
        "CACHE LIMIT TEST: ",
        "First attempt: ",
        first_attempt["timestamp"],
        "Second attempt(cashed data): ",
        second_attempt["timestamp"],
        "Third attempt(new data):",
        third_attempt["timestamp"],
    )
