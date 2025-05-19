from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Execution

class ExecutionRepo(BaseRepository[Execution]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Execution)
