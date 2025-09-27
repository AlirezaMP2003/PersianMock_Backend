from fastapi import FastAPI
from db.database import engine, Base
from models import *
from routers import generate, fields

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Persian Mockaroo API")

app.include_router(fields.router, prefix="/fields", tags=["fields"])
app.include_router(generate.router, prefix="/generate", tags=["generate"])

@app.get("/")
def root():
    return {"message": "Persian Mockaroo API is running 🚀"}
