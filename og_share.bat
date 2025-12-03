@echo off
REM run_share_v2.bat — starts the share web app v2 and opens the browser
SET PYTHON_EXE=python
REM If you want to use a specific python executable, edit PYTHON_EXE above.
"%PYTHON_EXE%" "%~dp0share_web_app_v2.py" runserver --open
pause
