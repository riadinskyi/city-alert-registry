from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pathlib import Path
from pydantic import constr
import logging

from .schemas import Match, HierarchyOption, CodeSearchResult
from .tool import CityRegistry

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "city_registry.json"

router = APIRouter(prefix="/codifier", tags=["codifier"])
cr = CityRegistry(DATA_PATH)

UA_CODE_PATTERN = r'^(UA)?\d{10,20}$'
UACode = constr(pattern=UA_CODE_PATTERN)



@router.get("/search/by-name", response_model=List[Match])
async def search(q: str = Query(..., description="Fragment of name to search")):
    """
    Search settlements by name fragment.
    """
    matches = await cr.search(q)
    return [Match(chain=chain, code=code, category=cat) for chain, code, cat in matches]

@router.get("/search/by-code/{ua_code}", response_model=CodeSearchResult)
async def search_with_code(ua_code: UACode):
    try:
        result = await cr.search_by_code(ua_code)

        if not result:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Точний збіг не знайдено",
                    "searched_code": ua_code,
                    "suggestion": "Перевірте правильність коду"
                }
            )

        chain, code, cat = result

        # Перевірка на пустий код
        if not code:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Код не знайдено",
                    "searched_code": ua_code,
                    "suggestion": "Недійсний код у базі даних"
                }
            )

        # Обережно формуємо ua_code, щоб уникнути дублювання префіксу
        normalized_code = (code or "").strip()
        ua_code_out = normalized_code if normalized_code.upper().startswith("UA") else f"UA{normalized_code}"
        return CodeSearchResult(
            code=normalized_code,
            ua_code=ua_code_out,
            chain=chain,
            category=cat,
            category_label=cr.CATEGORY_LABEL.get(cat, cat)
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка пошуку: {str(e)}")
@router.get("/location", response_model=List[HierarchyOption])
async def get_hierarchy(
    region: Optional[str] = Query(None, description="Region name"),
    district: Optional[str] = Query(None, description="District name"),
    community: Optional[str] = Query(None, description="Community name"),
):
    # 1) Getting region list
    if not region:
        items = await cr.list_level_with_cat("region")
        return [
            HierarchyOption(
                name=name,
                category=category,
                code=await cr.get_code(name),  # Adding region code
            )
            for name, category in items
        ]

    reg = region.strip()
    reg_code = await cr.get_code(reg)
    if not reg_code:
        raise HTTPException(status_code=404, detail="Region not found")

    # 2) Getting districts in region
    if not district:
        items = await cr.list_level_with_cat(
            "district", parent_key="First_Level", parent_code=reg_code
        )
        return [
            HierarchyOption(
                name=name,
                category=category,
                code=await cr.get_code(reg, name),  # Adding region code
            )
            for name, category in items
        ]

    dist = district.strip()
    dist_code = await cr.get_code(reg, dist)
    if not dist_code:
        raise HTTPException(status_code=404, detail="District not found")

    # 3) Getting communities in a district
    if not community:
        items = await cr.list_level_with_cat(
            "community", parent_key="Second_Level", parent_code=dist_code
        )
        return [
            HierarchyOption(
                name=name,
                category=category,
                code=await cr.get_code(reg, dist, name),  # Adding territory code
            )
            for name, category in items
        ]

    # 4) Getting territories in communit (without changing the code)
    comm = community.strip()
    comm_code = await cr.get_code(reg, dist, comm)
    if not comm_code:
        raise HTTPException(status_code=404, detail="Community not found")

    items = await cr.list_level_with_cat(
        "unit", parent_key="Third_Level", parent_code=comm_code
    )
    return [
        HierarchyOption(
            name=name, category=category, code=await cr.get_code(reg, dist, comm, name)
        )
        for name, category in items
    ]
