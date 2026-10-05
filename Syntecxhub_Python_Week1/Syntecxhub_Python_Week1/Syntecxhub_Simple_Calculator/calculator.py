"""Simple command-line calculator (Syntecxhub Python Internship - Week 1, Project 1).

Calculation logic (pure functions) is kept separate from input/output so it
can be unit-tested easily. Run with:  python calculator.py
"""
from __future__ import annotations

import math
import re
import sys
from typing import Callable, Optional, Tuple

# ----------------------------------------------------------------------------
# Calculation logic (no input/print here -> easy to test)
# ----------------------------------------------------------------------------


def add(a: float, b: float) -> float:
    return a + b


def subtract(a: float, b: float) -> float:
    return a - b


def multiply(a: float, b: float) -> float:
    return a * b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b


OPERATIONS: dict[str, Callable[[float, float], float]] = {
    "+": add,
    "-": subtract,
    "*": multiply,
    "/": divide,
}

# Accept friendly symbols too (x, ×, ÷, −) and map them to the canonical ones.
OPERATOR_ALIASES = {
    "+": "+", "-": "-", "−": "-",
    "*": "*", "x": "*", "X": "*", "×": "*",
    "/": "/", "÷": "/",
}

_NUMBER = r"(ans|[+-]?(?:\d+\.?\d*|\.\d+))"
_EXPRESSION = re.compile(rf"^\s*{_NUMBER}\s*([+\-−*/xX×÷])\s*{_NUMBER}\s*$", re.IGNORECASE)


def normalize_operator(op: str) -> str:
    """Convert any supported operator symbol to one of + - * /."""
    if op not in OPERATOR_ALIASES:
        raise ValueError(f"Unsupported operator: {op!r}. Use + - * /")
    return OPERATOR_ALIASES[op]


def calculate(a: float, op: str, b: float) -> float:
    """Apply `op` to a and b. Raises ValueError / ZeroDivisionError / OverflowError."""
    result = OPERATIONS[normalize_operator(op)](a, b)
    if not math.isfinite(result):
        raise OverflowError("Result is too large to represent.")
    return result


def parse_number(text: str, last_result: Optional[float] = None) -> float:
    """Turn text into a float. The word 'ans' means the previous result."""
    text = text.strip()
    if text.lower() == "ans":
        if last_result is None:
            raise ValueError("There is no previous result yet to use as 'ans'.")
        return last_result
    try:
        value = float(text)
    except ValueError:
        raise ValueError(f"'{text}' is not a valid number.") from None
    if not math.isfinite(value):
        raise ValueError(f"'{text}' is not a valid number.")
    return value


def parse_expression(text: str, last_result: Optional[float] = None) -> Tuple[float, str, float]:
    """Parse an expression like '12 + 5' or 'ans * 2' into (a, op, b)."""
    match = _EXPRESSION.match(text)
    if not match:
        raise ValueError("Invalid input. Use the form: number operator number (e.g. 12 + 5).")
    left, op, right = match.groups()
    return parse_number(left, last_result), normalize_operator(op), parse_number(right, last_result)


def format_result(value: float) -> str:
    """Show whole numbers without '.0' and trim floating-point noise."""
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    return f"{value:.10g}"


# ----------------------------------------------------------------------------
# Command-line interface
# ----------------------------------------------------------------------------

MENU = """
==============================
   SYNTECXHUB CALCULATOR
==============================
 1. New calculation
 2. View history
 3. Clear (screen, history, ans)
 4. Exit
"""


def clear_screen(output_fn: Callable[[str], None] = print) -> None:
    if sys.stdout.isatty():
        output_fn("\033[2J\033[H")


def run(input_fn: Callable[[str], str] = input, output_fn: Callable[[str], None] = print) -> None:
    """Menu loop. input_fn/output_fn are injectable so the loop can be tested."""
    last_result: Optional[float] = None
    history: list[str] = []

    while True:
        output_fn(MENU)
        try:
            choice = input_fn("Choose an option (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            choice = "4"

        if choice == "1":
            output_fn("Enter e.g.  12 + 5 | 7.5 x 2 | 9 / 3 | ans - 4   (type 'back' to return)")
            while True:
                try:
                    raw = input_fn("calc> ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if raw.lower() in {"back", "b", ""}:
                    break
                if raw.lower() in {"clear", "c"}:
                    last_result, history = None, []
                    clear_screen(output_fn)
                    output_fn("Cleared.")
                    continue
                try:
                    a, op, b = parse_expression(raw, last_result)
                    result = calculate(a, op, b)
                except ZeroDivisionError as err:
                    output_fn(f"Error: {err}")
                except (ValueError, OverflowError) as err:
                    output_fn(f"Error: {err}")
                else:
                    last_result = result
                    line = f"{format_result(a)} {op} {format_result(b)} = {format_result(result)}"
                    history.append(line)
                    output_fn(f"  {line}")
        elif choice == "2":
            if history:
                output_fn("--- History ---")
                for i, line in enumerate(history, 1):
                    output_fn(f"{i}. {line}")
            else:
                output_fn("History is empty.")
        elif choice == "3":
            last_result, history = None, []
            clear_screen(output_fn)
            output_fn("Cleared screen, history and stored result.")
        elif choice == "4":
            output_fn("Goodbye!")
            return
        else:
            output_fn("Invalid option. Please enter 1, 2, 3 or 4.")


if __name__ == "__main__":
    run()
