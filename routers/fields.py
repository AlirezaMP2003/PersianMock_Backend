from fastapi import APIRouter

from schemas.generate import ALLOWED_FIELD_TYPES

router = APIRouter()

ALL_FIELDS = [
    "id",
    "firstname",
    "lastname",
    "email",
    "username",
    "password",
    "gender",
    "province",
    "city",
    "car_company",
    "car_name",
    "car_color",
    "car_year",
    "mobile_number",
    "postal_code",
]


@router.get("/")
def get_fields():
    return {
        "fields": [
            field
            for field in ALL_FIELDS
            if field in ALLOWED_FIELD_TYPES
        ]
    }
