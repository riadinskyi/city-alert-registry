from fastapi import APIRouter
from .location.views import router as location_router
from .air_alert.views import router as air_alert_router
from .system.view import router as system_router

router = APIRouter(prefix="/api/v1")

router.include_router(location_router)
router.include_router(air_alert_router)
router.include_router(system_router)
