from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="OPEN")
    assignee_id = Column(Integer, ForeignKey("users.id"))
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    assignee = relationship("User")
    comments = relationship("Comment", back_populates="issue")
    issue_labels = relationship("IssueLabel", back_populates="issue")
    labels = relationship("Label", secondary="issue_labels", viewonly=True)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="comments")
    author = relationship("User")


class Label(Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class IssueLabel(Base):
    __tablename__ = "issue_labels"

    issue_id = Column(Integer, ForeignKey("issues.id"), primary_key=True)
    label_id = Column(Integer, ForeignKey("labels.id"), primary_key=True)

    issue = relationship("Issue", back_populates="issue_labels")
    label = relationship("Label")

    __table_args__ = (
        UniqueConstraint("issue_id", "label_id"),
    )
