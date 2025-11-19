from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from .nodes import entrypoint, agent, State
from src.config import system_config
from typing import Optional
from langgraph.graph import START, StateGraph, END
import uuid

def build_graph() -> StateGraph:
    builder = StateGraph(State)
    builder.add_node("entrypoint", entrypoint)
    builder.add_edge(START, "entrypoint")
    builder.add_node("agent", agent)
    
    builder.add_edge("entrypoint", "agent")
    builder.add_edge("agent", END)

    return builder

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


async def stream(message: str, execution_id: str, thread_id: Optional[str] = None):
    if thread_id is None:
        thread_id = str(uuid.uuid4())
        yield f"event: thread_id\ndata: {thread_id}\n\n"

    async with AsyncPostgresSaver.from_conn_string(system_config.ALEMBIC_DATABASE_URL) as checkpointer:
        # await checkpointer.setup()
        graph = build_graph()
        compiled_graph = graph.compile(checkpointer=checkpointer)
        state = State(
            execution_id=execution_id,
            messages=[{"role": "user", "content": message}]
        )
        try:
            async for event in compiled_graph.astream(state,
                                            config={"thread_id": thread_id},
                                            stream_mode="messages"):
                yield format_event(("messages", event))
        except Exception as e:
            print(event)
            yield f"event: error\ndata: {str(e)}\n\n"
            return

