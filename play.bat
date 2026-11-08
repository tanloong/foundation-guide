@echo off
chcp 65001 >nul
cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
    echo.
    echo This game needs uv to run.
    echo Install it from https://docs.astral.sh/uv/ and try again.
    echo.
    pause
    exit /b 1
)

uv run python -m foundation_guide %*

echo.
pause
