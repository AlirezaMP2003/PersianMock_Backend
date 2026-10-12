
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from db.database import SessionLocal
from models import Car, Province, City


PROVINCES = {
    "آذربایجان شرقی": [
        "تبریز", "مراغه", "مرند", "اهر"
    ],
    "آذربایجان غربی": [
        "ارومیه", "خوی", "مهاباد", "بوکان"
    ],
    "اردبیل": [
        "اردبیل", "مشگین‌شهر", "پارس‌آباد"
    ],
    "اصفهان": [
        "اصفهان", "کاشان", "نجف‌آباد", "شاهین‌شهر"
    ],
    "البرز": [
        "کرج", "فردیس", "نظرآباد", "هشتگرد"
    ],
    "ایلام": [
        "ایلام", "دهلران", "آبدانان"
    ],
    "بوشهر": [
        "بوشهر", "برازجان", "گناوه", "کنگان"
    ],
    "تهران": [
        "تهران", "ری", "اسلامشهر", "شهریار", "ورامین"
    ],
    "چهارمحال و بختیاری": [
        "شهرکرد", "بروجن", "فارسان"
    ],
    "خراسان جنوبی": [
        "بیرجند", "قائن", "فردوس", "طبس"
    ],
    "خراسان رضوی": [
        "مشهد", "نیشابور", "سبزوار", "تربت حیدریه"
    ],
    "خراسان شمالی": [
        "بجنورد", "شیروان", "اسفراین"
    ],
    "خوزستان": [
        "اهواز", "آبادان", "خرمشهر", "دزفول", "ماهشهر"
    ],
    "زنجان": [
        "زنجان", "ابهر", "خرمدره"
    ],
    "سمنان": [
        "سمنان", "شاهرود", "دامغان", "گرمسار"
    ],
    "سیستان و بلوچستان": [
        "زاهدان", "زابل", "چابهار", "ایرانشهر"
    ],
    "فارس": [
        "شیراز", "مرودشت", "جهرم", "فسا", "کازرون"
    ],
    "قزوین": [
        "قزوین", "الوند", "تاکستان", "آبیک"
    ],
    "قم": [
        "قم", "جعفریه", "کهک"
    ],
    "کردستان": [
        "سنندج", "سقز", "بانه", "مریوان"
    ],
    "کرمان": [
        "کرمان", "رفسنجان", "سیرجان", "جیرفت", "بم"
    ],
    "کرمانشاه": [
        "کرمانشاه", "اسلام‌آباد غرب", "سنقر", "پاوه"
    ],
    "کهگیلویه و بویراحمد": [
        "یاسوج", "دوگنبدان", "دهدشت"
    ],
    "گلستان": [
        "گرگان", "گنبد کاووس", "علی‌آباد کتول"
    ],
    "گیلان": [
        "رشت", "بندر انزلی", "لاهیجان", "آستارا"
    ],
    "لرستان": [
        "خرم‌آباد", "بروجرد", "دورود", "الیگودرز"
    ],
    "مازندران": [
        "ساری", "بابل", "آمل", "قائم‌شهر", "چالوس"
    ],
    "مرکزی": [
        "اراک", "ساوه", "خمین", "محلات"
    ],
    "هرمزگان": [
        "بندرعباس", "میناب", "قشم", "بندر لنگه"
    ],
    "همدان": [
        "همدان", "ملایر", "نهاوند", "تویسرکان"
    ],
    "یزد": [
        "یزد", "میبد", "اردکان", "بافق"
    ],
}


CARS = [
    ("ایران‌خودرو", "دنا"),
    ("ایران‌خودرو", "دنا پلاس"),
    ("ایران‌خودرو", "پژو ۲۰۶"),
    ("ایران‌خودرو", "پژو ۲۰۷"),
    ("ایران‌خودرو", "سمند"),
    ("ایران‌خودرو", "سورن پلاس"),
    ("ایران‌خودرو", "رانا"),
    ("ایران‌خودرو", "تارا"),
    ("سایپا", "پراید ۱۳۱"),
    ("سایپا", "تیبا"),
    ("سایپا", "تیبا ۲"),
    ("سایپا", "ساینا"),
    ("سایپا", "کوییک"),
    ("سایپا", "شاهین"),
    ("پارس‌خودرو", "برلیانس H330"),
    ("پارس‌خودرو", "رنو ساندرو"),
    ("مدیران خودرو", "ام‌وی‌ام X22"),
    ("مدیران خودرو", "ام‌وی‌ام X33"),
    ("مدیران خودرو", "آریزو ۵"),
    ("کرمان موتور", "جک S5"),
    ("کرمان موتور", "جک J4"),
    ("کرمان موتور", "کی‌ام‌سی T8"),
    ("بهمن موتور", "فیدلیتی"),
    ("بهمن موتور", "دیگنیتی"),
]


def seed_provinces_and_cities(db):
    provinces_added = 0
    cities_added = 0

    for province_name, city_names in PROVINCES.items():

        province = db.execute(
            select(Province).where(
                Province.name == province_name
            )
        ).scalar_one_or_none()

        if province is None:
            province = Province(name=province_name)
            db.add(province)
            db.flush()
            provinces_added += 1

        existing_cities = set(
            db.execute(
                select(City.name).where(
                    City.province_id == province.id
                )
            ).scalars().all()
        )

        for city_name in city_names:
            if city_name not in existing_cities:
                db.add(
                    City(
                        name=city_name,
                        province_id=province.id,
                    )
                )
                existing_cities.add(city_name)
                cities_added += 1

    return provinces_added, cities_added


def seed_cars(db):
    cars_added = 0

    existing_cars = set(
        db.execute(
            select(Car.company, Car.name)
        ).all()
    )

    for company, name in CARS:
        if (company, name) not in existing_cars:
            db.add(
                Car(
                    company=company,
                    name=name,
                )
            )
            existing_cars.add((company, name))
            cars_added += 1

    return cars_added


def main():
    db = SessionLocal()

    try:
        provinces_added, cities_added = (
            seed_provinces_and_cities(db)
        )

        cars_added = seed_cars(db)

        db.commit()

        print("Database seeding completed.")
        print(f"Provinces added: {provinces_added}")
        print(f"Cities added: {cities_added}")
        print(f"Cars added: {cars_added}")

    except SQLAlchemyError:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
