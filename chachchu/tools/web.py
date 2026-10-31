"""Yordamchi tool'lar: sana/vaqt. (Internet qidiruvi Claude'ning server tool'i orqali.)"""

from __future__ import annotations

from datetime import datetime

from .registry import ToolRegistry

_WEEKDAYS_UZ = [
    "Dushanba",
    "Seshanba",
    "Chorshanba",
    "Payshanba",
    "Juma",
    "Shanba",
    "Yakshanba",
]


def get_datetime() -> str:
    """Hozirgi sana va vaqtni o'zbekcha qaytaradi."""
    now = datetime.now()
    weekday = _WEEKDAYS_UZ[now.weekday()]
    return now.strftime(f"%Y-%m-%d %H:%M:%S ({weekday})")


def register(registry: ToolRegistry) -> None:
    registry.add(
        name="get_datetime",
        description="Hozirgi sana va vaqtni qaytaradi.",
        input_schema={"type": "object", "properties": {}},
        handler=get_datetime,
    )
