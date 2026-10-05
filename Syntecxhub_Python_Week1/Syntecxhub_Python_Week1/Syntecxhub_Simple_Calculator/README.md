# Syntecxhub Simple Calculator

Project 1 of the **Syntecxhub Python Programming Internship (Week 1)**.
A command-line calculator with input validation, divide-by-zero handling, a repeat-or-exit menu, and unit tests.

## Features
- Operations: `+`, `-`, `*` (also `x`, `×`), `/` (also `÷`), plus **clear**
- Natural input: `12 + 5`, `7.5 x 2`, `9 ÷ 3`, `5 - -3`
- `ans` keyword reuses the previous result (e.g. `ans * 2`)
- Validates input (bad numbers/operators, `nan`, `inf`) and handles **divide-by-zero**
- Calculation history, and a **Clear** option (screen, history, stored result)
- Logic (`add`, `subtract`, `multiply`, `divide`, `calculate`, `parse_expression`) is separated from I/O for testability
- Menu-driven: repeat calculations until you choose Exit

## Run
```bash
python calculator.py
```
Requires Python 3.9+ (standard library only).

## Test
```bash
python -m unittest -v
```

## Example
```
calc> 10 / 4
  10 / 4 = 2.5
calc> ans * 2
  2.5 * 2 = 5
calc> 5 / 0
Error: Cannot divide by zero.
```

## Project structure
```
calculator.py        # logic + CLI
test_calculator.py   # unit tests
README.md
```
