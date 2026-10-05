# Syntecxhub To-Do List Manager

Project 3 of the **Syntecxhub Python Programming Internship (Week 1)**.
A menu-driven CLI to manage tasks, saved to a JSON file so they survive restarts.

## Features
- **Add / view / delete / mark done** tasks
- **Persistence** in `tasks.json` (created automatically); atomic writes prevent data loss
- **Error handling**: missing file, corrupt file (backed up as `tasks.corrupt`), bad ids, empty titles, invalid dates
- **Separation of concerns**: pure logic functions (`add_task`, `mark_done`, `delete_task`, `filter_tasks`...) vs I/O (`load_tasks`, `save_tasks`, CLI)
- **Extra credit**: tags (`#work`), due dates (`YYYY-MM-DD`), overdue flag, sorted by due date, filter by tag

## Run
```bash
python todo_manager.py
```
Requires Python 3.9+ (standard library only).

## Test
```bash
python -m unittest -v
```

## Example
```
  1. [ ] Write report  #work  (due 2026-12-31)
  2. [x] Buy milk  #home
```

## Project structure
```
todo_manager.py        # logic + file I/O + CLI
test_todo_manager.py   # unit tests
tasks.json             # created automatically
README.md
```
