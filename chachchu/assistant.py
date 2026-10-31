"""Chach-Chu ni yig'ib, muloqot siklini boshqaradi."""

from __future__ import annotations

from .brain import Brain
from .config import Config
from .permissions import PermissionManager, cli_confirm
from .tools import memory as memory_tools
from .tools import social as social_tools
from .tools import system as system_tools
from .tools import web as web_tools
from .tools.registry import ToolRegistry
from .tools.social import SocialConfig


def build_registry(cfg: Config) -> ToolRegistry:
    """Barcha tool'larni ro'yxatga oladi."""
    registry = ToolRegistry()
    system_tools.register(registry)
    web_tools.register(registry)
    memory_tools.register(registry)
    social_cfg = SocialConfig(
        telegram_token=cfg.get("telegram", "bot_token", default=""),
        telegram_chat_id=cfg.get("telegram", "default_chat_id", default=""),
    )
    social_tools.register(registry, social_cfg)
    return registry


def build_brain(
    cfg: Config,
    headless: bool = False,
    assume_yes: bool = False,
) -> Brain:
    """Konfiguratsiyadan Brain yaratadi.

    headless=True bo'lsa (bridge rejimi) tasdiq so'ralmaydi — xavfli amallar rad etiladi.
    """
    registry = build_registry(cfg)
    permissions = PermissionManager(
        auto_allow=cfg.get("permissions", "auto_allow", default=[]),
        always_confirm=cfg.get("permissions", "always_confirm", default=[]),
        confirm_fn=None if headless else cli_confirm,
        assume_yes=assume_yes,
    )
    if not cfg.api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY topilmadi. .env faylida yoki muhit o'zgaruvchisida sozlang."
        )
    return Brain(
        registry=registry,
        permissions=permissions,
        model=cfg.model,
        api_key=cfg.api_key,
    )


def run_cli(cfg: Config, use_voice: bool = False, assume_yes: bool = False) -> None:
    """Terminalda interaktiv muloqot."""
    brain = build_brain(cfg, headless=False, assume_yes=assume_yes)

    voice = None
    if use_voice:
        from .speech import VoiceIO

        voice = VoiceIO(
            stt_language=cfg.get("voice", "stt_language", default="uz-UZ"),
            tts_language=cfg.get("voice", "tts_language", default="uz"),
        )
        if not voice.available:
            voice = None  # matnli rejimga tushamiz

    name = cfg.name
    hello = f"Assalomu alaykum! Men {name}. Sizga qanday yordam bera olaman?"
    print(f"\n🤖 {name} ishga tushdi. Chiqish uchun: 'chiq', 'exit' yoki Ctrl+C.\n")
    print(f"{name}: {hello}")
    if voice:
        voice.speak(hello)

    while True:
        try:
            if voice:
                user_text = voice.listen()
                if not user_text:
                    continue
                print(f"Siz: {user_text}")
            else:
                user_text = input("\nSiz: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nXayr! 👋")
            break

        if not user_text:
            continue
        if user_text.lower() in {"chiq", "chiqish", "exit", "quit", "xayr"}:
            bye = "Xayr! Yana kerak bo'lsam, chaqiring."
            print(f"{name}: {bye}")
            if voice:
                voice.speak(bye)
            break

        try:
            reply = brain.ask(user_text)
        except Exception as exc:  # noqa: BLE001
            reply = f"Kechirasiz, xatolik yuz berdi: {exc}"

        print(f"{name}: {reply}")
        if voice:
            voice.speak(reply)
