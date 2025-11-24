from src.modules.llm.service import LLMService
from langchain_core.messages import AIMessageChunk
from pydantic import BaseModel
from src.modules.job.service import JobService
from src.modules.job.models import Job
from sqlalchemy.ext.asyncio import AsyncSession
import json

def format_content(content: AIMessageChunk) -> str:
    """
    Format the content of an AIMessageChunk to a string.
    """
    if not content.content:
        return ""
    message = content.content.replace("\n", "\\n")
    return "event: content\ndata: " + message + "\n\n"    

class GenerationService:
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.llm_service = LLMService(session)
    
    async def add_execution_graph_job(self, document_id: str, execution_id: str, user_instructions: str = None) -> Job:
        """
        Enqueue a job to run the generation graph for a document execution.
        """
        service = JobService(self.session)
        payload = {
            "document_id": document_id,
            "execution_id": execution_id,
            "user_instructions": user_instructions
        }
        job = await service.enqueue_job(
            job_type="run_generation_graph",
            payload=json.dumps(payload)
        )
        return job
    
    async def fix_section_service(self, content: str, instructions: str):
        """
        Fix a section in a document.
        """
        llm = await self.llm_service.get_model()
        if not llm:
            raise ValueError(f"LLM with name not found.")
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
    
    async def redact_section_prompt_service(self, name: str, content: str = None):
        """
        Redact or improve the prompt for a section.
        """
        llm = await self.llm_service.get_model()
        if not llm:
            raise ValueError(f"LLM not found.")
        
        prompt_generate = """Redacta el prompt para un agente de IA que redacta una sección de un documento.
El prompt debe ser claro, detallado y contener toda la información necesaria para que el agente pueda redactar la sección de manera efectiva.
Debe ser una descripción de lo que tiene que contener la sección.
Incluye parámetros como el tono, estilo, el largo aproximado, usar bullets si es necesario, etc.
El nombre de la sección es el siguiente: {name}
Tu output debe ser solo el prompt, no incluyas 'Prompt:' o algo similar antes o después del prompt."""

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
    
    async def generate_document_structure(self, document_name: str, document_description: str) -> dict:
        class Section(BaseModel):
            name: str
            order: int
            prompt: str
            dependencies: list[str] = []
        
        class Document(BaseModel):
            sections: list[Section]
        
        prompt = """
Eres el encargado de organizar la estructura de un documento donde se va a utilizar IA para generar el contenido de cada sección.
Tu tarea es definir qué secciones debe tener el documento, en qué orden deben ir y si alguna sección depende de otra.
Cada sección consiste en:
- Nombre de la sección (name): Un título breve y descriptivo de la sección.
- Orden (order): Un número entero que indica la posición de la sección en el documento. El orden en que se generan las secciones es de acuerdo a las dependencias, y el orden numérico es para la presentación final.
- Prompt (prompt): Prompt debe ser claro, detallado y contener toda la información necesaria para que el agente pueda redactar la sección de manera efectiva. Debe ser una descripción de lo que tiene que contener la sección. Incluye parámetros como el tono, estilo, el largo aproximado, usar bullets si es necesario, etc.
- Dependencias (dependencies): Una lista de nombres de secciones de las que depende esta sección. Si una sección depende de otra, significa que para redactar esta sección es necesario tener en cuenta el contenido de las secciones de las que depende. Si no depende de ninguna, la lista estará vacía. Una sección puede depender de cero, una o varias secciones.

Intenta que las secciones sean lo más generales posibles, para que puedan ser reutilizadas en otros documentos.
Debes generar la estructura para el siguiente documento:
Nombre de documento: {document_name}
Descripción: {document_description}
        """
        llm = await self.llm_service.get_model()
        if not llm:
            raise ValueError(f"LLM with name not found.")
        document = await llm.with_structured_output(Document).ainvoke(
            prompt.format(
                document_name=document_name,
                document_description=document_description
        ),
            max_tokens=8000
        )
        return document.model_dump()
