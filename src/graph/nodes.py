from typing_extensions import TypedDict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.language_models import BaseChatModel
from langgraph.types import Command, StreamWriter
from .services import GraphServices
from .utils import topological_sort
from .prompts import (writer_prompt)

graph_services = GraphServices()

class State(TypedDict):
    document_id: str
    execution_id: int
    current_section: dict
    sections: List[object]
    sorted_sections_ids: List[dict]
    
class Config(TypedDict):
    llm: BaseChatModel
    eval_llm: Optional[BaseChatModel]
    recursion_limit: int
    
class BaseConfig(TypedDict):
    configurable: Config


async def entrypoint(state: State, config: BaseConfig) -> State:
    print(state)
    state['sections'] = await graph_services.get_sections_by_document_id(state['document_id'])
    state['execution_id'] = await graph_services.create_execution(state['document_id'])
    return state

async def sort_sections(state: State, config: BaseConfig) -> State:
    """
    Sort sections based on their dependencies.
    """
    if not state.get('sorted_sections_ids', False):
        print("Ordenando secciones")
        sorted_sections = topological_sort(state['sections'])
        sorted_sections_list = []
        for section_id in sorted_sections:
            sorted_sections_list.append({
                "id": section_id,
                "done": False,
            })
        state['sorted_sections_ids'] = sorted_sections_list
    return state

async def get_dependencies(state: State, config: BaseConfig) -> State:
    """
    Get dependencies for a section.
    """
    # This function should be implemented to fetch dependencies for a section
    state['current_section'] = next((section for section in state['sorted_sections_ids'] if not section['done']), None)
    if state['current_section']:
        dependencies = await graph_services.get_dependecies(state['current_section']['id'])
        state['current_section']['dependencies'] = dependencies
    return state

async def execute_section(state: State, config: BaseConfig) -> State:
    document_info = await graph_services.get_document_by_id(state['document_id'])
    section = await graph_services.get_section_by_id(state['current_section']['id'])
    final_prompt = writer_prompt.format(
        procedure_description=f"Tema del procedimiento: {document_info.description}",
        section_init_description=section.init_prompt,
        content=state['current_section']['dependencies'],
        restrictions="",
        section_final_description=section.final_prompt,
    )
    llm: BaseChatModel = config['configurable']['llm']
    response = await llm.ainvoke(final_prompt)
    state['current_section']['output'] = response
    return state


async def save_section_execution(state: State, config: BaseConfig) -> State:
    """
    Save the section execution to the database.
    """

    _ = await graph_services.save_section_execution(
        state['current_section']['id'],
        state['execution_id'],
        state['current_section']['output']
    )

    for section in state['sorted_sections_ids']:
        if section['id'] == state['current_section']['id']:
            section['done'] = True
            break
        
    return state
    
    
    
    



    
    
