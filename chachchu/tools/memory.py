"""Oddiy eslab qolish tool'i — faktlarni JSON faylga saqlaydi."""

from __future__ import annotations

import json
from pathlib import Path

from .registry import ToolRegistry

_MEMORY_PATH = Path.cwd() / "chachchu_memory.json"


def _load() -> dict[str, str]:
    if _MEMORY_PATH.is_file():
        try:
            return json.loads(_MEMORY_PATH.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return {}
    return {}


def _save(data: dict[str, str]) -> None:
    _MEMORY_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def remember(key: str, value: str) -> str:
    """Biror ma'lumotni kalit bilan eslab qolish."""
    data = _load()
    data[key] = value
    _save(data)
    return f"Eslab qoldim: '{key}' = '{value}'."


def recall_memory(key: str = "") -> str:
    """Eslab qolingan ma'lumotni qaytarish. key bo'sh bo'lsa — hammasini."""
    data = _load()
    if not data:
        return "Hozircha hech narsa eslab qolinmagan."
    if key:
        return data.get(key, f"'{key}' bo'yicha hech narsa eslamadim.")
    return "\n".join(f"- {k}: {v}" for k, v in data.items())


def register(registry: ToolRegistry) -> None:
    registry.add(
        name="remember",
        description="Foydalanuvchi haqidagi biror ma'lumotni (afzalliklar, ismlar, "
        "sozlamalar) keyingi suhbatlar uchun eslab qoladi.",
        input_schema={
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Ma'lumot kaliti/nomi."},
                "value": {"type": "string", "description": "Saqlanadigan qiymat."},
            },
            "required": ["key", "value"],
        },
        handler=remember,
    )
    registry.add(
        name="recall_memory",
        description="Avval eslab qolingan ma'lumotni qaytaradi. 'key' berilmasa, "
        "barcha eslab qolingan narsalarni qaytaradi.",
        input_schema={
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Qidirilayotgan kalit (ixtiyoriy)."}
            },
        },
        handler=recall_memory,
    )
