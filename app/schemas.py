from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime



class User(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Label(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class IssueCreate(BaseModel):
    title: str
    description: Optional[str]
    assignee_id: int


class IssueUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]
    version: int


class CommentCreate(BaseModel):
    author_id: int
    body: str = Field(..., min_length=1)


class Comment(BaseModel):
    id: int
    body: str
    author: User
    created_at: datetime

    class Config:
        orm_mode = True


class IssueOut(BaseModel):
    id: int
    title: str
    status: str
    version: int
    assignee: Optional[User]
    created_at: datetime

    class Config:
        orm_mode = True


class IssueDetail(IssueOut):
    description: Optional[str]
    comments: List[Comment]
    labels: List[Label]
