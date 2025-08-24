from alerts_in_ua import AsyncClient as AsyncAlertsClient
from pathlib import Path
from api_v1.air_alert.schemas import TerritorialOrganization
from core.tools.location.tool import CityRegistry
from typing import Optional
import re
import datetime

_DATA_PATH = (
    Path(__file__).parents[2] / "core" / "tools" / "location" / "kodifikator.json"
)

_cr_instance = None


def get_city_registry():
    global _cr_instance
    if _cr_instance is None:
        _cr_instance = CityRegistry(str(_DATA_PATH))
    return _cr_instance


def _norm_str(x: Optional[str]) -> Optional[str]:
    if isinstance(x, str):
        s = x.strip()
        return s if s else None
    return None


def _clean_unit_title(title: str) -> str:
    """
    Remove common prefixes in locality names: "м.", "смт", "с." etc.
    """
    s = title.strip()
    s = re.sub(r"^(м\.|смт|с\.|селище|місто)\s+", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r"\s*\((місто|селище|смт|с\.)\)\s*$", "", s, flags=re.IGNORECASE).strip()
    return s


def _clean_hromada_title(title: str) -> str:
    """
    Remove suffix "територіальна громада" in hromada titles.
    """
    s = title.strip()
    s = re.sub(r"\s*територіальна громада\s*$", "", s, flags=re.IGNORECASE).strip()
    return s


def _clean_region_name(name: str) -> str:
    """
    Normalize region (oblast) name: remove suffixes like "область" or "обл.", collapse spaces.
    """
    s = name.strip()
    s = re.sub(r"\s*(область|обl\.)\s*$", "", s, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", s).strip()


def _clean_raion_name(name: str) -> str:
    """
    Normalize district (raion) name: remove suffix "район", collapse spaces.
    """
    s = name.strip()
    s = re.sub(r"\s*район\s*$", "", s, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", s).strip()


async def _resolve_code_for_alert_obj(alert) -> Optional[str]:
    """
    Resolve UA code for an active alert object.
    Try hierarchical resolution first; if it fails, perform a name search.
    """
    cr = get_city_registry()
    loc_type = getattr(alert, "location_type", None)
    region_name = _norm_str(getattr(alert, "location_oblast", None))
    district_name = _norm_str(getattr(alert, "location_raion", None))
    title = _norm_str(getattr(alert, "location_title", None)) or ""

    # Normalize oblast and raion names to match codifier entries
    if region_name:
        region_name = _clean_region_name(region_name)
    if district_name:
        district_name = _clean_raion_name(district_name)

    # Optional fields that can help
    location_hromada = _norm_str(getattr(alert, "location_hromada", None))
    location_city = _norm_str(getattr(alert, "location_city", None))
    location_settlement = _norm_str(getattr(alert, "location_settlement", None))

    # Prepare cleaned names based on a location type
    community_name: Optional[str] = None
    unit_name: Optional[str] = None

    if loc_type == TerritorialOrganization.HROMADA.value:
        community_name = _clean_hromada_title(title)
    elif loc_type == TerritorialOrganization.CITY.value:
        unit_name = _clean_unit_title(title)

    # Sometimes API provides explicit hromada or city fields
    if not community_name and location_hromada:
        community_name = _clean_hromada_title(location_hromada)
    if not unit_name and (location_city or location_settlement):
        unit_name = _clean_unit_title(location_city or location_settlement)

    # Try stepwise resolution using codifier hierarchy
    try:
        if loc_type == TerritorialOrganization.OBLAST.value:
            if region_name:
                code = await cr.get_code(region_name=region_name)
                if code:
                    return code
        elif loc_type == TerritorialOrganization.RAION.value:
            if region_name and district_name:
                code = await cr.get_code(
                    region_name=region_name, district_name=district_name
                )
                if code:
                    return code
        elif loc_type == TerritorialOrganization.HROMADA.value:
            if region_name and district_name and community_name:
                code = await cr.get_code(
                    region_name=region_name,
                    district_name=district_name,
                    community_name=community_name,
                )
                if code:
                    return code
        elif loc_type == TerritorialOrganization.CITY.value:
            if region_name and district_name and community_name and unit_name:
                code = await cr.get_code(
                    region_name=region_name,
                    district_name=district_name,
                    community_name=community_name,
                    unit_name=unit_name,
                )
                if code:
                    return code
        # Fallback: try the deepest available with whatever we have
        code = await cr.get_code(
            region_name=region_name,
            district_name=district_name,
            community_name=community_name,
            unit_name=unit_name,
        )
        if code:
            return code
    except Exception:
        pass

    # Final fallback: search by name
    query = None
    if unit_name:
        query = unit_name
    elif community_name:
        query = community_name
    else:
        query = title or (location_city or location_settlement) or ""

    if query:
        try:
            matches = await cr.search(query)
            for chain, code, cat in matches:
                if code and code != "nan":
                    return code
        except Exception:
            pass

    return None


async def call_for_air_alert():
    from core.config import air_alert_api_token

    alerts_client = AsyncAlertsClient(token=air_alert_api_token)
    active_alerts = await alerts_client.get_active_alerts()
    print("ALERT API REQUEST: ", datetime.datetime.now())
    return {"data": active_alerts, "timestamp": datetime.datetime.now()}
