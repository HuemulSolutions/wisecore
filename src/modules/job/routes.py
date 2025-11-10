from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.core import get_session
from src.modules.job.models import Job
from src.modules.job.service import JobService
from src.schemas import ResponseSchema
from src.utils import get_transaction_id

router = APIRouter(prefix="/job", tags=["Jobs"])


class DummyJobRequest(BaseModel):
    payload: Optional[Dict[str, Any]] = None


def job_to_dict(job: Job) -> Dict[str, Any]:
    return {
        "id": str(job.id),
        "type": job.type,
        "status": job.status,
        "payload": job.payload,
        "result": job.result,
        "created_at": job.created_at.isoformat() if isinstance(job.created_at, datetime) else job.created_at,
        "updated_at": job.updated_at.isoformat() if isinstance(job.updated_at, datetime) else job.updated_at,
    }


@router.post("/dummy")
async def enqueue_dummy_job(
    request: DummyJobRequest,
    session: AsyncSession = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Enqueue a dummy generation job so the worker loop can be tested end-to-end.
    """
    try:
        service = JobService(session)
        payload = json.dumps(request.payload) if request.payload else None
        job = await service.enqueue_job(job_type="generate_document_dummy", payload=payload)
        return ResponseSchema(transaction_id=transaction_id, data=job_to_dict(job))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id, "error": f"Failed to enqueue job: {exc}"},
        ) from exc


@router.get("/{job_id}")
async def get_job(
    job_id: str,
    session: AsyncSession = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Retrieve a job by ID to inspect its status/result while testing.
    """
    service = JobService(session)
    try:
        job = await service.get_job(job_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail={"transaction_id": transaction_id, "error": str(exc)},
        ) from exc
    return ResponseSchema(transaction_id=transaction_id, data=job_to_dict(job))
