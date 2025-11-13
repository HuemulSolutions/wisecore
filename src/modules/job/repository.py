from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.sql import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_repo import BaseRepository
from .models import Job, JobStatus


class JobRepo(BaseRepository[Job]):
    """
    Repository focused on coordinating access to job rows. It exposes helpers
    to enqueue new work and to atomically claim pending jobs so multiple workers
    can cooperate without picking the same task.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Job)

    async def enqueue(self, *, job_type: str, payload: Optional[str] = None) -> Job:
        job = Job(type=job_type, payload=payload, status=JobStatus.PENDING.value)
        return await self.add(job)

    async def fetch_next_pending(self, *, types: Optional[Iterable[str]] = None) -> Optional[Job]:
        """
        Fetch the next pending job and mark it as running while holding a DB lock.
        Uses SELECT ... FOR UPDATE SKIP LOCKED so that concurrent workers cannot
        take the same job.
        """
        query = self._pending_jobs_query(types).with_for_update(skip_locked=True).limit(1)
        result = await self.session.execute(query)
        job = result.scalar_one_or_none()
        if not job:
            return None

        job.status = JobStatus.RUNNING.value
        await self.session.flush()
        return job

    async def mark_as_completed(self, job: Job, *, result: Optional[str] = None) -> Job:
        job.status = JobStatus.COMPLETED.value
        job.result = result
        await self.session.flush()
        return job

    async def mark_as_failed(self, job: Job, *, error: Optional[str] = None) -> Job:
        job.status = JobStatus.FAILED.value
        job.result = error
        await self.session.flush()
        return job

    async def get_latest_jobs(self, limit: int = 10) -> list[Job]:
        """
        Fetch the latest jobs ordered by creation date (most recent first).
        """
        query = select(self.model).order_by(self.model.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    def _pending_jobs_query(self, types: Optional[Iterable[str]] = None) -> Select:
        query = select(self.model).where(self.model.status == JobStatus.PENDING.value)
        if types:
            query = query.where(self.model.type.in_(list(types)))
        return query.order_by(self.model.created_at.asc())
