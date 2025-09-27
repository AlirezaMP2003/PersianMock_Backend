from fastapi import FastAPI
from db.database import engine, Base
from models import *

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Persian Mockaroo API")

@app.get("/")
def root():
    return {"message": "Persian Mockaroo API is running 🚀"}
