"""Load and normalize event exports from different sources."""

from __future__ import annotations
import csv
import json
from pathlib import Path
from typing import Any


def load_events(path: str | Path) -> list[dict[str, Any]]:
    """Load events from CSV or JSON. Expects normalized columns (see normalize)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    if path.suffix.lower() == ".json":
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "events" in data:
            data = data["events"]
        if not isinstance(data, list):
            raise ValueError("JSON root must be a list of events or {\"events\": [...]}")
        return [normalize_event(e, source_hint=path.stem) for e in data]

    # CSV
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [normalize_event(row, source_hint=path.stem) for row in reader]


def normalize_event(raw: dict, source_hint: str = "") -> dict[str, Any]:
    """Map common column names into a standard schema."""
    # Flexible key lookup (case-insensitive)
    lower = {str(k).lower().strip(): v for k, v in raw.items()}

    def get(*keys, default=None):
        for k in keys:
            if k.lower() in lower and lower[k.lower()] not in (None, ""):
                return lower[k.lower()]
        return default

    event = {
        "source": get("source", "platform", "system") or source_hint,
        "event_name": (get("event_name", "event", "eventname", "type") or "purchase").lower(),
        "transaction_id": str(get("transaction_id", "transactionid", "order_id", "orderid", "id") or "").strip(),
        "value": _to_float(get("value", "revenue", "amount", "total")),
        "currency": (get("currency", "currencycode") or "USD").upper(),
        "timestamp": get("timestamp", "time", "datetime", "date") or "",
        "items": get("items", "item_count", "quantity"),
        "consent": get("consent", "consent_status", "ad_storage"),
        "raw": raw,
    }
    return event


def _to_float(v) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(str(v).replace(",", "").replace("$", "").strip())
    except (TypeError, ValueError):
        return None


def load_multi(paths: list[str | Path]) -> list[dict]:
    """Load and concatenate events from multiple files."""
    all_events = []
    for p in paths:
        all_events.extend(load_events(p))
    return all_events