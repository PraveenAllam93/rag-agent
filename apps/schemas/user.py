from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    email: str
    created_at: datetime
    updated_at: datetime


class UserCreateSchema(BaseModel):
    username: str
    email: str
    password: str


class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
