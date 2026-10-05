1. Syntecxhub_Simple_Calculator:
2. # Syntecxhub Simple Calculator

A command-line calculator built for the Syntecxhub Python Internship (Week 1, Project 1).

## Features
- Addition, subtraction, multiplication, division and clear
- Accepts input like `12 + 5`, `7.5 x 2`, `9 / 3`
- `ans` reuses the previous result
- Input validation and divide-by-zero handling
- Calculation logic separated into functions for testability
- Menu to repeat calculations, view history or exit

## How to Run
```bash
python calculator.py
```

## Run Tests
```bash
python -m unittest -v
```

2. Syntecxhub_Number_Guessing_Game:
3. # Syntecxhub Number Guessing Game

A command-line guessing game built for the Syntecxhub Python Internship (Week 1, Project 2).

## Features
- Random number chosen with Python's `random` module
- Higher/lower hints and attempt counter
- Difficulty levels: Easy (1-50), Medium (1-100), Hard (1-500)
- Replay option and best (lowest) attempts saved per difficulty

## How to Run
```bash
python number_guessing_game.py
```

## Run Tests
```bash
python -m unittest -v
```


3. Syntecxhub_Todo_List_Manager:
4. # Syntecxhub To-Do List Manager

A menu-driven command-line task manager built for the Syntecxhub Python Internship (Week 1, Project 3).

## Features
- Add, view, delete and mark tasks as done
- Tasks are saved to `tasks.json`, so they survive restarts
- File reading/writing with error handling
- Logic separated from input/output
- Extra: tags, due dates, overdue flag and tag filter

## How to Run
```bash
python todo_manager.py
```

## Run Tests
```bash
python -m unittest -v
```
