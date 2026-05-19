# Learn Words

A simple vibe command-line Norwegian vocabulary quiz game.

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
