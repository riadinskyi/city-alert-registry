from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from pathlib import Path

from .tool import CityRegistry

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "city_regestry.json"

router = APIRouter(prefix="/codifier", tags=["codifier"])
cr = CityRegistry(DATA_PATH)


class Option(BaseModel):
    name: str
    category: str


class CodeResponse(BaseModel):
    code: Optional[str]


class Match(BaseModel):
    chain: List[str]
    code: str
    category: str


class UnitOption(BaseModel):
    name: str
    category: str
    code: str


class HierarchyOption(BaseModel):
    name: str
    category: str
    code: Optional[str] = None


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
    """
    - no params: return all regions (and special-status cities)
    - region only: return all districts in that region
    - region + district: return all communities in that district
    - region + district + community: return all units in that community (with codes)
    """
    # 1) regions
    if not region:
        items = await cr.list_level_with_cat("region")
        return [HierarchyOption(name=n, category=c) for n, c in items]

    reg = region.strip()
    reg_code = await cr.get_code(reg)
    if not reg_code:
        raise HTTPException(status_code=404, detail="Region not found")

    # 2) districts
    if not district:
        items = await cr.list_level_with_cat(
            "district", parent_key="First_Level", parent_code=reg_code
        )
        return [HierarchyOption(name=n, category=c) for n, c in items]

    dist = district.strip()
    dist_code = await cr.get_code(reg, dist)
    if not dist_code:
        raise HTTPException(status_code=404, detail="District not found")

    # 3) communities
    if not community:
        items = await cr.list_level_with_cat(
            "community", parent_key="Second_Level", parent_code=dist_code
        )
        return [HierarchyOption(name=n, category=c) for n, c in items]

    # 4) units
    comm = community.strip()
    comm_code = await cr.get_code(reg, dist, comm)
    if not comm_code:
        raise HTTPException(status_code=404, detail="Community not found")

    items = await cr.list_level_with_cat(
        "unit", parent_key="Third_Level", parent_code=comm_code
    )
    result: List[HierarchyOption] = []
    for name, cat in items:
        code = await cr.get_code(reg, dist, comm, name)
        result.append(HierarchyOption(name=name, category=cat, code=code or None))
    return result