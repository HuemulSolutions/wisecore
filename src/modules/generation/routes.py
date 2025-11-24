from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from .graph.execute import stream_graph
from .service import (GenerationService)
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.core import get_session
from .schemas import GenerateDocument, FixSection, RedactSectionPrompt


router = APIRouter(prefix="/generation")

# Almacena referencias de tareas activas para evitar garbage collection
# _active_tasks = weakref.WeakSet()

@router.post("/stream")
async def stream_generation(request: GenerateDocument):
    """
    Stream the generation of a document.
    """
    try:
        return StreamingResponse(
            stream_graph(request.document_id),
            media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while streaming the generation: {str(e)}"
        )
        
        
@router.post("/generate_worker")
async def generate_document_worker(request: GenerateDocument,
                                   session: AsyncSession = Depends(get_session)):
    """
    Generate a document using the worker and return the final result.
    """
    try:
        generation_service = GenerationService(session)
        result = await generation_service.add_execution_graph_job(request.document_id, request.execution_id, 
                                                                  request.instructions, request.start_section_id,
                                                                  request.single_section_mode)
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Document generation failed."
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the document: {str(e)}"
        )

@router.post("/generate_document")
async def generate_document(request: GenerateDocument):
    """
    Generate a document and stream the output.
    """
    try:
        return StreamingResponse(
            stream_graph(request.document_id, request.execution_id, request.instructions),
            media_type="text/event-stream")
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while generating the document: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
        
        
@router.post("/fix_section")
async def fix_section(request: FixSection, 
                      session: AsyncSession = Depends(get_session)):
    """
    Fix a section in a document.
    """
    try:
        service = GenerationService(session)
        return StreamingResponse(
            service.fix_section_service(content=request.content, instructions=request.instructions),
            media_type="text/event-stream")
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while fixing the section: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
        
        
@router.post("/redact_section_prompt")
async def redact_section_prompt(request: RedactSectionPrompt,
                                session: AsyncSession = Depends(get_session)):
    """
    Redact or improve the prompt for a section.
    """
    try:
        service = GenerationService(session)
        return StreamingResponse(
            service.redact_section_prompt_service(name=request.name, content=request.content),
            media_type="text/event-stream")
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while redacting the section prompt: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
        
