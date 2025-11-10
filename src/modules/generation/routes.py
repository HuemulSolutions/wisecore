from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from .graph.stream import stream_graph
from .service import (fix_section_service, redact_section_prompt_service)
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
        
        

# @router.post("/generate_document")
# async def generate_document(request: GenerateDocument):
#     try:
#         # Crea la cola
#         q: asyncio.Queue = asyncio.Queue(maxsize=100)
        
#         # Crea el worker desacoplado y mantén la referencia
#         worker_task = asyncio.create_task(run_graph_worker(
#             document_id=request.document_id,
#             execution_id=request.execution_id,
#             user_instructions=request.instructions,
#             q=q
#         ))
        
#         # Guarda la referencia para evitar garbage collection
#         _active_tasks.add(worker_task)
        
#         # Añade callback para limpiar cuando termine
#         def cleanup_task(task):
#             _active_tasks.discard(task)
        
#         worker_task.add_done_callback(cleanup_task)

#         # Devuelve un StreamingResponse que solo drena la cola
#         return StreamingResponse(
#             stream_queue(q),
#             media_type="text/event-stream",
#             headers={
#                 "Cache-Control": "no-cache",
#                 "Connection": "keep-alive",
#                 "X-Accel-Buffering": "no",
#             },
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"An error occurred while generating the document: {str(e)}"
#         )

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
        
        
# @router.post("/chatbot")
# async def chatbot_endpoint(request: Chatbot):
#     """
#     Chatbot interaction endpoint.
#     """
#     try:
#         return StreamingResponse(
#             stream(message=request.user_message, execution_id=request.execution_id, thread_id=request.thread_id),
#             media_type="text/event-stream")
#     except ValueError as e:
#         raise HTTPException(
#             status_code=400,
#             detail=f"An error occurred in the chatbot interaction: {str(e)}"
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"An unexpected error occurred: {str(e)}"
#         )
