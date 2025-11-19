from __future__ import annotations

import asyncio

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import system_config
from src.database.core import session as async_session_factory
from src.modules.job.service import JobService
from src.worker.worker import run_workers
from src.modules.job.routes import router as job_router

logger = logging.getLogger(__name__)
SHUTDOWN_FAIL_REASON = "Job worker stopped because the API was shut down."


async def _fail_running_jobs_on_shutdown() -> None:
    updated = 0
    try:
        async with async_session_factory() as db_session:
            service = JobService(db_session)
            updated = await service.fail_running_jobs(reason=SHUTDOWN_FAIL_REASON)
            await db_session.commit()
    except Exception:  # pragma: no cover - defensive logging
        logger.exception("Failed to mark running jobs as failed during shutdown.")
    else:
        logger.info("Marked %s running jobs as failed during shutdown.", updated)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.shutdown_event = asyncio.Event()
    app.state.worker_task = asyncio.create_task(
        run_workers(
            system_config.JOB_WORKER_COUNT,
            shutdown_event=app.state.shutdown_event,
            install_signal_handlers=False,
        )
    )
    try:
        yield
    finally:
        app.state.shutdown_event.set()
        await app.state.worker_task
        await _fail_running_jobs_on_shutdown()


app = FastAPI(title="Job Worker", version="1.0.0", lifespan=lifespan)
app.include_router(job_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/healthz")
async def health() -> dict[str, str]:
    return {"status": "ok"}
