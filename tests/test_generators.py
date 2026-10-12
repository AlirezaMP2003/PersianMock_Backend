import re

from generators.iranian import (
    CAR_COLORS,
    generate_car_color,
    generate_car_year,
    generate_mobile_number,
    generate_postal_code,
)


def test_car_color():
    for _ in range(100):
        color = generate_car_color()
        assert color in CAR_COLORS


def test_car_year():
    for _ in range(100):
        year = generate_car_year()

        assert isinstance(year, int)
        assert 1380 <= year <= 1405


def test_mobile_number():
    for _ in range(100):
        mobile = generate_mobile_number()

        assert isinstance(mobile, str)
        assert re.fullmatch(r"09[0-9]{9}", mobile)


def test_postal_code():
    for _ in range(100):
        postal_code = generate_postal_code()

        assert isinstance(postal_code, str)
        assert re.fullmatch(
            r"[0-9]{10}",
            postal_code,
        )
