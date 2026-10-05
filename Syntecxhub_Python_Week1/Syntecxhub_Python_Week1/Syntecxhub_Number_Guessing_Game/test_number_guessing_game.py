import random
import tempfile
import unittest
from pathlib import Path

import number_guessing_game as game


class FixedRng:
    def __init__(self, value):
        self.value = value

    def randint(self, a, b):
        return self.value


class TestLogic(unittest.TestCase):
    def test_choose_secret_in_range(self):
        rng = random.Random(1)
        for _ in range(200):
            self.assertTrue(1 <= game.choose_secret(1, 10, rng) <= 10)

    def test_check_guess(self):
        self.assertEqual(game.check_guess(3, 5), "low")
        self.assertEqual(game.check_guess(7, 5), "high")
        self.assertEqual(game.check_guess(5, 5), "correct")

    def test_parse_guess(self):
        self.assertEqual(game.parse_guess(" 42 ", 1, 100), 42)
        for bad in ["abc", "", "3.5", "0", "101"]:
            with self.assertRaises(ValueError):
                game.parse_guess(bad, 1, 100)

    def test_max_attempts(self):
        self.assertEqual(game.max_attempts_needed(1, 100), 7)
        self.assertEqual(game.max_attempts_needed(1, 50), 6)

    def test_update_best(self):
        scores = {}
        self.assertTrue(game.update_best(scores, "Easy", 8))
        self.assertFalse(game.update_best(scores, "Easy", 9))
        self.assertTrue(game.update_best(scores, "Easy", 5))
        self.assertEqual(scores["Easy"], 5)

    def test_best_score_persistence(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "best.json"
            self.assertEqual(game.load_best_scores(path), {})
            game.save_best_scores({"Easy": 4}, path)
            self.assertEqual(game.load_best_scores(path), {"Easy": 4})
            path.write_text("not json")
            self.assertEqual(game.load_best_scores(path), {})


class TestFlow(unittest.TestCase):
    def test_round_hints_and_attempts(self):
        inputs = iter(["abc", "500", "10", "90", "50"])  # 2 invalid, then 3 real guesses
        out = []
        attempts = game.play_round("Medium", 1, 100, lambda _p: next(inputs), out.append, FixedRng(50))
        self.assertEqual(attempts, 3)
        text = "\n".join(out)
        self.assertIn("Too low", text)
        self.assertIn("Too high", text)
        self.assertIn("3 attempts", text)

    def test_give_up(self):
        inputs = iter(["q"])
        out = []
        self.assertIsNone(game.play_round("Easy", 1, 50, lambda _p: next(inputs), out.append, FixedRng(7)))
        self.assertIn("The number was 7", "\n".join(out))

    def test_full_game_saves_best(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "best.json"
            inputs = iter(["1", "25", "n"])  # Easy, guess correctly first try, don't replay
            out = []
            game.main(path, lambda _p: next(inputs), out.append, FixedRng(25))
            self.assertEqual(game.load_best_scores(path), {"Easy": 1})
            self.assertIn("Thanks for playing!", out[-1])


if __name__ == "__main__":
    unittest.main()
