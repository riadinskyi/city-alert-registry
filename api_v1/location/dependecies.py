import json
import os


async def credentials_return(
    path=None,
):
    if path is None:
        # Build the path relative to the project root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        path = os.path.join(base_dir, "core", "tools", "location", "kodifikator.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        return {"provider": json_data["provider"], "order": json_data["order"]}
