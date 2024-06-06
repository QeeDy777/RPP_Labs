class IncorrectTriangleSides(Exception):
    pass


def get_triangle_type(a, b, c):
    if not (isinstance(a, (int, float)) and isinstance(b, (int, float)) and isinstance(c, (int, float))):
        raise IncorrectTriangleSides("Стороны треугольника должны быть числами")
    if a <= 0 or b <= 0 or c <= 0:
        raise IncorrectTriangleSides("Стороны треугольника должны быть положительными числами")
    if a + b <= c or a + c <= b or b + c <= a:
        raise IncorrectTriangleSides("Стороны не удовлетворяют неравенству треугольника")
    if a == b == c:
        return "equilateral"
    elif a == b or a == c or b == c:
        return "isosceles"
    else:
        return "nonequilateral"
