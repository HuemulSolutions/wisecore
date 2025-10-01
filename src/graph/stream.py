from .graph import compiled_graph
from .nodes import State
from src.database.core import get_graph_session
from src.graph.services import GraphServices
from src.database.models import Status
import asyncio
from typing import AsyncGenerator, Optional


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
    
async def run_graph_worker(document_id: str, execution_id: str, q: asyncio.Queue, user_instructions: str = None, ):
    """
    Corre el grafo hasta el final, escribiendo en DB y publicando eventos en la cola.
    No depende del stream HTTP; aunque el cliente se desconecte, esto sigue.
    """
    # Flag para saber si la cola está siendo consumida
    queue_active = True
    
    def mark_queue_inactive():
        nonlocal queue_active
        queue_active = False
        print(f"[Worker] Cola marcada como inactiva para {execution_id}")
    
    try:
        print(f"[Worker] Iniciando ejecución para {execution_id}")  # Debug log
        initial_config = {"recursion_limit": 60}
        state = State(
            document_id=document_id,
            execution_id=execution_id,
            execution_instructions=user_instructions
        )
        
        async for event in compiled_graph.astream(state, config=initial_config, stream_mode=["messages", "custom"]):
            try:
                formatted_event = format_event(event)
                if formatted_event and queue_active:
                    # Usar put_nowait para no bloquear nunca
                    try:
                        q.put_nowait(formatted_event)
                    except asyncio.QueueFull:
                        print(f"[Worker] Cola llena, marcando como inactiva para {execution_id}")
                        mark_queue_inactive()
                        # Continúa sin bloquear
                elif not queue_active:
                    # Solo logear ocasionalmente para no spam
                    if hash(str(event)) % 50 == 0:  # Log cada ~50 eventos
                        print(f"[Worker] Continuando ejecución sin cola para {execution_id}")
            except Exception as put_error:
                print(f"[Worker] Error al poner evento en cola: {put_error}")
                mark_queue_inactive()
                # Continúa ejecutando aunque falle el put
                
    except asyncio.CancelledError:
        print(f"[Worker] Cancelado para {execution_id}")
        raise
    except Exception as e:
        print(f"[Worker] Error en ejecución {execution_id}: {e}")
        try:
            async with get_graph_session() as session:
                service = GraphServices(session)
                await service.update_execution(execution_id, Status.FAILED, str(e))
        except Exception as db_error:
            print(f"[Worker] Error al actualizar DB: {db_error}")
        
        if queue_active:
            try:
                q.put_nowait(f"event: error\ndata: {str(e)}\n\n")
            except Exception:
                print(f"[Worker] No se pudo poner error en cola para {execution_id}")
    finally:
        if queue_active:
            try:
                q.put_nowait(None)  # Señal de fin
                print(f"[Worker] Señal de fin enviada para {execution_id}")
            except Exception:
                print(f"[Worker] No se pudo poner señal de fin en cola para {execution_id}")
        print(f"[Worker] Finalizado para {execution_id}")
        
async def stream_queue(q: asyncio.Queue) -> AsyncGenerator[bytes, None]:
    """
    Drena la cola y la envía al cliente como SSE.
    Si el cliente se desconecta, esta corrutina recibe CancelledError y se corta,
    pero la tarea 'worker' seguirá viva.
    """
    try:
        while True:
            try:
                # Timeout para evitar bloqueo infinito
                item = await asyncio.wait_for(q.get(), timeout=1.0)
                if item is None:
                    break
                yield item.encode("utf-8")
            except asyncio.TimeoutError:
                # Envía heartbeat para mantener conexión viva
                yield b"event: heartbeat\ndata: ping\n\n"
                continue
    except asyncio.CancelledError:
        print("[Stream] Cliente desconectado, pero worker continúa")
        raise
    
        
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