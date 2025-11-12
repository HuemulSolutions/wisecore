from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .models import Job
from .repository import JobRepo


class JobService:
    """
    High-level use cases around jobs. Wraps the repository and provides
    convenience helpers for API handlers or workers.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = JobRepo(session)

    async def enqueue_job(self, *, job_type: str, payload: Optional[str] = None) -> Job:
        """
        Create a new job in pending status.
        """
        return await self.repo.enqueue(job_type=job_type, payload=payload)

    async def get_job(self, job_id: str) -> Job:
        job = await self.repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job with id {job_id} not found.")
        return job

    async def claim_next_job(self, *, types: Optional[Iterable[str]] = None) -> Optional[Job]:
        """
        Retrieve the next pending job (optionally filtered by type) and
        mark it as running so no other worker can pick it.
        """
        return await self.repo.fetch_next_pending(types=types)

    async def complete_job(self, job_id: str, *, result: Optional[str] = None) -> Job:
        """
        Mark a job as completed and store an optional result.
        """
        job = await self.get_job(job_id)
        return await self.repo.mark_as_completed(job, result=result)

    async def fail_job(self, job_id: str, *, error: Optional[str] = None) -> Job:
        """
        Mark a job as failed and store an optional error payload.
        """
        job = await self.get_job(job_id)
        return await self.repo.mark_as_failed(job, error=error)

    async def get_latest_jobs(self, limit: int = 10) -> list[Job]:
        """
        Get the latest jobs ordered by creation date.
        """
        return await self.repo.get_latest_jobs(limit=limit)
