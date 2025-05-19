from typing_extensions import TypedDict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.language_models import BaseChatModel
from langgraph.types import Command, StreamWriter
from .services import GraphServices

graph_services = GraphServices()

class State(TypedDict):
    document_id: int
    execution_id: int
    current_section_id: str
    sections: List[object]
    
class Config(TypedDict):
    llm: BaseChatModel
    eval_llm: Optional[BaseChatModel]
    recursion_limit: int
    
class BaseConfig(TypedDict):
    configurable: Config


async def entrypoint(state: State, config: BaseConfig) -> State:
    state['sections'] = await graph_services.get_sections_by_document_id(state['document_id'])
    state['execution_id'] = await graph_services.create_execution(state['document_id'])
    return state
    
    
