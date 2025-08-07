from alerts_in_ua import AsyncClient as AsyncAlertsClient

import datetime


async def call_for_air_alert():
    from core.config import air_alert_api_token

    alerts_client = AsyncAlertsClient(token=air_alert_api_token)
    active_alerts = await alerts_client.get_active_alerts()
    print("ALERT API REQUEST: ", datetime.datetime.now())
    return {"data": active_alerts, "timestamp": datetime.datetime.now()}
