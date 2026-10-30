@echo off
setlocal
cd /d "%~dp0"
set "CIV_PYTHON=%GARRISON_PYTHON%"
if not defined CIV_PYTHON set "CIV_PYTHON=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not exist "%CIV_PYTHON%" (
  echo Install Python 3.13 or set GARRISON_PYTHON to its executable.
  pause
  exit /b 1
)
"%CIV_PYTHON%" -B tools\check_environment.py
if errorlevel 1 exit /b 1
"%CIV_PYTHON%" -B toolsuild.py --replace-current
pause
