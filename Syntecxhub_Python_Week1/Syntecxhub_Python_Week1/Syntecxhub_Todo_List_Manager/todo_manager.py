"""To-Do List Manager (Syntecxhub Python Internship - Week 1, Project 3).

Menu-driven CLI to add / view / delete / complete tasks, persisted to JSON.
Extra credit implemented: tags and due dates.
Logic (pure functions) is separated from I/O (file + console).
Run with:  python todo_manager.py
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

DATA_FILE = Path(__file__).with_name("tasks.json")
Task = Dict[str, object]


class TaskStorageError(Exception):
    """The tasks file could not be read or is corrupt."""


class TaskNotFoundError(Exception):
    """No task with the given id."""


# ----------------------------------------------------------------------------
# File I/O
# ----------------------------------------------------------------------------


def load_tasks(path: Path = DATA_FILE) -> List[Task]:
    """Load tasks. Missing file -> empty list. Corrupt file -> TaskStorageError."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, UnicodeDecodeError) as err:
        raise TaskStorageError(f"Task file is corrupt: {err}") from err
    except OSError as err:
        raise TaskStorageError(f"Cannot read task file: {err}") from err
    if not isinstance(data, list) or not all(isinstance(t, dict) and "id" in t and "title" in t for t in data):
        raise TaskStorageError("Task file has an unexpected format.")
    return data


def save_tasks(tasks: List[Task], path: Path = DATA_FILE) -> None:
    """Write atomically so a crash mid-write cannot destroy existing data."""
    path = Path(path)
    try:
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(tasks, fh, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except OSError as err:
        raise TaskStorageError(f"Cannot save tasks: {err}") from err


# ----------------------------------------------------------------------------
# Business logic (no I/O)
# ----------------------------------------------------------------------------


def parse_due(text: Optional[str]) -> Optional[str]:
    """Validate a YYYY-MM-DD date string. Empty -> None."""
    if not text or not text.strip():
        return None
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise ValueError("Due date must be in YYYY-MM-DD format (e.g. 2026-12-31).") from None


def parse_tags(text: Optional[str]) -> List[str]:
    if not text:
        return []
    seen: List[str] = []
    for tag in text.replace(";", ",").split(","):
        tag = tag.strip().lower().lstrip("#")
        if tag and tag not in seen:
            seen.append(tag)
    return seen


def next_id(tasks: List[Task]) -> int:
    return max((int(t["id"]) for t in tasks), default=0) + 1


def add_task(tasks: List[Task], title: str, tags: Optional[List[str]] = None,
             due: Optional[str] = None) -> Task:
    title = (title or "").strip()
    if not title:
        raise ValueError("Task title cannot be empty.")
    task: Task = {
        "id": next_id(tasks),
        "title": title,
        "done": False,
        "tags": tags or [],
        "due": parse_due(due),
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    tasks.append(task)
    return task


def find_task(tasks: List[Task], task_id: int) -> Task:
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise TaskNotFoundError(f"No task with id {task_id}.")


def mark_done(tasks: List[Task], task_id: int) -> Task:
    task = find_task(tasks, task_id)
    task["done"] = True
    return task


def delete_task(tasks: List[Task], task_id: int) -> Task:
    task = find_task(tasks, task_id)
    tasks.remove(task)
    return task


def filter_tasks(tasks: List[Task], status: str = "all", tag: Optional[str] = None) -> List[Task]:
    """status: 'all' | 'pending' | 'done'. Results sorted by due date (undated last), then id."""
    result = list(tasks)
    if status == "pending":
        result = [t for t in result if not t["done"]]
    elif status == "done":
        result = [t for t in result if t["done"]]
    if tag:
        tag = tag.strip().lower().lstrip("#")
        result = [t for t in result if tag in t.get("tags", [])]
    return sorted(result, key=lambda t: (t.get("due") is None, t.get("due") or "", t["id"]))


def is_overdue(task: Task, today: Optional[date] = None) -> bool:
    due = task.get("due")
    if task["done"] or not due:
        return False
    return date.fromisoformat(str(due)) < (today or date.today())


def format_task(task: Task, today: Optional[date] = None) -> str:
    box = "[x]" if task["done"] else "[ ]"
    line = f"{task['id']:>3}. {box} {task['title']}"
    if task.get("tags"):
        line += "  " + " ".join(f"#{t}" for t in task["tags"])
    if task.get("due"):
        line += f"  (due {task['due']})"
        if is_overdue(task, today):
            line += " OVERDUE"
    return line


# ----------------------------------------------------------------------------
# Command-line interface
# ----------------------------------------------------------------------------

MENU = """
==============================
   SYNTECXHUB TO-DO MANAGER
==============================
 1. Add task
 2. View all tasks
 3. View pending tasks
 4. Mark task as done
 5. Delete task
 6. Filter by tag
 7. Exit
"""


def _ask_id(input_fn: Callable[[str], str], prompt: str) -> int:
    raw = input_fn(prompt).strip()
    try:
        return int(raw)
    except ValueError:
        raise ValueError("Task id must be a number.") from None


def _show(tasks: List[Task], output_fn: Callable[[str], None]) -> None:
    if not tasks:
        output_fn("No tasks to show.")
        return
    for task in tasks:
        output_fn(format_task(task))


def run(path: Path = DATA_FILE,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print) -> None:
    try:
        tasks = load_tasks(path)
    except TaskStorageError as err:
        output_fn(f"Warning: {err}")
        backup = Path(path).with_suffix(".corrupt")
        try:
            os.replace(path, backup)
            output_fn(f"The old file was kept as {backup.name}. Starting with an empty list.")
        except OSError:
            output_fn("Starting with an empty list.")
        tasks = []

    while True:
        output_fn(MENU)
        try:
            choice = input_fn("Choose an option (1-7): ").strip()
        except (EOFError, KeyboardInterrupt):
            choice = "7"
        try:
            if choice == "1":
                title = input_fn("Title: ")
                tags = parse_tags(input_fn("Tags (comma separated, optional): "))
                due = input_fn("Due date YYYY-MM-DD (optional): ")
                task = add_task(tasks, title, tags, due)
                save_tasks(tasks, path)
                output_fn(f"Added task #{task['id']}.")
            elif choice == "2":
                _show(filter_tasks(tasks), output_fn)
            elif choice == "3":
                _show(filter_tasks(tasks, "pending"), output_fn)
            elif choice == "4":
                task = mark_done(tasks, _ask_id(input_fn, "Task id to mark done: "))
                save_tasks(tasks, path)
                output_fn(f"Marked '{task['title']}' as done.")
            elif choice == "5":
                task = delete_task(tasks, _ask_id(input_fn, "Task id to delete: "))
                save_tasks(tasks, path)
                output_fn(f"Deleted '{task['title']}'.")
            elif choice == "6":
                _show(filter_tasks(tasks, tag=input_fn("Tag: ")), output_fn)
            elif choice == "7":
                output_fn("Goodbye!")
                return
            else:
                output_fn("Invalid option. Please enter a number from 1 to 7.")
        except (ValueError, TaskNotFoundError, TaskStorageError) as err:
            output_fn(f"Error: {err}")


if __name__ == "__main__":
    run()
