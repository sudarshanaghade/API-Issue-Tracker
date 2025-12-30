from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import csv
from io import StringIO

from .database import engine, Base
from .dependencies import get_db
from . import schemas, crud, models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Issue Tracker API")


@app.post("/issues", response_model=schemas.IssueOut)
def create_issue(issue: schemas.IssueCreate, db: Session = Depends(get_db)):
    return crud.create_issue(db, issue)


@app.get("/issues", response_model=list[schemas.IssueOut])
def read_issues(skip: int = 0, limit: int = 100, status: str = None, db: Session = Depends(get_db)):
    return crud.get_issues(db, skip=skip, limit=limit, status=status)


@app.get("/issues/{issue_id}", response_model=schemas.IssueDetail)
def read_issue(issue_id: int, db: Session = Depends(get_db)):
    db_issue = crud.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    return db_issue


@app.patch("/issues/{issue_id}")
def update_issue(issue_id: int, data: schemas.IssueUpdate, db: Session = Depends(get_db)):
    return crud.update_issue(db, issue_id, data)


@app.post("/issues/{issue_id}/comments", response_model=schemas.Comment)
def add_comment(issue_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    return crud.add_comment(db, issue_id, comment)


@app.put("/issues/{issue_id}/labels", response_model=list[schemas.Label])
def update_issue_labels(issue_id: int, label_names: list[str], db: Session = Depends(get_db)):
    return crud.update_issue_labels(db, issue_id, label_names)


@app.post("/issues/bulk-status")
def bulk_update(issue_ids: list[int], status: str, db: Session = Depends(get_db)):
    try:
        for issue_id in issue_ids:
            issue = db.query(models.Issue).get(issue_id)
            if not issue:
                raise Exception("Invalid issue ID")
            issue.status = status
        db.commit()
        return {"message": "Bulk update successful"}
    except:
        db.rollback()
        return {"error": "Transaction rolled back"}


@app.post("/issues/import")
def import_issues(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read().decode()
    reader = csv.DictReader(StringIO(content))

    success, failed = 0, 0
    errors = []

    for row in reader:
        try:
            issue = models.Issue(
                title=row["title"],
                description=row.get("description"),
                assignee_id=int(row["assignee_id"])
            )
            db.add(issue)
            success += 1
        except Exception as e:
            failed += 1
            errors.append(str(e))

    db.commit()
    return {
        "created": success,
        "failed": failed,
        "errors": errors
    }


@app.get("/reports/top-assignees")
def top_assignees(db: Session = Depends(get_db)):
    return db.query(
        models.Issue.assignee_id,
        models.Issue.id
    ).count()


@app.get("/reports/latency")
def avg_latency(db: Session = Depends(get_db)):
    issues = db.query(models.Issue).filter(models.Issue.resolved_at.isnot(None)).all()
    if not issues:
        return {"average_time": None}

    total = sum([(i.resolved_at - i.created_at).total_seconds() for i in issues])
    return {"average_time_seconds": total / len(issues)}
