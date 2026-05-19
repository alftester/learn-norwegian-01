# Learn Words

A simple command-line Norwegian vocabulary quiz game.

## Prerequisites

- Python 3.8+

## Project Files

- `learn-words.py` - main quiz script
- `norwegian_words.json` - word database (required)
- `scores.json` - saved automatically after each session
- `points.txt` - human-readable points summary (updated after each session)

## Setup

1. `norwegian_words.json` is already included with a starter vocabulary list.
2. You can extend it anytime by adding more entries in this format:

```json
[
  { "word": "hei", "description": "hello" },
  { "word": "takk", "description": "thank you" },
  { "word": "ha det", "description": "goodbye" },
  { "word": "vann", "description": "water" },
  { "word": "hus", "description": "house" }
]
```

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
