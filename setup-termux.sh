#!/usr/bin/env bash
# Chach-Chu — Android (Termux) uchun to'liq o'rnatish
#
# Avval Termux va "Termux:API" ilovasini F-Droid'dan o'rnating:
#   https://f-droid.org/packages/com.termux/
#   https://f-droid.org/packages/com.termux.api/
set -e

echo "==> Termux paketlari o'rnatilmoqda..."
pkg update -y || true
pkg install -y python termux-api git

echo "==> Chach-Chu kutubxonalari o'rnatilmoqda..."
CHACHCHU_NO_VENV=1 CHACHCHU_VOICE=0 bash setup.sh

echo ""
echo "✅ Termux o'rnatishi tugadi!"
echo ""
echo "Ovoz uchun 'Termux:API' ilovasi o'rnatilgan bo'lishi kerak (F-Droid)."
echo "Sinov:  termux-tts-speak \"Salom, men Chach-Chu\""
echo ""
echo "Ishga tushirish:"
echo "   python -m chachchu            # matnli"
echo "   python -m chachchu --voice    # ovozli (termux-api orqali)"
