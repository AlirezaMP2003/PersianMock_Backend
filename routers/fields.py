from fastapi import APIRouter

router = APIRouter()

ALL_FIELDS = ["id", "firstname", "lastname", "email", "username", "password", "gender"]

@router.get("/")
def get_fields():
    return {"fields": ALL_FIELDS}
