#!/usr/bin/env bash
# ============================================================
#  setup_env.sh
#  Creates a Python virtual environment ("envi") in the
#  current folder, activates it, and installs everything
#  listed in requirements.txt.
#
#  Usage:
#    chmod +x setup_env.sh
#    ./setup_env.sh
# ============================================================

set -e

PY_EXE=python3

echo
echo "=== Checking Python installation ==="
$PY_EXE --version

echo
echo "=== Upgrading pip ==="
$PY_EXE -m pip install --upgrade pip

echo
echo "=== Creating virtual environment 'envi' ==="
if [ ! -d "envi" ]; then
    $PY_EXE -m venv envi
else
    echo "Virtual environment 'envi' already exists, skipping creation."
fi

echo
echo "=== Activating virtual environment ==="
source envi/bin/activate

echo
echo "=== Upgrading pip inside the virtual environment ==="
python -m pip install --upgrade pip

echo
echo "=== Installing dependencies from requirements.txt ==="
if [ -f "requirements.txt" ]; then
    python -m pip install -r requirements.txt
else
    echo "WARNING: requirements.txt not found in this folder."
fi

echo
echo "=== Installed packages ==="
pip list

echo
echo "============================================================"
echo " Setup complete."
echo " The virtual environment is currently ACTIVE in this shell."
echo " To run your app:      uvicorn main:app --reload"
echo " To re-activate later: source envi/bin/activate"
echo " To freeze deps again: pip freeze > requirements.txt"
echo "============================================================"
