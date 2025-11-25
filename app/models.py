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

class TestResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="run.id", index=True)
    fqname: str
    status: str
    duration_s: Optional[float] = None
    message: Optional[str] = None