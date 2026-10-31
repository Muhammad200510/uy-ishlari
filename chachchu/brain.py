"""Chach-Chu ning 'miyasi' — Claude API va tool-use mantig'i."""

from __future__ import annotations

from typing import Any

from .permissions import PermissionManager
from .tools.registry import ToolRegistry

SYSTEM_PROMPT = """Sen "Chach-Chu" nomli shaxsiy AI yordamchisan.

Qoidalar:
- Doim O'ZBEK TILIDA, tabiiy va samimiy ohangda javob ber.
- Qisqa, aniq va foydali bo'l. Keraksiz uzun gaplardan saqlan.
- Foydalanuvchi qurilmasini va topshiriqlarini bajarishga yordam ber.
- Biror amalni bajarish uchun senga tool'lar berilgan (dastur ochish, havola ochish,
  buyruq bajarish, internetdan qidirish, Telegramga yozish, eslab qolish va h.k.).
  Kerak bo'lsa ulardan foydalan.
- Xavfli yoki tashqariga ta'sir qiluvchi amallar (buyruq bajarish, post yuborish)
  foydalanuvchidan tasdiq so'raydi — bu normal holat. Agar foydalanuvchi rad etsa,
  hurmat bilan qabul qil va boshqa yo'l taklif qil.
- O'zingdan ma'lumot to'qima. Bilmasang yoki ishonchli bo'lmasang, internetdan qidir
  yoki rostini ayt.
- Foydalanuvchiga zarar beradigan yoki noqonuniy ishlarni bajarma.

Sen ovoz orqali ham gaplasha olasan, shuning uchun javoblaring og'zaki eshitishga
qulay bo'lsin: ortiqcha belgilar, jadvallar yoki uzun kod bloklaridan voz kech
(agar foydalanuvchi aniq kod so'ramasa)."""


class Brain:
    def __init__(
        self,
        registry: ToolRegistry,
        permissions: PermissionManager,
        model: str = "claude-opus-5-5",
        api_key: str | None = None,
        enable_web_search: bool = True,
        max_tokens: int = 4096,
    ):
        import anthropic  # lazy import — faqat kerak bo'lganda

        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        self.registry = registry
        self.permissions = permissions
        self.model = model
        self.max_tokens = max_tokens
        self.enable_web_search = enable_web_search
        self.messages: list[dict[str, Any]] = []

    def _tools_param(self) -> list[dict[str, Any]]:
        tools = list(self.registry.claude_schemas())
        if self.enable_web_search:
            # Anthropic server-side web qidiruv tool'i (kod tarafida bajarish shart emas).
            tools.append(
                {"type": "web_search_20260209", "name": "web_search", "max_uses": 5}
            )
        return tools

    def _execute_with_permission(self, name: str, tool_input: dict[str, Any]) -> str:
        allowed, reason = self.permissions.is_allowed(name, tool_input)
        if not allowed:
            return f"Amal bajarilmadi ({reason}). Foydalanuvchi bu amalni tasdiqlamadi."
        return self.registry.execute(name, tool_input)

    def ask(self, user_text: str) -> str:
        """Bitta foydalanuvchi so'roviga to'liq javob (tool'lar bilan birga) qaytaradi."""
        self.messages.append({"role": "user", "content": user_text})
        tools = self._tools_param()

        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                thinking={"type": "adaptive"},
                tools=tools,
                messages=self.messages,
            )

            # Suhbat tarixiga assistant javobini (thinking bloklari bilan) qo'shamiz
            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "pause_turn":
                # Server tool uzoq ishladi — davom ettirish uchun qayta yuboramiz
                continue

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if getattr(block, "type", None) == "tool_use":
                        result = self._execute_with_permission(block.name, dict(block.input))
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result,
                            }
                        )
                if tool_results:
                    self.messages.append({"role": "user", "content": tool_results})
                    continue
                # tool_use e'lon qilindi-yu, custom tool yo'q (faqat server tool) — davom
                continue

            # end_turn (yoki boshqa) — yakuniy matnni yig'amiz
            return self._extract_text(response.content)

    @staticmethod
    def _extract_text(content: list[Any]) -> str:
        parts = [
            block.text
            for block in content
            if getattr(block, "type", None) == "text"
        ]
        text = "\n".join(p for p in parts if p).strip()
        return text or "(javob bo'sh keldi)"
