"""Konfiguratsiyani yuklash."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # python-dotenv o'rnatilmagan bo'lsa ham ishlashi kerak
    pass


DEFAULT_CONFIG: dict[str, Any] = {
    "name": "Chach-Chu",
    "model": "claude-opus-5-5",
    "voice": {"enabled": False, "stt_language": "uz-UZ", "tts_language": "uz"},
    "permissions": {
        "auto_allow": ["get_datetime", "search_web", "recall_memory", "remember"],
        "always_confirm": [
            "run_shell",
            "open_app",
            "open_url",
            "send_telegram",
            "post_social",
        ],
    },
    "telegram": {"bot_token": "", "default_chat_id": ""},
    "bridge": {"enabled": False, "host": "0.0.0.0", "port": 8787, "token": ""},
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Ikki lug'atni rekursiv birlashtirish (override ustun)."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class Config:
    """Dastur sozlamalari."""

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @classmethod
    def load(cls, path: str | os.PathLike | None = None) -> "Config":
        """config.json ni yuklash (bo'lmasa — standart sozlamalar)."""
        data = dict(DEFAULT_CONFIG)
        candidates = []
        if path:
            candidates.append(Path(path))
        candidates.append(Path.cwd() / "config.json")
        candidates.append(Path(__file__).resolve().parent.parent / "config.json")

        for candidate in candidates:
            if candidate and candidate.is_file():
                with open(candidate, "r", encoding="utf-8") as f:
                    user_data = json.load(f)
                data = _deep_merge(data, user_data)
                break
        return cls(data)

    def get(self, *keys: str, default: Any = None) -> Any:
        """Ichki qiymatni olish: cfg.get('voice', 'enabled')."""
        node: Any = self._data
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    @property
    def api_key(self) -> str | None:
        return os.environ.get("ANTHROPIC_API_KEY")

    @property
    def model(self) -> str:
        return os.environ.get("CHACHCHU_MODEL") or self.get("model", default="claude-opus-5-5")

    @property
    def name(self) -> str:
        return self.get("name", default="Chach-Chu")

    def as_dict(self) -> dict[str, Any]:
        return dict(self._data)
