@echo off
echo Starting TCP File Transfer GUI...
echo.

REM Try python3 first
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    echo Using python3...
    python3 launch_gui.py
    goto end
)

REM Try python
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Using python...
    python launch_gui.py
    goto end
)

REM Try py launcher
py --version >nul 2>&1
if %errorlevel% == 0 (
    echo Using py launcher...
    py launch_gui.py
    goto end
)

echo ERROR: Python not found!
echo Please install Python 3.6+ from https://python.org
echo Make sure to add Python to your PATH during installation.

:end
pause