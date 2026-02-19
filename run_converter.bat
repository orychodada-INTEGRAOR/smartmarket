@echo off
chcp 65001 > nul
title מערכת המרת מחירונים

echo ============================================================
echo    מערכת המרת מחירונים - Price Converter
echo ============================================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python לא מותקן במחשב!
    echo.
    echo אנא התקן Python מ: https://www.python.org/downloads/
    echo.
    pause
    exit
)

REM Check if openpyxl is installed
python -c "import openpyxl" > nul 2>&1
if errorlevel 1 (
    echo 📦 מתקין חבילות נדרשות...
    python -m pip install openpyxl --quiet
    echo ✅ ההתקנה הושלמה!
    echo.
)

REM Run the converter
python price_converter.py

pause
