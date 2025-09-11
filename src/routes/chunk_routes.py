from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.database.core import get_session
from src.services.chunk_service import ChunkService
from src.schemas import ResponseSchema
from src.utils import get_transaction_id

router = APIRouter(prefix="/chunks")


@router.post("/generate_chunks/{execution_id}")
async def generate_chunks(execution_id: str,
                            session: Session = Depends(get_session),
                            transaction_id: str = Depends(get_transaction_id)):
        """
        Generate chunks for a specific execution.
        """
        try:
            chunk_service = ChunkService(session)
            num_chunks = await chunk_service.generate_chunks(execution_id)
            
            return ResponseSchema(
                transaction_id=transaction_id,
                data={"message": f"Generated {num_chunks} chunks for execution {execution_id}."}
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={"transaction_id": transaction_id,
                        "error": str(e)}
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={"transaction_id": transaction_id,
                        "error": f"An error occurred while generating chunks: {str(e)}"}
            )
            
            
@router.get("/search")
async def search_chunks(query: str,
                        session: Session = Depends(get_session),
                        transaction_id: str = Depends(get_transaction_id)):
    """
    Search for chunks containing the query string.
    """
    try:
        chunk_service = ChunkService(session)
        result = await chunk_service.search_chunks(query)
        
        return ResponseSchema(
            transaction_id=transaction_id,
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"transaction_id": transaction_id,
                    "error": f"An error occurred while searching for chunks: {str(e)}"}
        )
        