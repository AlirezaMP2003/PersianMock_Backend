import csv
import io
import random
import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session, joinedload

from db.database import get_db
from models import FirstName, LastName, Car, City
from schemas.generate import GenerateRequest, GenerateResponse

from generators.iranian import (
    generate_car_color,
    generate_car_year,
    generate_mobile_number,
    generate_postal_code,
)


router = APIRouter()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


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


def build_create_table_sql(table_name, fields):
    columns = ['"id" INTEGER PRIMARY KEY']

    for field in fields:
        if field.type == "id":
            continue

        sql_type = SQL_TYPES[field.type]
        column_name = quote_identifier(field.name)

        columns.append(
            f"{column_name} {sql_type}"
        )

    columns_sql = ", ".join(columns)

    return (
        f"CREATE TABLE IF NOT EXISTS "
        f"{quote_identifier(table_name)} "
        f"({columns_sql});"
    )


def spreadsheet_safe(value: Any) -> Any:
    if (
        isinstance(value, str)
        and value.lstrip().startswith(
            ("=", "+", "-", "@")
        )
    ):
        return "'" + value

    return value


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

    # Determine which reference tables are needed.

    needs_firstname = bool(
        requested_types
        & {
            "firstname",
            "email",
            "username",
            "gender",
        }
    )

    needs_lastname = "lastname" in requested_types

    needs_location = bool(
        requested_types & {"province", "city"}
    )

    needs_car = bool(
        requested_types & {"car_company", "car_name"}
    )

    # Load only the required reference data.

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

    # Check that the required tables have data.

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

    # Generate synthetic records.

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

        # A city and its province come from
        # the same reference relationship.

        city = (
            random.choice(cities)
            if needs_location
            else None
        )

        # Company and model come from
        # the same car record.

        car = (
            random.choice(cars)
            if needs_car
            else None
        )

        values: dict[str, Any] = {
            "id": i,
        }

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

        if city is not None:
            values["city"] = city.name
            values["province"] = city.province.name

        if car is not None:
            values["car_company"] = car.company
            values["car_name"] = car.name

        if "password" in requested_types:
            values["password"] = pwd_context.hash(
                secrets.token_hex(12)
            )

        
        # Generate algorithmic Iranian data.

        if "car_color" in requested_types:
            values["car_color"] = generate_car_color()

        if "car_year" in requested_types:
            values["car_year"] = generate_car_year()

        if "mobile_number" in requested_types:
            values["mobile_number"] = generate_mobile_number()

        if "postal_code" in requested_types:
            values["postal_code"] = generate_postal_code()


        row: dict[str, Any] = {
            "id": i,
        }

        for field in fields:
            row[field.name] = values[field.type]

        rows.append(row)

    # Build optional CREATE TABLE statement.

    ddl = None

    if request.include_create_table:
        ddl = build_create_table_sql(
            request.table_name,
            fields,
        )

    columns = ["id"] + [
        field.name
        for field in fields
    ]

    # JSON output.

    if request.format == "json":
        return GenerateResponse(
            data=rows,
            ddl=ddl,
            format="json",
        ).model_dump()

    # SQL output.

    if request.format == "sql":

        sql_rows = []

        for row in rows:
            values_sql = ", ".join(
                sql_literal(row[column])
                for column in columns
            )

            sql_rows.append(
                f"({values_sql})"
            )

        columns_sql = ", ".join(
            quote_identifier(column)
            for column in columns
        )

        insert_sql = (
            f"INSERT INTO "
            f"{quote_identifier(request.table_name)} "
            f"({columns_sql}) VALUES\n"
            + ",\n".join(sql_rows)
            + ";"
        )

        sql_text = "\n\n".join(
            part
            for part in [ddl, insert_sql]
            if part
        )

        return Response(
            content=sql_text,
            media_type="text/plain; charset=utf-8",
        )

    # CSV output.

    if request.format == "csv":

        output = io.StringIO(newline="")
        writer = csv.writer(output)

        writer.writerow(columns)

        for row in rows:
            writer.writerow([
                spreadsheet_safe(row[column])
                for column in columns
            ])

        csv_bytes = output.getvalue().encode(
            "utf-8-sig"
        )

        return StreamingResponse(
            io.BytesIO(csv_bytes),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition":
                f'attachment; filename="{request.table_name}.csv"'
            },
        )

    # Excel output.

    if request.format == "excel":

        try:
            import pandas as pd
            import openpyxl

        except ImportError as exc:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Excel export requires "
                    "pandas and openpyxl."
                ),
            ) from exc

        safe_rows = [
            {
                column: spreadsheet_safe(row[column])
                for column in columns
            }
            for row in rows
        ]

        dataframe = pd.DataFrame(
            safe_rows,
            columns=columns,
        )

        output = io.BytesIO()

        dataframe.to_excel(
            output,
            index=False,
            engine="openpyxl",
        )

        output.seek(0)

        return StreamingResponse(
            output,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition":
                f'attachment; filename="{request.table_name}.xlsx"'
            },
        )

    raise HTTPException(
        status_code=400,
        detail="Unsupported format",
    )
