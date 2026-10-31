#!/usr/bin/env bash
# Chach-Chu ni ishga tushirish (virtual muhit bo'lsa — avtomatik yoqadi)
set -e
cd "$(dirname "$0")"

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  . .venv/bin/activate
fi

if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi

exec $PY -m chachchu "$@"
