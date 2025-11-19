from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from .schemas import Chatbot
from .chatbot import stream

router = APIRouter(prefix="/chatbot")

@router.post("/")
async def chatbot_endpoint(request: Chatbot):
    """
    Chatbot interaction endpoint.
    """
    try:
        return StreamingResponse(
            stream(message=request.user_message, execution_id=request.execution_id, thread_id=request.thread_id),
            media_type="text/event-stream")
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred in the chatbot interaction: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
