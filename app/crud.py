from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from . import models, schemas


def create_issue(db: Session, issue: schemas.IssueCreate):
    new_issue = models.Issue(**issue.dict())
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)
    return new_issue


def get_issues(db: Session, skip: int = 0, limit: int = 100, status: str = None):
    query = db.query(models.Issue)
    if status:
        query = query.filter(models.Issue.status == status)
    return query.offset(skip).limit(limit).all()


def get_issue(db: Session, issue_id: int):
    return db.query(models.Issue).get(issue_id)


def update_issue(db: Session, issue_id: int, data: schemas.IssueUpdate):
    issue = db.query(models.Issue).get(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue.version != data.version:
        raise HTTPException(status_code=409, detail="Version conflict")

    for field, value in data.dict(exclude={"version"}, exclude_unset=True).items():
        setattr(issue, field, value)

    issue.version += 1
    issue.updated_at = datetime.utcnow()

    if issue.status == "CLOSED":
        issue.resolved_at = datetime.utcnow()

    db.commit()
    return issue


def add_comment(db: Session, issue_id: int, comment: schemas.CommentCreate):
    issue = db.query(models.Issue).get(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    new_comment = models.Comment(
        issue_id=issue_id,
        author_id=comment.author_id,
        body=comment.body
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


def get_label_by_name(db: Session, name: str):
    return db.query(models.Label).filter(models.Label.name == name).first()


def create_label(db: Session, name: str):
    label = models.Label(name=name)
    db.add(label)
    db.commit()
    db.refresh(label)
    return label


def update_issue_labels(db: Session, issue_id: int, label_names: list[str]):
    issue = db.query(models.Issue).get(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Clear existing labels
    issue.issue_labels = []
    
    for name in label_names:
        label = get_label_by_name(db, name)
        if not label:
            label = create_label(db, name)
        
        issue_label = models.IssueLabel(issue_id=issue_id, label_id=label.id)
        db.add(issue_label)
    
    db.commit()
    db.refresh(issue)
    return issue.labels
