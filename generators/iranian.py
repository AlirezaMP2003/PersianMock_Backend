import random

CAR_COLORS = (
    "سفید",
    "مشکی",
    "نقره‌ای",
    "خاکستری",
    "نوک‌مدادی",
    "آبی",
    "قرمز",
    "زرشکی",
    "سبز",
    "قهوه‌ای",
)


def generate_car_color() -> str:
    return random.choice(CAR_COLORS)


def generate_car_year() -> int:
    return random.randint(1395, 1405)


def generate_mobile_number() -> str:
    return "09" + "".join(
        str(random.randint(0, 9))
        for _ in range(9)
    )


def generate_postal_code() -> str:
    return "".join(
        str(random.randint(0, 9))
        for _ in range(10)
    )
