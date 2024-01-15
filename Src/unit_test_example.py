import unittest
from test_my_module import add_numbers

class MyTestCase(unittest.TestCase):
    def test_add_numbers_positive(self):
        result = add_numbers(3,5)
        self.assertEqual(result, 8)  # add assertion here

    def test_add_numbers_negative(self):
        result = add_numbers(9, 7)
        self.assertEqual(result, 8)

    def test_add_numbers_zero(self):
        result = add_numbers(0, 10)
        self.assertEqual(result, 10)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
