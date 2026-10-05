"""Number Guessing Game (Syntecxhub Python Internship - Week 1, Project 2).

Features: random number, higher/lower hints, attempt counting, difficulty
levels, replay, and best (lowest) attempts saved per difficulty.
Run with:  python number_guessing_game.py
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Callable, Dict, Optional

BEST_FILE = Path(__file__).with_name("best_scores.json")

# key -> (name, low, high)
DIFFICULTIES: Dict[str, tuple] = {
    "1": ("Easy", 1, 50),
    "2": ("Medium", 1, 100),
    "3": ("Hard", 1, 500),
}

# ----------------------------------------------------------------------------
# Game logic (testable)
# ----------------------------------------------------------------------------


def choose_secret(low: int, high: int, rng=random) -> int:
    return rng.randint(low, high)


def check_guess(guess: int, secret: int) -> str:
    """Return 'low', 'high' or 'correct'."""
    if guess < secret:
        return "low"
    if guess > secret:
        return "high"
    return "correct"


def parse_guess(text: str, low: int, high: int) -> int:
    try:
        guess = int(text.strip())
    except ValueError:
        raise ValueError("Please enter a whole number.") from None
    if not low <= guess <= high:
        raise ValueError(f"Your guess must be between {low} and {high}.")
    return guess


def max_attempts_needed(low: int, high: int) -> int:
    """Worst case guesses with perfect (binary-search) play."""
    return math.ceil(math.log2(high - low + 1))


def update_best(scores: Dict[str, int], difficulty: str, attempts: int) -> bool:
    """Record attempts if it beats the stored best. Returns True on a new record."""
    if difficulty not in scores or attempts < scores[difficulty]:
        scores[difficulty] = attempts
        return True
    return False


def load_best_scores(path: Path = BEST_FILE) -> Dict[str, int]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return {k: int(v) for k, v in data.items()}
    except (FileNotFoundError, ValueError, AttributeError, TypeError):
        return {}  # missing or corrupt file -> start fresh


def save_best_scores(scores: Dict[str, int], path: Path = BEST_FILE) -> None:
    try:
        Path(path).write_text(json.dumps(scores, indent=2), encoding="utf-8")
    except OSError:
        pass  # saving best score is a nicety; never crash the game


# ----------------------------------------------------------------------------
# Game flow
# ----------------------------------------------------------------------------


def play_round(name: str, low: int, high: int,
               input_fn: Callable[[str], str] = input,
               output_fn: Callable[[str], None] = print,
               rng=random) -> Optional[int]:
    """Play one round. Returns attempts used, or None if the player gave up."""
    secret = choose_secret(low, high, rng)
    attempts = 0
    output_fn(f"\nI'm thinking of a number between {low} and {high}. "
              f"(Perfect play wins in at most {max_attempts_needed(low, high)} guesses.)")
    while True:
        raw = input_fn(f"Guess #{attempts + 1} (or 'q' to give up): ").strip()
        if raw.lower() in {"q", "quit"}:
            output_fn(f"The number was {secret}. Better luck next time!")
            return None
        try:
            guess = parse_guess(raw, low, high)
        except ValueError as err:
            output_fn(f"  ! {err} (not counted as an attempt)")
            continue
        attempts += 1
        result = check_guess(guess, secret)
        if result == "correct":
            output_fn(f"  Correct! You got it in {attempts} attempt{'s' if attempts != 1 else ''}.")
            return attempts
        output_fn("  Too low - go higher." if result == "low" else "  Too high - go lower.")


def show_best(scores: Dict[str, int], output_fn: Callable[[str], None] = print) -> None:
    output_fn("\n--- Best scores (fewest attempts) ---")
    for _, (name, _lo, _hi) in DIFFICULTIES.items():
        value = scores.get(name)
        output_fn(f"  {name:<7}: {value if value is not None else '-'}")


def main(best_path: Path = BEST_FILE,
         input_fn: Callable[[str], str] = input,
         output_fn: Callable[[str], None] = print,
         rng=random) -> None:
    scores = load_best_scores(best_path)
    output_fn("=== SYNTECXHUB NUMBER GUESSING GAME ===")
    try:
        while True:
            output_fn("\nSelect difficulty:")
            for key, (name, low, high) in DIFFICULTIES.items():
                output_fn(f"  {key}. {name} ({low}-{high})")
            output_fn("  4. View best scores\n  5. Quit")
            choice = input_fn("Choice: ").strip()

            if choice in DIFFICULTIES:
                name, low, high = DIFFICULTIES[choice]
                attempts = play_round(name, low, high, input_fn, output_fn, rng)
                if attempts is not None:
                    if update_best(scores, name, attempts):
                        output_fn(f"  New best for {name}: {attempts}!")
                        save_best_scores(scores, best_path)
                    else:
                        output_fn(f"  Best for {name} is still {scores[name]}.")
                again = input_fn("\nPlay again? (y/n): ").strip().lower()
                if again not in {"y", "yes"}:
                    break
            elif choice == "4":
                show_best(scores, output_fn)
            elif choice == "5":
                break
            else:
                output_fn("Invalid choice. Enter 1-5.")
    except (EOFError, KeyboardInterrupt):
        output_fn("")
    output_fn("Thanks for playing!")


if __name__ == "__main__":
    main()
