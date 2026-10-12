from typing import Any


SQL_TYPES = {
    "firstname": "VARCHAR(100)",
    "lastname": "VARCHAR(100)",
    "email": "VARCHAR(255)",
    "username": "VARCHAR(255)",
    "gender": "VARCHAR(10)",
    "password": "VARCHAR(1000)",
    "province": "VARCHAR(100)",
    "city": "VARCHAR(100)",
    "car_company": "VARCHAR(100)",
    "car_name": "VARCHAR(100)",
    "car_color": "VARCHAR(100)",
    "car_year": "INTEGER",
    "mobile_number": "VARCHAR(11)",
    "postal_code": "VARCHAR(10)",
}


def get_columns(fields) -> list[str]:
    return ["id"] + [
        field.name
        for field in fields
        if field.type != "id"
    ]


def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"

    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"

    if isinstance(value, (int, float)):
        return str(value)

    return "'" + str(value).replace("'", "''") + "'"


def spreadsheet_safe(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    # Prevent spreadsheet formula execution.
    if value.lstrip().startswith(
        ("=", "+", "-", "@")
    ):
        return "'" + value

    return value
