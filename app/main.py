from fastapi import FastAPI
from .db import init_db
from .routers import runs

# uvicorn이 찾을 FastAPI 인스턴스 이름이 꼭 'app' 이어야 함
app = FastAPI(title="Test Report Hub")

@app.on_event("startup")
def on_startup():
    init_db()

# /runs 로 시작하는 API 묶기
app.include_router(runs.router, prefix="/runs")