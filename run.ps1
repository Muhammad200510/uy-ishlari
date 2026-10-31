# Chach-Chu ni ishga tushirish (Windows PowerShell)
# Masalan:  .\run.ps1          (matnli)
#           .\run.ps1 --voice  (ovozli)
Set-Location -Path $PSScriptRoot
$venvPy = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPy) {
  & $venvPy -m chachchu $args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  & python -m chachchu $args
} else {
  & py -m chachchu $args
}
