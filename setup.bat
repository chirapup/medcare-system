@echo off
echo ================================
echo MedCare System Setup
echo ================================
echo.

cd backend

echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo To start the server:
echo   1. cd backend
echo   2. venv\Scripts\activate
echo   3. python app.py
echo.
echo Then open frontend/index.html in your browser
echo.
pause