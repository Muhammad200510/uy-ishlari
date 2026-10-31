"""Qurilmani boshqarish tool'lari: dastur ochish, havola ochish, buyruq bajarish."""

from __future__ import annotations

import platform
import shlex
import subprocess
import webbrowser

from .registry import ToolRegistry


def _os() -> str:
    return platform.system()  # 'Darwin' (macOS), 'Windows', 'Linux'


def open_app(app_name: str) -> str:
    """Kompyuterda dastur ochish (platformaga qarab)."""
    system = _os()
    try:
        if system == "Darwin":
            subprocess.Popen(["open", "-a", app_name])
        elif system == "Windows":
            subprocess.Popen(["cmd", "/c", "start", "", app_name], shell=False)
        else:  # Linux
            subprocess.Popen([app_name])
        return f"'{app_name}' dasturi ochildi."
    except FileNotFoundError:
        return f"'{app_name}' dasturi topilmadi. Nom to'g'ri yozilganini tekshiring."
    except Exception as exc:  # noqa: BLE001
        return f"'{app_name}' ochilmadi: {exc}"


def open_url(url: str) -> str:
    """Brauzerda havola ochish."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    opened = webbrowser.open(url)
    return f"Havola ochildi: {url}" if opened else f"Havolani ochib bo'lmadi: {url}"


def run_shell(command: str, timeout: int = 30) -> str:
    """Terminal buyrug'ini bajarish. XAVFLI — faqat tasdiqdan keyin chaqiriladi.

    Natija (stdout/stderr) matn sifatida qaytariladi.
    """
    try:
        if _os() == "Windows":
            args = command  # Windows'da shell=True bilan satr
            shell = True
        else:
            args = shlex.split(command)
            shell = False
        proc = subprocess.run(
            args,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        parts = [f"Chiqish kodi: {proc.returncode}"]
        if out:
            parts.append(f"stdout:\n{out[:4000]}")
        if err:
            parts.append(f"stderr:\n{err[:2000]}")
        return "\n".join(parts)
    except subprocess.TimeoutExpired:
        return f"Buyruq {timeout} soniyada tugamadi (timeout)."
    except Exception as exc:  # noqa: BLE001
        return f"Buyruq bajarilmadi: {exc}"


def register(registry: ToolRegistry) -> None:
    registry.add(
        name="open_app",
        description="Kompyuterda biror dasturni ochadi. Masalan: 'Safari', 'Telegram', "
        "'Calculator'. Faqat foydalanuvchi aniq so'raganda ishlat.",
        input_schema={
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "Ochiladigan dastur nomi.",
                }
            },
            "required": ["app_name"],
        },
        handler=open_app,
    )
    registry.add(
        name="open_url",
        description="Brauzerda veb-havolani ochadi.",
        input_schema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Ochiladigan to'liq havola."}
            },
            "required": ["url"],
        },
        handler=open_url,
    )
    registry.add(
        name="run_shell",
        description="Operatsion tizim terminalida buyruq bajaradi va natijani qaytaradi. "
        "Bu XAVFLI amal — faqat foydalanuvchi aniq va ongli ravishda so'raganda ishlat. "
        "Fayl o'chirish yoki tizimga zarar beruvchi buyruqlardan ehtiyot bo'l.",
        input_schema={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Bajariladigan buyruq."},
                "timeout": {
                    "type": "integer",
                    "description": "Maksimal kutish vaqti (soniya). Standart: 30.",
                },
            },
            "required": ["command"],
        },
        handler=run_shell,
    )
