from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.template_section_repo import TemplateSectionRepo
from src.database.repositories.template_repo import TemplateRepo
from src.database.models import TemplateSection

class TemplateSectionService:
    def __init__(self, session: AsyncSession):
        self.session = session        
        self.template_repo = TemplateRepo(session)
        self.template_section_repo = TemplateSectionRepo(session)
        
    async def create_template_section(self, name: str, template_id: str,
                                order: int, prompt: str, type: str) -> TemplateSection:
        """
        Create a new template section.
        """
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found.")
        
        check_name = await self.template_section_repo.get_by_name(name, template_id)
        if check_name:
            raise ValueError(f"Template section with name {name} already exists in template {template_id}.")
        check_order = await self.template_section_repo.get_by_order(order, template_id)
        if check_order:
            raise ValueError(f"Template section with order {order} already exists in template {template_id}.")
        new_section = TemplateSection(name=name, template_id=template_id,
                                     order=order, prompt=prompt, type=type)
        created_section = await self.template_section_repo.add(new_section)
        return created_section
    
    async def add_dependency(self, section_id: str, depends_on_id: str) -> TemplateSection:
        """
        Add a dependency relationship between two template sections.
        """
        return await self.template_section_repo.add_dependency(section_id, depends_on_id)
        