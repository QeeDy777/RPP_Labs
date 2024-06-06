import unittest
from triangle_func import get_triangle_type, IncorrectTriangleSides


class TestTriangleFunc(unittest.TestCase):
    def test_nonequilateral(self):
        self.assertEqual(get_triangle_type(3, 4, 5), "nonequilateral")

    def test_equilateral(self):
        self.assertEqual(get_triangle_type(5, 5, 5), "equilateral")

    def test_isosceles(self):
        self.assertEqual(get_triangle_type(6, 6, 8), "isosceles")

    def test_incorrect_sides_zero(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(0, 1, 2)

    def test_incorrect_sides_negative(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-1, 2, 3)

    def test_incorrect_sides_inequality(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 2, 3)

    def test_incorrect_sides_type(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, "2", 3)
