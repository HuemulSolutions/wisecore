from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UpdateUserInfo(BaseModel):
    """
    Schema for updating basic user information.
    """

    name: Optional[str] = None
    last_name: Optional[str] = None
    birthdate: Optional[datetime] = None
