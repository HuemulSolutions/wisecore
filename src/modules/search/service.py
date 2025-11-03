from .repository import ChunkRepo
from src.modules.execution.service import ExecutionService
from .models import Chunk
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
import re
import tiktoken
import asyncio
from concurrent.futures import ThreadPoolExecutor
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# ---- Configuración de chunking ----
DEFAULT_MAX_TOKENS = 500
DEFAULT_OVERLAP = 80

_enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(_enc.encode(text))

def encode(text: str) -> List[int]:
    return _enc.encode(text)

def decode(tokens: List[int]) -> str:
    return _enc.decode(tokens)

# --------- Chunking por tokens con sliding window ----------
def chunk_tokens_sliding(
    text: str,
    max_tokens: int = 350,
    overlap: int = 35,
    min_tokens_last: int = 50
) -> List[str]:
    """
    Crea ventanas deslizantes de tokens con overlap fijo.
    """
    assert 0 <= overlap < max_tokens, "overlap debe ser menor a max_tokens"

    toks = encode(text)
    n = len(toks)
    chunks = []

    step = max_tokens - overlap
    i = 0
    while i < n:
        end = min(i + max_tokens, n)
        chunk = toks[i:end]
        chunks.append(decode(chunk))
        if end == n:
            break
        i += step

    # Fusiona el último si quedó demasiado corto
    if min_tokens_last and len(chunks) >= 2:
        last_len = count_tokens(chunks[-1])
        if last_len < min_tokens_last:
            toks_merged = encode(chunks[-2] + chunks[-1])
            if len(toks_merged) <= max_tokens:
                chunks = chunks[:-2] + [decode(toks_merged)]
    return chunks

# ---- Chunking por oraciones ----
_SENTENCE_SPLIT = re.compile(r'(?<=[\.!?…。؛])\s+(?=[A-ZÁÉÍÓÚÑ0-9""(\[])', flags=re.UNICODE)

def split_sentences(text: str) -> List[str]:
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    sentences = []
    for p in paragraphs:
        parts = _SENTENCE_SPLIT.split(p)
        if len(parts) == 1:
            sentences.append(p)
        else:
            sentences.extend([s.strip() for s in parts if s.strip()])
    return sentences

def chunk_by_sentences(
    text: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    overlap: int = DEFAULT_OVERLAP
) -> List[str]:
    """
    Construye chunks agregando oraciones hasta rozar el límite de tokens.
    """
    assert 0 <= overlap < max_tokens, "overlap debe ser menor a max_tokens"

    sents = split_sentences(text)
    chunks: List[str] = []
    cur_tokens: List[int] = []

    for s in sents:
        stoks = encode(s)
        if len(stoks) > max_tokens:
            parts = chunk_tokens_sliding(s, max_tokens=max_tokens, overlap=overlap)
            for part in parts:
                if cur_tokens:
                    chunks.append(decode(cur_tokens))
                    cur_tokens = []
                chunks.append(part)
            if chunks:
                tail = encode(chunks[-1])[-overlap:] if overlap else []
                cur_tokens = list(tail)
            continue

        if len(cur_tokens) + len(stoks) <= max_tokens:
            cur_tokens.extend(stoks)
        else:
            if cur_tokens:
                chunks.append(decode(cur_tokens))
            tail = encode(chunks[-1])[-overlap:] if overlap and chunks else []
            cur_tokens = list(tail) + stoks

    if cur_tokens:
        chunks.append(decode(cur_tokens))

    return chunks

def chunk_text(
    text: str,
    max_tokens_per_chunk: int = DEFAULT_MAX_TOKENS,
    overlap_tokens: int = DEFAULT_OVERLAP,
    strategy: str = "sentences",
    min_tokens_last: int = 0
) -> List[Dict[str, str]]:
    """
    Devuelve una lista de dicts con {'id': 'chunk-0001', 'text': '...'}.
    """
    if strategy == "sentences":
        pieces = chunk_by_sentences(text, max_tokens=max_tokens_per_chunk, overlap=overlap_tokens)
    elif strategy == "sliding":
        pieces = chunk_tokens_sliding(text, max_tokens=max_tokens_per_chunk, overlap=overlap_tokens, min_tokens_last=min_tokens_last)
    else:
        raise ValueError("strategy debe ser 'sentences' o 'sliding'")

    out = []
    for i, p in enumerate(pieces, start=1):
        out.append({"id": f"chunk-{i:04d}", "text": p})
    return out

class ChunkService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.chunk_repo = ChunkRepo(session)
        self.azure_client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version="2025-03-01-preview",
        )

    def create_embeddings(self, text: str) -> List[float]:
        """Crear embeddings usando Azure OpenAI"""
        embedding = self.azure_client.embeddings.create(
            model="text-embedding-3-large",
            input=text,
        )
        return embedding.data[0].embedding

    async def _process_section_execution(self, section_execution) -> List[Chunk]:
        """Procesar una section execution para crear chunks con embeddings"""
        # Usar custom_output si existe, sino output
        content = section_execution.custom_output or section_execution.output
        
        if not content or not content.strip():
            return []

        # Crear chunks del texto
        chunks_data = chunk_text(
            content,
            max_tokens_per_chunk=300,
            overlap_tokens=50,
            strategy="sentences"
        )

        # Crear embeddings en un thread pool para no bloquear el event loop
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=5) as executor:
            embedding_tasks = [
                loop.run_in_executor(executor, self.create_embeddings, chunk_data["text"])
                for chunk_data in chunks_data
            ]
            embeddings = await asyncio.gather(*embedding_tasks)

        # Crear objetos Chunk
        chunks = []
        for chunk_data, embedding in zip(chunks_data, embeddings):
            chunk = Chunk(
                content=chunk_data["text"],
                embedding=embedding,
                section_execution_id=section_execution.id
            )
            chunks.append(chunk)

        return chunks
        
    async def generate_chunks(self, execution_id: str) -> int:
        """
        Generate chunks for a specific execution.
        Returns the number of chunks created.
        """
        execution = await ExecutionService(self.session).get_execution_for_chunking(execution_id)
        if execution.status.value != "completed":
            raise ValueError(f"Execution with ID {execution_id} is not completed.")

        # Obtener todas las section executions
        section_executions = execution.sections_executions
        
        if not section_executions:
            return 0

        # Procesar section executions en paralelo
        processing_tasks = [
            self._process_section_execution(section_exec)
            for section_exec in section_executions
        ]
        
        # Ejecutar todas las tareas en paralelo
        all_chunks_lists = await asyncio.gather(*processing_tasks)
        
        # Aplanar la lista de listas
        all_chunks = []
        for chunks_list in all_chunks_lists:
            all_chunks.extend(chunks_list)

        # Guardar todos los chunks en la base de datos
        if all_chunks:
            await self.chunk_repo.create_chunks(all_chunks)

        return len(all_chunks)
    
    async def search_chunks(self, query: str, organization_id: str, top_k: int = 5) -> List[Chunk]:
        """
        Search for chunks similar to the query using vector similarity.
        """
        query_embedding = self.create_embeddings(query)
        results = await self.chunk_repo.search_by_embedding(query_embedding, 
                                                            organization_id=organization_id, 
                                                            limit=top_k)
        return results
    
    async def delete_chunks_by_execution(self, execution_id: str):
        """
        Delete all chunks associated with a specific execution.
        Returns the number of chunks deleted.
        """
        _ = await ExecutionService(self.session).get_execution_for_chunking(execution_id)
        
        await self.chunk_repo.delete_chunks_by_execution_id(execution_id)
        
        
        

