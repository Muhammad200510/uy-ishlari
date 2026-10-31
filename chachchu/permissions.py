"""Ruxsat so'rash mantig'i — Chach-Chu hech narsani yashirincha qilmaydi."""

from __future__ import annotations

import json
from typing import Any, Callable


class PermissionManager:
    """Qaysi tool'lar tasdiqsiz, qaysilari so'rab bajarilishini boshqaradi.

    confirm_fn — foydalanuvchidan 'ha/yo'q' so'raydigan funksiya. Agar None bo'lsa
    (masalan, bridge/headless rejim), always_confirm tool'lari avtomatik rad etiladi.
    """

    def __init__(
        self,
        auto_allow: list[str] | None = None,
        always_confirm: list[str] | None = None,
        confirm_fn: Callable[[str, dict], bool] | None = None,
        assume_yes: bool = False,
    ):
        self.auto_allow = set(auto_allow or [])
        self.always_confirm = set(always_confirm or [])
        self._confirm_fn = confirm_fn
        self.assume_yes = assume_yes

    def is_allowed(self, tool_name: str, tool_input: dict[str, Any]) -> tuple[bool, str]:
        """(ruxsat_berildimi, sabab) qaytaradi."""
        # Avtomatik ruxsat berilgan va majburiy tasdiq talab qilmaydigan tool
        if tool_name in self.auto_allow and tool_name not in self.always_confirm:
            return True, "auto_allow"

        # Tasdiq so'raydigan funksiya yo'q (headless) — xavfli tool'ni rad etamiz
        if self._confirm_fn is None:
            if tool_name in self.always_confirm:
                return False, "headless rejimda tasdiqlab bo'lmaydi"
            # auto_allow'da ham, always_confirm'da ham bo'lmasa — ehtiyotkorlik bilan rad
            return False, "tasdiqlovchi yo'q"

        # assume_yes faqat always_confirm'da BO'LMAGAN tool'larga tegishli
        if self.assume_yes and tool_name not in self.always_confirm:
            return True, "assume_yes"

        allowed = bool(self._confirm_fn(tool_name, tool_input))
        return allowed, ("foydalanuvchi tasdiqladi" if allowed else "foydalanuvchi rad etdi")


def cli_confirm(tool_name: str, tool_input: dict[str, Any]) -> bool:
    """Terminalda 'ha/yo'q' so'raydigan standart funksiya."""
    pretty = json.dumps(tool_input, ensure_ascii=False, indent=2)
    print(f"\n⚠️  Chach-Chu quyidagi amalni bajarmoqchi: \033[1m{tool_name}\033[0m")
    print(pretty)
    answer = input("Ruxsat berasizmi? [ha/yo'q]: ").strip().lower()
    return answer in {"ha", "h", "yes", "y", "ok", "mayli", "bemalol"}
