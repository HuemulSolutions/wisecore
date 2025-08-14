from src.config import system_config
from src.graph.llms import get_llm
from langchain_core.messages import AIMessageChunk

def format_content(content: AIMessageChunk) -> str:
    """
    Format the content of an AIMessageChunk to a string.
    """
    if not content.content:
        return ""
    message = content.content.replace("\n", "\\n")
    return "event: content\ndata: " + message + "\n\n"    


async def fix_section_service(content: str, instructions: str):
    """
    Fix a section in a document.
    """
    llm = get_llm(system_config.DEFAULT_LLM)
    if not llm:
        raise ValueError(f"LLM with name {system_config.DEFAULT_LLM} not found.")
    promtp = f"""Fix the following section content following the instructions of the user: 
```
{content}
```
    
Instructions: 
```
{instructions}
```

Output the fixed content only."""
    try:
        async for response in llm.astream(input=promtp):
            print("Response:", response)
            yield format_content(response)
    except Exception as e:
        raise ValueError(f"An error occurred while fixing the section: {str(e)}")
    return
