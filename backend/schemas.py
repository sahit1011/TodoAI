from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from backend.models.task import PriorityEnum, StatusEnum

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    uuid: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: PriorityEnum = PriorityEnum.MEDIUM
    status: StatusEnum = StatusEnum.TODO

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None

class TaskResponse(TaskBase):
    id: int
    uuid: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Assistant Schemas
class ChatMessage(BaseModel):
    message: str
    assistant_mode: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    actions: Optional[List[dict]] = None

class ChatResponseWithUIActions(ChatResponse):
    uiActions: Optional[List[dict]] = None
