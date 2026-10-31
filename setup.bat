@echo off
rem Chach-Chu - Windows o'rnatish (ikki marta bosib ishga tushirish mumkin)
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
echo.
pause
