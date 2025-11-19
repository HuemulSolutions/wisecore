from pydantic import BaseModel
from typing import Optional


class EvaluateUpdateSection(BaseModel):
    """
    Schema for updating the evaluation section of a graph.
    """
    should_update: bool
    explanation: Optional[str] = None
    