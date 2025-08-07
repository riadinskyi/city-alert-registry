from fastapi import APIRouter

from api_v1.air_alert.dependencies import air_alert, get_active_alerts
from api_v1.air_alert.dependencies import filter_by_location_type

from api_v1.air_alert.schemas import TerritorialOrganization

router = APIRouter(prefix="/air-alert", tags=["Air Alert"])


@router.get("/get-active")
async def check_air_alert():
    return await air_alert()


@router.get("/by-group")
async def get_alerts_by_group(location_type: TerritorialOrganization):
    """
    Групування повітряних тривог за територіальною організацією.
    """
    return await filter_by_location_type(location_type=location_type)


@router.get("/cashed-alerts")
async def return_cached_alerts():
    return await get_active_alerts()
