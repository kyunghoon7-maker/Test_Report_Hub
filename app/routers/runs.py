from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel import Session, select, delete
from datetime import datetime
import xml.etree.ElementTree as ET
from typing import Optional

from ..db import get_session
from ..models import Run, TestCase

router = APIRouter()

@router.post("")
def create_run(name: str, session: Session = Depends(get_session)):
    run = Run(name=name)
    session.add(run)
    session.commit()    
    session.refresh(run)
    return run

@router.get("")
def list_runs(
    limit: int = 20,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    runs = session.exec(
        select(Run)
        .order_by(Run.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    # Run별 요약을 같이 만들어서 반환
    out = []
    for run in runs:
        cases = session.exec(
            select(TestCase).where(TestCase.run_id == run.id)
        ).all()

        total = len(cases)
        failed = sum(1 for c in cases if c.status == "failed")
        skipped = sum(1 for c in cases if c.status == "skipped")
        passed = total - failed - skipped

        pass_rate = round((passed / total) * 100, 2) if total > 0 else None

        out.append({
            "id": run.id,
            "name": run.name,
            "status": run.status,
            "started_at": run.started_at,
            "finished_at": run.finished_at,
            "duration_s": run.duration_s,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "pass_rate": pass_rate,
            }
        })

    return out

@router.get("/latest")
def get_latest_run(session: Session = Depends(get_session)):
    run = session.exec(select(Run).order_by(Run.id.desc())).first()
    if not run:
        raise HTTPException(status_code=404, detail="No runs found")
    return run

@router.post("/{run_id}/artifacts/junit")
async def upload_junit_report(
    run_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    run = session.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if run.finished_at is not None:
        raise HTTPException(status_code=409, detail="Run already finished; create a new run_id")

    raw_bytes = await file.read()
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 text")

    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        raise HTTPException(status_code=400, detail="Invalid XML file")

    if root.tag.endswith("testsuites"):
        testsuites = list(root.findall(".//testsuite"))
    else:
        testsuites = [root]

    testcases_to_add: list[TestCase] = []

    for ts in testsuites:
        for tc in ts.findall(".//testcase"):
            name = tc.attrib.get("name", "")
            classname = tc.attrib.get("classname")
            time_attr = tc.attrib.get("time") or "0"
            try:
                time_s = float(time_attr)
            except ValueError:
                time_s = None

            status = "passed"
            failure_message = None

            # 기본 + fallback (namespace/구조 변화 대비)
            failure = tc.find("./failure")
            error = tc.find("./error")
            skipped = tc.find("./skipped")

            if failure is None:
                failure = next((ch for ch in list(tc) if ch.tag.endswith("failure")), None)
            if error is None:
                error = next((ch for ch in list(tc) if ch.tag.endswith("error")), None)
            if skipped is None:
                skipped = next((ch for ch in list(tc) if ch.tag.endswith("skipped")), None)

            if failure is not None or error is not None:
                status = "failed"
                node = failure or error

                attr_msg = node.get("message") if node is not None else None
                body_msg = "".join(node.itertext()) if node is not None else None

                msg = None
                if attr_msg and body_msg:
                    msg = f"{attr_msg}\n{body_msg}"
                else:
                    msg = attr_msg or body_msg

                failure_message = (msg or "").strip() or None

            elif skipped is not None:
                status = "skipped"

            testcases_to_add.append(
                TestCase(
                    run_id=run.id,
                    name=name,
                    classname=classname,
                    status=status,
                    time_s=time_s,
                    failure_message=failure_message,
                )
            )

    if not testcases_to_add:
        raise HTTPException(status_code=400, detail="No <testcase> elements found in XML")

    # 기존 케이스 덮어쓰기
    session.exec(delete(TestCase).where(TestCase.run_id == run.id))

    session.add_all(testcases_to_add)

    total_time = sum(tc.time_s or 0.0 for tc in testcases_to_add)
    total = len(testcases_to_add)
    failed = sum(1 for tc in testcases_to_add if tc.status == "failed")
    skipped_count = sum(1 for tc in testcases_to_add if tc.status == "skipped")
    pass_count = total - failed - skipped_count

    run.finished_at = datetime.utcnow()
    run.duration_s = total_time if total_time > 0 else None
    run.status = "failed" if failed > 0 else "passed"

    session.commit()

    return {
        "run_id": run.id,
        "total": total,
        "passed": pass_count,
        "failed": failed,
        "skipped": skipped_count,
        "status": run.status,
        "duration_s": run.duration_s,
    }
############################################################################
@router.get("/{run_id}/tests")
def list_testcases_for_run(
    run_id: int,
    status: Optional[str] = None,  # passed/failed/skipped
    limit: int = 200,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    run = session.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    q = select(TestCase).where(TestCase.run_id == run_id)

    if status is not None:
        q = q.where(TestCase.status == status)

    q = q.order_by(TestCase.id.asc()).offset(offset).limit(limit)

    cases = session.exec(q).all()
    return cases

############################################################################
@router.get("/{run_id}/summary")
def get_run_summary(
    run_id: int,
    session: Session = Depends(get_session),
):
    run = session.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    cases = session.exec(
        select(TestCase).where(TestCase.run_id == run_id)
    ).all()

    total = len(cases)
    failed = sum(1 for c in cases if c.status == "failed")
    skipped = sum(1 for c in cases if c.status == "skipped")
    passed = total - failed - skipped

    pass_rate = round((passed / total) * 100, 2) if total > 0 else None
    duration_s = sum((c.time_s or 0.0) for c in cases) if total > 0 else None

    return {
        "run_id": run_id,
        "name": run.name,
        "status": run.status,
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": pass_rate,      # 예: 75.0
        "duration_s": duration_s,    # 예: 0.07 (없으면 0.0 또는 None)
    }
