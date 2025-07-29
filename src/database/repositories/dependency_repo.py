from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from ..models import Dependency

class DependencyRepo(BaseRepository[Dependency]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Dependency)
        
        
    async def get_dependencies(self, document_id: UUID) -> list[dict]:
        """
        Retrieve all documents that the given document depends on.
        Returns dependencies both at document level and section level.
        """
        query = (
            select(Dependency)
            .options(
                selectinload(Dependency.depends_on),
                selectinload(Dependency.depends_on_section)
            )
            .where(Dependency.document_id == document_id)
        )
        result = await self.session.execute(query)
        dependencies = result.scalars().all()
        
        return [
            {
                "document_id": dep.depends_on.id,
                "document_name": dep.depends_on.name,
                "section_name": dep.depends_on_section.name if dep.depends_on_section else None,
                "dependency_type": "section" if dep.depends_on_section else "document"
            }
            for dep in dependencies
        ]
        
    async def get_by_ids(self, document_id: UUID, depends_on_document_id: UUID) -> Dependency:
        """
        Retrieve a specific dependency by document and its dependent document IDs.
        """
        query = (
            select(Dependency)
            .where(
                Dependency.document_id == document_id,
                Dependency.depends_on_document_id == depends_on_document_id
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
