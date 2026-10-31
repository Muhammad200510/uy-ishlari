"""Tool'larni ro'yxatga olish va Claude uchun sxemalarni tayyorlash."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Tool:
    """Bitta tool: nomi, tavsifi, kirish sxemasi va bajaruvchi funksiya."""

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., str]

    def to_claude_schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class ToolRegistry:
    """Barcha tool'lar ro'yxati."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def add(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Callable[..., str],
    ) -> None:
        self.register(Tool(name, description, input_schema, handler))

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools)

    def claude_schemas(self) -> list[dict[str, Any]]:
        """Claude API uchun barcha custom tool sxemalari."""
        return [t.to_claude_schema() for t in self._tools.values()]

    def execute(self, name: str, tool_input: dict[str, Any]) -> str:
        """Tool'ni bajarish. Xatolar matn sifatida qaytariladi (loop buzilmasin)."""
        tool = self.get(name)
        if tool is None:
            return f"Xatolik: '{name}' nomli tool topilmadi."
        try:
            return tool.handler(**tool_input)
        except TypeError as exc:
            return f"Xatolik: '{name}' tool'iga noto'g'ri parametrlar berildi: {exc}"
        except Exception as exc:  # noqa: BLE001 — har qanday xato matn bo'lib qaytsin
            return f"Xatolik: '{name}' bajarilmadi: {exc}"
