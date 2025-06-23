from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.template_repo import TemplateRepo
from src.database.models import Template

class TemplateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.template_repo = TemplateRepo(session)
        
    async def get_template_by_id(self, template_id: str) -> Template:
        """
        Retrieve a template by its ID.
        """
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found.")
        return template
    

    async def create_template(self, name: str) -> Template:
        """
        Create a new template.
        """
        new_template = Template(name=name)
        created_template = await self.template_repo.add(new_template)
        return created_template