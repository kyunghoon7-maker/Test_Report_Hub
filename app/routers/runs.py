from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..db import get_session
from ..models import Run

router = APIRouter()

@router.post("")
def create_run(name: str, session: Session = Depends(get_session)):
    run = Run(name=name)
    session.add(run)
    session.commit()
    session.refresh(run)
    return run

@router.get("")
def list_runs(session: Session = Depends(get_session)):
    runs = session.exec(select(Run).order_by(Run.id.desc())).all()
    return runs