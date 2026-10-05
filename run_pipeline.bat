@echo off
python src\generate_demo_data.py
if errorlevel 1 exit /b 1
python src\build_database.py
if errorlevel 1 exit /b 1
echo.
echo Pipeline complete.
echo Run: streamlit run dashboard\app.py
