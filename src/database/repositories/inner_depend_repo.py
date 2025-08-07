from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models import InnerDependency

class InnerDependencyRepo(BaseRepository[InnerDependency]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, InnerDependency)