from typing import List, Optional

from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    email: str
    password: str


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
