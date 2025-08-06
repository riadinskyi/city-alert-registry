from fastapi import APIRouter
from .location.views import router as location_router

router = APIRouter(prefix="/api/v1")

router.include_router(location_router)

