# Chach-Chu — Windows 11 uchun o'rnatish (PowerShell)
# Ishga tushirish:  powershell -ExecutionPolicy Bypass -File .\setup.ps1
#            yoki:  setup.bat ni ikki marta bosing

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

Write-Host "==> Chach-Chu o'rnatilmoqda (Windows)..."

# Python aniqlash
$py = $null
if (Get-Command python -ErrorAction SilentlyContinue) { $py = "python" }
elseif (Get-Command py -ErrorAction SilentlyContinue) { $py = "py" }
else {
  Write-Error "Python topilmadi. https://python.org dan Python 3.9+ o'rnating (o'rnatishda 'Add Python to PATH' ni belgilang)."
  exit 1
}
Write-Host "==> Python: $(& $py --version)"

# Virtual muhit
if (-not (Test-Path ".venv")) {
  Write-Host "==> Virtual muhit yaratilmoqda (.venv)..."
  & $py -m venv .venv
}
$venvPy = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Write-Host "==> Kutubxonalar o'rnatilmoqda..."
& $venvPy -m pip install --upgrade pip | Out-Null
& $venvPy -m pip install -r requirements.txt

# Ovoz kutubxonalari (ixtiyoriy) — $env:CHACHCHU_VOICE="1" bo'lsa
if ($env:CHACHCHU_VOICE -eq "1") {
  Write-Host "==> Ovoz kutubxonalari o'rnatilmoqda..."
  try { & $venvPy -m pip install -r requirements-voice.txt }
  catch { Write-Host "Ovoz kutubxonalarini o'rnatib bo'lmadi (matnli rejim baribir ishlaydi)." }
}

# Sozlama fayllari
if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "==> .env yaratildi — unga ANTHROPIC_API_KEY ni qo'ying!"
}
if (-not (Test-Path "config.json")) {
  Copy-Item "config.example.json" "config.json"
  Write-Host "==> config.json yaratildi."
}

Write-Host ""
Write-Host "O'rnatish tugadi!" -ForegroundColor Green
Write-Host "   1) .env faylini Notepad'da ochib ANTHROPIC_API_KEY ni qo'ying."
Write-Host "   2) Ishga tushirish:  .\run.ps1   yoki   run.bat"
