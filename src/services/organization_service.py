from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.organization_repo import OrganizationRepo
from src.database.models import Organization

class OrganizationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.organization_repo = OrganizationRepo(session)
        
        
    async def get_all_organizations(self):
        """
        Retrieve all organizations.
        """
        organizations = await self.organization_repo.get_all()
        return organizations