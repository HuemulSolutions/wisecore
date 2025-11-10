from __future__ import annotations

import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.job.models import Job


async def generate_document_handler(job: Job, session: AsyncSession) -> str:
    """
    Dummy handler that just echoes the payload. Use it to verify the worker loop
    can pick jobs and mark them as completed.
    """
    payload: dict[str, Any] = {}
    if job.payload:
        payload = json.loads(job.payload)
    print(f"Generating document with payload: {payload}")
    await session.flush()  # no-op to ensure the session is used in tests
    return "dummy handler OK"

