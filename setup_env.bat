@echo off
REM ============================================================
REM  setup_env.bat
REM  Creates a Python virtual environment ("envi") in the
REM  current folder, activates it, and installs everything
REM  listed in requirements.txt.
REM
REM  Usage:
REM    1. Place this file and requirements.txt in your project
REM       folder.
REM    2. Double-click it, or run it from a terminal:
REM         setup_env.bat
REM ============================================================

setlocal

REM --- Pick the Python launcher ------------------------------------------
REM Change PY_EXE below if you need a specific interpreter, e.g.:
REM set PY_EXE=C:\Users\smt29\AppData\Local\Python\pythoncore-3.14-64\python.exe
set PY_EXE=python

echo.
echo === Checking Python installation ===
%PY_EXE% --version
if errorlevel 1 (
    echo ERROR: Python was not found. Install Python or edit PY_EXE in this script.
    exit /b 1
)

echo.
echo === Upgrading pip ===
%PY_EXE% -m pip install --upgrade pip

echo.
echo === Creating virtual environment "envi" ===
if not exist envi (
    %PY_EXE% -m venv envi
) else (
    echo Virtual environment "envi" already exists, skipping creation.
)

echo.
echo === Activating virtual environment ===
call envi\Scripts\activate.bat

echo.
echo === Upgrading pip inside the virtual environment ===
python -m pip install --upgrade pip

echo.
echo === Installing dependencies from requirements.txt ===
if exist requirements.txt (
    python -m pip install -r requirements.txt
) else (
    echo WARNING: requirements.txt not found in this folder.
)

echo.
echo === Installed packages ===
pip list

echo.
echo ============================================================
echo  Setup complete.
echo  The virtual environment is currently ACTIVE in this window.
echo  To run your app:      uvicorn main:app --reload
echo  To re-activate later: envi\Scripts\activate
echo  To freeze deps again: pip freeze ^> requirements.txt
echo ============================================================

endlocal
