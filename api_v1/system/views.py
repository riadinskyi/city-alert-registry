from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["system"])


@router.post("update-codifier")
async def updatecodifier():
    pass
