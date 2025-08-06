from alerts_in_ua import AsyncClient as AsyncAlertsClient

from api_v1.air_alert.schemas import TerritorialOrganization

import datetime


async def air_alert():
    from core.config import air_alert_api_token

    alerts_client = AsyncAlertsClient(token=air_alert_api_token)
    active_alerts = await alerts_client.get_active_alerts()
    print("ALERT API REQUEST: ", datetime.datetime.now())
    return active_alerts


async def filter_by_location_type(location_type: TerritorialOrganization):
    """
    Функція яка отримує всі поточні тривоги та групує їх відповідно до парамерр location_type.
    :param location_type: TerritorialOrganization
    """
    alerts_data = await air_alert()
    all_alerts = alerts_data.alerts

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
