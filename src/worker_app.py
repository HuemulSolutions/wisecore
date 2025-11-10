from __future__ import annotations

import asyncio

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import system_config
from src.worker import run_workers


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


app = FastAPI(title="Job Worker", version="1.0.0", lifespan=lifespan)


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/healthz")
async def health() -> dict[str, str]:
    return {"status": "ok"}
