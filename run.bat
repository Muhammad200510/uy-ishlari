@echo off
rem Chach-Chu ni ishga tushirish (Windows)
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m chachchu %*
) else (
  python -m chachchu %*
)
