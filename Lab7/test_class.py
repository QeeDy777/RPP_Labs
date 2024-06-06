import pytest
from triangle_class import Triangle, IncorrectTriangleSides


def test_create_triangle():
    triangle = Triangle(3, 4, 5)
    assert triangle.a == 3
    assert triangle.b == 4
    assert triangle.c == 5


def test_triangle_type():
    triangle1 = Triangle(3, 4, 5)
    assert triangle1.triangle_type() == "nonequilateral"

    triangle2 = Triangle(5, 5, 5)
    assert triangle2.triangle_type() == "equilateral"

    triangle3 = Triangle(6, 6, 8)
    assert triangle3.triangle_type() == "isosceles"


def test_perimeter():
    triangle = Triangle(3, 4, 5)
    assert triangle.perimeter() == 12


def test_incorrect_sides_zero():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(0, 1, 2)


def test_incorrect_sides_negative():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(-1, 2, 3)


def test_incorrect_sides_inequality():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 2, 3)


def test_incorrect_sides_type():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, "2", 3)
