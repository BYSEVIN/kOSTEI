from fastapi import FastAPI
from interfaces.api import router as api_router

app = FastAPI(title="Kostey API")

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "API is running"}