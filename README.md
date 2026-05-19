# Learn Words

A Norwegian vocabulary quiz that can run in two ways:

- Command-line quiz (CLI)
- Dash web app with a statistics page

## Run Modes

- CLI mode: run `learn-words.py` directly. No extra libraries are required.
- Dash mode: run `dash_app.py`. Requires installing libraries from `requirements.txt`.

## Prerequisites

- Python 3.8+

## Quick Start (CLI)

No extra libraries are needed for CLI mode.

```powershell
python .\learn-words.py
```

If `python` is not available:

```powershell
py .\learn-words.py
```

## Quick Start (Dash Web App)

This mode requires dependencies from `requirements.txt`.

Create a virtual environment (recommended):

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the Dash app:

```powershell
python .\dash_app.py
```

Or run directly with the virtual environment Python executable:

```powershell
.\.venv\Scripts\python.exe .\dash_app.py
```

Open in browser:

- http://127.0.0.1:8050/

Available pages:

- `/` - play a 5-question session
- `/statistics` - view score, streak, accuracy, and charts

## Project Files

- `learn-words.py` - main quiz script
- `dash_app.py` - Dash web app
- `norwegian_words.json` - word database (required, but dont look)
- `scores.json` - saved automatically after each session
- `points.txt` - human-readable points summary (updated after each session)
- `report-stats.py` - optional text statistics report generator
- `statistics.txt` - output from `report-stats.py`

## Notes

- Each session asks 5 random words.
- Progress is stored in `scores.json`.
- A readable summary is written to `points.txt` after each session.
- If `norwegian_words.json` is missing or has fewer than 5 words, the script will show an error.
