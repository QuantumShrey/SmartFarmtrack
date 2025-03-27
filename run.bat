@echo off
echo Changing to project directory...
d:
cd d:\Projects\Farmtrack

echo Installing dependencies...
pip install -r requirements.txt

echo Starting server...
python app.py

pause
