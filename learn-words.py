import random
import json
import os
from datetime import datetime

# File paths
WORDS_FILE = "norwegian_words.json"
SCORES_FILE = "scores.json"
POINTS_FILE = "points.txt"

def load_words():
    """Load words and descriptions from file."""
    if not os.path.exists(WORDS_FILE):
        print(f"Error: {WORDS_FILE} not found.")
        return []
    with open(WORDS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_scores():
    """Load scores from file."""
    if not os.path.exists(SCORES_FILE):
        return {"total_words": 0, "sessions": []}
    with open(SCORES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_scores(scores):
    """Save scores to file."""
    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)

def write_points_file(scores, session_score):
    """Write a human-readable points summary to file."""
    sessions = scores.get("sessions", [])
    total_words = scores.get("total_words", 0)
    average = 0.0
    if sessions:
        average = sum(s.get("score", 0) for s in sessions) / len(sessions)

    lines = [
        "Norwegian Word Game - Points Summary",
        "====================================",
        f"Last session score: {session_score}/5",
        f"Total words learned: {total_words}",
        f"Sessions played: {len(sessions)}",
        f"Average score: {average:.2f}/5",
        "",
        "Recent sessions (latest first):"
    ]

    for i, session in enumerate(reversed(sessions[-10:]), 1):
        lines.append(f"{i}. {session.get('date', 'unknown')} - {session.get('score', 0)}/{session.get('max', 5)}")

    with open(POINTS_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")

def play_game():
    """Play the word of the day game."""
    words = load_words()
    if not words or len(words) < 5:
        print("Not enough words in the database. Need at least 5 words.")
        return
    
    # Select 5 random words
    selected_words = random.sample(words, 5)
    correct_answers = 0
    
    print("\n=== Norwegian Word of the Day ===\n")
    
    for i, word_data in enumerate(selected_words, 1):
        word = word_data["word"]
        correct_description = word_data["description"]
        
        # Get wrong descriptions
        wrong_descriptions = random.sample(
            [w["description"] for w in words if w["word"] != word], 2
        )
        
        # Create options
        options = [correct_description] + wrong_descriptions
        random.shuffle(options)
        
        print(f"Word {i}/5: {word}")
        for j, option in enumerate(options, 1):
            print(f"  {j}. {option}")
        
        while True:
            try:
                choice = int(input("Your answer (1-3): "))
                if choice in [1, 2, 3]:
                    if options[choice - 1] == correct_description:
                        print("✓ Correct!\n")
                        correct_answers += 1
                    else:
                        print(f"✗ Wrong! The correct answer is: {correct_description}\n")
                    break
            except ValueError:
                pass
            print("Invalid input. Enter 1, 2, or 3.")
    
    # Update scores
    scores = load_scores()
    scores["total_words"] += correct_answers
    scores["sessions"].append({
        "date": datetime.now().isoformat(),
        "score": correct_answers,
        "max": 5
    })
    save_scores(scores)
    write_points_file(scores, correct_answers)
    
    print(f"\nSession complete! You got {correct_answers}/5 correct.")
    print(f"Total words learned: {scores['total_words']}")
    print(f"Points file updated: {POINTS_FILE}")

if __name__ == "__main__":
    play_game()
