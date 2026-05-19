# Learn Words

A simple vibe command-line Norwegian vocabulary quiz game.

Now includes a Dash web frontend with a playable quiz and statistics page.

## Prerequisites

- Python 3.8+

## Project Files

- `learn-words.py` - main quiz script
- `norwegian_words.json` - word database (required, but dont look)
- `scores.json` - saved automatically after each session
- `points.txt` - human-readable points summary (updated after each session)


## How to Run

From the project folder, run:

```powershell
python "learn-words.py"
```

On systems where `python` is not available, try:

```powershell
py "learn-words.py"
```

## Notes

- Each session asks 5 random words.
- Progress is stored in `scores.json`.
- A readable summary is written to `points.txt` after each session.
- If `norwegian_words.json` is missing or has fewer than 5 words, the script will show an error.

## Dash Frontend

Create a virtual environment (recommended):

```powershell
python -m venv .venv
```

Activate the environment (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the app:

```powershell
python .\dash_app.py
```

Or run directly with the virtual environment Python executable:

```powershell
.\.venv\Scripts\python.exe .\dash_app.py
```

Open this URL in your browser:

- http://127.0.0.1:8050/

Available pages:

- `/` - play a 5-question session
- `/statistics` - view score, streak, accuracy, and charts
