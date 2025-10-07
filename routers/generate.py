from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from db.database import get_db
from models import FirstName, LastName
from schemas.generate import GenerateRequest, GenerateResponse, FieldItem
from typing import List, Dict, Any
import random, io, csv, secrets, re

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

ALL_FIELDS = ["id", "firstname", "lastname", "email", "username", "password", "gender"]

SQL_TYPES = {
    "firstname": "VARCHAR(100)",
    "lastname": "VARCHAR(100)",
    "email": "VARCHAR(255)",
    "username": "VARCHAR(255)",
    "gender": "VARCHAR(10)",
    "password": "VARCHAR(1000)"
}

def sql_escape(value: Any) -> str:
    """Escape a Python value for inclusion in a SQL literal (basic)."""
    if value is None:
        return "NULL"
    s = str(value)
    return "'" + s.replace("'", "''") + "'"

def build_create_table_sql(table_name: str, fields: List[FieldItem]) -> str:
    cols = ["id SERIAL PRIMARY KEY"]
    for f in fields:
        if not f.type or not f.name:
            continue
        sql_type = SQL_TYPES.get(f.type.lower(), "TEXT")
        cols.append(f"{f.name} {sql_type}")
    cols_sql = ", ".join(cols)
    return f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_sql});"

@router.post("/", tags=["generate"])
def generate_data(request: GenerateRequest, db: Session = Depends(get_db)):

    for f in request.fields:
        if f.type not in ALL_FIELDS:
            raise HTTPException(status_code=400, detail=f"Field '{f.type}' is not valid")

    if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', request.table_name):
        raise HTTPException(status_code=400, detail="Invalid table_name")

    first_names = db.query(FirstName).all()
    last_names = db.query(LastName).all()

    if not first_names or not last_names:
        raise HTTPException(status_code=500, detail="Source tables are empty. Seed data first.")

    rows: List[Dict[str, Any]] = []
    for i in range(1, request.count + 1):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        row: Dict[str, Any] = {}
        row["id"] = i
        for field in request.fields:
            if field.type == "firstname":
                row[field.name] = fn.name
            elif field.type == "lastname":
                row[field.name] = ln.name
            elif field.type == "email":
                row[field.name] = fn.email
            elif field.type == "username":
                row[field.name] = fn.username
            elif field.type == "gender":
                row[field.name] = fn.gender.value
            elif field.type == "password":
                plaintext = secrets.token_hex(12)
                plaintext_bytes = plaintext.encode("utf-8")[:72]
                plaintext = plaintext_bytes.decode("utf-8", errors="ignore")
                hashed = pwd_context.hash(plaintext)
                row[field.name] = hashed
        rows.append(row)

    ddl = None
    if request.include_create_table:
        ddl = build_create_table_sql(request.table_name, request.fields)

    fmt = request.format.lower()
    if fmt == "json":
        resp = GenerateResponse(data=rows, ddl=ddl, format="json")
        return resp.model_dump()

    if fmt == "sql":
        parts = []
        if ddl:
            parts.append(ddl)
        cols = ["id"] + [f.name for f in request.fields]
        cols_str = ", ".join(cols)
        values_list = []
        for r in rows:
            vals = []
            for c in cols:
                vals.append(sql_escape(r.get(c)))
            values_list.append("(" + ", ".join(vals) + ")")
        insert_sql = f"INSERT INTO {request.table_name} ({cols_str}) VALUES\n" + ",\n".join(values_list) + ";"
        parts.append(insert_sql)
        sql_text = "\n\n".join(parts)
        return Response(content=sql_text, media_type="text/sql")

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        header = ["id"] + [f.name for f in request.fields]
        writer.writerow(header)
        for r in rows:
            row_vals = [r.get(col, "") for col in header]
            writer.writerow(row_vals)
        output.seek(0)
        csv_bytes = output.getvalue().encode("utf-8-sig")
        return StreamingResponse(io.BytesIO(csv_bytes), media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={request.table_name}.csv"})

    if fmt == "excel":
        try:
            import pandas as pd
        except ImportError:
            raise HTTPException(status_code=500, detail="pandas is required for excel output. pip install pandas openpyxl")
        df = pd.DataFrame(rows)
        cols = ["id"] + [f.name for f in request.fields]
        df = df.reindex(columns=cols)
        bio = io.BytesIO()
        df.to_excel(bio, index=False, engine="openpyxl")
        bio.seek(0)
        return StreamingResponse(bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={request.table_name}.xlsx"})

    raise HTTPException(status_code=400, detail="Unsupported format")
