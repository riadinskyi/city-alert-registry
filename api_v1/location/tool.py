import json
import asyncio
import math


class CityRegistry:
    LEVEL_CAT = {
        "region": ("O", "K"),
        "district": ("P",),
        "community": ("H",),
        "unit": ("C", "M", "X"),
    }

    CATEGORY_LABEL = {
        "O": "область",
        "K": "місто зі спец. статусом",
        "P": "район",
        "H": "громада",
        "C": "село",
        "M": "місто",
        "X": "селище",
    }

    def __init__(self, path: str):
        self.path = path
        with open(path, encoding="utf-8") as f:
            self.recs = json.load(f)

    def _norm(self, s: str) -> str:
        return s.strip().lower()

    def _list_level_with_cat(
        self,
        level: str,
        parent_key: str = None,
        parent_code: str = None,
    ) -> list[tuple[str, str]]:
        cats = self.LEVEL_CAT[level]
        items: dict[str, str] = {}
        for r in self.recs:
            cat = r.get("Category")
            if cat not in cats:
                continue
            if parent_key and r.get(parent_key) != parent_code:
                continue
            name = r.get("Name", "").strip()
            if name:
                items[name] = cat
        return sorted(items.items(), key=lambda nc: nc[0].lower())

    async def list_level_with_cat(
        self,
        level: str,
        parent_key: str = None,
        parent_code: str = None,
    ) -> list[tuple[str, str]]:
        return await asyncio.to_thread(
            self._list_level_with_cat, level, parent_key, parent_code
        )

    def _get_code(
        self,
        region_name: str,
        district_name: str = None,
        community_name: str = None,
        unit_name: str = None,
    ) -> str | None:
        # 1) region
        reg = next(
            (
                r
                for r in self.recs
                if r.get("Category") in ("O", "K")
                and r.get("Name", "").strip() == region_name
            ),
            None,
        )
        if not reg:
            return None
        code = reg["First_Level"]

        if not district_name:
            return code

        # 2) district
        dist = next(
            (
                r
                for r in self.recs
                if r.get("Category") == "P"
                and r.get("First_Level") == code
                and r.get("Name", "").strip() == district_name
            ),
            None,
        )
        if not dist:
            return None
        code = dist["Second_Level"]

        if not community_name:
            return code

        # 3) community
        comm = next(
            (
                r
                for r in self.recs
                if r.get("Category") == "H"
                and r.get("Second_Level") == code
                and r.get("Name", "").strip() == community_name
            ),
            None,
        )
        if not comm:
            return None
        code = comm["Third_Level"]

        if not unit_name:
            return code

        # 4) unit (C, M або X)
        unit = next(
            (
                r
                for r in self.recs
                if r.get("Category") in ("C", "M", "X")
                and r.get("Third_Level") == code
                and r.get("Name", "").strip() == unit_name
            ),
            None,
        )
        return unit and unit["Fourth_Level"] or None

    async def get_code(
        self,
        region_name: str,
        district_name: str = None,
        community_name: str = None,
        unit_name: str = None,
    ) -> str | None:
        return await asyncio.to_thread(
            self._get_code, region_name, district_name, community_name, unit_name
        )

    def _get_chain(self, rec: dict) -> tuple[list[str], str, str]:
        chain: list[str] = []
        cat: str = rec.get("Category", "")

        # Обробка значень NaN для всіх рівнів
        def safe_value(val) -> str:
            if val is None or (isinstance(val, float) and math.isnan(val)):
                return ""
            return (
                str(int(val))
                if isinstance(val, float) and val.is_integer()
                else str(val)
            )

        f1 = safe_value(rec.get("First_Level"))
        s2 = safe_value(rec.get("Second_Level"))
        t3 = safe_value(rec.get("Third_Level"))
        f4 = safe_value(rec.get("Fourth_Level"))

        # region
        reg = next(
            (
                r
                for r in self.recs
                if r.get("Category") in ("O", "K")
                and safe_value(r.get("First_Level")) == f1
            ),
            None,
        )
        if reg:
            chain.append(reg["Name"].strip())
            if safe_value(reg.get("Category")) == "K":
                cat = "K"

        # district
        if s2:
            dist = next(
                (
                    r
                    for r in self.recs
                    if safe_value(r.get("Category")) == "P"
                    and safe_value(r.get("Second_Level")) == s2
                ),
                None,
            )
            if dist:
                chain.append(dist["Name"].strip())

        # community
        if t3:
            comm = next(
                (
                    r
                    for r in self.recs
                    if safe_value(r.get("Category")) == "H"
                    and safe_value(r.get("Third_Level")) == t3
                ),
                None,
            )
            if comm:
                chain.append(comm["Name"].strip())

        # unit
        if f4:
            unit = next(
                (
                    r
                    for r in self.recs
                    if safe_value(r.get("Category")) in ("C", "M", "X")
                    and safe_value(r.get("Fourth_Level")) == f4
                ),
                None,
            )
            if unit:
                chain.append(unit["Name"].strip())
                cat = safe_value(unit.get("Category"))

        # Визначення коду
        code = f4 or t3 or s2 or f1 or ""
        return chain, code, cat

    async def get_chain(self, rec: dict) -> tuple[list[str], str, str]:
        return await asyncio.to_thread(self._get_chain, rec)

    def _search(self, query: str) -> list[tuple[list[str], str, str]]:
        q = self._norm(query)
        results: list[tuple[list[str], str, str]] = []
        for r in self.recs:
            if q in self._norm(r.get("Name", "")):
                chain, code, cat = self._get_chain(r)
                if cat in ("C", "M", "X", "K") and code and code != "nan":
                    results.append((chain, code, cat))
        return results

    async def search(self, query: str) -> list[tuple[list[str], str, str]]:
        return await asyncio.to_thread(self._search, query)

    def _search_by_code(self, ua_code: str) -> tuple[list[str], str, str] | None:
        # Нормалізуємо вхідний код
        input_full = (ua_code or "").strip().upper()
        input_no_prefix = input_full[2:] if input_full.startswith("UA") else input_full

        # Функція безпечного читання значень
        def safe_value(val) -> str:
            if val is None or (isinstance(val, float) and math.isnan(val)):
                return ""
            return (
                str(int(val))
                if isinstance(val, float) and val.is_integer()
                else str(val)
            )

        # Пошук по всіх рівнях
        for record in self.recs:
            for key in ["First_Level", "Second_Level", "Third_Level", "Fourth_Level"]:
                raw = safe_value(record.get(key))
                val_full = (raw or "").strip().upper()
                val_no_prefix = val_full[2:] if val_full.startswith("UA") else val_full
                if val_full == input_full or val_no_prefix == input_no_prefix:
                    return self._get_chain(record)

        return None

    async def search_by_code(self, ua_code: str) -> tuple[list[str], str, str] | None:
        """Асинхронна версія пошуку за кодом"""
        return await asyncio.to_thread(self._search_by_code, ua_code)


