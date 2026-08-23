import json
from pathlib import Path
from typing import Dict, List, Any

RULES_DIR = Path(__file__).resolve().parent


def load_rules_from_json(filename: str) -> List[Dict[str, Any]]:
    """Loads rule definitions from a JSON file in the rules directory."""
    path = RULES_DIR / filename
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("rules", [])


def load_all_rules() -> Dict[str, List[Dict[str, Any]]]:
    """Loads all rule categories."""
    return {
        "mandatory": load_rules_from_json("mandatory.json"),
        "quantity": load_rules_from_json("quantity.json"),
        "pricing": load_rules_from_json("pricing.json"),
        "declarations": load_rules_from_json("declarations.json"),
    }
