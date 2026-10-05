import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

import todo_manager as todo


class TestLogic(unittest.TestCase):
    def test_add_and_ids(self):
        tasks = []
        a = todo.add_task(tasks, "  Buy milk ", ["home"], "2026-12-31")
        b = todo.add_task(tasks, "Study Python")
        self.assertEqual((a["id"], b["id"]), (1, 2))
        self.assertEqual(a["title"], "Buy milk")
        self.assertFalse(a["done"])
        todo.delete_task(tasks, 1)
        self.assertEqual(todo.add_task(tasks, "x")["id"], 3)  # ids never reused

    def test_validation(self):
        with self.assertRaises(ValueError):
            todo.add_task([], "   ")
        with self.assertRaises(ValueError):
            todo.add_task([], "t", due="31-12-2026")
        with self.assertRaises(ValueError):
            todo.add_task([], "t", due="2026-02-30")

    def test_mark_done_delete_not_found(self):
        tasks = []
        todo.add_task(tasks, "A")
        self.assertTrue(todo.mark_done(tasks, 1)["done"])
        with self.assertRaises(todo.TaskNotFoundError):
            todo.mark_done(tasks, 99)
        with self.assertRaises(todo.TaskNotFoundError):
            todo.delete_task(tasks, 99)
        todo.delete_task(tasks, 1)
        self.assertEqual(tasks, [])

    def test_tags_and_filters(self):
        self.assertEqual(todo.parse_tags("Work, #Urgent; work ,"), ["work", "urgent"])
        tasks = []
        todo.add_task(tasks, "a", ["work"], "2026-05-01")
        todo.add_task(tasks, "b", ["home"])
        todo.add_task(tasks, "c", ["work"], "2026-01-01")
        todo.mark_done(tasks, 3)
        self.assertEqual([t["id"] for t in todo.filter_tasks(tasks, "pending")], [1, 2])
        self.assertEqual([t["id"] for t in todo.filter_tasks(tasks, "done")], [3])
        self.assertEqual([t["id"] for t in todo.filter_tasks(tasks, tag="#Work")], [3, 1])  # due-date order
        self.assertEqual([t["id"] for t in todo.filter_tasks(tasks)], [3, 1, 2])  # undated last

    def test_overdue_and_format(self):
        tasks = []
        t = todo.add_task(tasks, "Pay bill", ["money"], "2026-01-01")
        self.assertTrue(todo.is_overdue(t, date(2026, 2, 1)))
        self.assertFalse(todo.is_overdue(t, date(2025, 12, 1)))
        self.assertIn("OVERDUE", todo.format_task(t, date(2026, 2, 1)))
        todo.mark_done(tasks, 1)
        self.assertFalse(todo.is_overdue(t, date(2026, 2, 1)))
        self.assertIn("[x]", todo.format_task(t))


class TestStorage(unittest.TestCase):
    def test_roundtrip_and_missing(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tasks.json"
            self.assertEqual(todo.load_tasks(path), [])
            tasks = []
            todo.add_task(tasks, "Persist me", ["t"])
            todo.save_tasks(tasks, path)
            self.assertEqual(todo.load_tasks(path), tasks)

    def test_corrupt_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tasks.json"
            path.write_text("{ not json")
            with self.assertRaises(todo.TaskStorageError):
                todo.load_tasks(path)
            path.write_text(json.dumps({"a": 1}))
            with self.assertRaises(todo.TaskStorageError):
                todo.load_tasks(path)


class TestCLI(unittest.TestCase):
    def run_script(self, path, inputs):
        it = iter(inputs)
        out = []
        todo.run(path, lambda _p: next(it), out.append)
        return "\n".join(out)

    def test_tasks_survive_restart(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tasks.json"
            self.run_script(path, ["1", "Write report", "work", "2099-01-01", "7"])
            text = self.run_script(path, ["2", "4", "1", "3", "7"])
            self.assertIn("Write report", text)
            self.assertIn("Marked 'Write report' as done.", text)
            self.assertIn("No tasks to show.", text)  # nothing pending after marking done

    def test_error_messages(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tasks.json"
            text = self.run_script(path, ["5", "abc", "4", "42", "1", "", "", "", "9", "7"])
            self.assertIn("Task id must be a number.", text)
            self.assertIn("No task with id 42.", text)
            self.assertIn("Task title cannot be empty.", text)
            self.assertIn("Invalid option", text)

    def test_corrupt_file_recovery(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tasks.json"
            path.write_text("garbage")
            text = self.run_script(path, ["7"])
            self.assertIn("Warning", text)
            self.assertTrue(path.with_suffix(".corrupt").exists())


if __name__ == "__main__":
    unittest.main()
