from .graph import compiled_graph
from .nodes import State, graph_services


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

async def stream_graph(document_id: str):
    """
    Stream the graph execution.
    """
    state = get_state(document_id)
    execution_id = None
    counter = 0
    try:
        async for event in compiled_graph.astream(state, stream_mode=["messages", "custom"]):
            yield format_event(event)
            counter += 1
            if counter > 50:
                break
    except Exception as e:
        yield f"event: error\ndata: {str(e)}\n\n"
        if execution_id:
            await graph_services.update_execution(execution_id, state)
        raise e
        
def test_stream_graph():
    """
    Test the stream_graph function.
    """
    import asyncio

    async def test():
        state = {
            "document_id": "f144078f-772c-4425-96bc-48bc2f6b74de"}
        async for event in stream_graph(state):
            print(event)
    asyncio.run(test())
if __name__ == "__main__":
    test_stream_graph()