from .graph import compiled_graph
from .nodes import State
from src.database.core import get_graph_session
from .services import GraphServices
from src.modules.execution.models import Status
import asyncio


def get_state(document_id: str) -> State:
    """
    Get the initial state for the graph execution.
    """
    state = State(document_id=document_id)
    return state

def format_event(event: tuple) -> dict:
    """
    Format the event for streaming.
    """
    if not event:
        return
    type_, data = event
    if type_ == "messages":
        content, _ = data
        message = content.content.replace("\n", "\\n")
        return "event: content\ndata: " + message + "\n\n"
    elif type_ == "custom":
        return f"event: info\ndata: {data}\n\n"

async def stream_graph(document_id: str, execution_id: str, user_instructions: str = None):
    """
    Stream the graph execution.
    """
    state = State(
        document_id=document_id,
        execution_id=execution_id,
        execution_instructions=user_instructions
    )
    initial_config = {
            "recursion_limit": 60,
        }
    try:
        async for event in compiled_graph.astream(state, config=initial_config, stream_mode=["messages", "custom"]):
            yield format_event(event)
    except asyncio.CancelledError:
        raise
    except Exception as e:
        async with get_graph_session() as session:
            service = GraphServices(session)
            await service.update_execution(execution_id, Status.FAILED, str(e))
        print(f"Error in stream_graph: {e}")
        yield f"event: error\ndata: {str(e)}\n\n"
        return
    
    
async def execute_graph_worker(document_id: str, execution_id: str, user_instructions: str = None):
    """
    Execute the graph without streaming.
    """
    state = State(
        document_id=document_id,
        execution_id=execution_id,
        execution_instructions=user_instructions
    )
    initial_config = {
            "recursion_limit": 60,
        }
    try:
        await compiled_graph.ainvoke(state, config=initial_config)
    except Exception as e:
        async with get_graph_session() as session:
            service = GraphServices(session)
            await service.update_execution(execution_id, Status.FAILED, str(e))
        print(f"Error in execute_graph_worker: {e}")
        raise e
    return "Execution completed successfully"
    

        
def test_stream_graph():
    """
    Test the stream_graph function.
    """
    import asyncio

    async def test():
        async for event in stream_graph(document_id="07bf9e5c-62e9-46a2-b5a3-c0f80f346c44",
                                        execution_id="6209ccb1-543f-4d15-adb4-e7cd03ca8e9c",
                                        user_instructions="Escribe el documento en inglés"):
            print(event)
    asyncio.run(test())
if __name__ == "__main__":
    test_stream_graph()