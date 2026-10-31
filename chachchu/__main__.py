"""Chach-Chu kirish nuqtasi: python -m chachchu"""

from __future__ import annotations

import argparse
import sys

from .config import Config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="chachchu",
        description="Chach-Chu — O'zbekcha ovozli AI agent.",
    )
    parser.add_argument("--voice", action="store_true", help="Ovozli rejimda ishga tushirish")
    parser.add_argument("--bridge", action="store_true", help="iPhone/Shortcuts HTTP bridge rejimi")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Xavfsiz amallarni tasdiqsiz bajarish (always_confirm baribir so'raladi)",
    )
    parser.add_argument("--config", help="config.json yo'li (ixtiyoriy)")
    args = parser.parse_args(argv)

    cfg = Config.load(args.config)

    if not cfg.api_key:
        print("❌ ANTHROPIC_API_KEY topilmadi.")
        print("   .env.example ni .env ga nusxalab, kalitni qo'ying yoki muhit o'zgaruvchisini sozlang.")
        return 1

    try:
        if args.bridge:
            from .bridge import run_bridge

            run_bridge(cfg)
        else:
            from .assistant import run_cli

            use_voice = args.voice or bool(cfg.get("voice", "enabled", default=False))
            run_cli(cfg, use_voice=use_voice, assume_yes=args.yes)
    except RuntimeError as exc:
        print(f"❌ {exc}")
        return 1
    except KeyboardInterrupt:
        print("\nTo'xtatildi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
