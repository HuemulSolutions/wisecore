from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models import Template, TemplateSection, TemplateSectionDependency

class TemplateRepo(BaseRepository[Template]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Template)
        
        
        
    async def get_templates(self, organization_id: str) -> list[Template]:
        """
        Retrieve all templates for a specific organization.
        """
        query = (select(self.model)
                 .where(self.model.organization_id == organization_id))
        result = await self.session.execute(query)
        return result.scalars().all()
        
    async def get_by_id(self, template_id: str) -> Template:
        """
        Retrieve a template by its ID and template sections.
        """
        query = (select(self.model)
                 .where(self.model.id == template_id)
                 .options(selectinload(Template.template_sections)
                         .selectinload(TemplateSection.internal_dependencies)
                         .selectinload(TemplateSectionDependency.depends_on_template_section)))
        result = await self.session.execute(query)
        template = result.scalar_one_or_none()
        
        # Ordenar las secciones por el atributo order y añadir atributo dependencies
        if template and template.template_sections:
            template.template_sections.sort(key=lambda section: section.order)
            
            # Añadir atributo dependencies a cada sección
            for section in template.template_sections:
                section.dependencies = [{"id": dep.depends_on_template_section.id, "name": dep.depends_on_template_section.name} for dep in section.internal_dependencies]
            
        return template
    
    async def get_by_name(self, name: str, organization_id: str = None) -> Template:
        """
        Retrieve a template by its name.
        """
        query = (select(self.model)
                 .where(self.model.name == name))
        if organization_id:
            query = query.where(self.model.organization_id == organization_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_template_sections(self, template_id: str) -> list[TemplateSection]:
        """
        Retrieve all sections for a specific template.
        """
        query = (select(TemplateSection)
                 .where(TemplateSection.template_id == template_id)
                 .options(selectinload(TemplateSection.internal_dependencies)))
        result = await self.session.execute(query)
        return result.scalars().all()