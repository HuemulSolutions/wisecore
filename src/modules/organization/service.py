from sqlalchemy.ext.asyncio import AsyncSession
from .repository import OrganizationRepo
from .models import Organization

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
    
    async def create_organization(self, name: str, description: str = None) -> Organization:
        """
        Create a new organization.
        """
        if not name:
            raise ValueError("Organization name cannot be empty.")
        
        if await self.organization_repo.get_by_name(name):
            raise ValueError(f"Organization with name {name} already exists.")
        
        new_organization = Organization(name=name, description=description)
        
        organization = await self.organization_repo.add(new_organization)
        if not organization:
            raise ValueError("Failed to create organization.")
        
        return organization
    
    async def check_organization_exists(self, organization_id: str) -> bool:
        """
        Check if an organization exists by its ID.
        """
        organization = await self.organization_repo.get_by_id(organization_id)
        return organization is not None