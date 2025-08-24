from fastapi import APIRouter, Depends
from core.tools.location.xsls_to_json import download_xlsx_and_parse_to_json

router = APIRouter(prefix="/system", tags=["System"])


@router.post("/request_update_kodifier")
async def request_update_kodifier():
    """
    Надіслати та обробити запит про оновлення даних кодифікатора.
    """
    result = await download_xlsx_and_parse_to_json()
    return result
