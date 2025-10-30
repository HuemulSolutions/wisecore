from pydantic import BaseModel
from typing import Optional

class Chatbot(BaseModel):
    """
    Schema for chatbot interaction.
    """
    execution_id: str
    thread_id: Optional[str] = None  # Optional field, can be None
    user_message: str
    