#!/usr/bin/env bash
# Chach-Chu — avtomatik o'rnatish (Linux / macOS / Termux)
set -e

echo "==> Chach-Chu o'rnatilmoqda..."

# Python aniqlash
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python topilmadi. Avval Python 3.9+ o'rnating."
  exit 1
fi
echo "==> Python: $($PY --version)"

# Virtual muhit (Termux'da venv ba'zan muammo qiladi — o'tkazib yuborish mumkin)
if [ "${CHACHCHU_NO_VENV:-0}" != "1" ]; then
  if [ ! -d ".venv" ]; then
    echo "==> Virtual muhit yaratilmoqda (.venv)..."
    $PY -m venv .venv || echo "venv yaratib bo'lmadi, tizim Python'i ishlatiladi."
  fi
  if [ -f ".venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    . .venv/bin/activate
    PY=python
  fi
fi

echo "==> Kutubxonalar o'rnatilmoqda..."
$PY -m pip install --upgrade pip >/dev/null 2>&1 || true
$PY -m pip install -r requirements.txt

# Ovoz kutubxonalari (ixtiyoriy)
if [ "${CHACHCHU_VOICE:-0}" = "1" ]; then
  echo "==> Ovoz kutubxonalari o'rnatilmoqda..."
  $PY -m pip install -r requirements-voice.txt || \
    echo "Ovoz kutubxonalarini o'rnatib bo'lmadi (matnli rejim baribir ishlaydi)."
fi

# Sozlama fayllari
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "==> .env yaratildi — unga ANTHROPIC_API_KEY ni qo'ying!"
fi
if [ ! -f "config.json" ]; then
  cp config.example.json config.json
  echo "==> config.json yaratildi."
fi

echo ""
echo "✅ O'rnatish tugadi!"
echo "   1) .env faylini ochib ANTHROPIC_API_KEY ni qo'ying."
echo "   2) Ishga tushirish:  ./run.sh   yoki   $PY -m chachchu"