def choose_typed(
    options: list[tuple[str, str]],
    prompt: str,
    cat_labels: dict[str, str],
) -> str:
    print(f"\n{prompt}:")
    for i, (name, cat) in enumerate(options, start=1):
        label = cat_labels.get(cat, cat)
        print(f"  {i}. {name} ({label})")
    while True:
        sel = input(f"Введіть номер (1–{len(options)}): ").strip()
        if sel.isdigit():
            idx = int(sel)
            if 1 <= idx <= len(options):
                return options[idx - 1][0]


async def interactive_manual(cr: CityRegistry) -> tuple[list[str], str]:
    regions = await cr.list_level_with_cat("region")
    reg = choose_typed(regions, "Оберіть область / місто", cr.CATEGORY_LABEL)

    dist_opts = await cr.list_level_with_cat(
        "district", parent_key="First_Level", parent_code=await cr.get_code(reg)
    )
    dist = (
        choose_typed(dist_opts, "Оберіть район", cr.CATEGORY_LABEL)
        if dist_opts
        else None
    )

    comm_opts = await cr.list_level_with_cat(
        "community", parent_key="Second_Level", parent_code=await cr.get_code(reg, dist)
    )
    comm = (
        choose_typed(comm_opts, "Оберіть громаду", cr.CATEGORY_LABEL)
        if comm_opts
        else None
    )

    unit_opts = await cr.list_level_with_cat(
        "unit", parent_key="Third_Level", parent_code=await cr.get_code(reg, dist, comm)
    )
    unit = (
        choose_typed(unit_opts, "Оберіть населений пункт", cr.CATEGORY_LABEL)
        if unit_opts
        else None
    )

    code = await cr.get_code(reg, dist, comm, unit)
    chain = list(filter(None, [reg, dist, comm, unit]))
    return chain, code or "Не знайдено"


async def interactive_search(cr: CityRegistry) -> tuple[list[str], str] | None:
    query = input("\n🔍 Введіть фрагмент назви для пошуку: ").strip()
    matches = await cr.search(query)
    if not matches:
        print("❌ Нічого не знайдено.")
        return None

    print("\nЗнайдені варіанти:")
    for i, (chain, code, cat) in enumerate(matches, start=1):
        label = cr.CATEGORY_LABEL.get(cat, cat)
        print(f"  {i}. {' > '.join(chain)} ({label})    [код: {code}]")

    while True:
        sel = input(f"Оберіть номер (1–{len(matches)}): ").strip()
        if sel.isdigit():
            idx = int(sel)
            if 1 <= idx <= len(matches):
                chain, code, _ = matches[idx - 1]
                return chain, code
