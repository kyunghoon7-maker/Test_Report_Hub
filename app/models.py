from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Run(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    status: str = "running"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    duration_s: Optional[float] = None


class TestCase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # 어떤 Run에 속한 테스트인지 연결 (FK)
    run_id: int = Field(foreign_key="run.id")

    name: str
    classname: Optional[str] = None  # pytest면 보통 모듈/파일 이름
    status: str  # "passed" / "failed" / "skipped"
    time_s: Optional[float] = None   # 실행 시간(초)

    failure_message: Optional[str] = None  # 실패 시 메시지 (assert 2 == 3 같은 것)

    
# class TestResult(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     run_id: int = Field(foreign_key="run.id", index=True)
#     fqname: str
#     status: str
#     duration_s: Optional[float] = None
#     message: Optional[str] = None

