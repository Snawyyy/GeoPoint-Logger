@echo off
REM GeoPoint Logger Installer Script
echo Installing GeoPoint Logger...

REM Create a virtual environment
python -m venv geopoint_env

REM Activate the virtual environment
call geopoint_env\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Run the application
echo Starting GeoPoint Logger...
python src/main.py

REM Deactivate the environment when done
REM pause
