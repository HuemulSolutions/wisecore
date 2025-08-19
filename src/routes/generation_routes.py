from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from src.graph.stream import stream_graph
from src.services.generation_service import (fix_section_service, redact_section_prompt_service)
from src.schemas import GenerateDocument, FixSection, RedactSectionPrompt

router = APIRouter(prefix="/generation")

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
        
        
@router.post("/generate_document")
async def generate_document(request: GenerateDocument):
    print("Generating document with request:", request)
    try:
        return StreamingResponse(
            stream_graph(document_id=request.document_id, 
                         execution_id=request.execution_id, 
                         user_instructions=request.instructions),
            media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the document: {str(e)}"
        )
        
        
@router.post("/fix_section")
async def fix_section(request: FixSection):
    """
    Fix a section in a document.
    """
    try:
        return StreamingResponse(
            fix_section_service(content=request.content, instructions=request.instructions),
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
async def redact_section_prompt(request: RedactSectionPrompt):
    """
    Redact or improve the prompt for a section.
    """
    try:
        return StreamingResponse(
            redact_section_prompt_service(name=request.name, content=request.content),
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