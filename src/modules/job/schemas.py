from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class JobResponse(BaseModel):
    id: UUID
    type: str
    payload: Optional[str]
    status: str
    result: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LatestJobsResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
