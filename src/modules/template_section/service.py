from sqlalchemy.ext.asyncio import AsyncSession
from .repository import TemplateSectionRepo
from .models import TemplateSection

class TemplateSectionService:
    def __init__(self, session: AsyncSession):
        self.session = session        
        self.template_section_repo = TemplateSectionRepo(session)
        
    async def create_template_section(self, name: str, template_id: str,
                                prompt: str, type: str, dependencies: list[str]) -> TemplateSection:
        """
        Create a new template section.
        """
        
        template = await self.template_section_repo.check_if_template_exists(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found.")
        
        check_name = await self.template_section_repo.get_by_name(name, template_id)
        if check_name:
            raise ValueError(f"Template section with name {name} already exists in this template.")
        
        last_order = template.template_sections[-1].order if template.template_sections else 0
        order = last_order + 1
        
        new_section = TemplateSection(name=name, template_id=template_id,
                                     order=order, prompt=prompt, type=type)
        created_section = await self.template_section_repo.add(new_section, dependencies=dependencies)
        return created_section
    
    async def add_template_section(self, section: TemplateSection) -> TemplateSection:
        """
        Add an existing template section.
        """
        created_section = await self.template_section_repo.add(section)
        return created_section
    
    async def delete_template_section(self, section_id: str) -> None:
        """
        Delete a template section.
        """
        section = await self.template_section_repo.get_by_id(section_id)
        if not section:
            raise ValueError(f"Template section with id {section_id} not found.")
        
        await self.template_section_repo.delete(section)
    
    async def add_dependency(self, section_id: str, depends_on_id: str) -> TemplateSection:
        """
        Add a dependency relationship between two template sections.
        """
        return await self.template_section_repo.add_dependency(section_id, depends_on_id)
    
    async def update_template_section(self, id: str, name: str,
                                      prompt: str, dependencies: list[str]) -> TemplateSection:
        """
        Update an existing template section.
        """
        section = await self.template_section_repo.get_by_id(id)
        if not section:
            raise ValueError(f"Template section with id {id} not found.")
        
        if name != section.name:
            check_name = await self.template_section_repo.get_by_name(name, section.template_id)
            if check_name and check_name.id != id:
                raise ValueError(f"Template section with name {name} already exists in this template.")
        
        updated_section = TemplateSection(
            id=section.id,
            name=name,
            template_id=section.template_id,
            order=section.order,
            prompt=prompt,
            type=section.type
        )
        
        updated_section = await self.template_section_repo.update_section(updated_section, dependencies)
        return updated_section
    
    async def update_section_order(self, new_order: list[dict]) -> list[TemplateSection]:
        """
        Update the order of template sections.
        """
        updated_sections = []
        for item in new_order:
            section = await self.template_section_repo.get_by_id(item.section_id)
            if not section:
                raise ValueError(f"Template section with id {item['section_id']} not found.")
            
            section.order = item.order
            updated_section = await self.template_section_repo.update(section)
            updated_sections.append(updated_section)
        
        return updated_sections
    
        
