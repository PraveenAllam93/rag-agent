from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


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
