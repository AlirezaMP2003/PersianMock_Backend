from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models import FirstName, LastName
from schemas.generate import GenerateRequest, GenerateResponse
from typing import Dict, Any
import random

router = APIRouter()

ALL_FIELDS = ["id", "firstname", "lastname", "email", "username", "password", "gender"]

@router.post("/", response_model=GenerateResponse)
def generate_data(request: GenerateRequest, db: Session = Depends(get_db)):

    for f in request.fields:
        if f not in ALL_FIELDS:
            raise HTTPException(status_code=400, detail=f"Field '{f}' is not valid")

    first_names = db.query(FirstName).all()
    last_names = db.query(LastName).all()

    result = []
    for _ in range(request.count):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        row: Dict[str, Any] = {}
        for field in request.fields:
            if field == "firstname":
                row["firstname"] = fn.name
            elif field == "lastname":
                row["lastname"] = ln.name
            elif field == "email":
                row["email"] = fn.email
            elif field == "username":
                row["username"] = fn.username
            elif field == "gender":
                row["gender"] = fn.gender
        result.append(row)
    return result
