from fastapi import FastAPI

app = FastAPI(title="Persian Mockaroo API")

@app.get("/")
def root():
    return {"message": "Persian Mockaroo API is running 🚀"}
