from typing_extensions import TypedDict, List, Optional
from .llms import get_llm
from langgraph.types import Command, StreamWriter
from .services import GraphServices
from .utils import topological_sort
from .prompts import (writer_prompt, past_section_prompt, 
                      update_past_section_prompt)
from .schemas import EvaluateUpdateSection
from src.database.core import get_graph_session
from src.database.models import Document, Section, Status
from rich import print

llm = get_llm("gpt-4.1")

class State(TypedDict):
    document_id: str
    execution_id: str
    execution_instructions: Optional[str]
    document: Document
    document_context: str
    current_section: Section
    sections: List[Section]
    sorted_sections_ids: List[dict]
    should_update: List[dict]
    
class Config(TypedDict):
    recursion_limit: int
    
class BaseConfig(TypedDict):
    configurable: Config


async def entrypoint(state: State, config: BaseConfig, writer: StreamWriter) -> State:
    print("Entrypoint")
    """
    Entry point for the graph. It retrieves the sections and creates an execution.
    """
    async with get_graph_session() as session:
        service = GraphServices(session)
        state['document'], state['sections'] = await service.init_execution(state['document_id'],
                                                                state['execution_id'], state.get('execution_instructions'))
        state['document_context'] = await service.get_document_context(state['document_id'])
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
    current_section_id = next((section['id'] for section in 
                                     state['sorted_sections_ids'] if not section['done']), 
                                    None)
    state['current_section'] = next((section for section in state['sections'] 
                                         if section.id == current_section_id), None)
    print(state)
    return state


async def get_dependencies(state: State, config: BaseConfig) -> State:
    """
    Get dependencies for a section.
    """
    print("Getting dependencies for section:", state['current_section'].name)
    
    dependency_content = []
    for dependency in state['current_section'].dependencies:
        print("Dependency:", dependency)
        print(state['sections'])
        dep_section = next(filter(lambda x: str(x.id) == dependency["id"], state['sections']), None)
        if dep_section:
            dependency_content.append(dep_section.output)
        else:
            raise ValueError(f"Dependency with ID {dependency['id']} not found in sections.")
    state['current_section'].dependencies_content = "\n".join(dependency_content)
    return state
    
async def execute_section(state: State, config: BaseConfig, writer: StreamWriter) -> State:
    """
    Write the section using the LLM.
    """
    writer({"section_id": str(state['current_section'].id)})
    section = state['current_section']
    prompt = writer_prompt.format(
        document_description=f"{state['document'].name}: {state['document'].description}",
        context=state['document_context'],
        past_sections=section.dependencies_content,
        section_description=section.prompt,
        additional_instructions=state.get('execution_instructions', '')
    )
    print("Executing section:", section.name)
    response = await llm.ainvoke(prompt)
    section = next(filter(lambda x: x.id == section.id, state['sections']), None)
    section.output = response.content
    return state


# async def should_update_past_section(current_section: str, past_section: str) -> bool:
#     """
#     Check if the past section should be updated based on the current section.
#     """
#     prompt = past_section_prompt.format(
#         past_section=past_section,
#         current_section=current_section
#     )
#     response = await llm.with_structured_output(EvaluateUpdateSection).ainvoke(prompt)
#     return response


# async def eval_update_past_sections(state: State, config: BaseConfig) -> State:
#     """
#     Update the past sections with the current section output.
#     """
#     should_update_list = []
#     for dependency in state['current_section']['dependencies']:
#         if dependency['type'] == "section":
#             should_update: EvaluateUpdateSection = await should_update_past_section(
#                 current_section=state['current_section']['output'],
#                 past_section=dependency['content']
#                 )
#             if should_update:
#                 should_update_list.append(
#                     {
#                         "id": dependency['id'],
#                         "content": dependency['content'],
#                         "explanation": should_update.explanation
#                         }
#                     )
#     state['should_update'] = should_update_list
#     return state

# def should_update(state: State, config: BaseConfig) -> bool:
#     """
#     Check if the past sections should be updated.
#     """
#     if len(state.get('should_update', [])) > 0:
#         return True
#     else:
#         return False


# async def update_past_sections(state: State, config: BaseConfig, writer: StreamWriter) -> State:
#     """
#     Update the past sections in the database.
#     """
#     for section in state['should_update']:
#         writer({"data": {"section_id": section['id']}})
#         prompt = update_past_section_prompt.format(
#             past_section=section['content'],
#             current_section=state['current_section']['output'],
#             feedback=section['explanation']
#         )
#         response = await llm.ainvoke(prompt)
#         _ = await graph_services.update_section_execution(
#             section_exec_id=section['id'],
#             output=response.content
#         )
#     return state


async def save_section_execution(state: State, config: BaseConfig) -> State:
    """
    Save the section execution to the database.
    """
    async with get_graph_session() as session:
        service = GraphServices(session)
        section = next(filter(lambda x: x.id == state['current_section'].id, state['sections']), None)
        await service.save_section_execution(
            section_id=section.id,
            execution_id=state['execution_id'],
            output=section.output,
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