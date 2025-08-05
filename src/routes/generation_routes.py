from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from src.graph.stream import stream_graph
from src.schemas import GenerateDocument

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