from fastapi import APIRouter

from api_v1.air_alert.crud import get_active_alerts, filter_by_location_type
from api_v1.air_alert.dependencies import _resolve_code_for_alert_obj
from api_v1.air_alert.schemas import TerritorialOrganization
from api_v1.location.dependecies import credentials_return

router = APIRouter(prefix="/air-alert", tags=["Air Alert"])


@router.get("/cached-alerts")
async def return_cached_alerts():
    return await get_active_alerts()


@router.get("/filter-by-location-type/{location_type}")
async def get_alerts_filterer(location_type: TerritorialOrganization):
    """
    Групування повітряних тривог за територіальною організацією.
    """
    return await filter_by_location_type(location_type=location_type)


@router.get("/codifier/")
async def return_alerts_codifier():
    """
    Return all active alerts enriched with codifier code of the territory.
    Attempts robust resolution so every active alert has a UA code if possible.
    """
    credit_location_data = await credentials_return()
    alerts_data = await get_active_alerts()
    all_alerts = alerts_data["data"].alerts

    enriched: list[dict] = []
    for alert in all_alerts:
        ua_code = await _resolve_code_for_alert_obj(alert)
        enriched.append(
            {
                "location_title": getattr(alert, "location_title", None),
                "alert_type": getattr(alert, "alert_type", None),
                "location_oblast": getattr(alert, "location_oblast", None),
                "location_raion": getattr(alert, "location_raion", None),
                "started_at": getattr(alert, "started_at", None),
                "location_type": getattr(alert, "location_type", None),
                "ua_code": ua_code,
            }
        )

    return {"credit_for_location_data": credit_location_data, "data": enriched}
