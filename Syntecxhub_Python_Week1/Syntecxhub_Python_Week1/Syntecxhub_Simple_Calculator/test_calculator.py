import unittest

import calculator as calc


class TestOperations(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(calc.add(2, 3), 5)
        self.assertEqual(calc.subtract(2, 3), -1)
        self.assertEqual(calc.multiply(4, 2.5), 10)
        self.assertEqual(calc.divide(9, 3), 3)

    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            calc.divide(1, 0)
        with self.assertRaises(ZeroDivisionError):
            calc.calculate(5, "/", 0)

    def test_operator_aliases(self):
        self.assertEqual(calc.calculate(6, "x", 3), 18)
        self.assertEqual(calc.calculate(6, "×", 3), 18)
        self.assertEqual(calc.calculate(6, "÷", 3), 2)
        self.assertEqual(calc.calculate(6, "−", 3), 3)

    def test_bad_operator(self):
        with self.assertRaises(ValueError):
            calc.calculate(1, "^", 2)

    def test_overflow(self):
        with self.assertRaises(OverflowError):
            calc.calculate(1e308, "*", 10)


class TestParsing(unittest.TestCase):
    def test_parse_number(self):
        self.assertEqual(calc.parse_number(" 3.5 "), 3.5)
        self.assertEqual(calc.parse_number("ans", 7), 7)
        for bad in ["abc", "", "nan", "inf"]:
            with self.assertRaises(ValueError):
                calc.parse_number(bad)
        with self.assertRaises(ValueError):
            calc.parse_number("ans")

    def test_parse_expression(self):
        self.assertEqual(calc.parse_expression("12 + 5"), (12, "+", 5))
        self.assertEqual(calc.parse_expression("5-3"), (5, "-", 3))
        self.assertEqual(calc.parse_expression("5 - -3"), (5, "-", -3))
        self.assertEqual(calc.parse_expression("2 x 4"), (2, "*", 4))
        self.assertEqual(calc.parse_expression("ans / 2", 10), (10, "/", 2))

    def test_parse_expression_invalid(self):
        for bad in ["", "12", "12 +", "a + b", "1 ++ 2", "1 + 2 + 3"]:
            with self.assertRaises(ValueError):
                calc.parse_expression(bad)

    def test_format_result(self):
        self.assertEqual(calc.format_result(5.0), "5")
        self.assertEqual(calc.format_result(0.1 + 0.2), "0.3")
        self.assertEqual(calc.format_result(2.5), "2.5")


class TestMenuLoop(unittest.TestCase):
    def run_script(self, inputs):
        it = iter(inputs)
        out = []
        calc.run(lambda _p: next(it), out.append)
        return "\n".join(out)

    def test_full_session(self):
        text = self.run_script(["1", "10 / 4", "ans * 2", "5 / 0", "oops", "back", "2", "3", "2", "4"])
        self.assertIn("10 / 4 = 2.5", text)
        self.assertIn("2.5 * 2 = 5", text)
        self.assertIn("Cannot divide by zero", text)
        self.assertIn("Invalid input", text)
        self.assertIn("History is empty.", text)  # after clear
        self.assertIn("Goodbye!", text)

    def test_invalid_menu_option(self):
        self.assertIn("Invalid option", self.run_script(["9", "4"]))


if __name__ == "__main__":
    unittest.main()
