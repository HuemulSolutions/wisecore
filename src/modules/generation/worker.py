from __future__ import annotations

import json
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.job.models import Job
from .graph.execute import execute_graph_worker


async def generate_document_handler(job: Job, session: Optional[AsyncSession] = None) -> str:
    """
    Dummy handler that just echoes the payload. Use it to verify the worker loop
    can pick jobs and mark them as completed.
    """
    payload: dict[str, Any] = {}
    if job.payload:
        payload = json.loads(job.payload)
    print(f"Generating document with payload: {payload}")
    return "dummy handler OK"


async def run_generation_graph_handler(job: Job, session: Optional[AsyncSession] = None) -> str:
    """
    Handler that runs the document generation graph based on the job payload.
    """
    payload: dict[str, Any] = {}
    if job.payload:
        payload = json.loads(job.payload)
    document_id = payload.get("document_id")
    if not document_id:
        raise ValueError("Payload must contain 'document_id' field.")
    
    execution_id = payload.get("execution_id")
    if not execution_id:
        raise ValueError("Payload must contain 'execution_id' field.")
    
    llm_id = payload.get("llm_id")
    if not llm_id:
        raise ValueError("Payload must contain 'llm_id' field.")
    
    user_instructions = payload.get("user_instructions", None)
    
    start_section_id = payload.get("start_section_id", None)
    single_section_mode = payload.get("single_section_mode", False)
    result = await execute_graph_worker(document_id=document_id,
                                        llm_id=llm_id,
                                        execution_id=execution_id,
                                        user_instructions=user_instructions,
                                        start_section_id=start_section_id,
                                        single_section_mode=single_section_mode)
    return json.dumps(result)
    
