from __future__ import annotations

import argparse
import asyncio
import json
import logging
import signal
from contextlib import suppress
from typing import Awaitable, Callable, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.core import session as async_session_factory
from src.database import load_models
from src.logger import setup_logging
from src.modules.job.models import Job
from src.modules.job.service import JobService

# Import job handler registrations
from src.modules.generation import worker as generation_worker  # noqa: F401

JobHandler = Callable[[Job, AsyncSession], Awaitable[Optional[str | dict]]]
JOB_HANDLERS: Dict[str, JobHandler] = {}

IDLE_SLEEP_SECONDS = 1.0
logger = setup_logging()
load_models()


def register_job_handler(job_type: str, handler: JobHandler) -> None:
    JOB_HANDLERS[job_type] = handler


async def claim_job() -> Optional[Job]:
    try:
        async with async_session_factory() as db_session:
            service = JobService(db_session)
            job = await service.claim_next_job()
            await db_session.commit()
            return job
    except Exception as e:
        logger.error("Error claiming job: %s", str(e))
        return None


async def mark_success(job_id: str, result: Optional[str]) -> None:
    try:
        async with async_session_factory() as db_session:
            service = JobService(db_session)
            await service.complete_job(job_id, result=result)
            await db_session.commit()
    except Exception as e:
        logger.error("Error marking job %s as success: %s", job_id, str(e))


async def mark_failure(job_id: str, error: Optional[str]) -> None:
    try:
        async with async_session_factory() as db_session:
            service = JobService(db_session)
            await service.fail_job(job_id, error=error)
            await db_session.commit()
    except Exception as e:
        logger.error("Error marking job %s as failure: %s", job_id, str(e))


async def run_handler(handler: JobHandler, job: Job, worker_name: str) -> Optional[str]:
    try:
        async with async_session_factory() as handler_session:
            handler_result = await handler(job, handler_session)
            await handler_session.commit()  # Asegurar que la sesión se confirme
            if handler_result is None or isinstance(handler_result, str):
                return handler_result
            return json.dumps(handler_result)
    except Exception as e:
        logger.error("Error running handler for job %s: %s", job.id, str(e))
        raise


async def worker_loop(name: str, shutdown_event: asyncio.Event) -> None:
    worker_logger = logging.getLogger(f"job-worker.{name}")
    worker_logger.info("Worker %s started", name)
    
    register_job_handler("generate_document_dummy", generation_worker.generate_document_handler)
    register_job_handler("run_generation_graph", generation_worker.run_generation_graph_handler)

    while not shutdown_event.is_set():
        try:
            worker_logger.debug("Worker loop iteration - checking for jobs")
            job = await claim_job()
            worker_logger.debug("Claimed job result: %s", job)
            
            if not job:
                worker_logger.debug("No job found, sleeping for %s seconds", IDLE_SLEEP_SECONDS)
                try:
                    await asyncio.wait_for(shutdown_event.wait(), timeout=IDLE_SLEEP_SECONDS)
                except asyncio.TimeoutError:
                    continue
                break

            worker_logger.info("Picked job %s (type=%s)", job.id, job.type)
            handler = JOB_HANDLERS.get(job.type)

            if not handler:
                error_message = f"No handler registered for job type '{job.type}'"
                worker_logger.error(error_message)
                await mark_failure(job.id, error_message)
                continue

            try:
                worker_logger.debug("Running handler for job %s", job.id)
                result = await run_handler(handler, job, name)
                worker_logger.debug("Handler completed for job %s", job.id)
            except Exception as exc:
                worker_logger.exception("Job %s failed", job.id)
                await mark_failure(job.id, str(exc))
            else:
                await mark_success(job.id, result)
                worker_logger.info("Job %s completed", job.id)
                
        except Exception as e:
            worker_logger.error("Unexpected error in worker loop: %s", str(e))
            # Esperar un poco antes de continuar para evitar loops rápidos en caso de error persistente
            await asyncio.sleep(1)

    worker_logger.info("Worker %s stopped", name)


async def run_workers(
    count: int,
    *,
    shutdown_event: Optional[asyncio.Event] = None,
    install_signal_handlers: bool = True,
) -> None:
    """
    Launch N worker loops and keep running until the shutdown event is set.
    When used from the CLI we install signal handlers; when embedded (e.g. in
    FastAPI) an external event should be provided and handlers disabled.
    """
    event = shutdown_event or asyncio.Event()

    def _handle_signal(*_: object) -> None:
        event.set()

    loop = asyncio.get_running_loop()
    if install_signal_handlers:
        for sig in (signal.SIGINT, signal.SIGTERM):
            with suppress(NotImplementedError):
                loop.add_signal_handler(sig, _handle_signal)

    tasks = [asyncio.create_task(worker_loop(f"{idx+1}", event)) for idx in range(count)]
    wait_task = asyncio.create_task(event.wait())
    try:
        await wait_task
    finally:
        event.set()
        await asyncio.gather(*tasks, return_exceptions=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run background job workers.")
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of concurrent worker loops to spawn.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logger.info("Launching %s worker(s)", args.workers)
    try:
        asyncio.run(run_workers(args.workers))
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")


if __name__ == "__main__":
    main()
