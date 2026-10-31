"""Ijtimoiy tarmoqlar tool'lari — rasmiy API orqali (hozircha Telegram)."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

from .registry import ToolRegistry

_TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


class SocialConfig:
    """Ijtimoiy tarmoq sozlamalari (config.json dan)."""

    def __init__(self, telegram_token: str = "", telegram_chat_id: str = ""):
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id


def _telegram_call(token: str, method: str, params: dict) -> dict:
    url = _TELEGRAM_API.format(token=token, method=method)
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310 — ishonchli host
        return json.loads(resp.read().decode("utf-8"))


def make_send_telegram(cfg: SocialConfig):
    """Config'ga bog'langan send_telegram funksiyasini yaratadi."""

    def send_telegram(text: str, chat_id: str = "") -> str:
        if not cfg.telegram_token:
            return (
                "Telegram sozlanmagan. config.json dagi telegram.bot_token ni to'ldiring "
                "(@BotFather orqali bot yarating)."
            )
        target = chat_id or cfg.telegram_chat_id
        if not target:
            return (
                "Qaysi chatga yuborishni bilmayman. config.json dagi "
                "telegram.default_chat_id ni to'ldiring yoki chat_id bering."
            )
        result = _telegram_call(
            cfg.telegram_token, "sendMessage", {"chat_id": target, "text": text}
        )
        if result.get("ok"):
            return f"Telegramga yuborildi: \"{text}\""
        return f"Telegramga yuborib bo'lmadi: {result.get('description', 'noma`lum xato')}"

    return send_telegram


def make_post_social(cfg: SocialConfig):
    """Umumiy post_social — platformaga qarab yo'naltiradi."""
    send_telegram = make_send_telegram(cfg)

    def post_social(platform: str, text: str) -> str:
        platform = platform.strip().lower()
        if platform in {"telegram", "tg"}:
            return send_telegram(text)
        return (
            f"'{platform}' hozircha qo'llab-quvvatlanmaydi. Hozir faqat Telegram ishlaydi. "
            "Instagram/X kabi tarmoqlarni faqat RASMIY API orqali qo'shish mumkin — "
            "norasmiy avtomatlashtirish akkauntni bloklaydi. "
            "Yangi platforma uchun chachchu/tools/social.py ni kengaytiring."
        )

    return post_social


def register(registry: ToolRegistry, cfg: SocialConfig) -> None:
    registry.add(
        name="send_telegram",
        description="Telegram bot orqali xabar yuboradi. Faqat foydalanuvchi so'raganda. "
        "chat_id berilmasa, sozlamalardagi standart chatga yuboriladi.",
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Yuboriladigan xabar matni."},
                "chat_id": {
                    "type": "string",
                    "description": "Qabul qiluvchi chat id (ixtiyoriy).",
                },
            },
            "required": ["text"],
        },
        handler=make_send_telegram(cfg),
    )
    registry.add(
        name="post_social",
        description="Ijtimoiy tarmoqqa post/xabar yuboradi. platform='telegram' ishlaydi.",
        input_schema={
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "description": "Tarmoq nomi, masalan 'telegram'.",
                },
                "text": {"type": "string", "description": "Post matni."},
            },
            "required": ["platform", "text"],
        },
        handler=make_post_social(cfg),
    )


def _whoami(token: str) -> None:
    """getUpdates orqali chat id ni aniqlashda yordam beradi."""
    if not token:
        print("Avval config.json da telegram.bot_token ni to'ldiring.")
        return
    result = _telegram_call(token, "getUpdates", {})
    if not result.get("ok"):
        print("Xato:", result.get("description"))
        return
    updates = result.get("result", [])
    if not updates:
        print("Hech qanday xabar yo'q. Avval botingizga biror xabar yozing, so'ng qayta urinib ko'ring.")
        return
    seen = set()
    for upd in updates:
        msg = upd.get("message") or upd.get("channel_post") or {}
        chat = msg.get("chat", {})
        cid = chat.get("id")
        if cid and cid not in seen:
            seen.add(cid)
            name = chat.get("title") or chat.get("username") or chat.get("first_name") or ""
            print(f"chat_id = {cid}   ({name})")


if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from chachchu.config import Config  # noqa: E402

    parser = argparse.ArgumentParser(description="Telegram yordamchi")
    parser.add_argument("--whoami", action="store_true", help="chat_id ni aniqlash")
    args = parser.parse_args()

    conf = Config.load()
    tok = conf.get("telegram", "bot_token", default="")
    if args.whoami:
        _whoami(tok)
    else:
        parser.print_help()
