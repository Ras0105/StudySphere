# Project Setup

Follow these steps to get the project running locally after cloning this repo.

## 1. Install Python

Make sure you have Python 3.10+ installed.

- **Windows:** Download from https://www.python.org/downloads/ — during install, check the box **"Add Python to PATH"**.
- **Mac:** Install via [Homebrew](https://brew.sh): `brew install python`
- **Linux:** Usually pre-installed. If not: `sudo apt install python3 python3-venv python3-pip`

Verify it worked:
```
python --version
```
(On Mac/Linux you may need `python3 --version` instead.)

## 2. Clone the repo

```
git clone <your-repo-url>
cd <repo-folder-name>
```

## 3. Install dependencies

This creates a virtual environment (`envi`) and installs everything listed in `requirement.txt` automatically.

**Windows:**
```
setup_env.bat
```
Just double-click the file in File Explorer, or run it from a terminal (Command Prompt / PowerShell) inside the project folder.

**Mac/Linux:**
```
chmod +x setup_env.sh
./setup_env.sh
```

Wait for it to finish — it will print a list of installed packages at the end.

## 4. Activate the environment (for future sessions)

Once setup has run the first time, you don't need to run the script again. Next time you open the project, just activate the existing environment:

**Windows:**
```
envi\Scripts\activate
```

**Mac/Linux:**
```
source envi/bin/activate
```

You'll know it worked because your terminal prompt will show `(envi)` at the start.

## 5. Run the app

```
uvicorn main:app --reload
```

Then open the URL shown in the terminal (usually `http://127.0.0.1:8000`).

## Troubleshooting

- **"python is not recognized"** (Windows) → Python wasn't added to PATH during install. Reinstall Python and check that box, or use the full path to `python.exe`.
- **"Permission denied" running setup_env.sh** (Mac/Linux) → Run `chmod +x setup_env.sh` first.
- **Still stuck?** Delete the `envi` folder and re-run the setup script.
