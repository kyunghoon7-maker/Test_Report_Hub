from fastapi import FastAPI
from .db import init_db
from .routers import runs

app = FastAPI(title="Test Report Hub")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(runs.router, prefix="/runs")