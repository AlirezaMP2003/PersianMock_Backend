import csv
import io
import random
import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db.database import get_db
from models import FirstName, LastName
from schemas.generate import GenerateRequest, GenerateResponse

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SQL_TYPES = {
    "firstname": "VARCHAR(100)",
    "lastname": "VARCHAR(100)",
    "email": "VARCHAR(255)",
    "username": "VARCHAR(255)",
    "gender": "VARCHAR(10)",
    "password": "VARCHAR(1000)",
}


def quote_identifier(name: str) -> str:
    # Names are also validated in Pydantic; quoting handles PostgreSQL reserved words.
    return '"' + name.replace('"', '""') + '"'


def sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def unique_with_suffix(value: str, seen: set[str], *, email: bool = False) -> str:
    if value not in seen:
        seen.add(value)
        return value
    if email:
        local, domain = value.rsplit("@", 1)
    else:
        local, domain = value, None
    # Random-looking suffix, with deterministic progress if repeated collisions occur.
    suffix = random.randint(1, 9999)
    while True:
        candidate = f"{local}{suffix}@{domain}" if email else f"{local}{suffix}"
        if candidate not in seen:
            seen.add(candidate)
            return candidate
        suffix += 1


def build_create_table_sql(table_name: str, fields) -> str:
    cols = ['"id" INTEGER PRIMARY KEY']
    for field in fields:
        if field.type == "id":
            continue
        cols.append(f"{quote_identifier(field.name)} {SQL_TYPES[field.type]}")
    return f"CREATE TABLE IF NOT EXISTS {quote_identifier(table_name)} ({', '.join(cols)});"


def spreadsheet_safe(value: Any) -> Any:
    # Prevent opening CSV/XLSX data from evaluating a potentially dangerous formula.
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


@router.post("/", tags=["generate"])
def generate_data(request: GenerateRequest, db: Session = Depends(get_db)):
    fields = [field for field in request.fields if field.type != "id"]
    requested_types = {field.type for field in fields}
    needs_firstname = bool(requested_types & {"firstname", "email", "username", "gender"})
    needs_lastname = "lastname" in requested_types

    first_names = db.query(FirstName).all() if needs_firstname else []
    last_names = db.query(LastName).all() if needs_lastname else []
    if (needs_firstname and not first_names) or (needs_lastname and not last_names):
        raise HTTPException(status_code=503, detail="Required source table is empty. Seed data first.")

    used_usernames: set[str] = set()
    used_emails: set[str] = set()
    rows: list[dict[str, Any]] = []
    for i in range(1, request.count + 1):
        first = random.choice(first_names) if needs_firstname else None
        last = random.choice(last_names) if needs_lastname else None
        values: dict[str, Any] = {"id": i}
        if first is not None:
            values["firstname"] = first.name
            values["gender"] = first.gender.value
            if "email" in requested_types:
                values["email"] = unique_with_suffix(first.email, used_emails, email=True)
            if "username" in requested_types:
                values["username"] = unique_with_suffix(first.username, used_usernames)
        if last is not None:
            values["lastname"] = last.name
        if "password" in requested_types:
            values["password"] = pwd_context.hash(secrets.token_hex(12))
        row: dict[str, Any] = {"id": i}
        for field in fields:
            row[field.name] = values[field.type]
        rows.append(row)

    ddl = build_create_table_sql(request.table_name, fields) if request.include_create_table else None
    columns = ["id"] + [field.name for field in fields]

    if request.format == "json":
        return GenerateResponse(data=rows, ddl=ddl, format="json").model_dump()

    if request.format == "sql":
        sql_rows = ["(" + ", ".join(sql_literal(row[col]) for col in columns) + ")" for row in rows]
        sql = (
            f"INSERT INTO {quote_identifier(request.table_name)} "
            f"({', '.join(quote_identifier(col) for col in columns)}) VALUES\n"
            + ",\n".join(sql_rows) + ";"
        )
        return Response(content="\n\n".join(filter(None, [ddl, sql])), media_type="text/plain; charset=utf-8")

    if request.format == "csv":
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(columns)
        writer.writerows([[spreadsheet_safe(row[col]) for col in columns] for row in rows])
        encoded = output.getvalue().encode("utf-8-sig")
        return StreamingResponse(
            io.BytesIO(encoded), media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{request.table_name}.csv"'},
        )

    if request.format == "excel":
        try:
            import pandas as pd
            import openpyxl  # noqa: F401
        except ImportError as exc:
            raise HTTPException(status_code=500, detail="Excel export requires pandas and openpyxl") from exc
        safe_rows = [{col: spreadsheet_safe(row[col]) for col in columns} for row in rows]
        frame = pd.DataFrame(safe_rows, columns=columns)
        output = io.BytesIO()
        frame.to_excel(output, index=False, engine="openpyxl")
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{request.table_name}.xlsx"'},
        )

    raise HTTPException(status_code=400, detail="Unsupported format")
