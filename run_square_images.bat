@echo off
REM Change directory to the folder where your scripts are located
cd /d "%~dp0"

echo Running image_square_processor.py...
python image_square_processor.py

pause
