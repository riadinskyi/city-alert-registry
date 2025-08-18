from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path

from .schemas import Match, HierarchyOption
from .tool import CityRegistry

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "city_registry.json"

router = APIRouter(prefix="/codifier", tags=["codifier"])
cr = CityRegistry(DATA_PATH)



@router.get("/search", response_model=List[Match])
async def search(q: str = Query(..., description="Fragment of name to search")):
    """
    Search settlements by name fragment.
    """
    matches = await cr.search(q)
    return [Match(chain=chain, code=code, category=cat) for chain, code, cat in matches]


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
