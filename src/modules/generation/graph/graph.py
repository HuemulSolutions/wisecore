from langgraph.graph import END, START, StateGraph
from .nodes import (
    State, Config, entrypoint, sort_sections, get_dependencies,
    execute_section, save_section_execution, should_continue, end_execution
)
import asyncio


def compile_graph():
    """
    Compile the state graph for the execution of sections.
    """
    # Create a state graph
    graph = StateGraph(State, config_schema=Config)
    
    # Add nodes to the graph
    graph.add_node("entrypoint", entrypoint)
    graph.add_node("sort_sections", sort_sections)
    graph.add_node("get_dependencies", get_dependencies)
    graph.add_node("execute_section", execute_section)
    # graph.add_node("eval_update_past_sections", eval_update_past_sections)
    # graph.add_node("update_past_sections", update_past_sections)
    graph.add_node("end_execution", end_execution)
    graph.add_node("save_section_execution", save_section_execution)
    
    # Add edges to the graph
    graph.add_edge(START, "entrypoint")
    graph.add_edge("entrypoint", "sort_sections")
    graph.add_edge("sort_sections", "get_dependencies")
    graph.add_edge("get_dependencies", "execute_section")
    graph.add_edge("execute_section", "save_section_execution")
    # graph.add_edge("execute_section", "eval_update_past_sections")
    # graph.add_conditional_edges(
    #     "eval_update_past_sections",
    #     should_update,
    #     {
    #         True: "update_past_sections",
    #         False: "save_section_execution",
    #     }
    # )
    graph.add_conditional_edges(
        "save_section_execution",
        should_continue,
        {
            True: "sort_sections",
            False: "end_execution",
        }
    )
    # graph.add_edge("update_past_sections", "save_section_execution")
    graph.add_edge("end_execution", END)
    
    # Compile the graph
    compiled_graph = graph.compile(
    )
    return compiled_graph

# Variable used by langgraph studio as starting point
compiled_graph = compile_graph()

if __name__ == "__main__":
    async def main():
        initial_state = {
            "document_id": "f144078f-772c-4425-96bc-48bc2f6b74de",
        }
        
        initial_config = {
            "recursion_limit": 40,
        }
        
        result = await compiled_graph.ainvoke(
            initial_state,
            config=initial_config,
        )
        print(result)
        
    asyncio.run(main())
        
    
    
    
    







