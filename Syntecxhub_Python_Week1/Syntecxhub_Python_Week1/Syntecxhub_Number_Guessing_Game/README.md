# Syntecxhub Number Guessing Game

Project 2 of the **Syntecxhub Python Programming Internship (Week 1)**.
A command-line guessing game that emphasises loops, conditionals and the `random` module.

## Features
- Random secret number via `random.randint`
- **Higher / lower hints** and **attempt counter**
- **Difficulty levels** (range changes): Easy 1-50, Medium 1-100, Hard 1-500
- **Replay option** and **best (lowest) attempts** per difficulty, saved to `best_scores.json`
- Invalid input (letters, out-of-range) is rejected and does not count as an attempt
- Type `q` to give up a round
- Shows the theoretical best (binary search) guess count for the chosen range

## Run
```bash
python number_guessing_game.py
```
Requires Python 3.9+ (standard library only).

## Test
```bash
python -m unittest -v
```

## Project structure
```
number_guessing_game.py       # logic + CLI
test_number_guessing_game.py  # unit tests
best_scores.json              # created automatically after your first win
README.md
```
