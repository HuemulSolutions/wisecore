from typing_extensions import TypedDict, List, Optional
# from .llms import get_llm
from src.llm.llm import get_llm
from langchain_core.language_models import BaseChatModel
from langgraph.types import Command, StreamWriter
from .services import GraphServices
from .utils import topological_sort
from .prompts import (writer_prompt, past_section_prompt, 
                      update_past_section_prompt)
from .schemas import EvaluateUpdateSection
from src.database.core import get_graph_session
from src.modules.document.models import Document
from src.modules.section.models import Section
from src.modules.execution.models import Status
from rich import print

# llm = get_llm("gpt-4.1")

class State(TypedDict): 
    document_id: str
    execution_id: str
    llm_id: str
    start_section_id: Optional[str]
    single_section_mode: Optional[bool]
    execution_instructions: Optional[str]
    document: Document
    document_context: str
    current_section: Section
    sections: List[Section]
    sorted_sections_ids: List[dict]
    llm: BaseChatModel
    section_outputs: dict  # Diccionario para almacenar outputs de secciones
    
class Config(TypedDict):
    recursion_limit: int
    
class BaseConfig(TypedDict):
    configurable: Config


async def entrypoint(state: State) -> State:
    print("Entrypoint")
    """
    Entry point for the graph. It retrieves the sections and creates an execution.
    """
    
    async with get_graph_session() as session:
        service = GraphServices(session)
        # Only if executing all sections, update execution instructions
        # if not state.get("start_section_id"):
        #     state['document'], state['sections'] = await (service.init_execution(state['document_id'],
        #                                                                 state['execution_id'], 
        #                                                                 state.get('execution_instructions')))
        state['document'], state['sections'] = await (service.init_execution(state['document_id'],
                                                                        state['execution_id']))
        state["llm"] = await service.get_llm(state['llm_id'])
        state['document_context'] = await service.get_document_context(state['document_id'])
        # Inicializar diccionario para outputs de secciones
        if state.get('start_section_id'):
            state['section_outputs'] = await service.get_partial_sections_execution(state['execution_id'])
        else:
            state['section_outputs'] = {}
    return state


def sort_sections(state: State, config: BaseConfig) -> State:
    print("Sorting sections")
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
        
        if state.get('start_section_id'):
            print("Buscando sección de inicio:", state['start_section_id'])
            # Marcar secciones anteriores a start_section_id como done
            found_start = False
            for section in state['sorted_sections_ids']:
                if str(section['id']) == state['start_section_id']:
                    found_start = True
                    section['done'] = False
                elif not found_start:
                    section['done'] = True
    current_section_id = next((section['id'] for section in 
                                     state['sorted_sections_ids'] if not section['done']), 
                                    None)
    state['current_section'] = next((section for section in state['sections'] 
                                         if section.id == current_section_id), None)
    return state


async def get_dependencies(state: State, config: BaseConfig) -> State:
    """
    Get dependencies for a section.
    """
    print("Getting dependencies for section:", state['current_section'].name)
    
    # Inicializar diccionario si no existe
    if 'section_outputs' not in state:
        state['section_outputs'] = {}
    
    dependency_content = []
    for dependency in state['current_section'].dependencies:
        print(state['sections'])
        dep_section = next(filter(lambda x: str(x.id) == dependency["id"], state['sections']), None)
        if dep_section:
            # Obtener output del diccionario del state
            section_output = state['section_outputs'].get(str(dep_section.id), None)
            if not section_output:
                raise ValueError(f"Output of dependency not found, make sure to execute sections in order of dependencies.")
            dependency_content.append(section_output)
        else:
            raise ValueError(f"Dependency with ID {dependency['id']} not found in sections.")
    state['current_section'].dependencies_content = "\n".join(dependency_content)
    return state
    
async def execute_section(state: State, config: BaseConfig, writer: StreamWriter) -> State:
    """
    Write the section using the LLM.
    """
    print("Executing section:", state['current_section'].name)
    writer({"section_id": str(state['current_section'].id)})
    section = state['current_section']
    prompt = writer_prompt.format(
        document_description=f"{state['document'].name}: {state['document'].description}",
        context=state['document_context'],
        past_sections=section.dependencies_content,
        section_description=f"Nombre sección: {section.name}\nDescripción: {section.prompt}",
        additional_instructions=state.get('execution_instructions', '')
    )
    
    llm = state['llm']
    response = await llm.ainvoke(prompt)
    
    # Inicializar diccionario si no existe
    if 'section_outputs' not in state:
        state['section_outputs'] = {}
    
    # Guardar output en el diccionario del state
    state['section_outputs'][str(section.id)] = response.content
    return state


async def save_section_execution(state: State, config: BaseConfig) -> State:
    """
    Save the section execution to the database.
    """
    async with get_graph_session() as session:
        service = GraphServices(session)
        section = state['current_section']
        
        # Obtener output del diccionario del state
        section_output = state['section_outputs'].get(str(section.id), "")
        
        await service.save_section_execution(
            section_id=section.id,
            name=section.name,
            execution_id=state['execution_id'],
            output=section_output,
            prompt=section.prompt,
            order=section.order
        )

    for section in state['sorted_sections_ids']:
        if section['id'] == state['current_section'].id:
            section['done'] = True
            break
    return state


def should_continue(state: State, config: BaseConfig) -> bool:
    """
    Check if there are more sections to process.
    """
    if state.get('single_section_mode', False):
        return False
    if any(section['done'] == False for section in state['sorted_sections_ids']):
        return True
    else:
        return False
    
    
async def end_execution(state: State, config: BaseConfig) -> State:
    """
    End the execution and update the status.
    """
    async with get_graph_session() as session:
        graph_services = GraphServices(session)
        await graph_services.update_execution(
            state['execution_id'],
            status=Status.COMPLETED,
            status_message="Execution completed successfully"
        )
    return state