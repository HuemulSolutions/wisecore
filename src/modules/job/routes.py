from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.core import get_session
from src.modules.job.models import Job
from src.modules.job.service import JobService
from src.schemas import ResponseSchema
from src.utils import get_transaction_id
from .schemas import JobResponse

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


@router.post("/dummy", response_model=ResponseSchema)
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

        return ResponseSchema(
            data=jsonable_encoder(job_to_dict(job)),
            message="Dummy job enqueued successfully",
            transaction_id=transaction_id
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id, "error": f"Failed to enqueue job: {exc}"},
        ) from exc
        
@router.get("/latest", response_model=ResponseSchema)
async def get_latest_jobs(
    limit: int = Query(default=10, ge=1, le=100, description="Número de jobs a obtener"),
    session: AsyncSession = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Obtiene los últimos jobs ordenados por fecha de creación (más recientes primero).
    """
    try:
        job_service = JobService(session)
        jobs = await job_service.get_latest_jobs(limit=limit)

        return ResponseSchema(
            data=jsonable_encoder(jobs),
            message="Latest jobs retrieved successfully",
            transaction_id=transaction_id
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id, "error": f"An error occurred while retrieving latest jobs: {str(exc)}"},
        ) from exc


@router.get("/{job_id}", response_model=ResponseSchema)
async def get_job(
    job_id: str,
    session: AsyncSession = Depends(get_session),
    transaction_id: str = Depends(get_transaction_id),
):
    """
    Retrieve a job by ID to inspect its status/result while testing.
    """
    try:
        service = JobService(session)
        job = await service.get_job(job_id)

        return ResponseSchema(
            data=jsonable_encoder(job_to_dict(job)),
            message="Job retrieved successfully",
            transaction_id=transaction_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail={"transaction_id": transaction_id, "error": str(exc)},
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id, "error": f"An error occurred while retrieving the job: {str(exc)}"},
        ) from exc



