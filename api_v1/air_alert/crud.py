import asyncio
import time

from api_v1.air_alert.dependencies import call_for_air_alert
from api_v1.air_alert.schemas import TerritorialOrganization

active_alerts_cache = {}
last_update_time = 0
update_lock = asyncio.Lock()


async def get_active_alerts():
    """
    Зберігати та оновлючати поточний список активних тривог, кожні 20 секунд
    :return:
    """
    global active_alerts_cache, last_update_time, update_lock
    current_time = time.time()

    if last_update_time > 0 and (current_time - last_update_time) < 20:
        return active_alerts_cache

    async with update_lock:
        if last_update_time > 0 and (current_time - last_update_time) < 20:
            return active_alerts_cache

        try:
            new_data = await call_for_air_alert()
        except Exception as e:
            raise e

        active_alerts_cache = new_data
        last_update_time = current_time

    return active_alerts_cache


async def filter_by_location_type(location_type: TerritorialOrganization):
    """
    Функція яка отримує всі поточні тривоги та групує їх відповідно до парамерр location_type.
    :param location_type: TerritorialOrganization
    """
    alerts_data = await get_active_alerts()
    all_alerts = alerts_data["data"].alerts

    filtered_data = [
        {
            "location_title": alert.location_title,
            "alert_type": alert.alert_type,
            "location_oblast": alert.location_oblast,
            "location_raion": alert.location_raion,
            "started_at": alert.started_at,
        }
        for alert in all_alerts
        if alert.location_type == location_type.value
    ]

    return filtered_data
