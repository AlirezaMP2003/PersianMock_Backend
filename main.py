from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import engine, Base
from models import *
from routers import generate, fields

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Persian Mockaroo API")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fields.router, prefix="/fields", tags=["fields"])
app.include_router(generate.router, prefix="/generate", tags=["generate"])

@app.get("/")
def root():
    return {"message": "Persian Mockaroo API is running 🚀"}
