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
    promtp = f"""Fix the following section content following the instructions of the user, usually the content is in markdown format:   
The content is inside the triple backticks:
```
{content}
```
    
Instructions: 
```
{instructions}
```

Output the fixed content only, no need to add backticks, just the content."""
    try:
        async for response in llm.astream(input=promtp):
            yield format_content(response)
    except Exception as e:
        raise ValueError(f"An error occurred while fixing the section: {str(e)}")
    return


async def redact_section_prompt_service(name: str, content: str = None):
    """
    Redact or improve the prompt for a section.
    """
    llm = get_llm(system_config.DEFAULT_LLM)
    if not llm:
        raise ValueError(f"LLM with name {system_config.DEFAULT_LLM} not found.")
    
    prompt_generate = """Redacta el prompt para un agente de IA que redacta una sección de un documento.
El prompt debe ser claro, conciso y contener toda la información necesaria para que el agente pueda redactar la sección de manera efectiva.
Debe ser una descripción breve de lo que tiene que contener la sección.
El nombre de la sección es el siguiente: {name}"""

    prompt_improve = """Mejora el prompt para un agente de IA que redacta una sección de un documento.
El prompt debe ser claro, conciso y contener toda la información necesaria para que el agente pueda redactar la sección de manera efectiva.
Debe ser una descripción breve de lo que tiene que contener la sección.
El nombre de la sección es el siguiente: {name}
El prompt actual es el siguiente:
{content}"""
    if content:
        prompt = prompt_improve.format(name=name, content=content)
    else:
        prompt = prompt_generate.format(name=name)
    try:
        async for response in llm.astream(input=prompt):
            yield format_content(response)
    except Exception as e:
        raise ValueError(f"An error occurred while redacting the section prompt: {str(e)}")
    return
