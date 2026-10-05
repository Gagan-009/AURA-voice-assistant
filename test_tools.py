import unittest
from tools import get_current_time, calculate, create_client_tools


class TestAuraTools(unittest.TestCase):
    def test_get_current_time(self):
        result = get_current_time()
        self.assertIsInstance(result, str)
        self.assertIn("The current local date and time is", result)
        # Should include day and year
        self.assertIn("202", result)

    def test_calculate_basic_arithmetic(self):
        self.assertIn("4", calculate("2 + 2"))
        self.assertIn("20", calculate("5 * 4"))
        self.assertIn("7", calculate("10 - 3"))
        self.assertIn("5", calculate("25 / 5"))
        self.assertIn("1", calculate("10 % 3"))

    def test_calculate_precedence_and_parentheses(self):
        self.assertIn("14", calculate("2 + 3 * 4"))
        self.assertIn("20", calculate("(2 + 3) * 4"))
        self.assertIn("50", calculate("((12 * 5) + 40) / 2"))

    def test_calculate_decimals_and_negatives(self):
        self.assertIn("7.5", calculate("15 / 2"))
        self.assertIn("-5", calculate("-10 + 5"))
        self.assertIn("-15", calculate("-5 * 3"))

    def test_calculate_powers(self):
        self.assertIn("8", calculate("2 ** 3"))
        self.assertIn("8", calculate("2 ^ 3"))  # Caret support
        self.assertIn("1024", calculate("2 ^ 10"))

    def test_calculate_division_by_zero(self):
        res = calculate("10 / 0")
        self.assertTrue(res.startswith("Error:"))
        self.assertIn("zero", res.lower())

    def test_calculate_security_rejections(self):
        # Function calls
        self.assertTrue(calculate("__import__('os').system('ls')").startswith("Error:"))
        self.assertTrue(calculate("abs(-5)").startswith("Error:"))
        self.assertTrue(calculate("print('hello')").startswith("Error:"))

        # Variable access
        self.assertTrue(calculate("x + 1").startswith("Error:"))

        # Syntax errors / invalid inputs
        self.assertTrue(calculate("2 ++* 3").startswith("Error:"))
        self.assertTrue(calculate("").startswith("Error:"))

    def test_create_client_tools_registration(self):
        tools = create_client_tools()
        self.assertIn("get_current_time", tools.tools)
        self.assertIn("calculate", tools.tools)
        tools.stop()


if __name__ == "__main__":
    unittest.main()
