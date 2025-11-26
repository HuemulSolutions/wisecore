from abc import ABC, abstractmethod
from typing import List, Union


class BaseEmbeddings(ABC):
    """Clase abstracta base para generar embeddings de texto."""
    
    @abstractmethod
    def generate_embeddings(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Genera embeddings para el texto o lista de textos proporcionados.
        
        Args:
            texts: Texto individual o lista de textos para generar embeddings
            
        Returns:
            Lista de embeddings (floats) para un texto individual,
            o lista de listas de embeddings para múltiples textos
        """
        pass
