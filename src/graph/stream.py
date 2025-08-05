from .graph import compiled_graph
from .nodes import State
from .services import GraphServices
from src.database.core import get_graph_session


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
    try:
        async for event in compiled_graph.astream(state, stream_mode=["messages", "custom"]):
            yield format_event(event)
    except Exception as e:
        yield f"event: error\ndata: {str(e)}\n\n"
        raise e
        
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