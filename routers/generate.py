
import random
import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session, joinedload

from db.database import get_db
from models import FirstName, LastName, Car, City
from schemas.generate import GenerateRequest

from generators.iranian import (
    generate_car_color,
    generate_car_year,
    generate_mobile_number,
    generate_postal_code,
)

from exporters.common import get_columns
from exporters.json_exporter import export_json
from exporters.csv_exporter import export_csv
from exporters.sql_exporter import (
    build_create_table_sql,
    export_sql,
)
from exporters.excel_exporter import export_excel


router = APIRouter()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def unique_with_suffix(
    value: str,
    seen: set[str],
    *,
    email: bool = False,
) -> str:

    if value not in seen:
        seen.add(value)
        return value

    if email:
        local, domain = value.rsplit("@", 1)
    else:
        local, domain = value, None

    suffix = random.randint(1, 9999)

    while True:
        if email:
            candidate = f"{local}{suffix}@{domain}"
        else:
            candidate = f"{local}{suffix}"

        if candidate not in seen:
            seen.add(candidate)
            return candidate

        suffix += 1


@router.post("/", tags=["generate"])
def generate_data(
    request: GenerateRequest,
    db: Session = Depends(get_db),
):
    fields = [
        field
        for field in request.fields
        if field.type != "id"
    ]

    requested_types = {
        field.type
        for field in fields
    }

    # Determine the required reference tables.

    needs_firstname = bool(
        requested_types
        & {
            "firstname",
            "email",
            "username",
            "gender",
        }
    )

    needs_lastname = (
        "lastname" in requested_types
    )

    needs_location = bool(
        requested_types
        & {"province", "city"}
    )

    needs_car = bool(
        requested_types
        & {"car_company", "car_name"}
    )

    # Load only required reference datasets.

    first_names = (
        db.query(FirstName).all()
        if needs_firstname
        else []
    )

    last_names = (
        db.query(LastName).all()
        if needs_lastname
        else []
    )

    cities = (
        db.query(City)
        .options(joinedload(City.province))
        .all()
        if needs_location
        else []
    )

    cars = (
        db.query(Car).all()
        if needs_car
        else []
    )

    # Validate reference data availability.

    if needs_firstname and not first_names:
        raise HTTPException(
            status_code=503,
            detail="First name reference table is empty.",
        )

    if needs_lastname and not last_names:
        raise HTTPException(
            status_code=503,
            detail="Last name reference table is empty.",
        )

    if needs_location and not cities:
        raise HTTPException(
            status_code=503,
            detail="City reference table is empty.",
        )

    if needs_car and not cars:
        raise HTTPException(
            status_code=503,
            detail="Car reference table is empty.",
        )

    used_usernames: set[str] = set()
    used_emails: set[str] = set()

    rows: list[dict[str, Any]] = []

    # Generate records.

    for i in range(1, request.count + 1):

        first = (
            random.choice(first_names)
            if needs_firstname
            else None
        )

        last = (
            random.choice(last_names)
            if needs_lastname
            else None
        )

        city = (
            random.choice(cities)
            if needs_location
            else None
        )

        car = (
            random.choice(cars)
            if needs_car
            else None
        )

        values: dict[str, Any] = {
            "id": i,
        }

        # Personal fields

        if first is not None:
            values["firstname"] = first.name
            values["gender"] = first.gender.value

            if "email" in requested_types:
                values["email"] = unique_with_suffix(
                    first.email,
                    used_emails,
                    email=True,
                )

            if "username" in requested_types:
                values["username"] = unique_with_suffix(
                    first.username,
                    used_usernames,
                )

        if last is not None:
            values["lastname"] = last.name

        # Geographic fields

        if city is not None:
            values["city"] = city.name
            values["province"] = city.province.name

        # Vehicle fields

        if car is not None:
            values["car_company"] = car.company
            values["car_name"] = car.name

        # Password

        if "password" in requested_types:
            values["password"] = pwd_context.hash(
                secrets.token_hex(12)
            )

        # Algorithmic fields

        if "car_color" in requested_types:
            values["car_color"] = generate_car_color()

        if "car_year" in requested_types:
            values["car_year"] = generate_car_year()

        if "mobile_number" in requested_types:
            values["mobile_number"] = generate_mobile_number()

        if "postal_code" in requested_types:
            values["postal_code"] = generate_postal_code()

        # Map field types to custom column names.

        row: dict[str, Any] = {
            "id": i,
        }

        for field in fields:
            row[field.name] = values[field.type]

        rows.append(row)

    # Optional SQL DDL.

    ddl = None

    if request.include_create_table:
        ddl = build_create_table_sql(
            request.table_name,
            fields,
        )

    # Dispatch to the appropriate exporter.

    if request.format == "json":
        return export_json(
            rows=rows,
            ddl=ddl,
        )

    if request.format == "sql":
        return export_sql(
            rows=rows,
            table_name=request.table_name,
            fields=fields,
            ddl=ddl,
        )

    columns = get_columns(fields)

    if request.format == "csv":
        return export_csv(
            rows=rows,
            columns=columns,
            table_name=request.table_name,
        )

    if request.format == "excel":
        return export_excel(
            rows=rows,
            columns=columns,
            table_name=request.table_name,
        )

    raise HTTPException(
        status_code=400,
        detail="Unsupported format",
    )
