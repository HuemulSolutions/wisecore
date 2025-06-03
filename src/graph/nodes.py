from typing_extensions import TypedDict, List
from .llms import get_llm
from langgraph.types import Command, StreamWriter
from .services import GraphServices
from .utils import topological_sort
from .prompts import (writer_prompt, past_section_prompt, 
                      update_past_section_prompt)
from .schemas import EvaluateUpdateSection


graph_services = GraphServices()

llm = get_llm("llama")

class State(TypedDict):
    document_id: str
    execution_id: int
    current_section: dict
    sections: List[object]
    sorted_sections_ids: List[dict]
    should_update: List[dict]
    
class Config(TypedDict):
    recursion_limit: int
    
class BaseConfig(TypedDict):
    configurable: Config


async def entrypoint(state: State, config: BaseConfig, writer: StreamWriter) -> State:
    """
    Entry point for the graph. It retrieves the sections and creates an execution.
    """
    print(state)
    state['sections'] = await graph_services.get_sections_by_document_id(state['document_id'])
    state['execution_id'] = await graph_services.create_execution(state['document_id'])
    writer({"data": {"execution_id": str(state['execution_id'])}})
    return state


def sort_sections(state: State, config: BaseConfig) -> State:
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
    state['current_section'] = next((section for section in 
                                     state['sorted_sections_ids'] if not section['done']), 
                                    None)
    return state


async def get_dependencies(state: State, config: BaseConfig) -> State:
    """
    Get dependencies for a section.
    """
    dependencies = await graph_services.get_dependecies(state['current_section']['id'])
    state['current_section']['dependencies'] = dependencies
    return state


async def execute_section(state: State, config: BaseConfig, writer: StreamWriter) -> State:
    """
    Write the section using the LLM.
    """
    writer({"data": {"section_id": state['current_section']['id']}})
    document_info = await graph_services.get_document_by_id(state['document_id'])
    section = await graph_services.get_section_by_id(state['current_section']['id'])
    dependencies_content = "\n".join(dep['content'] for dep in 
                                     state['current_section']['dependencies'])
    final_prompt = writer_prompt.format(
        procedure_description=f"Tema del procedimiento: {document_info.description}",
        section_init_description=section.init_prompt,
        content=dependencies_content,
        restrictions="",
        section_final_description=section.final_prompt,
    )
    response = await llm.ainvoke(final_prompt)
    state['current_section']['output'] = response.content
    return state


async def should_update_past_section(current_section: str, past_section: str) -> bool:
    """
    Check if the past section should be updated based on the current section.
    """
    prompt = past_section_prompt.format(
        past_section=past_section,
        current_section=current_section
    )
    response = await llm.with_structured_output(EvaluateUpdateSection).ainvoke(prompt)
    return response


async def eval_update_past_sections(state: State, config: BaseConfig) -> State:
    """
    Update the past sections with the current section output.
    """
    should_update_list = []
    for dependency in state['current_section']['dependencies']:
        if dependency['type'] == "section":
            should_update: EvaluateUpdateSection = await should_update_past_section(
                current_section=state['current_section']['output'],
                past_section=dependency['content']
                )
            if should_update:
                should_update_list.append(
                    {
                        "id": dependency['id'],
                        "content": dependency['content'],
                        "explanation": should_update.explanation
                        }
                    )
    state['should_update'] = should_update_list
    return state

def should_update(state: State, config: BaseConfig) -> bool:
    """
    Check if the past sections should be updated.
    """
    if len(state.get('should_update', [])) > 0:
        return True
    else:
        return False


async def update_past_sections(state: State, config: BaseConfig, writer: StreamWriter) -> State:
    """
    Update the past sections in the database.
    """
    for section in state['should_update']:
        writer({"data": {"section_id": section['id']}})
        prompt = update_past_section_prompt.format(
            past_section=section['content'],
            current_section=state['current_section']['output'],
            feedback=section['explanation']
        )
        response = await llm.ainvoke(prompt)
        _ = await graph_services.update_section_execution(
            section_exec_id=section['id'],
            output=response.content
        )
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
    await graph_services.update_execution(
        state['execution_id'],
        status="completed",
        status_message="Execution completed successfully"
    )
    return state