from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .login_guard import forbidden_sensitive_keys


@dataclass
class Listing:
    id: str
    title: str
    price: str
    description: str
    postal_code: str = ""
    city: str = ""
    condition: str = "Gut"
    category_path: list[str] = field(default_factory=list)
    shipping: str = "default"
    photos: list[str] = field(default_factory=list)


def _load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise SystemExit("YAML support requires: python -m pip install '.[yaml]'") from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_raw_queue(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(p)

    suffix = p.suffix.lower()
    if suffix == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
    elif suffix in {".yaml", ".yml"}:
        data = _load_yaml(p)
    elif suffix == ".csv":
        with p.open(newline="", encoding="utf-8") as handle:
            data = list(csv.DictReader(handle))
    else:
        raise ValueError(f"Unsupported queue format: {p.suffix}")

    if isinstance(data, dict):
        data = data.get("items") or data.get("listings") or [data]
    if not isinstance(data, list):
        raise ValueError("Queue must be a list or a dict with items/listings")
    for idx, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Queue item {idx} must be an object/dict")
    return data


def _as_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(">") if part.strip()]
    if isinstance(value, Iterable):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value).strip()]


def coerce_listing(raw: dict[str, Any], idx: int = 1) -> Listing:
    sensitive = forbidden_sensitive_keys(raw)
    if sensitive:
        raise ValueError(
            "Listing contains forbidden credential/session-like keys: " + ", ".join(sorted(sensitive))
        )

    title = str(raw.get("title") or raw.get("titel") or "").strip()
    price = str(raw.get("price") or raw.get("preis") or "").strip()
    description = str(raw.get("description") or raw.get("beschreibung") or "").strip()

    missing = [name for name, value in {"title": title, "price": price, "description": description}.items() if not value]
    if missing:
        raise ValueError(f"Listing {idx} is missing required fields: {', '.join(missing)}")

    return Listing(
        id=str(raw.get("id") or f"item-{idx:03d}"),
        title=title,
        price=price,
        description=description,
        postal_code=str(raw.get("postal_code") or raw.get("zip") or raw.get("plz") or "").strip(),
        city=str(raw.get("city") or raw.get("ort") or "").strip(),
        condition=str(raw.get("condition") or raw.get("zustand") or "Gut").strip(),
        category_path=_as_list(raw.get("category_path") or raw.get("category") or raw.get("kategorie")),
        shipping=str(raw.get("shipping") or raw.get("versand") or "default").strip(),
        photos=_as_list(raw.get("photos") or raw.get("bilder")),
    )


def load_listings(path: str | Path) -> list[Listing]:
    raw_items = load_raw_queue(path)
    return [coerce_listing(item, idx=i) for i, item in enumerate(raw_items, start=1)]
