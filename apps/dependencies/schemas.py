from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None


class TenantChoiceSchema(BaseModel):
    tenant_id: int
    tenant_name: str
    role_id: int


class TenantChooseSchema(BaseModel):
    tenants: List[TenantChoiceSchema] = Field(
        ..., description="Tenants this user can select from after authenticating"
    )


class AuthRequest(BaseModel):
    email: str
    password: str


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


class TenantSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tenant_id: int
    name: str
    created_at: datetime
    updated_at: datetime


class TenantCreateSchema(BaseModel):
    name: str


class TenantUpdateSchema(BaseModel):
    name: Optional[str] = None
