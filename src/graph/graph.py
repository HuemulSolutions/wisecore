from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph
from dotenv import load_dotenv
from .nodes import (
    State, Config, entrypoint, sort_sections,
    get_dependencies, execute_section, save_section_execution
)
import os
import asyncio

load_dotenv()


gpt = init_chat_model(
    model="azure_openai:gpt-4.1",
    azure_deployment="gpt-4.1",
)

# llama = init_chat_model(
#     model="ibm:meta-llama/llama-4-maverick-17b-128e-instruct-fp8",
#     project_id=os.getenv("WATSONX_PROJECT_ID")
# )

# granite = init_chat_model(
#     model="ibm:ibm/granite-3-3-8b-instruct",
#     model_provider="ibm",
#     project_id=os.getenv("WATSONX_PROJECT_ID")
# )


def compile_graph():
    graph = StateGraph(State, config_schema=Config)
    graph.add_node("entrypoint", entrypoint)
    graph.add_node("sort_sections", sort_sections)
    graph.add_node("get_dependencies", get_dependencies)
    graph.add_node("execute_section", execute_section)
    graph.add_node("save_section_execution", save_section_execution)
    
    graph.add_edge(START, "entrypoint")
    graph.add_edge("entrypoint", "sort_sections")
    graph.add_edge("sort_sections", "get_dependencies")
    graph.add_edge("get_dependencies", "execute_section")
    graph.add_edge("execute_section", "save_section_execution")
    graph.add_edge("save_section_execution", END)
    
    compiled_graph = graph.compile(
    )
    return compiled_graph


compiled_graph = compile_graph()

if __name__ == "__main__":
    async def main():
        initial_state = {
            "document_id": "f144078f-772c-4425-96bc-48bc2f6b74de",
        }
        
        initial_config = {
            "llm": gpt,
            "eval_llm": None,
            "recursion_limit": 40,
        }
        
        result = await compiled_graph.ainvoke(
            initial_state,
            config=initial_config,
        )
        print(result)
        
    asyncio.run(main())
        
    
    
    
    







